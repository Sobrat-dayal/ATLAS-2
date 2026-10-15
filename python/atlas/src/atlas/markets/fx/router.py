"""FastAPI router for ATLAS FX Markets V1 (Stage 59)."""

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
    FxConversionRequest,
    FxConversionResponse,
    FxCurrenciesResponse,
    FxPairDirectoryResponse,
    FxPairOverviewDetailResponse,
)
from .repository import FxDirectoryRepository
from .service import FxConversionService, FxDirectoryService, FxMarketReadService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/fx", tags=["Markets FX"])


def get_fx_services(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> tuple[FxDirectoryService, FxConversionService]:
    """Dependency factory assembling FX services from application state."""
    quote_service = None
    freshness_query_service = None

    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            quote_store = LiveQuoteStateStore(redis_client)
            quote_service = LiveQuoteService(quote_store)
        except Exception as e:
            logger.warning("Could not instantiate LiveQuoteService from redis for FX: %s", e)

    gateway = getattr(request.app.state, "realtime_gateway", None)
    if gateway is not None:
        freshness_query_service = getattr(gateway, "freshness_query_service", None)

    repository = FxDirectoryRepository(db_session=session)
    market_read_service = FxMarketReadService(
        quote_service=quote_service,
        freshness_query_service=freshness_query_service,
        ch_client_factory=getattr(request.app.state, "clickhouse_factory", None),
    )
    directory_service = FxDirectoryService(
        repository=repository,
        market_read_service=market_read_service,
    )
    conversion_service = FxConversionService(
        repository=repository,
        market_read_service=market_read_service,
    )
    return directory_service, conversion_service


def get_fx_directory_service(
    services: tuple[FxDirectoryService, FxConversionService] = Depends(get_fx_services),
) -> FxDirectoryService:
    return services[0]


def get_fx_conversion_service(
    services: tuple[FxDirectoryService, FxConversionService] = Depends(get_fx_services),
) -> FxConversionService:
    return services[1]


@router.get(
    "",
    response_model=FxPairDirectoryResponse,
    summary="Get FX Pair Directory",
    description=(
        "Read-only directory of canonical spot currency pairs with bid/ask quotes "
        "and spread analytics."
    ),
)
async def get_fx_directory(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[FxDirectoryService, Depends(get_fx_directory_service)],
    base_currency: Optional[str] = Query(
        default=None,
        max_length=3,
        description="Filter by 3-letter base currency code (e.g. EUR, USD, GBP).",
    ),
    quote_currency: Optional[str] = Query(
        default=None,
        max_length=3,
        description="Filter by 3-letter quote currency code (e.g. USD, JPY, EUR).",
    ),
    query: Optional[str] = Query(
        default=None,
        max_length=50,
        description="Search by pair (e.g. EUR/USD), alias, or currency name.",
    ),
    limit: int = Query(default=25, ge=1, le=100, description="Page limit (max 100)."),
    cursor: Optional[str] = Query(default=None, description="Pagination cursor offset token."),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FxPairDirectoryResponse:
    """Authenticated, read-only endpoint returning canonical FX Pair Directory."""
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_directory(
        base_currency=base_currency,
        quote_currency=quote_currency,
        query=query,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/currencies",
    response_model=FxCurrenciesResponse,
    summary="Get Supported FX Currencies",
    description=(
        "Returns distinct validated ISO 4217 fiat currencies represented in the "
        "canonical FX catalog."
    ),
)
async def get_fx_currencies(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[FxDirectoryService, Depends(get_fx_directory_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FxCurrenciesResponse:
    """Returns validated fiat currencies supported for FX discovery and conversion."""
    response.headers["Cache-Control"] = "private, no-store"
    items = await service.get_supported_currencies()
    return FxCurrenciesResponse(items=items, total_count=len(items))


@router.get(
    "/{instrument_entity_id}",
    response_model=FxPairOverviewDetailResponse,
    summary="Get FX Pair Overview Detail",
    description="Inspect a single canonical currency pair by instrument UUID.",
)
async def get_fx_pair_detail(
    instrument_entity_id: UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[FxDirectoryService, Depends(get_fx_directory_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FxPairOverviewDetailResponse:
    """Detailed inspection of a canonical currency pair."""
    response.headers["Cache-Control"] = "private, no-store"
    detail = await service.get_pair_detail(instrument_entity_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Canonical FX pair with instrument_entity_id '{instrument_entity_id}' not found."
            ),
        )
    return detail


@router.post(
    "/convert",
    response_model=FxConversionResponse,
    summary="Indicative Currency Conversion",
    description=(
        "Performs read-only, bounded indicative currency conversion using Decimal precision."
    ),
)
async def convert_currency(
    payload: FxConversionRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[FxConversionService, Depends(get_fx_conversion_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> FxConversionResponse:
    """
    Read-only conversion endpoint.
    Zero mutations, zero broker order placement, strictly indicative.
    """
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.convert(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
