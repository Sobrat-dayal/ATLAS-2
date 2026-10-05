import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.capabilities import CapabilityGateway, CapabilityRef, CapabilityExecutionContext
from atlas_api.capabilities_dependencies import get_capability_gateway, get_capability_execution_context
from atlas_api.dependencies import get_db_session
from atlas.provenance.schemas import (
    ProvenanceSourceListResponse,
    TargetProvenanceListResponse,
)

router = APIRouter(prefix="/provenance", tags=["provenance"])

@router.get("/sources", response_model=ProvenanceSourceListResponse)
async def list_sources(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)] = None,
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)] = None,
):
    """List registered provenance sources."""
    return await gateway.execute(
        ref=CapabilityRef(key="provenance.source.list"),
        payload={"limit": limit, "offset": offset},
        execution_context=context
    )


@router.get("/entities/{entity_id}", response_model=TargetProvenanceListResponse)
async def get_entity_provenance(
    entity_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)] = None,
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)] = None,
):
    """Get provenance records supporting an entity."""
    try:
        return await gateway.execute(
            ref=CapabilityRef(key="entity.provenance.list"),
            payload={"entity_id": entity_id, "limit": limit, "offset": offset},
            execution_context=context
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/identifiers/{identifier_id}", response_model=TargetProvenanceListResponse)
async def get_identifier_provenance(
    identifier_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)] = None,
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)] = None,
):
    """Get provenance records supporting an identifier."""
    try:
        return await gateway.execute(
            ref=CapabilityRef(key="identifier.provenance.list"),
            payload={"identifier_id": identifier_id, "limit": limit, "offset": offset},
            execution_context=context
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/aliases/{alias_id}", response_model=TargetProvenanceListResponse)
async def get_alias_provenance(
    alias_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)] = None,
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)] = None,
):
    """Get provenance records supporting an alias."""
    try:
        return await gateway.execute(
            ref=CapabilityRef(key="alias.provenance.list"),
            payload={"alias_id": alias_id, "limit": limit, "offset": offset},
            execution_context=context
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/relationships/{relationship_id}", response_model=TargetProvenanceListResponse)
async def get_relationship_provenance(
    relationship_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)] = None,
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)] = None,
):
    """Get provenance records supporting a relationship."""
    try:
        return await gateway.execute(
            ref=CapabilityRef(key="relationship.provenance.list"),
            payload={"relationship_id": relationship_id, "limit": limit, "offset": offset},
            execution_context=context
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
