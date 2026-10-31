"""Errors for ATLAS God's Eye Financial Intelligence (Stage 140).

Enforces institutional invariants:
- Bitemporal look-ahead enforcement
- Multi-tenant data segregation
- Source entitlement and revocation protection
- Graph traversal bounding
- Strict semantic boundaries (no fake omniscience, no speculative damage)
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from atlas.intelligence.errors import IntelligenceDomainError


class GodsEyeDomainError(IntelligenceDomainError):
    """Base exception for all God's Eye Financial Intelligence operations."""

    def __init__(
        self,
        message: str,
        code: str = "GODS_EYE_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code=code, details=details)


class GodsEyeLookAheadViolationError(GodsEyeDomainError):
    """Raised when an as-of query attempts to inspect data known only after the specified as-of date."""

    def __init__(
        self,
        as_of: str,
        record_known_at: str,
        message: str = "Historical reconstruction query violates bitemporal point-in-time integrity (look-ahead bias).",
    ):
        super().__init__(
            message,
            code="GODS_EYE_LOOK_AHEAD_VIOLATION",
            details={"as_of": as_of, "record_known_at": record_known_at},
        )


class GodsEyeTenantAccessDeniedError(GodsEyeDomainError):
    """Raised when an unauthorized principal attempts to access private portfolios or tenant-isolated data."""

    def __init__(
        self,
        resource_id: str,
        tenant_id: Optional[str] = None,
        message: str = "Access to private portfolio or tenant-isolated intelligence is denied.",
    ):
        super().__init__(
            message,
            code="GODS_EYE_TENANT_ACCESS_DENIED",
            details={"resource_id": resource_id, "tenant_id": tenant_id},
        )


class GodsEyeSourceUnavailableError(GodsEyeDomainError):
    """Raised when a required data source is unavailable or revoked."""

    def __init__(
        self,
        source_id: str,
        status: str = "DEGRADED",
        message: str = "Intelligence source is currently unavailable or access has been revoked.",
    ):
        super().__init__(
            message,
            code="GODS_EYE_SOURCE_UNAVAILABLE",
            details={"source_id": source_id, "status": status},
        )


class GodsEyeEntityNotFoundError(GodsEyeDomainError):
    """Raised when an entity requested for situational awareness cannot be resolved."""

    def __init__(
        self,
        entity_id: str,
        message: str = "Canonical entity could not be found or resolved in the knowledge graph.",
    ):
        super().__init__(
            message,
            code="GODS_EYE_ENTITY_NOT_FOUND",
            details={"entity_id": entity_id},
        )


class GodsEyeTraversalLimitExceededError(GodsEyeDomainError):
    """Raised when a graph traversal exceeds depth or node limits to protect platform stability."""

    def __init__(
        self,
        requested_depth: int,
        max_allowed_depth: int = 3,
        message: str = "Graph traversal exceeded maximum allowed depth or fanout limit.",
    ):
        super().__init__(
            message,
            code="GODS_EYE_TRAVERSAL_LIMIT_EXCEEDED",
            details={"requested_depth": requested_depth, "max_allowed_depth": max_allowed_depth},
        )


class GodsEyeQuotaExceededError(GodsEyeDomainError):
    """Raised when rate or query compute budget is exceeded."""

    def __init__(
        self,
        message: str = "God's Eye query compute quota or rate limit exceeded.",
    ):
        super().__init__(message, code="GODS_EYE_QUOTA_EXCEEDED")

