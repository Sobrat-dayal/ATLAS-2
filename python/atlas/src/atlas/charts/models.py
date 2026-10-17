"""Pydantic DTO models for ATLAS Charts V1 (Stage 66).

Defines strongly-typed request and response structures with Decimal precision
for OHLCV bar representation, coverage auditing, pagination, and instrument metadata.
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChartBarDTO(BaseModel):
    """Canonical historical OHLCV observation bar."""

    model_config = ConfigDict(frozen=True)

    timestamp: str = Field(
        ...,
        description="ISO 8601 UTC timestamp of the bar period start.",
    )
    time_unix: int = Field(
        ...,
        description="Unix timestamp in seconds representing the bar start.",
    )
    open: Decimal = Field(
        ...,
        description="Opening price for the bar interval.",
    )
    high: Decimal = Field(
        ...,
        description="Highest price observed in the bar interval.",
    )
    low: Decimal = Field(
        ...,
        description="Lowest price observed in the bar interval.",
    )
    close: Decimal = Field(
        ...,
        description="Closing price for the bar interval.",
    )
    volume: Optional[Decimal] = Field(
        default=None,
        description="Traded volume. None for non-volume feeds (e.g. OTC FX). Never 0 for missing.",
    )
    is_final: bool = Field(
        default=True,
        description="Guarantees interval is closed and will not change retrospectively.",
    )


class ChartInstrumentMetadata(BaseModel):
    """Metadata describing a canonical chartable financial instrument."""

    model_config = ConfigDict(frozen=True)

    entity_id: UUID = Field(
        ...,
        description="Authoritative canonical instrument UUID.",
    )
    display_name: str = Field(
        ...,
        description="Full human-readable instrument or company name.",
    )
    display_symbol: str = Field(
        ...,
        description="Authoritative ticker or market symbol.",
    )
    asset_class: str = Field(
        ...,
        description="Financial asset class: equities, etfs, fx, crypto, bonds, futures.",
    )
    market_or_venue: str = Field(
        ...,
        description="Primary exchange, trading venue, or market structure.",
    )
    price_currency: str = Field(
        ...,
        description="Currency code of the quotation (e.g. USD, EUR, JPY, USDT).",
    )
    quotation_unit: str = Field(
        ...,
        description="Quotation convention (e.g. USD/share, % of par, USD/barrel).",
    )
    supported_intervals: List[str] = Field(
        default=["1d"],
        description="List of supported bar intervals (baseline is ['1d'] for Stage 66).",
    )
    default_interval: str = Field(
        default="1d",
        description="Default interval code.",
    )
    price_basis: str = Field(
        ...,
        description="Trade price, midpoint, clean price, settlement.",
    )
    adjustment_basis: str = Field(
        ...,
        description="Split-adjusted, raw, total return, or unadjusted.",
    )
    provider_key: str = Field(
        ...,
        description="Authoritative data provider or market data feed provenance.",
    )
    has_volume: bool = Field(
        default=True,
        description="True if this instrument produces genuine volume observations.",
    )
    is_futures: bool = Field(
        default=False,
        description="True if this is an exchange-traded individual futures contract.",
    )
    allows_negative_price: bool = Field(
        default=False,
        description="True if negative prices are valid for this instrument (e.g. WTI Crude).",
    )
    contract_expiration: Optional[str] = Field(
        default=None,
        description="Contract expiration ISO timestamp if applicable.",
    )
    base_asset: Optional[str] = Field(
        default=None,
        description="Base currency or asset (e.g. BTC in BTC/USDT).",
    )
    quote_asset: Optional[str] = Field(
        default=None,
        description="Quote currency or asset (e.g. USDT in BTC/USDT).",
    )


class ChartCoverageDTO(BaseModel):
    """Data coverage, range bounds, and quality metrics for the chart request."""

    model_config = ConfigDict(frozen=True)

    requested_start: Optional[str] = Field(
        default=None,
        description="Requested start boundary ISO timestamp.",
    )
    requested_end: Optional[str] = Field(
        default=None,
        description="Requested end boundary ISO timestamp.",
    )
    earliest_available_bar: Optional[str] = Field(
        default=None,
        description="Timestamp of the earliest available bar in the database.",
    )
    latest_available_bar: Optional[str] = Field(
        default=None,
        description="Timestamp of the latest available bar in the database.",
    )
    returned_bars_count: int = Field(
        ...,
        description="Number of bars returned in this specific payload.",
    )
    total_bars_available: int = Field(
        ...,
        description="Total number of stored bars for this instrument in the system.",
    )
    has_more: bool = Field(
        default=False,
        description="True if earlier historical bars exist prior to this page.",
    )
    known_gaps_count: int = Field(
        default=0,
        description="Number of non-calendar gaps identified in the observation series.",
    )
    source_status: str = Field(
        default="QUALIFIED",
        description="Source status: QUALIFIED, PARTIAL, DEGRADED, or UNAVAILABLE.",
    )


class ChartPaginationDTO(BaseModel):
    """Pagination metadata for incremental historical data backfill."""

    model_config = ConfigDict(frozen=True)

    limit: int = Field(
        ...,
        description="Requested maximum bar count limit.",
    )
    has_more: bool = Field(
        ...,
        description="True if older bars exist before the earliest returned bar.",
    )
    next_cursor: Optional[str] = Field(
        default=None,
        description="Cursor token representing the timestamp before which to fetch older bars.",
    )


class ChartHistoryResponse(BaseModel):
    """Top-level response payload for GET /api/v1/charts/history."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = Field(
        default="1.0.0",
        description="Schema contract version.",
    )
    instrument: ChartInstrumentMetadata = Field(
        ...,
        description="Metadata for the charted canonical financial instrument.",
    )
    interval: str = Field(
        default="1d",
        description="Resolved bar interval code.",
    )
    bars: List[ChartBarDTO] = Field(
        ...,
        description="Chronological ascending array of valid canonical OHLCV bars.",
    )
    coverage: ChartCoverageDTO = Field(
        ...,
        description="Auditable data coverage and quality metadata.",
    )
    pagination: Optional[ChartPaginationDTO] = Field(
        default=None,
        description="Pagination metadata for viewport backfill.",
    )
    interval_source_kind: str = Field(
        default="NATIVE",
        description="Whether returned bars are NATIVE (source stored) or DERIVED (aggregated).",
    )
    derived_source_interval: Optional[str] = Field(
        default=None,
        description="Source interval used if bars were mathematically aggregated (e.g. '1d').",
    )


