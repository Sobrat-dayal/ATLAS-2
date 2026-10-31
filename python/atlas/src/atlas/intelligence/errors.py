"""Domain errors for ATLAS INTELLIGENCE V1 (Stage 138).

Enforces institutional invariants:
- Typed failure modes
- Partial failure representation without whole-dashboard failure
- Point-in-time historical protection (zero look-ahead)
- Multi-tenant boundary protection
- Source entitlement enforcement
"""

from __future__ import annotations
from typing import Optional, Dict, Any


class IntelligenceDomainError(Exception):
    """Base exception for all Intelligence Subsystem errors."""
    def __init__(self, message: str, code: str = "INTELLIGENCE_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class IntelligenceSourceUnavailableError(IntelligenceDomainError):
    def __init__(self, source_id: str, message: str = "Requested intelligence source is currently unavailable."):
        super().__init__(message, code="INTELLIGENCE_SOURCE_UNAVAILABLE", details={"source_id": source_id})
        self.source_id = source_id


class IntelligenceEventNotFoundError(IntelligenceDomainError):
    def __init__(self, event_id: str):
        super().__init__(f"Universal event '{event_id}' not found.", code="INTELLIGENCE_EVENT_NOT_FOUND", details={"event_id": event_id})
        self.event_id = event_id


class IntelligenceEntityNotFoundError(IntelligenceDomainError):
    def __init__(self, entity_id: str, node_type: Optional[str] = None):
        super().__init__(f"Entity '{entity_id}' of type '{node_type}' not found.", code="INTELLIGENCE_ENTITY_NOT_FOUND", details={"entity_id": entity_id, "node_type": node_type})
        self.entity_id = entity_id


class IntelligenceExposureUnavailableError(IntelligenceDomainError):
    def __init__(self, message: str = "No supported quantitative exposure is available from authorized data."):
        super().__init__(message, code="INTELLIGENCE_EXPOSURE_UNAVAILABLE")


class IntelligenceHistoryUnsupportedError(IntelligenceDomainError):
    def __init__(self, dataset: str, as_of: str):
        super().__init__(f"Historical as-of queries are not supported for dataset '{dataset}' at '{as_of}'.", code="INTELLIGENCE_HISTORY_UNSUPPORTED", details={"dataset": dataset, "as_of": as_of})


class IntelligenceEntitlementRequiredError(IntelligenceDomainError):
    def __init__(self, source_id: str, message: str = "Active dataset license or source entitlement required."):
        super().__init__(message, code="INTELLIGENCE_ENTITLEMENT_REQUIRED", details={"source_id": source_id})
        self.source_id = source_id


class IntelligenceLookAheadViolationError(IntelligenceDomainError):
    def __init__(self, message: str = "Historical query violates bitemporal point-in-time integrity (look-ahead bias)."):
        super().__init__(message, code="INTELLIGENCE_LOOK_AHEAD_VIOLATION")


class IntelligenceTenantAccessDeniedError(IntelligenceDomainError):
    def __init__(self, message: str = "Access denied: requested intelligence asset belongs to another tenant."):
        super().__init__(message, code="INTELLIGENCE_TENANT_ACCESS_DENIED")


class IntelligenceAmbiguousIdentityError(IntelligenceDomainError):
    def __init__(self, query: str, candidates: list):
        super().__init__(f"Ambiguous entity query '{query}' matched multiple canonical entities.", code="INTELLIGENCE_AMBIGUOUS_IDENTITY", details={"query": query, "candidate_count": len(candidates)})
        self.candidates = candidates

