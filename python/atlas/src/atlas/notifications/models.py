import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class NotificationModel(Base):
    """Authoritative durable notification entity stored in PostgreSQL."""

    __tablename__ = "notifications"

    notification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )
    producer_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    dedupe_key: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
    )
    action_kind: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="none",
        server_default="none",
    )
    action_route: Mapped[Optional[str]] = mapped_column(
        String(256),
        nullable=True,
    )
    action_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    read_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    archived_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_notifications_recipient_pagination",
            recipient_user_id,
            created_at.desc(),
            notification_id.desc(),
        ),
        Index(
            "ix_notifications_recipient_unread",
            recipient_user_id,
            created_at.desc(),
            postgresql_where=(read_at.is_(None) & archived_at.is_(None)),
        ),
        Index(
            "uq_notifications_recipient_producer_dedupe",
            recipient_user_id,
            producer_key,
            dedupe_key,
            unique=True,
            postgresql_where=dedupe_key.isnot(None),
        ),
        Index(
            "ix_notifications_recipient_archived",
            recipient_user_id,
            archived_at.desc(),
            postgresql_where=archived_at.isnot(None),
        ),
        CheckConstraint(
            "category IN ('general', 'system', 'security', 'data', "
            "'market', 'research', 'account')",
            name="ck_notifications_category",
        ),
        CheckConstraint(
            "severity IN ('info', 'success', 'warning', 'error')",
            name="ck_notifications_severity",
        ),
        CheckConstraint(
            "action_kind IN ('none', 'internal_route', 'entity_route')",
            name="ck_notifications_action_kind",
        ),
        CheckConstraint(
            "(action_kind = 'none' AND action_route IS NULL AND action_entity_id IS NULL) "
            "OR (action_kind = 'internal_route' AND action_route IS NOT NULL "
            "AND action_entity_id IS NULL) "
            "OR (action_kind = 'entity_route' AND action_route IS NOT NULL "
            "AND action_entity_id IS NOT NULL)",
            name="ck_notifications_action_consistency",
        ),
    )
