"""FastAPI router for ATLAS Home Market Summary (Stage 52)."""

import logging
from typing import Annotated

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import LiveQuoteStateStore

from .models import HomeMarketSummaryResponse
from .service import HomeMarketSummaryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/home", tags=["Home"])


def get_market_summary_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> HomeMarketSummaryService:
    """Dependency factory assembling HomeMarketSummaryService from application state."""
    quote_service = None
    freshness_query_service = None

    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            quote_store = LiveQuoteStateStore(redis_client)
            quote_service = LiveQuoteService(quote_store)
        except Exception as e:
            logger.warning("Could not instantiate LiveQuoteService from redis: %s", e)

    gateway = getattr(request.app.state, "realtime_gateway", None)
    if gateway is not None:
        freshness_query_service = getattr(gateway, "freshness_query_service", None)

    return HomeMarketSummaryService(
        quote_service=quote_service,
        freshness_query_service=freshness_query_service,
        db_session=session,
        ch_client_factory=getattr(request.app.state, "clickhouse_factory", None),
    )


@router.get(
    "/market-summary",
    response_model=HomeMarketSummaryResponse,
    summary="Get Home Market Summary",
    description="Read-only canonical overview for curated ATLAS benchmark instruments.",
)
async def get_home_market_summary(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[HomeMarketSummaryService, Depends(get_market_summary_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> HomeMarketSummaryResponse:
    """
    Authenticated, read-only endpoint returning canonical Home Market Summary.
    Enforces 'atlas.access' permission and applies 'private, no-store' cache headers.
    """
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_market_summary()
