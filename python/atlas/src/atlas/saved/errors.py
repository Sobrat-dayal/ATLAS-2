"""Domain Exceptions for Stage 119 - Universal Saved System and Cross-Module Library."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class SavedError(Exception):
    """Base exception for all Saved domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "SAVED_OPERATION_FAILED",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class SavedItemNotFoundError(SavedError):
    def __init__(self, saved_item_id: str) -> None:
        super().__init__(
            message=f"Saved item '{saved_item_id}' not found.",
            code="SAVED_ITEM_NOT_FOUND",
            status_code=404,
            details={"saved_item_id": saved_item_id},
        )


class SavedItemAccessDeniedError(SavedError):
    def __init__(self, saved_item_id: str, user_id: str) -> None:
        super().__init__(
            message=f"Access denied to saved item '{saved_item_id}' for user '{user_id}'.",
            code="SAVED_ITEM_ACCESS_DENIED",
            status_code=403,
            details={"saved_item_id": saved_item_id, "user_id": user_id},
        )


class SavedTargetTypeUnsupportedError(SavedError):
    def __init__(self, target_type: str) -> None:
        super().__init__(
            message=f"Target type '{target_type}' is unsupported.",
            code="SAVED_TARGET_TYPE_UNSUPPORTED",
            status_code=400,
            details={"target_type": target_type},
        )


class SavedTargetIdInvalidError(SavedError):
    def __init__(self, target_id: str, reason: str = "Target ID cannot be empty.") -> None:
        super().__init__(
            message=f"Target ID '{target_id}' is invalid: {reason}",
            code="SAVED_TARGET_ID_INVALID",
            status_code=400,
            details={"target_id": target_id, "reason": reason},
        )


class SavedTargetNotFoundError(SavedError):
    def __init__(self, target_type: str, target_id: str) -> None:
        super().__init__(
            message=f"Target resource of type '{target_type}' with ID '{target_id}' was not found.",
            code="SAVED_TARGET_NOT_FOUND",
            status_code=404,
            details={"target_type": target_type, "target_id": target_id},
        )


class SavedTargetAccessDeniedError(SavedError):
    def __init__(self, target_type: str, target_id: str) -> None:
        super().__init__(
            message=f"Access denied to underlying target resource '{target_type}:{target_id}'.",
            code="SAVED_TARGET_ACCESS_DENIED",
            status_code=403,
            details={"target_type": target_type, "target_id": target_id},
        )


class SavedTargetSourceRestrictedError(SavedError):
    def __init__(
        self, target_type: str, target_id: str, reason: str = "Provider entitlement required."
    ) -> None:
        super().__init__(
            message=f"Access to source data for '{target_type}:{target_id}' is restricted: {reason}",
            code="SAVED_TARGET_SOURCE_RESTRICTED",
            status_code=403,
            details={"target_type": target_type, "target_id": target_id, "reason": reason},
        )


class SavedTargetSupersededError(SavedError):
    def __init__(self, target_type: str, target_id: str, latest_revision_id: str) -> None:
        super().__init__(
            message=f"Target resource '{target_type}:{target_id}' has been superseded by revision '{latest_revision_id}'.",
            code="SAVED_TARGET_SUPERSEDED",
            status_code=409,
            details={
                "target_type": target_type,
                "target_id": target_id,
                "latest_revision_id": latest_revision_id,
            },
        )


class SavedTargetUnavailableError(SavedError):
    def __init__(self, target_type: str, target_id: str, reason: str) -> None:
        super().__init__(
            message=f"Target resource '{target_type}:{target_id}' is unavailable: {reason}",
            code="SAVED_TARGET_UNAVAILABLE",
            status_code=503,
            details={"target_type": target_type, "target_id": target_id, "reason": reason},
        )


class SavedItemAlreadyExistsError(SavedError):
    def __init__(self, target_type: str, target_id: str, existing_saved_item_id: str) -> None:
        super().__init__(
            message=f"Resource '{target_type}:{target_id}' is already saved with ID '{existing_saved_item_id}'.",
            code="SAVED_ITEM_ALREADY_EXISTS",
            status_code=409,
            details={
                "target_type": target_type,
                "target_id": target_id,
                "existing_saved_item_id": existing_saved_item_id,
            },
        )


class SavedCollectionNotFoundError(SavedError):
    def __init__(self, collection_id: str) -> None:
        super().__init__(
            message=f"Collection '{collection_id}' not found.",
            code="SAVED_COLLECTION_NOT_FOUND",
            status_code=404,
            details={"collection_id": collection_id},
        )


class SavedCollectionAccessDeniedError(SavedError):
    def __init__(self, collection_id: str, user_id: str) -> None:
        super().__init__(
            message=f"Access denied to collection '{collection_id}' for user '{user_id}'.",
            code="SAVED_COLLECTION_ACCESS_DENIED",
            status_code=403,
            details={"collection_id": collection_id, "user_id": user_id},
        )


class SavedCollectionDuplicateNameError(SavedError):
    def __init__(self, name: str) -> None:
        super().__init__(
            message=f"A collection named '{name}' already exists in this scope.",
            code="SAVED_COLLECTION_DUPLICATE_NAME",
            status_code=409,
            details={"name": name},
        )


