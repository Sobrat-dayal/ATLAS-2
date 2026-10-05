import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from atlas.capabilities import CapabilityGateway, CapabilityRef, CapabilityExecutionContext
from atlas_api.capabilities_dependencies import get_capability_gateway, get_capability_execution_context
from .schemas import EntityResponse, EntityTypeListResponse

router = APIRouter(tags=["Entities"])


@router.get("/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: uuid.UUID,
    response: Response,
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)],
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)],
):
    """
    Get a universal entity by its ID.
    """
    response.headers["Cache-Control"] = "private, max-age=60"
    
    result = await gateway.execute(
        ref=CapabilityRef(key="entity.get"),
        payload={"entity_id": entity_id},
        execution_context=context
    )
    return result


@router.get("/entity-types", response_model=EntityTypeListResponse)
async def list_entity_types(
    response: Response,
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)],
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)],
):
    """
    List all supported canonical entity types.
    """
    response.headers["Cache-Control"] = "public, max-age=3600"
    
    result = await gateway.execute(
        ref=CapabilityRef(key="entity.type.list"),
        payload={},
        execution_context=context
    )
    return result
