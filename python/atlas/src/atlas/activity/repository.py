"""SQLAlchemy repository implementation for user activity events."""

import datetime
import uuid
from typing import Optional, Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import UserActivityEvent


class UserActivityRepository:
    """Encapsulates database operations on user_activity_events."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_client_event_id(
        self,
        user_id: uuid.UUID,
        client_event_id: uuid.UUID,
    ) -> Optional[UserActivityEvent]:
        """Look up an event by user_id and client_event_id to enforce idempotency."""
        stmt = (
            select(UserActivityEvent)
            .where(
                UserActivityEvent.user_id == user_id,
                UserActivityEvent.client_event_id == client_event_id,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_event(
        self,
        user_id: uuid.UUID,
        event_type: str,
        client_event_id: uuid.UUID,
        module_id: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        occurred_at: Optional[datetime.datetime] = None,
    ) -> UserActivityEvent:
        """Insert a validated user activity event into the database session."""
        now = occurred_at or datetime.datetime.now(datetime.timezone.utc)
        event = UserActivityEvent(
            activity_id=uuid.uuid4(),
            user_id=user_id,
            event_type=event_type,
            module_id=module_id,
            entity_id=entity_id,
            client_event_id=client_event_id,
            occurred_at=now,
            created_at=now,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_events(
        self,
        user_id: uuid.UUID,
        limit: int,
        cursor_occurred_at: Optional[datetime.datetime] = None,
        cursor_activity_id: Optional[uuid.UUID] = None,
        retention_cutoff: Optional[datetime.datetime] = None,
    ) -> Sequence[UserActivityEvent]:
        """
        List user events ordered by occurred_at DESC, activity_id DESC using keyset pagination.
        Filters out events older than retention_cutoff.
        """
        stmt = select(UserActivityEvent).where(UserActivityEvent.user_id == user_id)

        if retention_cutoff is not None:
            stmt = stmt.where(UserActivityEvent.occurred_at >= retention_cutoff)

        if cursor_occurred_at is not None and cursor_activity_id is not None:
            # Keyset condition: (occurred_at < cursor_time)
            # OR (occurred_at == cursor_time AND activity_id < cursor_id)
            stmt = stmt.where(
                (UserActivityEvent.occurred_at < cursor_occurred_at)
                | (
                    (UserActivityEvent.occurred_at == cursor_occurred_at)
                    & (UserActivityEvent.activity_id < cursor_activity_id)
                )
            )

        stmt = stmt.order_by(
            UserActivityEvent.occurred_at.desc(),
            UserActivityEvent.activity_id.desc(),
        ).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_user_events(self, user_id: uuid.UUID) -> int:
        """Counts total activity events for a user."""
        stmt = select(func.count(UserActivityEvent.activity_id)).where(
            UserActivityEvent.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def prune_user_cap(self, user_id: uuid.UUID, max_retained: int = 1000) -> int:
        """
        Enforces per-user storage bound. If user has more than max_retained events,
        removes the oldest events.
        """
        total = await self.count_user_events(user_id)
        if total <= max_retained:
            return 0

        # Find the boundary row at offset max_retained - 1
        stmt = (
            select(UserActivityEvent.occurred_at, UserActivityEvent.activity_id)
            .where(UserActivityEvent.user_id == user_id)
            .order_by(
                UserActivityEvent.occurred_at.desc(),
                UserActivityEvent.activity_id.desc(),
            )
            .offset(max_retained - 1)
            .limit(1)
        )
        boundary_res = await self.session.execute(stmt)
        boundary = boundary_res.first()
        if not boundary:
            return 0

        boundary_occurred, boundary_id = boundary

        # Delete rows older than boundary
        del_stmt = delete(UserActivityEvent).where(
            UserActivityEvent.user_id == user_id,
            (UserActivityEvent.occurred_at < boundary_occurred)
            | (
                (UserActivityEvent.occurred_at == boundary_occurred)
                & (UserActivityEvent.activity_id < boundary_id)
            ),
        )
        del_res = await self.session.execute(del_stmt)
        return del_res.rowcount or 0

    async def delete_all_for_user(self, user_id: uuid.UUID) -> int:
        """Deletes all activity records owned by the specified user."""
        stmt = delete(UserActivityEvent).where(UserActivityEvent.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount or 0

    async def cleanup_expired(
        self,
        retention_cutoff: datetime.datetime,
        batch_size: int = 500,
    ) -> int:
        """Deletes expired activity events across the database in bounded batches."""
        # Find IDs of expired events up to batch_size
        id_stmt = (
            select(UserActivityEvent.activity_id)
            .where(UserActivityEvent.occurred_at < retention_cutoff)
            .limit(batch_size)
        )
        res = await self.session.execute(id_stmt)
        ids_to_delete = res.scalars().all()
        if not ids_to_delete:
            return 0

        del_stmt = delete(UserActivityEvent).where(UserActivityEvent.activity_id.in_(ids_to_delete))
        del_res = await self.session.execute(del_stmt)
        return del_res.rowcount or 0
