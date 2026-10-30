"""Typed error taxonomy for ATLAS AI Financial Action Engine (Stage 128, Part LXXVII)."""

from __future__ import annotations

from typing import Any, Dict, Optional


class AiActionError(Exception):
    """Base exception for all AI action errors."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code,
        }


class AiActionUnsupportedError(AiActionError):
    def __init__(self, action_type: str) -> None:
        super().__init__(
            code="AI_ACTION_UNSUPPORTED",
            message=f"Action type '{action_type}' is not supported by the ATLAS AI Action Engine.",
            details={"action_type": action_type},
            status_code=400,
        )


class AiActionInvalidIntentError(AiActionError):
    def __init__(self, intent: str, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_INVALID_INTENT",
            message=f"Could not translate intent into a valid financial action: {reason}",
            details={"intent": intent, "reason": reason},
            status_code=422,
        )


class AiActionAmbiguousTargetError(AiActionError):
    def __init__(self, target_resource_type: str, matches: list[str]) -> None:
        super().__init__(
            code="AI_ACTION_AMBIGUOUS_TARGET",
            message=f"Ambiguous target {target_resource_type}. Multiple candidates found: {matches}. Please specify.",
            details={"target_resource_type": target_resource_type, "matches": matches},
            status_code=409,
        )


class AiActionTargetNotFoundError(AiActionError):
    def __init__(self, target_resource_type: str, resource_id: str) -> None:
        super().__init__(
            code="AI_ACTION_TARGET_NOT_FOUND",
            message=f"Target {target_resource_type} '{resource_id}' was not found.",
            details={"target_resource_type": target_resource_type, "resource_id": resource_id},
            status_code=404,
        )


class AiActionAccessDeniedError(AiActionError):
    def __init__(
        self, resource_type: str, resource_id: str, reason: str = "Insufficient permissions"
    ) -> None:
        super().__init__(
            code="AI_ACTION_ACCESS_DENIED",
            message=f"Access denied to {resource_type} '{resource_id}': {reason}",
            details={"resource_type": resource_type, "resource_id": resource_id, "reason": reason},
            status_code=403,
        )


class AiActionProviderDisclosureDeniedError(AiActionError):
    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_PROVIDER_DISCLOSURE_DENIED",
            message=f"Provider disclosure policy prevents sharing sensitive financial data with '{provider}': {reason}",
            details={"provider": provider, "reason": reason},
            status_code=403,
        )


class AiActionSchemaInvalidError(AiActionError):
    def __init__(self, errors: Dict[str, Any]) -> None:
        super().__init__(
            code="AI_ACTION_SCHEMA_INVALID",
            message="Proposed action arguments failed schema validation.",
            details={"errors": errors},
            status_code=422,
        )


class AiActionParameterUnsupportedError(AiActionError):
    def __init__(self, parameter: str, value: Any, supported: list[Any]) -> None:
        super().__init__(
            code="AI_ACTION_PARAMETER_UNSUPPORTED",
            message=f"Parameter '{parameter}' value '{value}' is unsupported. Supported values: {supported}",
            details={"parameter": parameter, "value": value, "supported": supported},
            status_code=422,
        )


class AiActionValidationFailedError(AiActionError):
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="AI_ACTION_VALIDATION_FAILED",
            message=f"Action validation failed: {reason}",
            details=details or {"reason": reason},
            status_code=422,
        )


class AiActionPreviewUnavailableError(AiActionError):
    def __init__(self, action_id: str, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_PREVIEW_UNAVAILABLE",
            message=f"Preview unavailable for action '{action_id}': {reason}",
            details={"action_id": action_id, "reason": reason},
            status_code=400,
        )


class AiActionPreviewExpiredError(AiActionError):
    def __init__(self, preview_id: str) -> None:
        super().__init__(
            code="AI_ACTION_PREVIEW_EXPIRED",
            message=f"Action preview '{preview_id}' has expired. A fresh preview must be generated.",
            details={"preview_id": preview_id},
            status_code=410,
        )


class AiActionApprovalRequiredError(AiActionError):
    def __init__(self, action_id: str, policy: str) -> None:
        super().__init__(
            code="AI_ACTION_APPROVAL_REQUIRED",
            message=f"Action '{action_id}' requires explicit user confirmation under policy '{policy}'.",
            details={"action_id": action_id, "policy": policy},
            status_code=403,
        )


class AiActionApprovalDeniedError(AiActionError):
    def __init__(self, action_id: str, reason: Optional[str] = None) -> None:
        super().__init__(
            code="AI_ACTION_APPROVAL_DENIED",
            message=f"Action '{action_id}' was denied by the user: {reason or 'No reason provided'}",
            details={"action_id": action_id, "reason": reason},
            status_code=403,
        )


class AiActionApprovalExpiredError(AiActionError):
    def __init__(self, approval_id: str) -> None:
        super().__init__(
            code="AI_ACTION_APPROVAL_EXPIRED",
            message=f"Approval '{approval_id}' has expired. Execution blocked.",
            details={"approval_id": approval_id},
            status_code=410,
        )


class AiActionApprovalMismatchError(AiActionError):
    def __init__(self, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_APPROVAL_MISMATCH",
            message=f"Approval mismatch detected: {reason}",
            details={"reason": reason},
            status_code=403,
        )


class AiActionReplayDetectedError(AiActionError):
    def __init__(self, approval_id: str) -> None:
        super().__init__(
            code="AI_ACTION_REPLAY_DETECTED",
            message=f"Approval '{approval_id}' has already been consumed. Replay rejected.",
            details={"approval_id": approval_id},
            status_code=409,
        )


class AiActionResourceConflictError(AiActionError):
    def __init__(self, resource_id: str, expected_revision: str, actual_revision: str) -> None:
        super().__init__(
            code="AI_ACTION_RESOURCE_CONFLICT",
            message=(
                f"Resource conflict for '{resource_id}': expected revision '{expected_revision}', "
                f"but found '{actual_revision}'. Please re-preview before execution."
            ),
            details={
                "resource_id": resource_id,
                "expected_revision": expected_revision,
                "actual_revision": actual_revision,
            },
            status_code=409,
        )


class AiActionQuotaExceededError(AiActionError):
    def __init__(self, quota_type: str, limit: int) -> None:
        super().__init__(
            code="AI_ACTION_QUOTA_EXCEEDED",
            message=f"Quota exceeded for '{quota_type}'. Limit is {limit}.",
            details={"quota_type": quota_type, "limit": limit},
            status_code=429,
        )


class AiActionRateLimitedError(AiActionError):
    def __init__(self, retry_after_seconds: int = 30) -> None:
        super().__init__(
            code="AI_ACTION_RATE_LIMITED",
            message=f"Too many action requests. Please retry in {retry_after_seconds}s.",
            details={"retry_after_seconds": retry_after_seconds},
            status_code=429,
        )


class AiActionExecutionFailedError(AiActionError):
    def __init__(self, action_id: str, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_EXECUTION_FAILED",
            message=f"Execution of action '{action_id}' failed: {reason}",
            details={"action_id": action_id, "reason": reason},
            status_code=500,
        )


class AiActionPartialCompletionError(AiActionError):
    def __init__(self, plan_id: str, succeeded: list[str], failed: list[str]) -> None:
        super().__init__(
            code="AI_ACTION_PARTIAL_COMPLETION",
            message=f"Plan '{plan_id}' completed partially. Succeeded: {len(succeeded)}, Failed: {len(failed)}.",
            details={"plan_id": plan_id, "succeeded": succeeded, "failed": failed},
            status_code=207,
        )


class AiActionCancelledError(AiActionError):
    def __init__(self, action_id: str, reason: str = "User cancelled execution") -> None:
        super().__init__(
            code="AI_ACTION_CANCELLED",
            message=f"Action '{action_id}' was cancelled: {reason}",
            details={"action_id": action_id, "reason": reason},
            status_code=400,
        )


class AiActionTimeoutError(AiActionError):
    def __init__(self, action_id: str, timeout_seconds: int) -> None:
        super().__init__(
            code="AI_ACTION_TIMEOUT",
            message=f"Action '{action_id}' exceeded timeout limit of {timeout_seconds}s.",
            details={"action_id": action_id, "timeout_seconds": timeout_seconds},
            status_code=504,
        )


class AiActionUndoUnavailableError(AiActionError):
    def __init__(self, action_id: str, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_UNDO_UNAVAILABLE",
            message=f"Undo is unavailable for action '{action_id}': {reason}",
            details={"action_id": action_id, "reason": reason},
            status_code=400,
        )


class AiActionUndoConflictError(AiActionError):
    def __init__(self, action_id: str, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_UNDO_CONFLICT",
            message=f"Undo failed due to state conflict on action '{action_id}': {reason}",
            details={"action_id": action_id, "reason": reason},
            status_code=409,
        )


class AiActionSourceUnavailableError(AiActionError):
    def __init__(self, source_id: str) -> None:
        super().__init__(
            code="AI_ACTION_SOURCE_UNAVAILABLE",
            message=f"Financial data source '{source_id}' is temporarily unavailable.",
            details={"source_id": source_id},
            status_code=503,
        )


class AiActionDataQualityInsufficientError(AiActionError):
    def __init__(self, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_DATA_QUALITY_INSUFFICIENT",
            message=f"Data quality is insufficient for accurate calculation: {reason}",
            details={"reason": reason},
            status_code=422,
        )


class AiActionFinancialConstraintFailedError(AiActionError):
    def __init__(self, constraint: str, reason: str) -> None:
        super().__init__(
            code="AI_ACTION_FINANCIAL_CONSTRAINT_FAILED",
            message=f"Financial constraint violation ({constraint}): {reason}",
            details={"constraint": constraint, "reason": reason},
            status_code=422,
        )


class AiActionLedgerMutationProhibitedError(AiActionError):
    def __init__(self, attempted_operation: str) -> None:
        super().__init__(
            code="AI_ACTION_LEDGER_MUTATION_PROHIBITED",
            message=(
                f"Operation '{attempted_operation}' is strictly prohibited. The AI Action Engine cannot "
                "directly modify real transaction ledgers, cash balances, or accounting records."
            ),
            details={"attempted_operation": attempted_operation},
            status_code=403,
        )


class AiActionBrokerExecutionProhibitedError(AiActionError):
    def __init__(self, attempted_order: str) -> None:
        super().__init__(
            code="AI_ACTION_BROKER_EXECUTION_PROHIBITED",
            message=(
                f"Live broker order execution ('{attempted_order}') is strictly prohibited. "
                "Stage 128 only supports non-executing analytical and hypothetical proposals."
            ),
            details={"attempted_order": attempted_order},
            status_code=403,
        )


class AiActionInternalError(AiActionError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="AI_ACTION_INTERNAL_ERROR",
            message=f"An internal error occurred in the AI Action Engine: {message}",
            details=details or {},
            status_code=500,
        )
