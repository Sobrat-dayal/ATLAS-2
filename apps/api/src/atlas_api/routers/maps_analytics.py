"""FastAPI Router for ATLAS Spatial Analytics and H3 Engine (Stage 131).

Provides endpoints for analytical capabilities, metric discovery, H3 aggregations,
density maps, regional comparisons, cell inspections, and materialization jobs.
"""

from __future__ import annotations

import logging
from typing import Optional

from atlas.maps.analytics.domain import (
    GeoBoundingBox,
    SpatialAggregationMethod,
    SpatialAnalyticsQuery,
    SpatialVisualizationType,
)
from atlas.maps.analytics.errors import (
    ExcessiveH3ResolutionError,
    InvalidH3CellError,
    InvalidH3ResolutionError,
    MaterializationJobNotFoundError,
    PrivacySuppressionError,
    SourceEntitlementRevokedError,
    SpatialAnalyticsDomainError,
    SpatialMetricNotAllowedError,
    SpatialQueryTimeoutError,
    UnauthorizedSpatialDatasetError,
)
from atlas.maps.analytics.schemas import (
    CellDetailsResponse,
    CreateMaterializationJobRequest,
    MaterializationJobDTO,
    RegionComparisonRequest,
    RegionComparisonResponse,
    SpatialAnalyticsQueryRequest,
    SpatialAnalyticsResultDTO,
)
from atlas.maps.analytics.service import AtlasSpatialAnalyticsService
from fastapi import APIRouter, HTTPException, Query, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Maps Spatial Analytics"])

# Singleton service instance
_analytics_service: Optional[AtlasSpatialAnalyticsService] = None


def get_analytics_service() -> AtlasSpatialAnalyticsService:
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AtlasSpatialAnalyticsService()
    return _analytics_service


def handle_domain_error(exc: SpatialAnalyticsDomainError) -> None:
    """Translates typed domain errors to compliant HTTP exceptions."""
    if isinstance(
        exc,
        (
            InvalidH3CellError,
            InvalidH3ResolutionError,
            ExcessiveH3ResolutionError,
            SpatialMetricNotAllowedError,
        ),
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
        )
    if isinstance(exc, (UnauthorizedSpatialDatasetError, SourceEntitlementRevokedError)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
        )
    if isinstance(exc, PrivacySuppressionError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
        )
    if isinstance(exc, MaterializationJobNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
        )
    if isinstance(exc, SpatialQueryTimeoutError):
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={"error_code": exc.error_code, "message": exc.message, "details": exc.details},
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"error_code": exc.error_code, "message": exc.message},
    )


@router.get("/capabilities")
async def get_analytics_capabilities():
    """Returns supported spatial analytics visualization modes, aggregations, and H3 limits."""
    service = get_analytics_service()
    return service.get_capabilities()


@router.get("/metrics")
async def list_analytics_metrics(dataset_id: str = Query(..., description="Target dataset ID")):
    """Returns approved analytical metrics for the specified dataset."""
    service = get_analytics_service()
    metrics = service.list_metrics(dataset_id)
    return [
        {
            "metric_id": m.metric_id,
            "dataset_id": m.dataset_id,
            "display_name": m.display_name,
            "description": m.description,
            "unit": m.unit,
            "value_type": m.value_type,
            "allowed_aggregations": [a.value for a in m.allowed_aggregations],
            "default_aggregation": m.default_aggregation.value,
            "currency": m.currency,
            "null_policy": m.null_policy.value,
            "minimum_contributor_threshold": m.minimum_contributor_threshold,
            "is_temporal": m.is_temporal,
        }
        for m in metrics
    ]


@router.post("/query", response_model=SpatialAnalyticsResultDTO)
async def query_spatial_analytics(payload: SpatialAnalyticsQueryRequest):
    """Executes a validated spatial analytics query, producing H3 aggregates or point summaries."""
    service = get_analytics_service()

    bounds: Optional[GeoBoundingBox] = None
    if payload.bounds:
        bounds = GeoBoundingBox(
            west=payload.bounds.west,
            south=payload.bounds.south,
            east=payload.bounds.east,
            north=payload.bounds.north,
        )

    query = SpatialAnalyticsQuery(
        dataset_id=payload.dataset_id,
        metric_id=payload.metric_id,
        aggregation=payload.aggregation,
        visualization_type=payload.visualization_type,
        h3_resolution=payload.h3_resolution,
        bounds=bounds,
        filters=payload.filters,
        time_range_start=payload.time_range_start,
        time_range_end=payload.time_range_end,
        time_bucket=payload.time_bucket,
        historical_as_of=payload.historical_as_of,
        min_contributors=payload.min_contributors,
        result_limit=payload.result_limit,
    )

    try:
        result = service.query_analytics(query)
        return result.to_dict()
    except SpatialAnalyticsDomainError as exc:
        handle_domain_error(exc)


@router.post("/h3", response_model=SpatialAnalyticsResultDTO)
async def query_h3_aggregates(payload: SpatialAnalyticsQueryRequest):
    """Specialized endpoint for H3 hexagonal binning."""
    payload.visualization_type = SpatialVisualizationType.H3_HEXAGON
    return await query_spatial_analytics(payload)


@router.post("/density", response_model=SpatialAnalyticsResultDTO)
async def query_density_aggregates(payload: SpatialAnalyticsQueryRequest):
    """Specialized endpoint for area-normalized density analysis."""
    payload.aggregation = SpatialAggregationMethod.DENSITY
    return await query_spatial_analytics(payload)


