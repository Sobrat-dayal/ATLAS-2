"""FastAPI router for ATLAS Cross-Asset Markets V1 (Stage 65)."""

import logging
from typing import Optional

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from fastapi import APIRouter, Depends, HTTPException, Query, Response

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode

from .config import (
    MAX_SELECTION_COUNT,
    CrossAssetMode,
    CrossAssetWindow,
)
from .models import (
    CrossAssetOptionsResponse,
    CrossAssetOverviewResponse,
    CrossAssetUniverseResponse,
)
from .repository import CrossAssetMarketRepository
from .service import CrossAssetMarketService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/cross-asset", tags=["Markets Cross-Asset"])


def get_cross_asset_service() -> CrossAssetMarketService:
    """Dependency provider for CrossAssetMarketService."""
    repository = CrossAssetMarketRepository()
    return CrossAssetMarketService(repository=repository)


@router.get(
    "/universes",
    response_model=CrossAssetUniverseResponse,
    summary="List available canonical cross-asset universes",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_cross_asset_universes(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CrossAssetMarketService = Depends(get_cross_asset_service),
) -> CrossAssetUniverseResponse:
    """Returns supported canonical multi-asset universes."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return service.get_universes()


@router.get(
    "/options",
    response_model=CrossAssetOptionsResponse,
    summary="List supported analytical modes, comparison windows, and asset classes",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_cross_asset_options(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CrossAssetMarketService = Depends(get_cross_asset_service),
) -> CrossAssetOptionsResponse:
    """Returns supported analytical modes, windows, and alignment parameters."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return service.get_options()


@router.get(
    "",
    response_model=CrossAssetOverviewResponse,
    summary="Get cross-asset market overview and aligned performance snapshot",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_cross_asset_overview(
    response: Response,
    universe_id: str = Query(
        default="univ_cross_asset_macro",
        description="Canonical multi-asset universe identifier.",
    ),
    mode: CrossAssetMode = Query(
        default=CrossAssetMode.NATIVE_OVERVIEW,
        description="Analytical mode: 'native_overview' or 'aligned_performance'.",
    ),
    window: CrossAssetWindow = Query(
        default=CrossAssetWindow.LAST_24H,
        description="Comparison window: 'last_24h', 'last_7d', or 'last_30d'.",
    ),
    symbols: Optional[str] = Query(
        default=None,
        description="Optional comma-separated list of canonical symbols to compare (max 12).",
    ),
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CrossAssetMarketService = Depends(get_cross_asset_service),
) -> CrossAssetOverviewResponse:
    """Computes and returns a verified institutional cross-asset market snapshot."""
    response.headers["Cache-Control"] = "no-store, max-age=0"

    selected_symbols = None
    if symbols:
        sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if len(sym_list) > MAX_SELECTION_COUNT:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Exceeded maximum bounded selection count of "
                    f"{MAX_SELECTION_COUNT} instruments."
                ),
            )
        selected_symbols = sym_list

    return service.get_cross_asset_overview(
        universe_id=universe_id,
        mode=mode,
        window=window,
        selected_symbols=selected_symbols,
    )
