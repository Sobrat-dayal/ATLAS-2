"""Universal Event Model Subsystem (Stage 135).

Institutional-grade canonical event representation, multi-clock temporal history,
zero look-ahead point-in-time as-of evaluation, multi-source deduplication,
and source-grounded evidence & claim registries.
"""

from .domain import (
    AtlasUniversalEvent,
    ClaimConflictStatus,
    DatePrecision,
    EventCategory,
    EventClaim,
    EventEvidence,
    EventGeographicScope,
    EventLifecycleStatus,
    EventRevision,
    EventSourceRecord,
    EventVerificationStatus,
    EvidenceRole,
    GeographicScopeType,
)
from .errors import (
    EventDeduplicationConflictError,
    EventDomainError,
    EventLookAheadViolationError,
    EventMergeSplitValidationError,
    EventNotFoundError,
    EventRetractedError,
    EventSourceNotAuthorizedError,
)
from .service import AtlasUniversalEventService

__all__ = [
    "AtlasUniversalEvent",
    "AtlasUniversalEventService",
    "ClaimConflictStatus",
    "DatePrecision",
    "EventCategory",
    "EventClaim",
    "EventDeduplicationConflictError",
    "EventDomainError",
    "EventEvidence",
    "EventGeographicScope",
    "EventLifecycleStatus",
    "EventLookAheadViolationError",
    "EventMergeSplitValidationError",
    "EventNotFoundError",
    "EventRetractedError",
    "EventRevision",
    "EventSourceNotAuthorizedError",
    "EventSourceRecord",
    "EventVerificationStatus",
    "EvidenceRole",
    "GeographicScopeType",
]