class ChartIntervalOptionDTO(BaseModel):
    """Typed representation of a selectable chart interval."""

    model_config = ConfigDict(frozen=True)

    interval_id: str = Field(
        ...,
        description="Canonical interval code (e.g. 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M).",
    )
    display_label: str = Field(
        ...,
        description="Human-readable interval display label.",
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        description="Nominal duration of the interval in seconds (None for calendar intervals).",
    )
    availability: str = Field(
        default="AVAILABLE_NATIVE",
        description="Availability: AVAILABLE_NATIVE, AVAILABLE_DERIVED, PARTIAL, UNAVAILABLE.",
    )
    native_or_derived: str = Field(
        default="NATIVE",
        description="Lineage classification: NATIVE, DERIVED, or UNAVAILABLE.",
    )
    is_supported: bool = Field(
        default=True,
        description="True if this interval can be charted for the instrument.",
    )
    source_interval: Optional[str] = Field(
        default=None,
        description="Constituent base interval code if derived (e.g. '1d' or '1m').",
    )
    earliest_available: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC timestamp of earliest available bar.",
    )
    latest_available: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC timestamp of latest available bar.",
    )
    live_bar_supported: bool = Field(
        default=False,
        description="True if provisional live bar updates are supported for this interval.",
    )
    unavailability_reason: Optional[str] = Field(
        default=None,
        description="Explicit explanation if this interval cannot be provided.",
    )


