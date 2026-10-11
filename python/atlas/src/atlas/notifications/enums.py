from enum import Enum


class NotificationCategory(str, Enum):
    """Categorization for durable notifications."""

    GENERAL = "general"
    SYSTEM = "system"
    SECURITY = "security"
    DATA = "data"
    MARKET = "market"
    RESEARCH = "research"
    ACCOUNT = "account"


class NotificationSeverity(str, Enum):
    """Severity level for durable notifications."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationActionKind(str, Enum):
    """Interaction target kind for durable notifications."""

    NONE = "none"
    INTERNAL_ROUTE = "internal_route"
    ENTITY_ROUTE = "entity_route"


class NotificationListFilter(str, Enum):
    """List filtering strategy for durable notifications."""

    ALL = "all"
    UNREAD = "unread"
    ARCHIVED = "archived"
