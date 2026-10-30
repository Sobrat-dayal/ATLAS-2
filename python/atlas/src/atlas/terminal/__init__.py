"""ATLAS Stage 122 — Integrated Terminal Shell Package."""

from .enums import (
    ConnectionState,
    ExecutionCapability,
    LogSeverity,
    OutputRecordType,
    SessionLifecycle,
    SessionStatus,
    TerminalCursorStyle,
    TerminalType,
)
from .errors import (
    TerminalDraftTooLargeError,
    TerminalError,
    TerminalExecutionUnavailableError,
    TerminalLogSourceUnavailableError,
    TerminalSessionAccessDeniedError,
    TerminalSessionLimitExceededError,
    TerminalSessionNotFoundError,
    TerminalSessionVersionConflictError,
    TerminalTypeUnsupportedError,
)
from .models import (
    AgentStatusRecord,
    ExecutionCapabilityDefinition,
    ExecutionOutputStreamingContract,
    ExecutionRequestSchemaContract,
    ExecutionStatusContract,
    LogEntry,
    McpConnectionRecord,
    TerminalCapability,
    TerminalOutputRecord,
    TerminalSession,
    TerminalUserPreferences,
)
from .repository import TerminalRepository
from .service import TerminalService

__all__ = [
    "ConnectionState",
    "ExecutionCapability",
    "LogSeverity",
    "OutputRecordType",
    "SessionLifecycle",
    "SessionStatus",
    "TerminalCursorStyle",
    "TerminalType",
    "TerminalError",
    "TerminalDraftTooLargeError",
    "TerminalExecutionUnavailableError",
    "TerminalLogSourceUnavailableError",
    "TerminalSessionAccessDeniedError",
    "TerminalSessionLimitExceededError",
    "TerminalSessionNotFoundError",
    "TerminalSessionVersionConflictError",
    "TerminalTypeUnsupportedError",
    "AgentStatusRecord",
    "ExecutionCapabilityDefinition",
    "ExecutionOutputStreamingContract",
    "ExecutionRequestSchemaContract",
    "ExecutionStatusContract",
    "LogEntry",
    "McpConnectionRecord",
    "TerminalCapability",
    "TerminalOutputRecord",
    "TerminalSession",
    "TerminalUserPreferences",
    "TerminalRepository",
    "TerminalService",
]

