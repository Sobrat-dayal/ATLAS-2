"""Services for ATLAS Cryptocurrency Markets V1 (Stage 60).

Provides Decimal-safe quote evaluation, bid/ask spread calculations,
24-hour price change verification, volume metrics, and directory assembly.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from atlas.market_data.live.service import LiveQuoteService

from .config import CanonicalCryptoSpotMarketConfig
from .models import (
    CryptoAssetDirectoryResponse,
    CryptoAssetItem,
    CryptoCoverageSummary,
    CryptoQuoteView,
    CryptoRateKind,
    CryptoSpotMarketDirectoryItem,
    CryptoSpotMarketDirectoryResponse,
    CryptoSpotMarketOverviewDetailResponse,
    CryptoVenueItem,
)
from .repository import CryptoMarketRepository


class CryptoMarketReadService:
    """Service responsible for reading and validating spot crypto market observations."""

    def __init__(
        self,
        quote_service: Optional[LiveQuoteService] = None,
        freshness_query_service: Optional[Any] = None,
        ch_client_factory: Optional[Any] = None,
    ) -> None:
        self.quote_service = quote_service
        self.freshness_query_service = freshness_query_service
        self.ch_client_factory = ch_client_factory

    async def get_market_quote(self, market: CanonicalCryptoSpotMarketConfig) -> CryptoQuoteView:
        """Retrieve, validate, and compute market quote metrics for a spot market."""
        now = datetime.now(timezone.utc)

        live_quote = None
        if self.quote_service is not None:
            try:
                live_quote = await self.quote_service.get_latest_quote(market.instrument_entity_id)
            except Exception:
                live_quote = None

        last_price: Optional[Decimal] = None
        bid: Optional[Decimal] = None
        ask: Optional[Decimal] = None
        vol_base: Optional[Decimal] = market.default_volume_24h_base
        vol_quote: Optional[Decimal] = market.default_volume_24h_quote
        change_24h_pct: Optional[Decimal] = market.default_change_24h_percent
        rate_kind: CryptoRateKind = CryptoRateKind.SPOT_TRADE
        observed_at: Optional[datetime] = now
        received_at: Optional[datetime] = now

        if live_quote is not None:
            last_price = (
                Decimal(str(live_quote.last_price))
                if live_quote.last_price is not None
                else market.default_last_price
            )
            bid = (
                Decimal(str(live_quote.bid_price))
                if live_quote.bid_price is not None
                else market.default_bid
            )
            ask = (
                Decimal(str(live_quote.ask_price))
                if live_quote.ask_price is not None
                else market.default_ask
            )
            observed_at = getattr(live_quote, "observed_at", now) or now
            received_at = getattr(live_quote, "received_at", now) or now
        else:
            last_price = market.default_last_price
            bid = market.default_bid
            ask = market.default_ask

        # Spread & Midpoint validation
        midpoint: Optional[Decimal] = None
        spread_absolute: Optional[Decimal] = None
        spread_bps: Optional[Decimal] = None

        if bid is not None and ask is not None:
            if bid > ask:
                # Crossed/inconsistent market state
                rate_kind = CryptoRateKind.CROSSED_INVALID
                spread_absolute = None
                midpoint = None
                spread_bps = None
            elif bid > Decimal("0") and ask > Decimal("0"):
                rate_kind = CryptoRateKind.BID_ASK_QUOTE
                spread_absolute = ask - bid
                midpoint = (bid + ask) / Decimal("2")
                if midpoint > Decimal("0"):
                    spread_bps = (spread_absolute / midpoint) * Decimal("10000")
                    spread_bps = spread_bps.quantize(Decimal("0.01"))

        # Calculate absolute 24h change if last_price and change_pct exist
        change_24h: Optional[Decimal] = None
        if last_price is not None and change_24h_pct is not None:
            try:
                # ref = last / (1 + pct / 100) => change = last - ref
                denom = Decimal("1") + (change_24h_pct / Decimal("100"))
                if denom > Decimal("0"):
                    ref_price = last_price / denom
                    change_24h = (last_price - ref_price).quantize(
                        Decimal(f"1e-{market.price_precision}")
                    )
            except Exception:
                change_24h = None

        # Freshness evaluation
        freshness_status = "FRESH"
        data_status = "REALTIME"
        if observed_at:
            age_seconds = (now - observed_at).total_seconds()
            if age_seconds > 300:
                freshness_status = "STALE"

        return CryptoQuoteView(
            last_price=last_price,
            bid=bid,
            ask=ask,
            midpoint=midpoint,
            spread_absolute=spread_absolute,
            spread_bps=spread_bps,
            rate_kind=rate_kind.value,
            change_24h=change_24h,
            change_24h_percent=change_24h_pct,
            volume_24h_base=vol_base,
            volume_24h_quote=vol_quote,
            quote_asset_unit=market.quote_asset_symbol,
            data_status=data_status,
            freshness_status=freshness_status,
            provider=market.default_provider,
            observed_at=observed_at,
            received_at=received_at,
        )


class CryptoDirectoryService:
    """Service orchestrating crypto spot market catalog search, filtering, and detail."""

    def __init__(
        self,
        repository: CryptoMarketRepository,
        market_read_service: CryptoMarketReadService,
    ) -> None:
        self.repository = repository
        self.market_read_service = market_read_service

    async def list_spot_markets(
        self,
        query: Optional[str] = None,
        base_asset: Optional[str] = None,
        quote_asset: Optional[str] = None,
        venue: Optional[str] = None,
        quote_asset_type: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> CryptoSpotMarketDirectoryResponse:
        """List, filter, and enrich spot markets with quotes."""
        configs, total_count, next_cursor = self.repository.list_spot_markets(
            query=query,
            base_asset=base_asset,
            quote_asset=quote_asset,
            venue=venue,
            quote_asset_type=quote_asset_type,
            limit=limit,
            cursor=cursor,
        )

        items: List[CryptoSpotMarketDirectoryItem] = []
        with_quotes = 0
        with_bid_ask = 0
        with_vol = 0
        with_change = 0

        for config in configs:
            quote = await self.market_read_service.get_market_quote(config)
            if quote.last_price is not None:
                with_quotes += 1
            if quote.bid is not None and quote.ask is not None:
                with_bid_ask += 1
            if quote.volume_24h_base is not None:
                with_vol += 1
            if quote.change_24h_percent is not None:
                with_change += 1

            asset = self.repository.get_asset(config.base_asset_symbol)
            base_name = asset.name if asset else config.base_asset_symbol

            items.append(
                CryptoSpotMarketDirectoryItem(
                    instrument_entity_id=config.instrument_entity_id,
                    market_symbol=config.market_symbol,
                    base_asset_symbol=config.base_asset_symbol,
                    base_asset_name=base_name,
                    quote_asset_symbol=config.quote_asset_symbol,
                    quote_asset_type=config.quote_asset_type.value,
                    venue_id=config.venue_id,
                    venue_name=config.venue_name,
                    venue_market_symbol=config.venue_market_symbol,
                    market_type=config.market_type,
                    price_precision=config.price_precision,
                    quantity_precision=config.quantity_precision,
                    quote=quote,
                    provider_aliases=config.provider_aliases,
                )
            )

        filter_options = self.repository.get_filter_options()
        coverage = self.repository.get_coverage_summary(
            markets_with_quotes=with_quotes,
            markets_with_bid_ask=with_bid_ask,
            markets_with_volume=with_vol,
            markets_with_24h_change=with_change,
        )

        return CryptoSpotMarketDirectoryResponse(
            items=items,
            total_count=total_count,
            coverage_summary=coverage,
            available_filters=filter_options,
            next_cursor=next_cursor,
        )

    async def get_market_overview(
        self, instrument_entity_id: UUID
    ) -> Optional[CryptoSpotMarketOverviewDetailResponse]:
        """Retrieve full market overview including base asset and venue inspection data."""
        config = self.repository.get_spot_market(instrument_entity_id)
        if not config:
            return None

        quote = await self.market_read_service.get_market_quote(config)
        asset = self.repository.get_asset(config.base_asset_symbol)
        if not asset:
            asset = CryptoAssetItem(
                asset_entity_id=instrument_entity_id,
                symbol=config.base_asset_symbol,
                name=config.base_asset_symbol,
                asset_kind="coin",
            )

        venue_cfg = self.repository._venues.get(config.venue_id)
        venue_item = CryptoVenueItem(
            venue_id=config.venue_id,
            name=config.venue_name,
            venue_type=venue_cfg.venue_type if venue_cfg else "CENTRALIZED_EXCHANGE",
            jurisdiction=venue_cfg.jurisdiction if venue_cfg else "Global",
        )

        return CryptoSpotMarketOverviewDetailResponse(
            instrument_entity_id=config.instrument_entity_id,
            market_symbol=config.market_symbol,
            base_asset=asset,
            quote_asset_symbol=config.quote_asset_symbol,
            quote_asset_type=config.quote_asset_type.value,
            venue=venue_item,
            venue_market_symbol=config.venue_market_symbol,
            market_type=config.market_type,
            price_precision=config.price_precision,
            quantity_precision=config.quantity_precision,
            min_quantity=config.min_quantity,
            quote=quote,
            provider_aliases=config.provider_aliases,
        )

    def get_coverage_summary(self) -> CryptoCoverageSummary:
        """Retrieve global catalog coverage summary."""
        return self.repository.get_coverage_summary()


class CryptoAssetDirectoryService:
    """Service providing digital asset discovery and metadata lookups."""

    def __init__(self, repository: CryptoMarketRepository) -> None:
        self.repository = repository

    def list_assets(
        self,
        query: Optional[str] = None,
        asset_kind: Optional[str] = None,
        network: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> CryptoAssetDirectoryResponse:
        """List digital assets matching query criteria."""
        items, total_count, next_cursor = self.repository.list_assets(
            query=query,
            asset_kind=asset_kind,
            network=network,
            limit=limit,
            cursor=cursor,
        )
        return CryptoAssetDirectoryResponse(
            items=items,
            total_count=total_count,
            next_cursor=next_cursor,
        )

    def get_asset(self, identifier: UUID | str) -> Optional[CryptoAssetItem]:
        """Look up single digital asset."""
        return self.repository.get_asset(identifier)
