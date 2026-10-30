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


def get_terminal_service() -> TerminalService:
    return _terminal_service


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


# ---------------- Stage 123 Execution Boundary Enforcement ----------------


@router.post("/execute", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def execute_command():
    """Strictly disabled endpoint in Stage 122. Rejects all arbitrary execution."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Command execution is strictly unavailable in Stage 122. "
            "Stage 123 provides approved sandboxed runtimes for Python, SQL, and ATLAS CLI."
        ),
    )
