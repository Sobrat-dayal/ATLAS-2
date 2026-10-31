"""Universal Event Model Exceptions and Error Hierarchy (Stage 135)."""

from typing import Optional


class EventDomainError(Exception):
    """Base error for all universal event intelligence operations."""
    def __init__(self, message: str, code: str = "EVENT_DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class EventNotFoundError(EventDomainError):
    """Raised when an event ID cannot be found."""
    def __init__(self, event_id: str):
        super().__init__(f"Universal event '{event_id}' not found", code="EVENT_NOT_FOUND")
        self.event_id = event_id


class EventTypeInvalidError(EventDomainError):
    """Raised when an event type or category is unrecognized or invalid."""
    def __init__(self, event_type: str):
        super().__init__(f"Invalid or unsupported event type: '{event_type}'", code="INVALID_EVENT_TYPE")
        self.event_type = event_type


class EventDateSemanticsInvalidError(EventDomainError):
    """Raised when event timestamps violate causality or date ranges are malformed."""
    def __init__(self, reason: str):
        super().__init__(f"Invalid event temporal semantics: {reason}", code="INVALID_TEMPORAL_SEMANTICS")
        self.reason = reason


class EventLookAheadViolationError(EventDomainError):
    """Raised when a historical as-of query attempts to access future knowledge time."""
    def __init__(self, as_of_time: str, data_knowledge_time: str):
        super().__init__(
            f"Historical look-ahead violation: as-of query time '{as_of_time}' cannot access "
            f"data recorded at knowledge time '{data_knowledge_time}'",
            code="LOOK_AHEAD_BIAS_PROHIBITED"
        )
        self.as_of_time = as_of_time
        self.data_knowledge_time = data_knowledge_time


class EventDeduplicationConflictError(EventDomainError):
    """Raised when candidate events have irreconcilable conflicting attributes."""
    def __init__(self, event_id1: str, event_id2: str, reason: str):
        super().__init__(
            f"Cannot merge events '{event_id1}' and '{event_id2}': {reason}",
            code="DEDUPLICATION_CONFLICT"
        )
        self.event_id1 = event_id1
        self.event_id2 = event_id2
        self.reason = reason


class EventRetractedError(EventDomainError):
    """Raised when an operation targets an event that has been officially retracted."""
    def __init__(self, event_id: str, reason: Optional[str] = None):
        super().__init__(
            f"Event '{event_id}' was retracted: {reason or 'No reason provided'}",
            code="EVENT_RETRACTED"
        )
        self.event_id = event_id
        self.reason = reason


class EventSourceNotAuthorizedError(EventDomainError):
    """Raised when user or tenant lacks entitlement to an underlying event source record."""
    def __init__(self, source_id: str, required_tier: str = "INSTITUTIONAL"):
        super().__init__(
            f"Access denied to event source '{source_id}'. Requires {required_tier} entitlement tier.",
            code="SOURCE_ACCESS_DENIED"
        )
        self.source_id = source_id
        self.required_tier = required_tier


class EventRateMathError(EventDomainError):
    """Raised when monetary policy rate or basis point calculations are mathematically invalid."""
    def __init__(self, reason: str):
        super().__init__(f"Rate mathematical evaluation error: {reason}", code="RATE_MATH_ERROR")
        self.reason = reason


class EventMergeSplitValidationError(EventDomainError):
    """Raised when an event merge or split request is structurally invalid."""
    def __init__(self, reason: str):
        super().__init__(f"Merge/Split validation failed: {reason}", code="MERGE_SPLIT_VALIDATION_ERROR")
        self.reason = reason


class EventQuarantineError(EventDomainError):
    """Raised when an unvalidated event candidate fails quality gates and is moved to quarantine."""
    def __init__(self, candidate_key: str, reason: str):
        super().__init__(
            f"Event candidate '{candidate_key}' failed quality verification and is quarantined: {reason}",
            code="EVENT_QUARANTINED"
        )
        self.candidate_key = candidate_key
        self.reason = reason
