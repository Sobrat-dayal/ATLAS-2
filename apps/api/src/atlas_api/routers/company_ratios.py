"""FastAPI Router for Company Financial Ratios (Stage 83).

Endpoints:
- GET /companies/{company_id}/ratios/catalog
- GET /companies/{company_id}/ratios
- GET /companies/{company_id}/ratios/history
- GET /companies/{company_id}/ratios/{ratio_id}/methodology
- GET /companies/{company_id}/ratios/{ratio_id}/lineage
"""

import logging
import uuid
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.companies.errors import CompanyNotFoundError
from atlas.companies.ratios.enums import RatioCategory, RatioPeriodType
from atlas.companies.ratios.errors import RatioError, RatioNotFoundError
from atlas.companies.ratios.schemas import (
    CompanyRatiosResponse,
    RatioCatalogResponse,
    RatioHistoryResponse,
    RatioLineageResponse,
    RatioMethodologyResponse,
)
from atlas.companies.ratios.service import CompanyRatiosService
from atlas.companies.service import CompanyService
from atlas.companies.statements.enums import ConsolidationScope
from atlas.companies.statements.repository import CompanyStatementsRepository
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from atlas_api.routers.companies import get_company_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies/{company_id}/ratios", tags=["Company Financial Ratios"])


def get_ratios_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CompanyRatiosService:
    statements_repo = CompanyStatementsRepository(session=session)
    return CompanyRatiosService(statements_repo=statements_repo)


async def _resolve_company_name(
    company_id: uuid.UUID,
    company_service: CompanyService,
) -> str:
    """Helper to verify company existence and resolve its display name."""
    try:
        entity, company = await company_service.get_company(company_id)
        return entity.display_name or company.legal_name or "Company"
    except CompanyNotFoundError:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")
    except Exception as e:
        logger.warning("Falling back for company %s name: %s", company_id, e)
        return "Company"


# -----------------------------------------------------------------------------
# 1. Ratio Catalog Endpoint
# -----------------------------------------------------------------------------
@router.get(
    "/catalog",
    response_model=RatioCatalogResponse,
    summary="Get Financial Ratio Catalog",
    description="Lists all canonical financial ratios supported by the ATLAS registry.",
)
async def get_ratio_catalog(
    company_id: Annotated[uuid.UUID, Path(description="Company entity UUID")],
    category: Annotated[Optional[RatioCategory], Query(description="Optional ratio category filter")] = None,
    service: Annotated[CompanyRatiosService, Depends(get_ratios_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
    _: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))] = None,
) -> RatioCatalogResponse:
    return service.get_ratio_catalog(category=category)


# -----------------------------------------------------------------------------
# 2. Main Company Ratios Endpoint
# -----------------------------------------------------------------------------
@router.get(
    "",
    response_model=CompanyRatiosResponse,
    summary="Get Company Financial Ratios",
    description="Computes and qualifies financial ratios for a given company and reporting period.",
)
async def get_company_ratios(
    response: Response,
    company_id: Annotated[uuid.UUID, Path(description="Company entity UUID")],
    period_id: Annotated[str, Query(description="Reporting period ID (e.g. 'FY2024', 'Q4-2024')")] = "FY2024",
    period_type: Annotated[RatioPeriodType, Query(description="Period type (ANNUAL, QUARTERLY, TTM)")] = RatioPeriodType.ANNUAL,
    category: Annotated[Optional[RatioCategory], Query(description="Filter by ratio category")] = None,
    consolidation_scope: Annotated[ConsolidationScope, Query(description="Reporting scope")] = ConsolidationScope.CONSOLIDATED,
    service: Annotated[CompanyRatiosService, Depends(get_ratios_service)] = None,
    company_service: Annotated[CompanyService, Depends(get_company_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
    _: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))] = None,
) -> CompanyRatiosResponse:
    company_name = await _resolve_company_name(company_id, company_service)

    try:
        result = service.get_company_ratios(
            company_id=company_id,
            company_name=company_name,
            period_id=period_id,
            period_type=period_type,
            category=category,
            consolidation_scope=consolidation_scope,
        )
        response.headers["Cache-Control"] = "private, max-age=60"
        return result
    except RatioError as e:
        raise HTTPException(status_code=400, detail={"code": e.code, "message": e.message})


