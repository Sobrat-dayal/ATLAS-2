"""Persistent Notification subsystem for ATLAS (Stage 49)."""

from atlas.notifications.enums import (
    NotificationActionKind,
    NotificationCategory,
    NotificationListFilter,
    NotificationSeverity,
)
from atlas.notifications.errors import (
    InvalidCursorError,
    InvalidNotificationActionError,
    InvalidNotificationContentError,
    NotificationArchivedError,
    NotificationDedupeConflictError,
    NotificationError,
    NotificationNotFoundError,
)
from atlas.notifications.models import NotificationModel
from atlas.notifications.repository import (
    NotificationRepository,
    decode_cursor,
    encode_cursor,
)
from atlas.notifications.schemas import (
    ALLOWED_INTERNAL_ROUTES,
    CreateNotification,
    MarkAllReadResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from atlas.notifications.service import NotificationService

__all__ = [
    "NotificationCategory",
    "NotificationSeverity",
    "NotificationActionKind",
    "NotificationListFilter",
    "NotificationError",
    "NotificationNotFoundError",
    "NotificationArchivedError",
    "NotificationDedupeConflictError",
    "InvalidNotificationActionError",
    "InvalidCursorError",
    "InvalidNotificationContentError",
    "NotificationModel",
    "NotificationRepository",
    "NotificationService",
    "CreateNotification",
    "NotificationResponse",
    "NotificationListResponse",
    "UnreadCountResponse",
    "MarkAllReadResponse",
    "encode_cursor",
    "decode_cursor",
    "ALLOWED_INTERNAL_ROUTES",
]
