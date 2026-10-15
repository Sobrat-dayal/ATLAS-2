"""FastAPI router for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61)."""

import logging
from typing import Annotated, Optional
from uuid import UUID

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode

from .models import (
    BondDirectoryResponse,
    BondFilterOptionsResponse,
    BondOverviewResponse,
)
from .repository import BondMarketRepository
from .service import BondDirectoryService, BondMarketReadService, BondOverviewService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/markets/bonds", tags=["Markets Bonds"])


def get_bond_services() -> tuple[BondDirectoryService, BondOverviewService, BondMarketRepository]:
    """Dependency factory providing fixed-income market services."""
    repository = BondMarketRepository()
    read_service = BondMarketReadService(repository=repository)
    directory_service = BondDirectoryService(repository=repository, read_service=read_service)
    overview_service = BondOverviewService(repository=repository, read_service=read_service)
    return directory_service, overview_service, repository


def get_bond_directory_service(
    services: tuple[BondDirectoryService, BondOverviewService, BondMarketRepository] = Depends(
        get_bond_services
    ),
) -> BondDirectoryService:
    return services[0]


def get_bond_overview_service(
    services: tuple[BondDirectoryService, BondOverviewService, BondMarketRepository] = Depends(
        get_bond_services
    ),
) -> BondOverviewService:
    return services[1]


def get_bond_repository(
    services: tuple[BondDirectoryService, BondOverviewService, BondMarketRepository] = Depends(
        get_bond_services
    ),
) -> BondMarketRepository:
    return services[2]


@router.get(
    "",
    response_model=BondDirectoryResponse,
    summary="List and filter canonical bond and fixed-income securities",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def list_bonds(
    response: Response,
    query: Annotated[
        Optional[str],
        Query(description="Search by security name, symbol, ISIN, CUSIP, or issuer", max_length=64),
    ] = None,
    issuer_type: Annotated[
        Optional[str],
        Query(description="Filter by issuer category (e.g. sovereign, corporate, supranational)"),
    ] = None,
    issuer_entity_id: Annotated[
        Optional[UUID],
        Query(description="Filter by specific Organization Entity UUID"),
    ] = None,
    bond_type: Annotated[
        Optional[str],
        Query(description="Filter by debt type (e.g. sovereign, corporate, treasury_bill)"),
    ] = None,
    currency: Annotated[
        Optional[str],
        Query(
            description="Filter by currency denomination (e.g. USD, EUR, GBP, JPY)",
            max_length=3,
        ),
    ] = None,
    coupon_type: Annotated[
        Optional[str],
        Query(description="Filter by coupon type (e.g. fixed, zero_coupon, floating)"),
    ] = None,
    maturity_bucket: Annotated[
        Optional[str],
        Query(description="Filter by maturity bucket approximation"),
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
    service: BondDirectoryService = Depends(get_bond_directory_service),
) -> BondDirectoryResponse:
    """Retrieve filtered, paginated bond securities directory with clean/dirty prices and yields."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"

    return service.get_directory(
        query=query,
        issuer_type=issuer_type,
        issuer_entity_id=issuer_entity_id,
        bond_type=bond_type,
        currency=currency,
        coupon_type=coupon_type,
        maturity_bucket=maturity_bucket,
        limit=limit,
        cursor=cursor,
    )


@router.get(
    "/filters",
    response_model=BondFilterOptionsResponse,
    summary="Get available filter options derived from the configured bond catalog",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_filter_options(
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    repo: BondMarketRepository = Depends(get_bond_repository),
) -> BondFilterOptionsResponse:
    """Return distinct active issuer categories, bond types, currencies, and coverage."""
    response.headers["Cache-Control"] = "private, max-age=60"
    return repo.get_filter_options()


@router.get(
    "/{instrument_entity_id}",
    response_model=BondOverviewResponse,
    summary="Get comprehensive inspection details for a selected bond security",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_bond_overview(
    instrument_entity_id: UUID,
    response: Response,
    current_user: AuthPrincipal = Depends(get_current_user),
    service: BondOverviewService = Depends(get_bond_overview_service),
) -> BondOverviewResponse:
    """Retrieve detailed bond overview including terms, clean/dirty prices, and yields."""
    response.headers["Cache-Control"] = "private, no-cache, no-transform"

    overview = service.get_overview(instrument_entity_id)
    if not overview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bond security with instrument ID '{instrument_entity_id}' not found.",
        )
    return overview
