import datetime
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.repository import EntityRepository

from .models import EntityRelationship
from .policies import get_policy
from .registry import get_all_relationship_type_definitions, get_relationship_type_definition
from .repository import RelationshipRepository
from .schemas import EntityRelationshipCreate


class RelationshipService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RelationshipRepository(session)
        self.entity_repo = EntityRepository(session)

    async def get_all_system_types(self) -> List[dict]:
        types = get_all_relationship_type_definitions()
        return [
            {
                "key": t.key,
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "inverse_key": t.inverse_key,
                "canonical_key": t.canonical_key,
                "is_symmetric": t.is_symmetric,
                "source_policy_key": t.source_policy_key,
                "target_policy_key": t.target_policy_key,
                "allows_self": t.allows_self,
                "is_system": t.is_system,
            }
            for t in types
        ]

    async def list_relationships(
        self,
        entity_id: uuid.UUID,
        relationship_type_key: Optional[str] = None,
        is_current: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[EntityRelationship], int]:

        # Verify entity exists
        entity = await self.entity_repo.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")

        return await self.repository.list_relationships_for_entity(
            entity_id=entity_id,
            relationship_type_key=relationship_type_key,
            is_current=is_current,
            limit=limit,
            offset=offset,
        )

    async def create_relationship(
        self, source_entity_id: uuid.UUID, data: EntityRelationshipCreate
    ) -> EntityRelationship:

        rel_def = get_relationship_type_definition(data.relationship_type_key)
        if not rel_def:
            raise ValueError(f"Unknown relationship type: {data.relationship_type_key}")

        source_entity = await self.entity_repo.get_entity(source_entity_id)
        if not source_entity:
            raise ValueError(f"Source entity not found: {source_entity_id}")

        target_entity = await self.entity_repo.get_entity(data.target_entity_id)
        if not target_entity:
            raise ValueError(f"Target entity not found: {data.target_entity_id}")

        if source_entity_id == data.target_entity_id and not rel_def.allows_self:
            raise ValueError(
                f"Relationship type {data.relationship_type_key} does not allow self-relationships"
            )

        source_policy = get_policy(rel_def.source_policy_key)
        target_policy = get_policy(rel_def.target_policy_key)

        if not source_policy(source_entity):
            raise ValueError(
                f"Source entity {source_entity_id} fails policy {rel_def.source_policy_key}"
            )

        if not target_policy(target_entity):
            raise ValueError(
                f"Target entity {data.target_entity_id} fails policy {rel_def.target_policy_key}"
            )

        canonical_key = rel_def.canonical_key
        canonical_source_id = source_entity_id
        canonical_target_id = data.target_entity_id

        # Inverse canonicalization
        if rel_def.key != canonical_key:
            canonical_source_id = data.target_entity_id
            canonical_target_id = source_entity_id

        # Symmetric canonical order
        if rel_def.is_symmetric:
            if canonical_source_id > canonical_target_id:
                canonical_source_id, canonical_target_id = canonical_target_id, canonical_source_id

        # Check for existing current relationship
        stmt = select(EntityRelationship).where(
            and_(
                EntityRelationship.relationship_type_key == canonical_key,
                EntityRelationship.source_entity_id == canonical_source_id,
                EntityRelationship.target_entity_id == canonical_target_id,
                EntityRelationship.is_current == True,
            )
        )
        existing = await self.session.execute(stmt)
        if existing.scalar_one_or_none():
            raise ValueError("Relationship already exists")

        new_rel = EntityRelationship(
            relationship_type_key=canonical_key,
            source_entity_id=canonical_source_id,
            target_entity_id=canonical_target_id,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
            is_current=True,
        )

        return await self.repository.create_relationship(new_rel)

    async def end_relationship(
        self, relationship_id: uuid.UUID, end_date: datetime.date
    ) -> EntityRelationship:

        rel = await self.repository.get_relationship(relationship_id)
        if not rel:
            raise ValueError(f"Relationship not found: {relationship_id}")

        if not rel.is_current:
            raise ValueError("Relationship is already ended")

        rel.is_current = False
        rel.valid_to = end_date
        return await self.repository.update_relationship(rel)
