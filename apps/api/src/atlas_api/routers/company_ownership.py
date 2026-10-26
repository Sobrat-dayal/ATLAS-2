"""FastAPI Router for Company Ownership Intelligence (Stage 85).

Endpoints:
- GET /companies/{company_id}/ownership/overview
- GET /companies/{company_id}/ownership/securities
- GET /companies/{company_id}/ownership/holders
- GET /companies/{company_id}/ownership/institutions
- GET /companies/{company_id}/ownership/insiders
- GET /companies/{company_id}/ownership/beneficial
- GET /companies/{company_id}/ownership/patterns
- GET /companies/{company_id}/ownership/history
- GET /companies/{company_id}/ownership/changes
"""

import logging
import uuid
from typing import Optional

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.companies.errors import CompanyNotFoundError
from atlas.companies.ownership.enums import HolderCategory
from atlas.companies.ownership.errors import OwnershipError
from atlas.companies.ownership.repository import CompanyOwnershipRepository
from atlas.companies.ownership.schemas import (
    BeneficialOwnersResponseDTO,
    CompanyOwnershipOverviewDTO,
    InsiderHoldingsResponseDTO,
    InstitutionalHoldingsResponseDTO,
    OwnershipChangesResponseDTO,
    OwnershipHistoryResponseDTO,
    OwnershipHoldersResponseDTO,
    OwnershipSecuritiesResponseDTO,
    ShareholdingPatternDTO,
)
from atlas.companies.ownership.service import CompanyOwnershipService
from atlas.companies.service import CompanyService
from fastapi import APIRouter, Depends, HTTPException, Query

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.routers.companies import get_company_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies/{company_id}/ownership", tags=["Company Ownership"])


def get_ownership_service() -> CompanyOwnershipService:
    repository = CompanyOwnershipRepository()
    return CompanyOwnershipService(repository=repository)


async def _verify_company(
    company_id: uuid.UUID,
    company_service: CompanyService,
) -> str:
    """Helper to verify company existence and resolve its display name."""
    try:
        entity, company = await company_service.get_company(company_id)
        return entity.display_name or company.legal_name or "Company"
    except CompanyNotFoundError:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")


@router.get(
    "/overview",
    response_model=CompanyOwnershipOverviewDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_ownership_overview(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Target security/share class ID"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> CompanyOwnershipOverviewDTO:
    """Returns high-level ownership intelligence summary, top holders, and concentration metrics."""
    company_name = await _verify_company(company_id, company_service)
    try:
        overview = ownership_service.get_ownership_overview(str(company_id), security_id=security_id)
        overview.company_name = company_name
        return overview
    except OwnershipError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/securities",
    response_model=OwnershipSecuritiesResponseDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_ownership_securities(
    company_id: uuid.UUID,
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> OwnershipSecuritiesResponseDTO:
    """Returns available securities and share classes for the issuing company."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_securities(str(company_id))


@router.get(
    "/holders",
    response_model=OwnershipHoldersResponseDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_all_holders(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Security entity ID"),
    category: Optional[HolderCategory] = Query(None, description="Filter by holder category"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> OwnershipHoldersResponseDTO:
    """Returns paginated collection of verified disclosed security holders."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_all_holders(
        str(company_id),
        security_id=security_id,
        category=category,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/institutions",
    response_model=InstitutionalHoldingsResponseDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_institutional_holdings(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Security entity ID"),
    limit: int = Query(50, ge=1, le=100, description="Page limit"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> InstitutionalHoldingsResponseDTO:
    """Returns institutional manager and fund holdings with comparative position changes."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_institutional_holdings(
        str(company_id),
        security_id=security_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/insiders",
    response_model=InsiderHoldingsResponseDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_insider_holdings(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Security entity ID"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> InsiderHoldingsResponseDTO:
    """Returns corporate officer, director, and 10% insider holdings from public filings."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_insider_holdings(str(company_id), security_id=security_id)


@router.get(
    "/beneficial",
    response_model=BeneficialOwnersResponseDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_beneficial_owners(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Security entity ID"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> BeneficialOwnersResponseDTO:
    """Returns Schedule 13D/13G beneficial owners with voting and dispositive power breakdowns."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_beneficial_ownership(str(company_id), security_id=security_id)


@router.get(
    "/patterns",
    response_model=ShareholdingPatternDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_shareholding_patterns(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Security entity ID"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> ShareholdingPatternDTO:
    """Returns categorized shareholding patterns (e.g. SEBI or standard category taxonomy)."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_shareholding_patterns(str(company_id), security_id=security_id)


@router.get(
    "/history",
    response_model=OwnershipHistoryResponseDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_ownership_history(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Security entity ID"),
    limit: int = Query(12, ge=1, le=40, description="Snapshots limit"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> OwnershipHistoryResponseDTO:
    """Returns historical ownership snapshots for trend analysis."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_ownership_history(str(company_id), security_id=security_id, limit=limit)


@router.get(
    "/changes",
    response_model=OwnershipChangesResponseDTO,
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_position_changes(
    company_id: uuid.UUID,
    security_id: Optional[str] = Query(None, description="Security entity ID"),
    current_period: Optional[str] = Query(None, description="Current quarter period (e.g. 2024-Q3)"),
    prior_period: Optional[str] = Query(None, description="Prior quarter period (e.g. 2024-Q2)"),
    current_user: AuthPrincipal = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
    ownership_service: CompanyOwnershipService = Depends(get_ownership_service),
) -> OwnershipChangesResponseDTO:
    """Returns comparative position changes between two quarterly disclosure snapshots."""
    await _verify_company(company_id, company_service)
    return ownership_service.get_position_changes(
        str(company_id),
        security_id=security_id,
        current_period=current_period,
        prior_period=prior_period,
    )
