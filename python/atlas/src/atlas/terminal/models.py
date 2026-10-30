"""Domain models and dataclasses for Stage 122 Terminal Shell."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

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


@dataclass
class TerminalSession:
    """Represents an active, configured, or closed terminal session."""

    session_id: str
    owner_user_id: str
    terminal_type: TerminalType
    display_name: str
    lifecycle: SessionLifecycle = SessionLifecycle.ACTIVE
    connection_state: ConnectionState = ConnectionState.CONNECTED
    execution_capability: ExecutionCapability = ExecutionCapability.DISABLED
    status: SessionStatus = SessionStatus.READY
    session_order: int = 0
    workspace_id: Optional[str] = None
    configuration_schema_version: int = 1
    version: int = 1
    draft_content: str = ""
    scrollback_limit: int = 2000
    appearance_options: Dict[str, Any] = field(default_factory=dict)
    input_options: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_active_at: datetime = field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None


@dataclass
class TerminalUserPreferences:
    """User-level persistent terminal preferences."""

    user_id: str
    font_size: int = 12
    font_family: str = "JetBrains Mono, Fira Code, Menlo, monospace"
    line_height: float = 1.45
    scrollback_limit: int = 2000
    cursor_style: TerminalCursorStyle = TerminalCursorStyle.BLOCK
    word_wrap: bool = True
    terminal_height: int = 320
    default_tab_type: TerminalType = TerminalType.ATLAS_CLI
    restore_previous_tabs: bool = True
    timestamp_display: bool = True
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TerminalOutputRecord:
    """A single entry in terminal output / scrollback buffer."""

    output_id: str
    session_id: str
    record_type: OutputRecordType
    content: str
    content_format: str = "text/plain"  # "text/plain", "text/ansi", "application/json"
    severity: Optional[LogSeverity] = None
    source: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)
    source_reference: Optional[Dict[str, Any]] = None


@dataclass
class LogEntry:
    """Normalized authorized application log line."""

    log_id: str
    timestamp: datetime
    level: LogSeverity
    service: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStatusRecord:
    """Read-only operational status of an ATLAS agent."""

    agent_id: str
    display_name: str
    state: str  # e.g. "REGISTERED", "IDLE", "UNAVAILABLE"
    last_activity_at: Optional[datetime] = None
    source: str = "atlas.agents"
    permission_scope: str = "read_only"


@dataclass
class McpConnectionRecord:
    """Read-only connection metadata for a Model Context Protocol server."""

    server_id: str
    display_name: str
    status: ConnectionState
    available_tools_count: int = 0
    resources_count: int = 0
    last_checked_at: Optional[datetime] = None
    configured_in: str = "mcp/configs"


@dataclass
class TerminalCapability:
    """Declarative capability profile for a console type."""

    terminal_type: TerminalType
    display_label: str
    description: str
    icon_name: str
    supports_multiline: bool
    supports_draft_persistence: bool
    supports_real_read_data: bool
    supports_arbitrary_execution: bool  # Always False in Stage 122
    execution_status_notice: str
    stage_122_status: str


# ============================================================================
# STAGE 123 PREPARATION CONTRACTS (Interface Specification Only)
# ============================================================================


@dataclass
class ExecutionCapabilityDefinition:
    """Contract specification for Stage 123 approved sandboxed execution."""

    capability_id: str
    terminal_type: TerminalType
    supported: bool = False
    enabled: bool = False
    requires_sandbox: bool = True
    required_permissions: List[str] = field(default_factory=list)
    resource_limits_reference: str = "limits.sandbox.standard_v1"
    execution_api_version: str = "v1-alpha"


@dataclass
class ExecutionRequestSchemaContract:
    """Typed schema specification for future Stage 123 command execution requests."""

    request_id: str
    session_id: str
    terminal_type: TerminalType
    execution_capability_id: str
    payload: str
    workspace_context_reference: Optional[Dict[str, Any]] = None
    expected_environment_reference: Optional[str] = None
    idempotency_key: Optional[str] = None


@dataclass
class ExecutionStatusContract:
    """Typed schema specification for future Stage 123 command execution status."""

    execution_id: str
    session_id: str
    status: str  # QUEUED, STARTING, RUNNING, COMPLETED, FAILED, CANCELLED, TIMED_OUT
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    exit_status: Optional[int] = None
    resource_usage: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


@dataclass
class ExecutionOutputStreamingContract:
    """Typed schema specification for future Stage 123 output streaming events."""

    event_id: str
    execution_id: str
    session_id: str
    stream_type: str  # stdout, stderr, system
    sequence_number: int
    content: str
    timestamp: datetime
