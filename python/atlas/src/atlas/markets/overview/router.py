"""FastAPI router for ATLAS Markets Overview V1 (Stage 56)."""

import logging
from typing import Annotated, Optional

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import LiveQuoteStateStore

from .models import MarketsOverviewResponse
from .service import MarketsOverviewService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets", tags=["Markets"])


def get_markets_overview_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> MarketsOverviewService:
    """Dependency factory assembling MarketsOverviewService from application state."""
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

    return MarketsOverviewService(
        quote_service=quote_service,
        freshness_query_service=freshness_query_service,
        db_session=session,
        ch_client_factory=getattr(request.app.state, "clickhouse_factory", None),
    )


@router.get(
    "/overview",
    response_model=MarketsOverviewResponse,
    summary="Get Markets Overview",
    description="Read-only multi-asset market overview for configured canonical instruments.",
)
async def get_markets_overview(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[MarketsOverviewService, Depends(get_markets_overview_service)],
    group: Optional[str] = Query(
        default=None,
        description=(
            "Filter by asset group (benchmarks, equities, etfs, "
            "fx, crypto, commodities, bonds)."
        ),
    ),
    limit: int = Query(default=25, ge=1, le=100, description="Page size limit."),
    cursor: Optional[str] = Query(default=None, description="Pagination cursor (offset token)."),
    featured_only: bool = Query(default=False, description="Filter only featured instruments."),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> MarketsOverviewResponse:
    """
    Authenticated, read-only endpoint returning canonical Markets Overview.
    Enforces 'atlas.access' permission and applies 'private, no-store' cache headers.
    """
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_markets_overview(
        group=group,
        limit=limit,
        cursor=cursor,
        featured_only=featured_only,
    )
