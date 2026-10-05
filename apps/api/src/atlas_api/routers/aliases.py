import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends
from atlas.capabilities import CapabilityGateway, CapabilityRef, CapabilityExecutionContext
from atlas_api.capabilities_dependencies import get_capability_gateway, get_capability_execution_context
from atlas.aliases.schemas import AliasTypeResponse, EntityAliasResponse

router = APIRouter(prefix="/aliases", tags=["Aliases"])


@router.get("/types", response_model=List[AliasTypeResponse])
async def list_alias_types(
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)],
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)],
):
    """
    Lists all supported alias types.
    """
    return await gateway.execute(
        ref=CapabilityRef(key="alias.type.list"),
        payload={},
        execution_context=context
    )


@router.get("/entities/{entity_id}", response_model=List[EntityAliasResponse])
async def get_entity_aliases(
    entity_id: uuid.UUID,
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)],
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)],
):
    """
    Lists all aliases for a given entity.
    """
    return await gateway.execute(
        ref=CapabilityRef(key="entity.aliases.list"),
        payload={"entity_id": entity_id},
        execution_context=context
    )