# -----------------------------------------------------------------------------
# 3. Ratio History Endpoint
# -----------------------------------------------------------------------------
@router.get(
    "/history",
    response_model=RatioHistoryResponse,
    summary="Get Ratio Historical Time Series",
    description="Retrieves chronological multi-period historical time series for a single financial ratio.",
)
async def get_company_ratio_history(
    company_id: Annotated[uuid.UUID, Path(description="Company entity UUID")],
    ratio_id: Annotated[str, Query(description="Canonical ratio ID (e.g. 'profitability.roe')")],
    period_type: Annotated[RatioPeriodType, Query(description="Period type (ANNUAL, QUARTERLY)")] = RatioPeriodType.ANNUAL,
    limit: Annotated[int, Query(ge=1, le=50, description="Max periods to retrieve")] = 10,
    service: Annotated[CompanyRatiosService, Depends(get_ratios_service)] = None,
    company_service: Annotated[CompanyService, Depends(get_company_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
    _: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))] = None,
) -> RatioHistoryResponse:
    company_name = await _resolve_company_name(company_id, company_service)

    try:
        return service.get_company_ratio_history(
            company_id=company_id,
            ratio_id=ratio_id,
            company_name=company_name,
            period_type=period_type,
            limit=limit,
        )
    except RatioNotFoundError as e:
        raise HTTPException(status_code=404, detail={"code": e.code, "message": e.message})
    except RatioError as e:
        raise HTTPException(status_code=400, detail={"code": e.code, "message": e.message})


# -----------------------------------------------------------------------------
# 4. Ratio Methodology Endpoint
# -----------------------------------------------------------------------------
@router.get(
    "/{ratio_id}/methodology",
    response_model=RatioMethodologyResponse,
    summary="Get Ratio Methodology",
    description="Inspects the exact formula, numerator, denominator, and policies for a financial ratio.",
)
async def get_ratio_methodology(
    company_id: Annotated[uuid.UUID, Path(description="Company entity UUID")],
    ratio_id: Annotated[str, Path(description="Canonical ratio ID")],
    service: Annotated[CompanyRatiosService, Depends(get_ratios_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
    _: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))] = None,
) -> RatioMethodologyResponse:
    try:
        return service.get_ratio_methodology(ratio_id=ratio_id)
    except RatioNotFoundError as e:
        raise HTTPException(status_code=404, detail={"code": e.code, "message": e.message})


# -----------------------------------------------------------------------------
# 5. Ratio Lineage Endpoint
# -----------------------------------------------------------------------------
@router.get(
    "/{ratio_id}/lineage",
    response_model=RatioLineageResponse,
    summary="Get Ratio Calculation Lineage",
    description="Returns underlying financial statement fact inputs and source references for a ratio calculation.",
)
async def get_ratio_lineage(
    company_id: Annotated[uuid.UUID, Path(description="Company entity UUID")],
    ratio_id: Annotated[str, Path(description="Canonical ratio ID")],
    period_id: Annotated[str, Query(description="Reporting period ID")] = "FY2024",
    service: Annotated[CompanyRatiosService, Depends(get_ratios_service)] = None,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)] = None,
    _: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))] = None,
) -> RatioLineageResponse:
    try:
        return service.get_ratio_lineage(
            company_id=company_id,
            ratio_id=ratio_id,
            period_id=period_id,
        )
    except RatioNotFoundError as e:
        raise HTTPException(status_code=404, detail={"code": e.code, "message": e.message})
    except RatioError as e:
        raise HTTPException(status_code=400, detail={"code": e.code, "message": e.message})