@router.post("/compare", response_model=RegionComparisonResponse)
async def compare_geographic_regions(payload: RegionComparisonRequest):
    """Compares spatial analytical statistics across two geographic regions."""
    service = get_analytics_service()

    bounds_a = GeoBoundingBox(
        west=payload.region_a_bounds.west,
        south=payload.region_a_bounds.south,
        east=payload.region_a_bounds.east,
        north=payload.region_a_bounds.north,
    )
    bounds_b = GeoBoundingBox(
        west=payload.region_b_bounds.west,
        south=payload.region_b_bounds.south,
        east=payload.region_b_bounds.east,
        north=payload.region_b_bounds.north,
    )

    try:
        cmp = service.compare_regions(
            dataset_id=payload.dataset_id,
            metric_id=payload.metric_id,
            aggregation=payload.aggregation,
            region_a_name=payload.region_a_name,
            region_a_bounds=bounds_a,
            region_b_name=payload.region_b_name,
            region_b_bounds=bounds_b,
            h3_resolution=payload.h3_resolution,
        )
        return {
            "region_a_name": cmp.region_a_name,
            "region_b_name": cmp.region_b_name,
            "metric_id": cmp.metric_id,
            "unit": cmp.unit,
            "region_a_summary": {
                "total_records": cmp.region_a_summary.total_records,
                "total_cells": cmp.region_a_summary.total_cells,
                "suppressed_cells": cmp.region_a_summary.suppressed_cells,
                "sum_value": cmp.region_a_summary.sum_value,
                "mean_value": cmp.region_a_summary.mean_value,
                "min_value": cmp.region_a_summary.min_value,
                "max_value": cmp.region_a_summary.max_value,
                "weighted_mean": cmp.region_a_summary.weighted_mean,
                "unit": cmp.region_a_summary.unit,
            },
            "region_b_summary": {
                "total_records": cmp.region_b_summary.total_records,
                "total_cells": cmp.region_b_summary.total_cells,
                "suppressed_cells": cmp.region_b_summary.suppressed_cells,
                "sum_value": cmp.region_b_summary.sum_value,
                "mean_value": cmp.region_b_summary.mean_value,
                "min_value": cmp.region_b_summary.min_value,
                "max_value": cmp.region_b_summary.max_value,
                "weighted_mean": cmp.region_b_summary.weighted_mean,
                "unit": cmp.region_b_summary.unit,
            },
            "absolute_difference": cmp.absolute_difference,
            "relative_difference_pct": cmp.relative_difference_pct,
            "higher_region": cmp.higher_region,
            "area_normalized_a": cmp.area_normalized_a,
            "area_normalized_b": cmp.area_normalized_b,
        }
    except SpatialAnalyticsDomainError as exc:
        handle_domain_error(exc)


@router.get("/cells/{cell_id}", response_model=CellDetailsResponse)
async def get_cell_details(cell_id: str):
    """Retrieves geometry, surface area, and resolution metadata for a single H3 cell."""
    service = get_analytics_service()
    try:
        return service.get_cell_details(cell_id)
    except SpatialAnalyticsDomainError as exc:
        handle_domain_error(exc)


@router.post("/jobs", response_model=MaterializationJobDTO)
async def create_materialization_job(payload: CreateMaterializationJobRequest):
    """Initiates a background preaggregation job for high-volume datasets."""
    service = get_analytics_service()
    job = service.create_materialization_job(
        dataset_id=payload.dataset_id,
        metric_id=payload.metric_id,
        h3_resolution=payload.h3_resolution,
    )
    return {
        "job_id": job.job_id,
        "dataset_id": job.dataset_id,
        "dataset_revision": job.dataset_revision,
        "metric_id": job.metric_id,
        "h3_resolution": job.h3_resolution,
        "status": job.status.value,
        "records_processed": job.records_processed,
        "total_records": job.total_records,
        "cells_generated": job.cells_generated,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
    }


@router.get("/jobs/{job_id}", response_model=MaterializationJobDTO)
async def get_materialization_job(job_id: str):
    """Retrieves status and progress for a materialization job."""
    service = get_analytics_service()
    try:
        job = service.get_job(job_id)
        return {
            "job_id": job.job_id,
            "dataset_id": job.dataset_id,
            "dataset_revision": job.dataset_revision,
            "metric_id": job.metric_id,
            "h3_resolution": job.h3_resolution,
            "status": job.status.value,
            "records_processed": job.records_processed,
            "total_records": job.total_records,
            "cells_generated": job.cells_generated,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
        }
    except SpatialAnalyticsDomainError as exc:
        handle_domain_error(exc)


@router.post("/jobs/{job_id}/cancel", response_model=MaterializationJobDTO)
async def cancel_materialization_job(job_id: str):
    """Cancels a pending or running materialization job."""
    service = get_analytics_service()
    try:
        job = service.cancel_job(job_id)
        return {
            "job_id": job.job_id,
            "dataset_id": job.dataset_id,
            "dataset_revision": job.dataset_revision,
            "metric_id": job.metric_id,
            "h3_resolution": job.h3_resolution,
            "status": job.status.value,
            "records_processed": job.records_processed,
            "total_records": job.total_records,
            "cells_generated": job.cells_generated,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
        }
    except SpatialAnalyticsDomainError as exc:
        handle_domain_error(exc)
