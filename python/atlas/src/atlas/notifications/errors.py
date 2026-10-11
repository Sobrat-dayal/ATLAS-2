"""Exception definitions for ATLAS persistent notifications."""

from atlas.core.exceptions import AtlasError


class NotificationError(AtlasError):
    """Base exception for all notification subsystem errors."""

    def __init__(
        self,
        message: str = "Notification error",
        code: str = "NOTIFICATION_ERROR",
        status_code: int = 400,
        details: dict | list | None = None,
    ):
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class NotificationNotFoundError(NotificationError):
    """Raised when a requested notification cannot be found for the recipient."""

    def __init__(self, notification_id: str | None = None):
        msg = (
            f"Notification '{notification_id}' not found."
            if notification_id
            else "Notification not found."
        )
        super().__init__(message=msg, code="NOTIFICATION_NOT_FOUND", status_code=404)


class NotificationArchivedError(NotificationError):
    """Raised when an operation is disallowed on an archived notification (e.g. mark unread)."""

    def __init__(self, message: str = "Archived notifications cannot be marked unread."):
        super().__init__(message=message, code="NOTIFICATION_ARCHIVED", status_code=400)


class NotificationDedupeConflictError(NotificationError):
    """Raised when a producer creates a notification with an existing dedupe key
    but mismatched payload content."""

    def __init__(
        self,
        producer_key: str,
        dedupe_key: str,
        message: str = "Notification dedupe key conflict with mismatched payload content.",
    ):
        super().__init__(
            message=message,
            code="NOTIFICATION_DEDUPE_CONFLICT",
            status_code=409,
            details={"producer_key": producer_key, "dedupe_key": dedupe_key},
        )


class InvalidNotificationActionError(NotificationError):
    """Raised when notification action kind, route, or entity targets violate
    security allowlists."""

    def __init__(self, message: str):
        super().__init__(message=message, code="INVALID_NOTIFICATION_ACTION", status_code=422)


class InvalidCursorError(NotificationError):
    """Raised when an opaque pagination cursor is malformed or invalid."""

    def __init__(self, message: str = "Invalid notification pagination cursor."):
        super().__init__(message=message, code="INVALID_CURSOR", status_code=400)


class InvalidNotificationContentError(NotificationError):
    """Raised when notification title, message, or metadata violate bounds."""

    def __init__(self, message: str):
        super().__init__(message=message, code="INVALID_NOTIFICATION_CONTENT", status_code=422)
