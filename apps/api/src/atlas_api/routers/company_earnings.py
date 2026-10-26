"""FastAPI Router for Company Earnings Intelligence (Stage 84).

Endpoints:
- GET /companies/{company_id}/earnings/overview
- GET /companies/{company_id}/earnings/events
- GET /companies/{company_id}/earnings/history
- GET /companies/{company_id}/earnings/guidance
- GET /companies/{company_id}/earnings/calls
- GET /companies/{company_id}/earnings/events/{event_id}
"""

import logging
import uuid
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.companies.earnings.enums import (
    EarningsEventStatus,
    EarningsPeriodType,
    GuidanceStatus,
)
from atlas.companies.earnings.errors import (
    EarningsError,
    EarningsEventNotFoundError,
)
from atlas.companies.earnings.repository import CompanyEarningsRepository
from atlas.companies.earnings.schemas import (
    CompanyEarningsOverviewDTO,
    EarningsCallsResponseDTO,
    EarningsEventDTO,
    EarningsEventsResponseDTO,
    EarningsHistoryResponseDTO,
    GuidanceResponseDTO,
)
from atlas.companies.earnings.service import CompanyEarningsService
from atlas.companies.errors import CompanyNotFoundError
from atlas.companies.service import CompanyService
from atlas.companies.statements.repository import CompanyStatementsRepository
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from atlas_api.routers.companies import get_company_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies/{company_id}/earnings", tags=["Company Earnings"])


def get_earnings_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CompanyEarningsService:
    statements_repo = CompanyStatementsRepository(session=session)
    repository = CompanyEarningsRepository(statements_repo=statements_repo)
    return CompanyEarningsService(repository=repository)


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
    response_model=CompanyEarningsOverviewDTO,
    summary="Get Company Earnings Overview",
    description="Returns high-level summary of latest reported earnings, next upcoming release, and active guidance.",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_company_earnings_overview(
    company_id: Annotated[uuid.UUID, Path(description="Canonical Company UUID")],
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[CompanyEarningsService, Depends(get_earnings_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> CompanyEarningsOverviewDTO:
    company_name = await _verify_company(company_id, company_service)
    try:
        overview = await service.get_earnings_overview(company_id)
        overview.company_name = company_name
        return overview
    except EarningsError as e:
        logger.error(f"Earnings overview error for company {company_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/history",
    response_model=EarningsHistoryResponseDTO,
    summary="Get Multi-Period Historical Earnings Results",
    description="Returns chronological earnings history with reported actuals, pre-release consensus, and pure Decimal surprises.",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_company_earnings_history(
    company_id: Annotated[uuid.UUID, Path(description="Canonical Company UUID")],
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[CompanyEarningsService, Depends(get_earnings_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    period_type: Annotated[EarningsPeriodType, Query(description="Fiscal period type")] = EarningsPeriodType.QUARTERLY,
    limit: Annotated[int, Query(ge=1, le=40, description="Max periods to return")] = 16,
) -> EarningsHistoryResponseDTO:
    company_name = await _verify_company(company_id, company_service)
    try:
        history = await service.get_earnings_history(company_id, period_type=period_type, limit=limit)
        history.company_name = company_name
        return history
    except EarningsError as e:
        logger.error(f"Earnings history error for company {company_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/events",
    response_model=EarningsEventsResponseDTO,
    summary="Get Earnings Announcement Events",
    description="Returns verified scheduled, completed, and revised earnings announcement events.",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_company_earnings_events(
    company_id: Annotated[uuid.UUID, Path(description="Canonical Company UUID")],
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[CompanyEarningsService, Depends(get_earnings_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    status: Annotated[Optional[EarningsEventStatus], Query(description="Filter by event status")] = None,
) -> EarningsEventsResponseDTO:
    company_name = await _verify_company(company_id, company_service)
    try:
        events = await service.get_earnings_events(company_id, status=status)
        events.company_name = company_name
        return events
    except EarningsError as e:
        logger.error(f"Earnings events error for company {company_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/events/{event_id}",
    response_model=EarningsEventDTO,
    summary="Get Specific Earnings Event Details",
    description="Returns details for a single verified corporate earnings event.",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_company_earnings_event_detail(
    company_id: Annotated[uuid.UUID, Path(description="Canonical Company UUID")],
    event_id: Annotated[str, Path(description="Unique Earnings Event ID")],
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[CompanyEarningsService, Depends(get_earnings_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> EarningsEventDTO:
    await _verify_company(company_id, company_service)
    try:
        return await service.get_event_detail(company_id, event_id)
    except EarningsEventNotFoundError:
        raise HTTPException(status_code=404, detail=f"Earnings event '{event_id}' not found")


@router.get(
    "/guidance",
    response_model=GuidanceResponseDTO,
    summary="Get Management Forward Guidance",
    description="Returns management-issued forward guidance ranges and revisions.",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_company_management_guidance(
    company_id: Annotated[uuid.UUID, Path(description="Canonical Company UUID")],
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[CompanyEarningsService, Depends(get_earnings_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    status: Annotated[Optional[GuidanceStatus], Query(description="Filter by guidance status")] = None,
) -> GuidanceResponseDTO:
    company_name = await _verify_company(company_id, company_service)
    try:
        guidance = await service.get_management_guidance(company_id, status=status)
        guidance.company_name = company_name
        return guidance
    except EarningsError as e:
        logger.error(f"Guidance error for company {company_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/calls",
    response_model=EarningsCallsResponseDTO,
    summary="Get Earnings Call Records & Transcript Links",
    description="Returns verified earnings call dates, webcasts, and transcript document references.",
    dependencies=[Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
)
async def get_company_earnings_calls(
    company_id: Annotated[uuid.UUID, Path(description="Canonical Company UUID")],
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[CompanyEarningsService, Depends(get_earnings_service)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
) -> EarningsCallsResponseDTO:
    company_name = await _verify_company(company_id, company_service)
    try:
        calls = await service.get_earnings_calls(company_id)
        calls.company_name = company_name
        return calls
    except EarningsError as e:
        logger.error(f"Earnings calls error for company {company_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
