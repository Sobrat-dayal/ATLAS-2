"""FastAPI Router for Financial Screeners V1 (Stage 94)."""

from typing import List

from atlas.screeners import (
    CountryOptionDTO,
    ExchangeOptionDTO,
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
