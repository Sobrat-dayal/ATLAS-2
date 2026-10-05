import uuid
from typing import Any
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.capabilities.context import CapabilityExecutionContext
from atlas.provenance.service import ProvenanceService
from atlas.provenance.schemas import (
    ProvenanceSourceListResponse,
    TargetProvenanceListResponse,
    ProvenanceLinkResponse,
    ProvenanceRecordResponse,
    ProvenanceSourceResponse,
)

class ProvenanceSourceListInput(BaseModel):
    limit: int = 50
    offset: int = 0
    model_config = ConfigDict(extra="forbid")

class EntityProvenanceListInput(BaseModel):
    entity_id: uuid.UUID
    limit: int = 50
    offset: int = 0
    model_config = ConfigDict(extra="forbid")

class IdentifierProvenanceListInput(BaseModel):
    identifier_id: uuid.UUID
    limit: int = 50
    offset: int = 0
    model_config = ConfigDict(extra="forbid")

class AliasProvenanceListInput(BaseModel):
    alias_id: uuid.UUID
    limit: int = 50
    offset: int = 0
    model_config = ConfigDict(extra="forbid")

class RelationshipProvenanceListInput(BaseModel):
    relationship_id: uuid.UUID
    limit: int = 50
    offset: int = 0
    model_config = ConfigDict(extra="forbid")

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

def provenance_source_list_factory(session: AsyncSession):
    service = ProvenanceService(session)
    async def handler(context: CapabilityExecutionContext, input_data: ProvenanceSourceListInput) -> ProvenanceSourceListResponse:
        items, total = await service.list_sources(limit=input_data.limit, offset=input_data.offset)
        return ProvenanceSourceListResponse(
            items=[ProvenanceSourceResponse.model_validate(item) for item in items],
            total=total
        )
    return handler

def entity_provenance_list_factory(session: AsyncSession):
    service = ProvenanceService(session)
    async def handler(context: CapabilityExecutionContext, input_data: EntityProvenanceListInput) -> TargetProvenanceListResponse:
        items, total = await service.get_entity_provenance(input_data.entity_id, limit=input_data.limit, offset=input_data.offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    return handler

def identifier_provenance_list_factory(session: AsyncSession):
    service = ProvenanceService(session)
    async def handler(context: CapabilityExecutionContext, input_data: IdentifierProvenanceListInput) -> TargetProvenanceListResponse:
        items, total = await service.get_identifier_provenance(input_data.identifier_id, limit=input_data.limit, offset=input_data.offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    return handler

def alias_provenance_list_factory(session: AsyncSession):
    service = ProvenanceService(session)
    async def handler(context: CapabilityExecutionContext, input_data: AliasProvenanceListInput) -> TargetProvenanceListResponse:
        items, total = await service.get_alias_provenance(input_data.alias_id, limit=input_data.limit, offset=input_data.offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    return handler

def relationship_provenance_list_factory(session: AsyncSession):
    service = ProvenanceService(session)
    async def handler(context: CapabilityExecutionContext, input_data: RelationshipProvenanceListInput) -> TargetProvenanceListResponse:
        items, total = await service.get_relationship_provenance(input_data.relationship_id, limit=input_data.limit, offset=input_data.offset)
        return TargetProvenanceListResponse(
            items=[map_link_to_response(l, r, s) for l, r, s in items],
            total=total
        )
    return handler
