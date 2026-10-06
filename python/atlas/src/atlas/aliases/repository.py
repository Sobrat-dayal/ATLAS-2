import datetime
import uuid
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import AliasType, EntityAlias


class AliasRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_alias_type(self, key: str) -> Optional[AliasType]:
        stmt = select(AliasType).where(AliasType.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_alias_types(self) -> Sequence[AliasType]:
        stmt = select(AliasType)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def upsert_alias_type(
        self,
        key: str,
        name: str,
        category: str,
        normalization_strategy: str,
        description: Optional[str] = None,
        is_system: bool = True,
    ) -> AliasType:
        stmt = (
            insert(AliasType)
            .values(
                key=key,
                name=name,
                category=category,
                normalization_strategy=normalization_strategy,
                description=description,
                is_system=is_system,
            )
            .on_conflict_do_update(
                index_elements=["key"],
                set_=dict(
                    name=name,
                    category=category,
                    normalization_strategy=normalization_strategy,
                    description=description,
                    is_system=is_system,
                ),
            )
            .returning(AliasType)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def add_alias(
        self,
        entity_id: uuid.UUID,
        alias_type_key: str,
        value: str,
        normalized_value: str,
        language_code: Optional[str] = None,
        valid_from: Optional[datetime.date] = None,
        is_current: bool = True,
    ) -> EntityAlias:

        if is_current:
            stmt = select(EntityAlias).where(
                EntityAlias.entity_id == entity_id,
                EntityAlias.alias_type_key == alias_type_key,
                EntityAlias.normalized_value == normalized_value,
                EntityAlias.is_current == True,
            )
            if language_code:
                stmt = stmt.where(EntityAlias.language_code == language_code)
            else:
                stmt = stmt.where(EntityAlias.language_code.is_(None))

            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                return existing

        alias = EntityAlias(
            entity_id=entity_id,
            alias_type_key=alias_type_key,
            value=value,
            normalized_value=normalized_value,
            language_code=language_code,
            valid_from=valid_from,
            is_current=is_current,
        )
        self.session.add(alias)
        await self.session.flush()
        return alias

    async def get_entity_aliases(
        self, entity_id: uuid.UUID, include_history: bool = False
    ) -> Sequence[EntityAlias]:
        stmt = select(EntityAlias).where(EntityAlias.entity_id == entity_id)
        if not include_history:
            stmt = stmt.where(EntityAlias.is_current == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def retire_alias(
        self,
        alias_id: uuid.UUID,
        valid_to: Optional[datetime.date] = None,
    ) -> Optional[EntityAlias]:
        stmt = select(EntityAlias).where(EntityAlias.alias_id == alias_id)
        result = await self.session.execute(stmt)
        alias = result.scalar_one_or_none()
        if alias:
            alias.is_current = False
            if valid_to:
                alias.valid_to = valid_to
            await self.session.flush()
        return alias
