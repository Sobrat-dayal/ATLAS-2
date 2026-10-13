"""MarketsOverviewService - Read-only composition service for Markets Overview V1 (Stage 56)."""

import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity
from atlas.home.market_summary.models import (
    MarketSummaryChangeDirection,
    MarketSummaryDataStatus,
    MarketSummaryDeliveryDelay,
)
from atlas.home.market_summary.reference_close import (
    ReferenceCloseResolver,
    calculate_market_changes,
)
from atlas.home.market_summary.service import KNOWN_PROVIDER_NAMES
from atlas.market_data.freshness.enums import MarketDataFreshnessStatus
from atlas.market_data.freshness.models import MarketDataFreshnessState
from atlas.market_data.freshness.query import MarketDataFreshnessQueryService
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.realtime.websocket.models import QuoteSubscriptionKey

from .config import (
    DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS,
    MARKET_GROUPS_ALLOWLIST,
    MarketsOverviewInstrumentConfig,
    validate_markets_overview_config,
)
from .models import (
    MarketGroupSummary,
    MarketsOverviewCoverage,
    MarketsOverviewItem,
    MarketsOverviewResponse,
)

logger = logging.getLogger(__name__)

# Canonical human labels for market groups
GROUP_LABELS: Dict[str, str] = {
    "all": "All",
    "benchmarks": "Benchmarks",
    "equities": "Equities",
    "etfs": "ETFs & Funds",
    "fx": "FX",
    "crypto": "Cryptocurrency",
    "commodities": "Commodities",
    "bonds": "Bonds & Rates",
}


