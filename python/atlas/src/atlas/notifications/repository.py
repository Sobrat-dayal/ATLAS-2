import base64
import datetime
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.notifications.enums import NotificationListFilter
from atlas.notifications.errors import InvalidCursorError
from atlas.notifications.models import NotificationModel


def encode_cursor(created_at: datetime.datetime, notification_id: uuid.UUID) -> str:
    """Encode created_at timestamp and notification_id into an opaque keyset cursor."""
    raw = f"{created_at.isoformat()}|{notification_id}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor_str: str) -> Tuple[datetime.datetime, uuid.UUID]:
    """Decode keyset cursor into (created_at, notification_id)."""
    try:
        raw = base64.urlsafe_b64decode(cursor_str.encode("utf-8")).decode("utf-8")
        parts = raw.split("|", 1)
        if len(parts) != 2:
            raise ValueError("Malformed cursor parts")
        dt_str, id_str = parts
        dt = datetime.datetime.fromisoformat(dt_str)
        uid = uuid.UUID(id_str)
        return dt, uid
    except Exception as e:
        raise InvalidCursorError(f"Invalid cursor format: {e}") from e


class NotificationRepository:
    """Async repository for durable PostgreSQL notification operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, model: NotificationModel) -> NotificationModel:
        """Add notification model to session without committing."""
        self.session.add(model)
        await self.session.flush()
        return model

    async def find_by_id(
        self,
        notification_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> Optional[NotificationModel]:
        """Find notification by ID strictly scoped to recipient."""
        stmt = select(NotificationModel).where(
            NotificationModel.notification_id == notification_id,
            NotificationModel.recipient_user_id == recipient_user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_dedupe(
        self,
        recipient_user_id: uuid.UUID,
        producer_key: str,
        dedupe_key: str,
    ) -> Optional[NotificationModel]:
        """Find existing notification by recipient, producer, and dedupe key."""
        stmt = select(NotificationModel).where(
            NotificationModel.recipient_user_id == recipient_user_id,
            NotificationModel.producer_key == producer_key,
            NotificationModel.dedupe_key == dedupe_key,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_unread_count(self, recipient_user_id: uuid.UUID) -> int:
        """Count unread non-archived notifications for the user."""
        stmt = select(func.count(NotificationModel.notification_id)).where(
            NotificationModel.recipient_user_id == recipient_user_id,
            NotificationModel.read_at.is_(None),
            NotificationModel.archived_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def list_notifications(
        self,
        recipient_user_id: uuid.UUID,
        filter_mode: NotificationListFilter = NotificationListFilter.ALL,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[NotificationModel], Optional[str], bool]:
        """List notifications using deterministic keyset pagination."""
        stmt = select(NotificationModel).where(
            NotificationModel.recipient_user_id == recipient_user_id
        )

        if filter_mode == NotificationListFilter.ALL:
            stmt = stmt.where(NotificationModel.archived_at.is_(None))
        elif filter_mode == NotificationListFilter.UNREAD:
            stmt = stmt.where(
                NotificationModel.read_at.is_(None),
                NotificationModel.archived_at.is_(None),
            )
        elif filter_mode == NotificationListFilter.ARCHIVED:
            stmt = stmt.where(NotificationModel.archived_at.isnot(None))

        if cursor:
            cursor_dt, cursor_id = decode_cursor(cursor)
            stmt = stmt.where(
                or_(
                    NotificationModel.created_at < cursor_dt,
                    and_(
                        NotificationModel.created_at == cursor_dt,
                        NotificationModel.notification_id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(
            NotificationModel.created_at.desc(),
            NotificationModel.notification_id.desc(),
        ).limit(limit + 1)

        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())

        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = None
        if has_more and items:
            last = items[-1]
            next_cursor = encode_cursor(last.created_at, last.notification_id)

        return items, next_cursor, has_more

    async def mark_read(
        self,
        notification_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        now: datetime.datetime,
    ) -> Optional[NotificationModel]:
        """Mark notification as read if not already read, preserving original read_at."""
        notification = await self.find_by_id(notification_id, recipient_user_id)
        if not notification:
            return None
        if notification.read_at is None:
            notification.read_at = now
            await self.session.flush()
        return notification

    async def mark_unread(
        self,
        notification_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> Optional[NotificationModel]:
        """Mark notification as unread (sets read_at to NULL)."""
        notification = await self.find_by_id(notification_id, recipient_user_id)
        if not notification:
            return None
        notification.read_at = None
        await self.session.flush()
        return notification

    async def mark_all_read(
        self,
        recipient_user_id: uuid.UUID,
        now: datetime.datetime,
    ) -> int:
        """Mark all unread non-archived notifications as read for current user."""
        stmt = (
            update(NotificationModel)
            .where(
                NotificationModel.recipient_user_id == recipient_user_id,
                NotificationModel.read_at.is_(None),
                NotificationModel.archived_at.is_(None),
            )
            .values(read_at=now)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return int(result.rowcount or 0)

    async def archive(
        self,
        notification_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
        now: datetime.datetime,
    ) -> Optional[NotificationModel]:
        """Archive notification. If unread, mark as read simultaneously."""
        notification = await self.find_by_id(notification_id, recipient_user_id)
        if not notification:
            return None
        if notification.archived_at is None:
            notification.archived_at = now
            if notification.read_at is None:
                notification.read_at = now
            await self.session.flush()
        return notification
