"""Domain error types for ATLAS Approval Inbox and Decision Architecture (Stage 54)."""


class ApprovalError(Exception):
    """Base exception for all approval errors."""

    def __init__(self, message: str, code: str = "APPROVAL_ERROR"):
        super().__init__(message)
        self.code = code


class ApprovalNotFoundError(ApprovalError):
    """Raised when an approval request does not exist or does not belong to the user."""

    def __init__(self, approval_id: str):
        super().__init__(
            f"Approval request '{approval_id}' not found",
            code="APPROVAL_NOT_FOUND",
        )


class ApprovalExpiredError(ApprovalError):
    """Raised when an approval decision is attempted on an expired request."""

    def __init__(self, message: str = "Approval request has expired and cannot be decided"):
        super().__init__(message, code="APPROVAL_EXPIRED")


class ApprovalAlreadyDecidedError(ApprovalError):
    """Raised when an approval request is already in a terminal decided state."""

    def __init__(self, current_status: str):
        super().__init__(
            f"Approval request has already been decided (status: {current_status})",
            code="APPROVAL_ALREADY_DECIDED",
        )


class ApprovalConflictError(ApprovalError):
    """Raised when optimistic concurrency conflict occurs during decision."""

    def __init__(self, message: str = "Approval request was modified by another operation"):
        super().__init__(message, code="APPROVAL_VERSION_CONFLICT")


class UntrustedProducerError(ApprovalError):
    """Raised when a non-allowlisted producer attempts to originate an approval request."""

    def __init__(self, producer_key: str):
        super().__init__(
            f"Originating producer '{producer_key}' is not in the trusted producer allowlist",
            code="UNTRUSTED_APPROVAL_PRODUCER",
        )


class InvalidActionKindError(ApprovalError):
    """Raised when an unallowlisted action kind is requested."""

    def __init__(self, action_kind: str):
        super().__init__(
            f"Action kind '{action_kind}' is not in the allowed action kinds allowlist",
            code="INVALID_APPROVAL_ACTION_KIND",
        )


class InvalidApprovalPayloadError(ApprovalError):
    """Raised when approval request fields fail validation."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_APPROVAL_PAYLOAD")


class ApprovalIdempotencyConflictError(ApprovalError):
    """Raised when an approval idempotency key is reused with conflicting content."""

    def __init__(self, message: str = "Conflicting decision payload for idempotency key"):
        super().__init__(message, code="IDEMPOTENCY_CONFLICT")
