"""Repository layer for persisting Watchlist Column Preferences (Stage 77)."""

import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.watchlists.models import WatchlistColumnPreference

from .errors import ColumnConfigRevisionConflictError


class WatchlistColumnPreferenceRepository:
    """Handles PostgreSQL storage and atomic concurrency for column preferences."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_watchlist_id(self, watchlist_id: UUID) -> Optional[WatchlistColumnPreference]:
        """Fetches the persistent column preference record for a given watchlist."""
        stmt = select(WatchlistColumnPreference).where(
            WatchlistColumnPreference.watchlist_id == watchlist_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def save_preferences(
        self,
        watchlist_id: UUID,
        configuration_dict: dict,
        expected_revision: Optional[int] = None,
    ) -> WatchlistColumnPreference:
        """
        Saves or updates column preferences with atomic revision concurrency control.
        """
        existing = await self.get_by_watchlist_id(watchlist_id)

        if existing is None:
            # First-time persistent save
            pref = WatchlistColumnPreference(
                watchlist_id=watchlist_id,
                configuration_schema_version=configuration_dict.get("schema_version", 1),
                revision=1,
                configuration_jsonb=configuration_dict,
            )
            self.session.add(pref)
            await self.session.commit()
            await self.session.refresh(pref)
            return pref

        # Concurrency verification
        if expected_revision is not None and existing.revision != expected_revision:
            raise ColumnConfigRevisionConflictError(
                f"Revision conflict: expected revision {expected_revision}, "
                f"current database revision is {existing.revision}."
            )

        existing.configuration_jsonb = configuration_dict
        existing.configuration_schema_version = configuration_dict.get("schema_version", 1)
        existing.revision += 1
        existing.updated_at = datetime.datetime.now(datetime.timezone.utc)

        await self.session.commit()
        await self.session.refresh(existing)
        return existing

    async def delete_preferences(self, watchlist_id: UUID) -> bool:
        """Deletes preferences record, effectively resetting watchlist to defaults."""
        stmt = delete(WatchlistColumnPreference).where(
            WatchlistColumnPreference.watchlist_id == watchlist_id
        )
        res = await self.session.execute(stmt)
        await self.session.commit()
        return bool(res.rowcount and res.rowcount > 0)
