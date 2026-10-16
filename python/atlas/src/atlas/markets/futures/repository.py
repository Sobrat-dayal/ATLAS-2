"""Repository layer for ATLAS Futures & Commodities Markets V1 (Stage 62).

Provides in-memory catalog query, deterministic keyset pagination, multi-dimensional filtering,
and coverage computation across commodities, products, and contracts.
"""

import base64
import json
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from .config import (
    CANONICAL_FUTURES_CONTRACTS,
    COMMODITIES_BY_ID,
    FUTURES_PRODUCTS_BY_ID,
    SPOT_BENCHMARKS_BY_ID,
    CanonicalFuturesContractConfig,
    CommoditySpotBenchmarkConfig,
    CommodityUnderlyingConfig,
    ContractLifecycleEnum,
    FuturesProductConfig,
)
from .models import FuturesCoverageSummary, FuturesFilterOptionsResponse


class FuturesMarketRepository:
    """Repository accessing the canonical ATLAS Futures & Commodities catalog."""

    def __init__(
        self,
        contracts: Optional[List[CanonicalFuturesContractConfig]] = None,
        products: Optional[Dict[UUID, FuturesProductConfig]] = None,
        commodities: Optional[Dict[UUID, CommodityUnderlyingConfig]] = None,
        spot_benchmarks: Optional[Dict[UUID, CommoditySpotBenchmarkConfig]] = None,
    ) -> None:
        self._contracts = list(contracts or CANONICAL_FUTURES_CONTRACTS)
        self._products = dict(products or FUTURES_PRODUCTS_BY_ID)
        self._commodities = dict(commodities or COMMODITIES_BY_ID)
        self._spot_benchmarks = dict(spot_benchmarks or SPOT_BENCHMARKS_BY_ID)

    def get_contract_by_id(
        self, instrument_entity_id: UUID
    ) -> Optional[CanonicalFuturesContractConfig]:
        """Lookup canonical futures contract by its Financial Instrument UUID."""
        for c in self._contracts:
            if c.instrument_entity_id == instrument_entity_id:
                return c
        return None

    def get_product_by_id(self, product_entity_id: UUID) -> Optional[FuturesProductConfig]:
        """Lookup futures product specification by Product Entity UUID."""
        return self._products.get(product_entity_id)

    def get_commodity_by_id(self, commodity_entity_id: UUID) -> Optional[CommodityUnderlyingConfig]:
        """Lookup underlying commodity by Commodity Entity UUID."""
        return self._commodities.get(commodity_entity_id)

    def list_commodities(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[CommodityUnderlyingConfig]:
        """List canonical underlying commodities with optional filtering."""
        items = list(self._commodities.values())

        if category:
            cat_clean = category.strip().lower()
            items = [c for c in items if c.category.value == cat_clean]

        if query:
            q_clean = query.strip().lower()
            items = [
                c
                for c in items
                if q_clean in c.name.lower()
                or q_clean in c.slug.lower()
                or (c.reference_region and q_clean in c.reference_region.lower())
            ]

        # Deterministic sorting
        items.sort(key=lambda c: (c.category.value, c.name))
        return items

    def list_products_for_commodity(self, commodity_entity_id: UUID) -> List[FuturesProductConfig]:
        """Return all futures products associated with a specific underlying commodity."""
        return [p for p in self._products.values() if p.underlying_entity_id == commodity_entity_id]

    def list_contracts_for_product(
        self, product_entity_id: UUID
    ) -> List[CanonicalFuturesContractConfig]:
        """Return all listed contracts associated with a specific futures product."""
        return [c for c in self._contracts if c.product_entity_id == product_entity_id]

    def list_spot_benchmarks(self) -> List[CommoditySpotBenchmarkConfig]:
        """Return all cataloged physical spot benchmarks."""
        items = list(self._spot_benchmarks.values())
        items.sort(key=lambda b: b.name)
        return items

    def list_contracts(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        exchange: Optional[str] = None,
        product_entity_id: Optional[UUID] = None,
        root_symbol: Optional[str] = None,
        contract_month: Optional[str] = None,
        settlement_type: Optional[str] = None,
        lifecycle_status: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[CanonicalFuturesContractConfig], int, Optional[str], bool]:
        """Filter and paginate canonical futures contracts using keyset cursor pagination."""
        items = list(self._contracts)

        # 1. Text search
        if query:
            q_clean = query.strip().lower()
            filtered = []
            for c in items:
                prod = self._products.get(c.product_entity_id)
                und = self._commodities.get(c.underlying_entity_id)

                match_symbol = q_clean in c.symbol.lower()
                match_name = q_clean in c.name.lower()
                match_exchange = q_clean in c.exchange.lower() or q_clean in c.exchange_mic.lower()
                match_month = q_clean in c.contract_month.lower()
                match_prod = prod and (
                    q_clean in prod.root_symbol.lower() or q_clean in prod.name.lower()
                )
                match_und = und and (q_clean in und.name.lower() or q_clean in und.slug.lower())

                if (
                    match_symbol
                    or match_name
                    or match_exchange
                    or match_month
                    or match_prod
                    or match_und
                ):
                    filtered.append(c)
            items = filtered

        # 2. Filter by commodity category
        if category:
            cat_clean = category.strip().lower()
            filtered = []
            for c in items:
                prod = self._products.get(c.product_entity_id)
                if prod and prod.category.value == cat_clean:
                    filtered.append(c)
            items = filtered

        # 3. Filter by exchange
        if exchange:
            ex_clean = exchange.strip().upper()
            items = [
                c
                for c in items
                if c.exchange.upper() == ex_clean or c.exchange_mic.upper() == ex_clean
            ]

        # 4. Filter by product entity ID
        if product_entity_id:
            items = [c for c in items if c.product_entity_id == product_entity_id]

        # 5. Filter by root symbol
        if root_symbol:
            rs_clean = root_symbol.strip().upper()
            filtered = []
            for c in items:
                prod = self._products.get(c.product_entity_id)
                if prod and prod.root_symbol.upper() == rs_clean:
                    filtered.append(c)
            items = filtered

        # 6. Filter by contract month (YYYY-MM)
        if contract_month:
            cm_clean = contract_month.strip()
            items = [c for c in items if c.contract_month == cm_clean]

        # 7. Filter by settlement type
        if settlement_type:
            st_clean = settlement_type.strip().lower()
            items = [c for c in items if c.settlement_type.value == st_clean]

        # 8. Filter by lifecycle status
        if lifecycle_status:
            ls_clean = lifecycle_status.strip().lower()
            items = [c for c in items if c.lifecycle_status.value == ls_clean]

        # Deterministic sorting: Category -> Product Root -> Expiration Date -> Symbol
        def sort_key(c: CanonicalFuturesContractConfig):
            prod = self._products.get(c.product_entity_id)
            cat = prod.category.value if prod else ""
            root = prod.root_symbol if prod else ""
            return (cat, root, c.expiration_date, c.symbol)

        items.sort(key=sort_key)

        total_matches = len(items)

        # Decode pagination cursor
        offset = self._decode_cursor(cursor)
        bounded_limit = min(max(1, limit), 100)

        paged_items = items[offset : offset + bounded_limit]
        has_more = (offset + bounded_limit) < total_matches
        next_cursor = self._encode_cursor(offset + bounded_limit) if has_more else None

        return paged_items, total_matches, next_cursor, has_more

    def get_coverage_summary(self) -> FuturesCoverageSummary:
        """Compute live coverage counts across the canonical futures catalog."""
        total_commodities = len(self._commodities)
        total_products = len(self._products)
        total_contracts = len(self._contracts)
        active_contracts = sum(
            1 for c in self._contracts if c.lifecycle_status == ContractLifecycleEnum.ACTIVE
        )
        contracts_with_last = sum(1 for c in self._contracts if c.latest_trade_price is not None)
        contracts_with_settlement = sum(
            1 for c in self._contracts if c.official_settlement is not None
        )
        contracts_with_volume = sum(
            1 for c in self._contracts if c.volume is not None and c.volume > 0
        )
        contracts_with_open_interest = sum(
            1 for c in self._contracts if c.open_interest is not None and c.open_interest > 0
        )

        exchanges = sorted(list(set(c.exchange for c in self._contracts)))

        return FuturesCoverageSummary(
            total_commodities=total_commodities,
            total_products=total_products,
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            contracts_with_last=contracts_with_last,
            contracts_with_settlement=contracts_with_settlement,
            contracts_with_volume=contracts_with_volume,
            contracts_with_open_interest=contracts_with_open_interest,
            exchanges_represented=exchanges,
        )

    def get_filter_options(self) -> FuturesFilterOptionsResponse:
        """Derive distinct categories, exchanges, products, and contract months."""
        categories = sorted(list(set(c.category.value for c in self._commodities.values())))
        exchanges = sorted(list(set(c.exchange for c in self._contracts)))

        products = []
        for p in sorted(self._products.values(), key=lambda x: (x.category.value, x.root_symbol)):
            products.append(
                {
                    "product_entity_id": str(p.product_entity_id),
                    "root_symbol": p.root_symbol,
                    "name": p.name,
                    "exchange": p.exchange,
                    "category": p.category.value,
                }
            )

        months = sorted(list(set(c.contract_month for c in self._contracts)))
        settlement_types = sorted(list(set(c.settlement_type.value for c in self._contracts)))
        lifecycle_statuses = sorted(list(set(c.lifecycle_status.value for c in self._contracts)))

        coverage = self.get_coverage_summary()

        return FuturesFilterOptionsResponse(
            categories=categories,
            exchanges=exchanges,
            products=products,
            months=months,
            settlement_types=settlement_types,
            lifecycle_statuses=lifecycle_statuses,
            coverage=coverage,
        )

    def _encode_cursor(self, offset: int) -> str:
        payload = json.dumps({"offset": offset})
        return base64.b64encode(payload.encode("utf-8")).decode("utf-8")

    def _decode_cursor(self, cursor_str: Optional[str]) -> int:
        if not cursor_str:
            return 0
        try:
            decoded = base64.b64decode(cursor_str.encode("utf-8")).decode("utf-8")
            data = json.loads(decoded)
            return int(data.get("offset", 0))
        except Exception:
            return 0
