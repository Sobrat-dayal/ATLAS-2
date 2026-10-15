"""FastAPI router for ATLAS Equities Markets V1 (Stage 57)."""

import logging
from typing import Annotated, Optional
from uuid import UUID

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import LiveQuoteStateStore

from .models import (
    EquityDirectoryResponse,
    EquityFilterOptionsResponse,
    EquityOverviewDetailResponse,
)
from .repository import EquityDirectoryRepository
from .service import EquityDirectoryService, EquityMarketReadService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/equities", tags=["Markets Equities"])


def get_equity_directory_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> EquityDirectoryService:
    """Dependency factory assembling EquityDirectoryService from application state."""
    quote_service = None
    freshness_query_service = None

    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            quote_store = LiveQuoteStateStore(redis_client)
            quote_service = LiveQuoteService(quote_store)
        except Exception as e:
            logger.warning("Could not instantiate LiveQuoteService from redis for equities: %s", e)

    gateway = getattr(request.app.state, "realtime_gateway", None)
    if gateway is not None:
        freshness_query_service = getattr(gateway, "freshness_query_service", None)

    repository = EquityDirectoryRepository(db_session=session)
    market_read_service = EquityMarketReadService(
        quote_service=quote_service,
        freshness_query_service=freshness_query_service,
        ch_client_factory=getattr(request.app.state, "clickhouse_factory", None),
    )

    return EquityDirectoryService(
        repository=repository,
        market_read_service=market_read_service,
    )


@router.get(
    "",
    response_model=EquityDirectoryResponse,
    summary="Get Equity Directory",
    description="Read-only directory of canonical equity securities with market data.",
)
async def get_equity_directory(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[EquityDirectoryService, Depends(get_equity_directory_service)],
    query: Optional[str] = Query(
        default=None, max_length=100, description="Search by name, symbol, or venue."
    ),
    market_country: Optional[str] = Query(
        default=None, max_length=64, description="Filter by listing market country."
    ),
    exchange: Optional[str] = Query(
        default=None, max_length=64, description="Filter by exchange MIC or name."
    ),
    equity_type: Optional[str] = Query(
        default=None, max_length=64, description="Filter by subtype (e.g. common_stock)."
    ),
    listing_status: Optional[str] = Query(
        default=None, max_length=32, description="Filter by listing status (e.g. ACTIVE)."
    ),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit (max 100)."),
    cursor: Optional[str] = Query(default=None, description="Pagination cursor offset token."),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EquityDirectoryResponse:
    """
    Authenticated, read-only endpoint returning canonical Equity Directory.
    Enforces 'atlas.access' permission and applies 'private, no-store' cache headers.
    """
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_equity_directory(
        query=query,
        market_country=market_country,
        exchange=exchange,
        equity_type=equity_type,
        listing_status=listing_status,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/filters",
    response_model=EquityFilterOptionsResponse,
    summary="Get Equity Filter Options",
    description="Returns available filter options grounded strictly in canonical catalog contents.",
)
async def get_equity_filter_options(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[EquityDirectoryService, Depends(get_equity_directory_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EquityFilterOptionsResponse:
    """
    Returns distinct listing market countries, exchanges, and subtypes in the catalog.
    """
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_equity_filter_options()


@router.get(
    "/{instrument_entity_id}",
    response_model=EquityOverviewDetailResponse,
    summary="Get Equity Security Overview",
    description="Detailed inspector overview for a single canonical equity security.",
)
async def get_equity_detail(
    instrument_entity_id: UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[EquityDirectoryService, Depends(get_equity_directory_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> EquityOverviewDetailResponse:
    """
    Returns detailed Security Overview inspector model.
    Enforces UUID validity, returns 404 if instrument is not found or not an equity security.
    """
    response.headers["Cache-Control"] = "private, no-store"
    detail = await service.get_equity_detail(instrument_entity_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equity instrument not found.",
        )
    return detail
