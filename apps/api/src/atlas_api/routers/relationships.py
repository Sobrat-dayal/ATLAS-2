import uuid
from typing import List, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.capabilities import CapabilityGateway, CapabilityRef, CapabilityExecutionContext
from atlas_api.capabilities_dependencies import get_capability_gateway, get_capability_execution_context
from atlas_api.dependencies.database import get_db
from atlas.relationships.schemas import (
    RelationshipTypeResponse,
    EntityRelationshipResponse,
    EntityRelationshipCreate,
    EntityRelationshipListResponse,
)
from atlas.relationships.service import RelationshipService

router = APIRouter(prefix="/api/v1", tags=["relationships"])

@router.get("/relationship-types", response_model=List[RelationshipTypeResponse])
async def list_relationship_types(
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)],
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)],
):
    return await gateway.execute(
        ref=CapabilityRef(key="relationship.type.list"),
        payload={},
        execution_context=context
    )


@router.get("/entities/{entity_id}/relationships", response_model=EntityRelationshipListResponse)
async def list_entity_relationships(
    entity_id: uuid.UUID,
    relationship_type_key: Optional[str] = Query(None),
    is_current: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)] = None,
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)] = None,
):
    try:
        return await gateway.execute(
            ref=CapabilityRef(key="entity.relationships.list"),
            payload={
                "entity_id": entity_id,
                "relationship_type_key": relationship_type_key,
                "is_current": is_current,
                "limit": limit,
                "offset": offset
            },
            execution_context=context
        )
    except Exception as e:
        # Note: capability exception handler should ideally throw HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/entities/{entity_id}/relationships", response_model=EntityRelationshipResponse, status_code=201)
async def create_entity_relationship(
    entity_id: uuid.UUID,
    data: EntityRelationshipCreate,
    db: AsyncSession = Depends(get_db)
):
    service = RelationshipService(db)
    try:
        rel = await service.create_relationship(entity_id, data)
        await db.commit()
        return rel
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
