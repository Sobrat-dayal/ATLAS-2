"""HomeMarketSummaryService - Read-only composition service for Stage 52."""

import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity
from atlas.market_data.freshness.enums import MarketDataFreshnessStatus
from atlas.market_data.freshness.models import MarketDataFreshnessState
from atlas.market_data.freshness.query import MarketDataFreshnessQueryService
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.realtime.websocket.models import QuoteSubscriptionKey

from .config import (
    DEFAULT_MARKET_SUMMARY_INSTRUMENTS,
    MarketSummaryInstrumentConfig,
    validate_market_summary_config,
)
from .models import (
    HomeMarketSummaryCoverage,
    HomeMarketSummaryItem,
    HomeMarketSummaryResponse,
    MarketSummaryChangeDirection,
    MarketSummaryDataStatus,
    MarketSummaryDeliveryDelay,
)
from .reference_close import ReferenceCloseResolver, calculate_market_changes

logger = logging.getLogger(__name__)

# Human-readable provider mapping for safe provenance
KNOWN_PROVIDER_NAMES = {
    "openbb": "OpenBB Financial Platform",
    "fmp": "Financial Modeling Prep",
    "polygon": "Polygon.io",
    "yfinance": "Yahoo Finance Feed",
    "binance": "Binance Spot Feed",
    "coinbase": "Coinbase Exchange Feed",
    "unknown": "Market Data Engine",
}


