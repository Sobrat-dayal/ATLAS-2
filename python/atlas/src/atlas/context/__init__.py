"""
ATLAS Global Workspace Linking & Cross-Module Context Synchronization Package (Stage 121).
"""

from .capabilities import CAPABILITIES_CATALOG, get_panel_capability, is_dimension_compatible
from .enums import (
    ContextDimension,
    ContextEventType,
    ContextScope,
    LinkingStatus,
    SubscriptionMode,
    TransformationType,
)
from .errors import (
    ContextChannelAccessDeniedError,
    ContextChannelLimitExceededError,
    ContextChannelNotFoundError,
    ContextChannelScopeInvalidError,
    ContextDimensionUnsupportedError,
    ContextEntityAmbiguousError,
    ContextEntityNotFoundError,
    ContextEventLoopDetectedError,
    ContextEventStaleError,
    ContextLinkingError,
    ContextMembershipDuplicateError,
    ContextMembershipNotFoundError,
    ContextRevisionConflictError,
    ContextSourceRestrictedError,
    ContextSubscriberIncompatibleError,
    ContextTransformationUnsupportedError,
)
from .models import (
    ContextSelectionEvent,
    LinkChannel,
    LinkSubscription,
    PanelContextCapability,
    ResolvedEntity,
)
from .repository import ContextRepository
from .resolution import CanonicalEntityResolver
from .service import ContextLinkingService

__all__ = [
    "ContextScope",
    "ContextDimension",
    "SubscriptionMode",
    "ContextEventType",
    "LinkingStatus",
    "TransformationType",
    "ContextLinkingError",
    "ContextChannelNotFoundError",
    "ContextChannelAccessDeniedError",
    "ContextChannelScopeInvalidError",
    "ContextChannelLimitExceededError",
    "ContextMembershipNotFoundError",
    "ContextMembershipDuplicateError",
    "ContextDimensionUnsupportedError",
    "ContextEntityNotFoundError",
    "ContextEntityAmbiguousError",
    "ContextTransformationUnsupportedError",
    "ContextSubscriberIncompatibleError",
    "ContextRevisionConflictError",
    "ContextEventStaleError",
    "ContextEventLoopDetectedError",
    "ContextSourceRestrictedError",
    "ResolvedEntity",
    "LinkSubscription",
    "LinkChannel",
    "ContextSelectionEvent",
    "PanelContextCapability",
    "CAPABILITIES_CATALOG",
    "get_panel_capability",
    "is_dimension_compatible",
    "CanonicalEntityResolver",
    "ContextRepository",
    "ContextLinkingService",
]