class ChartIntervalsResponse(BaseModel):
    """Response payload for GET /api/v1/charts/intervals."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = Field(
        default="1.0.0",
        description="Contract schema version.",
    )
    instrument_entity_id: UUID = Field(
        ...,
        description="Canonical instrument UUID.",
    )
    display_symbol: str = Field(
        ...,
        description="Authoritative ticker or market symbol.",
    )
    instrument: Optional[ChartInstrumentMetadata] = Field(
        default=None,
        description="Canonical instrument metadata.",
    )
    default_interval: str = Field(
        default="1d",
        description="Default baseline interval code.",
    )
    intervals: List[ChartIntervalOptionDTO] = Field(
        ...,
        description="Complete list of selectable and available intervals.",
    )


class ChartSearchResponse(BaseModel):
    """Response payload for GET /api/v1/charts/instruments."""

    model_config = ConfigDict(frozen=True)

    results: List[ChartInstrumentMetadata] = Field(
        ...,
        description="Matching canonical chartable instruments.",
    )
    count: int = Field(
        ...,
        description="Total number of results returned.",
    )


# ============================================================================
# Stage 67 Live Chart Streaming DTOs
# ============================================================================


class LiveQuoteDTO(BaseModel):
    """Canonical representation of an accepted live quote observation.

    Strict financial integrity rules:
    - Quote snapshot is not a complete trade feed.
    - Bid/ask are not last. Midpoint is not an executed trade.
    - Quote count is not volume.
    - Negative commodity futures prices are fully supported.
    """

    model_config = ConfigDict(frozen=True)

    bid_price: Optional[Decimal] = Field(
        default=None,
        description="Highest price a buyer will pay. Decimal precision preserved.",
    )
    ask_price: Optional[Decimal] = Field(
        default=None,
        description="Lowest price a seller will accept. Decimal precision preserved.",
    )
    bid_size: Optional[Decimal] = Field(
        default=None,
        description="Quantity offered at bid price.",
    )
    ask_size: Optional[Decimal] = Field(
        default=None,
        description="Quantity offered at ask price.",
    )
    last_price: Optional[Decimal] = Field(
        default=None,
        description="Real executed trade or settlement price. None when quote has bid/ask only.",
    )
    last_size: Optional[Decimal] = Field(
        default=None,
        description="Real executed transaction quantity. Never fabricated from quote updates.",
    )
    as_of: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC source observation timestamp.",
    )
    is_midpoint: bool = Field(
        default=False,
        description="Flag indicating whether value is an indicative midpoint rather than a trade.",
    )
    has_genuine_last: bool = Field(
        default=False,
        description="True if last_price represents a genuine qualified executed transaction.",
    )


class ChartLiveStateResponse(BaseModel):
    """Authoritative snapshot of the live market streaming state for a chart instrument."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = Field(
        default="1.0.0",
        description="Schema contract version.",
    )
    instrument_entity_id: UUID = Field(
        ...,
        description="Canonical instrument UUID.",
    )
    display_symbol: str = Field(
        ...,
        description="Authoritative ticker or market symbol.",
    )
    market_or_venue: str = Field(
        ...,
        description="Primary venue or exchange.",
    )
    price_currency: str = Field(
        ...,
        description="Quoted currency code.",
    )
    quotation_unit: str = Field(
        ...,
        description="Quotation convention (e.g. USD/share, % par, USD/barrel).",
    )
    quote: Optional[LiveQuoteDTO] = Field(
        default=None,
        description="Latest accepted market quote observation.",
    )
    source_timestamp: Optional[str] = Field(
        default=None,
        description="Source observation time in ISO 8601 UTC.",
    )
    received_at: Optional[str] = Field(
        default=None,
        description="System receipt time in ISO 8601 UTC.",
    )
    provider: str = Field(
        default="canonical_feed",
        description="Authoritative source provider identifier.",
    )
    freshness_status: str = Field(
        default="LIVE",
        description="Freshness classification: LIVE, DELAYED, STALE, UNKNOWN, UNAVAILABLE.",
    )
    delay_status: str = Field(
        default="REALTIME",
        description="Feed delay classification: REALTIME, DELAYED_15M, UNKNOWN.",
    )
    live_capability: str = Field(
        default="LIVE_PRICE_AVAILABLE",
        description="Live capability: LIVE_PRICE_AVAILABLE, HISTORICAL_ONLY, LIVE_BAR_AVAILABLE.",
    )
    availability: str = Field(
        default="AVAILABLE",
        description="Availability status: AVAILABLE, UNAVAILABLE.",
    )
    is_paused: bool = Field(
        default=False,
        description="Whether live stream updates are paused in client viewport.",
    )
