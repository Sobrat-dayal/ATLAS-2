"""FastAPI Router for Institutional Economics V1 (Stage 89).

Endpoints:
- GET /api/v1/economics/overview
- GET /api/v1/economics/categories
- GET /api/v1/economics/indicators
- GET /api/v1/economics/indicators/{indicator_id}
- GET /api/v1/economics/series
- GET /api/v1/economics/series/{series_id}
- GET /api/v1/economics/series/{series_id}/observations
- GET /api/v1/economics/series/{series_id}/vintages
- GET /api/v1/economics/geographies
- GET /api/v1/economics/coverage
- GET /api/v1/economics/transformations
"""

import logging
from datetime import date
from typing import List, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization.permissions import PermissionCode
from atlas.economics.v1 import (
    EconomicCalculationError,
    EconomicCoverageResponseDTO,
    EconomicGeographyDTO,
    EconomicIndicatorDTO,
    EconomicIndicatorNotFoundError,
    EconomicPeriodInvalidError,
    EconomicSeriesDTO,
    EconomicSeriesNotFoundError,
    EconomicSeriesObservationsResponseDTO,
    EconomicsV1Service,
    EconomicTransformationUnsupportedError,
    EconomicVintageDTO,
    GlobalMacroOverviewResponseDTO,
    TransformationDefinitionDTO,
    TransformationType,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/economics",
    tags=["Economics V1"],
)

_service: Optional[EconomicsV1Service] = None


def get_economics_service() -> EconomicsV1Service:
    global _service
    if _service is None:
        _service = EconomicsV1Service()
    return _service


@router.get(
    "/overview",
    response_model=GlobalMacroOverviewResponseDTO,
    summary="Get Global Macroeconomic Snapshot",
    description="Returns cross-economy macro snapshot with GDP growth, CPI inflation, unemployment, and policy interest rates.",
)
async def get_overview(
    geography_ids: Optional[List[str]] = Query(None, description="Optional list of geography IDs to filter"),
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> GlobalMacroOverviewResponseDTO:
    try:
        return service.get_overview(geography_ids=geography_ids)
    except Exception as exc:
        logger.exception("Error loading global macro overview")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get Macroeconomic Categories",
    description="Returns list of macroeconomic classification taxonomy categories.",
)
async def get_categories(
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[str]:
    return service.get_categories()


@router.get(
    "/indicators",
    response_model=List[EconomicIndicatorDTO],
    summary="List Canonical Economic Indicators",
    description="Discovers conceptual economic indicators with optional category filtering and search query.",
)
async def get_indicators(
    category: Optional[str] = Query(None, description="Optional category filter"),
    search: Optional[str] = Query(None, description="Search query across code, name, and description"),
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[EconomicIndicatorDTO]:
    return service.get_indicators(category=category, search=search)


@router.get(
    "/indicators/{indicator_id}",
    response_model=EconomicIndicatorDTO,
    summary="Get Economic Indicator Details",
    description="Returns metadata specification for a single canonical economic indicator.",
)
async def get_indicator_detail(
    indicator_id: str,
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EconomicIndicatorDTO:
    try:
        return service.get_indicator_detail(indicator_id)
    except EconomicIndicatorNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get(
    "/series",
    response_model=List[EconomicSeriesDTO],
    summary="List Economic Series",
    description="Discovers official statistical time-series with geography and indicator filters.",
)
async def get_series(
    indicator_id: Optional[str] = Query(None, description="Filter by canonical indicator ID"),
    geography_id: Optional[str] = Query(None, description="Filter by geography ID"),
    category: Optional[str] = Query(None, description="Filter by indicator category"),
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[EconomicSeriesDTO]:
    return service.get_series(
        indicator_id=indicator_id,
        geography_id=geography_id,
        category=category,
    )


@router.get(
    "/series/{series_id}",
    response_model=EconomicSeriesDTO,
    summary="Get Economic Series Details",
    description="Returns metadata, official provider citation, frequency, and coverage for a series.",
)
async def get_series_detail(
    series_id: str,
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EconomicSeriesDTO:
    try:
        return service.get_series_detail(series_id)
    except EconomicSeriesNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get(
    "/series/{series_id}/observations",
    response_model=EconomicSeriesObservationsResponseDTO,
    summary="Get Historical Economic Observations",
    description="Fetches time-series observations with optional on-the-fly statistical transformations and point-in-time publication filtering.",
)
async def get_observations(
    series_id: str,
    start_period: Optional[str] = Query(None, description="Start period (e.g. 2023-01 or 2023-Q1)"),
    end_period: Optional[str] = Query(None, description="End period (e.g. 2024-09 or 2024-Q3)"),
    transformation: TransformationType = Query(
        TransformationType.SOURCE_REPORTED,
        description="Statistical transformation (SOURCE_REPORTED, YEAR_OVER_YEAR, MONTH_OVER_MONTH, QUARTER_OVER_QUARTER, ANNUALIZED_QUARTERLY_GROWTH, etc.)",
    ),
    as_of_date: Optional[date] = Query(
        None, description="Point-in-time date constraint (excludes data published after this date)"
    ),
    limit: int = Query(100, ge=1, le=500, description="Observations page size"),
    page: int = Query(1, ge=1, description="Page number"),
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EconomicSeriesObservationsResponseDTO:
    try:
        return service.get_observations(
            series_id=series_id,
            start_period=start_period,
            end_period=end_period,
            transformation=transformation,
            as_of_date=as_of_date,
            limit=limit,
            page=page,
        )
    except EconomicSeriesNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except EconomicTransformationUnsupportedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except (EconomicPeriodInvalidError, EconomicCalculationError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc


@router.get(
    "/series/{series_id}/vintages",
    response_model=List[EconomicVintageDTO],
    summary="Get Historical Data Vintages",
    description="Returns point-in-time publication and revision vintages for a statistical series.",
)
async def get_vintages(
    series_id: str,
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[EconomicVintageDTO]:
    try:
        return service.get_vintages(series_id)
    except EconomicSeriesNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get(
    "/geographies",
    response_model=List[EconomicGeographyDTO],
    summary="List Supported Economic Geographies",
    description="Returns covered sovereign states and regional economic areas.",
)
async def get_geographies(
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[EconomicGeographyDTO]:
    return service.get_geographies()


@router.get(
    "/coverage",
    response_model=EconomicCoverageResponseDTO,
    summary="Get Economic Data Coverage",
    description="Returns active official statistical providers, jurisdiction bounds, and documented data limitations.",
)
async def get_coverage(
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EconomicCoverageResponseDTO:
    return service.get_coverage()


@router.get(
    "/transformations",
    response_model=List[TransformationDefinitionDTO],
    summary="List Supported Statistical Transformations",
    description="Returns mathematical descriptions and frequency compatibilities for all registered transformation algorithms.",
)
async def get_transformations(
    service: EconomicsV1Service = Depends(get_economics_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[TransformationDefinitionDTO]:
    return service.get_transformations()
