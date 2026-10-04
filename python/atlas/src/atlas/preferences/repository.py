import uuid
from typing import Sequence, Optional, Any

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import UserPreference


class UserPreferenceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_preferences(self, user_id: uuid.UUID) -> Sequence[UserPreference]:
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_preference(self, user_id: uuid.UUID, preference_key: str) -> Optional[UserPreference]:
        stmt = select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.preference_key == preference_key
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_preference(
        self,
        user_id: uuid.UUID,
        preference_key: str,
        schema_version: int,
        payload: dict[str, Any]
    ) -> UserPreference:
        pref = UserPreference(
            user_id=user_id,
            preference_key=preference_key,
            schema_version=schema_version,
            payload=payload,
            revision=1
        )
        self.session.add(pref)
        return pref

    async def update_preference(
        self,
        user_id: uuid.UUID,
        preference_key: str,
        expected_revision: int,
        schema_version: int,
        payload: dict[str, Any]
    ) -> Optional[int]:
        """
        Optimistic update. Returns the new revision if successful, None if conflict or not found.
        """
        new_revision = expected_revision + 1
        stmt = (
            update(UserPreference)
            .where(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key,
                UserPreference.revision == expected_revision
            )
            .values(
                payload=payload,
                schema_version=schema_version,
                revision=new_revision
            )
            .returning(UserPreference.revision)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_preference(self, user_id: uuid.UUID, preference_key: str) -> bool:
        stmt = (
            delete(UserPreference)
            .where(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete_all_preferences(self, user_id: uuid.UUID) -> int:
        stmt = delete(UserPreference).where(UserPreference.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount
