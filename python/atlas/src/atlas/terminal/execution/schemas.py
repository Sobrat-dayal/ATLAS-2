"""Pydantic schemas for the Stage 123 Terminal Execution Platform."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from atlas.terminal.execution.domain import (
    CommandMutabilityClass,
    ExecutionStatus,
    ExecutionType,
    StreamOutputType,
)


class ExecutionSubmitRequest(BaseModel):
    session_id: str = Field(..., description="Target active terminal session ID.")
    input_code: str = Field(
        ..., description="Command string, Python script, or SQL statement to execute."
    )
    execution_type: Optional[ExecutionType] = Field(
        None, description="Execution category (derived from session if omitted)."
    )
    environment_id: Optional[str] = Field(None, description="Pinned Python runtime ID.")
    source_id: Optional[str] = Field(None, description="Target analytical SQL source ID.")
    workspace_id: Optional[str] = Field(None, description="Active workspace desk reference.")
    idempotency_key: Optional[str] = Field(None, description="Unique client key for deduplication.")
    timeout_seconds: Optional[int] = Field(
        None, ge=1, le=30, description="Requested timeout override."
    )


class TabularColumnSchema(BaseModel):
    name: str
    data_type: str


class TabularResultSchema(BaseModel):
    columns: List[TabularColumnSchema] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    total_rows: int = 0
    truncated: bool = False
    as_of: Optional[datetime] = None


class ExecutionStatusResponse(BaseModel):
    execution_id: str
    status: ExecutionStatus
    state_revision: int
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class ExecutionDetailResponse(BaseModel):
    execution_id: str
    owner_user_id: str
    tenant_id: Optional[str] = None
    terminal_session_id: str
    execution_type: ExecutionType
    status: ExecutionStatus
    state_revision: int
    input_code: str
    environment_id: Optional[str] = None
    source_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    row_count: Optional[int] = None
    stdout_summary: Optional[str] = None
    tabular_result: Optional[TabularResultSchema] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ExecutionOutputChunkResponse(BaseModel):
    execution_id: str
    seq_num: int
    stream_type: StreamOutputType
    payload: str
    timestamp: datetime


class PythonEnvironmentResponse(BaseModel):
    environment_id: str
    name: str
    version: str
    python_version: str
    packages: Dict[str, str]
    is_default: bool
    resource_profiles: List[str]


class ResourceProfileResponse(BaseModel):
    profile_id: str
    name: str
    cpu_cores: float
    memory_mb: int
    timeout_seconds: int
    max_output_bytes: int
    max_rows: int


class SqlSourceResponse(BaseModel):
    source_id: str
    display_name: str
    source_type: str
    allowed_schemas: List[str]
    allowed_views: List[str]
    is_read_only: bool
    default_row_limit: int
    timeout_seconds: int
    description: str


class SqlValidateRequest(BaseModel):
    sql_text: str = Field(..., description="SQL statement to validate against read-only allowlist.")


class SqlValidateResponse(BaseModel):
    valid: bool
    statement_type: str
    clean_statement: str
    error: Optional[str] = None


class CliCommandResponse(BaseModel):
    command_id: str
    namespace: str
    name: str
    description: str
    usage: str
    arguments_schema: List[Dict[str, Any]]
    examples: List[str]
    mutability_class: CommandMutabilityClass
