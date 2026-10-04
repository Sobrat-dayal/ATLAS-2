import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.dependencies.database import get_db
from atlas.relationships.schemas import (
    RelationshipTypeResponse,
    EntityRelationshipResponse,
    EntityRelationshipCreate,
    EntityRelationshipListResponse,
)
from atlas.relationships.service import RelationshipService
import datetime

router = APIRouter(prefix="/api/v1", tags=["relationships"])

@router.get("/relationship-types", response_model=List[RelationshipTypeResponse])
async def list_relationship_types(
    db: AsyncSession = Depends(get_db)
):
    service = RelationshipService(db)
    return await service.get_all_system_types()


@router.get("/entities/{entity_id}/relationships", response_model=EntityRelationshipListResponse)
async def list_entity_relationships(
    entity_id: uuid.UUID,
    relationship_type_key: Optional[str] = Query(None),
    is_current: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    service = RelationshipService(db)
    try:
        items, total = await service.list_relationships(
            entity_id=entity_id,
            relationship_type_key=relationship_type_key,
            is_current=is_current,
            limit=limit,
            offset=offset
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    return EntityRelationshipListResponse(items=items, total=total)


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
