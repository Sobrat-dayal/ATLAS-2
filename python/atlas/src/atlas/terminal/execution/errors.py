"""Typed exceptions for Stage 123 Terminal Execution Platform."""

from typing import Any, Dict, Optional

from atlas.terminal.errors import TerminalError


class TerminalExecutionNotFoundError(TerminalError):
    def __init__(self, execution_id: str):
        super().__init__(
            f"Terminal execution '{execution_id}' not found.",
            code="TERMINAL_EXECUTION_NOT_FOUND",
            status_code=404,
            details={"execution_id": execution_id},
        )


class TerminalExecutionAccessDeniedError(TerminalError):
    def __init__(self, execution_id: str, user_id: str):
        super().__init__(
            f"Access denied to execution '{execution_id}' for user '{user_id}'.",
            code="TERMINAL_EXECUTION_ACCESS_DENIED",
            status_code=403,
            details={"execution_id": execution_id, "user_id": user_id},
        )


class TerminalExecutionTypeUnsupportedError(TerminalError):
    def __init__(self, execution_type: str):
        super().__init__(
            f"Execution type '{execution_type}' is not supported.",
            code="TERMINAL_EXECUTION_TYPE_UNSUPPORTED",
            status_code=400,
            details={"execution_type": execution_type},
        )


class TerminalExecutionCapabilityDisabledError(TerminalError):
    def __init__(self, capability: str):
        super().__init__(
            f"Execution capability '{capability}' is currently disabled.",
            code="TERMINAL_EXECUTION_CAPABILITY_DISABLED",
            status_code=403,
            details={"capability": capability},
        )


class TerminalExecutionInputInvalidError(TerminalError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Invalid execution input: {message}",
            code="TERMINAL_EXECUTION_INPUT_INVALID",
            status_code=400,
            details=details,
        )


class TerminalExecutionInputTooLargeError(TerminalError):
    def __init__(self, current_bytes: int, max_bytes: int = 65536):
        super().__init__(
            f"Execution input size {current_bytes} bytes exceeds maximum allowed {max_bytes} bytes.",
            code="TERMINAL_EXECUTION_INPUT_TOO_LARGE",
            status_code=400,
            details={"current_bytes": current_bytes, "max_bytes": max_bytes},
        )


class TerminalExecutionQuotaExceededError(TerminalError):
    def __init__(
        self, message: str = "Execution quota exceeded. Maximum concurrent executions reached."
    ):
        super().__init__(
            message,
            code="TERMINAL_EXECUTION_QUOTA_EXCEEDED",
            status_code=429,
        )


class TerminalExecutionQueueFullError(TerminalError):
    def __init__(self, queue_size: int, max_queue: int = 10):
        super().__init__(
            f"Execution queue full ({queue_size}/{max_queue}). Please retry shortly.",
            code="TERMINAL_EXECUTION_QUEUE_FULL",
            status_code=429,
            details={"queue_size": queue_size, "max_queue": max_queue},
        )


class TerminalExecutionEnvironmentUnavailableError(TerminalError):
    def __init__(self, env_id: str):
        super().__init__(
            f"Execution environment '{env_id}' is unavailable.",
            code="TERMINAL_EXECUTION_ENVIRONMENT_UNAVAILABLE",
            status_code=400,
            details={"environment_id": env_id},
        )


class TerminalExecutionTimedOutError(TerminalError):
    def __init__(self, timeout_seconds: int):
        super().__init__(
            f"Execution timed out after {timeout_seconds} seconds.",
            code="TERMINAL_EXECUTION_TIMED_OUT",
            status_code=408,
            details={"timeout_seconds": timeout_seconds},
        )


class TerminalExecutionCancelledError(TerminalError):
    def __init__(self, execution_id: str):
        super().__init__(
            f"Execution '{execution_id}' was cancelled by user request.",
            code="TERMINAL_EXECUTION_CANCELLED",
            status_code=400,
            details={"execution_id": execution_id},
        )


class TerminalExecutionCancelFailedError(TerminalError):
    def __init__(self, execution_id: str, reason: str):
        super().__init__(
            f"Failed to cancel execution '{execution_id}': {reason}",
            code="TERMINAL_EXECUTION_CANCEL_FAILED",
            status_code=400,
            details={"execution_id": execution_id, "reason": reason},
        )


class TerminalExecutionResourceLimitExceededError(TerminalError):
    def __init__(self, resource: str, limit_value: Any):
        super().__init__(
            f"Execution resource limit exceeded for '{resource}': limit is {limit_value}.",
            code="TERMINAL_EXECUTION_RESOURCE_LIMIT_EXCEEDED",
            status_code=400,
            details={"resource": resource, "limit": limit_value},
        )


class TerminalExecutionSecurityDeniedError(TerminalError):
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Execution denied by security policy: {reason}",
            code="TERMINAL_EXECUTION_SECURITY_DENIED",
            status_code=403,
            details=details,
        )


class TerminalExecutionArtifactUnavailableError(TerminalError):
    def __init__(self, artifact_id: str):
        super().__init__(
            f"Execution artifact '{artifact_id}' not found or expired.",
            code="TERMINAL_EXECUTION_ARTIFACT_UNAVAILABLE",
            status_code=404,
            details={"artifact_id": artifact_id},
        )


