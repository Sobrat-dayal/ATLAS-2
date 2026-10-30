"""Service orchestration layer for Stage 122 Terminal Shell."""

from typing import Any, Dict, List, Optional

from .capabilities import (
    TERMINAL_CAPABILITIES_CATALOG,
    get_cli_help,
    get_stage_123_contracts,
)
from .diagnostics import (
    AgentDiagnosticsService,
    LogDiagnosticsService,
    McpDiagnosticsService,
)
from .enums import LogSeverity, TerminalCursorStyle, TerminalType
from .errors import TerminalExecutionUnavailableError
from .models import (
    AgentStatusRecord,
    LogEntry,
    McpConnectionRecord,
    TerminalSession,
    TerminalUserPreferences,
)
from .repository import TerminalRepository


class TerminalService:
    """Orchestration service for the Stage 122 Integrated Terminal Shell."""

    def __init__(
        self,
        repository: Optional[TerminalRepository] = None,
        log_diagnostics: Optional[LogDiagnosticsService] = None,
    ):
        self.repository = repository or TerminalRepository.get_instance()
        self.log_diagnostics = log_diagnostics or LogDiagnosticsService.get_instance()

    def get_capabilities(self) -> Dict[str, Any]:
        """Return full capability catalog and Stage 123 preparation contracts."""
        return {
            "stage": 122,
            "stage_title": "VS Code-Style ATLAS Terminal Shell",
            "consoles": {t.value: cap for t, cap in TERMINAL_CAPABILITIES_CATALOG.items()},
            "stage_123_contracts": get_stage_123_contracts(),
        }

    def get_cli_command_help(self, command: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return registered CLI command definitions and syntax."""
        return get_cli_help(command)

    def list_sessions(
        self, user_id: str, workspace_id: Optional[str] = None
    ) -> List[TerminalSession]:
        return self.repository.list_sessions(user_id=user_id, workspace_id=workspace_id)

    def get_session(self, session_id: str, user_id: str) -> TerminalSession:
        return self.repository.get_session(session_id=session_id, user_id=user_id)

    def create_session(
        self,
        user_id: str,
        terminal_type: TerminalType,
        display_name: Optional[str] = None,
        workspace_id: Optional[str] = None,
        initial_draft: str = "",
    ) -> TerminalSession:
        return self.repository.create_session(
            user_id=user_id,
            terminal_type=terminal_type,
            display_name=display_name,
            workspace_id=workspace_id,
            initial_draft=initial_draft,
        )

    def update_session(
        self,
        session_id: str,
        user_id: str,
        display_name: Optional[str] = None,
        draft_content: Optional[str] = None,
        scrollback_limit: Optional[int] = None,
        expected_version: Optional[int] = None,
    ) -> TerminalSession:
        return self.repository.update_session(
            session_id=session_id,
            user_id=user_id,
            display_name=display_name,
            draft_content=draft_content,
            scrollback_limit=scrollback_limit,
            expected_version=expected_version,
        )

    def close_session(self, session_id: str, user_id: str) -> bool:
        return self.repository.close_session(session_id=session_id, user_id=user_id)

    def reorder_sessions(self, user_id: str, session_ids: List[str]) -> List[TerminalSession]:
        return self.repository.reorder_sessions(user_id=user_id, session_ids=session_ids)

    def get_preferences(self, user_id: str) -> TerminalUserPreferences:
        return self.repository.get_preferences(user_id=user_id)

    def update_preferences(
        self,
        user_id: str,
        font_size: Optional[int] = None,
        font_family: Optional[str] = None,
        line_height: Optional[float] = None,
        scrollback_limit: Optional[int] = None,
        cursor_style: Optional[TerminalCursorStyle] = None,
        word_wrap: Optional[bool] = None,
        terminal_height: Optional[int] = None,
        default_tab_type: Optional[TerminalType] = None,
        restore_previous_tabs: Optional[bool] = None,
        timestamp_display: Optional[bool] = None,
    ) -> TerminalUserPreferences:
        return self.repository.update_preferences(
            user_id=user_id,
            font_size=font_size,
            font_family=font_family,
            line_height=line_height,
            scrollback_limit=scrollback_limit,
            cursor_style=cursor_style,
            word_wrap=word_wrap,
            terminal_height=terminal_height,
            default_tab_type=default_tab_type,
            restore_previous_tabs=restore_previous_tabs,
            timestamp_display=timestamp_display,
        )

    def query_logs(
        self,
        severity: Optional[LogSeverity] = None,
        service: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LogEntry]:
        return self.log_diagnostics.query_logs(
            severity=severity,
            service=service,
            search=search,
            limit=limit,
            offset=offset,
        )

    def get_agent_statuses(self) -> List[AgentStatusRecord]:
        return AgentDiagnosticsService.get_agent_status_list()

    def get_mcp_connections(self) -> List[McpConnectionRecord]:
        return McpDiagnosticsService.get_mcp_connections()

    def execute_command_attempt(self, *args, **kwargs) -> None:
        """Explicitly blocks and rejects arbitrary un-sandboxed execution attempts."""
        raise TerminalExecutionUnavailableError()

    def execute_command(
        self,
        user_id: str,
        session_id: str,
        input_code: str,
        execution_type: Optional[Any] = None,
        workspace_id: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Executes terminal code/command using Stage 123 sandboxed execution engine."""
        from atlas.terminal.execution.service import TerminalExecutionService

        return TerminalExecutionService.get_instance().submit_execution(
            user_id=user_id,
            session_id=session_id,
            input_code=input_code,
            execution_type=execution_type,
            workspace_id=workspace_id,
            **kwargs,
        )
