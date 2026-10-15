"""EquityDirectoryService and EquityMarketReadService for ATLAS Equities Markets V1 (Stage 57)."""

import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

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

from .config import CanonicalEquityConfig
from .models import (
    EquityCoverageSummary,
    EquityDirectoryFiltersApplied,
    EquityDirectoryItem,
    EquityDirectoryResponse,
    EquityFilterOptionsResponse,
    EquityIdentifierItem,
    EquityIssuerCompanyDetails,
    EquityOverviewDetailResponse,
    EquityVenueDetails,
)
from .repository import EquityDirectoryRepository

logger = logging.getLogger(__name__)


class EquityMarketReadService:
    """
    Retrieves and calculates latest financial market quotes for equity securities.

    Guarantees:
    - 100% Read-Only:
        * 0 Redis writes
        * 0 ClickHouse writes
        * 0 External provider HTTP/stream calls
    - True data transparency: Missing quotes marked unavailable, never faked with 0.
    - Full Decimal precision preserved without floating-point math loss.
    - Reuses Stage 52 reference close & calculation logic and Stage 44 freshness.
    """

    def __init__(
        self,
        quote_service: Optional[LiveQuoteService] = None,
        freshness_query_service: Optional[MarketDataFreshnessQueryService] = None,
        ch_client_factory: Optional[object] = None,
    ):
        self._quote_service = quote_service
        self._freshness_query_service = freshness_query_service
        self._ch_client_factory = ch_client_factory
        self._reference_resolver = ReferenceCloseResolver(ch_client_factory)

    async def enrich_equity_items(
        self, configs: List[CanonicalEquityConfig]
    ) -> List[EquityDirectoryItem]:
        """
        Batches latest quote lookups and reference close resolutions for equity configurations.
        """
        if not configs:
            return []

        now = datetime.now(timezone.utc)
        instrument_ids: List[UUID] = [c.instrument_entity_id for c in configs]

        # 1. Bounded batch query to LiveQuoteStateStore (Valkey/Redis)
        quote_records_map: Dict[UUID, Optional[QuoteCacheRecord]] = {}
        if self._quote_service is not None and instrument_ids:
            try:
                records = await self._quote_service.get_latest_quotes(instrument_ids)
                for q_id, rec in zip(instrument_ids, records):
                    quote_records_map[q_id] = rec
            except Exception as e:
                logger.error("Failed to query latest quotes from LiveQuoteService: %s", e)
                for q_id in instrument_ids:
                    quote_records_map[q_id] = None
        else:
            for q_id in instrument_ids:
                quote_records_map[q_id] = None

        # 2. Assemble presentation items
        items: List[EquityDirectoryItem] = []
        for cfg in configs:
            rec = quote_records_map.get(cfg.instrument_entity_id)

            if rec is None:
                items.append(
                    EquityDirectoryItem(
                        instrument_entity_id=cfg.instrument_entity_id,
                        display_name=cfg.display_name,
                        display_symbol=cfg.display_symbol,
                        equity_subtype=cfg.equity_subtype,
                        equity_subtype_label=cfg.equity_subtype_label,
                        share_class_name=cfg.share_class_name,
                        exchange_id=cfg.exchange_id,
                        exchange_mic=cfg.exchange_mic,
                        exchange_display_name=cfg.exchange_display_name,
                        listing_market_country=cfg.listing_market_country,
                        listing_market_country_code=cfg.listing_market_country_code,
                        trading_currency=cfg.trading_currency,
                        listing_status=cfg.listing_status,
                        issuer_company_entity_id=cfg.issuer_company_entity_id,
                        issuer_company_name=cfg.issuer_company_name,
                        data_status=MarketSummaryDataStatus.NO_QUOTE,
                        freshness_status="unavailable",
                        delivery_delay_status=MarketSummaryDeliveryDelay.UNKNOWN,
                        change_direction=MarketSummaryChangeDirection.UNKNOWN,
                        unavailable_reason="No live quote observation stored in ATLAS state store.",
                    )
                )
                continue

            quote = rec.quote

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
                instrument_id=cfg.instrument_entity_id,
            )

            # Calculate change using Stage 52/56 qualified arithmetic
            abs_change, pct_change, change_direction = calculate_market_changes(
                last_price=last_price_dec,
                reference_close=ref_close_dec,
            )

            # Freshness & delay via Stage 44
            freshness_status_str = "unavailable"
            delivery_delay = MarketSummaryDeliveryDelay.UNKNOWN
            delay_seconds = None
            provider_key = cfg.provider_hint or "unknown"

            if self._freshness_query_service is not None:
                try:
                    series_key = QuoteSubscriptionKey(
                        instrument_entity_id=cfg.instrument_entity_id
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
                    logger.debug(
                        "Freshness lookup exception for equity %s: %s",
                        cfg.display_symbol,
                        e,
                    )

            # Fallback freshness heuristics if query service not configured
            if freshness_status_str == "unavailable" and rec.source_timestamp:
                age_seconds = (
                    now - rec.source_timestamp.replace(tzinfo=timezone.utc)
                ).total_seconds()
                if age_seconds < 300:
                    freshness_status_str = MarketDataFreshnessStatus.FRESH.value
                elif age_seconds < 900:
                    freshness_status_str = MarketDataFreshnessStatus.AGING.value
                else:
                    freshness_status_str = MarketDataFreshnessStatus.STALE.value
                delivery_delay = MarketSummaryDeliveryDelay.REALTIME

            provider_display_name = KNOWN_PROVIDER_NAMES.get(provider_key, provider_key.title())

            items.append(
                EquityDirectoryItem(
                    instrument_entity_id=cfg.instrument_entity_id,
                    display_name=cfg.display_name,
                    display_symbol=cfg.display_symbol,
                    equity_subtype=cfg.equity_subtype,
                    equity_subtype_label=cfg.equity_subtype_label,
                    share_class_name=cfg.share_class_name,
                    exchange_id=cfg.exchange_id,
                    exchange_mic=cfg.exchange_mic,
                    exchange_display_name=cfg.exchange_display_name,
                    listing_market_country=cfg.listing_market_country,
                    listing_market_country_code=cfg.listing_market_country_code,
                    trading_currency=cfg.trading_currency,
                    listing_status=cfg.listing_status,
                    issuer_company_entity_id=cfg.issuer_company_entity_id,
                    issuer_company_name=cfg.issuer_company_name,
                    last_price=str(last_price_dec) if last_price_dec is not None else None,
                    bid_price=str(bid_price_dec) if bid_price_dec is not None else None,
                    ask_price=str(ask_price_dec) if ask_price_dec is not None else None,
                    absolute_change=str(abs_change) if abs_change is not None else None,
                    percentage_change=str(pct_change) if pct_change is not None else None,
                    change_direction=change_direction,
                    source_timestamp=rec.source_timestamp,
                    received_at=rec.received_at,
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
                )
            )

        return items


class EquityDirectoryService:
    """
    Primary coordinator service for ATLAS Equities Markets V1 (Stage 57).

    Guarantees:
    - 100% Read-Only execution (0 PostgreSQL writes, 0 Redis writes, 0 ClickHouse writes).
    - Canonical UUID identity authority (Stage 17).
    - Separation of Security identity from issuer Company identity (Stage 18/23).
    - Bounded directory search and deterministic pagination.
    - True data transparency without fabricated stock observations.
    """

    def __init__(
        self,
        repository: EquityDirectoryRepository,
        market_read_service: EquityMarketReadService,
    ):
        self._repository = repository
        self._market_read_service = market_read_service

    async def get_equity_directory(
        self,
        query: Optional[str] = None,
        market_country: Optional[str] = None,
        exchange: Optional[str] = None,
        equity_type: Optional[str] = None,
        listing_status: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> EquityDirectoryResponse:
        """
        Returns authenticated directory of canonical equity securities with
        real market observations.
        """
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)

        # 1. Query catalog repository
        (
            page_configs,
            total_filtered,
            next_cursor,
            has_more,
        ) = await self._repository.query_directory(
            query=query,
            market_country=market_country,
            exchange=exchange,
            equity_type=equity_type,
            listing_status=listing_status,
            limit=limit,
            cursor=cursor,
        )

        # 2. Enrich with real latest quotes and calculations
        items = await self._market_read_service.enrich_equity_items(page_configs)

        # 3. Compute available filter metadata and overall catalog stats
        available_filters = await self._repository.get_filter_options()
        all_equities = await self._repository.get_all_canonical_equities()

        available_count = sum(
            1 for it in items if it.data_status == MarketSummaryDataStatus.AVAILABLE
        )
        unavailable_count = len(items) - available_count

        coverage = EquityCoverageSummary(
            total_catalog_count=len(all_equities),
            returned_count=len(items),
            exchanges_represented=len(available_filters.exchanges),
            countries_represented=len(available_filters.countries),
            available_quotes_count=available_count,
            unavailable_quotes_count=unavailable_count,
        )

        applied_filters = EquityDirectoryFiltersApplied(
            query=query,
            market_country=market_country,
            exchange=exchange,
            equity_type=equity_type,
            listing_status=listing_status,
        )

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(
            "EquityDirectory assembled: query=%s, page=%d items in %.2fms",
            query or "none",
            len(items),
            duration_ms,
        )

        return EquityDirectoryResponse(
            schema_version=1,
            generated_at=now,
            scope="authorized_canonical_equity_directory",
            filters=applied_filters,
            coverage=coverage,
            available_filters=available_filters,
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_equity_filter_options(self) -> EquityFilterOptionsResponse:
        """Returns dynamically computed filter choices grounded strictly in catalog contents."""
        return await self._repository.get_filter_options()

    async def get_equity_detail(
        self, instrument_entity_id: UUID
    ) -> Optional[EquityOverviewDetailResponse]:
        """
        Retrieves detailed Security Overview inspector model for a single canonical equity.
        """
        cfg = await self._repository.get_by_instrument_id(instrument_entity_id)
        if cfg is None:
            return None

        # Enrich item
        items = await self._market_read_service.enrich_equity_items([cfg])
        if not items:
            return None
        item = items[0]

        # Universal identifiers (Stage 21)
        identifiers = [
            EquityIdentifierItem(
                scheme_key="ticker",
                value=cfg.display_symbol,
                is_current=True,
            )
        ]

        # Verified Issuer Company details (Stage 18/23)
        issuer_company = None
        if cfg.issuer_company_entity_id:
            issuer_company = EquityIssuerCompanyDetails(
                company_entity_id=cfg.issuer_company_entity_id,
                legal_name=cfg.issuer_legal_name or cfg.issuer_company_name,
                short_name=cfg.issuer_company_name,
                organization_type=cfg.issuer_organization_type or "public_company",
                status="active",
                website_url=cfg.issuer_website_url,
                primary_country=cfg.issuer_country or cfg.listing_market_country,
            )

        # Venue details
        venue_details = EquityVenueDetails(
            exchange_id=cfg.exchange_id,
            name=cfg.exchange_display_name,
            mic=cfg.exchange_mic,
            timezone_name="America/New_York" if cfg.exchange_mic in ("XNAS", "XNYS") else "UTC",
            exchange_kind="stock_exchange",
            country_name=cfg.listing_market_country,
            country_code=cfg.listing_market_country_code,
        )

        return EquityOverviewDetailResponse(
            item=item,
            identifiers=identifiers,
            issuer_company=issuer_company,
            venue_details=venue_details,
        )
