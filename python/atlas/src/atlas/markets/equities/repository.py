"""Authoritative Equity Directory Repository for ATLAS Equities Markets V1 (Stage 57)."""

import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity
from atlas.instruments.models import Equity

from .config import (
    DEFAULT_EQUITIES_CATALOG,
    SUPPORTED_EQUITY_SUBTYPES,
    SUPPORTED_LISTING_STATUSES,
    CanonicalEquityConfig,
    validate_equities_catalog,
)
from .models import (
    EquityFilterOptionsResponse,
    EquityListingMetadata,
    FilterCountryItem,
    FilterExchangeItem,
    FilterStatusItem,
    FilterTypeItem,
)

logger = logging.getLogger(__name__)


class EquityDirectoryRepository:
    """
    Authoritative catalog repository for Equity Securities.

    Guarantees:
    - 100% Read-Only: 0 writes to PostgreSQL, 0 provider calls.
    - Grounded in canonical Financial Instrument UUIDs.
    - Supports exchange-scoped symbols and listing venues.
    - Deterministic ordering and bounded pagination.
    - Extracts truthful available filters based strictly on catalog contents.
    """

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        catalog_configs: Optional[List[CanonicalEquityConfig]] = None,
    ):
        self._db_session = db_session
        raw_configs = (
            catalog_configs if catalog_configs is not None else DEFAULT_EQUITIES_CATALOG
        )
        self._configs = validate_equities_catalog([c for c in raw_configs if c.enabled])

    async def get_all_canonical_equities(self) -> List[CanonicalEquityConfig]:
        """
        Retrieves all canonical equity configurations.
        If database contains registered equities and listing metadata, integrates them;
        otherwise serves validated server-owned canonical catalog.
        """
        if self._db_session is not None:
            try:
                # Query database to check if database has canonical equities
                stmt = (
                    select(Equity, Entity, EquityListingMetadata)
                    .join(Entity, Entity.entity_id == Equity.entity_id)
                    .outerjoin(
                        EquityListingMetadata,
                        EquityListingMetadata.instrument_entity_id == Equity.entity_id,
                    )
                )
                result = await self._db_session.execute(stmt)
                db_rows = result.all()

                if db_rows:
                    db_configs: List[CanonicalEquityConfig] = []
                    for eq, ent, meta in db_rows:
                        # Extract or construct canonical config from DB row
                        raw_mic = meta.exchange_mic if meta and meta.exchange_mic else "UNKNOWN"
                        mic = raw_mic.upper()
                        sym = (
                            meta.symbol
                            if meta and meta.symbol
                            else (ent.canonical_name or "UNKNOWN")
                        )
                        curr = meta.quote_currency if meta and meta.quote_currency else "USD"
                        status = meta.listing_status if meta and meta.listing_status else "ACTIVE"
                        subtype = eq.equity_kind or "common_stock"
                        subtype_label = SUPPORTED_EQUITY_SUBTYPES.get(subtype, "Common Equity")
                        country_name = "United States" if curr == "USD" else "Global"
                        country_code = "US" if curr == "USD" else "XX"

                        db_configs.append(
                            CanonicalEquityConfig(
                                instrument_entity_id=ent.entity_id,
                                display_name=ent.display_name or ent.canonical_name,
                                display_symbol=sym,
                                equity_subtype=subtype,
                                equity_subtype_label=subtype_label,
                                share_class_name=eq.share_class_name,
                                exchange_id=meta.exchange_entity_id if meta else None,
                                exchange_mic=mic,
                                exchange_display_name=f"Exchange ({mic})",
                                listing_market_country=country_name,
                                listing_market_country_code=country_code,
                                trading_currency=curr,
                                listing_status=status,
                                enabled=True,
                            )
                        )
                    return db_configs
            except Exception as e:
                logger.warning("Database equity query fallback to catalog: %s", e)

        return self._configs

    async def query_directory(
        self,
        query: Optional[str] = None,
        market_country: Optional[str] = None,
        exchange: Optional[str] = None,
        equity_type: Optional[str] = None,
        listing_status: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[CanonicalEquityConfig], int, Optional[str], bool]:
        """
        Filters and paginates canonical equities.
        Returns: (page_items, total_filtered_count, next_cursor, has_more).
        """
        all_equities = await self.get_all_canonical_equities()

        # 1. Filter execution
        filtered: List[CanonicalEquityConfig] = []
        for eq in all_equities:
            # Query match (name, symbol, or MIC)
            if query:
                q_clean = query.strip().upper()
                name_match = q_clean in eq.display_name.upper()
                sym_match = q_clean in eq.display_symbol.upper()
                mic_match = q_clean in eq.exchange_mic.upper()
                comp_match = (
                    eq.issuer_company_name is not None
                    and q_clean in eq.issuer_company_name.upper()
                )
                if not (name_match or sym_match or mic_match or comp_match):
                    continue

            # Market Country match
            if market_country and market_country.lower() != "all":
                c_clean = market_country.strip().lower()
                country_match = (
                    eq.listing_market_country.lower() == c_clean
                    or eq.listing_market_country_code.lower() == c_clean
                )
                if not country_match:
                    continue

            # Exchange match (MIC, display name, or UUID)
            if exchange and exchange.lower() != "all":
                ex_clean = exchange.strip().lower()
                ex_mic_match = eq.exchange_mic.lower() == ex_clean
                ex_name_match = eq.exchange_display_name.lower() == ex_clean
                ex_uuid_match = (
                    eq.exchange_id is not None
                    and str(eq.exchange_id).lower() == ex_clean
                )
                if not (ex_mic_match or ex_name_match or ex_uuid_match):
                    continue

            # Equity Subtype match
            if equity_type and equity_type.lower() != "all":
                type_clean = equity_type.strip().lower()
                if eq.equity_subtype.lower() != type_clean:
                    continue

            # Listing Status match
            if listing_status and listing_status.lower() != "all":
                status_clean = listing_status.strip().upper()
                if eq.listing_status.upper() != status_clean:
                    continue

            filtered.append(eq)

        # 2. Deterministic ordering: display_name.lower() ASC, exchange_mic ASC, UUID ASC
        filtered.sort(
            key=lambda x: (
                x.display_name.lower(),
                x.exchange_mic.upper(),
                str(x.instrument_entity_id),
            )
        )

        # 3. Bounded pagination
        limit = max(1, min(limit, 100))
        offset = 0
        if cursor and cursor.isdigit():
            offset = max(0, int(cursor))

        total_count = len(filtered)
        page_items = filtered[offset : offset + limit]
        has_more = (offset + limit) < total_count
        next_cursor = str(offset + limit) if has_more else None

        return page_items, total_count, next_cursor, has_more

    async def get_by_instrument_id(
        self, instrument_entity_id: UUID
    ) -> Optional[CanonicalEquityConfig]:
        """Looks up a single canonical equity by Financial Instrument UUID."""
        all_equities = await self.get_all_canonical_equities()
        for eq in all_equities:
            if eq.instrument_entity_id == instrument_entity_id:
                return eq
        return None

    async def get_filter_options(self) -> EquityFilterOptionsResponse:
        """Dynamically computes truthful filter choices grounded strictly in catalog contents."""
        all_equities = await self.get_all_canonical_equities()

        country_counts: Dict[Tuple[str, str], int] = {}
        exchange_counts: Dict[Tuple[Optional[UUID], str, str, str], int] = {}
        type_counts: Dict[Tuple[str, str], int] = {}
        status_counts: Dict[Tuple[str, str], int] = {}

        for eq in all_equities:
            c_key = (eq.listing_market_country_code, eq.listing_market_country)
            country_counts[c_key] = country_counts.get(c_key, 0) + 1

            ex_key = (
                eq.exchange_id,
                eq.exchange_mic,
                eq.exchange_display_name,
                eq.listing_market_country_code,
            )
            exchange_counts[ex_key] = exchange_counts.get(ex_key, 0) + 1

            t_key = (eq.equity_subtype, eq.equity_subtype_label)
            type_counts[t_key] = type_counts.get(t_key, 0) + 1

            s_label = SUPPORTED_LISTING_STATUSES.get(eq.listing_status, eq.listing_status.title())
            s_key = (eq.listing_status, s_label)
            status_counts[s_key] = status_counts.get(s_key, 0) + 1

        countries = [
            FilterCountryItem(code=code, name=name, count=cnt)
            for (code, name), cnt in sorted(country_counts.items(), key=lambda x: x[0][1])
        ]

        exchanges = [
            FilterExchangeItem(
                id=ex_id,
                mic=mic,
                name=name,
                country_code=cc,
                count=cnt,
            )
            for (ex_id, mic, name, cc), cnt in sorted(
                exchange_counts.items(), key=lambda x: x[0][2]
            )
        ]

        equity_types = [
            FilterTypeItem(id=t_id, label=label, count=cnt)
            for (t_id, label), cnt in sorted(type_counts.items(), key=lambda x: x[0][1])
        ]

        listing_statuses = [
            FilterStatusItem(id=s_id, label=label, count=cnt)
            for (s_id, label), cnt in sorted(status_counts.items(), key=lambda x: x[0][1])
        ]

        return EquityFilterOptionsResponse(
            countries=countries,
            exchanges=exchanges,
            equity_types=equity_types,
            listing_statuses=listing_statuses,
        )
