"""Thread-safe execution scheduler and queue for Stage 123."""

import collections
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.terminal.execution.cli_router import AtlasCliRouter
from atlas.terminal.execution.domain import (
    ExecutionOutputChunk,
    ExecutionStatus,
    ExecutionType,
    StreamOutputType,
    TerminalExecution,
)
from atlas.terminal.execution.errors import (
    TerminalCliArgumentInvalidError,
    TerminalCliCommandUnknownError,
    TerminalCliMutationNotAllowedError,
    TerminalExecutionAccessDeniedError,
    TerminalExecutionCancelFailedError,
    TerminalExecutionInputTooLargeError,
    TerminalExecutionNotFoundError,
    TerminalExecutionQuotaExceededError,
    TerminalSqlStatementNotAllowedError,
)
from atlas.terminal.execution.python_sandbox import PythonSandboxRunner
from atlas.terminal.execution.sql_runner import SqlSandboxRunner
from atlas.terminal.execution.state_machine import TERMINAL_STATES


class ExecutionScheduler:
    """Manages execution queue, quotas, worker dispatch, cancellation, and streaming output buffers."""

    _instance = None
    _lock = threading.Lock()

    def __init__(
        self,
        max_concurrent_per_user: int = 2,
        max_history_size: int = 1000,
    ):
        self.max_concurrent_per_user = max_concurrent_per_user
        self.max_history_size = max_history_size

        self._executions: Dict[str, TerminalExecution] = {}
        self._execution_order: collections.deque = collections.deque(maxlen=max_history_size)
        self._output_chunks: Dict[str, List[ExecutionOutputChunk]] = collections.defaultdict(list)
        self._cancellation_events: Dict[str, threading.Event] = {}

        self._active_per_user: Dict[str, int] = collections.defaultdict(int)
        self._rlock = threading.RLock()

        self._python_runner = PythonSandboxRunner()
        self._sql_runner = SqlSandboxRunner()
        self._cli_router = AtlasCliRouter()

    @classmethod
    def get_instance(cls) -> "ExecutionScheduler":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def submit_execution(
        self,
        execution: TerminalExecution,
        workspace_id: Optional[str] = None,
    ) -> TerminalExecution:
        """Enforce quotas, queue execution, and run worker synchronously/asynchronously."""
        user_id = execution.owner_user_id

        with self._rlock:
            if self._active_per_user[user_id] >= self.max_concurrent_per_user:
                raise TerminalExecutionQuotaExceededError(
                    f"User {user_id} has reached maximum concurrent executions ({self.max_concurrent_per_user})."
                )

            self._executions[execution.execution_id] = execution
            self._execution_order.append(execution.execution_id)
            cancel_event = threading.Event()
            self._cancellation_events[execution.execution_id] = cancel_event
            self._active_per_user[user_id] += 1

            execution.status = ExecutionStatus.QUEUED
            execution.state_revision += 1

        try:
            self._run_job(execution, cancel_event, workspace_id)
        finally:
            with self._rlock:
                if self._active_per_user[user_id] > 0:
                    self._active_per_user[user_id] -= 1
                self._cancellation_events.pop(execution.execution_id, None)

        return execution

    def _run_job(
        self,
        execution: TerminalExecution,
        cancel_event: threading.Event,
        workspace_id: Optional[str],
    ) -> None:
        """Run execution against corresponding sandboxed runner."""
        with self._rlock:
            execution.status = ExecutionStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            execution.state_revision += 1

        def append_chunk(st_type: StreamOutputType, payload: str):
            with self._rlock:
                seq = len(self._output_chunks[execution.execution_id]) + 1
                chunk = ExecutionOutputChunk(
                    execution_id=execution.execution_id,
                    seq_num=seq,
                    stream_type=st_type,
                    payload=payload,
                )
                self._output_chunks[execution.execution_id].append(chunk)

        res: Dict[str, Any] = {}
        try:
            if execution.execution_type == ExecutionType.PYTHON:
                res = self._python_runner.execute(
                    execution_id=execution.execution_id,
                    code=execution.input_code,
                    resource_profile=execution.resource_profile,
                    cancellation_event=cancel_event,
                    on_chunk=append_chunk,
                )
            elif execution.execution_type == ExecutionType.SQL:
                res = self._sql_runner.execute(
                    execution_id=execution.execution_id,
                    sql_text=execution.input_code,
                    source_id=execution.source_id,
                    resource_profile=execution.resource_profile,
                    cancellation_event=cancel_event,
                )
                if res.get("stdout"):
                    append_chunk(StreamOutputType.STDOUT, res["stdout"])
                if res.get("stderr"):
                    append_chunk(StreamOutputType.STDERR, res["stderr"])
            elif execution.execution_type == ExecutionType.ATLAS_CLI:
                res = self._cli_router.execute(
                    execution_id=execution.execution_id,
                    command_line=execution.input_code,
                    user_id=execution.owner_user_id,
                    workspace_id=workspace_id,
                )
                if res.get("stdout"):
                    append_chunk(StreamOutputType.STDOUT, res["stdout"])
                if res.get("stderr"):
                    append_chunk(StreamOutputType.STDERR, res["stderr"])
            else:
                res = {
                    "status": ExecutionStatus.FAILED,
                    "stdout": "",
                    "stderr": f"Execution type '{execution.execution_type}' unsupported.",
                    "duration_ms": 0.0,
                    "error_code": "TERMINAL_EXECUTION_TYPE_UNSUPPORTED",
                    "error_message": f"Unsupported execution type {execution.execution_type}",
                    "row_count": None,
                    "tabular_result": None,
                }
        except (
            TerminalCliCommandUnknownError,
            TerminalCliArgumentInvalidError,
            TerminalCliMutationNotAllowedError,
            TerminalSqlStatementNotAllowedError,
            TerminalExecutionInputTooLargeError,
        ) as client_err:
            with self._rlock:
                execution.status = ExecutionStatus.FAILED
                execution.error_code = client_err.code
                execution.error_message = client_err.message
                execution.finished_at = datetime.now(timezone.utc)
                execution.state_revision += 1
            append_chunk(StreamOutputType.ERROR, client_err.message)
            raise
        except Exception as exc:
            res = {
                "status": ExecutionStatus.FAILED,
                "stdout": "",
                "stderr": f"Fatal worker error: {str(exc)}",
                "duration_ms": 0.0,
                "error_code": "TERMINAL_EXECUTION_INTERNAL_ERROR",
                "error_message": str(exc),
                "row_count": None,
                "tabular_result": None,
            }
            append_chunk(StreamOutputType.ERROR, f"Fatal worker exception: {str(exc)}")

        with self._rlock:
            execution.status = res.get("status", ExecutionStatus.FAILED)
            execution.duration_ms = res.get("duration_ms")
            execution.error_code = res.get("error_code")
            execution.error_message = res.get("error_message")
            execution.row_count = res.get("row_count")
            execution.stdout_summary = res.get("stdout")
            execution.tabular_result = res.get("tabular_result")
            execution.finished_at = datetime.now(timezone.utc)
            execution.state_revision += 1

    def cancel_execution(self, execution_id: str, user_id: str) -> TerminalExecution:
        """Request cancellation of an active execution."""
        with self._rlock:
            execution = self._executions.get(execution_id)
            if not execution:
                raise TerminalExecutionNotFoundError(execution_id)

            if execution.owner_user_id != user_id:
                raise TerminalExecutionAccessDeniedError(execution_id, user_id)

            if execution.status in TERMINAL_STATES:
                raise TerminalExecutionCancelFailedError(
                    execution_id,
                    f"Execution is already in terminal state '{execution.status.value}'.",
                )

            execution.cancellation_requested_at = datetime.now(timezone.utc)
            execution.status = ExecutionStatus.CANCEL_REQUESTED
            execution.state_revision += 1

            cancel_event = self._cancellation_events.get(execution_id)
            if cancel_event:
                cancel_event.set()

            return execution

    def get_execution(self, execution_id: str, user_id: str) -> TerminalExecution:
        """Retrieve execution by ID with owner validation."""
        with self._rlock:
            execution = self._executions.get(execution_id)
            if not execution:
                raise TerminalExecutionNotFoundError(execution_id)

            if execution.owner_user_id != user_id:
                raise TerminalExecutionAccessDeniedError(execution_id, user_id)

            return execution

    def get_execution_output(self, execution_id: str, user_id: str) -> List[ExecutionOutputChunk]:
        """Retrieve bounded output chunks for an execution."""
        self.get_execution(execution_id, user_id)  # validates existence & ownership
        with self._rlock:
            return list(self._output_chunks.get(execution_id, []))

    def list_executions(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        execution_type: Optional[ExecutionType] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TerminalExecution]:
        """Query execution history for an authenticated user."""
        with self._rlock:
            results: List[TerminalExecution] = []
            for exec_id in reversed(self._execution_order):
                item = self._executions.get(exec_id)
                if not item or item.owner_user_id != user_id:
                    continue
                if session_id and item.terminal_session_id != session_id:
                    continue
                if execution_type and item.execution_type != execution_type:
                    continue
                if status and item.status != status:
                    continue
                results.append(item)

            return results[offset : offset + limit]
