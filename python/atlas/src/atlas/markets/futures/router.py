"""FastAPI router for ATLAS Futures & Commodities Markets V1 (Stage 62)."""

import logging
from typing import Annotated, Optional
from uuid import UUID

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode

from .models import (
    CommodityDirectoryItem,
    CommodityDirectoryResponse,
    FuturesContractDirectoryResponse,
    FuturesContractOverviewResponse,
    FuturesFilterOptionsResponse,
    SpotBenchmarkDirectoryResponse,
)
from .repository import FuturesMarketRepository
from .service import (
    CommodityDirectoryService,
    FuturesDirectoryService,
    FuturesMarketReadService,
    FuturesOverviewService,
    SpotBenchmarkService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/futures", tags=["Markets Futures"])


def get_futures_services() -> tuple[
    FuturesDirectoryService,
    FuturesOverviewService,
    CommodityDirectoryService,
    SpotBenchmarkService,
    FuturesMarketRepository,
]:
    """Dependency factory providing futures and commodity market services."""
    repository = FuturesMarketRepository()
    read_service = FuturesMarketReadService(repository=repository)
    directory_service = FuturesDirectoryService(repository=repository, read_service=read_service)
    overview_service = FuturesOverviewService(repository=repository, read_service=read_service)
    commodity_service = CommodityDirectoryService(repository=repository)
    spot_service = SpotBenchmarkService(repository=repository)
    return (
        directory_service,
        overview_service,
        commodity_service,
        spot_service,
        repository,
    )


def get_futures_directory_service(
    services: tuple = Depends(get_futures_services),
) -> FuturesDirectoryService:
    return services[0]


def get_futures_overview_service(
    services: tuple = Depends(get_futures_services),
) -> FuturesOverviewService:
    return services[1]


def get_commodity_directory_service(
    services: tuple = Depends(get_futures_services),
) -> CommodityDirectoryService:
    return services[2]


def get_spot_benchmark_service(
    services: tuple = Depends(get_futures_services),
) -> SpotBenchmarkService:
    return services[3]


def get_futures_repository(
    services: tuple = Depends(get_futures_services),
) -> FuturesMarketRepository:
    return services[4]


@router.get(
    "/contracts",
    response_model=FuturesContractDirectoryResponse,
    summary="List and filter canonical exchange-traded futures contracts",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_futures_contracts(
    response: Response,
    query: Annotated[
        Optional[str],
        Query(
            description="Search by symbol, name, product, underlying, or exchange",
            max_length=64,
        ),
    ] = None,
    category: Annotated[
        Optional[str],
        Query(description="Filter by commodity category (e.g. energy, precious_metals)"),
    ] = None,
    exchange: Annotated[
        Optional[str],
        Query(description="Filter by exchange venue (e.g. NYMEX, COMEX, CBOT, CME, ICE)"),
    ] = None,
    product_entity_id: Annotated[
        Optional[UUID],
        Query(description="Filter by standardized Futures Product UUID"),
    ] = None,
    root_symbol: Annotated[
        Optional[str],
        Query(description="Filter by product root symbol (e.g. CL, GC, ZC, ES)", max_length=16),
    ] = None,
    contract_month: Annotated[
        Optional[str],
        Query(description="Filter by contract expiration month (YYYY-MM)", max_length=7),
    ] = None,
    settlement_type: Annotated[
        Optional[str],
        Query(description="Filter by settlement type (physical, cash)"),
    ] = None,
    lifecycle_status: Annotated[
        Optional[str],
        Query(description="Filter by contract lifecycle status (active, expired)"),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Page limit (default: 25, max: 100)"),
    ] = 25,
    cursor: Annotated[
        Optional[str],
        Query(description="Keyset pagination cursor from previous response"),
    ] = None,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: FuturesDirectoryService = Depends(get_futures_directory_service),
) -> FuturesContractDirectoryResponse:
    """Retrieve filtered, paginated futures contracts directory with quotes and settlements."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"

    return service.get_directory(
        query=query,
        category=category,
        exchange=exchange,
        product_entity_id=product_entity_id,
        root_symbol=root_symbol,
        contract_month=contract_month,
        settlement_type=settlement_type,
        lifecycle_status=lifecycle_status,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/filters",
    response_model=FuturesFilterOptionsResponse,
    summary="Get available filter options derived from the configured futures catalog",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_filter_options(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    repo: FuturesMarketRepository = Depends(get_futures_repository),
) -> FuturesFilterOptionsResponse:
    """Return distinct active categories, exchanges, products, months, and coverage."""
    response.headers["Cache-Control"] = "private, max-age=60"
    return repo.get_filter_options()


@router.get(
    "/commodities",
    response_model=CommodityDirectoryResponse,
    summary="List canonical underlying economic commodities",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_commodities(
    response: Response,
    category: Annotated[
        Optional[str],
        Query(description="Filter by commodity category"),
    ] = None,
    query: Annotated[
        Optional[str],
        Query(description="Search by commodity name or slug", max_length=64),
    ] = None,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CommodityDirectoryService = Depends(get_commodity_directory_service),
) -> CommodityDirectoryResponse:
    """Retrieve canonical commodities with associated futures products and active contracts."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"
    return service.get_commodities(category=category, query=query)


@router.get(
    "/commodities/{commodity_entity_id}",
    response_model=CommodityDirectoryItem,
    summary="Get details of a single underlying commodity",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_commodity(
    commodity_entity_id: UUID,
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: CommodityDirectoryService = Depends(get_commodity_directory_service),
) -> CommodityDirectoryItem:
    """Retrieve single commodity overview with associated product specifications."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"
    commodity = service.get_commodity_by_id(commodity_entity_id)
    if not commodity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commodity with entity ID '{commodity_entity_id}' not found.",
        )
    return commodity


@router.get(
    "/spot-benchmarks",
    response_model=SpotBenchmarkDirectoryResponse,
    summary="List supported physical commodity spot price benchmarks",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_spot_benchmarks(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: SpotBenchmarkService = Depends(get_spot_benchmark_service),
) -> SpotBenchmarkDirectoryResponse:
    """Retrieve physical commodity spot price benchmarks (distinct from futures prices)."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"
    return service.get_spot_benchmarks()


@router.get(
    "/contracts/{instrument_entity_id}",
    response_model=FuturesContractOverviewResponse,
    summary="Get comprehensive inspection details for a selected futures contract",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_futures_contract_overview(
    instrument_entity_id: UUID,
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: FuturesOverviewService = Depends(get_futures_overview_service),
) -> FuturesContractOverviewResponse:
    """Retrieve detailed contract overview including specifications, settlement, quotes, and OI."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"

    overview = service.get_overview(instrument_entity_id)
    if not overview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Futures contract with instrument ID '{instrument_entity_id}' not found.",
        )
    return overview