class TerminalPythonEnvironmentUnsupportedError(TerminalError):
    def __init__(self, env_id: str):
        super().__init__(
            f"Python environment '{env_id}' is not supported.",
            code="TERMINAL_PYTHON_ENVIRONMENT_UNSUPPORTED",
            status_code=400,
            details={"environment_id": env_id},
        )


class TerminalPythonDataAccessDeniedError(TerminalError):
    def __init__(self, dataset_id: str):
        super().__init__(
            f"Access to dataset '{dataset_id}' from Python sandbox is denied.",
            code="TERMINAL_PYTHON_DATA_ACCESS_DENIED",
            status_code=403,
            details={"dataset_id": dataset_id},
        )


class TerminalSqlSourceNotFoundError(TerminalError):
    def __init__(self, source_id: str):
        super().__init__(
            f"SQL source '{source_id}' not found.",
            code="TERMINAL_SQL_SOURCE_NOT_FOUND",
            status_code=404,
            details={"source_id": source_id},
        )


class TerminalSqlSourceAccessDeniedError(TerminalError):
    def __init__(self, source_id: str, user_id: str):
        super().__init__(
            f"Access denied to SQL source '{source_id}' for user '{user_id}'.",
            code="TERMINAL_SQL_SOURCE_ACCESS_DENIED",
            status_code=403,
            details={"source_id": source_id, "user_id": user_id},
        )


class TerminalSqlStatementNotAllowedError(TerminalError):
    def __init__(
        self, statement_type: str, reason: str = "Only read-only SELECT statements are permitted."
    ):
        super().__init__(
            f"SQL statement '{statement_type}' is not allowed: {reason}",
            code="TERMINAL_SQL_STATEMENT_NOT_ALLOWED",
            status_code=400,
            details={"statement_type": statement_type, "reason": reason},
        )


class TerminalSqlQueryTimeoutError(TerminalError):
    def __init__(self, timeout_seconds: int):
        super().__init__(
            f"SQL query timed out after {timeout_seconds} seconds.",
            code="TERMINAL_SQL_QUERY_TIMEOUT",
            status_code=408,
            details={"timeout_seconds": timeout_seconds},
        )


class TerminalSqlQueryTooExpensiveError(TerminalError):
    def __init__(self, reason: str):
        super().__init__(
            f"SQL query rejected as too expensive: {reason}",
            code="TERMINAL_SQL_QUERY_TOO_EXPENSIVE",
            status_code=400,
            details={"reason": reason},
        )


class TerminalSqlResultLimitExceededError(TerminalError):
    def __init__(self, row_count: int, max_limit: int):
        super().__init__(
            f"SQL result row count ({row_count}) exceeded limit ({max_limit}).",
            code="TERMINAL_SQL_RESULT_LIMIT_EXCEEDED",
            status_code=400,
            details={"row_count": row_count, "max_limit": max_limit},
        )


class TerminalSqlQueryCancelledError(TerminalError):
    def __init__(self, query_id: str):
        super().__init__(
            f"SQL query '{query_id}' was cancelled.",
            code="TERMINAL_SQL_QUERY_CANCELLED",
            status_code=400,
            details={"query_id": query_id},
        )


class TerminalSqlPermissionDeniedError(TerminalError):
    def __init__(self, object_name: str):
        super().__init__(
            f"Permission denied for database object '{object_name}'.",
            code="TERMINAL_SQL_PERMISSION_DENIED",
            status_code=403,
            details={"object_name": object_name},
        )


class TerminalCliCommandUnknownError(TerminalError):
    def __init__(self, command: str):
        super().__init__(
            f"Unknown or unapproved ATLAS CLI command: '{command}'. Use 'atlas help' to list registered commands.",
            code="TERMINAL_CLI_COMMAND_UNKNOWN",
            status_code=400,
            details={"command": command},
        )


class TerminalCliArgumentInvalidError(TerminalError):
    def __init__(self, command: str, argument: str, reason: str):
        super().__init__(
            f"Invalid argument '{argument}' for CLI command '{command}': {reason}",
            code="TERMINAL_CLI_ARGUMENT_INVALID",
            status_code=400,
            details={"command": command, "argument": argument, "reason": reason},
        )


class TerminalCliPermissionDeniedError(TerminalError):
    def __init__(self, command: str, user_id: str):
        super().__init__(
            f"Permission denied to execute CLI command '{command}' for user '{user_id}'.",
            code="TERMINAL_CLI_PERMISSION_DENIED",
            status_code=403,
            details={"command": command, "user_id": user_id},
        )


class TerminalCliMutationNotAllowedError(TerminalError):
    def __init__(self, command: str):
        super().__init__(
            f"Mutation operations are not allowed via terminal CLI command '{command}'.",
            code="TERMINAL_CLI_MUTATION_NOT_ALLOWED",
            status_code=403,
            details={"command": command},
        )


class TerminalExecutionInternalError(TerminalError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Terminal execution internal error: {message}",
            code="TERMINAL_EXECUTION_INTERNAL_ERROR",
            status_code=500,
            details=details,
        )
