"""Pydantic DTO models and schemas for ATLAS Cryptocurrency Markets V1 (Stage 60)."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CryptoRateKind(str, Enum):
    """Classification of crypto market price/quote observation."""

    SPOT_TRADE = "SPOT_TRADE"
    BID_ASK_QUOTE = "BID_ASK_QUOTE"
    INDICATIVE_COMPOSITE = "INDICATIVE_COMPOSITE"
    CROSSED_INVALID = "CROSSED_INVALID"
    UNKNOWN = "UNKNOWN"


class QuoteAssetType(str, Enum):
    """Classification of quote asset denomination."""

    FIAT = "fiat"
    STABLECOIN = "stablecoin"
    CRYPTO = "crypto"


class CryptoAssetItem(BaseModel):
    """Canonical digital asset representation."""

    model_config = ConfigDict(frozen=True)

    asset_entity_id: UUID
    symbol: str
    name: str
    asset_kind: str
    network_id: Optional[str] = None
    contract_address: Optional[str] = None
    token_standard: Optional[str] = None
    decimals: int = 8
    description: str = ""


class CryptoVenueItem(BaseModel):
    """Cryptocurrency exchange/trading venue metadata."""

    model_config = ConfigDict(frozen=True)

    venue_id: str
    name: str
    venue_type: str = "CENTRALIZED_EXCHANGE"
    jurisdiction: str


class CryptoQuoteView(BaseModel):
    """Typed observation of latest crypto spot price, bid/ask, spread, and volume."""

    model_config = ConfigDict(frozen=True)

    last_price: Optional[Decimal] = None
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    midpoint: Optional[Decimal] = None
    spread_absolute: Optional[Decimal] = None
    spread_bps: Optional[Decimal] = None
    rate_kind: str = "SPOT_TRADE"
    change_24h: Optional[Decimal] = None
    change_24h_percent: Optional[Decimal] = None
    volume_24h_base: Optional[Decimal] = None
    volume_24h_quote: Optional[Decimal] = None
    quote_asset_unit: str = "USD"
    data_status: str = "REALTIME"
    freshness_status: str = "FRESH"
    provider: str = "OPENBB"
    observed_at: Optional[datetime] = None
    received_at: Optional[datetime] = None


class CryptoSpotMarketDirectoryItem(BaseModel):
    """Canonical spot market item in the cryptocurrency directory."""

    model_config = ConfigDict(frozen=True)

    instrument_entity_id: UUID
    market_symbol: str
    base_asset_symbol: str
    base_asset_name: str
    quote_asset_symbol: str
    quote_asset_type: str
    venue_id: str
    venue_name: str
    venue_market_symbol: str
    market_type: str = "SPOT"
    price_precision: int = 2
    quantity_precision: int = 8
    quote: Optional[CryptoQuoteView] = None
    provider_aliases: List[str] = Field(default_factory=list)


class CryptoCoverageSummary(BaseModel):
    """Aggregate coverage metrics for configured crypto spot universe."""

    model_config = ConfigDict(frozen=True)

    total_assets: int
    total_spot_markets: int
    total_venues: int
    markets_with_quotes: int
    markets_with_bid_ask: int
    markets_with_volume: int
    markets_with_24h_change: int
    scope: str = "ATLAS_CONFIGURED_CRYPTO_SPOT"


class CryptoFilterOptionsResponse(BaseModel):
    """Distinct filter options available in current crypto catalog."""

    model_config = ConfigDict(frozen=True)

    base_assets: List[str]
    quote_assets: List[str]
    venues: List[CryptoVenueItem]
    quote_asset_types: List[str]


class CryptoSpotMarketDirectoryResponse(BaseModel):
    """Response payload for spot markets directory query."""

    model_config = ConfigDict(frozen=True)

    items: List[CryptoSpotMarketDirectoryItem]
    total_count: int
    coverage_summary: CryptoCoverageSummary
    available_filters: CryptoFilterOptionsResponse
    next_cursor: Optional[str] = None


class CryptoAssetDirectoryResponse(BaseModel):
    """Response payload for digital assets directory query."""

    model_config = ConfigDict(frozen=True)

    items: List[CryptoAssetItem]
    total_count: int
    next_cursor: Optional[str] = None


class CryptoSpotMarketOverviewDetailResponse(BaseModel):
    """Comprehensive detail response for an individual crypto spot market."""

    model_config = ConfigDict(frozen=True)

    instrument_entity_id: UUID
    market_symbol: str
    base_asset: CryptoAssetItem
    quote_asset_symbol: str
    quote_asset_type: str
    venue: CryptoVenueItem
    venue_market_symbol: str
    market_type: str = "SPOT"
    price_precision: int
    quantity_precision: int
    min_quantity: Decimal
    quote: CryptoQuoteView
    provider_aliases: List[str]
    disclaimer: str = (
        "Indicative spot market observation from identified venue. "
        "Not an order execution offer, custody service, or investment advice."
    )
