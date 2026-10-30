"""Domain models and enumerations for the Stage 123 Terminal Execution Platform."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionType(str, Enum):
    """Supported sandboxed execution categories."""

    PYTHON = "PYTHON"
    SQL = "SQL"
    ATLAS_CLI = "ATLAS_CLI"


class ExecutionStatus(str, Enum):
    """Strict execution lifecycle state machine states."""

    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STREAMING = "STREAMING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
    SECURITY_DENIED = "SECURITY_DENIED"
    INFRASTRUCTURE_FAILED = "INFRASTRUCTURE_FAILED"


class StreamOutputType(str, Enum):
    """Categorized execution output streaming channels."""

    STDOUT = "stdout"
    STDERR = "stderr"
    TABULAR = "tabular"
    ARTIFACT = "artifact"
    ERROR = "error"
    SYSTEM = "system"


class CommandMutabilityClass(str, Enum):
    """Classification of command side-effect risk."""

    READ_ONLY = "READ_ONLY"
    COMPUTATIONAL = "COMPUTATIONAL"
    MUTATING = "MUTATING"
    PRIVILEGED = "PRIVILEGED"


@dataclass
class ResourceProfile:
    """Bounded compute and memory constraints for execution."""

    profile_id: str = "standard_v1"
    name: str = "Standard Sandbox"
    cpu_cores: float = 1.0
    memory_mb: int = 512
    timeout_seconds: int = 10
    max_output_bytes: int = 65536
    max_rows: int = 500


@dataclass
class ExecutionOutputChunk:
    """Bounded, ordered output chunk emitted during execution."""

    execution_id: str
    seq_num: int
    stream_type: StreamOutputType
    payload: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TabularColumn:
    """Column definition for structured tabular query results."""

    name: str
    data_type: str


@dataclass
class TabularResult:
    """Normalized structured tabular dataset from SQL or Python DataFrames."""

    columns: List[TabularColumn] = field(default_factory=list)
    rows: List[Dict[str, Any]] = field(default_factory=list)
    total_rows: int = 0
    truncated: bool = False
    as_of: Optional[datetime] = None


@dataclass
class ExecutionArtifact:
    """User-scoped analytical artifact (e.g. plot image, chart json)."""

    artifact_id: str
    execution_id: str
    name: str
    mime_type: str
    byte_size: int
    storage_path: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PythonEnvironment:
    """Declarative specification of an authorized, pinned Python runtime."""

    environment_id: str
    name: str
    version: str
    python_version: str
    packages: Dict[str, str]
    is_default: bool = False
    resource_profiles: List[str] = field(default_factory=lambda: ["standard_v1"])
    filesystem_policy: str = "isolated_ephemeral_tempdir"
    network_policy: str = "default_deny_egress"


@dataclass
class SqlSource:
    """Authorized analytical data source for permission-controlled SQL."""

    source_id: str
    display_name: str
    source_type: str  # e.g., 'in_memory_fixture', 'postgresql_analytical', 'clickhouse_analytics'
    allowed_schemas: List[str] = field(default_factory=lambda: ["public"])
    allowed_views: List[str] = field(default_factory=list)
    is_read_only: bool = True
    default_row_limit: int = 500
    timeout_seconds: int = 15
    description: str = ""


@dataclass
class CliCommandDef:
    """Schema and capability definition for an approved ATLAS CLI command."""

    command_id: str
    namespace: str
    name: str
    description: str
    usage: str
    arguments_schema: List[Dict[str, Any]] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    mutability_class: CommandMutabilityClass = CommandMutabilityClass.READ_ONLY
    required_capability: str = "terminal.cli"


@dataclass
class TerminalExecution:
    """Canonical persistent execution record."""

    execution_id: str
    owner_user_id: str
    terminal_session_id: str
    execution_type: ExecutionType
    status: ExecutionStatus = ExecutionStatus.CREATED
    state_revision: int = 1
    input_code: str = ""
    environment_id: Optional[str] = None
    source_id: Optional[str] = None
    tenant_id: Optional[str] = None
    resource_profile: ResourceProfile = field(default_factory=ResourceProfile)
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    row_count: Optional[int] = None
    stdout_summary: Optional[str] = None
    tabular_result: Optional[TabularResult] = None
    artifacts: List[ExecutionArtifact] = field(default_factory=list)
    idempotency_key: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    cancellation_requested_at: Optional[datetime] = None