class SavedCollectionHierarchyCycleError(SavedError):
    def __init__(self, collection_id: str, target_parent_id: str) -> None:
        super().__init__(
            message=f"Cannot set parent to '{target_parent_id}': creates a cyclical collection hierarchy for '{collection_id}'.",
            code="SAVED_COLLECTION_HIERARCHY_CYCLE",
            status_code=400,
            details={"collection_id": collection_id, "target_parent_id": target_parent_id},
        )


class SavedCollectionMaxDepthError(SavedError):
    def __init__(self, max_depth: int = 5) -> None:
        super().__init__(
            message=f"Collection hierarchy exceeds maximum allowed depth of {max_depth}.",
            code="SAVED_COLLECTION_MAX_DEPTH",
            status_code=400,
            details={"max_depth": max_depth},
        )


class SavedCollectionMembershipExistsError(SavedError):
    def __init__(self, collection_id: str, saved_item_id: str) -> None:
        super().__init__(
            message=f"Saved item '{saved_item_id}' is already a member of collection '{collection_id}'.",
            code="SAVED_COLLECTION_MEMBERSHIP_EXISTS",
            status_code=409,
            details={"collection_id": collection_id, "saved_item_id": saved_item_id},
        )


class SavedCollectionMembershipNotFoundError(SavedError):
    def __init__(self, collection_id: str, saved_item_id: str) -> None:
        super().__init__(
            message=f"Saved item '{saved_item_id}' is not a member of collection '{collection_id}'.",
            code="SAVED_COLLECTION_MEMBERSHIP_NOT_FOUND",
            status_code=404,
            details={"collection_id": collection_id, "saved_item_id": saved_item_id},
        )


class SavedTagNotFoundError(SavedError):
    def __init__(self, tag_id: str) -> None:
        super().__init__(
            message=f"Tag '{tag_id}' not found.",
            code="SAVED_TAG_NOT_FOUND",
            status_code=404,
            details={"tag_id": tag_id},
        )


class SavedTagAlreadyExistsError(SavedError):
    def __init__(self, name: str) -> None:
        super().__init__(
            message=f"Tag '{name}' already exists.",
            code="SAVED_TAG_ALREADY_EXISTS",
            status_code=409,
            details={"name": name},
        )


class SavedConfigurationInvalidError(SavedError):
    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Saved view configuration is invalid: {reason}",
            code="SAVED_CONFIGURATION_INVALID",
            status_code=422,
            details={"reason": reason},
        )


class SavedConfigurationUnsupportedVersionError(SavedError):
    def __init__(self, schema_version: int, supported_versions: List[int]) -> None:
        super().__init__(
            message=f"Configuration schema version {schema_version} is unsupported (supported: {supported_versions}).",
            code="SAVED_CONFIGURATION_UNSUPPORTED_VERSION",
            status_code=400,
            details={"schema_version": schema_version, "supported_versions": supported_versions},
        )


class SavedConfigurationMigrationFailedError(SavedError):
    def __init__(self, from_version: int, to_version: int, reason: str) -> None:
        super().__init__(
            message=f"Failed to migrate configuration from v{from_version} to v{to_version}: {reason}",
            code="SAVED_CONFIGURATION_MIGRATION_FAILED",
            status_code=500,
            details={"from_version": from_version, "to_version": to_version, "reason": reason},
        )


class SavedConfigurationTooLargeError(SavedError):
    def __init__(self, size_bytes: int, max_bytes: int = 262144) -> None:
        super().__init__(
            message=f"Configuration payload size ({size_bytes} bytes) exceeds limit of {max_bytes} bytes (256 KB).",
            code="SAVED_CONFIGURATION_TOO_LARGE",
            status_code=413,
            details={"size_bytes": size_bytes, "max_bytes": max_bytes},
        )


class SavedItemVersionConflictError(SavedError):
    def __init__(self, saved_item_id: str, current_version: int, provided_version: int) -> None:
        super().__init__(
            message=f"Conflict updating saved item '{saved_item_id}': current version is {current_version}, provided is {provided_version}.",
            code="SAVED_ITEM_VERSION_CONFLICT",
            status_code=409,
            details={
                "saved_item_id": saved_item_id,
                "current_version": current_version,
                "provided_version": provided_version,
            },
        )


class SavedItemRestoreUnavailableError(SavedError):
    def __init__(self, saved_item_id: str, reason: str) -> None:
        super().__init__(
            message=f"Saved item '{saved_item_id}' cannot be restored: {reason}",
            code="SAVED_ITEM_RESTORE_UNAVAILABLE",
            status_code=400,
            details={"saved_item_id": saved_item_id, "reason": reason},
        )


class SavedBulkOperationPartialFailureError(SavedError):
    def __init__(
        self, succeeded_count: int, failed_count: int, failures: List[Dict[str, Any]]
    ) -> None:
        super().__init__(
            message=f"Bulk operation completed with partial failures: {succeeded_count} succeeded, {failed_count} failed.",
            code="SAVED_BULK_OPERATION_PARTIAL_FAILURE",
            status_code=207,
            details={
                "succeeded_count": succeeded_count,
                "failed_count": failed_count,
                "failures": failures,
            },
        )


class SavedRateLimitExceededError(SavedError):
    def __init__(self, operation: str, retry_after_seconds: int = 60) -> None:
        super().__init__(
            message=f"Rate limit exceeded for saved operation '{operation}'. Retry after {retry_after_seconds}s.",
            code="SAVED_RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"operation": operation, "retry_after_seconds": retry_after_seconds},
        )


class SavedOperationFailedError(SavedError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="SAVED_OPERATION_FAILED",
            status_code=500,
        )
