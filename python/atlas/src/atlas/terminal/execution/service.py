"""Terminal Execution Service orchestrating submissions, lifecycle, and registries."""

import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.terminal.enums import TerminalType
from atlas.terminal.execution.cli_router import REGISTERED_CLI_COMMANDS_MAP
from atlas.terminal.execution.domain import (
    CliCommandDef,
    ExecutionOutputChunk,
    ExecutionStatus,
    ExecutionType,
    PythonEnvironment,
    ResourceProfile,
    SqlSource,
    TerminalExecution,
)
from atlas.terminal.execution.errors import (
    TerminalCliCommandUnknownError,
    TerminalExecutionTypeUnsupportedError,
    TerminalPythonEnvironmentUnsupportedError,
    TerminalSqlSourceNotFoundError,
)
from atlas.terminal.execution.python_sandbox import STANDARD_PYTHON_PACKAGES
from atlas.terminal.execution.scheduler import ExecutionScheduler
from atlas.terminal.execution.sql_runner import (
    AUTHORIZED_SQL_SOURCES,
    validate_sql_statement,
)
from atlas.terminal.repository import TerminalRepository


class TerminalExecutionService:
    """Core domain service for Stage 123 sandboxed execution platform."""

    _instance = None

    def __init__(
        self,
        repository: Optional[TerminalRepository] = None,
        scheduler: Optional[ExecutionScheduler] = None,
    ):
        self.repository = repository or TerminalRepository.get_instance()
        self.scheduler = scheduler or ExecutionScheduler.get_instance()

    @classmethod
    def get_instance(cls) -> "TerminalExecutionService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def submit_execution(
        self,
        user_id: str,
        session_id: str,
        input_code: str,
        execution_type: Optional[ExecutionType] = None,
        environment_id: Optional[str] = None,
        source_id: Optional[str] = None,
        resource_profile: Optional[ResourceProfile] = None,
        workspace_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> TerminalExecution:
        """Validate session, capability, and dispatch execution job."""
        # Validate session existence and ownership
        session = self.repository.get_session(session_id, user_id)

        # Derive execution type if omitted
        if execution_type is None:
            if session.terminal_type == TerminalType.PYTHON:
                execution_type = ExecutionType.PYTHON
            elif session.terminal_type == TerminalType.SQL:
                execution_type = ExecutionType.SQL
            elif session.terminal_type == TerminalType.ATLAS_CLI:
                execution_type = ExecutionType.ATLAS_CLI
            else:
                raise TerminalExecutionTypeUnsupportedError(session.terminal_type.value)

        # Validate environment if Python
        if execution_type == ExecutionType.PYTHON:
            selected_env = environment_id or "env_python_standard"
            if selected_env not in ("env_python_standard", "default"):
                raise TerminalPythonEnvironmentUnsupportedError(selected_env)
            environment_id = "env_python_standard"

        # Validate source if SQL
        if execution_type == ExecutionType.SQL:
            selected_source = source_id or "test_prices"
            if selected_source not in AUTHORIZED_SQL_SOURCES:
                raise TerminalSqlSourceNotFoundError(selected_source)
            source_id = selected_source

        profile = resource_profile or ResourceProfile()

        # Build execution record
        execution_id = (
            f"exec_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:6]}"
        )
        execution = TerminalExecution(
            execution_id=execution_id,
            owner_user_id=user_id,
            tenant_id=tenant_id,
            terminal_session_id=session_id,
            execution_type=execution_type,
            status=ExecutionStatus.CREATED,
            input_code=input_code,
            environment_id=environment_id,
            source_id=source_id,
            resource_profile=profile,
            idempotency_key=idempotency_key,
        )

        # Dispatch via scheduler
        return self.scheduler.submit_execution(
            execution=execution,
            workspace_id=workspace_id or session.workspace_id,
        )

    def get_execution(self, execution_id: str, user_id: str) -> TerminalExecution:
        return self.scheduler.get_execution(execution_id, user_id)

    def cancel_execution(self, execution_id: str, user_id: str) -> TerminalExecution:
        return self.scheduler.cancel_execution(execution_id, user_id)

    def get_execution_output(self, execution_id: str, user_id: str) -> List[ExecutionOutputChunk]:
        return self.scheduler.get_execution_output(execution_id, user_id)

    def list_executions(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        execution_type: Optional[ExecutionType] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TerminalExecution]:
        return self.scheduler.list_executions(
            user_id=user_id,
            session_id=session_id,
            execution_type=execution_type,
            status=status,
            limit=limit,
            offset=offset,
        )

    def get_execution_capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "capability_id": "cap.terminal.python.sandbox",
                "execution_type": ExecutionType.PYTHON.value,
                "display_name": "Sandboxed Python 3 Runtime",
                "description": "Subprocess-isolated, unprivileged Python execution with pinned NumPy.",
                "supported": True,
                "enabled": True,
                "requires_sandbox": True,
                "timeout_limit_seconds": 30,
            },
            {
                "capability_id": "cap.terminal.sql.readonly",
                "execution_type": ExecutionType.SQL.value,
                "display_name": "Read-Only Analytical SQL Engine",
                "description": "Permission-controlled SQL engine strictly enforcing statement allowlists.",
                "supported": True,
                "enabled": True,
                "requires_sandbox": True,
                "timeout_limit_seconds": 15,
            },
            {
                "capability_id": "cap.terminal.cli.router",
                "execution_type": ExecutionType.ATLAS_CLI.value,
                "display_name": "Approved ATLAS CLI Command Router",
                "description": "Dispatches approved institutional commands with no OS shell fallback.",
                "supported": True,
                "enabled": True,
                "requires_sandbox": False,
                "timeout_limit_seconds": 10,
            },
        ]

    def get_python_environments(self) -> List[PythonEnvironment]:
        return [
            PythonEnvironment(
                environment_id="env_python_standard",
                name="Python 3 Standard Financial Quantitative Sandbox",
                version="1.0.0",
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                packages=STANDARD_PYTHON_PACKAGES,
                is_default=True,
                resource_profiles=["standard_v1"],
            )
        ]

    def get_python_resource_profiles(self) -> List[ResourceProfile]:
        return [
            ResourceProfile(
                profile_id="standard_v1",
                name="Standard Sandbox Profile",
                cpu_cores=1.0,
                memory_mb=512,
                timeout_seconds=10,
                max_output_bytes=65536,
                max_rows=500,
            ),
            ResourceProfile(
                profile_id="high_compute_v1",
                name="High Compute Analytical Profile",
                cpu_cores=2.0,
                memory_mb=1024,
                timeout_seconds=30,
                max_output_bytes=262144,
                max_rows=1000,
            ),
        ]

    def get_sql_sources(self) -> List[SqlSource]:
        return list(AUTHORIZED_SQL_SOURCES.values())

    def get_sql_source_schema(self, source_id: str) -> Dict[str, Any]:
        source = AUTHORIZED_SQL_SOURCES.get(source_id)
        if not source:
            raise TerminalSqlSourceNotFoundError(source_id)

        if source_id == "test_prices":
            return {
                "source_id": source.source_id,
                "display_name": source.display_name,
                "schemas": {
                    "public": {
                        "test_prices": [
                            {"name": "instrument", "type": "VARCHAR(16)", "primary_key": True},
                            {"name": "price", "type": "REAL", "primary_key": False},
                        ]
                    }
                },
            }

        return {
            "source_id": source.source_id,
            "display_name": source.display_name,
            "schemas": {
                schema: {view: [] for view in source.allowed_views}
                for schema in source.allowed_schemas
            },
        }

    def validate_sql(self, sql_text: str) -> Dict[str, Any]:
        return validate_sql_statement(sql_text)

    def get_cli_commands(self) -> List[CliCommandDef]:
        return list(REGISTERED_CLI_COMMANDS_MAP.values())

    def get_cli_command(self, command_id: str) -> CliCommandDef:
        for cmd in REGISTERED_CLI_COMMANDS_MAP.values():
            if cmd.command_id == command_id or cmd.name == command_id:
                return cmd
        raise TerminalCliCommandUnknownError(command_id)