class HomeMarketSummaryService:
    """
    Assembles real-time Market Summary for ATLAS Home.

    Guarantees:
    - 100% Read-Only:
        * PostgreSQL writes: 0
        * Redis writes: 0
        * ClickHouse writes: 0
        * Provider external HTTP/stream calls: 0
    - Canonical UUID identity authority.
    - True data transparency: Missing quotes are marked unavailable, never faked.
    - Full Decimal precision preserved without floating-point math loss.
    - Stage 44 Market Data Freshness reuse.
    """

    def __init__(
        self,
        quote_service: Optional[LiveQuoteService] = None,
        freshness_query_service: Optional[MarketDataFreshnessQueryService] = None,
        db_session: Optional[AsyncSession] = None,
        ch_client_factory: Optional[object] = None,
        instrument_configs: Optional[List[MarketSummaryInstrumentConfig]] = None,
    ):
        self._quote_service = quote_service
        self._freshness_query_service = freshness_query_service
        self._db_session = db_session
        self._ch_client_factory = ch_client_factory
        self._reference_resolver = ReferenceCloseResolver(ch_client_factory)

        raw_configs = (
            instrument_configs
            if instrument_configs is not None
            else DEFAULT_MARKET_SUMMARY_INSTRUMENTS
        )
        self._configs = validate_market_summary_config([c for c in raw_configs if c.enabled])

    async def get_market_summary(self) -> HomeMarketSummaryResponse:
        """
        Retrieves canonical summary observations for all configured instruments.
        """
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        if not self._configs:
            logger.info("HomeMarketSummaryService: No instruments configured.")
            return HomeMarketSummaryResponse(
                schema_version=1,
                generated_at=now,
                items=[],
                coverage=HomeMarketSummaryCoverage(
                    configured_count=0,
                    available_count=0,
                    unavailable_count=0,
                ),
            )

        # 1. Bounded batch query: Retrieve latest quote records from Valkey/Redis
        configured_ids = [c.instrument_entity_id for c in self._configs]
        quote_records: List[Optional[QuoteCacheRecord]] = []

        if self._quote_service is not None:
            try:
                quote_records = await self._quote_service.get_latest_quotes(configured_ids)
            except Exception as e:
                logger.error("Failed to query latest quotes from LiveQuoteService: %s", e)
                quote_records = [None] * len(configured_ids)
        else:
            quote_records = [None] * len(configured_ids)

        # 2. Optional batch lookup of Entity metadata from PostgreSQL
        entity_name_map = {}
        if self._db_session is not None:
            try:
                stmt = select(Entity.entity_id, Entity.display_name).where(
                    Entity.entity_id.in_(configured_ids)
                )
                res = await self._db_session.execute(stmt)
                for eid, dname in res.all():
                    if dname:
                        entity_name_map[eid] = dname
            except Exception as e:
                logger.warning(
                    "Optional PostgreSQL entity metadata lookup failed (proceeding): %s", e
                )

        # 3. Assemble observations for each configured instrument
        items: List[HomeMarketSummaryItem] = []
        available_count = 0

        for config, quote_record in zip(self._configs, quote_records):
            display_name = entity_name_map.get(config.instrument_entity_id, config.display_name)

            if quote_record is None:
                # Honest unavailable state - never fabricate price
                items.append(
                    HomeMarketSummaryItem(
                        instrument_entity_id=config.instrument_entity_id,
                        display_name=display_name,
                        display_symbol=config.display_symbol,
                        instrument_category=config.instrument_category,
                        value_kind=config.value_kind,
                        quote_currency=config.quote_currency,
                        quote_unit=config.quote_unit,
                        data_status=MarketSummaryDataStatus.NO_QUOTE,
                        freshness_status="unavailable",
                        delivery_delay_status=MarketSummaryDeliveryDelay.UNKNOWN,
                        change_direction=MarketSummaryChangeDirection.UNKNOWN,
                        unavailable_reason="No live quote observation stored in ATLAS state store.",
                    )
                )
                continue

            # We have a quote record from the canonical state store
            quote = quote_record.quote

            # Extract price fields
            # Check if quote has traded price or bid/ask
            last_price_dec: Optional[Decimal] = None
            if hasattr(quote, "last_price") and quote.last_price is not None:
                last_price_dec = Decimal(str(quote.last_price))
            elif hasattr(quote, "price") and quote.price is not None:
                last_price_dec = Decimal(str(quote.price))
            elif (
                hasattr(quote, "bid_price")
                and quote.bid_price is not None
                and hasattr(quote, "ask_price")
                and quote.ask_price is not None
            ):
                # If only bid/ask available, we report them cleanly
                # Note: Prompt Section 31 bans silent midpoint substitution as traded price
                last_price_dec = None
            elif hasattr(quote, "ask_price") and quote.ask_price is not None:
                last_price_dec = None
            elif hasattr(quote, "bid_price") and quote.bid_price is not None:
                last_price_dec = None

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

            # 4. Resolve reference close
            (
                ref_close_dec,
                ref_date,
                ref_source,
            ) = await self._reference_resolver.resolve_reference_close(
                instrument_id=config.instrument_entity_id,
            )

            # 5. Calculate change if reference exists
            abs_change, pct_change, change_direction = calculate_market_changes(
                last_price=last_price_dec,
                reference_close=ref_close_dec,
            )

            # 6. Freshness & delay via Stage 44
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

            # Provenance
            provider_display_name = KNOWN_PROVIDER_NAMES.get(provider_key, provider_key.title())

            # Data status
            data_status = MarketSummaryDataStatus.AVAILABLE
            available_count += 1

            items.append(
                HomeMarketSummaryItem(
                    instrument_entity_id=config.instrument_entity_id,
                    display_name=display_name,
                    display_symbol=config.display_symbol,
                    instrument_category=config.instrument_category,
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
                    data_status=data_status,
                    unavailable_reason=None,
                )
            )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        unavailable_count = len(self._configs) - available_count

        logger.info(
            "HomeMarketSummary assembled: %d configured, %d available, %d unavailable in %.2fms",
            len(self._configs),
            available_count,
            unavailable_count,
            duration_ms,
        )

        return HomeMarketSummaryResponse(
            schema_version=1,
            generated_at=now,
            items=items,
            coverage=HomeMarketSummaryCoverage(
                configured_count=len(self._configs),
                available_count=available_count,
                unavailable_count=unavailable_count,
            ),
        )
