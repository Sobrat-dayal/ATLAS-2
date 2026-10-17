"""Pydantic Models and Data Transfer Objects for ATLAS Market Movers V1 (Stage 63).

Guarantees:
- Institutional numerical fidelity using Decimal.
- Explicit ranking value units, observation windows, and timestamps.
- Transparent ranking coverage reporting (candidate, qualified, excluded counts, exclusion reasons).
- Keyset-based pagination with deterministic ordering.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .config import (
    ComparisonWindow,
    CoverageStatus,
    MoverAssetClass,
    MoverCategory,
    MoverMetricDefinition,
    MoverUniverseDefinition,
)


class MoverRankedItem(BaseModel):
    """An individual security or series ranked within a qualified mover snapshot."""

    model_config = ConfigDict(frozen=True)

    rank: int = Field(..., ge=1, description="1-based ordinal rank within the snapshot.")
    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority (Stage 17)."
    )
    market_series_identity: str = Field(
        ..., description="Exact listing or venue-scoped series key."
    )
    display_name: str = Field(..., min_length=1, max_length=256)
    symbol: str = Field(..., min_length=1, max_length=64)
    asset_class: MoverAssetClass
    exchange_or_venue: str = Field(..., description="Exchange MIC or venue identifier.")

    # Ranking Metric Values
    ranking_value: Decimal = Field(
        ..., description="Exact primary metric value upon which this item was sorted."
    )
    ranking_unit: str = Field(
        ...,
        description="Explicit unit of the ranking metric (e.g. %, shares, contracts, USDT).",
    )

    # Qualified Underlying Observations
    current_observation: Optional[Decimal] = Field(
        default=None, description="Current traded price or rate observation."
    )
    reference_observation: Optional[Decimal] = Field(
        default=None, description="Prior qualified reference price, close, or settlement."
    )
    absolute_change: Optional[Decimal] = Field(
        default=None, description="Absolute price or rate change (current - reference)."
    )
    percent_change: Optional[Decimal] = Field(
        default=None, description="Percentage return ((current - reference) / reference * 100)."
    )
    activity_observation: Optional[Decimal] = Field(
        default=None, description="Observed trading activity (shares, contracts, or turnover)."
    )
    activity_unit: Optional[str] = Field(
        default=None, description="Unit of trading activity if present."
    )

    # Provenance and Timestamps
    source_timestamp: Optional[datetime] = Field(
        default=None, description="Observation timestamp of the current market quote."
    )
    reference_timestamp: Optional[datetime] = Field(
        default=None, description="Timestamp or date of the reference price observation."
    )
    reference_period_label: Optional[str] = Field(
        default=None,
        description="Human-readable reference description (e.g. 'Prev Close (2026-10-16)').",
    )
    provider: str = Field(default="atlas_core", description="Provider source or attribution.")
    freshness_status: str = Field(
        default="live", description="Freshness status (live, delayed, stale)."
    )
    delay_status: str = Field(default="realtime", description="Delivery delay classification.")
    delivery_delay_seconds: Optional[int] = Field(default=None)
    eligibility_notes: Optional[str] = Field(default=None)


class MoverCoverage(BaseModel):
    """Institutional ranking coverage transparency report."""

    model_config = ConfigDict(frozen=True)

    universe_size: int = Field(
        ..., ge=0, description="Total authorized candidate count defined in this universe."
    )
    candidate_count: int = Field(
        ..., ge=0, description="Number of candidates retrieved for evaluation."
    )
    evaluated_count: int = Field(
        ..., ge=0, description="Number of candidates evaluated through qualification pipeline."
    )
    qualified_count: int = Field(
        ..., ge=0, description="Number of candidates passing all qualification criteria."
    )
    excluded_count: int = Field(
        ..., ge=0, description="Number of candidates excluded from the ranking."
    )
    exclusion_reasons: Dict[str, int] = Field(
        default_factory=dict,
        description="Aggregate count of candidates excluded by specific typed ExclusionReason.",
    )
    coverage_status: CoverageStatus = Field(
        ..., description="Coverage completeness classification."
    )
    ranking_as_of: datetime = Field(
        ..., description="Timestamp at which this ranking snapshot was computed."
    )


class MarketMoverResponse(BaseModel):
    """Full API response for Market Movers ranking query."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "v1"
    snapshot_id: str = Field(
        ..., description="Deterministic or unique identifier of the computed ranking snapshot."
    )
    universe_id: str
    universe_display_name: str
    category: MoverCategory
    metric_id: str
    window: ComparisonWindow
    asset_class: MoverAssetClass
    calculated_at: datetime
    coverage: MoverCoverage
    items: List[MoverRankedItem]
    next_cursor: Optional[str] = None
    has_more: bool = False
    source_status: str = "ok"


class MoverUniverseResponse(BaseModel):
    """Response containing supported mover universes."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "v1"
    universes: List[MoverUniverseDefinition]
    default_universe_id: str


class MoverMetricOptionsResponse(BaseModel):
    """Response describing available ranking metrics and windows for a universe."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "v1"
    universe_id: str
    asset_class: MoverAssetClass
    supported_categories: List[MoverCategory]
    supported_windows: List[ComparisonWindow]
    activity_metric_label: Optional[str] = None
    activity_unit: Optional[str] = None
    metrics: List[MoverMetricDefinition]
