"""FastAPI router for ATLAS Market Movers V1 (Stage 63)."""

import logging
from typing import Annotated, Optional

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from fastapi import APIRouter, Depends, Query, Response

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode

from .config import (
    DEFAULT_MOVER_UNIVERSE_ID,
    ComparisonWindow,
    MoverCategory,
)
from .models import (
    MarketMoverResponse,
    MoverMetricOptionsResponse,
    MoverUniverseResponse,
)
from .repository import MarketMoversRepository
from .service import MarketMoverRankingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/movers", tags=["Markets Movers"])


def get_market_movers_service() -> MarketMoverRankingService:
    """Dependency provider for MarketMoverRankingService."""
    repository = MarketMoversRepository()
    return MarketMoverRankingService(repository=repository)


@router.get(
    "/universes",
    response_model=MoverUniverseResponse,
    summary="List available, authorized ranking universes",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_mover_universes(
    response: Response,
    service: MarketMoverRankingService = Depends(get_market_movers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> MoverUniverseResponse:
    """Returns all supported canonical mover universes for the authenticated user."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return service.get_supported_universes()


@router.get(
    "/metrics",
    response_model=MoverMetricOptionsResponse,
    summary="List valid ranking metrics and windows for a universe",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_mover_metric_options(
    response: Response,
    universe_id: Annotated[
        str,
        Query(description="Universe identifier to inspect metric support for"),
    ] = DEFAULT_MOVER_UNIVERSE_ID,
    service: MarketMoverRankingService = Depends(get_market_movers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> MoverMetricOptionsResponse:
    """Returns active metric policies, observation windows, and units for a universe."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return service.get_metric_options(universe_id=universe_id)


@router.get(
    "",
    response_model=MarketMoverResponse,
    summary="Query qualified market mover rankings",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_market_movers(
    response: Response,
    universe_id: Annotated[
        str,
        Query(description="Universe ID (e.g. univ_us_equities, univ_crypto_spot, univ_futures)"),
    ] = DEFAULT_MOVER_UNIVERSE_ID,
    category: Annotated[
        MoverCategory,
        Query(description="Ranking category (gainers, losers, most_active)"),
    ] = MoverCategory.GAINERS,
    window: Annotated[
        Optional[ComparisonWindow],
        Query(description="Comparison window (defaults to universe default window)"),
    ] = None,
    exchange: Annotated[
        Optional[str],
        Query(description="Filter by exchange or venue"),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Page size limit (default: 25, max: 100)"),
    ] = 25,
    cursor: Annotated[
        Optional[str],
        Query(description="Pagination cursor from previous response"),
    ] = None,
    service: MarketMoverRankingService = Depends(get_market_movers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
) -> MarketMoverResponse:
    """
    Computes and returns a qualified market mover leaderboard snapshot.

    Guarantees:
    - Strictly Decimal calculations.
    - Deterministic tie-breaking by instrument UUID.
    - Zero denominator exclusion for percentage return rankings.
    - Comprehensive coverage statistics (candidate, evaluated, qualified, excluded counts).
    - Read-only operations (0 writes to database or cache).
    """
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return await service.get_market_movers(
        universe_id=universe_id,
        category=category,
        window=window,
        exchange=exchange,
        limit=limit,
        cursor=cursor,
    )
