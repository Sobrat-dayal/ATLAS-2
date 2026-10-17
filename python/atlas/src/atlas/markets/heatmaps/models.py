"""Pydantic Models and Data Transfer Objects for ATLAS Market Heatmaps V1 (Stage 64).

Guarantees:
- Institutional numerical fidelity using Decimal for all financial quantities.
- Explicit visualization modes: Equal-Size vs Market-Cap Weighted.
- Transparent coverage reporting: counts of qualified, missing returns,
  missing weights, unclassified items.
- Strict grouping hierarchy with verified sector and industry aggregation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .config import (
    HeatmapComparisonWindow,
    HeatmapCoverageStatus,
    HeatmapExclusionReason,
    HeatmapHierarchyMode,
    HeatmapUniverseDefinition,
    HeatmapVisualizationMode,
)


class HeatmapLeafNode(BaseModel):
    """An individual security or series tile visualized within a market heatmap."""

    model_config = ConfigDict(frozen=True)

    node_id: str = Field(..., description="Unique stable node identifier.")
    node_kind: Literal["instrument"] = "instrument"
    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority (Stage 17)."
    )
    market_series_identity: str = Field(
        ..., description="Exact listing or venue-scoped series key."
    )
    symbol: str = Field(..., min_length=1, max_length=64)
    display_name: str = Field(..., min_length=1, max_length=256)
    asset_class: str
    exchange_or_venue: str
    sector: Optional[str] = Field(default=None, description="Authoritative sector classification.")
    industry: Optional[str] = Field(
        default=None, description="Authoritative industry classification."
    )

    # Performance metric observations
    current_price: Optional[Decimal] = Field(
        default=None, description="Current traded price or rate observation."
    )
    reference_price: Optional[Decimal] = Field(
        default=None, description="Prior qualified reference price or settlement."
    )
    percent_change: Optional[Decimal] = Field(
        default=None, description="Percentage return ((current - reference) / reference * 100)."
    )
    absolute_change: Optional[Decimal] = Field(
        default=None, description="Absolute price change (current - reference)."
    )

    # Weighting metrics
    weight_value: Optional[Decimal] = Field(
        default=None, description="Verified market capitalization or weighting value."
    )
    weight_unit: Optional[str] = Field(
        default=None, description="Explicit unit of weight (e.g. USD, USDT)."
    )
    normalized_weight: Optional[Decimal] = Field(
        default=None,
        description="Proportional area fraction of total qualified universe (0.0 to 1.0).",
    )

    currency: str = Field(default="USD")
    freshness_status: str = Field(
        default="live", description="Freshness status (live, delayed, stale)."
    )
    delay_status: str = Field(default="realtime", description="Delivery delay classification.")
    delivery_delay_seconds: Optional[int] = Field(default=None)
    provider: str = Field(default="atlas_core", description="Provider source or attribution.")
    source_timestamp: Optional[datetime] = Field(
        default=None, description="Observation timestamp of the current market quote."
    )
    reference_timestamp: Optional[datetime] = Field(
        default=None, description="Timestamp or date of the reference price observation."
    )
    reference_period_label: Optional[str] = Field(default=None)

    # Qualification & Exclusion
    is_qualified: bool = Field(default=True)
    exclusion_reason: Optional[HeatmapExclusionReason] = Field(default=None)


class HeatmapGroupNode(BaseModel):
    """A sector or industry group node aggregating constituent leaf nodes."""

    model_config = ConfigDict(frozen=True)

    group_id: str = Field(..., description="Unique stable group key (e.g. 'sector:Technology').")
    group_kind: Literal["sector", "industry"] = "sector"
    label: str = Field(..., min_length=1, max_length=128)
    taxonomy: str = Field(default="GICS")
    constituent_count: int = Field(..., ge=0)
    qualified_count: int = Field(..., ge=0)

    # Aggregate performance
    aggregate_return: Optional[Decimal] = Field(
        default=None, description="Calculated aggregate return across qualified constituents."
    )
    aggregate_method: str = Field(
        default="equal_weight_mean",
        description=(
            "Explicit calculation methodology ('equal_weight_mean' or 'cap_weighted_return')."
        ),
    )

    # Aggregate weighting
    total_weight: Optional[Decimal] = Field(default=None, description="Sum of constituent weights.")
    normalized_weight: Optional[Decimal] = Field(
        default=None, description="Group area fraction of total universe (0.0 to 1.0)."
    )

    children: List[HeatmapLeafNode] = Field(default_factory=list)


class HeatmapCoverage(BaseModel):
    """Institutional heatmap coverage transparency report."""

    model_config = ConfigDict(frozen=True)

    universe_size: int = Field(
        ..., ge=0, description="Total authorized candidate count defined in this universe."
    )
    candidate_count: int = Field(..., ge=0, description="Number of candidates evaluated.")
    qualified_count: int = Field(
        ..., ge=0, description="Number of instruments with qualified price return observations."
    )
    missing_returns: int = Field(
        ..., ge=0, description="Count of instruments missing current price or reference price."
    )
    missing_weights: int = Field(
        ..., ge=0, description="Count of instruments lacking verified weighting data."
    )
    unclassified_count: int = Field(
        ..., ge=0, description="Count of instruments in 'Unclassified' sector."
    )
    coverage_status: HeatmapCoverageStatus
    total_qualified_weight: Optional[Decimal] = Field(
        default=None, description="Total verified market cap for qualified instruments."
    )
    exclusion_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Counts of items per HeatmapExclusionReason."
    )


class MarketHeatmapResponse(BaseModel):
    """Top-level response payload for ATLAS Market Heatmaps V1."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = Field(default="1.0.0")
    snapshot_id: str = Field(..., description="Coherent calculation snapshot UUID.")
    universe_id: str
    universe_name: str
    asset_class: str
    comparison_window: HeatmapComparisonWindow
    visualization_mode: HeatmapVisualizationMode
    hierarchy_mode: HeatmapHierarchyMode
    calculated_at: datetime = Field(
        ..., description="Timestamp when ATLAS computed this coherent snapshot."
    )

    weight_metric_label: Optional[str] = Field(default=None)
    weight_unit: Optional[str] = Field(default=None)

    color_domain_min: Decimal = Field(
        default=Decimal("-5.0"), description="Negative saturation boundary (%)"
    )
    color_domain_max: Decimal = Field(
        default=Decimal("5.0"), description="Positive saturation boundary (%)"
    )

    coverage: HeatmapCoverage

    # Heatmap layout data: either flat nodes or grouped by sector/industry
    nodes: List[HeatmapLeafNode] = Field(default_factory=list)
    groups: List[HeatmapGroupNode] = Field(default_factory=list)
    notes: Optional[str] = None


class HeatmapUniverseResponse(BaseModel):
    """List of supported heatmap candidate universes."""

    model_config = ConfigDict(frozen=True)

    universes: List[HeatmapUniverseDefinition]
    count: int


class HeatmapOptionsResponse(BaseModel):
    """Metadata detailing supported modes, hierarchies, and comparison windows."""

    model_config = ConfigDict(frozen=True)

    modes: List[HeatmapVisualizationMode]
    hierarchies: List[HeatmapHierarchyMode]
    windows: List[HeatmapComparisonWindow]
    taxonomies: List[str]
