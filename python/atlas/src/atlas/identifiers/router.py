import uuid
from typing import Annotated, List

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from atlas_api.entities.dependencies import get_entity_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.entities.service import EntityService
from atlas.identifiers.schemas import EntityIdentifierResponse, IdentifierSchemeResponse
from atlas.identifiers.service import IdentifierService


def get_identifier_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IdentifierService:
    return IdentifierService(session)


router = APIRouter(tags=["Identifiers"])

@router.get(
    "/api/v1/identifier-schemes",
    response_model=List[IdentifierSchemeResponse],
    summary="List Identifier Schemes",
    description="List all available identifier schemes.",
)
async def list_identifier_schemes(
    identifier_service: Annotated[IdentifierService, Depends(get_identifier_service)],
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    return await identifier_service.list_identifier_schemes()


@router.get(
    "/api/v1/entities/{entity_id}/identifiers",
    response_model=List[EntityIdentifierResponse],
    summary="Get Entity Identifiers",
    description="Get identifiers for a specific entity.",
)
async def get_entity_identifiers(
    entity_id: uuid.UUID,
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    identifier_service: Annotated[IdentifierService, Depends(get_identifier_service)],
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    include_history: bool = Query(False, description="Include historical retired identifiers"),
):
    entity = await entity_service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        
    return await identifier_service.get_entity_identifiers(entity_id, include_history)
