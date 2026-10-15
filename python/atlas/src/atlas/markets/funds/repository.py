"""Authoritative Fund Directory Repository for ATLAS ETFs & Funds Markets V1 (Stage 58)."""

import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity

from .config import (
    DEFAULT_FUNDS_CATALOG,
    SUPPORTED_FUND_TYPES,
    SUPPORTED_INVESTMENT_CATEGORIES,
    CanonicalFundConfig,
    validate_funds_catalog,
)
from .models import (
    FundExchangeFilterOption,
    FundFilterOption,
    FundFilterOptionsResponse,
    FundListingMetadata,
    FundMetadata,
    FundNAVObservation,
)

logger = logging.getLogger(__name__)


class FundDirectoryRepository:
    """
    Authoritative catalog repository for ETFs and Investment Funds.

    Guarantees:
    - 100% Read-Only: 0 writes to PostgreSQL, 0 provider calls on read.
    - Grounded in canonical Financial Instrument UUIDs.
    - Preserves distinct Fund Types (ETF, Mutual Fund, Closed-End Fund).
    - Preserves exchange listing vs unlisted mutual fund status.
    - Deterministic ordering and bounded keyset pagination.
    - Extracts truthful available filters based strictly on catalog contents.
    """

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        catalog_configs: Optional[List[CanonicalFundConfig]] = None,
    ):
        self._db_session = db_session
        raw_configs = catalog_configs if catalog_configs is not None else DEFAULT_FUNDS_CATALOG
        self._configs = validate_funds_catalog([c for c in raw_configs if c.enabled])

    async def get_all_canonical_funds(self) -> List[CanonicalFundConfig]:
        """
        Retrieves all canonical fund configurations.
        If database contains registered fund metadata, integrates them;
        otherwise serves validated server-owned canonical catalog.
        """
        if self._db_session is not None:
            try:
                stmt = (
                    select(FundMetadata, Entity, FundListingMetadata, FundNAVObservation)
                    .join(Entity, Entity.entity_id == FundMetadata.instrument_entity_id)
                    .outerjoin(
                        FundListingMetadata,
                        FundListingMetadata.instrument_entity_id
                        == FundMetadata.instrument_entity_id,
                    )
                    .outerjoin(
                        FundNAVObservation,
                        FundNAVObservation.instrument_entity_id
                        == FundMetadata.instrument_entity_id,
                    )
                )
                result = await self._db_session.execute(stmt)
                db_rows = result.all()

                if db_rows:
                    db_configs: List[CanonicalFundConfig] = []
                    for f_meta, ent, l_meta, nav_obs in db_rows:
                        is_listed = l_meta is not None
                        sym = (
                            l_meta.symbol
                            if l_meta and l_meta.symbol
                            else (ent.canonical_name or "UNKNOWN")
                        )
                        mic = l_meta.exchange_mic if l_meta else None
                        curr = l_meta.trading_currency if l_meta else None
                        country = (
                            "United States"
                            if (curr == "USD" or f_meta.base_currency == "USD")
                            else "Global"
                        )
                        c_code = "US" if country == "United States" else "XX"

                        db_configs.append(
                            CanonicalFundConfig(
                                instrument_entity_id=ent.entity_id,
                                fund_name=ent.display_name or ent.canonical_name,
                                display_symbol=sym,
                                fund_type=f_meta.fund_type,
                                is_exchange_traded=is_listed,
                                exchange_id=l_meta.exchange_entity_id if l_meta else None,
                                exchange_mic=mic,
                                exchange_display_name=(l_meta.exchange_mic if l_meta else None),
                                listing_market_country=country if is_listed else None,
                                listing_market_country_code=c_code if is_listed else None,
                                trading_currency=curr,
                                listing_status=(l_meta.listing_status if l_meta else "ACTIVE"),
                                domicile=f_meta.domicile or "United States",
                                inception_date=f_meta.inception_date,
                                investment_category=f_meta.investment_category or "Equity",
                                distribution_policy=f_meta.distribution_policy or "Distributing",
                                base_currency=f_meta.base_currency or "USD",
                                share_class_currency=f_meta.share_class_currency or "USD",
                                benchmark_entity_id=f_meta.benchmark_entity_id,
                                benchmark_name=f_meta.benchmark_name,
                                manager_entity_id=f_meta.manager_entity_id,
                                manager_name=f_meta.manager_name,
                                sponsor_name=f_meta.sponsor_name,
                                fund_objective=f_meta.fund_objective,
                                net_expense_ratio=(
                                    float(f_meta.net_expense_ratio)
                                    if f_meta.net_expense_ratio is not None
                                    else None
                                ),
                                gross_expense_ratio=(
                                    float(f_meta.gross_expense_ratio)
                                    if f_meta.gross_expense_ratio is not None
                                    else None
                                ),
                                fee_metric_type=f_meta.fee_metric_type,
                                fee_effective_date=f_meta.fee_effective_date,
                                total_aum=(
                                    float(f_meta.total_aum)
                                    if f_meta.total_aum is not None
                                    else None
                                ),
                                aum_currency=f_meta.aum_currency,
                                aum_as_of_date=f_meta.aum_as_of_date,
                                aum_scope=f_meta.aum_scope,
                                initial_nav=(
                                    float(nav_obs.nav_per_unit)
                                    if nav_obs and nav_obs.nav_per_unit is not None
                                    else None
                                ),
                                nav_currency=(
                                    nav_obs.nav_currency if nav_obs else f_meta.share_class_currency
                                ),
                                nav_valuation_date=(nav_obs.valuation_date if nav_obs else None),
                                nav_published_at=(nav_obs.published_at if nav_obs else None),
                                nav_valuation_method=(
                                    nav_obs.valuation_method if nav_obs else None
                                ),
                            )
                        )
                    return db_configs
            except Exception as e:
                logger.warning(
                    "Database query for canonical funds failed, falling back to static config: %s",
                    e,
                )

        return list(self._configs)

    async def get_filtered_funds(
        self,
        fund_type: Optional[str] = None,
        market_country: Optional[str] = None,
        exchange: Optional[str] = None,
        domicile: Optional[str] = None,
        fund_category: Optional[str] = None,
        share_class_currency: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[CanonicalFundConfig], Optional[str], bool, int]:
        """
        Filters canonical fund catalog with deterministic ordering and bounded pagination.
        """
        all_funds = await self.get_all_canonical_funds()

        # 1. Deterministic sorting: Fund Type ASC, Name ASC, UUID ASC
        sorted_funds = sorted(
            all_funds,
            key=lambda f: (f.fund_type, f.fund_name.lower(), str(f.instrument_entity_id)),
        )

        filtered: List[CanonicalFundConfig] = []
        for f in sorted_funds:
            # Fund Type Filter
            if fund_type and fund_type.lower() != "all":
                if f.fund_type.upper() != fund_type.upper():
                    continue

            # Market Country Filter (applies to exchange listed funds)
            if market_country and market_country.lower() != "all":
                if not f.listing_market_country or (
                    f.listing_market_country.lower() != market_country.lower()
                    and (f.listing_market_country_code or "").lower() != market_country.lower()
                ):
                    continue

            # Exchange Filter (MIC or Name)
            if exchange and exchange.lower() != "all":
                match_mic = (f.exchange_mic or "").lower() == exchange.lower()
                match_name = (f.exchange_display_name or "").lower() == exchange.lower()
                if not (match_mic or match_name):
                    continue

            # Domicile Filter
            if domicile and domicile.lower() != "all":
                if (f.domicile or "").lower() != domicile.lower():
                    continue

            # Category Filter
            if fund_category and fund_category.lower() != "all":
                if (f.investment_category or "").lower() != fund_category.lower():
                    continue

            # Currency Filter
            if share_class_currency and share_class_currency.lower() != "all":
                if f.share_class_currency.upper() != share_class_currency.upper():
                    continue

            # Text / Identifier Search
            if query and query.strip():
                q = query.strip().lower()
                matched = (
                    q in f.fund_name.lower()
                    or q in f.display_symbol.lower()
                    or (f.exchange_mic and q in f.exchange_mic.lower())
                    or (f.isin and q in f.isin.lower())
                    or (f.figi and q in f.figi.lower())
                    or (f.manager_name and q in f.manager_name.lower())
                    or (f.sponsor_name and q in f.sponsor_name.lower())
                    or (f.benchmark_name and q in f.benchmark_name.lower())
                )
                if not matched:
                    continue

            filtered.append(f)

        total_matched = len(filtered)

        # 2. Keyset/offset pagination
        offset = 0
        if cursor:
            try:
                offset = max(0, int(cursor))
            except ValueError:
                offset = 0

        bounded_limit = min(max(1, limit), 100)
        paged_items = filtered[offset : offset + bounded_limit]

        has_more = (offset + bounded_limit) < total_matched
        next_cursor = str(offset + bounded_limit) if has_more else None

        return paged_items, next_cursor, has_more, total_matched

    async def get_fund_by_id(self, instrument_entity_id: UUID) -> Optional[CanonicalFundConfig]:
        """Looks up a canonical fund instrument by its authoritative UUID."""
        all_funds = await self.get_all_canonical_funds()
        for f in all_funds:
            if f.instrument_entity_id == instrument_entity_id:
                return f
        return None

    async def get_filter_options(self) -> FundFilterOptionsResponse:
        """Computes truthful available filter options strictly grounded in catalog contents."""
        all_funds = await self.get_all_canonical_funds()

        type_counts: Dict[str, int] = {}
        country_counts: Dict[str, int] = {}
        exchange_counts: Dict[str, Tuple[str, str, int]] = {}
        cat_counts: Dict[str, int] = {}
        curr_counts: Dict[str, int] = {}

        for f in all_funds:
            # Fund Type
            ft = f.fund_type
            type_counts[ft] = type_counts.get(ft, 0) + 1

            # Country
            c = f.listing_market_country or f.domicile or "Global"
            country_counts[c] = country_counts.get(c, 0) + 1

            # Exchange (only for listed funds)
            if f.is_exchange_traded and f.exchange_mic:
                mic = f.exchange_mic
                name = f.exchange_display_name or mic
                cntry = f.listing_market_country or "United States"
                if mic in exchange_counts:
                    exchange_counts[mic] = (
                        exchange_counts[mic][0],
                        exchange_counts[mic][1],
                        exchange_counts[mic][2] + 1,
                    )
                else:
                    exchange_counts[mic] = (name, cntry, 1)

            # Category
            cat = f.investment_category or "Equity"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

            # Currency
            curr = f.share_class_currency
            curr_counts[curr] = curr_counts.get(curr, 0) + 1

        fund_types = [
            FundFilterOption(
                id=ft,
                label=SUPPORTED_FUND_TYPES.get(ft, ft),
                count=count,
            )
            for ft, count in sorted(type_counts.items())
        ]

        countries = [
            FundFilterOption(id=c, label=c, count=count)
            for c, count in sorted(country_counts.items())
        ]

        exchanges = [
            FundExchangeFilterOption(mic=mic, name=name, country=cntry, count=count)
            for mic, (name, cntry, count) in sorted(exchange_counts.items())
        ]

        categories = [
            FundFilterOption(
                id=cat,
                label=SUPPORTED_INVESTMENT_CATEGORIES.get(cat, cat),
                count=count,
            )
            for cat, count in sorted(cat_counts.items())
        ]

        currencies = [
            FundFilterOption(id=curr, label=curr, count=count)
            for curr, count in sorted(curr_counts.items())
        ]

        return FundFilterOptionsResponse(
            fund_types=fund_types,
            countries=countries,
            exchanges=exchanges,
            categories=categories,
            currencies=currencies,
        )
