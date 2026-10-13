"""Pydantic DTOs and Enums for Home Market Summary (Stage 52)."""

from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MarketSummaryDataStatus(str, Enum):
    """Explicit per-instrument availability classification."""

    AVAILABLE = "available"
    NO_QUOTE = "no_quote"
    NOT_CONFIGURED = "not_configured"
    UNRESOLVED_INSTRUMENT = "unresolved_instrument"
    SOURCE_UNAVAILABLE = "source_unavailable"
    ERROR = "error"


class MarketSummaryChangeDirection(str, Enum):
    """Direction of instrument price movement."""

    UP = "up"
    DOWN = "down"
    FLAT = "flat"
    UNKNOWN = "unknown"


class MarketSummaryDeliveryDelay(str, Enum):
    """Data feed delivery latency categorization."""

    REALTIME = "realtime"
    DELAYED = "delayed"
    UNKNOWN = "unknown"


class HomeMarketSummaryCoverage(BaseModel):
    """Summary coverage metadata for configured instruments."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    configured_count: int = Field(
        ge=0, description="Total number of active configured instruments."
    )
    available_count: int = Field(
        ge=0, description="Number of instruments with real quote observations."
    )
    unavailable_count: int = Field(
        ge=0, description="Number of instruments without available quotes."
    )


class HomeMarketSummaryItem(BaseModel):
    """Canonical per-instrument summary DTO."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority."
    )
    display_name: str = Field(
        ..., min_length=1, max_length=256, description="Human-readable instrument title."
    )
    display_symbol: Optional[str] = Field(
        default=None, max_length=64, description="Display/ticker identification symbol."
    )
    instrument_category: str = Field(
        ...,
        description="Canonical category (market_index, etf, currency, crypto, commodity, equity).",
    )
    value_kind: str = Field(default="price", description="Denomination type (price, points, rate).")

    quote_currency: Optional[str] = Field(
        default=None,
        max_length=16,
        description="ISO currency code where applicable (e.g. USD, EUR).",
    )
    quote_unit: Optional[str] = Field(
        default=None, max_length=32, description="Display unit (e.g. pts, USD/bbl)."
    )

    # High-precision Decimal serialized as strings to prevent floating point inaccuracies
    last_price: Optional[str] = Field(
        default=None, description="Traded price from canonical quote/trade state."
    )
    bid_price: Optional[str] = Field(default=None, description="Current highest bid price.")
    ask_price: Optional[str] = Field(default=None, description="Current lowest ask price.")

    absolute_change: Optional[str] = Field(
        default=None, description="Signed price change relative to valid reference close."
    )
    percentage_change: Optional[str] = Field(
        default=None, description="Signed percentage change relative to valid reference close."
    )
    change_direction: MarketSummaryChangeDirection = Field(
        default=MarketSummaryChangeDirection.UNKNOWN,
        description="Performance direction derived from absolute change.",
    )

    source_timestamp: Optional[datetime] = Field(
        default=None, description="Observation timestamp from source feed in UTC."
    )
    received_at: Optional[datetime] = Field(
        default=None, description="Timestamp when observation entered ATLAS pipeline."
    )

    # Stage 44 freshness integration
    freshness_status: str = Field(
        default="unavailable", description="Freshness status (fresh, aging, stale, unavailable)."
    )
    delivery_delay_status: MarketSummaryDeliveryDelay = Field(
        default=MarketSummaryDeliveryDelay.UNKNOWN,
        description="Realtime vs delayed feed classification.",
    )
    delay_seconds: Optional[int] = Field(
        default=None, ge=0, description="Reported upstream feed delay duration in seconds."
    )

    # Provenance
    provider_key: Optional[str] = Field(
        default=None, description="Safe identifier of data provider."
    )
    provider_display_name: Optional[str] = Field(
        default=None, description="Human-readable data provider name."
    )

    # Reference Close Metadata
    reference_close: Optional[str] = Field(
        default=None, description="Verified completed-session reference close price."
    )
    reference_session_date: Optional[date] = Field(
        default=None, description="Date of completed reference trading session."
    )
    reference_source: Optional[str] = Field(
        default=None,
        description="Source of reference close (e.g. canonical_snapshot, clickhouse_daily).",
    )

    # Availability & error handling
    data_status: MarketSummaryDataStatus = Field(
        default=MarketSummaryDataStatus.NO_QUOTE, description="Data availability classification."
    )
    unavailable_reason: Optional[str] = Field(
        default=None, description="Safe diagnostic reason when observation is unavailable."
    )


class HomeMarketSummaryResponse(BaseModel):
    """Root presentation response for GET /api/v1/home/market-summary."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = Field(default=1, description="Presentation schema version.")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response assembly UTC timestamp.",
    )
    items: List[HomeMarketSummaryItem] = Field(
        default_factory=list,
        max_length=20,
        description="Bounded list of configured market summary observations.",
    )
    coverage: HomeMarketSummaryCoverage = Field(..., description="Coverage statistics.")
