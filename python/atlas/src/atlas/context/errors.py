"""
Typed domain exceptions for ATLAS Stage 121: Global Workspace Linking.
"""

from typing import Any, Optional


class ContextLinkingError(Exception):
    """Base exception for all context linking operations."""

    def __init__(self, message: str, code: str = "CONTEXT_LINKING_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class ContextChannelNotFoundError(ContextLinkingError):
    def __init__(self, channel_id: str):
        super().__init__(
            f"Link channel '{channel_id}' not found.",
            code="CONTEXT_CHANNEL_NOT_FOUND",
            status_code=404,
        )
        self.channel_id = channel_id


class ContextChannelAccessDeniedError(ContextLinkingError):
    def __init__(self, channel_id: str):
        super().__init__(
            f"Access denied to link channel '{channel_id}'.",
            code="CONTEXT_CHANNEL_ACCESS_DENIED",
            status_code=403,
        )
        self.channel_id = channel_id


class ContextChannelScopeInvalidError(ContextLinkingError):
    def __init__(self, scope: str, reason: str):
        super().__init__(
            f"Invalid channel scope '{scope}': {reason}",
            code="CONTEXT_CHANNEL_SCOPE_INVALID",
            status_code=400,
        )


class ContextChannelLimitExceededError(ContextLinkingError):
    def __init__(self, max_channels: int):
        super().__init__(
            f"Maximum channel limit ({max_channels}) exceeded for this workspace or user session.",
            code="CONTEXT_CHANNEL_LIMIT_EXCEEDED",
            status_code=400,
        )


class ContextMembershipNotFoundError(ContextLinkingError):
    def __init__(self, membership_id: str):
        super().__init__(
            f"Link membership '{membership_id}' not found.",
            code="CONTEXT_MEMBERSHIP_NOT_FOUND",
            status_code=404,
        )


class ContextMembershipDuplicateError(ContextLinkingError):
    def __init__(self, channel_id: str, panel_instance_id: str):
        super().__init__(
            f"Panel instance '{panel_instance_id}' is already registered in channel '{channel_id}'.",
            code="CONTEXT_MEMBERSHIP_DUPLICATE",
            status_code=409,
        )


class ContextDimensionUnsupportedError(ContextLinkingError):
    def __init__(self, panel_type: str, dimension: str):
        super().__init__(
            f"Dimension '{dimension}' is not supported by panel type '{panel_type}'.",
            code="CONTEXT_DIMENSION_UNSUPPORTED",
            status_code=400,
        )


class ContextEntityNotFoundError(ContextLinkingError):
    def __init__(self, entity_id: str, entity_type: str):
        super().__init__(
            f"Canonical entity '{entity_id}' of type '{entity_type}' not found.",
            code="CONTEXT_ENTITY_NOT_FOUND",
            status_code=404,
        )


class ContextEntityAmbiguousError(ContextLinkingError):
    def __init__(self, query: str, candidates: list[Any]):
        super().__init__(
            f"Multiple canonical candidates found for '{query}'. Disambiguation required.",
            code="CONTEXT_ENTITY_AMBIGUOUS",
            status_code=422,
        )
        self.candidates = candidates


class ContextTransformationUnsupportedError(ContextLinkingError):
    def __init__(self, source_type: str, target_type: str):
        super().__init__(
            f"Entity transformation from '{source_type}' to '{target_type}' is not supported or relation is missing.",
            code="CONTEXT_TRANSFORMATION_UNSUPPORTED",
            status_code=422,
        )


class ContextSubscriberIncompatibleError(ContextLinkingError):
    def __init__(self, panel_instance_id: str, reason: str):
        super().__init__(
            f"Panel '{panel_instance_id}' is incompatible with the dispatched context: {reason}",
            code="CONTEXT_SUBSCRIBER_INCOMPATIBLE",
            status_code=422,
        )


class ContextRevisionConflictError(ContextLinkingError):
    def __init__(self, expected_revision: int, current_revision: int):
        super().__init__(
            f"Context revision conflict: Expected {expected_revision}, but server is at {current_revision}.",
            code="CONTEXT_REVISION_CONFLICT",
            status_code=409,
        )
        self.expected_revision = expected_revision
        self.current_revision = current_revision


class ContextEventStaleError(ContextLinkingError):
    def __init__(self, event_revision: int, current_revision: int):
        super().__init__(
            f"Stale context event with revision {event_revision} dropped (current is {current_revision}).",
            code="CONTEXT_EVENT_STALE",
            status_code=409,
        )


class ContextEventLoopDetectedError(ContextLinkingError):
    def __init__(self, event_id: str, causation_id: Optional[str]):
        super().__init__(
            f"Context event loop detected for event '{event_id}' (causation '{causation_id}'). Dropped to prevent cyclic storms.",
            code="CONTEXT_EVENT_LOOP_DETECTED",
            status_code=422,
        )


class ContextSourceRestrictedError(ContextLinkingError):
    def __init__(self, source: str, reason: str):
        super().__init__(
            f"Data source '{source}' access restricted by provider entitlements: {reason}",
            code="CONTEXT_SOURCE_RESTRICTED",
            status_code=403,
        )

