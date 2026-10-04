import datetime
import uuid
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.repository import EntityRepository
from atlas.identifiers.repository import IdentifierRepository
from atlas.aliases.repository import AliasRepository
from atlas.relationships.repository import RelationshipRepository

from .models import (
    ProvenanceSource,
    ProvenanceRecord,
    EntityProvenanceLink,
    IdentifierProvenanceLink,
    AliasProvenanceLink,
    RelationshipProvenanceLink,
)
from .repository import ProvenanceSourceRepository, ProvenanceRepository
from .types import ProvenanceSourceKind, ProvenanceRecordKind, EvidenceRole
from .errors import (
    ProvenanceSourceNotFoundError,
    ProvenanceSourceConflictError,
    ProvenanceNotFoundError,
    ProvenanceTargetNotFoundError,
    InvalidProvenanceConfidenceError,
    InvalidEvidenceRoleError,
)
from .validation import validate_source_key, validate_url, validate_content_hash


class ProvenanceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.source_repo = ProvenanceSourceRepository(session)
        self.prov_repo = ProvenanceRepository(session)
        
        self.entity_repo = EntityRepository(session)
        self.identifier_repo = IdentifierRepository(session)
        self.alias_repo = AliasRepository(session)
        self.relationship_repo = RelationshipRepository(session)

    async def list_sources(self, limit: int = 50, offset: int = 0) -> Tuple[List[ProvenanceSource], int]:
        return await self.source_repo.list_sources(limit, offset)

    async def get_provenance_record(self, provenance_id: uuid.UUID) -> Tuple[ProvenanceRecord, ProvenanceSource]:
        record_tuple = await self.prov_repo.get_record_with_source(provenance_id)
        if not record_tuple:
            raise ProvenanceNotFoundError(f"Provenance record {provenance_id} not found")
        return record_tuple

    async def create_source(
        self,
        name: str,
        source_kind: str,
        source_key: Optional[str] = None,
        base_url: Optional[str] = None,
        is_system: bool = False
    ) -> ProvenanceSource:
        
        try:
            ProvenanceSourceKind(source_kind)
        except ValueError:
            raise ValueError(f"Invalid source kind: {source_kind}")

        source_key = validate_source_key(source_key)
        base_url = validate_url(base_url)

        if source_key:
            existing = await self.source_repo.get_source_by_key(source_key)
            if existing:
                if existing.source_kind != source_kind or existing.base_url != base_url:
                    raise ProvenanceSourceConflictError(f"Source with key {source_key} exists but with different metadata")
                return existing

        new_source = ProvenanceSource(
            source_key=source_key,
            name=name,
            source_kind=source_kind,
            base_url=base_url,
            is_system=is_system
        )
        return await self.source_repo.create_source(new_source)

    async def create_provenance_record(
        self,
        source_id: uuid.UUID,
        record_kind: str,
        source_reference: Optional[str] = None,
        source_uri: Optional[str] = None,
        source_locator: Optional[str] = None,
        published_at: Optional[datetime.datetime] = None,
        observed_at: Optional[datetime.datetime] = None,
        retrieved_at: Optional[datetime.datetime] = None,
        license_name: Optional[str] = None,
        license_url: Optional[str] = None,
        attribution_text: Optional[str] = None,
        content_hash_sha256: Optional[str] = None
    ) -> ProvenanceRecord:
        
        try:
            ProvenanceRecordKind(record_kind)
        except ValueError:
            raise ValueError(f"Invalid record kind: {record_kind}")

        source = await self.source_repo.get_source(source_id)
        if not source:
            raise ProvenanceSourceNotFoundError(f"Source {source_id} not found")

        source_uri = validate_url(source_uri)
        license_url = validate_url(license_url)
        content_hash_sha256 = validate_content_hash(content_hash_sha256)

        if retrieved_at is None:
            retrieved_at = datetime.datetime.now(datetime.timezone.utc)

        record = ProvenanceRecord(
            source_id=source_id,
            record_kind=record_kind,
            source_reference=source_reference.strip() if source_reference else None,
            source_uri=source_uri,
            source_locator=source_locator.strip() if source_locator else None,
            published_at=published_at,
            observed_at=observed_at,
            retrieved_at=retrieved_at,
            license_name=license_name,
            license_url=license_url,
            attribution_text=attribution_text,
            content_hash_sha256=content_hash_sha256
        )

        return await self.prov_repo.create_record(record)

    def _validate_link_metadata(self, evidence_role: str, confidence_score: Optional[float]):
        try:
            EvidenceRole(evidence_role)
        except ValueError:
            raise InvalidEvidenceRoleError(f"Invalid evidence role: {evidence_role}")

        if confidence_score is not None:
            if not (0.0 <= confidence_score <= 1.0):
                raise InvalidProvenanceConfidenceError("Confidence score must be between 0.0 and 1.0")

    async def link_entity_provenance(
        self,
        entity_id: uuid.UUID,
        provenance_id: uuid.UUID,
        evidence_role: str = EvidenceRole.SUPPORTS.value,
        confidence_score: Optional[float] = None
    ) -> EntityProvenanceLink:
        
        self._validate_link_metadata(evidence_role, confidence_score)
        
        entity = await self.entity_repo.get_entity(entity_id)
        if not entity:
            raise ProvenanceTargetNotFoundError(f"Entity {entity_id} not found")
            
        record = await self.prov_repo.get_record(provenance_id)
        if not record:
            raise ProvenanceNotFoundError(f"Provenance record {provenance_id} not found")

        link = EntityProvenanceLink(
            entity_id=entity_id,
            provenance_id=provenance_id,
            evidence_role=evidence_role,
            confidence_score=confidence_score
        )
        return await self.prov_repo.link_entity(link)

    async def link_identifier_provenance(
        self,
        identifier_id: uuid.UUID,
        provenance_id: uuid.UUID,
        evidence_role: str = EvidenceRole.SUPPORTS.value,
        confidence_score: Optional[float] = None
    ) -> IdentifierProvenanceLink:
        
        self._validate_link_metadata(evidence_role, confidence_score)
        
        identifier = await self.identifier_repo.get_identifier(identifier_id)
        if not identifier:
            raise ProvenanceTargetNotFoundError(f"Identifier {identifier_id} not found")
            
        record = await self.prov_repo.get_record(provenance_id)
        if not record:
            raise ProvenanceNotFoundError(f"Provenance record {provenance_id} not found")

        link = IdentifierProvenanceLink(
            identifier_id=identifier_id,
            provenance_id=provenance_id,
            evidence_role=evidence_role,
            confidence_score=confidence_score
        )
        return await self.prov_repo.link_identifier(link)

    async def link_alias_provenance(
        self,
        alias_id: uuid.UUID,
        provenance_id: uuid.UUID,
        evidence_role: str = EvidenceRole.SUPPORTS.value,
        confidence_score: Optional[float] = None
    ) -> AliasProvenanceLink:
        
        self._validate_link_metadata(evidence_role, confidence_score)
        
        alias = await self.alias_repo.get_alias(alias_id)
        if not alias:
            raise ProvenanceTargetNotFoundError(f"Alias {alias_id} not found")
            
        record = await self.prov_repo.get_record(provenance_id)
        if not record:
            raise ProvenanceNotFoundError(f"Provenance record {provenance_id} not found")

        link = AliasProvenanceLink(
            alias_id=alias_id,
            provenance_id=provenance_id,
            evidence_role=evidence_role,
            confidence_score=confidence_score
        )
        return await self.prov_repo.link_alias(link)

    async def link_relationship_provenance(
        self,
        relationship_id: uuid.UUID,
        provenance_id: uuid.UUID,
        evidence_role: str = EvidenceRole.SUPPORTS.value,
        confidence_score: Optional[float] = None
    ) -> RelationshipProvenanceLink:
        
        self._validate_link_metadata(evidence_role, confidence_score)
        
        relationship = await self.relationship_repo.get_relationship(relationship_id)
        if not relationship:
            raise ProvenanceTargetNotFoundError(f"Relationship {relationship_id} not found")
            
        record = await self.prov_repo.get_record(provenance_id)
        if not record:
            raise ProvenanceNotFoundError(f"Provenance record {provenance_id} not found")

        link = RelationshipProvenanceLink(
            relationship_id=relationship_id,
            provenance_id=provenance_id,
            evidence_role=evidence_role,
            confidence_score=confidence_score
        )
        return await self.prov_repo.link_relationship(link)

    async def get_entity_provenance(self, entity_id: uuid.UUID, limit: int = 50, offset: int = 0):
        if not await self.entity_repo.get_entity(entity_id):
            raise ProvenanceTargetNotFoundError("Entity not found")
        return await self.prov_repo.get_entity_provenance(entity_id, limit, offset)

    async def get_identifier_provenance(self, identifier_id: uuid.UUID, limit: int = 50, offset: int = 0):
        if not await self.identifier_repo.get_identifier(identifier_id):
            raise ProvenanceTargetNotFoundError("Identifier not found")
        return await self.prov_repo.get_identifier_provenance(identifier_id, limit, offset)

    async def get_alias_provenance(self, alias_id: uuid.UUID, limit: int = 50, offset: int = 0):
        if not await self.alias_repo.get_alias(alias_id):
            raise ProvenanceTargetNotFoundError("Alias not found")
        return await self.prov_repo.get_alias_provenance(alias_id, limit, offset)

    async def get_relationship_provenance(self, relationship_id: uuid.UUID, limit: int = 50, offset: int = 0):
        if not await self.relationship_repo.get_relationship(relationship_id):
            raise ProvenanceTargetNotFoundError("Relationship not found")
        return await self.prov_repo.get_relationship_provenance(relationship_id, limit, offset)
