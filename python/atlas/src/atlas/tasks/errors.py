"""Domain error types for ATLAS Personal Tasks (Stage 54)."""


class TaskError(Exception):
    """Base exception for all personal task errors."""

    def __init__(self, message: str, code: str = "TASK_ERROR"):
        super().__init__(message)
        self.code = code


class TaskNotFoundError(TaskError):
    """Raised when a requested task does not exist or does not belong to the user."""

    def __init__(self, task_id: str):
        super().__init__(f"Task '{task_id}' not found", code="TASK_NOT_FOUND")


class TaskConflictError(TaskError):
    """Raised when optimistic concurrency conflict occurs."""

    def __init__(self, message: str = "Task was modified by another operation"):
        super().__init__(message, code="TASK_VERSION_CONFLICT")


class InvalidTaskTransitionError(TaskError):
    """Raised when an illegal task lifecycle transition is attempted."""

    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            f"Cannot transition task from {current_status} to {target_status}",
            code="INVALID_TASK_TRANSITION",
        )


class InvalidTaskPayloadError(TaskError):
    """Raised when task fields fail domain validation."""

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_TASK_PAYLOAD")


class TaskIdempotencyConflictError(TaskError):
    """Raised when an idempotency key is reused with conflicting content."""

    def __init__(self, message: str = "Conflicting task payload for idempotency key"):
        super().__init__(message, code="IDEMPOTENCY_CONFLICT")
