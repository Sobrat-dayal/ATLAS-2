"""Exceptions for the Stage 122 Integrated ATLAS Terminal Shell."""

from typing import Any, Dict, Optional


class TerminalError(Exception):
    """Base exception for terminal operations."""

    def __init__(
        self,
        message: str,
        code: str = "TERMINAL_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class TerminalSessionNotFoundError(TerminalError):
    def __init__(self, session_id: str):
        super().__init__(
            f"Terminal session '{session_id}' not found.",
            code="TERMINAL_SESSION_NOT_FOUND",
            status_code=404,
            details={"session_id": session_id},
        )


class TerminalSessionAccessDeniedError(TerminalError):
    def __init__(self, session_id: str, user_id: str):
        super().__init__(
            f"Access denied to terminal session '{session_id}' for user '{user_id}'.",
            code="TERMINAL_SESSION_ACCESS_DENIED",
            status_code=403,
            details={"session_id": session_id, "user_id": user_id},
        )


class TerminalTypeUnsupportedError(TerminalError):
    def __init__(self, terminal_type: str):
        super().__init__(
            f"Terminal type '{terminal_type}' is not supported.",
            code="TERMINAL_TYPE_UNSUPPORTED",
            status_code=400,
            details={"terminal_type": terminal_type},
        )


class TerminalConfigurationInvalidError(TerminalError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Invalid terminal configuration: {message}",
            code="TERMINAL_CONFIGURATION_INVALID",
            status_code=400,
            details=details,
        )


class TerminalSessionLimitExceededError(TerminalError):
    def __init__(self, current_count: int, max_limit: int = 32):
        super().__init__(
            f"Terminal session limit exceeded. Current: {current_count}, Maximum: {max_limit}.",
            code="TERMINAL_SESSION_LIMIT_EXCEEDED",
            status_code=400,
            details={"current_count": current_count, "max_limit": max_limit},
        )


class TerminalDraftTooLargeError(TerminalError):
    def __init__(self, current_bytes: int, max_bytes: int = 65536):
        super().__init__(
            f"Terminal draft size {current_bytes} bytes exceeds maximum allowed {max_bytes} bytes.",
            code="TERMINAL_DRAFT_TOO_LARGE",
            status_code=400,
            details={"current_bytes": current_bytes, "max_bytes": max_bytes},
        )


class TerminalExecutionUnavailableError(TerminalError):
    def __init__(
        self,
        message: str = (
            "Command execution is unavailable in Stage 122. "
            "Stage 123 provides approved sandboxed execution for Python, SQL, and ATLAS CLI."
        ),
    ):
        super().__init__(
            message,
            code="TERMINAL_EXECUTION_UNAVAILABLE",
            status_code=501,  # Not Implemented / Forbidden execution in Stage 122
            details={"stage": 122, "execution_milestone": "Stage 123"},
        )


class TerminalLogSourceUnavailableError(TerminalError):
    def __init__(self, source_name: str):
        super().__init__(
            f"Log source '{source_name}' is currently unavailable or disconnected.",
            code="TERMINAL_LOG_SOURCE_UNAVAILABLE",
            status_code=503,
            details={"source_name": source_name},
        )


class TerminalSessionVersionConflictError(TerminalError):
    def __init__(self, session_id: str, expected_version: int, current_version: int):
        super().__init__(
            f"Terminal session '{session_id}' update conflict. Expected version {expected_version}, but current version is {current_version}.",
            code="TERMINAL_SESSION_VERSION_CONFLICT",
            status_code=409,
            details={
                "session_id": session_id,
                "expected_version": expected_version,
                "current_version": current_version,
            },
        )
