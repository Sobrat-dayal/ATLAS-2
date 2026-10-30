"""FastAPI Router for ATLAS Stage 122: Integrated Terminal Shell.
Mounted under /terminal.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.terminal.enums import LogSeverity
from atlas.terminal.errors import (
    TerminalError,
)
from atlas.terminal.execution.domain import ExecutionStatus, ExecutionType, ResourceProfile
from atlas.terminal.execution.errors import TerminalError as ExecutionTerminalError
from atlas.terminal.execution.schemas import (
    CliCommandResponse,
    ExecutionDetailResponse,
    ExecutionOutputChunkResponse,
    ExecutionStatusResponse,
    ExecutionSubmitRequest,
    PythonEnvironmentResponse,
    ResourceProfileResponse,
    SqlSourceResponse,
    SqlValidateRequest,
    SqlValidateResponse,
)
from atlas.terminal.execution.service import TerminalExecutionService
from atlas.terminal.schemas import (
    AgentStatusResponse,
    CliCommandHelpResponse,
    CreateTerminalSessionRequest,
    LogEntryResponse,
    McpConnectionResponse,
    ReorderTerminalSessionsRequest,
    TerminalCapabilitiesResponse,
    TerminalPreferencesResponse,
    TerminalSessionResponse,
    UpdateTerminalPreferencesRequest,
    UpdateTerminalSessionRequest,
)
from atlas.terminal.service import TerminalService
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/terminal", tags=["Terminal Shell"])

_terminal_service = TerminalService()
_exec_service = TerminalExecutionService.get_instance()


def get_terminal_service() -> TerminalService:
    return _terminal_service


def get_execution_service() -> TerminalExecutionService:
    return _exec_service


def _get_principal_user_id(principal: AuthPrincipal) -> str:
    user_id = getattr(principal, "user_id", None) or getattr(principal, "sub", None)
    if not user_id:
        return "usr_default_trader"
    return str(user_id)


# ---------------- Capabilities & CLI Help ----------------


@router.get("/capabilities", response_model=TerminalCapabilitiesResponse)
async def get_terminal_capabilities(
    service: TerminalService = Depends(get_terminal_service),
) -> Dict[str, Any]:
    """Retrieve full capability catalog, console profiles, and Stage 123 contracts."""
    return service.get_capabilities()


@router.get("/cli/help", response_model=List[CliCommandHelpResponse])
async def get_cli_help(
    command: Optional[str] = Query(None, description="Optional command name to inspect"),
    service: TerminalService = Depends(get_terminal_service),
) -> List[Dict[str, Any]]:
    """Retrieve documented CLI syntax and static registered commands."""
    return service.get_cli_command_help(command)


# ---------------- Sessions Management ----------------


@router.get("/sessions", response_model=List[TerminalSessionResponse])
async def list_sessions(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    workspace_id: Optional[str] = Query(None, description="Optional workspace scope filter"),
    service: TerminalService = Depends(get_terminal_service),
) -> List[Any]:
    """List all active terminal sessions for the authenticated user."""
    user_id = _get_principal_user_id(principal)
    return service.list_sessions(user_id=user_id, workspace_id=workspace_id)


@router.post(
    "/sessions", response_model=TerminalSessionResponse, status_code=status.HTTP_201_CREATED
)
async def create_session(
    request: CreateTerminalSessionRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> Any:
    """Create a new terminal session of a designated console type."""
    user_id = _get_principal_user_id(principal)
    try:
        return service.create_session(
            user_id=user_id,
            terminal_type=request.terminal_type,
            display_name=request.display_name,
            workspace_id=request.workspace_id,
            initial_draft=request.initial_draft or "",
        )
    except TerminalError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.get("/sessions/{session_id}", response_model=TerminalSessionResponse)
async def get_session(
    session_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> Any:
    """Retrieve details and draft for a specific terminal session."""
    user_id = _get_principal_user_id(principal)
    try:
        return service.get_session(session_id=session_id, user_id=user_id)
    except TerminalError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.patch("/sessions/{session_id}", response_model=TerminalSessionResponse)
async def update_session(
    session_id: str,
    request: UpdateTerminalSessionRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> Any:
    """Update title, draft content, or scrollback limit of a session with optimistic concurrency."""
    user_id = _get_principal_user_id(principal)
    try:
        return service.update_session(
            session_id=session_id,
            user_id=user_id,
            display_name=request.display_name,
            draft_content=request.draft_content,
            scrollback_limit=request.scrollback_limit,
            expected_version=request.expected_version,
        )
    except TerminalError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_session(
    session_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> None:
    """Close/delete a terminal session."""
    user_id = _get_principal_user_id(principal)
    try:
        service.close_session(session_id=session_id, user_id=user_id)
    except TerminalError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)


@router.patch("/sessions/order", response_model=List[TerminalSessionResponse])
async def reorder_sessions(
    request: ReorderTerminalSessionsRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> List[Any]:
    """Reorder tabs for the user."""
    user_id = _get_principal_user_id(principal)
    return service.reorder_sessions(user_id=user_id, session_ids=request.session_ids)


# ---------------- Preferences Management ----------------


@router.get("/preferences", response_model=TerminalPreferencesResponse)
async def get_preferences(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> Any:
    """Load user's persistent terminal preferences."""
    user_id = _get_principal_user_id(principal)
    return service.get_preferences(user_id=user_id)


