"""FastAPI router for ATLAS ETFs & Funds Markets V1 (Stage 58)."""

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
    FundDirectoryResponse,
    FundFilterOptionsResponse,
    FundOverviewDetailResponse,
)
from .repository import FundDirectoryRepository
from .service import FundDirectoryService, FundMarketReadService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/funds", tags=["Markets Funds"])


def get_fund_directory_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> FundDirectoryService:
    """Dependency factory assembling FundDirectoryService from application state."""
    quote_service = None
    freshness_query_service = None

    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            quote_store = LiveQuoteStateStore(redis_client)
            quote_service = LiveQuoteService(quote_store)
        except Exception as e:
            logger.warning("Could not instantiate LiveQuoteService from redis for funds: %s", e)

    gateway = getattr(request.app.state, "realtime_gateway", None)
    if gateway is not None:
        freshness_query_service = getattr(gateway, "freshness_query_service", None)

    repository = FundDirectoryRepository(db_session=session)
    market_read_service = FundMarketReadService(
        quote_service=quote_service,
        freshness_query_service=freshness_query_service,
        ch_client_factory=getattr(request.app.state, "clickhouse_factory", None),
    )

    return FundDirectoryService(
        repository=repository,
        market_read_service=market_read_service,
    )


@router.get(
    "",
    response_model=FundDirectoryResponse,
    summary="Get Fund Directory",
    description=(
        "Read-only directory of canonical ETFs and investment funds with market data and NAV."
    ),
)
async def get_fund_directory(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[FundDirectoryService, Depends(get_fund_directory_service)],
    fund_type: Optional[str] = Query(
        default=None,
        max_length=64,
        description="Filter by fund type (e.g. ETF, OPEN_END_MUTUAL_FUND, CLOSED_END_FUND).",
    ),
    market_country: Optional[str] = Query(
        default=None,
        max_length=64,
        description="Filter by listing market country.",
    ),
    exchange: Optional[str] = Query(
        default=None,
        max_length=64,
        description="Filter by exchange MIC or name.",
    ),
    domicile: Optional[str] = Query(
        default=None,
        max_length=64,
        description="Filter by fund domicile jurisdiction.",
    ),
    fund_category: Optional[str] = Query(
        default=None,
        max_length=128,
        description="Filter by investment category (e.g. Equity, Fixed Income, Commodity).",
    ),
    share_class_currency: Optional[str] = Query(
        default=None,
        max_length=16,
        description="Filter by share class currency (e.g. USD).",
    ),
    query: Optional[str] = Query(
        default=None,
        max_length=100,
        description="Search by fund name, symbol, ISIN, FIGI, benchmark or manager.",
    ),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit (max 100)."),
    cursor: Optional[str] = Query(default=None, description="Pagination cursor offset token."),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FundDirectoryResponse:
    """
    Authenticated, read-only endpoint returning canonical Fund Directory.
    Enforces 'atlas.access' permission and applies 'private, no-store' cache headers.
    """
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_fund_directory(
        fund_type=fund_type,
        market_country=market_country,
        exchange=exchange,
        domicile=domicile,
        fund_category=fund_category,
        share_class_currency=share_class_currency,
        query=query,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/filters",
    response_model=FundFilterOptionsResponse,
    summary="Get Fund Filter Options",
    description=(
        "Returns available filter options grounded strictly in canonical fund catalog contents."
    ),
)
async def get_fund_filter_options(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[FundDirectoryService, Depends(get_fund_directory_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FundFilterOptionsResponse:
    """
    Returns distinct fund types, listing countries, exchanges, categories, and currencies.
    """
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_fund_filter_options()


@router.get(
    "/{instrument_entity_id}",
    response_model=FundOverviewDetailResponse,
    summary="Get Fund Overview Detail",
    description="Detailed inspector overview for a single canonical fund or ETF instrument.",
)
async def get_fund_detail(
    instrument_entity_id: UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[FundDirectoryService, Depends(get_fund_directory_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FundOverviewDetailResponse:
    """
    Returns detailed Fund Overview inspector model.
    Enforces UUID validity, returns 404 if instrument is not found.
    """
    response.headers["Cache-Control"] = "private, no-store"
    detail = await service.get_fund_detail(instrument_entity_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund instrument not found.",
        )
    return detail
