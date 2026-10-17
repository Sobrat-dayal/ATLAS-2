"""FastAPI router for ATLAS Market Heatmaps V1 (Stage 64)."""

import logging
from typing import Annotated, Optional

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from fastapi import APIRouter, Depends, HTTPException, Query, Response

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode

from .config import (
    SUPPORTED_HEATMAP_UNIVERSES,
    HeatmapComparisonWindow,
    HeatmapHierarchyMode,
    HeatmapVisualizationMode,
)
from .models import (
    HeatmapOptionsResponse,
    HeatmapUniverseResponse,
    MarketHeatmapResponse,
)
from .repository import MarketHeatmapRepository
from .service import MarketHeatmapService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/heatmaps", tags=["Markets Heatmaps"])


def get_market_heatmaps_service() -> MarketHeatmapService:
    """Dependency provider for MarketHeatmapService."""
    repository = MarketHeatmapRepository()
    return MarketHeatmapService(repository=repository)


@router.get(
    "/universes",
    response_model=HeatmapUniverseResponse,
    summary="List available, authorized heatmap universes",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_heatmap_universes(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> HeatmapUniverseResponse:
    """Returns all supported canonical heatmap candidate universes."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return HeatmapUniverseResponse(
        universes=SUPPORTED_HEATMAP_UNIVERSES,
        count=len(SUPPORTED_HEATMAP_UNIVERSES),
    )


@router.get(
    "/options",
    response_model=HeatmapOptionsResponse,
    summary="List supported visualization modes, hierarchies, and comparison windows",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_heatmap_options(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
) -> HeatmapOptionsResponse:
    """Returns supported modes, hierarchies, and taxonomy metadata."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return HeatmapOptionsResponse(
        modes=list(HeatmapVisualizationMode),
        hierarchies=list(HeatmapHierarchyMode),
        windows=list(HeatmapComparisonWindow),
        taxonomies=["GICS", "Commodity Class"],
    )


@router.get(
    "",
    response_model=MarketHeatmapResponse,
    summary="Query qualified market heatmap snapshot",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_market_heatmap(
    response: Response,
    universe_id: Annotated[
        str,
        Query(description="Universe ID (e.g. univ_us_equities, univ_crypto_spot, univ_futures)"),
    ] = "univ_us_equities",
    visualization_mode: Annotated[
        Optional[HeatmapVisualizationMode],
        Query(description="Visualization mode (equal_size, market_cap_weighted)"),
    ] = None,
    hierarchy_mode: Annotated[
        Optional[HeatmapHierarchyMode],
        Query(description="Hierarchy mode (none, sector, industry)"),
    ] = None,
    comparison_window: Annotated[
        Optional[HeatmapComparisonWindow],
        Query(description="Comparison window"),
    ] = None,
    sector: Annotated[
        Optional[str],
        Query(description="Optional sector filter (e.g. Technology, Healthcare)"),
    ] = None,
    max_nodes: Annotated[
        Optional[int],
        Query(ge=1, le=1000, description="Optional maximum node limit"),
    ] = None,
    service: MarketHeatmapService = Depends(get_market_heatmaps_service),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> MarketHeatmapResponse:
    """
    Computes a verified, qualified market heatmap snapshot.
    Guarantees 100% read-only access with zero provider RPC side effects.
    """
    response.headers["Cache-Control"] = "no-store, max-age=0"
    try:
        return await service.get_heatmap_snapshot(
            universe_id=universe_id,
            visualization_mode=visualization_mode,
            hierarchy_mode=hierarchy_mode,
            comparison_window=comparison_window,
            sector_filter=sector,
            max_nodes=max_nodes,
        )
    except ValueError as e:
        logger.warning(f"Heatmap validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate heatmap snapshot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to calculate market heatmap snapshot.")
