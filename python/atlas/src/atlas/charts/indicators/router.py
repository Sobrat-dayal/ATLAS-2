"""FastAPI router for Technical Indicator Infrastructure (Stage 69).

Provides:
- GET /charts/indicators/catalog: Catalog of registered, approved indicator definitions
- POST /charts/indicators/calculate: Authenticated calculation of active indicator instances
- GET /charts/indicators/{indicator_id}: Specific indicator definition details
"""

import logging

from fastapi import APIRouter, HTTPException, Query, status

from .models import (
    IndicatorCalculationRequest,
    IndicatorCalculationResponse,
    IndicatorCatalogResponse,
    IndicatorDefinition,
)
from .service import TechnicalIndicatorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/indicators", tags=["charts-indicators"])
_indicator_service = TechnicalIndicatorService()


@router.get(
    "/catalog",
    response_model=IndicatorCatalogResponse,
    summary="Get registered technical indicator catalog",
    description="Returns all server-approved, registered technical indicator definitions.",
)
async def get_indicator_catalog() -> IndicatorCatalogResponse:
    """Return list of all registered indicator definitions."""
    return _indicator_service.get_catalog()


@router.get(
    "/{indicator_id}",
    response_model=IndicatorDefinition,
    summary="Get indicator definition by ID",
    description="Retrieves the metadata definition and parameter schema for an indicator ID.",
)
async def get_indicator_definition(
    indicator_id: str,
    version: int = Query(1, ge=1, description="Indicator definition schema version"),
) -> IndicatorDefinition:
    """Retrieve specific indicator definition."""
    try:
        defn, _ = _indicator_service.registry.get(indicator_id, version)
        return defn
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/calculate",
    response_model=IndicatorCalculationResponse,
    summary="Calculate technical indicator instances",
    description=(
        "Executes deterministic mathematical calculation for requested indicator instances "
        "using canonical historical market bars with lookback warmup."
    ),
)
async def calculate_indicators(
    request: IndicatorCalculationRequest,
) -> IndicatorCalculationResponse:
    """Calculate indicator series over canonical historical data."""
    try:
        return _indicator_service.calculate_indicators(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error in calculate_indicators: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate technical indicators.",
        )
