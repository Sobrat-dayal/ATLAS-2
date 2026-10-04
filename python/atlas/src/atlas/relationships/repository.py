import uuid
from typing import List, Optional, Tuple, Any

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .models import RelationshipType, EntityRelationship

class RelationshipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_relationship_type(self, key: str) -> Optional[RelationshipType]:
        stmt = select(RelationshipType).where(RelationshipType.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_relationship_types(self) -> List[RelationshipType]:
        stmt = select(RelationshipType).order_by(RelationshipType.key)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_relationship(self, relationship_id: uuid.UUID) -> Optional[EntityRelationship]:
        stmt = select(EntityRelationship).where(EntityRelationship.relationship_id == relationship_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_relationships_for_entity(
        self,
        entity_id: uuid.UUID,
        relationship_type_key: Optional[str] = None,
        is_current: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[EntityRelationship], int]:
        
        conditions = [
            or_(
                EntityRelationship.source_entity_id == entity_id,
                EntityRelationship.target_entity_id == entity_id
            )
        ]
        
        if relationship_type_key:
            conditions.append(EntityRelationship.relationship_type_key == relationship_type_key)
            
        if is_current is not None:
            conditions.append(EntityRelationship.is_current == is_current)

        where_clause = and_(*conditions)

        # Count
        count_stmt = select(func.count(EntityRelationship.relationship_id)).where(where_clause)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Query
        stmt = (
            select(EntityRelationship)
            .where(where_clause)
            .order_by(EntityRelationship.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def create_relationship(self, relationship: EntityRelationship) -> EntityRelationship:
        self.session.add(relationship)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Relationship already exists or violates constraints.")
        return relationship

    async def update_relationship(self, relationship: EntityRelationship) -> EntityRelationship:
        await self.session.flush()
        return relationship
