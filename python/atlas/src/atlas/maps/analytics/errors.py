"""Typed Domain Exceptions for ATLAS Spatial Analytics (Stage 131).

Defines structured, auditable domain errors for H3 indexing, resolution constraints,
dataset entitlements, privacy suppression, and query limits.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class SpatialAnalyticsDomainError(Exception):
    """Base domain exception for all spatial analytics operations."""

    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class InvalidH3CellError(SpatialAnalyticsDomainError):
    """Raised when an H3 cell index is malformed or invalid."""

    def __init__(self, cell_id: str, reason: str = "Invalid H3 index"):
        super().__init__(
            message=f"H3 cell '{cell_id}' is invalid: {reason}",
            error_code="INVALID_H3_CELL",
            details={"cell_id": cell_id, "reason": reason},
        )


class InvalidH3ResolutionError(SpatialAnalyticsDomainError):
    """Raised when an H3 resolution is out of supported range (0-15)."""

    def __init__(self, resolution: int, min_res: int = 0, max_res: int = 15):
        super().__init__(
            message=f"H3 resolution {resolution} is out of permitted range [{min_res}, {max_res}].",
            error_code="INVALID_H3_RESOLUTION",
            details={
                "resolution": resolution,
                "min_resolution": min_res,
                "max_resolution": max_res,
            },
        )


class ExcessiveH3ResolutionError(SpatialAnalyticsDomainError):
    """Raised when the requested resolution would exceed safe computational or query bounds."""

    def __init__(self, resolution: int, max_allowed: int, estimated_cells: int):
        super().__init__(
            message=(
                f"H3 resolution {resolution} exceeds current viewport budget limit "
                f"(max {max_allowed}, estimated cells: {estimated_cells})."
            ),
            error_code="EXCESSIVE_H3_RESOLUTION",
            details={
                "resolution": resolution,
                "max_allowed": max_allowed,
                "estimated_cells": estimated_cells,
            },
        )


class UnauthorizedSpatialDatasetError(SpatialAnalyticsDomainError):
    """Raised when access to an analytical dataset is denied by policy or tenant isolation."""

    def __init__(
        self, dataset_id: str, user_id: Optional[str] = None, tenant_id: Optional[str] = None
    ):
        super().__init__(
            message=f"Access to analytical dataset '{dataset_id}' is unauthorized for current principal.",
            error_code="UNAUTHORIZED_SPATIAL_DATASET",
            details={"dataset_id": dataset_id, "user_id": user_id, "tenant_id": tenant_id},
        )


class SpatialMetricNotAllowedError(SpatialAnalyticsDomainError):
    """Raised when a metric or aggregation method is unsupported or invalid for a dataset."""

    def __init__(self, metric_id: str, dataset_id: str, reason: str):
        super().__init__(
            message=f"Metric '{metric_id}' cannot be computed for dataset '{dataset_id}': {reason}",
            error_code="SPATIAL_METRIC_NOT_ALLOWED",
            details={"metric_id": metric_id, "dataset_id": dataset_id, "reason": reason},
        )


class PrivacySuppressionError(SpatialAnalyticsDomainError):
    """Raised when cell drill-down or raw observation access is blocked by privacy suppression."""

    def __init__(self, cell_id: str, contributor_count: int, threshold: int):
        super().__init__(
            message=(
                f"Detailed records for cell '{cell_id}' are suppressed for privacy "
                f"({contributor_count} contributors < minimum threshold of {threshold})."
            ),
            error_code="PRIVACY_SUPPRESSED",
            details={
                "cell_id": cell_id,
                "contributor_count": contributor_count,
                "threshold": threshold,
            },
        )


class SpatialQueryTimeoutError(SpatialAnalyticsDomainError):
    """Raised when a spatial analytical query exceeds its allocated time budget."""

    def __init__(self, query_id: str, timeout_seconds: float):
        super().__init__(
            message=f"Spatial analytical query '{query_id}' timed out after {timeout_seconds}s.",
            error_code="SPATIAL_QUERY_TIMEOUT",
            details={"query_id": query_id, "timeout_seconds": timeout_seconds},
        )


class MaterializationJobNotFoundError(SpatialAnalyticsDomainError):
    """Raised when an aggregate materialization job is not found."""

    def __init__(self, job_id: str):
        super().__init__(
            message=f"Materialization job '{job_id}' not found.",
            error_code="MATERIALIZATION_JOB_NOT_FOUND",
            details={"job_id": job_id},
        )


class SourceEntitlementRevokedError(SpatialAnalyticsDomainError):
    """Raised when a dataset source entitlement is expired or revoked."""

    def __init__(self, dataset_id: str, source_id: str):
        super().__init__(
            message=f"Source entitlement for dataset '{dataset_id}' (source '{source_id}') has been revoked.",
            error_code="SOURCE_ENTITLEMENT_REVOKED",
            details={"dataset_id": dataset_id, "source_id": source_id},
        )
