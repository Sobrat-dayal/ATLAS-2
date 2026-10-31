"""Typed Domain Errors for ATLAS Intelligence Scoring (Stage 139)."""

from typing import Any, Dict, Optional


class ScoringDomainError(Exception):
    """Base exception for all Intelligence Scoring domain errors."""

    def __init__(self, message: str, code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ScoringObjectiveNotFoundError(ScoringDomainError):
    """Raised when an unknown scoring objective is requested."""

    def __init__(self, objective_id: str):
        super().__init__(
            f"Scoring objective '{objective_id}' not found in registry.",
            code="SCORING_OBJECTIVE_NOT_FOUND",
            details={"objective_id": objective_id},
        )


class ScoringModelNotFoundError(ScoringDomainError):
    """Raised when an unknown scoring model or version is requested."""

    def __init__(self, model_id: str, version: Optional[str] = None):
        msg = f"Scoring model '{model_id}' (version={version}) not found." if version else f"Scoring model '{model_id}' not found."
        super().__init__(
            msg,
            code="SCORING_MODEL_NOT_FOUND",
            details={"model_id": model_id, "version": version},
        )


class ScoringPolicyNotFoundError(ScoringDomainError):
    """Raised when a scoring policy is not registered."""

    def __init__(self, policy_id: str):
        super().__init__(
            f"Scoring policy '{policy_id}' not found.",
            code="SCORING_POLICY_NOT_FOUND",
            details={"policy_id": policy_id},
        )


class ScoringEligibilityError(ScoringDomainError):
    """Raised when a candidate subject is not eligible for scoring under the objective."""

    def __init__(self, reason: str, subject_id: str, objective_id: str):
        super().__init__(
            f"Subject '{subject_id}' is not eligible for objective '{objective_id}': {reason}",
            code="SCORING_NOT_ELIGIBLE",
            details={"subject_id": subject_id, "objective_id": objective_id, "reason": reason},
        )


class ScoringLookAheadViolationError(ScoringDomainError):
    """Raised when input features or sources violate the bitemporal known_as_of horizon."""

    def __init__(self, known_as_of: str, feature_available_at: str, feature_id: str):
        super().__init__(
            f"Look-ahead violation: Feature '{feature_id}' available at {feature_available_at} > as-of {known_as_of}.",
            code="SCORING_LOOK_AHEAD_VIOLATION",
            details={"known_as_of": known_as_of, "feature_available_at": feature_available_at, "feature_id": feature_id},
        )


class ScoringQuotaExceededError(ScoringDomainError):
    """Raised when ranking or scoring batch requests exceed system limits."""

    def __init__(self, requested: int, limit: int):
        super().__init__(
            f"Scoring request size {requested} exceeds institutional limit of {limit}.",
            code="SCORING_QUOTA_EXCEEDED",
            details={"requested": requested, "limit": limit},
        )


class ScoringTenantAccessDeniedError(ScoringDomainError):
    """Raised when attempting to access private portfolio attention or tenant-isolated scores."""

    def __init__(self, tenant_id: str, resource_type: str, resource_id: str):
        super().__init__(
            f"Access denied: Tenant '{tenant_id}' cannot access private {resource_type} '{resource_id}'.",
            code="SCORING_TENANT_ACCESS_DENIED",
            details={"tenant_id": tenant_id, "resource_type": resource_type, "resource_id": resource_id},
        )


class ScoringSourceEntitlementError(ScoringDomainError):
    """Raised when a feature depends on a data provider source the tenant is not licensed for."""

    def __init__(self, source_id: str, tenant_id: str):
        super().__init__(
            f"Tenant '{tenant_id}' lacks entitlement license for scoring source '{source_id}'.",
            code="SCORING_SOURCE_NOT_ENTITLED",
            details={"source_id": source_id, "tenant_id": tenant_id},
        )


class ScoringModelValidationError(ScoringDomainError):
    """Raised when a candidate model version fails governance validation gates."""

    def __init__(self, model_id: str, version: str, failure_reasons: list):
        super().__init__(
            f"Model '{model_id}' version '{version}' failed validation: {'; '.join(failure_reasons)}",
            code="SCORING_MODEL_VALIDATION_FAILED",
            details={"model_id": model_id, "version": version, "failure_reasons": failure_reasons},
        )


class ScoringUnauthorizedActivationError(ScoringDomainError):
    """Raised when an unauthorized user attempts to activate or promote a production model."""

    def __init__(self, user_id: str, action: str):
        super().__init__(
            f"User '{user_id}' is unauthorized to perform model governance action '{action}'.",
            code="SCORING_UNAUTHORIZED_GOVERNANCE",
            details={"user_id": user_id, "action": action},
        )

