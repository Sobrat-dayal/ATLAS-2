import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from .models import (
    ProvenanceSource,
    ProvenanceRecord,
    EntityProvenanceLink,
    IdentifierProvenanceLink,
    AliasProvenanceLink,
    RelationshipProvenanceLink,
)


class ProvenanceSourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_source(self, source_id: uuid.UUID) -> Optional[ProvenanceSource]:
        stmt = select(ProvenanceSource).where(ProvenanceSource.source_id == source_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_source_by_key(self, source_key: str) -> Optional[ProvenanceSource]:
        stmt = select(ProvenanceSource).where(ProvenanceSource.source_key == source_key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_sources(self, limit: int = 50, offset: int = 0) -> Tuple[List[ProvenanceSource], int]:
        count_stmt = select(func.count(ProvenanceSource.source_id))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = select(ProvenanceSource).order_by(ProvenanceSource.name, ProvenanceSource.source_id).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total

    async def create_source(self, source: ProvenanceSource) -> ProvenanceSource:
        self.session.add(source)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Integrity error when creating source (possibly duplicate key).")
        return source


class ProvenanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_record(self, provenance_id: uuid.UUID) -> Optional[ProvenanceRecord]:
        stmt = select(ProvenanceRecord).where(ProvenanceRecord.provenance_id == provenance_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_record_with_source(self, provenance_id: uuid.UUID) -> Optional[Tuple[ProvenanceRecord, ProvenanceSource]]:
        stmt = (
            select(ProvenanceRecord, ProvenanceSource)
            .join(ProvenanceSource, ProvenanceRecord.source_id == ProvenanceSource.source_id)
            .where(ProvenanceRecord.provenance_id == provenance_id)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if row:
            return row[0], row[1]
        return None

    async def create_record(self, record: ProvenanceRecord) -> ProvenanceRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def _get_target_provenance(self, model, target_col, target_id: uuid.UUID, limit: int, offset: int):
        count_stmt = select(func.count(model.provenance_id)).where(target_col == target_id)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(model, ProvenanceRecord, ProvenanceSource)
            .join(ProvenanceRecord, model.provenance_id == ProvenanceRecord.provenance_id)
            .join(ProvenanceSource, ProvenanceRecord.source_id == ProvenanceSource.source_id)
            .where(target_col == target_id)
            .order_by(ProvenanceRecord.retrieved_at.desc(), ProvenanceRecord.provenance_id)
            .limit(limit)
            .offset(offset)
        )
        
        items = []
        result = await self.session.execute(stmt)
        for link, rec, src in result:
            items.append((link, rec, src))
            
        return items, total

    async def get_entity_provenance(self, entity_id: uuid.UUID, limit: int = 50, offset: int = 0):
        return await self._get_target_provenance(EntityProvenanceLink, EntityProvenanceLink.entity_id, entity_id, limit, offset)

    async def get_identifier_provenance(self, identifier_id: uuid.UUID, limit: int = 50, offset: int = 0):
        return await self._get_target_provenance(IdentifierProvenanceLink, IdentifierProvenanceLink.identifier_id, identifier_id, limit, offset)

    async def get_alias_provenance(self, alias_id: uuid.UUID, limit: int = 50, offset: int = 0):
        return await self._get_target_provenance(AliasProvenanceLink, AliasProvenanceLink.alias_id, alias_id, limit, offset)

    async def get_relationship_provenance(self, relationship_id: uuid.UUID, limit: int = 50, offset: int = 0):
        return await self._get_target_provenance(RelationshipProvenanceLink, RelationshipProvenanceLink.relationship_id, relationship_id, limit, offset)

    async def link_entity(self, link: EntityProvenanceLink) -> EntityProvenanceLink:
        self.session.add(link)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            # Idempotent fetch
            stmt = select(EntityProvenanceLink).where(
                and_(EntityProvenanceLink.entity_id == link.entity_id, EntityProvenanceLink.provenance_id == link.provenance_id)
            )
            return (await self.session.execute(stmt)).scalar_one()
        return link

    async def link_identifier(self, link: IdentifierProvenanceLink) -> IdentifierProvenanceLink:
        self.session.add(link)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            stmt = select(IdentifierProvenanceLink).where(
                and_(IdentifierProvenanceLink.identifier_id == link.identifier_id, IdentifierProvenanceLink.provenance_id == link.provenance_id)
            )
            return (await self.session.execute(stmt)).scalar_one()
        return link

    async def link_alias(self, link: AliasProvenanceLink) -> AliasProvenanceLink:
        self.session.add(link)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            stmt = select(AliasProvenanceLink).where(
                and_(AliasProvenanceLink.alias_id == link.alias_id, AliasProvenanceLink.provenance_id == link.provenance_id)
            )
            return (await self.session.execute(stmt)).scalar_one()
        return link

    async def link_relationship(self, link: RelationshipProvenanceLink) -> RelationshipProvenanceLink:
        self.session.add(link)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            stmt = select(RelationshipProvenanceLink).where(
                and_(RelationshipProvenanceLink.relationship_id == link.relationship_id, RelationshipProvenanceLink.provenance_id == link.provenance_id)
            )
            return (await self.session.execute(stmt)).scalar_one()
        return link
