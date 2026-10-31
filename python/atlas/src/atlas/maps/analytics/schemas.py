"""Pydantic Request and Response Schemas for Spatial Analytics API (Stage 131)."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from atlas.maps.analytics.domain import (
    SpatialAggregationMethod,
    SpatialVisualizationType,
    TimeBucketInterval,
)


class GeoBoundingBoxDTO(BaseModel):
    west: float = Field(..., ge=-180.0, le=180.0)
    south: float = Field(..., ge=-90.0, le=90.0)
    east: float = Field(..., ge=-180.0, le=180.0)
    north: float = Field(..., ge=-90.0, le=90.0)


class SpatialAnalyticsQueryRequest(BaseModel):
    dataset_id: str
    metric_id: str
    aggregation: SpatialAggregationMethod = SpatialAggregationMethod.COUNT
    visualization_type: SpatialVisualizationType = SpatialVisualizationType.H3_HEXAGON
    h3_resolution: int = Field(default=5, ge=0, le=15)
    bounds: Optional[GeoBoundingBoxDTO] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    time_range_start: Optional[datetime.datetime] = None
    time_range_end: Optional[datetime.datetime] = None
    time_bucket: Optional[TimeBucketInterval] = None
    historical_as_of: Optional[datetime.datetime] = None
    min_contributors: int = Field(default=5, ge=1)
    result_limit: int = Field(default=5000, le=10000)


class AtlasH3AggregateDTO(BaseModel):
    h3_cell_id: str
    h3_resolution: int
    metric_id: str
    aggregation_method: str
    value: Optional[float]
    record_count: int
    non_null_count: int
    distinct_count: Optional[int] = None
    valid_weight_sum: Optional[float] = None
    cell_area_km2: float
    density: Optional[float] = None
    unit: str
    is_suppressed: bool
    time_bucket: Optional[str] = None
    data_quality: str


class SpatialSummaryStatisticsDTO(BaseModel):
    total_records: int
    total_cells: int
    suppressed_cells: int
    sum_value: float
    mean_value: float
    min_value: float
    max_value: float
    weighted_mean: Optional[float] = None
    unit: str


class SpatialAnalyticsResultDTO(BaseModel):
    query_id: str
    dataset_id: str
    dataset_version: str
    metric_id: str
    aggregation: str
    visualization_type: str
    h3_resolution: int
    unit: str
    aggregates: List[AtlasH3AggregateDTO]
    summary: SpatialSummaryStatisticsDTO
    bounds: Optional[List[float]] = None
    time_scope: Optional[Dict[str, Any]] = None
    data_quality: str
    source_attribution: str
    licensing_policy: str
    is_truncated: bool
    execution_time_ms: float
    computed_at: str


class RegionComparisonRequest(BaseModel):
    dataset_id: str
    metric_id: str
    aggregation: SpatialAggregationMethod = SpatialAggregationMethod.MEAN
    region_a_name: str
    region_a_bounds: GeoBoundingBoxDTO
    region_b_name: str
    region_b_bounds: GeoBoundingBoxDTO
    h3_resolution: int = Field(default=6, ge=0, le=15)


class RegionComparisonResponse(BaseModel):
    region_a_name: str
    region_b_name: str
    metric_id: str
    unit: str
    region_a_summary: SpatialSummaryStatisticsDTO
    region_b_summary: SpatialSummaryStatisticsDTO
    absolute_difference: float
    relative_difference_pct: Optional[float] = None
    higher_region: Optional[str] = None
    area_normalized_a: float
    area_normalized_b: float


class CellDetailsResponse(BaseModel):
    h3_cell_id: str
    resolution: int
    cell_area_km2: float
    centroid: Dict[str, float]
    is_pentagon: bool
    supported_drill_down: bool


class CreateMaterializationJobRequest(BaseModel):
    dataset_id: str
    metric_id: str
    h3_resolution: int = Field(default=6, ge=0, le=15)


class MaterializationJobDTO(BaseModel):
    job_id: str
    dataset_id: str
    dataset_revision: str
    metric_id: str
    h3_resolution: int
    status: str
    records_processed: int
    total_records: int
    cells_generated: int
    error_message: Optional[str] = None
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