@router.put("/preferences", response_model=TerminalPreferencesResponse)
async def update_preferences(
    request: UpdateTerminalPreferencesRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> Any:
    """Save updated terminal preferences."""
    user_id = _get_principal_user_id(principal)
    return service.update_preferences(
        user_id=user_id,
        font_size=request.font_size,
        font_family=request.font_family,
        line_height=request.line_height,
        scrollback_limit=request.scrollback_limit,
        cursor_style=request.cursor_style,
        word_wrap=request.word_wrap,
        terminal_height=request.terminal_height,
        default_tab_type=request.default_tab_type,
        restore_previous_tabs=request.restore_previous_tabs,
        timestamp_display=request.timestamp_display,
    )


# ---------------- Read-Only Diagnostics Feeds ----------------


@router.get("/logs", response_model=List[LogEntryResponse])
async def query_logs(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    severity: Optional[LogSeverity] = Query(None, description="Filter by minimum severity"),
    service_name: Optional[str] = Query(
        None, alias="service", description="Filter by service name"
    ),
    search: Optional[str] = Query(None, description="Search log text or metadata"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: TerminalService = Depends(get_terminal_service),
) -> List[Any]:
    """Retrieve sanitized, authorized operational logs for the Logs console."""
    # Ensure authenticated
    _ = _get_principal_user_id(principal)
    return service.query_logs(
        severity=severity,
        service=service_name,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/agents/status", response_model=List[AgentStatusResponse])
async def get_agents_status(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> List[Any]:
    """Retrieve truthful operational status of registered agents."""
    _ = _get_principal_user_id(principal)
    return service.get_agent_statuses()


@router.get("/mcp/connections", response_model=List[McpConnectionResponse])
async def get_mcp_connections(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: TerminalService = Depends(get_terminal_service),
) -> List[Any]:
    """Retrieve truthful connection metadata for configured Model Context Protocol servers."""
    _ = _get_principal_user_id(principal)
    return service.get_mcp_connections()


# ============================================================================
# Stage 123 Sandboxed Terminal Execution APIs
# ============================================================================


@router.post(
    "/executions", response_model=ExecutionDetailResponse, status_code=status.HTTP_201_CREATED
)
async def submit_execution(
    request: ExecutionSubmitRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Submit command, Python script, or read-only SQL for sandboxed execution."""
    user_id = _get_principal_user_id(principal)
    try:
        profile = None
        if request.timeout_seconds:
            profile = ResourceProfile(timeout_seconds=request.timeout_seconds)

        return exec_service.submit_execution(
            user_id=user_id,
            session_id=request.session_id,
            input_code=request.input_code,
            execution_type=request.execution_type,
            environment_id=request.environment_id,
            source_id=request.source_id,
            resource_profile=profile,
            workspace_id=request.workspace_id,
            idempotency_key=request.idempotency_key,
        )
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )


@router.get("/executions/{execution_id}", response_model=ExecutionDetailResponse)
async def get_execution_detail(
    execution_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Retrieve execution record, status, timings, and output summary."""
    user_id = _get_principal_user_id(principal)
    try:
        return exec_service.get_execution(execution_id, user_id)
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )


@router.get("/executions/{execution_id}/status", response_model=ExecutionStatusResponse)
async def get_execution_status(
    execution_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Fast status polling endpoint for active executions."""
    user_id = _get_principal_user_id(principal)
    try:
        item = exec_service.get_execution(execution_id, user_id)
        return {
            "execution_id": item.execution_id,
            "status": item.status,
            "state_revision": item.state_revision,
            "duration_ms": item.duration_ms,
            "error_code": item.error_code,
            "error_message": item.error_message,
        }
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )


@router.get("/executions/{execution_id}/output", response_model=List[ExecutionOutputChunkResponse])
async def get_execution_output(
    execution_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Retrieve authorized, ordered output chunks emitted by an execution."""
    user_id = _get_principal_user_id(principal)
    try:
        return exec_service.get_execution_output(execution_id, user_id)
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )


@router.post("/executions/{execution_id}/cancel", response_model=ExecutionDetailResponse)
async def cancel_execution(
    execution_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Request graceful cancellation of a running execution."""
    user_id = _get_principal_user_id(principal)
    try:
        return exec_service.cancel_execution(execution_id, user_id)
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )


@router.get("/executions", response_model=List[ExecutionDetailResponse])
async def list_executions(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    session_id: Optional[str] = Query(None, description="Filter by terminal session"),
    execution_type: Optional[ExecutionType] = Query(None, description="Filter by execution type"),
    status_filter: Optional[ExecutionStatus] = Query(
        None, alias="status", description="Filter by status"
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Query user execution history with filtering and pagination."""
    user_id = _get_principal_user_id(principal)
    return exec_service.list_executions(
        user_id=user_id,
        session_id=session_id,
        execution_type=execution_type,
        status=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get("/execution-capabilities")
async def get_execution_capabilities(
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """List operational execution capabilities (Python, SQL, ATLAS CLI)."""
    return exec_service.get_execution_capabilities()


# ---------------- Python Runtimes & Resource Profiles ----------------


@router.get("/python/environments", response_model=List[PythonEnvironmentResponse])
async def get_python_environments(
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """List approved, deterministic Python sandbox environments."""
    return exec_service.get_python_environments()


@router.get("/python/environments/{environment_id}", response_model=PythonEnvironmentResponse)
async def get_python_environment(
    environment_id: str,
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Inspect specific Python environment package manifest and policies."""
    envs = exec_service.get_python_environments()
    for env in envs:
        if env.environment_id == environment_id:
            return env
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Python environment '{environment_id}' not found.",
    )


@router.get("/python/resource-profiles", response_model=List[ResourceProfileResponse])
async def get_python_resource_profiles(
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """List permitted compute and memory resource profiles."""
    return exec_service.get_python_resource_profiles()


# ---------------- SQL Analytical Sources & Validation ----------------


@router.get("/sql/sources", response_model=List[SqlSourceResponse])
async def get_sql_sources(
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """List authorized analytical SQL data sources."""
    return exec_service.get_sql_sources()


@router.get("/sql/sources/{source_id}/schema")
async def get_sql_source_schema(
    source_id: str,
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Inspect allowed views and column schemas for a source."""
    try:
        return exec_service.get_sql_source_schema(source_id)
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )


@router.post("/sql/validate", response_model=SqlValidateResponse)
async def validate_sql(
    request: SqlValidateRequest,
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Validate query against the read-only analytical allowlist prior to execution."""
    try:
        res = exec_service.validate_sql(request.sql_text)
        return {
            "valid": True,
            "statement_type": res["statement_type"],
            "clean_statement": res["clean_statement"],
            "error": None,
        }
    except ExecutionTerminalError as err:
        return {
            "valid": False,
            "statement_type": "PROHIBITED",
            "clean_statement": request.sql_text,
            "error": err.message,
        }


# ---------------- Approved CLI Commands Registry ----------------


@router.get("/cli/commands", response_model=List[CliCommandResponse])
async def get_cli_commands(
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """List registered approved ATLAS CLI commands."""
    return exec_service.get_cli_commands()


@router.get("/cli/commands/{command_id}", response_model=CliCommandResponse)
async def get_cli_command(
    command_id: str,
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Inspect specific ATLAS CLI command schema and usage."""
    try:
        return exec_service.get_cli_command(command_id)
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )


# ---------------- Legacy / Convenience Execute Endpoint ----------------


@router.post("/execute", response_model=Optional[ExecutionDetailResponse])
async def execute_command(
    request: Optional[ExecutionSubmitRequest] = None,
    principal: Annotated[Optional[AuthPrincipal], Depends(get_current_user)] = None,
    exec_service: TerminalExecutionService = Depends(get_execution_service),
) -> Any:
    """Convenience alias for /executions or rejects bare execute calls."""
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Command execution is strictly unavailable in Stage 122. "
                "Stage 123 provides approved sandboxed runtimes for Python, SQL, and ATLAS CLI."
            ),
        )
    user_id = _get_principal_user_id(principal) if principal else "usr_default_trader"
    try:
        return exec_service.submit_execution(
            user_id=user_id,
            session_id=request.session_id,
            input_code=request.input_code,
            execution_type=request.execution_type,
            environment_id=request.environment_id,
            source_id=request.source_id,
            workspace_id=request.workspace_id,
            idempotency_key=request.idempotency_key,
        )
    except ExecutionTerminalError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"message": err.message, "code": err.code, "details": err.details},
        )
