"""FastAPI Router for Company Financial Statements (Stage 82).

Endpoints:
- GET /companies/{company_id}/statements/catalog
- GET /companies/{company_id}/statements/income
- GET /companies/{company_id}/statements/balance-sheet
- GET /companies/{company_id}/statements/cash-flow
- GET /companies/{company_id}/statements/{statement_type}
- GET /companies/{company_id}/statements/{statement_type}/sources
"""

import logging
import uuid
from typing import Annotated, List, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.companies.errors import CompanyNotFoundError
from atlas.companies.service import CompanyService
from atlas.companies.statements.enums import (
    ComparisonMode,
    ConsolidationScope,
    RevisionPolicy,
    ScaleType,
    StatementPeriodType,
    StatementType,
)
from atlas.companies.statements.repository import CompanyStatementsRepository
from atlas.companies.statements.schemas import (
    FinancialStatementResponse,
    StatementCatalogResponse,
)
from atlas.companies.statements.service import CompanyStatementsService
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from atlas_api.routers.companies import get_company_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies/{company_id}/statements", tags=["Company Financial Statements"])


def get_statements_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CompanyStatementsService:
    repository = CompanyStatementsRepository(session=session)
    return CompanyStatementsService(repository=repository)


class StatementSourceMetadataDTO(BaseModel):
    statement_type: StatementType
    period_id: str
    filing_name: Optional[str] = None
    source_document_id: Optional[uuid.UUID] = None
    source_revision: Optional[str] = None
    is_restated: bool = False
    is_derived: bool = False
    derivation_lineage: List[str] = Field(default_factory=list)
    accounting_standard: str
    reporting_currency: str

    model_config = ConfigDict(from_attributes=True)


class StatementSourcesResponse(BaseModel):
    company_id: uuid.UUID
    statement_type: StatementType
    sources: List[StatementSourceMetadataDTO]

async def _resolve_company_name(company_service: CompanyService, company_id: uuid.UUID) -> str:
    res = await company_service.get_company(company_id)
    if not res:
        raise CompanyNotFoundError(str(company_id))
    if isinstance(res, tuple):
        entity, company = res
        return getattr(entity, "display_name", None) or getattr(company, "legal_name", None) or "Company"
    return getattr(res, "display_name", None) or getattr(res, "legal_name", None) or "Company"


