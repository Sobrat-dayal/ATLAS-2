import uuid
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.identifiers.models import EntityIdentifier, IdentifierScheme


class IdentifierRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_schemes(self) -> List[IdentifierScheme]:
        stmt = select(IdentifierScheme).order_by(IdentifierScheme.key)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_scheme(self, key: str) -> Optional[IdentifierScheme]:
        stmt = select(IdentifierScheme).where(IdentifierScheme.key == key)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_entity_identifiers(
        self, entity_id: uuid.UUID, include_history: bool = False
    ) -> List[EntityIdentifier]:
        stmt = select(EntityIdentifier).where(EntityIdentifier.entity_id == entity_id)
        if not include_history:
            stmt = stmt.where(EntityIdentifier.is_current == True)

        # Determine sorting order (e.g., scheme, scope, value)
        stmt = stmt.order_by(
            EntityIdentifier.scheme_key,
            EntityIdentifier.scope_entity_id,
            EntityIdentifier.value,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_current(
        self,
        scheme_key: str,
        normalized_value: str,
        scope_entity_id: Optional[uuid.UUID] = None,
        namespace: Optional[str] = None,
    ) -> Optional[EntityIdentifier]:
        stmt = (
            select(EntityIdentifier)
            .where(EntityIdentifier.scheme_key == scheme_key)
            .where(EntityIdentifier.normalized_value == normalized_value)
            .where(EntityIdentifier.is_current == True)
        )
        if scope_entity_id:
            stmt = stmt.where(EntityIdentifier.scope_entity_id == scope_entity_id)
        else:
            stmt = stmt.where(EntityIdentifier.scope_entity_id.is_(None))

        if namespace:
            stmt = stmt.where(EntityIdentifier.namespace == namespace)
        else:
            stmt = stmt.where(EntityIdentifier.namespace.is_(None))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_overlapping_history(
        self,
        scheme_key: str,
        normalized_value: str,
        scope_entity_id: Optional[uuid.UUID],
        namespace: Optional[str],
        valid_from: Optional[date],
        valid_to: Optional[date],
    ) -> List[EntityIdentifier]:
        stmt = (
            select(EntityIdentifier)
            .where(EntityIdentifier.scheme_key == scheme_key)
            .where(EntityIdentifier.normalized_value == normalized_value)
        )
        if scope_entity_id:
            stmt = stmt.where(EntityIdentifier.scope_entity_id == scope_entity_id)
        else:
            stmt = stmt.where(EntityIdentifier.scope_entity_id.is_(None))

        if namespace:
            stmt = stmt.where(EntityIdentifier.namespace == namespace)
        else:
            stmt = stmt.where(EntityIdentifier.namespace.is_(None))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_assignment(self, assignment: EntityIdentifier) -> EntityIdentifier:
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def find_identifier_candidates(
        self,
        scheme_key: str,
        normalized_value: str,
        include_historical: bool = False,
    ) -> List[EntityIdentifier]:
        stmt = (
            select(EntityIdentifier)
            .where(EntityIdentifier.scheme_key == scheme_key)
            .where(EntityIdentifier.normalized_value == normalized_value)
        )
        if not include_historical:
            stmt = stmt.where(EntityIdentifier.is_current == True)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
