"""FundDirectoryService and FundMarketReadService for ATLAS ETFs & Funds Markets V1 (Stage 58)."""

import logging
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

from .config import CanonicalFundConfig
from .models import (
    FundAUMView,
    FundCoverageSummary,
    FundDirectoryFilters,
    FundDirectoryItem,
    FundDirectoryResponse,
    FundFeeView,
    FundFilterOptionsResponse,
    FundIdentifierItem,
    FundMarketQuoteView,
    FundNAVView,
    FundOverviewDetailResponse,
    FundRelationshipsView,
)
from .repository import FundDirectoryRepository

logger = logging.getLogger(__name__)


class FundMarketReadService:
    """
    Retrieves and calculates latest financial market quotes and Net Asset Value (NAV)
    for ETFs, mutual funds, and closed-end funds.

    Guarantees:
    - 100% Read-Only:
        * 0 Redis writes
        * 0 ClickHouse writes
        * 0 External provider HTTP/stream calls on read
    - Strict financial-data integrity:
        * Market price and NAV are NEVER conflated.
        * Mutual funds without exchange listings report no fake quotes.
        * Full Decimal precision preserved without floating-point math loss.
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

    async def enrich_fund_items(
        self, configs: List[CanonicalFundConfig]
    ) -> List[FundDirectoryItem]:
        """
        Batches latest quote lookups for exchange-listed funds, and constructs
        independent NAV, fee, and AUM views for all funds.
        """
        if not configs:
            return []

        now = datetime.now(timezone.utc)

        # 1. Filter out only exchange-listed funds for live quote queries
        listed_configs = [c for c in configs if c.is_exchange_traded]
        listed_ids: List[UUID] = [c.instrument_entity_id for c in listed_configs]

        quote_records_map: Dict[UUID, Optional[QuoteCacheRecord]] = {}
        if self._quote_service is not None and listed_ids:
            try:
                records = await self._quote_service.get_latest_quotes(listed_ids)
                for q_id, rec in zip(listed_ids, records):
                    quote_records_map[q_id] = rec
            except Exception as e:
                logger.error("Failed to query latest quotes from LiveQuoteService for funds: %s", e)
                for q_id in listed_ids:
                    quote_records_map[q_id] = None
        else:
            for q_id in listed_ids:
                quote_records_map[q_id] = None

        # 2. Assemble presentation items
        items: List[FundDirectoryItem] = []
        for cfg in configs:
            # -----------------------------------------------------------------
            # A. Market Price Handling (Only for exchange-traded funds)
            # -----------------------------------------------------------------
            market_quote_view: Optional[FundMarketQuoteView] = None

            if not cfg.is_exchange_traded:
                # Traditional unlisted mutual fund: exchange quote is NOT APPLICABLE
                market_quote_view = FundMarketQuoteView(
                    data_status=MarketSummaryDataStatus.NOT_CONFIGURED,
                    freshness_status="not_applicable",
                    delivery_delay_status=MarketSummaryDeliveryDelay.UNKNOWN,
                    change_direction=MarketSummaryChangeDirection.UNKNOWN,
                    unavailable_reason=(
                        "Fund is not exchange-traded (priced via official NAV only)."
                    ),
                )
            else:
                rec = quote_records_map.get(cfg.instrument_entity_id)
                if rec is None:
                    # Listed fund with no current quote in Redis
                    market_quote_view = FundMarketQuoteView(
                        data_status=MarketSummaryDataStatus.NO_QUOTE,
                        freshness_status="unavailable",
                        delivery_delay_status=MarketSummaryDeliveryDelay.UNKNOWN,
                        change_direction=MarketSummaryChangeDirection.UNKNOWN,
                        unavailable_reason="No live quote observation stored in ATLAS state store.",
                    )
                else:
                    quote = rec.quote
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

                    # Reference Close & Change calculations
                    ref_close_dec = None
                    ref_source = "unavailable"
                    if last_price_dec is not None:
                        (
                            ref_close_dec,
                            _ref_date,
                            ref_source,
                        ) = await self._reference_resolver.resolve_reference_close(
                            instrument_id=cfg.instrument_entity_id,
                        )

                    abs_change, pct_change, change_direction = calculate_market_changes(
                        last_price=last_price_dec,
                        reference_close=ref_close_dec,
                    )

                    # Freshness Evaluation (Stage 44 reuse)
                    freshness_str = "stale"
                    delay_status = MarketSummaryDeliveryDelay.UNKNOWN
                    if self._freshness_query_service is not None:
                        try:
                            key = QuoteSubscriptionKey(
                                instrument_entity_id=cfg.instrument_entity_id,
                                source_provider=cfg.provider_hint or "openbb",
                            )
                            state: Optional[
                                MarketDataFreshnessState
                            ] = await self._freshness_query_service.get_freshness_state(key)
                            if state is not None:
                                freshness_str = state.status.value.lower()
                                if state.is_delayed:
                                    delay_status = MarketSummaryDeliveryDelay.DELAYED
                                else:
                                    delay_status = MarketSummaryDeliveryDelay.REALTIME
                        except Exception as e:
                            logger.debug(
                                "Freshness evaluation error for fund %s: %s",
                                cfg.display_symbol,
                                e,
                            )
                    else:
                        age_sec = (now - rec.source_timestamp).total_seconds()
                        if age_sec < 60:
                            freshness_str = MarketDataFreshnessStatus.FRESH.value.lower()
                            delay_status = MarketSummaryDeliveryDelay.REALTIME
                        elif age_sec < 900:
                            freshness_str = MarketDataFreshnessStatus.ACCEPTABLE.value.lower()
                            delay_status = MarketSummaryDeliveryDelay.REALTIME
                        else:
                            freshness_str = MarketDataFreshnessStatus.STALE.value.lower()

                    provider_disp = KNOWN_PROVIDER_NAMES.get(
                        cfg.provider_hint or "openbb", (cfg.provider_hint or "OpenBB").upper()
                    )

                    market_quote_view = FundMarketQuoteView(
                        last_price=str(last_price_dec) if last_price_dec is not None else None,
                        bid_price=str(bid_price_dec) if bid_price_dec is not None else None,
                        ask_price=str(ask_price_dec) if ask_price_dec is not None else None,
                        reference_close=str(ref_close_dec) if ref_close_dec is not None else None,
                        reference_source=ref_source,
                        absolute_change=(str(abs_change) if abs_change is not None else None),
                        percentage_change=(str(pct_change) if pct_change is not None else None),
                        change_direction=change_direction,
                        source_timestamp=rec.source_timestamp,
                        received_at=rec.received_at,
                        freshness_status=freshness_str,
                        delivery_delay_status=delay_status,
                        provider_key=cfg.provider_hint or "openbb",
                        provider_display_name=provider_disp,
                        data_status=MarketSummaryDataStatus.AVAILABLE,
                    )

            # -----------------------------------------------------------------
            # B. Net Asset Value (NAV) Handling
            # -----------------------------------------------------------------
            nav_view: Optional[FundNAVView] = None
            if cfg.initial_nav is not None:
                nav_view = FundNAVView(
                    nav_per_unit=f"{cfg.initial_nav:.4f}",
                    nav_currency=cfg.nav_currency or cfg.share_class_currency,
                    valuation_date=cfg.nav_valuation_date,
                    published_at=cfg.nav_published_at,
                    valuation_method=cfg.nav_valuation_method or "OFFICIAL_CLOSE_NAV",
                    provider_key=cfg.provider_hint or "openbb",
                    provenance="authoritative_fund_catalog",
                    is_available=True,
                )
            else:
                nav_view = FundNAVView(is_available=False)

            # -----------------------------------------------------------------
            # C. Fees & Expense Ratios
            # -----------------------------------------------------------------
            fee_view = FundFeeView(
                net_expense_ratio=(
                    f"{cfg.net_expense_ratio * 100:.3f}%"
                    if cfg.net_expense_ratio is not None
                    else None
                ),
                gross_expense_ratio=(
                    f"{cfg.gross_expense_ratio * 100:.3f}%"
                    if cfg.gross_expense_ratio is not None
                    else None
                ),
                fee_metric_type=cfg.fee_metric_type,
                fee_effective_date=cfg.fee_effective_date,
                is_available=cfg.net_expense_ratio is not None,
            )

            # -----------------------------------------------------------------
            # D. Assets Under Management (AUM)
            # -----------------------------------------------------------------
            aum_view = FundAUMView(
                total_aum=f"{cfg.total_aum:.2f}" if cfg.total_aum is not None else None,
                aum_currency=cfg.aum_currency,
                aum_as_of_date=cfg.aum_as_of_date,
                aum_scope=cfg.aum_scope,
                is_available=cfg.total_aum is not None,
            )

            # -----------------------------------------------------------------
            # E. Build Unified Directory Item
            # -----------------------------------------------------------------
            items.append(
                FundDirectoryItem(
                    instrument_entity_id=cfg.instrument_entity_id,
                    fund_name=cfg.fund_name,
                    display_symbol=cfg.display_symbol,
                    fund_type=cfg.fund_type,
                    is_exchange_traded=cfg.is_exchange_traded,
                    exchange_mic=cfg.exchange_mic,
                    exchange_display_name=cfg.exchange_display_name,
                    listing_market_country=cfg.listing_market_country,
                    trading_currency=cfg.trading_currency,
                    listing_status=cfg.listing_status,
                    domicile=cfg.domicile,
                    investment_category=cfg.investment_category,
                    distribution_policy=cfg.distribution_policy,
                    base_currency=cfg.base_currency,
                    share_class_currency=cfg.share_class_currency,
                    manager_name=cfg.manager_name,
                    sponsor_name=cfg.sponsor_name,
                    benchmark_name=cfg.benchmark_name,
                    market_quote=market_quote_view,
                    official_nav=nav_view,
                    fees=fee_view,
                    aum=aum_view,
                )
            )

        return items


class FundDirectoryService:
    """
    Coordinator service providing unified read operations for the ATLAS Funds workspace.
    Fulfills Stage 58 Sections 127-131.
    """

    def __init__(
        self,
        repository: FundDirectoryRepository,
        market_read_service: FundMarketReadService,
    ):
        self._repository = repository
        self._market_read_service = market_read_service

    async def get_fund_directory(
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
    ) -> FundDirectoryResponse:
        """
        Returns filtered, paginated Fund Directory items enriched with market quotes and NAV.
        """
        all_funds = await self._repository.get_all_canonical_funds()
        (
            paged_configs,
            next_cursor,
            has_more,
            total_matched,
        ) = await self._repository.get_filtered_funds(
            fund_type=fund_type,
            market_country=market_country,
            exchange=exchange,
            domicile=domicile,
            fund_category=fund_category,
            share_class_currency=share_class_currency,
            query=query,
            limit=limit,
            cursor=cursor,
        )

        items = await self._market_read_service.enrich_fund_items(paged_configs)
        available_filters = await self._repository.get_filter_options()

        # Compute accurate, scoped coverage metrics
        etf_count = sum(1 for f in all_funds if f.fund_type == "ETF")
        mf_count = sum(1 for f in all_funds if f.fund_type == "OPEN_END_MUTUAL_FUND")
        cef_count = sum(1 for f in all_funds if f.fund_type == "CLOSED_END_FUND")
        listed_count = sum(1 for f in all_funds if f.is_exchange_traded)

        avail_quotes = sum(
            1
            for it in items
            if it.market_quote and it.market_quote.data_status == MarketSummaryDataStatus.AVAILABLE
        )
        unavail_quotes = sum(
            1
            for it in items
            if it.is_exchange_traded
            and (
                not it.market_quote
                or it.market_quote.data_status != MarketSummaryDataStatus.AVAILABLE
            )
        )
        avail_navs = sum(1 for it in items if it.official_nav and it.official_nav.is_available)
        unavail_navs = sum(
            1 for it in items if not it.official_nav or not it.official_nav.is_available
        )

        coverage = FundCoverageSummary(
            configured_funds_count=len(all_funds),
            etf_count=etf_count,
            mutual_fund_count=mf_count,
            closed_end_fund_count=cef_count,
            exchange_listed_count=listed_count,
            returned_count=len(items),
            available_quotes_count=avail_quotes,
            available_navs_count=avail_navs,
            unavailable_quotes_count=unavail_quotes,
            unavailable_navs_count=unavail_navs,
        )

        applied_filters = FundDirectoryFilters(
            fund_type=fund_type,
            market_country=market_country,
            exchange=exchange,
            domicile=domicile,
            fund_category=fund_category,
            share_class_currency=share_class_currency,
            query=query,
        )

        return FundDirectoryResponse(
            items=items,
            filters=applied_filters,
            coverage=coverage,
            available_filters=available_filters,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_fund_filter_options(self) -> FundFilterOptionsResponse:
        """Returns distinct filter options available across configured funds."""
        return await self._repository.get_filter_options()

    async def get_fund_detail(
        self, instrument_entity_id: UUID
    ) -> Optional[FundOverviewDetailResponse]:
        """
        Returns full detailed inspector overview for a single canonical fund.
        """
        cfg = await self._repository.get_fund_by_id(instrument_entity_id)
        if cfg is None:
            return None

        enriched_items = await self._market_read_service.enrich_fund_items([cfg])
        if not enriched_items:
            return None
        item = enriched_items[0]

        # Identifiers
        identifiers: List[FundIdentifierItem] = [
            FundIdentifierItem(
                scheme="ATLAS_UUID",
                value=str(cfg.instrument_entity_id),
                is_primary=True,
            ),
            FundIdentifierItem(scheme="TICKER", value=cfg.display_symbol, is_primary=False),
        ]
        if cfg.isin:
            identifiers.append(FundIdentifierItem(scheme="ISIN", value=cfg.isin, is_primary=False))
        if cfg.figi:
            identifiers.append(FundIdentifierItem(scheme="FIGI", value=cfg.figi, is_primary=False))

        # Relationships
        relationships = FundRelationshipsView(
            manager_company_id=cfg.manager_entity_id,
            manager_name=cfg.manager_name,
            sponsor_name=cfg.sponsor_name,
            benchmark_entity_id=cfg.benchmark_entity_id,
            benchmark_name=cfg.benchmark_name,
        )

        coverage_limitations: List[str] = []
        if not cfg.is_exchange_traded:
            coverage_limitations.append(
                "This investment vehicle is an open-end mutual fund and is not exchange-traded. "
                "Intraday exchange quotes are not applicable; valuations occur via official daily "
                "NAV."
            )
        if item.official_nav and not item.official_nav.is_available:
            coverage_limitations.append(
                "Official Net Asset Value (NAV) has not yet been reported for this valuation cycle."
            )
        if item.fees and not item.fees.is_available:
            coverage_limitations.append(
                "Expense ratio and management fee data are currently unverified."
            )

        return FundOverviewDetailResponse(
            item=item,
            fund_objective=cfg.fund_objective,
            inception_date=cfg.inception_date,
            identifiers=identifiers,
            relationships=relationships,
            coverage_limitations=coverage_limitations,
        )
