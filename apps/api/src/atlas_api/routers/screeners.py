"""FastAPI Router for Financial Screeners V1 (Stage 94)."""

from typing import Any, Dict, List, Optional

from atlas.screeners import (
    CountryOptionDTO,
    ExchangeOptionDTO,
    FilterCriterionDTO,
    ScreenerColumnDefinition,
    ScreenerCoverageResponseDTO,
    ScreenerError,
    ScreenerFilterDefinition,
    ScreenerRunRequestDTO,
    ScreenerRunResponseDTO,
    ScreenerService,
    ScreenerUniverseDefinition,
    SectorOptionDTO,
    ValidationResponseDTO,
)
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/screeners", tags=["Screeners"])

# Singleton service instance
_screener_service = ScreenerService()


def get_screener_service() -> ScreenerService:
    """Dependency provider for ScreenerService."""
    return _screener_service


@router.get(
    "/universes",
    response_model=List[ScreenerUniverseDefinition],
    summary="List available canonical security universes",
)
def list_universes(
    service: ScreenerService = Depends(get_screener_service),
) -> List[ScreenerUniverseDefinition]:
    """Retrieves all registered canonical financial screening universes."""
    return service.get_universes()


@router.get(
    "/filters",
    response_model=List[ScreenerFilterDefinition],
    summary="List approved filter registry definitions",
)
def list_filters(
    service: ScreenerService = Depends(get_screener_service),
) -> List[ScreenerFilterDefinition]:
    """Retrieves all approved filter criteria with value types, operators, and units."""
    return service.get_filters()


@router.get(
    "/factors",
    response_model=List[ScreenerFilterDefinition],
    summary="List approved factor and filter definitions",
)
def list_factors(
    category: Optional[str] = None,
    service: ScreenerService = Depends(get_screener_service),
) -> List[ScreenerFilterDefinition]:
    """Retrieves all approved fundamental and technical factors, optionally filtered by category."""
    return service.get_factors(category=category)


@router.get(
    "/factors/{factor_id}",
    response_model=ScreenerFilterDefinition,
    summary="Inspect factor methodology and definition",
)
def get_factor(
    factor_id: str,
    service: ScreenerService = Depends(get_screener_service),
) -> ScreenerFilterDefinition:
    """Retrieves full methodology, formula reference, allowed operators, and parameters for a specific factor."""
    factor = service.get_filter(factor_id)
    if not factor:
        raise HTTPException(
            status_code=404,
            detail={"code": "FACTOR_NOT_FOUND", "message": f"Factor '{factor_id}' is not in the canonical registry."},
        )
    return factor


@router.get(
    "/factors/{factor_id}/parameters",
    summary="Get allowed and default parameters for a factor",
)
def get_factor_parameters(
    factor_id: str,
    service: ScreenerService = Depends(get_screener_service),
) -> Dict[str, Any]:
    """Retrieves allowed parameter bounds, defaults, and components for technical and parameterized factors."""
    factor = service.get_filter(factor_id)
    if not factor:
        raise HTTPException(
            status_code=404,
            detail={"code": "FACTOR_NOT_FOUND", "message": f"Factor '{factor_id}' is not in the canonical registry."},
        )
    return {
        "factor_id": factor.filter_id,
        "indicator_type": factor.indicator_type,
        "default_parameters": factor.default_parameters,
        "allowed_parameters": factor.allowed_parameters,
        "minimum_lookback": factor.minimum_lookback,
        "output_components": factor.output_components,
        "calculation_version": factor.calculation_version,
    }


class FactorValidationRequestDTO(BaseModel):
    filters: List[FilterCriterionDTO]
    universe_id: str = "all_us_equities"


@router.post(
    "/factors/validate",
    response_model=ValidationResponseDTO,
    summary="Validate factor conditions and parameter bounds",
)
def validate_factors(
    request: FactorValidationRequestDTO,
    service: ScreenerService = Depends(get_screener_service),
) -> ValidationResponseDTO:
    """Validates factor predicates and parameter bounds without executing the full screen."""
    run_req = ScreenerRunRequestDTO(
        universe_id=request.universe_id,
        filters=request.filters,
        limit=1,
    )
    return service.validate_query(run_req)


@router.get(
    "/columns",
    response_model=List[ScreenerColumnDefinition],
    summary="List available result column specifications",
)
def list_columns(
    service: ScreenerService = Depends(get_screener_service),
) -> List[ScreenerColumnDefinition]:
    """Retrieves all available columns for institutional screener data tables."""
    return service.get_columns()


@router.get(
    "/exchanges",
    response_model=List[ExchangeOptionDTO],
    summary="List supported exchanges and venue options",
)
def list_exchanges(
    service: ScreenerService = Depends(get_screener_service),
) -> List[ExchangeOptionDTO]:
    """Retrieves supported exchange venues with canonical security listing counts."""
    return service.get_exchanges()


@router.get(
    "/geographies",
    response_model=List[CountryOptionDTO],
    summary="List supported country and geographic filter options",
)
def list_geographies(
    service: ScreenerService = Depends(get_screener_service),
) -> List[CountryOptionDTO]:
    """Retrieves supported listing countries with active equity counts."""
    return service.get_geographies()


@router.get(
    "/industries",
    response_model=List[SectorOptionDTO],
    summary="List supported sector and industry hierarchies",
)
def list_industries(
    service: ScreenerService = Depends(get_screener_service),
) -> List[SectorOptionDTO]:
    """Retrieves canonical classification sectors and child industry groups."""
    return service.get_industries()


@router.post(
    "/validate",
    response_model=ValidationResponseDTO,
    summary="Validate candidate screener query",
)
def validate_query(
    request: ScreenerRunRequestDTO,
    service: ScreenerService = Depends(get_screener_service),
) -> ValidationResponseDTO:
    """Pre-validates filter predicates, operator compatibility, and complexity limits."""
    try:
        return service.validate_query(request)
    except ScreenerError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message},
        )


@router.post(
    "/run",
    response_model=ScreenerRunResponseDTO,
    summary="Execute bounded financial security screen",
)
def run_screener(
    request: ScreenerRunRequestDTO,
    service: ScreenerService = Depends(get_screener_service),
) -> ScreenerRunResponseDTO:
    """Executes server-side screening with universe reduction, filtering, sorting, and pagination."""
    try:
        return service.run_screen(request)
    except ScreenerError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"code": e.code, "message": e.message},
        )


@router.get(
    "/coverage",
    response_model=ScreenerCoverageResponseDTO,
    summary="Data coverage and freshness status audit",
)
def get_coverage(
    service: ScreenerService = Depends(get_screener_service),
) -> ScreenerCoverageResponseDTO:
    """Retrieves factual data coverage and quote freshness breakdown."""
    return service.get_coverage()
