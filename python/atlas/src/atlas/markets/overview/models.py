"""Pydantic DTOs and Enums for Markets Overview V1 (Stage 56)."""

from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Reuse established enums from Stage 52 to maintain 100% semantic consistency
from atlas.home.market_summary.models import (
    MarketSummaryChangeDirection,
    MarketSummaryDataStatus,
    MarketSummaryDeliveryDelay,
)


class MarketGroupSummary(BaseModel):
    """Presentation summary for a supported market asset group."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(
        ...,
        description="Stable group identifier (e.g. all, benchmarks, equities, etc.).",
    )
    label: str = Field(..., description="Human-readable group label.")
    count: int = Field(ge=0, description="Number of configured instruments in this group.")


class MarketsOverviewCoverage(BaseModel):
    """Aggregate coverage metrics for the Markets Overview response."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    configured_count: int = Field(
        ge=0, description="Total number of active configured instruments in the catalog."
    )
    returned_count: int = Field(
        ge=0, description="Number of instruments returned in the current response page."
    )
    available_count: int = Field(
        ge=0, description="Number of instruments with real quote observations."
    )
    unavailable_count: int = Field(
        ge=0, description="Number of instruments without available quotes."
    )


class MarketsOverviewItem(BaseModel):
    """Canonical per-instrument overview observation DTO."""

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
        description=(
            "Canonical category (market_index, equity, etf, "
            "currency, crypto_asset, commodity, bond)."
        ),
    )
    market_group: str = Field(
        ...,
        description=(
            "Presentation group (benchmarks, equities, etfs, "
            "fx, crypto, commodities, bonds)."
        ),
    )
    venue: Optional[str] = Field(
        default=None, max_length=64, description="Exchange or trading venue."
    )
    value_kind: str = Field(
        default="price", description="Denomination type (price, points, rate, yield)."
    )

    quote_currency: Optional[str] = Field(
        default=None,
        max_length=16,
        description="ISO currency code where applicable (e.g. USD, EUR, JPY).",
    )
    quote_unit: Optional[str] = Field(
        default=None, max_length=32, description="Display unit (e.g. pts, USD/bbl, % yield)."
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
        description="Source of reference close (e.g. feed_snapshot_prior_close, clickhouse_daily).",
    )

    # Availability & error handling
    data_status: MarketSummaryDataStatus = Field(
        default=MarketSummaryDataStatus.NO_QUOTE, description="Data availability classification."
    )
    unavailable_reason: Optional[str] = Field(
        default=None, description="Safe diagnostic reason when observation is unavailable."
    )

    featured: bool = Field(
        default=False,
        description="Whether instrument is featured prominently above overview table.",
    )
    display_order: int = Field(ge=0, description="Configured sorting rank.")


class MarketsOverviewResponse(BaseModel):
    """Root presentation response for GET /api/v1/markets/overview."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: int = Field(default=1, description="Presentation schema version.")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response assembly UTC timestamp.",
    )
    scope: str = Field(
        default="configured_overview_universe",
        description="Authoritative scope identifying that response covers configured catalog.",
    )
    groups: List[MarketGroupSummary] = Field(
        default_factory=list, description="Available market groups with counts."
    )
    items: List[MarketsOverviewItem] = Field(
        default_factory=list,
        max_length=100,
        description="Paginated list of configured market instruments.",
    )
    featured_items: List[MarketsOverviewItem] = Field(
        default_factory=list,
        max_length=10,
        description="Featured benchmark and market instruments for prominent display.",
    )
    coverage: MarketsOverviewCoverage = Field(..., description="Coverage statistics.")
    next_cursor: Optional[str] = Field(
        default=None, description="Cursor for the next page of results."
    )
    has_more: bool = Field(
        default=False, description="True if additional configured instruments remain."
    )
