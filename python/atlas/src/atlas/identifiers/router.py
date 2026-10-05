import uuid
from typing import Annotated, List

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.identifiers.schemas import EntityIdentifierResponse, IdentifierSchemeResponse

from atlas.capabilities import CapabilityGateway, CapabilityRef, CapabilityExecutionContext
from atlas_api.capabilities_dependencies import get_capability_gateway, get_capability_execution_context

router = APIRouter(tags=["Identifiers"])

@router.get(
    "/api/v1/identifier-schemes",
    response_model=List[IdentifierSchemeResponse],
    summary="List Identifier Schemes",
    description="List all available identifier schemes.",
)
async def list_identifier_schemes(
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)],
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)],
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    return await gateway.execute(
        ref=CapabilityRef(key="identifier.scheme.list"),
        payload={},
        execution_context=context
    )


@router.get(
    "/api/v1/entities/{entity_id}/identifiers",
    response_model=List[EntityIdentifierResponse],
    summary="Get Entity Identifiers",
    description="Get identifiers for a specific entity.",
)
async def get_entity_identifiers(
    entity_id: uuid.UUID,
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)],
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)],
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    include_history: bool = Query(False, description="Include historical retired identifiers"),
):
    return await gateway.execute(
        ref=CapabilityRef(key="entity.identifiers.list"),
        payload={
            "entity_id": entity_id,
            "include_history": include_history
        },
        execution_context=context
    )
