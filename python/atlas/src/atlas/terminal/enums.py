"""Enums for the Stage 122 Integrated ATLAS Terminal Shell."""

from enum import Enum


class TerminalType(str, Enum):
    """Supported principal terminal console types."""

    ATLAS_CLI = "ATLAS_CLI"
    PYTHON = "PYTHON"
    SQL = "SQL"
    LOGS = "LOGS"
    AGENTS = "AGENTS"
    MCP = "MCP"


class SessionLifecycle(str, Enum):
    """Lifecycle state of a terminal session."""

    ACTIVE = "ACTIVE"
    MINIMIZED = "MINIMIZED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class ConnectionState(str, Enum):
    """Physical or logical upstream connection state."""

    NOT_CONFIGURED = "NOT_CONFIGURED"
    CONFIGURED = "CONFIGURED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"
    ACCESS_RESTRICTED = "ACCESS_RESTRICTED"


class ExecutionCapability(str, Enum):
    """Command execution capability status."""

    DISABLED = "DISABLED"
    SANDBOX_REQUIRED = "SANDBOX_REQUIRED"
    PERMITTED = "PERMITTED"


class SessionStatus(str, Enum):
    """Composite status of a session."""

    INITIALIZING = "INITIALIZING"
    READY = "READY"
    INPUT_ONLY = "INPUT_ONLY"
    READ_ONLY = "READ_ONLY"
    EXECUTION_UNAVAILABLE = "EXECUTION_UNAVAILABLE"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"
    CLOSED = "CLOSED"


class OutputRecordType(str, Enum):
    """Classification of output record entries in terminal scrollback."""

    SYSTEM_MESSAGE = "SYSTEM_MESSAGE"
    LOCAL_INPUT = "LOCAL_INPUT"
    HELP_TEXT = "HELP_TEXT"
    STATUS_MESSAGE = "STATUS_MESSAGE"
    READ_ONLY_LOG = "READ_ONLY_LOG"
    ERROR = "ERROR"
    WARNING = "WARNING"
    EXECUTION_RESULT = "EXECUTION_RESULT"  # Strictly reserved for Stage 123


class LogSeverity(str, Enum):
    """Log severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TerminalCursorStyle(str, Enum):
    """Cursor rendering style."""

    BLOCK = "BLOCK"
    LINE = "LINE"
    UNDERLINE = "UNDERLINE"