# ---------------------------------------------------------------------------
# 1. Statement Catalog
# ---------------------------------------------------------------------------
@router.get(
    "/catalog",
    response_model=StatementCatalogResponse,
    summary="Get Financial Statement Catalog",
    description="Returns available statement types, fiscal years, quarters, scopes, and supported reporting currencies.",
)
async def get_statement_catalog(
    company_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    statements_service: Annotated[CompanyStatementsService, Depends(get_statements_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    consolidation_scope: Annotated[
        ConsolidationScope,
        Query(description="Consolidation scope (consolidated or standalone)"),
    ] = ConsolidationScope.CONSOLIDATED,
):
    response.headers["Cache-Control"] = "private, max-age=60"
    company = await company_service.get_company(company_id)
    if not company:
        raise CompanyNotFoundError(str(company_id))

    return await statements_service.get_statement_catalog(
        company_id=company_id,
        consolidation_scope=consolidation_scope,
    )


# ---------------------------------------------------------------------------
# 2. Income Statement
# ---------------------------------------------------------------------------
@router.get(
    "/income",
    response_model=FinancialStatementResponse,
    summary="Get Income Statement",
    description="Returns normalized, multi-period Income Statement with exact Decimal precision and taxonomy hierarchy.",
)
async def get_income_statement(
    company_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    statements_service: Annotated[CompanyStatementsService, Depends(get_statements_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    period_type: Annotated[
        StatementPeriodType,
        Query(description="Period type: annual, quarterly, or ttm"),
    ] = StatementPeriodType.ANNUAL,
    consolidation_scope: Annotated[
        ConsolidationScope,
        Query(description="Consolidated or standalone"),
    ] = ConsolidationScope.CONSOLIDATED,
    scale: Annotated[
        ScaleType,
        Query(description="Display numerical scale (auto, billions, millions, thousands, original)"),
    ] = ScaleType.MILLIONS,
    comparison_mode: Annotated[
        ComparisonMode,
        Query(description="Comparison mode: none, yoy_absolute, yoy_percent, qoq_absolute, qoq_percent, common_size"),
    ] = ComparisonMode.NONE,
    revision_policy: Annotated[
        RevisionPolicy,
        Query(description="Revision policy: latest or original"),
    ] = RevisionPolicy.LATEST,
    fiscal_year_from: Annotated[Optional[int], Query(description="Start fiscal year filter")] = None,
    fiscal_year_to: Annotated[Optional[int], Query(description="End fiscal year filter")] = None,
    max_periods: Annotated[int, Query(ge=1, le=20, description="Max periods to return")] = 5,
):
    response.headers["Cache-Control"] = "private, max-age=60"
    company_name = await _resolve_company_name(company_service, company_id)

    return await statements_service.get_financial_statement(
        company_id=company_id,
        statement_type=StatementType.INCOME_STATEMENT,
        period_type=period_type,
        consolidation_scope=consolidation_scope,
        scale=scale,
        comparison_mode=comparison_mode,
        revision_policy=revision_policy,
        fiscal_year_from=fiscal_year_from,
        fiscal_year_to=fiscal_year_to,
        max_periods=max_periods,
        company_name=company_name,
    )


# ---------------------------------------------------------------------------
# 3. Balance Sheet
# ---------------------------------------------------------------------------
@router.get(
    "/balance-sheet",
    response_model=FinancialStatementResponse,
    summary="Get Balance Sheet",
    description="Returns point-in-time stock balances and Assets = Liabilities + Equity diagnostics.",
)
async def get_balance_sheet(
    company_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    statements_service: Annotated[CompanyStatementsService, Depends(get_statements_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    period_type: Annotated[
        StatementPeriodType,
        Query(description="Period type: annual or quarterly (TTM is invalid for stock balances)"),
    ] = StatementPeriodType.ANNUAL,
    consolidation_scope: Annotated[
        ConsolidationScope,
        Query(description="Consolidated or standalone"),
    ] = ConsolidationScope.CONSOLIDATED,
    scale: Annotated[
        ScaleType,
        Query(description="Display numerical scale"),
    ] = ScaleType.MILLIONS,
    comparison_mode: Annotated[
        ComparisonMode,
        Query(description="Comparison mode: none, yoy_absolute, yoy_percent, qoq_absolute, qoq_percent, common_size"),
    ] = ComparisonMode.NONE,
    revision_policy: Annotated[
        RevisionPolicy,
        Query(description="Revision policy: latest or original"),
    ] = RevisionPolicy.LATEST,
    fiscal_year_from: Annotated[Optional[int], Query(description="Start fiscal year filter")] = None,
    fiscal_year_to: Annotated[Optional[int], Query(description="End fiscal year filter")] = None,
    max_periods: Annotated[int, Query(ge=1, le=20, description="Max periods to return")] = 5,
):
    response.headers["Cache-Control"] = "private, max-age=60"
    if period_type == StatementPeriodType.TTM:
        raise HTTPException(
            status_code=400,
            detail="TTM summation is mathematically invalid for Balance Sheet stock balances.",
        )

    company_name = await _resolve_company_name(company_service, company_id)

    return await statements_service.get_financial_statement(
        company_id=company_id,
        statement_type=StatementType.BALANCE_SHEET,
        period_type=period_type,
        consolidation_scope=consolidation_scope,
        scale=scale,
        comparison_mode=comparison_mode,
        revision_policy=revision_policy,
        fiscal_year_from=fiscal_year_from,
        fiscal_year_to=fiscal_year_to,
        max_periods=max_periods,
        company_name=company_name,
    )


# ---------------------------------------------------------------------------
# 4. Cash Flow Statement
# ---------------------------------------------------------------------------
@router.get(
    "/cash-flow",
    response_model=FinancialStatementResponse,
    summary="Get Cash Flow Statement",
    description="Returns operating, investing, and financing cash flows with cash reconciliation diagnostics.",
)
async def get_cash_flow_statement(
    company_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    statements_service: Annotated[CompanyStatementsService, Depends(get_statements_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    period_type: Annotated[
        StatementPeriodType,
        Query(description="Period type: annual, quarterly, or ttm"),
    ] = StatementPeriodType.ANNUAL,
    consolidation_scope: Annotated[
        ConsolidationScope,
        Query(description="Consolidated or standalone"),
    ] = ConsolidationScope.CONSOLIDATED,
    scale: Annotated[
        ScaleType,
        Query(description="Display numerical scale"),
    ] = ScaleType.MILLIONS,
    comparison_mode: Annotated[
        ComparisonMode,
        Query(description="Comparison mode: none, yoy_absolute, yoy_percent, qoq_absolute, qoq_percent"),
    ] = ComparisonMode.NONE,
    revision_policy: Annotated[
        RevisionPolicy,
        Query(description="Revision policy: latest or original"),
    ] = RevisionPolicy.LATEST,
    fiscal_year_from: Annotated[Optional[int], Query(description="Start fiscal year filter")] = None,
    fiscal_year_to: Annotated[Optional[int], Query(description="End fiscal year filter")] = None,
    max_periods: Annotated[int, Query(ge=1, le=20, description="Max periods to return")] = 5,
):
    response.headers["Cache-Control"] = "private, max-age=60"
    company_name = await _resolve_company_name(company_service, company_id)

    return await statements_service.get_financial_statement(
        company_id=company_id,
        statement_type=StatementType.CASH_FLOW_STATEMENT,
        period_type=period_type,
        consolidation_scope=consolidation_scope,
        scale=scale,
        comparison_mode=comparison_mode,
        revision_policy=revision_policy,
        fiscal_year_from=fiscal_year_from,
        fiscal_year_to=fiscal_year_to,
        max_periods=max_periods,
        company_name=company_name,
    )


# ---------------------------------------------------------------------------
# 5. Generic Statement by Type
# ---------------------------------------------------------------------------
@router.get(
    "/{statement_type}",
    response_model=FinancialStatementResponse,
    summary="Get Financial Statement by Type",
    description="Returns financial statement for the specified type (income_statement, balance_sheet, cash_flow_statement).",
)
async def get_statement_by_type(
    company_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    statement_type: Annotated[StatementType, Path(..., description="Statement type")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    statements_service: Annotated[CompanyStatementsService, Depends(get_statements_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    period_type: Annotated[StatementPeriodType, Query()] = StatementPeriodType.ANNUAL,
    consolidation_scope: Annotated[ConsolidationScope, Query()] = ConsolidationScope.CONSOLIDATED,
    scale: Annotated[ScaleType, Query()] = ScaleType.MILLIONS,
    comparison_mode: Annotated[ComparisonMode, Query()] = ComparisonMode.NONE,
    revision_policy: Annotated[RevisionPolicy, Query()] = RevisionPolicy.LATEST,
    fiscal_year_from: Annotated[Optional[int], Query()] = None,
    fiscal_year_to: Annotated[Optional[int], Query()] = None,
    max_periods: Annotated[int, Query(ge=1, le=20)] = 5,
):
    response.headers["Cache-Control"] = "private, max-age=60"
    if statement_type == StatementType.BALANCE_SHEET and period_type == StatementPeriodType.TTM:
        raise HTTPException(
            status_code=400,
            detail="TTM summation is mathematically invalid for Balance Sheet stock balances.",
        )

    company_name = await _resolve_company_name(company_service, company_id)

    return await statements_service.get_financial_statement(
        company_id=company_id,
        statement_type=statement_type,
        period_type=period_type,
        consolidation_scope=consolidation_scope,
        scale=scale,
        comparison_mode=comparison_mode,
        revision_policy=revision_policy,
        fiscal_year_from=fiscal_year_from,
        fiscal_year_to=fiscal_year_to,
        max_periods=max_periods,
        company_name=company_name,
    )


# ---------------------------------------------------------------------------
# 6. Statement Sources & Provenance Sub-Resource
# ---------------------------------------------------------------------------
@router.get(
    "/{statement_type}/sources",
    response_model=StatementSourcesResponse,
    summary="Get Financial Statement Sources & Provenance",
    description="Returns verified source document references, filing timestamps, and revision lineages.",
)
async def get_statement_sources(
    company_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    statement_type: Annotated[StatementType, Path(..., description="Statement type")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    statements_service: Annotated[CompanyStatementsService, Depends(get_statements_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    consolidation_scope: Annotated[ConsolidationScope, Query()] = ConsolidationScope.CONSOLIDATED,
):
    response.headers["Cache-Control"] = "private, max-age=300"
    _ = await _resolve_company_name(company_service, company_id)

    periods = statements_service.repository.get_statement_periods(
        company_id=company_id,
        statement_type=statement_type,
        period_type=None,
        consolidation_scope=consolidation_scope,
        max_periods=20,
    )

    sources_dto = [
        StatementSourceMetadataDTO(
            statement_type=statement_type,
            period_id=p["period_id"],
            filing_name=p.get("source_filing_name"),
            source_document_id=p.get("source_document_id"),
            source_revision=p.get("revision_id"),
            is_restated=p.get("is_restated", False),
            is_derived=p.get("is_derived", False),
            derivation_lineage=p.get("derivation_lineage", []),
            accounting_standard=str(p.get("accounting_standard", "US_GAAP")),
            reporting_currency=str(p.get("reporting_currency", "USD")),
        )
        for p in periods
    ]

    return StatementSourcesResponse(
        company_id=company_id,
        statement_type=statement_type,
        sources=sources_dto,
    )
