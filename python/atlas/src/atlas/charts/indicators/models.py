"""Domain models and DTO schemas for Technical Indicator Infrastructure (Stage 69).

Defines:
- Enums for indicator categories, parameter types, rendering targets, and calculation statuses.
- Parameter and indicator definitions for registration in the allowlisted registry.
- Indicator calculation request and response DTOs with time-aligned points.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IndicatorCategory(str, Enum):
    """Classification category for technical indicators."""

    TREND = "TREND"
    MOMENTUM = "MOMENTUM"
    VOLATILITY = "VOLATILITY"
    VOLUME = "VOLUME"
    STATISTICAL = "STATISTICAL"


class IndicatorRenderingTarget(str, Enum):
    """Visual rendering surface for the indicator output."""

    PRICE_OVERLAY = "PRICE_OVERLAY"
    INDICATOR_PANE = "INDICATOR_PANE"


class IndicatorParameterType(str, Enum):
    """Primitive type for indicator parameters."""

    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"


class IndicatorStatus(str, Enum):
    """Status classification for indicator calculation output points and series."""

    READY = "READY"
    WARMUP = "WARMUP"
    DATA_GAP = "DATA_GAP"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    INCOMPATIBLE_INPUT = "INCOMPATIBLE_INPUT"
    MISSING_VOLUME = "MISSING_VOLUME"
    TALIB_UNAVAILABLE = "TALIB_UNAVAILABLE"
    UNSUPPORTED_INTERVAL = "UNSUPPORTED_INTERVAL"
    NOT_ENTITLED = "NOT_ENTITLED"
    CALCULATION_ERROR = "CALCULATION_ERROR"


class IndicatorParameterDefinition(BaseModel):
    """Schema defining a validated indicator parameter."""

    name: str = Field(..., description="Parameter key name (e.g. 'period', 'source')")
    type: IndicatorParameterType = Field(..., description="Parameter primitive data type")
    default: Any = Field(..., description="Authoritative default parameter value")
    required: bool = Field(True, description="Whether parameter is mandatory")
    min_value: Optional[float] = Field(
        None, description="Minimum permissible numeric value (inclusive)"
    )
    max_value: Optional[float] = Field(
        None, description="Maximum permissible numeric value (inclusive)"
    )
    allowed_values: Optional[List[Any]] = Field(
        None, description="Permissible enumeration values if restricted"
    )
    description: Optional[str] = Field(
        None, description="Human-readable description of parameter impact"
    )


class IndicatorDefinition(BaseModel):
    """Metadata schema defining a registered technical indicator."""

    indicator_id: str = Field(..., description="Unique namespaced identifier (e.g. 'atlas.sma')")
    version: int = Field(1, ge=1, description="Indicator definition schema version")
    display_name: str = Field(
        ..., description="Human-readable title (e.g. 'Simple Moving Average')"
    )
    description: str = Field(..., description="Mathematical calculation summary")
    category: IndicatorCategory = Field(IndicatorCategory.TREND, description="Analytical category")
    rendering_target: IndicatorRenderingTarget = Field(
        IndicatorRenderingTarget.PRICE_OVERLAY,
        description="Whether rendered on primary price scale or independent subpane",
    )
    input_requirements: List[str] = Field(
        default_factory=lambda: ["close"],
        description="Required OHLCV constituent fields (e.g. ['close'], ['volume'])",
    )
    parameters: List[IndicatorParameterDefinition] = Field(
        default_factory=list,
        description="List of configurable parameter definitions",
    )
    default_color: str = Field(
        "#38bdf8", description="Default HEX stroke color (e.g. '#38bdf8' sky-400)"
    )
    default_line_width: int = Field(2, ge=1, le=5, description="Default line width in pixels")
    supported_intervals: List[str] = Field(
        default_factory=lambda: ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
        description="Compatible chart intervals",
    )
    min_history_bars: int = Field(
        2, ge=1, description="Minimum total history bars required for meaningful evaluation"
    )
    output_names: List[str] = Field(
        default_factory=lambda: ["main"],
        description="Names of output series produced (e.g. ['macd', 'signal', 'histogram'])",
    )


class IndicatorPoint(BaseModel):
    """Single time-aligned calculation point."""

    timestamp: str = Field(
        ..., description="ISO 8601 UTC timestamp identical to constituent source bar"
    )
    time_unix: int = Field(..., description="Unix epoch timestamp in seconds")
    value: Optional[float] = Field(
        None,
        description="Calculated numeric value, or None if in warmup, gap, or insufficient history",
    )
    status: IndicatorStatus = Field(
        IndicatorStatus.READY, description="Classification of point status"
    )


class IndicatorOutputSeries(BaseModel):
    """Output series for an indicator (allows multi-line or band indicators in future)."""

    series_id: str = Field(
        ...,
        description="Unique series identifier within indicator (e.g. 'main', 'upper')",
    )
    name: str = Field(..., description="Human-readable series name")
    rendering_type: str = Field("LINE", description="Visual style: LINE, HISTOGRAM, BAND")
    unit: Optional[str] = Field(
        None, description="Output measurement unit (e.g. 'USD', 'percent', 'points', 'volume')"
    )
    color: Optional[str] = Field(None, description="Rendered stroke color")
    line_width: Optional[int] = Field(None, description="Rendered line width")
    points: List[IndicatorPoint] = Field(
        default_factory=list, description="Ordered time-aligned points"
    )


class IndicatorInstanceConfig(BaseModel):
    """Client configuration for an active indicator instance on a chart."""

    instance_id: str = Field(
        ..., description="Client-unique instance identifier (e.g. 'sma-1', 'sma-2')"
    )
    indicator_id: str = Field(..., description="Namespaced indicator ID (e.g. 'atlas.sma')")
    version: int = Field(1, ge=1, description="Requested indicator definition version")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="User-selected parameter dictionary (e.g. {'period': 20, 'source': 'close'})",
    )
    visible: bool = Field(True, description="Whether series is visible on canvas")
    color: Optional[str] = Field(None, description="Custom line color override")
    line_width: Optional[int] = Field(None, ge=1, le=5, description="Custom line width override")


class IndicatorCalculationRequest(BaseModel):
    """Request payload to calculate one or more indicator instances."""

    instrument_id: Optional[str] = Field(None, description="Canonical instrument UUID")
    symbol: Optional[str] = Field(
        None, description="Instrument ticker symbol (e.g. 'SPY', 'BTCUSDT')"
    )
    interval: str = Field(
        "1d", description="Canonical chart interval (e.g. 1m, 5m, 1h, 1d, 1w, 1M)"
    )
    start: Optional[datetime] = Field(
        None, description="Requested visible start time boundary (inclusive)"
    )
    end: Optional[datetime] = Field(
        None, description="Requested visible end time boundary (exclusive)"
    )
    instances: List[IndicatorInstanceConfig] = Field(
        ...,
        min_length=1,
        max_length=12,
        description="List of active indicator instances to compute (max 12 per request)",
    )


class IndicatorCalculationResult(BaseModel):
    """Computed result for a single indicator instance."""

    instance_id: str = Field(..., description="Matching client instance ID")
    indicator_id: str = Field(..., description="Namespaced indicator identifier")
    version: int = Field(..., description="Calculated indicator version")
    parameters: Dict[str, Any] = Field(
        ...,
        description="Authoritative normalized parameters applied",
    )
    rendering_target: IndicatorRenderingTarget = Field(
        ...,
        description="Target rendering surface",
    )
    status: IndicatorStatus = Field(..., description="Overall calculation status")
    error_message: Optional[str] = Field(
        None,
        description="Details if status is an error or insufficient history",
    )
    required_lookback_bars: int = Field(
        ...,
        description="Number of earlier bars consumed for warmup",
    )
    series: List[IndicatorOutputSeries] = Field(
        default_factory=list,
        description="Output series list",
    )


class IndicatorCalculationResponse(BaseModel):
    """Response envelope for technical indicator calculation request."""

    instrument_entity_id: str = Field(..., description="Canonical instrument UUID")
    symbol: str = Field(..., description="Resolved ticker symbol")
    interval: str = Field(..., description="Bar interval used for calculation")
    calculated_at: str = Field(..., description="ISO 8601 calculation execution timestamp")
    results: List[IndicatorCalculationResult] = Field(
        ...,
        description="Computed results per instance",
    )


class IndicatorCatalogResponse(BaseModel):
    """Catalog response listing all registered and approved technical indicators."""

    indicators: List[IndicatorDefinition] = Field(
        ...,
        description="Registered indicator definitions",
    )
