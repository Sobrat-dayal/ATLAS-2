"""Domain Models and Value Objects for ATLAS Spatial Analytics Engine (Stage 131).

Defines canonical representations of H3 aggregates, metrics, aggregation methods,
visualization types, query parameters, source provenance, materialization jobs,
and privacy policies.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from atlas.maps.domain import DataQualityStatus, GeoBoundingBox, LicensingPolicy


class SpatialVisualizationType(str, Enum):
    """Supported deck.gl and 3D globe analytical visualization modes."""

    SCATTERPLOT = "scatterplot"
    H3_HEXAGON = "h3_hexagon"
    HEATMAP = "heatmap"
    HEXAGON_GRID = "hexagon_grid"


class SpatialAggregationMethod(str, Enum):
    """Supported aggregation functions for geospatial records."""

    COUNT = "count"
    SUM = "sum"
    MEAN = "mean"
    WEIGHTED_MEAN = "weighted_mean"
    DISTINCT_COUNT = "distinct_count"
    DENSITY = "density"


class NullValuePolicy(str, Enum):
    """Policy for handling null or missing numeric values in calculations."""

    EXCLUDE = "exclude"
    ZERO = "zero"
    WARN = "warn"


class TimeBucketInterval(str, Enum):
    """Temporal bucketing intervals for historical geographic analytics."""

    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    QUARTER = "1q"
    YEAR = "1y"


@dataclass(frozen=True)
class SpatialMetricDefinition:
    """Canonical registry definition of an analytical metric."""

    metric_id: str
    dataset_id: str
    display_name: str
    description: str
    unit: str
    value_type: str  # "float", "integer", "currency", "percentage"
    allowed_aggregations: List[SpatialAggregationMethod]
    default_aggregation: SpatialAggregationMethod = SpatialAggregationMethod.COUNT
    currency: Optional[str] = None  # e.g. "USD", "EUR"
    weight_metric_id: Optional[str] = None
    null_policy: NullValuePolicy = NullValuePolicy.EXCLUDE
    minimum_contributor_threshold: int = 5
    is_temporal: bool = False
    source_entitlement_required: Optional[str] = None

    def supports_aggregation(self, method: SpatialAggregationMethod) -> bool:
        return method in self.allowed_aggregations


@dataclass
class AtlasH3Aggregate:
    """Canonical aggregated record for a single H3 hexagon cell."""

    h3_cell_id: str
    h3_resolution: int
    metric_id: str
    aggregation_method: SpatialAggregationMethod
    value: float
    record_count: int
    non_null_count: int
    distinct_count: Optional[int] = None
    valid_weight_sum: Optional[float] = None
    cell_area_km2: float = 0.0
    density: float = 0.0  # value or count / cell_area_km2
    unit: str = ""
    is_suppressed: bool = False  # True when contributors < privacy threshold
    time_bucket: Optional[str] = None
    data_quality: DataQualityStatus = DataQualityStatus.VERIFIED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "h3_cell_id": self.h3_cell_id,
            "h3_resolution": self.h3_resolution,
            "metric_id": self.metric_id,
            "aggregation_method": self.aggregation_method.value,
            "value": None if self.is_suppressed else self.value,
            "record_count": self.record_count,
            "non_null_count": self.non_null_count,
            "distinct_count": None if self.is_suppressed else self.distinct_count,
            "valid_weight_sum": self.valid_weight_sum,
            "cell_area_km2": round(self.cell_area_km2, 4),
            "density": None if self.is_suppressed else round(self.density, 4),
            "unit": self.unit,
            "is_suppressed": self.is_suppressed,
            "time_bucket": self.time_bucket,
            "data_quality": self.data_quality.value,
        }


@dataclass
class SpatialAnalyticsQuery:
    """Canonical query specification for geospatial analytics."""

    dataset_id: str
    metric_id: str
    aggregation: SpatialAggregationMethod
    visualization_type: SpatialVisualizationType
    h3_resolution: int = 5
    bounds: Optional[GeoBoundingBox] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    time_range_start: Optional[datetime.datetime] = None
    time_range_end: Optional[datetime.datetime] = None
    time_bucket: Optional[TimeBucketInterval] = None
    historical_as_of: Optional[datetime.datetime] = None
    min_contributors: int = 5
    result_limit: int = 5000
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None


@dataclass
class SpatialSummaryStatistics:
    """Statistical summary across all aggregated cells or points."""

    total_records: int
    total_cells: int
    suppressed_cells: int
    sum_value: float
    mean_value: float
    min_value: float
    max_value: float
    weighted_mean: Optional[float] = None
    unit: str = ""


@dataclass
class SpatialAnalyticsResult:
    """Canonical response containing aggregated cells, bounds, and provenance."""

    query_id: str
    dataset_id: str
    dataset_version: str
    metric_id: str
    aggregation: SpatialAggregationMethod
    visualization_type: SpatialVisualizationType
    h3_resolution: int
    unit: str
    aggregates: List[AtlasH3Aggregate]
    summary: SpatialSummaryStatistics
    bounds: Optional[GeoBoundingBox] = None
    time_scope: Optional[Dict[str, Any]] = None
    data_quality: DataQualityStatus = DataQualityStatus.VERIFIED
    source_attribution: str = ""
    licensing_policy: LicensingPolicy = LicensingPolicy.OPEN_DATA_CC_BY
    is_truncated: bool = False
    execution_time_ms: float = 0.0
    computed_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "dataset_id": self.dataset_id,
            "dataset_version": self.dataset_version,
            "metric_id": self.metric_id,
            "aggregation": self.aggregation.value,
            "visualization_type": self.visualization_type.value,
            "h3_resolution": self.h3_resolution,
            "unit": self.unit,
            "aggregates": [agg.to_dict() for agg in self.aggregates],
            "summary": {
                "total_records": self.summary.total_records,
                "total_cells": self.summary.total_cells,
                "suppressed_cells": self.summary.suppressed_cells,
                "sum_value": self.summary.sum_value,
                "mean_value": self.summary.mean_value,
                "min_value": self.summary.min_value,
                "max_value": self.summary.max_value,
                "weighted_mean": self.summary.weighted_mean,
                "unit": self.summary.unit,
            },
            "bounds": self.bounds.to_list() if self.bounds else None,
            "time_scope": self.time_scope,
            "data_quality": self.data_quality.value,
            "source_attribution": self.source_attribution,
            "licensing_policy": self.licensing_policy.value,
            "is_truncated": self.is_truncated,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "computed_at": self.computed_at.isoformat(),
        }


@dataclass
class RegionComparisonResult:
    """Comparison metrics between two geographic bounding regions."""

    region_a_name: str
    region_b_name: str
    metric_id: str
    unit: str
    region_a_summary: SpatialSummaryStatistics
    region_b_summary: SpatialSummaryStatistics
    absolute_difference: float
    relative_difference_pct: Optional[float]
    higher_region: Optional[str]
    area_normalized_a: float
    area_normalized_b: float


class MaterializationJobStatus(str, Enum):
    """Status lifecycle for background aggregate materialization."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class MaterializationJob:
    """Metadata tracking durable preaggregation jobs."""

    job_id: str
    dataset_id: str
    dataset_revision: str
    metric_id: str
    h3_resolution: int
    status: MaterializationJobStatus
    records_processed: int = 0
    total_records: int = 0
    cells_generated: int = 0
    error_message: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    completed_at: Optional[datetime.datetime] = None
