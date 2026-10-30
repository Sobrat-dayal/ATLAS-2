"""Pydantic v2 schemas for Stage 122 Terminal HTTP endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    ConnectionState,
    ExecutionCapability,
    LogSeverity,
    SessionLifecycle,
    SessionStatus,
    TerminalCursorStyle,
    TerminalType,
)


class CreateTerminalSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    terminal_type: TerminalType
    display_name: Optional[str] = Field(None, max_length=128)
    workspace_id: Optional[str] = Field(None, max_length=64)
    initial_draft: Optional[str] = Field("", max_length=65536)


class UpdateTerminalSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: Optional[str] = Field(None, max_length=128)
    draft_content: Optional[str] = Field(None, max_length=65536)
    scrollback_limit: Optional[int] = Field(None, ge=100, le=10000)
    expected_version: Optional[int] = None


class ReorderTerminalSessionsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_ids: List[str] = Field(..., min_length=1, max_length=32)


class UpdateTerminalPreferencesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    font_size: Optional[int] = Field(None, ge=8, le=32)
    font_family: Optional[str] = Field(None, max_length=256)
    line_height: Optional[float] = Field(None, ge=1.0, le=2.5)
    scrollback_limit: Optional[int] = Field(None, ge=100, le=10000)
    cursor_style: Optional[TerminalCursorStyle] = None
    word_wrap: Optional[bool] = None
    terminal_height: Optional[int] = Field(None, ge=140, le=1200)
    default_tab_type: Optional[TerminalType] = None
    restore_previous_tabs: Optional[bool] = None
    timestamp_display: Optional[bool] = None


class TerminalSessionResponse(BaseModel):
    session_id: str
    owner_user_id: str
    terminal_type: TerminalType
    display_name: str
    lifecycle: SessionLifecycle
    connection_state: ConnectionState
    execution_capability: ExecutionCapability
    status: SessionStatus
    session_order: int
    workspace_id: Optional[str] = None
    configuration_schema_version: int
    version: int
    draft_content: str
    scrollback_limit: int
    created_at: datetime
    updated_at: datetime
    last_active_at: datetime
    closed_at: Optional[datetime] = None


class TerminalPreferencesResponse(BaseModel):
    user_id: str
    font_size: int
    font_family: str
    line_height: float
    scrollback_limit: int
    cursor_style: TerminalCursorStyle
    word_wrap: bool
    terminal_height: int
    default_tab_type: TerminalType
    restore_previous_tabs: bool
    timestamp_display: bool
    updated_at: datetime


class LogEntryResponse(BaseModel):
    log_id: str
    timestamp: datetime
    level: LogSeverity
    service: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentStatusResponse(BaseModel):
    agent_id: str
    display_name: str
    state: str
    last_activity_at: Optional[datetime] = None
    source: str
    permission_scope: str


class McpConnectionResponse(BaseModel):
    server_id: str
    display_name: str
    status: ConnectionState
    available_tools_count: int
    resources_count: int
    last_checked_at: Optional[datetime] = None
    configured_in: str


class CliCommandHelpResponse(BaseModel):
    command: str
    syntax: str
    summary: str
    example: str
    category: str


class TerminalCapabilitiesResponse(BaseModel):
    stage: int
    stage_title: str
    consoles: Dict[str, Any]
    stage_123_contracts: Dict[str, Any]
