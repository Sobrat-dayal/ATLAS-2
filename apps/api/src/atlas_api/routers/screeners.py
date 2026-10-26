"""FastAPI Router for Financial Screeners V1 (Stage 94)."""

import uuid
from typing import Annotated, Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.screeners import (
    CountryOptionDTO,
    ExchangeOptionDTO,
    FactorRankingEngine,
    FilterCriterionDTO,
    SavedScreenerCreateRequestDTO,
    SavedScreenerDTO,
    SavedScreenerListResponseDTO,
    SavedScreenerUpdateRequestDTO,
    ScreenerColumnDefinition,
    ScreenerCoverageResponseDTO,
    ScreenerError,
    ScreenerExportJobDTO,
    ScreenerExportListResponseDTO,
    ScreenerExportRequestDTO,
    ScreenerFilterDefinition,
    ScreenerRankingResponseDTO,
    ScreenerRankingSpecDTO,
    ScreenerRunRequestDTO,
    ScreenerRunResponseDTO,
    ScreenerService,
    ScreenerUniverseDefinition,
    SectorOptionDTO,
    ValidationResponseDTO,
    export_job_manager,
    saved_screener_repository,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel

from atlas_api.auth.dependencies import get_current_user

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


# =============================================================================
# Stage 97: Saved Screeners Endpoints
# =============================================================================


@router.get(
    "/saved",
    response_model=SavedScreenerListResponseDTO,
    summary="List authenticated user's saved screeners",
)
def list_saved_screeners(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    search: Optional[str] = Query(None, description="Search by name or description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> SavedScreenerListResponseDTO:
    """Retrieves paginated user-owned saved screeners with tenant isolation."""
    user_id = uuid.UUID(principal.user_id)
    return saved_screener_repository.list(user_id, search=search, page=page, page_size=page_size)


@router.post(
    "/saved",
    response_model=SavedScreenerDTO,
    summary="Create a new user-owned saved screener",
)
def create_saved_screener(
    request: SavedScreenerCreateRequestDTO,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> SavedScreenerDTO:
    """Persists a new user-owned screener query strategy with optimistic concurrency revision."""
    user_id = uuid.UUID(principal.user_id)
    try:
        return saved_screener_repository.create(user_id, request)
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.get(
    "/saved/{saved_screen_id}",
    response_model=SavedScreenerDTO,
    summary="Read a private saved screener",
)
def get_saved_screener(
    saved_screen_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> SavedScreenerDTO:
    """Reads a private saved screener, enforcing owner-only RLS authorization."""
    user_id = uuid.UUID(principal.user_id)
    try:
        return saved_screener_repository.get(user_id, saved_screen_id)
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.patch(
    "/saved/{saved_screen_id}",
    response_model=SavedScreenerDTO,
    summary="Update saved screener configuration with revision check",
)
def update_saved_screener(
    saved_screen_id: uuid.UUID,
    request: SavedScreenerUpdateRequestDTO,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> SavedScreenerDTO:
    """Updates saved screen configuration with optimistic concurrency protection."""
    user_id = uuid.UUID(principal.user_id)
    try:
        return saved_screener_repository.update(user_id, saved_screen_id, request)
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.delete(
    "/saved/{saved_screen_id}",
    summary="Delete a user-owned saved screener",
)
def delete_saved_screener(
    saved_screen_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Deletes a user-owned saved screen."""
    user_id = uuid.UUID(principal.user_id)
    try:
        saved_screener_repository.delete(user_id, saved_screen_id)
        return {"status": "DELETED", "saved_screen_id": str(saved_screen_id)}
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post(
    "/saved/{saved_screen_id}/duplicate",
    response_model=SavedScreenerDTO,
    summary="Duplicate a saved screener strategy",
)
def duplicate_saved_screener(
    saved_screen_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    new_name: Optional[str] = Query(None),
) -> SavedScreenerDTO:
    """Clones a saved screener into a new user-owned screener entity."""
    user_id = uuid.UUID(principal.user_id)
    try:
        return saved_screener_repository.duplicate(user_id, saved_screen_id, new_name=new_name)
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post(
    "/saved/{saved_screen_id}/run",
    response_model=ScreenerRunResponseDTO,
    summary="Execute saved screen query against current market data",
)
def run_saved_screener(
    saved_screen_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: ScreenerService = Depends(get_screener_service),
) -> ScreenerRunResponseDTO:
    """Reruns saved query strategy against authoritative current market data."""
    user_id = uuid.UUID(principal.user_id)
    try:
        screen = saved_screener_repository.get(user_id, saved_screen_id)
        run_req = ScreenerRunRequestDTO(
            universe=screen.universe,
            filters=screen.filters,
            columns=screen.columns,
            sort=screen.sort,
            ranking=screen.ranking,
            page=page,
            page_size=page_size,
            period_policy=screen.period_policy,
            currency_policy=screen.currency_policy,
        )
        res = service.run_screen(run_req)
        saved_screener_repository.mark_executed(user_id, saved_screen_id)
        return res
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


# =============================================================================
# Stage 97: Factor Ranking Endpoints
# =============================================================================


class RankingEvaluationRequestDTO(BaseModel):
    query: ScreenerRunRequestDTO
    ranking: ScreenerRankingSpecDTO


@router.post(
    "/ranking/evaluate",
    response_model=ScreenerRankingResponseDTO,
    summary="Evaluate quantitative factor ranking over screener results",
)
def evaluate_ranking(
    request: RankingEvaluationRequestDTO,
    service: ScreenerService = Depends(get_screener_service),
) -> ScreenerRankingResponseDTO:
    """Calculates cross-sectional percentiles, Z-scores, and weighted composite factor rankings."""
    try:
        run_res = service.run_screen(request.query)
        cand_dicts = [
            {
                "instrument_entity_id": row.instrument_entity_id,
                "ticker": row.ticker,
                "canonical_security_name": row.canonical_security_name,
                "row": row,
            }
            for row in run_res.rows
        ]

        def extractor(cand: Dict[str, Any], factor_id: str) -> Optional[float]:
            row = cand["row"]
            cell = row.metrics.get(factor_id)
            if cell and cell.status == "AVAILABLE" and cell.raw_value is not None:
                try:
                    return float(cell.raw_value)
                except (ValueError, TypeError):
                    return None
            return None

        return FactorRankingEngine.evaluate(cand_dicts, request.ranking, extractor)
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


# =============================================================================
# Stage 97: Export Endpoints
# =============================================================================


@router.post(
    "/exports",
    response_model=ScreenerExportJobDTO,
    summary="Create authorized financial export job",
)
def create_export(
    request: ScreenerExportRequestDTO,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: ScreenerService = Depends(get_screener_service),
) -> ScreenerExportJobDTO:
    """Generates an institutional CSV or XLSX dataset export."""
    user_id = uuid.UUID(principal.user_id)
    try:
        job = export_job_manager.create_job(user_id, request)

        export_query = request.query.model_copy()
        if request.scope.value == "all_matching_results":
            export_query.page = 1
            export_query.page_size = 1000

        run_res = service.run_screen(export_query)
        columns = request.selected_columns or [
            "ticker", "canonical_security_name", "last_price", "market_cap", "pe_ratio", "volume_24h"
        ]
        if export_query.ranking and "rank" not in columns:
            columns = ["rank"] + columns

        completed_job = export_job_manager.execute_job_synchronously(job.export_job_id, run_res, columns)
        return completed_job
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.get(
    "/exports",
    response_model=ScreenerExportListResponseDTO,
    summary="List current user's export jobs",
)
def list_exports(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ScreenerExportListResponseDTO:
    """Lists export jobs belonging to the authenticated user."""
    user_id = uuid.UUID(principal.user_id)
    jobs = export_job_manager.list_jobs(user_id)
    return ScreenerExportListResponseDTO(total=len(jobs), items=jobs)


@router.get(
    "/exports/{export_id}",
    response_model=ScreenerExportJobDTO,
    summary="Get export job status",
)
def get_export_status(
    export_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ScreenerExportJobDTO:
    """Checks the status and metadata of an export job."""
    user_id = uuid.UUID(principal.user_id)
    try:
        return export_job_manager.get_job(user_id, export_id)
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post(
    "/exports/{export_id}/cancel",
    response_model=ScreenerExportJobDTO,
    summary="Cancel a pending or running export job",
)
def cancel_export(
    export_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ScreenerExportJobDTO:
    """Cancels a pending or running export job."""
    user_id = uuid.UUID(principal.user_id)
    try:
        return export_job_manager.cancel_job(user_id, export_id)
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.get(
    "/exports/{export_id}/download",
    summary="Authorized download of generated export artifact",
)
def download_export(
    export_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Response:
    """Streams authorized, time-limited CSV or XLSX export file."""
    user_id = uuid.UUID(principal.user_id)
    try:
        content, media_type, filename = export_job_manager.get_file_content(user_id, export_id)
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.delete(
    "/exports/{export_id}",
    summary="Delete an export artifact and job",
)
def delete_export(
    export_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Deletes an export artifact and job record."""
    user_id = uuid.UUID(principal.user_id)
    try:
        export_job_manager.delete_job(user_id, export_id)
        return {"status": "DELETED", "export_id": str(export_id)}
    except ScreenerError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})

