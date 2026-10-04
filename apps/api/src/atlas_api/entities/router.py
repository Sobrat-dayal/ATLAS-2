import uuid
from typing import Annotated

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.entities import EntityService
from fastapi import APIRouter, Depends, Response

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission

from .dependencies import get_entity_service
from .schemas import EntityResponse, EntityTypeListResponse

router = APIRouter(tags=["Entities"])


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[EntityService, Depends(get_entity_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    """
    Get a universal entity by its ID.
    """
    response.headers["Cache-Control"] = "private, max-age=60"
    entity = await service.get_entity(entity_id)
    return entity


@router.get("/entity-types", response_model=EntityTypeListResponse)
async def list_entity_types(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[EntityService, Depends(get_entity_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    """
    List all supported canonical entity types.
    """
    response.headers["Cache-Control"] = "public, max-age=3600"
    types = await service.list_entity_types()
    return EntityTypeListResponse(types=types)
