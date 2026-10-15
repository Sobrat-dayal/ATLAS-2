"""FastAPI router for ATLAS Cryptocurrency Markets V1 (Stage 60)."""

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
    CryptoAssetDirectoryResponse,
    CryptoFilterOptionsResponse,
    CryptoSpotMarketDirectoryResponse,
    CryptoSpotMarketOverviewDetailResponse,
)
from .repository import CryptoMarketRepository
from .service import (
    CryptoAssetDirectoryService,
    CryptoDirectoryService,
    CryptoMarketReadService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/crypto", tags=["Markets Crypto"])


def get_crypto_services(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> tuple[CryptoDirectoryService, CryptoAssetDirectoryService]:
    """Dependency factory assembling crypto services from application state."""
    quote_service = None
    freshness_query_service = None

    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            quote_store = LiveQuoteStateStore(redis_client)
            quote_service = LiveQuoteService(quote_store)
        except Exception as e:
            logger.warning("Could not instantiate LiveQuoteService from redis for Crypto: %s", e)

    gateway = getattr(request.app.state, "realtime_gateway", None)
    if gateway is not None:
        freshness_query_service = getattr(gateway, "freshness_query_service", None)

    repository = CryptoMarketRepository(db_session=session)
    market_read_service = CryptoMarketReadService(
        quote_service=quote_service,
        freshness_query_service=freshness_query_service,
        ch_client_factory=getattr(request.app.state, "clickhouse_factory", None),
    )
    directory_service = CryptoDirectoryService(
        repository=repository,
        market_read_service=market_read_service,
    )
    asset_directory_service = CryptoAssetDirectoryService(repository=repository)
    return directory_service, asset_directory_service


def get_crypto_directory_service(
    services: tuple[CryptoDirectoryService, CryptoAssetDirectoryService] = Depends(
        get_crypto_services
    ),
) -> CryptoDirectoryService:
    return services[0]


def get_crypto_asset_service(
    services: tuple[CryptoDirectoryService, CryptoAssetDirectoryService] = Depends(
        get_crypto_services
    ),
) -> CryptoAssetDirectoryService:
    return services[1]


@router.get(
    "",
    response_model=CryptoSpotMarketDirectoryResponse,
    summary="List and filter canonical cryptocurrency spot markets",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_spot_markets(
    response: Response,
    query: Annotated[
        Optional[str],
        Query(description="Search by symbol, pair, alias, venue, or name", max_length=64),
    ] = None,
    base_asset: Annotated[
        Optional[str],
        Query(description="Filter by canonical base asset symbol (e.g. BTC, ETH)", max_length=16),
    ] = None,
    quote_asset: Annotated[
        Optional[str],
        Query(description="Filter by quote asset symbol (e.g. USD, USDT, EUR, BTC)", max_length=16),
    ] = None,
    venue: Annotated[
        Optional[str],
        Query(description="Filter by exchange/venue identifier (e.g. coinbase, binance)"),
    ] = None,
    quote_asset_type: Annotated[
        Optional[str],
        Query(description="Filter by quote asset type: fiat, stablecoin, crypto"),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Page limit (default: 25, max: 100)"),
    ] = 25,
    cursor: Annotated[
        Optional[str],
        Query(description="Pagination cursor from previous response"),
    ] = None,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CryptoDirectoryService = Depends(get_crypto_directory_service),
) -> CryptoSpotMarketDirectoryResponse:
    """Retrieve filtered, exchange-aware cryptocurrency spot markets with latest quotes."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"

    return await service.list_spot_markets(
        query=query,
        base_asset=base_asset,
        quote_asset=quote_asset,
        venue=venue,
        quote_asset_type=quote_asset_type,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/assets",
    response_model=CryptoAssetDirectoryResponse,
    summary="List canonical digital assets in the ATLAS catalog",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_digital_assets(
    response: Response,
    query: Annotated[
        Optional[str],
        Query(description="Search digital assets by symbol, name, or contract address"),
    ] = None,
    asset_kind: Annotated[
        Optional[str],
        Query(description="Filter by asset kind: coin, token, stablecoin, wrapped"),
    ] = None,
    network: Annotated[
        Optional[str],
        Query(description="Filter by native blockchain network (e.g. ethereum, bitcoin)"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    cursor: Annotated[Optional[str], Query()] = None,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CryptoAssetDirectoryService = Depends(get_crypto_asset_service),
) -> CryptoAssetDirectoryResponse:
    """List canonical digital assets with network and contract metadata."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"

    return service.list_assets(
        query=query,
        asset_kind=asset_kind,
        network=network,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/filters",
    response_model=CryptoFilterOptionsResponse,
    summary="Get available filter options derived from the configured crypto catalog",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_filter_options(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CryptoDirectoryService = Depends(get_crypto_directory_service),
) -> CryptoFilterOptionsResponse:
    """Return distinct active base assets, quote assets, venues, and quote asset types."""
    response.headers["Cache-Control"] = "private, max-age=60"
    return service.repository.get_filter_options()


@router.get(
    "/{instrument_entity_id}",
    response_model=CryptoSpotMarketOverviewDetailResponse,
    summary="Get comprehensive inspection details for a crypto spot market",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_market_overview(
    instrument_entity_id: UUID,
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CryptoDirectoryService = Depends(get_crypto_directory_service),
) -> CryptoSpotMarketOverviewDetailResponse:
    """Retrieve detailed spot market overview including venue and asset identity."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"

    detail = await service.get_market_overview(instrument_entity_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crypto spot market with instrument ID '{instrument_entity_id}' not found.",
        )
    return detail
