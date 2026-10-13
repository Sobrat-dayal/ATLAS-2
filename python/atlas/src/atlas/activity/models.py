"""SQLAlchemy database models and Pydantic schemas for ATLAS User Activity."""

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
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

from .enums import ActivityEventType


class UserActivityEvent(Base):
    """Authoritative durable activity event stored in PostgreSQL."""

    __tablename__ = "user_activity_events"

    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    module_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="SET NULL"),
        nullable=True,
    )
    client_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    occurred_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_user_activity_events_user_occurred_id",
            user_id,
            occurred_at.desc(),
            activity_id.desc(),
        ),
        Index(
            "uq_user_activity_events_user_client_event",
            user_id,
            client_event_id,
            unique=True,
        ),
        Index(
            "ix_user_activity_events_occurred_at",
            occurred_at,
        ),
        CheckConstraint(
            "event_type IN ('MODULE_OPENED', 'ENTITY_SELECTED')",
            name="ck_user_activity_event_type",
        ),
        CheckConstraint(
            "(event_type = 'MODULE_OPENED' AND module_id IS NOT NULL AND entity_id IS NULL) OR "
            "(event_type = 'ENTITY_SELECTED' AND entity_id IS NOT NULL)",
            name="ck_user_activity_payload_consistency",
        ),
    )


# --- Pydantic Schemas ---


class RecordActivityEventRequest(BaseModel):
    """Strict typed request payload for capturing an explicit user action."""

    model_config = ConfigDict(extra="forbid")

    event_type: ActivityEventType
    module_id: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    client_event_id: uuid.UUID

    @model_validator(mode="after")
    def validate_payload_consistency(self) -> "RecordActivityEventRequest":
        if self.event_type == ActivityEventType.MODULE_OPENED:
            if not self.module_id:
                raise ValueError("module_id is required when event_type is MODULE_OPENED")
            if self.entity_id is not None:
                raise ValueError("entity_id must be null when event_type is MODULE_OPENED")
        elif self.event_type == ActivityEventType.ENTITY_SELECTED:
            if not self.entity_id:
                raise ValueError("entity_id is required when event_type is ENTITY_SELECTED")
        return self


class ActivityConsentRequest(BaseModel):
    """Request payload for updating user activity recording consent."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool


class ActivityConsentResponse(BaseModel):
    """Response returned upon reading or mutating activity consent."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool
    updated_at: datetime.datetime


class UserActivityItem(BaseModel):
    """Authorized, safely resolved view of a recorded activity item."""

    model_config = ConfigDict(extra="forbid")

    activity_id: uuid.UUID
    event_type: ActivityEventType
    module_id: Optional[str] = None
    module_label: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    entity_display_name: Optional[str] = None
    entity_type: Optional[str] = None
    occurred_at: datetime.datetime
    resume_target: str
    is_accessible: bool = True


class UserActivityListResponse(BaseModel):
    """Paginated list response for Home Personalized Activity."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    enabled: bool
    items: list[UserActivityItem] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    has_more: bool = False


class ClearActivityResponse(BaseModel):
    """Response returned upon securely clearing user activity history."""

    model_config = ConfigDict(extra="forbid")

    deleted_count: int
    cleared: bool = True
