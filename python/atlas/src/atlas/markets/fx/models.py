"""Pydantic DTO models and schemas for ATLAS FX Markets V1 (Stage 59)."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FxRateKind(str, Enum):
    """Classification of exchange rate observation."""

    SPOT_BID_ASK = "SPOT_BID_ASK"
    INDICATIVE_MID = "INDICATIVE_MID"
    REFERENCE_RATE = "REFERENCE_RATE"
    LAST_TRADE = "LAST_TRADE"
    UNKNOWN = "UNKNOWN"
    CROSSED_INVALID = "CROSSED_INVALID"


class FxCalculationDirection(str, Enum):
    """Direction of currency conversion relative to canonical BASE/QUOTE pair."""

    DIRECT = "DIRECT"  # BASE -> QUOTE: amount * rate
    REVERSE = "REVERSE"  # QUOTE -> BASE: amount / rate
    SAME_CURRENCY = "SAME_CURRENCY"  # SAME: amount * 1.0


class FxConversionMode(str, Enum):
    """Mode for indicative rate selection."""

    INDICATIVE_MID = "INDICATIVE_MID"
    OBSERVED_REFERENCE = "OBSERVED_REFERENCE"
    QUOTE_SIDE_ILLUSTRATION = "QUOTE_SIDE_ILLUSTRATION"


class CurrencyItem(BaseModel):
    """Validated fiat currency reference metadata."""

    model_config = ConfigDict(frozen=True)

    code: str = Field(..., min_length=3, max_length=3)
    name: str
    symbol: str
    minor_units: int
    country_or_region: str


class FxQuoteView(BaseModel):
    """Typed observation of latest spot exchange rate, bid/ask, and spread."""

    model_config = ConfigDict(frozen=True)

    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    midpoint: Optional[Decimal] = None
    spread_absolute: Optional[Decimal] = None
    spread_bps: Optional[Decimal] = None
    spread_pips: Optional[Decimal] = None
    rate_kind: str = "SPOT_BID_ASK"
    change_24h: Optional[Decimal] = None
    change_24h_percent: Optional[Decimal] = None
    qualified_reference_close: Optional[Decimal] = None
    data_status: str = "REALTIME"
    freshness_status: str = "FRESH"
    provider: str = "OPENBB"
    observed_at: Optional[datetime] = None
    received_at: Optional[datetime] = None


class FxPairDirectoryItem(BaseModel):
    """Canonical spot currency pair item in the directory."""

    model_config = ConfigDict(frozen=True)

    instrument_entity_id: UUID
    display_pair: str
    base_currency: str
    quote_currency: str
    instrument_kind: str = "SPOT_FX"
    pip_size: Decimal = Decimal("0.0001")
    rate_precision: int = 4
    quote: Optional[FxQuoteView] = None
    provider_aliases: List[str] = Field(default_factory=list)


class FxPairCoverageSummary(BaseModel):
    """Aggregate coverage metrics for configured FX universe."""

    model_config = ConfigDict(frozen=True)

    total_pairs: int
    base_currencies_count: int
    quote_currencies_count: int
    pairs_with_quotes: int
    pairs_with_bid_ask: int
    pairs_with_spread: int
    scope: str = "ATLAS_CONFIGURED_SPOT_FX"


class FxConversionRequest(BaseModel):
    """Request payload for indicative currency conversion."""

    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(
        ...,
        gt=Decimal("0"),
        le=Decimal("1000000000000"),
        description="Finite, positive conversion amount.",
    )
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    mode: Optional[FxConversionMode] = Field(default=FxConversionMode.INDICATIVE_MID)


class FxConversionResponse(BaseModel):
    """Result of indicative currency conversion calculation."""

    model_config = ConfigDict(frozen=True)

    from_currency: str
    to_currency: str
    input_amount: Decimal
    output_amount: Decimal
    rate_used: Decimal
    rate_kind: str
    calculation_direction: str
    source_pair_entity_id: Optional[UUID] = None
    quote_side: Optional[str] = None
    source_timestamp: Optional[datetime] = None
    received_at: Optional[datetime] = None
    freshness_status: str = "FRESH"
    delay_status: str = "REALTIME"
    provider: str = "OPENBB"
    indicative: bool = True
    disclaimer: str = (
        "Indicative conversion only. Not an executable order, bank remittance quote, "
        "or settlement rate."
    )


class FxCurrenciesResponse(BaseModel):
    """Response containing supported fiat currency options."""

    model_config = ConfigDict(frozen=True)

    items: List[CurrencyItem]
    total_count: int


class FxPairDirectoryResponse(BaseModel):
    """Paginated response for the FX currency pair directory."""

    model_config = ConfigDict(frozen=True)

    items: List[FxPairDirectoryItem]
    total_count: int
    coverage: FxPairCoverageSummary
    next_cursor: Optional[str] = None
    has_more: bool = False


class FxPairOverviewDetailResponse(BaseModel):
    """Detailed inspector response for a selected currency pair."""

    model_config = ConfigDict(frozen=True)

    pair: FxPairDirectoryItem
    base_currency_info: CurrencyItem
    quote_currency_info: CurrencyItem
    orientation_explanation: str
