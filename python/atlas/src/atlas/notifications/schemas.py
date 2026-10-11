import datetime
import re
import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from atlas.notifications.enums import (
    NotificationActionKind,
    NotificationCategory,
    NotificationSeverity,
)

PRODUCER_KEY_REGEX = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")

ALLOWED_INTERNAL_ROUTES = {
    "/home",
    "/markets",
    "/charts",
    "/watchlists",
    "/screeners",
    "/companies",
    "/economics",
    "/news",
    "/research",
    "/maps",
    "/intelligence",
    "/options",
    "/trading",
    "/portfolios",
    "/risk",
    "/ai",
    "/data",
    "/saved",
    "/workspaces",
    "/agents",
    "/settings",
}


class CreateNotification(BaseModel):
    """Internal model for creating a durable user-scoped notification."""

    model_config = ConfigDict(extra="forbid")

    recipient_user_id: uuid.UUID
    category: NotificationCategory = NotificationCategory.GENERAL
    severity: NotificationSeverity = NotificationSeverity.INFO
    title: str = Field(..., min_length=1, max_length=160)
    message: str = Field(..., min_length=1, max_length=2000)
    producer_key: str = Field(..., min_length=1, max_length=128)
    dedupe_key: Optional[str] = Field(None, max_length=256)
    action_kind: NotificationActionKind = NotificationActionKind.NONE
    action_route: Optional[str] = Field(None, max_length=256)
    action_entity_id: Optional[uuid.UUID] = None

    @field_validator("producer_key")
    @classmethod
    def validate_producer_key(cls, v: str) -> str:
        if not PRODUCER_KEY_REGEX.match(v):
            raise ValueError(
                "producer_key must start with a lowercase letter and contain only "
                "lowercase alphanumeric, dot, underscore, or hyphen characters (max 128)."
            )
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("title cannot be empty or whitespace only.")
        return s

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("message cannot be empty or whitespace only.")
        return s

    @model_validator(mode="after")
    def validate_action_consistency(self) -> "CreateNotification":
        if self.action_kind == NotificationActionKind.NONE:
            if self.action_route is not None or self.action_entity_id is not None:
                raise ValueError(
                    "Action kind NONE requires action_route and action_entity_id to be None."
                )
        elif self.action_kind == NotificationActionKind.INTERNAL_ROUTE:
            if not self.action_route:
                raise ValueError("Action kind INTERNAL_ROUTE requires a valid action_route.")
            if self.action_entity_id is not None:
                raise ValueError("Action kind INTERNAL_ROUTE must have action_entity_id as None.")
            if self.action_route not in ALLOWED_INTERNAL_ROUTES:
                raise ValueError(
                    f"action_route '{self.action_route}' is not in the allowed "
                    "ATLAS routes list."
                )
        elif self.action_kind == NotificationActionKind.ENTITY_ROUTE:
            if not self.action_route:
                raise ValueError("Action kind ENTITY_ROUTE requires a valid action_route.")
            if self.action_entity_id is None:
                raise ValueError("Action kind ENTITY_ROUTE requires action_entity_id.")
            if self.action_route not in ALLOWED_INTERNAL_ROUTES:
                raise ValueError(
                    f"action_route '{self.action_route}' is not in the allowed "
                    "ATLAS routes list."
                )
        return self


class NotificationResponse(BaseModel):
    """User-facing public representation of a durable notification."""

    model_config = ConfigDict(from_attributes=True)

    notification_id: uuid.UUID
    category: NotificationCategory
    severity: NotificationSeverity
    title: str
    message: str
    action_kind: NotificationActionKind
    action_route: Optional[str] = None
    action_entity_id: Optional[uuid.UUID] = None
    created_at: datetime.datetime
    read_at: Optional[datetime.datetime] = None
    archived_at: Optional[datetime.datetime] = None

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None


class NotificationListResponse(BaseModel):
    """Paginated list of user-scoped notifications."""

    items: List[NotificationResponse]
    next_cursor: Optional[str] = None
    has_more: bool = False
    unread_count: Optional[int] = None


class UnreadCountResponse(BaseModel):
    """Lightweight unread count response."""

    unread_count: int


class MarkAllReadResponse(BaseModel):
    """Response from marking all non-archived notifications as read."""

    updated_count: int
