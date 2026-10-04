import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.dependencies import get_db_session
from atlas.provenance.service import ProvenanceService
from atlas.provenance.schemas import (
    ProvenanceSourceResponse,
    ProvenanceSourceListResponse,
    TargetProvenanceListResponse,
    ProvenanceLinkResponse,
    ProvenanceRecordResponse,
)
from atlas.provenance.errors import ProvenanceTargetNotFoundError

router = APIRouter(prefix="/provenance", tags=["provenance"])


def map_link_to_response(link, record, source) -> ProvenanceLinkResponse:
    return ProvenanceLinkResponse(
        provenance=ProvenanceRecordResponse(
            provenance_id=record.provenance_id,
            source=ProvenanceSourceResponse.model_validate(source),
            record_kind=record.record_kind,
            source_reference=record.source_reference,
            source_uri=record.source_uri,
            source_locator=record.source_locator,
            published_at=record.published_at,
            observed_at=record.observed_at,
            retrieved_at=record.retrieved_at,
            license_name=record.license_name,
            license_url=record.license_url,
            attribution_text=record.attribution_text,
            content_hash_sha256=record.content_hash_sha256,
            created_at=record.created_at,
        ),
        evidence_role=link.evidence_role,
        confidence_score=float(link.confidence_score) if link.confidence_score is not None else None,
    )


@router.get("/sources", response_model=ProvenanceSourceListResponse)
async def list_sources(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """List registered provenance sources."""
    service = ProvenanceService(session)
    items, total = await service.list_sources(limit=limit, offset=offset)
    return ProvenanceSourceListResponse(
        items=[ProvenanceSourceResponse.model_validate(item) for item in items],
        total=total
    )


@router.get("/entities/{entity_id}", response_model=TargetProvenanceListResponse)
async def get_entity_provenance(
    entity_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """Get provenance records supporting an entity."""
    service = ProvenanceService(session)
    try:
        items, total = await service.get_entity_provenance(entity_id, limit=limit, offset=offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    except ProvenanceTargetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/identifiers/{identifier_id}", response_model=TargetProvenanceListResponse)
async def get_identifier_provenance(
    identifier_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """Get provenance records supporting an identifier."""
    service = ProvenanceService(session)
    try:
        items, total = await service.get_identifier_provenance(identifier_id, limit=limit, offset=offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    except ProvenanceTargetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/aliases/{alias_id}", response_model=TargetProvenanceListResponse)
async def get_alias_provenance(
    alias_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """Get provenance records supporting an alias."""
    service = ProvenanceService(session)
    try:
        items, total = await service.get_alias_provenance(alias_id, limit=limit, offset=offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    except ProvenanceTargetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/relationships/{relationship_id}", response_model=TargetProvenanceListResponse)
async def get_relationship_provenance(
    relationship_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """Get provenance records supporting a relationship."""
    service = ProvenanceService(session)
    try:
        items, total = await service.get_relationship_provenance(relationship_id, limit=limit, offset=offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    except ProvenanceTargetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
