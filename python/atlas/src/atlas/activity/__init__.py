"""ATLAS User Activity domain package (Stage 53)."""

from .canonical_modules import CANONICAL_MODULES, is_valid_module_id
from .enums import ActivityEventType
from .errors import (
    ActivityError,
    ActivityHistoryDisabledError,
    EntityAccessDeniedError,
    IdempotencyConflictError,
    InvalidCursorError,
    InvalidEntityError,
    InvalidModuleIdError,
    ModuleAccessDeniedError,
)
from .models import (
    ActivityConsentRequest,
    ActivityConsentResponse,
    ClearActivityResponse,
    RecordActivityEventRequest,
    UserActivityEvent,
    UserActivityItem,
    UserActivityListResponse,
)
from .repository import UserActivityRepository
from .router import router
from .service import UserActivityService

__all__ = [
    "ActivityConsentRequest",
    "ActivityConsentResponse",
    "ActivityError",
    "ActivityEventType",
    "ActivityHistoryDisabledError",
    "CANONICAL_MODULES",
    "ClearActivityResponse",
    "EntityAccessDeniedError",
    "IdempotencyConflictError",
    "InvalidCursorError",
    "InvalidEntityError",
    "InvalidModuleIdError",
    "ModuleAccessDeniedError",
    "RecordActivityEventRequest",
    "UserActivityEvent",
    "UserActivityItem",
    "UserActivityListResponse",
    "UserActivityRepository",
    "UserActivityService",
    "is_valid_module_id",
    "router",
]
