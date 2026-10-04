import uuid
from typing import Annotated

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.companies.repository import CompanyRepository
from atlas.companies.schemas import CompanyResponse
from atlas.companies.service import CompanyService
from atlas.entities.service import EntityService
from fastapi import APIRouter, Depends, Path, Response
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from atlas_api.entities.dependencies import get_entity_service


def get_company_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
) -> CompanyService:
    return CompanyService(CompanyRepository(session), entity_service)


router = APIRouter(tags=["Companies"])


@router.get(
    "/companies/{entity_id}",
    response_model=CompanyResponse,
    summary="Get Company",
    description="Returns the stable company identity and profile data for a specific entity.",
)
async def get_company(
    entity_id: Annotated[uuid.UUID, Path(..., description="The unique entity ID of the company")],
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    response.headers["Cache-Control"] = "private, max-age=60"
    entity, company = await company_service.get_company(entity_id)

    return CompanyResponse(
        entity_id=entity.entity_id,
        entity_type=entity.entity_type,
        canonical_name=entity.canonical_name,
        display_name=entity.display_name,
        description=entity.description,
        legal_name=company.legal_name,
        short_name=company.short_name,
        organization_type=company.organization_type,
        status=company.status,
        founded_date=company.founded_date,
        website_url=company.website_url,
        primary_country_entity_id=company.primary_country_entity_id,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
