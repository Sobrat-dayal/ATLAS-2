import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Entity, EntityType


class EntityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_entity_type(self, key: str) -> Optional[EntityType]:
        stmt = select(EntityType).where(EntityType.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_entity_types(self) -> Sequence[EntityType]:
        stmt = select(EntityType)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, entity_id: uuid.UUID) -> Optional[Entity]:
        stmt = select(Entity).where(Entity.entity_id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def create(
        self,
        entity_id: uuid.UUID,
        entity_type: str,
        canonical_name: str,
        display_name: str,
        description: Optional[str],
    ) -> Entity:
        """
        Creates an entity object and adds it to the session.
        Does not issue a commit, allowing caller to atomic specialize.
        """
        entity = Entity(
            entity_id=entity_id,
            entity_type=entity_type,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )
        self.session.add(entity)
        return entity