class MarketsOverviewService:
    """
    Assembles multi-asset market overview for ATLAS Markets (/markets, Module 2).

    Guarantees:
    - 100% Read-Only:
        * PostgreSQL writes: 0
        * Redis writes: 0
        * ClickHouse writes: 0
        * Provider external HTTP/stream calls: 0
    - Canonical UUID identity authority.
    - True data transparency: Missing quotes are marked unavailable, never faked.
    - Full Decimal precision preserved without floating-point math loss.
    - Reuses Stage 52 reference close & calculation logic and Stage 44 freshness.
    """

    def __init__(
        self,
        quote_service: Optional[LiveQuoteService] = None,
        freshness_query_service: Optional[MarketDataFreshnessQueryService] = None,
        db_session: Optional[AsyncSession] = None,
        ch_client_factory: Optional[object] = None,
        instrument_configs: Optional[List[MarketsOverviewInstrumentConfig]] = None,
    ):
        self._quote_service = quote_service
        self._freshness_query_service = freshness_query_service
        self._db_session = db_session
        self._ch_client_factory = ch_client_factory
        self._reference_resolver = ReferenceCloseResolver(ch_client_factory)

        raw_configs = (
            instrument_configs
            if instrument_configs is not None
            else DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS
        )
        self._configs = validate_markets_overview_config([c for c in raw_configs if c.enabled])

    async def get_markets_overview(
        self,
        group: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
        featured_only: bool = False,
    ) -> MarketsOverviewResponse:
        """
        Retrieves canonical overview observations for configured market instruments.
        Supports bounded group filtering and keyset pagination.
        """
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        # 1. Compute group distribution counts across the full active catalog
        group_counts: Dict[str, int] = {g: 0 for g in GROUP_LABELS}
        group_counts["all"] = len(self._configs)
        for cfg in self._configs:
            if cfg.market_group in group_counts:
                group_counts[cfg.market_group] += 1

        groups_summary: List[MarketGroupSummary] = [
            MarketGroupSummary(
                id=g_id,
                label=GROUP_LABELS[g_id],
                count=group_counts.get(g_id, 0),
            )
            for g_id in [
                "all",
                "benchmarks",
                "equities",
                "etfs",
                "fx",
                "crypto",
                "commodities",
                "bonds",
            ]
            if group_counts.get(g_id, 0) > 0 or g_id == "all"
        ]

        # 2. Filter configs by requested group and featured constraint
        filtered_configs = self._configs
        if group and group.lower() != "all":
            norm_group = group.lower()
            if norm_group in MARKET_GROUPS_ALLOWLIST:
                filtered_configs = [c for c in filtered_configs if c.market_group == norm_group]
            else:
                filtered_configs = []

        if featured_only:
            filtered_configs = [c for c in filtered_configs if c.featured]

        # 3. Deterministic pagination slicing
        limit = max(1, min(limit, 100))
        offset = 0
        if cursor and cursor.isdigit():
            offset = max(0, int(cursor))

        total_filtered = len(filtered_configs)
        page_configs = filtered_configs[offset : offset + limit]
        has_more = (offset + limit) < total_filtered
        next_cursor = str(offset + limit) if has_more else None

        # 4. Identify all instruments to query quotes for (current page + all featured instruments)
        featured_configs = [c for c in self._configs if c.featured]
        instruments_to_query_set: Set[UUID] = {c.instrument_entity_id for c in page_configs}
        instruments_to_query_set.update(c.instrument_entity_id for c in featured_configs)
        query_ids_list = list(instruments_to_query_set)

        # 5. Bounded batch query: Retrieve latest quote records from Valkey/Redis
        quote_records_map: Dict[UUID, Optional[QuoteCacheRecord]] = {}
        if self._quote_service is not None and query_ids_list:
            try:
                records = await self._quote_service.get_latest_quotes(query_ids_list)
                for q_id, rec in zip(query_ids_list, records):
                    quote_records_map[q_id] = rec
            except Exception as e:
                logger.error("Failed to query latest quotes from LiveQuoteService: %s", e)
                for q_id in query_ids_list:
                    quote_records_map[q_id] = None
        else:
            for q_id in query_ids_list:
                quote_records_map[q_id] = None

        # 6. Optional batch lookup of Entity metadata from PostgreSQL
        entity_name_map: Dict[UUID, str] = {}
        if self._db_session is not None and query_ids_list:
            try:
                stmt = select(Entity.entity_id, Entity.display_name).where(
                    Entity.entity_id.in_(query_ids_list)
                )
                res = await self._db_session.execute(stmt)
                for eid, dname in res.all():
                    if dname:
                        entity_name_map[eid] = dname
            except Exception as e:
                logger.warning("Optional PostgreSQL entity metadata lookup failed: %s", e)

        # 7. Helper to assemble a single MarketsOverviewItem
        async def assemble_item(config: MarketsOverviewInstrumentConfig) -> MarketsOverviewItem:
            display_name = entity_name_map.get(config.instrument_entity_id, config.display_name)
            quote_record = quote_records_map.get(config.instrument_entity_id)

            if quote_record is None:
                return MarketsOverviewItem(
                    instrument_entity_id=config.instrument_entity_id,
                    display_name=display_name,
                    display_symbol=config.display_symbol,
                    instrument_category=config.instrument_category,
                    market_group=config.market_group,
                    venue=config.venue,
                    value_kind=config.value_kind,
                    quote_currency=config.quote_currency,
                    quote_unit=config.quote_unit,
                    data_status=MarketSummaryDataStatus.NO_QUOTE,
                    freshness_status="unavailable",
                    delivery_delay_status=MarketSummaryDeliveryDelay.UNKNOWN,
                    change_direction=MarketSummaryChangeDirection.UNKNOWN,
                    unavailable_reason="No live quote observation stored in ATLAS state store.",
                    featured=config.featured,
                    display_order=config.display_order,
                )

            quote = quote_record.quote

            # Extract traded price or bid/ask
            last_price_dec: Optional[Decimal] = None
            if hasattr(quote, "last_price") and quote.last_price is not None:
                last_price_dec = Decimal(str(quote.last_price))
            elif hasattr(quote, "price") and quote.price is not None:
                last_price_dec = Decimal(str(quote.price))

            bid_price_dec = (
                Decimal(str(quote.bid_price))
                if getattr(quote, "bid_price", None) is not None
                else None
            )
            ask_price_dec = (
                Decimal(str(quote.ask_price))
                if getattr(quote, "ask_price", None) is not None
                else None
            )

            # Resolve reference close
            (
                ref_close_dec,
                ref_date,
                ref_source,
            ) = await self._reference_resolver.resolve_reference_close(
                instrument_id=config.instrument_entity_id,
            )

            # Calculate change
            abs_change, pct_change, change_direction = calculate_market_changes(
                last_price=last_price_dec,
                reference_close=ref_close_dec,
            )

            # Freshness & delay via Stage 44
            freshness_status_str = "unavailable"
            delivery_delay = MarketSummaryDeliveryDelay.UNKNOWN
            delay_seconds = None
            provider_key = config.provider_hint or "unknown"

            if self._freshness_query_service is not None:
                try:
                    series_key = QuoteSubscriptionKey(
                        instrument_entity_id=config.instrument_entity_id
                    )
                    freshness_state: Optional[
                        MarketDataFreshnessState
                    ] = await self._freshness_query_service.get_freshness(
                        series_key=series_key,
                        fallback_evaluation=True,
                    )
                    if freshness_state:
                        freshness_status_str = freshness_state.status.value
                        delivery_delay = (
                            MarketSummaryDeliveryDelay.DELAYED
                            if freshness_state.provider_delayed
                            else MarketSummaryDeliveryDelay.REALTIME
                        )
                        delay_seconds = freshness_state.provider_delay_seconds
                        provider_key = freshness_state.provider_key or provider_key
                except Exception as e:
                    logger.debug("Freshness lookup exception: %s", e)

            # Fallback freshness heuristics if query service not configured
            if freshness_status_str == "unavailable" and quote_record.source_timestamp:
                age_seconds = (
                    now - quote_record.source_timestamp.replace(tzinfo=timezone.utc)
                ).total_seconds()
                if age_seconds < 300:
                    freshness_status_str = MarketDataFreshnessStatus.FRESH.value
                elif age_seconds < 900:
                    freshness_status_str = MarketDataFreshnessStatus.AGING.value
                else:
                    freshness_status_str = MarketDataFreshnessStatus.STALE.value
                delivery_delay = MarketSummaryDeliveryDelay.REALTIME

            provider_display_name = KNOWN_PROVIDER_NAMES.get(provider_key, provider_key.title())

            return MarketsOverviewItem(
                instrument_entity_id=config.instrument_entity_id,
                display_name=display_name,
                display_symbol=config.display_symbol,
                instrument_category=config.instrument_category,
                market_group=config.market_group,
                venue=config.venue,
                value_kind=config.value_kind,
                quote_currency=config.quote_currency,
                quote_unit=config.quote_unit,
                last_price=str(last_price_dec) if last_price_dec is not None else None,
                bid_price=str(bid_price_dec) if bid_price_dec is not None else None,
                ask_price=str(ask_price_dec) if ask_price_dec is not None else None,
                absolute_change=str(abs_change) if abs_change is not None else None,
                percentage_change=str(pct_change) if pct_change is not None else None,
                change_direction=change_direction,
                source_timestamp=quote_record.source_timestamp,
                received_at=quote_record.received_at,
                freshness_status=freshness_status_str,
                delivery_delay_status=delivery_delay,
                delay_seconds=delay_seconds,
                provider_key=provider_key,
                provider_display_name=provider_display_name,
                reference_close=str(ref_close_dec) if ref_close_dec is not None else None,
                reference_session_date=ref_date,
                reference_source=ref_source,
                data_status=MarketSummaryDataStatus.AVAILABLE,
                unavailable_reason=None,
                featured=config.featured,
                display_order=config.display_order,
            )

        # 8. Assemble paged items and featured items
        items: List[MarketsOverviewItem] = []
        available_count = 0
        for cfg in page_configs:
            item = await assemble_item(cfg)
            if item.data_status == MarketSummaryDataStatus.AVAILABLE:
                available_count += 1
            items.append(item)

        featured_items: List[MarketsOverviewItem] = []
        for f_cfg in featured_configs:
            f_item = await assemble_item(f_cfg)
            featured_items.append(f_item)

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        unavailable_count = len(items) - available_count

        logger.info(
            "MarketsOverview assembled: group=%s, page=%d items, featured=%d in %.2fms",
            group or "all",
            len(items),
            len(featured_items),
            duration_ms,
        )

        return MarketsOverviewResponse(
            schema_version=1,
            generated_at=now,
            scope="configured_overview_universe",
            groups=groups_summary,
            items=items,
            featured_items=featured_items,
            coverage=MarketsOverviewCoverage(
                configured_count=len(self._configs),
                returned_count=len(items),
                available_count=available_count,
                unavailable_count=unavailable_count,
            ),
            next_cursor=next_cursor,
            has_more=has_more,
        )
