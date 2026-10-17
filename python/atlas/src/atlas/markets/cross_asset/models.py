"""Pydantic Models and Data Transfer Objects for ATLAS Cross-Asset Markets V1 (Stage 65).

Guarantees:
- Institutional numerical fidelity using Decimal.
- Explicit native asset-class measurement semantics (yields vs returns vs rates vs points).
- Strict separation of Native Market Overview and Aligned Price Performance.
- Full provenance, source timestamps, and effective time offsets.
- Transparent coverage and exclusion reason reporting.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .config import (
    AssetClassEnum,
    CrossAssetCoverageStatus,
    CrossAssetExclusionReason,
    CrossAssetMode,
    CrossAssetUniverseDefinition,
    CrossAssetWindow,
    NativeMetricKind,
    ProxyKind,
)


class NativeMetricObservation(BaseModel):
    """Native financial observation adhering to its underlying market convention."""

    model_config = ConfigDict(frozen=True)

    metric_kind: NativeMetricKind = Field(
        ...,
        description=(
            "Exact measurement convention (e.g. price change %, yield bps, spot rate change %)."
        ),
    )
    display_label: str = Field(..., description="Human-readable measurement label.")
    current_value: Decimal = Field(
        ..., description="Latest qualified traded price, yield, or exchange rate."
    )
    reference_value: Optional[Decimal] = Field(
        default=None,
        description=(
            "Prior reference observation (e.g. previous regular session close or prior settlement)."
        ),
    )
    change_value: Optional[Decimal] = Field(
        default=None, description="Absolute change in native units (points, bps, price diff)."
    )
    change_percent: Optional[Decimal] = Field(
        default=None,
        description="Relative percentage change if natively applicable; None for bond yields.",
    )
    unit: str = Field(
        ..., description="Quotation unit (e.g. 'USD', '%', 'bps', 'USDT/BTC', 'USD/bbl')."
    )
    as_of_time: datetime = Field(
        ..., description="Timestamp of the latest source observation in UTC."
    )
    session_status: str = Field(
        default="OPEN", description="Trading session state: OPEN, CLOSED, or AFTER_HOURS."
    )


class AlignedPricePerformance(BaseModel):
    """Strict common-window time-aligned price performance evaluation."""

    model_config = ConfigDict(frozen=True)

    eligible: bool = Field(
        ..., description="True if instrument qualifies for common-window price comparison."
    )
    price_return_percent: Optional[Decimal] = Field(
        default=None, description="Decimal percentage price return ((end - start) / start) * 100."
    )
    indexed_value: Optional[Decimal] = Field(
        default=None, description="Normalized price level indexed to 100.0 at window start."
    )
    start_price: Optional[Decimal] = Field(
        default=None, description="Effective starting observation price."
    )
    end_price: Optional[Decimal] = Field(
        default=None, description="Effective ending observation price."
    )
    quote_currency: str = Field(
        ..., description="Quotation currency of the underlying price series."
    )
    quote_unit: str = Field(..., description="Physical or contractual quotation unit.")
    effective_start_time: Optional[datetime] = Field(
        default=None, description="Actual source timestamp of the start observation."
    )
    effective_end_time: Optional[datetime] = Field(
        default=None, description="Actual source timestamp of the end observation."
    )
    start_time_offset_seconds: Optional[int] = Field(
        default=None,
        description=(
            "Seconds difference between effective start observation and requested window start."
        ),
    )
    end_time_offset_seconds: Optional[int] = Field(
        default=None,
        description=(
            "Seconds difference between effective end observation and requested window end."
        ),
    )
    currency_interpretation: str = Field(
        default="LOCAL_QUOTE_CURRENCY_PRICE_RETURN",
        description="Explicit currency interpretation note.",
    )
    is_common_currency_converted: bool = Field(
        default=False,
        description="Whether price returns were converted via a unified FX service (False for V1).",
    )
    exclusion_reason: Optional[CrossAssetExclusionReason] = Field(
        default=None,
        description="Typed reason why instrument was excluded from aligned comparison.",
    )
    exclusion_detail: Optional[str] = Field(
        default=None, description="Specific institutional explanation for the exclusion."
    )


class CrossAssetMember(BaseModel):
    """A canonical market instrument or benchmark series participating in cross-asset analysis."""

    model_config = ConfigDict(frozen=True)

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority."
    )
    market_series_identity: str = Field(
        ..., description="Listing or venue-scoped series key (e.g. 'NYSE:SPY', 'BINANCE:BTCUSDT')."
    )
    display_name: str = Field(..., min_length=1, max_length=256)
    symbol: str = Field(..., min_length=1, max_length=64)
    asset_class: AssetClassEnum
    market_or_venue: str = Field(..., description="Exchange MIC or trading venue.")

    # Benchmark vs Proxy Disclosures
    is_benchmark: bool = Field(
        default=False,
        description="Whether this series represents an authoritative canonical benchmark index.",
    )
    is_proxy: bool = Field(
        default=False,
        description="Whether this instrument is an ETF or Futures proxy for a benchmark.",
    )
    proxy_kind: ProxyKind = Field(
        default=ProxyKind.NONE, description="Explicit proxy classification."
    )
    proxy_benchmark_target: Optional[str] = Field(
        default=None,
        description=(
            "Name of the underlying target index tracked by this proxy (e.g. 'S&P 500 Index')."
        ),
    )

    # Observations
    native_metric: NativeMetricObservation = Field(
        ..., description="Native asset-class market observation."
    )
    aligned_performance: AlignedPricePerformance = Field(
        ..., description="Common-window aligned price performance result."
    )

    # Provenance and Freshness
    freshness_status: str = Field(
        default="FRESH", description="Freshness classification (FRESH, STALE, DELAYED)."
    )
    is_delayed: bool = Field(
        default=False, description="Whether observations are subject to statutory exchange delays."
    )
    delay_minutes: int = Field(default=0, ge=0)
    provider: str = Field(default="CANONICAL_FEED", description="Source provider authority.")


class AssetClassSummarySection(BaseModel):
    """High-density summary section for an individual asset class in Native Market Overview."""

    model_config = ConfigDict(frozen=True)

    asset_class: AssetClassEnum
    display_title: str
    native_metric_description: str
    representative_members: List[CrossAssetMember]
    total_members: int = Field(..., ge=0)
    qualified_members: int = Field(..., ge=0)
    coverage_status: CrossAssetCoverageStatus


class CrossAssetCoverage(BaseModel):
    """Institutional evaluation of cross-asset comparison completeness and exclusions."""

    model_config = ConfigDict(frozen=True)

    requested_members: int = Field(..., ge=0)
    authorized_members: int = Field(..., ge=0)
    evaluated_members: int = Field(..., ge=0)
    qualified_members: int = Field(..., ge=0)
    excluded_members: int = Field(..., ge=0)
    exclusions_by_reason: Dict[str, int] = Field(default_factory=dict)
    included_asset_classes: List[AssetClassEnum]
    unavailable_asset_classes: List[AssetClassEnum]
    completeness_status: CrossAssetCoverageStatus


class CrossAssetOverviewResponse(BaseModel):
    """Institutional snapshot response for the Cross-Asset Markets Workspace."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = Field(default="1.0.0")
    snapshot_id: str = Field(
        ..., description="Unique deterministic identifier for this cross-asset snapshot."
    )
    universe_id: str
    universe_name: str
    mode: CrossAssetMode
    comparison_window: CrossAssetWindow
    requested_start: datetime
    requested_end: datetime
    calculated_at: datetime
    alignment_methodology: str
    currency_policy_label: str
    coverage: CrossAssetCoverage
    asset_class_sections: List[AssetClassSummarySection]
    comparison_members: List[CrossAssetMember]
    exclusions: List[Dict[str, Any]] = Field(default_factory=list)


class CrossAssetUniverseResponse(BaseModel):
    """Response containing supported cross-asset universes."""

    model_config = ConfigDict(frozen=True)

    universes: List[CrossAssetUniverseDefinition]
    count: int = Field(..., ge=0)


class CrossAssetOptionsResponse(BaseModel):
    """Supported options, analytical modes, windows, and policies."""

    model_config = ConfigDict(frozen=True)

    modes: List[CrossAssetMode]
    windows: List[CrossAssetWindow]
    asset_classes: List[AssetClassEnum]
    max_selection_count: int
    currency_policy: str
    alignment_tolerance_seconds: int
