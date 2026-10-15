"""Authoritative FX Directory Repository for ATLAS FX Markets V1 (Stage 59)."""

import logging
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .config import (
    DEFAULT_FX_CATALOG,
    ISO_4217_REGISTRY,
    CanonicalFxPairConfig,
    validate_fx_catalog,
)
from .models import CurrencyItem

logger = logging.getLogger(__name__)


class FxDirectoryRepository:
    """
    Authoritative catalog repository for Spot Currency Pairs.

    Guarantees:
    - 100% Read-Only: 0 writes to PostgreSQL, 0 provider calls on read.
    - Grounded in canonical Financial Instrument UUIDs.
    - Strictly preserves base currency vs quote currency semantics (BASE/QUOTE).
    - Deterministic ordering and bounded keyset pagination.
    - Currency lookup strictly backed by validated ISO 4217 fiat registry.
    """

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        catalog_configs: Optional[List[CanonicalFxPairConfig]] = None,
    ):
        self._db_session = db_session
        raw_configs = catalog_configs if catalog_configs is not None else DEFAULT_FX_CATALOG
        validate_fx_catalog(raw_configs)
        self._configs = list(raw_configs)
        self._by_id: Dict[UUID, CanonicalFxPairConfig] = {
            item.instrument_entity_id: item for item in self._configs
        }
        self._by_pair: Dict[Tuple[str, str], CanonicalFxPairConfig] = {
            (item.base_currency, item.quote_currency): item for item in self._configs
        }

    async def get_all_pairs(self) -> List[CanonicalFxPairConfig]:
        """Retrieves all configured canonical spot FX pairs."""
        return list(self._configs)

    async def get_pair_by_id(self, instrument_entity_id: UUID) -> Optional[CanonicalFxPairConfig]:
        """Lookup canonical pair by instrument UUID."""
        return self._by_id.get(instrument_entity_id)

    async def get_pair_by_currencies(
        self, base: str, quote: str
    ) -> Optional[CanonicalFxPairConfig]:
        """Lookup canonical direct pair by base and quote currency codes."""
        return self._by_pair.get((base.upper(), quote.upper()))

    async def get_supported_currencies(self) -> List[CurrencyItem]:
        """Return all distinct validated currencies represented in the FX catalog."""
        represented_codes = set()
        for p in self._configs:
            represented_codes.add(p.base_currency)
            represented_codes.add(p.quote_currency)

        result: List[CurrencyItem] = []
        for code in sorted(represented_codes):
            meta = ISO_4217_REGISTRY.get(code)
            if meta:
                result.append(
                    CurrencyItem(
                        code=meta.code,
                        name=meta.name,
                        symbol=meta.symbol,
                        minor_units=meta.minor_units,
                        country_or_region=meta.country_or_region,
                    )
                )
        return result

    async def list_pairs(
        self,
        base_currency: Optional[str] = None,
        quote_currency: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[CanonicalFxPairConfig], int, Optional[str], bool]:
        """
        Filters, sorts, and paginates canonical spot currency pairs.

        Returns: (items, total_filtered_count, next_cursor, has_more)
        """
        filtered = self._configs

        if base_currency:
            b_norm = base_currency.strip().upper()
            filtered = [p for p in filtered if p.base_currency == b_norm]

        if quote_currency:
            q_norm = quote_currency.strip().upper()
            filtered = [p for p in filtered if p.quote_currency == q_norm]

        if query:
            q_clean = query.strip().lower().replace("/", "").replace("_", "").replace("-", "")
            q_raw = query.strip().lower()

            def matches(p: CanonicalFxPairConfig) -> bool:
                # Direct symbol match e.g. "EUR/USD" or "EURUSD"
                pair_compact = p.display_pair.lower().replace("/", "")
                if q_clean and (
                    q_clean in pair_compact
                    or q_clean == p.base_currency.lower()
                    or q_clean == p.quote_currency.lower()
                ):
                    return True
                # Match aliases
                for alias in p.provider_aliases:
                    if q_clean in alias.lower().replace("_", "").replace("-", ""):
                        return True
                # Match currency names e.g. "Euro", "Yen", "Dollar"
                base_meta = ISO_4217_REGISTRY.get(p.base_currency)
                if base_meta and q_raw in base_meta.name.lower():
                    return True
                quote_meta = ISO_4217_REGISTRY.get(p.quote_currency)
                if quote_meta and q_raw in quote_meta.name.lower():
                    return True
                return False

            filtered = [p for p in filtered if matches(p)]

        # Deterministic sorting by base_currency, quote_currency, instrument_entity_id
        filtered.sort(
            key=lambda p: (p.base_currency, p.quote_currency, str(p.instrument_entity_id))
        )

        total_count = len(filtered)
        start_idx = 0
        if cursor:
            try:
                start_idx = max(0, int(cursor))
            except ValueError:
                # If cursor is a display_pair or token, find index
                for idx, p in enumerate(filtered):
                    if p.display_pair == cursor:
                        start_idx = idx + 1
                        break

        bounded_limit = max(1, min(limit, 100))
        page_items = filtered[start_idx : start_idx + bounded_limit]
        has_more = (start_idx + len(page_items)) < total_count
        next_cursor = str(start_idx + len(page_items)) if has_more else None

        return page_items, total_count, next_cursor, has_more
