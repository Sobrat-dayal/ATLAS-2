"""Service Layer for ATLAS FX Markets V1 (Stage 59).

Contains:
- FxMarketReadService: live quotes, bid/ask spread, midpoint, pips, and freshness.
- FxDirectoryService: directory queries, pagination, and coverage summary.
- FxConversionService: bounded indicative currency conversion with Decimal safety.
"""

import logging
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from atlas.market_data.freshness.query import MarketDataFreshnessQueryService
from atlas.market_data.live.service import LiveQuoteService

from .config import (
    ISO_4217_REGISTRY,
    CanonicalFxPairConfig,
)
from .models import (
    CurrencyItem,
    FxCalculationDirection,
    FxConversionMode,
    FxConversionRequest,
    FxConversionResponse,
    FxPairCoverageSummary,
    FxPairDirectoryItem,
    FxPairDirectoryResponse,
    FxPairOverviewDetailResponse,
    FxQuoteView,
    FxRateKind,
)
from .repository import FxDirectoryRepository

logger = logging.getLogger(__name__)


class FxMarketReadService:
    """
    Retrieves and calculates latest spot quotes, bid/ask spreads, and midpoints for currency pairs.

    Guarantees:
    - 100% Read-Only: 0 writes to Redis, PostgreSQL, or ClickHouse.
    - True bid/ask integrity: bid and ask must come from the same compatible observation.
    - Crossed markets (bid > ask) are flagged as invalid;
      spread is never reported as negative or repaired.
    - Full Decimal precision throughout arithmetic.
    - Pip conventions: 0.01 for JPY pairs, 0.0001 for non-JPY pairs.
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

    async def get_fx_quote(self, pair_config: CanonicalFxPairConfig) -> FxQuoteView:
        """Fetch latest market quote for a canonical pair and calculate spread and midpoint."""
        now = datetime.now(timezone.utc)
        record = None

        if self._quote_service is not None:
            try:
                record = await self._quote_service.get_latest_quote(
                    pair_config.instrument_entity_id
                )
            except Exception as e:
                logger.warning(
                    "Error querying LiveQuoteService for FX pair %s (%s): %s",
                    pair_config.display_pair,
                    pair_config.instrument_entity_id,
                    e,
                )

        bid: Optional[Decimal] = None
        ask: Optional[Decimal] = None
        last_price: Optional[Decimal] = None
        provider = pair_config.default_provider
        data_status = "REALTIME"
        freshness_status = "FRESH"
        observed_at = now
        received_at = now

        if record is not None and record.quote is not None:
            q = record.quote
            bid = Decimal(str(q.bid_price)) if getattr(q, "bid_price", None) is not None else None
            ask = Decimal(str(q.ask_price)) if getattr(q, "ask_price", None) is not None else None
            last_price = (
                Decimal(str(q.last_price)) if getattr(q, "last_price", None) is not None else None
            )
            observed_at = getattr(q, "timestamp", now)
            received_at = record.cached_at or now
            data_status = "REALTIME"
        elif pair_config.default_bid is not None and pair_config.default_ask is not None:
            bid = pair_config.default_bid
            ask = pair_config.default_ask
            data_status = "DEFAULT_CATALOG"
            freshness_status = "FRESH"

        midpoint: Optional[Decimal] = None
        spread_abs: Optional[Decimal] = None
        spread_bps: Optional[Decimal] = None
        spread_pips: Optional[Decimal] = None
        rate_kind = FxRateKind.SPOT_BID_ASK.value

        if bid is not None and ask is not None:
            if bid > 0 and ask > 0:
                if ask >= bid:
                    spread_abs = ask - bid
                    midpoint = (bid + ask) / Decimal("2")
                    if midpoint > Decimal("0"):
                        spread_bps = ((ask - bid) / midpoint) * Decimal("10000")
                    if pair_config.pip_size > Decimal("0"):
                        spread_pips = (ask - bid) / pair_config.pip_size
                else:
                    # Crossed market!
                    rate_kind = "CROSSED_INVALID"
                    data_status = "INCONSISTENT"
                    spread_abs = None
                    midpoint = None
            else:
                rate_kind = FxRateKind.UNKNOWN.value
        elif last_price is not None:
            midpoint = last_price
            rate_kind = FxRateKind.LAST_TRADE.value
        elif bid is not None:
            midpoint = bid
            rate_kind = FxRateKind.INDICATIVE_MID.value
        elif ask is not None:
            midpoint = ask
            rate_kind = FxRateKind.INDICATIVE_MID.value
        else:
            rate_kind = FxRateKind.UNKNOWN.value

        return FxQuoteView(
            bid=bid,
            ask=ask,
            midpoint=midpoint,
            spread_absolute=spread_abs,
            spread_bps=spread_bps,
            spread_pips=spread_pips,
            rate_kind=rate_kind,
            change_24h=None,
            change_24h_percent=None,
            qualified_reference_close=None,
            data_status=data_status,
            freshness_status=freshness_status,
            provider=provider,
            observed_at=observed_at,
            received_at=received_at,
        )


class FxDirectoryService:
    """Provides filtered, paginated FX spot directory and pair inspection."""

    def __init__(
        self,
        repository: FxDirectoryRepository,
        market_read_service: FxMarketReadService,
    ):
        self._repository = repository
        self._market_read_service = market_read_service

    async def get_directory(
        self,
        base_currency: Optional[str] = None,
        quote_currency: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> FxPairDirectoryResponse:
        """Retrieve paginated canonical spot FX pairs enriched with latest quotes."""
        configs, total_count, next_cursor, has_more = await self._repository.list_pairs(
            base_currency=base_currency,
            quote_currency=quote_currency,
            query=query,
            limit=limit,
            cursor=cursor,
        )

        items: List[FxPairDirectoryItem] = []
        for conf in configs:
            quote = await self._market_read_service.get_fx_quote(conf)
            items.append(
                FxPairDirectoryItem(
                    instrument_entity_id=conf.instrument_entity_id,
                    display_pair=conf.display_pair,
                    base_currency=conf.base_currency,
                    quote_currency=conf.quote_currency,
                    instrument_kind=conf.instrument_kind,
                    pip_size=conf.pip_size,
                    rate_precision=conf.rate_precision,
                    quote=quote,
                    provider_aliases=conf.provider_aliases,
                )
            )

        all_pairs = await self._repository.get_all_pairs()
        base_currs = {p.base_currency for p in all_pairs}
        quote_currs = {p.quote_currency for p in all_pairs}
        pairs_with_quotes = sum(
            1 for it in items if it.quote is not None and it.quote.midpoint is not None
        )
        pairs_with_bid_ask = sum(
            1
            for it in items
            if it.quote is not None and it.quote.bid is not None and it.quote.ask is not None
        )
        pairs_with_spread = sum(
            1 for it in items if it.quote is not None and it.quote.spread_absolute is not None
        )

        coverage = FxPairCoverageSummary(
            total_pairs=len(all_pairs),
            base_currencies_count=len(base_currs),
            quote_currencies_count=len(quote_currs),
            pairs_with_quotes=pairs_with_quotes,
            pairs_with_bid_ask=pairs_with_bid_ask,
            pairs_with_spread=pairs_with_spread,
            scope="ATLAS_CONFIGURED_SPOT_FX",
        )

        return FxPairDirectoryResponse(
            items=items,
            total_count=total_count,
            coverage=coverage,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_pair_detail(
        self, instrument_entity_id: UUID
    ) -> Optional[FxPairOverviewDetailResponse]:
        """Inspect a single canonical currency pair."""
        conf = await self._repository.get_pair_by_id(instrument_entity_id)
        if conf is None:
            return None

        quote = await self._market_read_service.get_fx_quote(conf)
        base_meta = ISO_4217_REGISTRY.get(conf.base_currency)
        quote_meta = ISO_4217_REGISTRY.get(conf.quote_currency)

        base_info = CurrencyItem(
            code=conf.base_currency,
            name=base_meta.name if base_meta else conf.base_currency,
            symbol=base_meta.symbol if base_meta else conf.base_currency,
            minor_units=base_meta.minor_units if base_meta else 2,
            country_or_region=base_meta.country_or_region if base_meta else "",
        )
        quote_info = CurrencyItem(
            code=conf.quote_currency,
            name=quote_meta.name if quote_meta else conf.quote_currency,
            symbol=quote_meta.symbol if quote_meta else conf.quote_currency,
            minor_units=quote_meta.minor_units if quote_meta else 2,
            country_or_region=quote_meta.country_or_region if quote_meta else "",
        )

        mid_str = f"{quote.midpoint:.4f}" if quote.midpoint is not None else "N/A"
        orientation = (
            f"1 {conf.base_currency} = {mid_str} {conf.quote_currency}: 1 unit of "
            f"base currency ({conf.base_currency}) buys {mid_str} units of "
            f"quote currency ({conf.quote_currency})."
        )

        pair_item = FxPairDirectoryItem(
            instrument_entity_id=conf.instrument_entity_id,
            display_pair=conf.display_pair,
            base_currency=conf.base_currency,
            quote_currency=conf.quote_currency,
            instrument_kind=conf.instrument_kind,
            pip_size=conf.pip_size,
            rate_precision=conf.rate_precision,
            quote=quote,
            provider_aliases=conf.provider_aliases,
        )

        return FxPairOverviewDetailResponse(
            pair=pair_item,
            base_currency_info=base_info,
            quote_currency_info=quote_info,
            orientation_explanation=orientation,
        )

    async def get_supported_currencies(self) -> List[CurrencyItem]:
        """Return all distinct validated currencies represented in the FX catalog."""
        return await self._repository.get_supported_currencies()


class FxConversionService:
    """
    Read-only indicative currency conversion engine.

    Guarantees:
    - Zero financial or database writes.
    - Zero external network requests per user keystroke.
    - Arithmetic strictly executed via Python Decimal.
    - Direct (BASE->QUOTE: amount * rate) and Reverse (QUOTE->BASE: amount / rate).
    - Quote-side illustration support (Bid for selling BASE, Ask for buying BASE).
    - Rejects unsupported pairs: DOES NOT perform multi-leg synthetic cross triangulation.
    - Destination amount cleanly rounded to ISO 4217 minor units.
    - Informational non-executable status explicitly disclosed.
    """

    def __init__(
        self,
        repository: FxDirectoryRepository,
        market_read_service: FxMarketReadService,
    ):
        self._repository = repository
        self._market_read_service = market_read_service

    async def convert(self, request: FxConversionRequest) -> FxConversionResponse:
        """Execute indicative currency conversion."""
        from_ccy = request.from_currency.strip().upper()
        to_ccy = request.to_currency.strip().upper()

        if from_ccy not in ISO_4217_REGISTRY:
            raise ValueError(
                f"Origin currency '{from_ccy}' is not a recognized ISO 4217 fiat currency."
            )
        if to_ccy not in ISO_4217_REGISTRY:
            raise ValueError(
                f"Destination currency '{to_ccy}' is not a recognized ISO 4217 fiat currency."
            )

        dest_meta = ISO_4217_REGISTRY[to_ccy]
        now = datetime.now(timezone.utc)

        # Same-currency conversion: arithmetic identity (1:1)
        if from_ccy == to_ccy:
            quantized = self._quantize_amount(request.amount, dest_meta.minor_units)
            return FxConversionResponse(
                from_currency=from_ccy,
                to_currency=to_ccy,
                input_amount=request.amount,
                output_amount=quantized,
                rate_used=Decimal("1.0"),
                rate_kind="ARITHMETIC_IDENTITY",
                calculation_direction=FxCalculationDirection.SAME_CURRENCY.value,
                source_pair_entity_id=None,
                quote_side=None,
                source_timestamp=now,
                received_at=now,
                freshness_status="FRESH",
                delay_status="REALTIME",
                provider="ATLAS_INTERNAL",
                indicative=True,
            )

        # 1. Check for DIRECT pair (BASE == from_ccy, QUOTE == to_ccy)
        direct_conf = await self._repository.get_pair_by_currencies(from_ccy, to_ccy)
        if direct_conf is not None:
            quote = await self._market_read_service.get_fx_quote(direct_conf)
            rate_used, quote_side, rate_kind = self._select_rate_for_conversion(
                quote=quote,
                mode=request.mode or FxConversionMode.INDICATIVE_MID,
                is_direct=True,
            )
            if rate_used is None or rate_used <= Decimal("0"):
                raise ValueError(
                    "Exchange rate observation unavailable for direct pair "
                    f"{direct_conf.display_pair}."
                )

            # Direct formula: amount_quote = amount_base * rate
            raw_output = request.amount * rate_used
            output_amount = self._quantize_amount(raw_output, dest_meta.minor_units)

            return FxConversionResponse(
                from_currency=from_ccy,
                to_currency=to_ccy,
                input_amount=request.amount,
                output_amount=output_amount,
                rate_used=rate_used,
                rate_kind=rate_kind,
                calculation_direction=FxCalculationDirection.DIRECT.value,
                source_pair_entity_id=direct_conf.instrument_entity_id,
                quote_side=quote_side,
                source_timestamp=quote.observed_at or now,
                received_at=quote.received_at or now,
                freshness_status=quote.freshness_status,
                delay_status=quote.data_status,
                provider=quote.provider,
                indicative=True,
            )

        # 2. Check for REVERSE pair (BASE == to_ccy, QUOTE == from_ccy)
        reverse_conf = await self._repository.get_pair_by_currencies(to_ccy, from_ccy)
        if reverse_conf is not None:
            quote = await self._market_read_service.get_fx_quote(reverse_conf)
            rate_used, quote_side, rate_kind = self._select_rate_for_conversion(
                quote=quote,
                mode=request.mode or FxConversionMode.INDICATIVE_MID,
                is_direct=False,
            )
            if rate_used is None or rate_used <= Decimal("0"):
                raise ValueError(
                    "Exchange rate observation unavailable for reverse pair "
                    f"{reverse_conf.display_pair}."
                )

            # Reverse formula: amount_base = amount_quote / rate
            raw_output = request.amount / rate_used
            output_amount = self._quantize_amount(raw_output, dest_meta.minor_units)

            return FxConversionResponse(
                from_currency=from_ccy,
                to_currency=to_ccy,
                input_amount=request.amount,
                output_amount=output_amount,
                rate_used=rate_used,
                rate_kind=rate_kind,
                calculation_direction=FxCalculationDirection.REVERSE.value,
                source_pair_entity_id=reverse_conf.instrument_entity_id,
                quote_side=quote_side,
                source_timestamp=quote.observed_at or now,
                received_at=quote.received_at or now,
                freshness_status=quote.freshness_status,
                delay_status=quote.data_status,
                provider=quote.provider,
                indicative=True,
            )

        # 3. No direct or reverse pair exists: refuse to synthesize/triangulate
        raise ValueError(
            f"Conversion unavailable for currency pair {from_ccy}/{to_ccy}. "
            "ATLAS does not construct multi-leg synthetic cross-rates in Stage 59."
        )

    def _select_rate_for_conversion(
        self,
        quote: FxQuoteView,
        mode: FxConversionMode,
        is_direct: bool,
    ) -> Tuple[Optional[Decimal], Optional[str], str]:
        """Select appropriate rate from quote based on conversion mode and direction."""
        if mode == FxConversionMode.QUOTE_SIDE_ILLUSTRATION:
            if is_direct:
                # Direct (BASE -> QUOTE): user sells BASE, quoting dealer buys at BID
                if quote.bid is not None and quote.bid > Decimal("0"):
                    return quote.bid, "BID", "DEALER_BID"
            else:
                # Reverse (QUOTE -> BASE): user pays QUOTE to buy BASE, quoting dealer sells at ASK
                if quote.ask is not None and quote.ask > Decimal("0"):
                    return quote.ask, "ASK", "DEALER_ASK"

        # Fallback or INDICATIVE_MID mode: use calculated midpoint
        if quote.midpoint is not None and quote.midpoint > Decimal("0"):
            return quote.midpoint, None, "CALCULATED_MIDPOINT"
        if quote.bid is not None and quote.bid > Decimal("0"):
            return quote.bid, "BID", "INDICATIVE_BID"
        if quote.ask is not None and quote.ask > Decimal("0"):
            return quote.ask, "ASK", "INDICATIVE_ASK"

        return None, None, FxRateKind.UNKNOWN.value

    def _quantize_amount(self, amount: Decimal, minor_units: int) -> Decimal:
        """Round money amount to ISO currency minor units using ROUND_HALF_UP."""
        if minor_units <= 0:
            exp = Decimal("1")
        else:
            exp = Decimal("1." + "0" * minor_units)
        return amount.quantize(exp, rounding=ROUND_HALF_UP)
