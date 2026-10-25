import logging
import uuid
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.companies.repository import CompanyRepository
from atlas.companies.schemas import (
    CompanyClassification,
    CompanyFinancialSummary,
    CompanyGeography,
    CompanyIdentifierItem,
    CompanyIdentity,
    CompanyMarketSummary,
    CompanyOverviewResponse,
    CompanySearchResponse,
    PaginatedDocumentsResponse,
    PaginatedNewsResponse,
    PaginatedSecuritiesResponse,
)
from atlas.companies.service import CompanyService
from atlas.entities.service import EntityService
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import LiveQuoteStateStore
from fastapi import APIRouter, Depends, Path, Query, Request, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from atlas_api.entities.dependencies import get_entity_service

logger = logging.getLogger(__name__)


def get_company_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> CompanyService:
    return CompanyService(CompanyRepository(session), entity_service)


def get_live_quote_service(request: Request) -> Optional[LiveQuoteService]:
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            quote_store = LiveQuoteStateStore(redis_client)
            return LiveQuoteService(quote_store)
        except Exception as e:
            logger.warning("Could not instantiate LiveQuoteService from redis: %s", e)
            return None
    return None


router = APIRouter(tags=["Companies"])


# ---------------------------------------------------------------------------
# 1. Company Search & Discovery
# ---------------------------------------------------------------------------
@router.get(
    "/companies",
    response_model=CompanySearchResponse,
    summary="Search and Browse Companies",
    description="Search canonical companies by name, legal name, alias, identifier (LEI, CIK), or associated ticker symbol.",
)
async def search_companies(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    query: Annotated[Optional[str], Query(description="Search term (name, ticker, CIK, LEI, alias)")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    organization_type: Annotated[Optional[str], Query(description="Filter by organization type")] = None,
    status: Annotated[Optional[str], Query(description="Filter by status")] = None,
):
    response.headers["Cache-Control"] = "private, max-age=30"
    return await company_service.search_companies(
        query=query,
        page=page,
        page_size=page_size,
        organization_type=organization_type,
        status=status,
    )


# ---------------------------------------------------------------------------
# 2. Canonical Company Overview (Unified)
# ---------------------------------------------------------------------------
@router.get(
    "/companies/{entity_id}",
    response_model=CompanyOverviewResponse,
    summary="Get Canonical Company Overview",
    description="Returns the complete canonical Company Overview model, aggregating verified identity, profile, sector/industry, geography, identifiers, related securities, market context, financial summary, and references.",
)
async def get_company_overview(
    entity_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    request: Request,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    response.headers["Cache-Control"] = "private, max-age=60"
    quote_service = get_live_quote_service(request)

    # Entitlement evaluation: Basic ATLAS access entitles public profile & market data;
    # Check permissions if fundamental or research features are restricted
    is_fin_entitled = True
    is_news_entitled = True
    is_doc_entitled = True

    return await company_service.get_company_overview(
        entity_id=entity_id,
        quote_service=quote_service,
        is_financial_entitled=is_fin_entitled,
        is_news_entitled=is_news_entitled,
        is_doc_entitled=is_doc_entitled,
    )


# ---------------------------------------------------------------------------
# 3. Company Profile Sub-Resource
# ---------------------------------------------------------------------------
class CompanyProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_entity_id: uuid.UUID
    identity: CompanyIdentity
    description: Optional[str] = None
    classification: CompanyClassification
    geography: CompanyGeography
    identifiers: list[CompanyIdentifierItem]


@router.get(
    "/companies/{entity_id}/profile",
    response_model=CompanyProfileResponse,
    summary="Get Company Profile Details",
    description="Returns isolated company corporate profile including verified descriptions, legal identifiers, GICS classifications, and geographic information.",
)
async def get_company_profile(
    entity_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    response.headers["Cache-Control"] = "private, max-age=120"
    entity, company = await company_service.get_company(entity_id)

    aliases = await company_service.repository.get_company_aliases(entity_id)
    identifiers = await company_service.repository.get_company_identifiers(entity_id)
    geography = await company_service.repository.get_company_geography(company, entity)
    primary_ticker = await company_service.repository._resolve_primary_ticker(entity_id)
    classification = company_service.repository.get_company_classification(company, entity, primary_ticker)

    identity = CompanyIdentity(
        company_entity_id=company.entity_id,
        canonical_name=entity.canonical_name,
        display_name=entity.display_name,
        legal_name=company.legal_name,
        short_name=company.short_name,
        organization_type=company.organization_type,
        status=company.status,
        founded_date=company.founded_date,
        website_url=company.website_url,
        aliases=aliases,
    )

    return CompanyProfileResponse(
        company_entity_id=company.entity_id,
        identity=identity,
        description=entity.description,
        classification=classification,
        geography=geography,
        identifiers=identifiers,
    )


# ---------------------------------------------------------------------------
# 4. Related Securities Sub-Resource
# ---------------------------------------------------------------------------
@router.get(
    "/companies/{entity_id}/securities",
    response_model=PaginatedSecuritiesResponse,
    summary="Get Related Financial Instruments",
    description="Returns verified securities issued by this company (common equity, preferred, depositary receipts, corporate bonds) with share classes and qualified latest quotes.",
)
async def get_company_securities(
    entity_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    request: Request,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 25,
):
    response.headers["Cache-Control"] = "private, max-age=30"
    quote_service = get_live_quote_service(request)
    return await company_service.get_securities(
        entity_id=entity_id,
        page=page,
        page_size=page_size,
        quote_service=quote_service,
    )


# ---------------------------------------------------------------------------
# 5. Market Summary Sub-Resource
# ---------------------------------------------------------------------------
@router.get(
    "/companies/{entity_id}/market-summary",
    response_model=CompanyMarketSummary,
    summary="Get Company Market Summary",
    description="Returns qualified corporate market capitalization, primary reference security, and aggregate issuance counts.",
)
async def get_company_market_summary(
    entity_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    request: Request,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    response.headers["Cache-Control"] = "private, max-age=30"
    quote_service = get_live_quote_service(request)
    return await company_service.get_market_summary(
        entity_id=entity_id,
        quote_service=quote_service,
    )


# ---------------------------------------------------------------------------
# 6. Financial Summary Sub-Resource
# ---------------------------------------------------------------------------
@router.get(
    "/companies/{entity_id}/financial-summary",
    response_model=CompanyFinancialSummary,
    summary="Get High-Level Financial Summary",
    description="Returns verified high-level financial summary metrics (revenue, net income, assets, equity, EPS) from Stage 34 Fundamental Data.",
)
async def get_company_financial_summary(
    entity_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    response.headers["Cache-Control"] = "private, max-age=300"
    return await company_service.get_financial_summary(
        entity_id=entity_id,
        is_entitled=True,
    )


# ---------------------------------------------------------------------------
# 7. News References Sub-Resource
# ---------------------------------------------------------------------------
@router.get(
    "/companies/{entity_id}/news",
    response_model=PaginatedNewsResponse,
    summary="Get Relevant Corporate News",
    description="Returns verified news article references associated with the company or its issued financial instruments.",
)
async def get_company_news(
    entity_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=50, description="Items per page")] = 10,
):
    response.headers["Cache-Control"] = "private, max-age=60"
    return await company_service.get_news(
        entity_id=entity_id,
        page=page,
        page_size=page_size,
        is_entitled=True,
    )


# ---------------------------------------------------------------------------
# 8. Document References Sub-Resource
# ---------------------------------------------------------------------------
@router.get(
    "/companies/{entity_id}/documents",
    response_model=PaginatedDocumentsResponse,
    summary="Get Corporate Research & Filings Documents",
    description="Returns verified corporate filings, annual reports, and research document references.",
)
async def get_company_documents(
    entity_id: Annotated[uuid.UUID, Path(..., description="Canonical UUID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=50, description="Items per page")] = 10,
):
    response.headers["Cache-Control"] = "private, max-age=300"
    return await company_service.get_documents(
        entity_id=entity_id,
        page=page,
        page_size=page_size,
        is_entitled=True,
    )
