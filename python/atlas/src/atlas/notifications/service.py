import datetime
import uuid
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity
from atlas.notifications.enums import (
    NotificationActionKind,
    NotificationListFilter,
)
from atlas.notifications.errors import (
    InvalidNotificationActionError,
    NotificationArchivedError,
    NotificationDedupeConflictError,
    NotificationNotFoundError,
)
from atlas.notifications.models import NotificationModel
from atlas.notifications.repository import NotificationRepository
from atlas.notifications.schemas import (
    CreateNotification,
    NotificationListResponse,
    NotificationResponse,
)


class NotificationService:
    """Canonical service for creating, querying, and managing persistent notifications."""

    def __init__(
        self,
        session: AsyncSession,
        repository: Optional[NotificationRepository] = None,
    ) -> None:
        self.session = session
        self.repository = repository or NotificationRepository(session)

    async def create_notification(
        self,
        params: Union[CreateNotification, dict],
    ) -> NotificationResponse:
        """Create a durable user-scoped notification with dedupe idempotency and
        action verification."""
        if isinstance(params, dict):
            validated = CreateNotification.model_validate(params)
        else:
            validated = params

        # Validate action entity target exists in PostgreSQL Universal Entity System
        if validated.action_kind == NotificationActionKind.ENTITY_ROUTE:
            stmt = select(Entity.entity_id).where(Entity.entity_id == validated.action_entity_id)
            res = await self.session.execute(stmt)
            if res.scalar_one_or_none() is None:
                raise InvalidNotificationActionError(
                    f"Entity '{validated.action_entity_id}' referenced by "
                    "action_entity_id does not exist."
                )

        # Check dedupe key idempotency
        if validated.dedupe_key:
            existing = await self.repository.find_by_dedupe(
                recipient_user_id=validated.recipient_user_id,
                producer_key=validated.producer_key,
                dedupe_key=validated.dedupe_key,
            )
            if existing is not None:
                # Compare semantic content
                is_identical = (
                    existing.title == validated.title
                    and existing.message == validated.message
                    and existing.category == validated.category.value
                    and existing.severity == validated.severity.value
                    and existing.action_kind == validated.action_kind.value
                    and existing.action_route == validated.action_route
                    and existing.action_entity_id == validated.action_entity_id
                )
                if is_identical:
                    return NotificationResponse.model_validate(existing)
                else:
                    raise NotificationDedupeConflictError(
                        producer_key=validated.producer_key,
                        dedupe_key=validated.dedupe_key,
                    )

        now = datetime.datetime.now(datetime.timezone.utc)
        model = NotificationModel(
            notification_id=uuid.uuid4(),
            recipient_user_id=validated.recipient_user_id,
            category=validated.category.value,
            severity=validated.severity.value,
            title=validated.title,
            message=validated.message,
            producer_key=validated.producer_key,
            dedupe_key=validated.dedupe_key,
            action_kind=validated.action_kind.value,
            action_route=validated.action_route,
            action_entity_id=validated.action_entity_id,
            created_at=now,
            updated_at=now,
            read_at=None,
            archived_at=None,
        )

        await self.repository.create(model)
        return NotificationResponse.model_validate(model)

    async def list_notifications(
        self,
        recipient_user_id: uuid.UUID,
        filter_mode: NotificationListFilter = NotificationListFilter.ALL,
        limit: int = 25,
        cursor: Optional[str] = None,
        include_unread_count: bool = False,
    ) -> NotificationListResponse:
        """List notifications for recipient with bounded keyset pagination."""
        bounded_limit = max(1, min(limit, 100))
        items, next_cursor, has_more = await self.repository.list_notifications(
            recipient_user_id=recipient_user_id,
            filter_mode=filter_mode,
            limit=bounded_limit,
            cursor=cursor,
        )

        unread_count = None
        if include_unread_count:
            unread_count = await self.repository.get_unread_count(recipient_user_id)

        responses = [NotificationResponse.model_validate(m) for m in items]
        return NotificationListResponse(
            items=responses,
            next_cursor=next_cursor,
            has_more=has_more,
            unread_count=unread_count,
        )

    async def get_unread_count(self, recipient_user_id: uuid.UUID) -> int:
        """Get unread count for recipient."""
        return await self.repository.get_unread_count(recipient_user_id)

    async def mark_read(
        self,
        notification_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> NotificationResponse:
        """Mark notification as read idempotently."""
        now = datetime.datetime.now(datetime.timezone.utc)
        updated = await self.repository.mark_read(
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
            now=now,
        )
        if updated is None:
            raise NotificationNotFoundError(str(notification_id))
        return NotificationResponse.model_validate(updated)

    async def mark_unread(
        self,
        notification_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> NotificationResponse:
        """Mark notification as unread. Rejects if archived."""
        existing = await self.repository.find_by_id(notification_id, recipient_user_id)
        if existing is None:
            raise NotificationNotFoundError(str(notification_id))
        if existing.archived_at is not None:
            raise NotificationArchivedError()

        updated = await self.repository.mark_unread(
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )
        if updated is None:
            raise NotificationNotFoundError(str(notification_id))
        return NotificationResponse.model_validate(updated)

    async def mark_all_read(self, recipient_user_id: uuid.UUID) -> int:
        """Mark all unread non-archived notifications as read."""
        now = datetime.datetime.now(datetime.timezone.utc)
        return await self.repository.mark_all_read(recipient_user_id, now)

    async def archive(
        self,
        notification_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> NotificationResponse:
        """Archive notification. If unread, simultaneously mark as read."""
        now = datetime.datetime.now(datetime.timezone.utc)
        updated = await self.repository.archive(
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
            now=now,
        )
        if updated is None:
            raise NotificationNotFoundError(str(notification_id))
        return NotificationResponse.model_validate(updated)
