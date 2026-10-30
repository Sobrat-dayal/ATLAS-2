"""Execution state machine and transition rules for Stage 123."""

from typing import Set

from atlas.terminal.execution.domain import ExecutionStatus
from atlas.terminal.execution.errors import TerminalExecutionInternalError

TERMINAL_STATES: Set[ExecutionStatus] = {
    ExecutionStatus.COMPLETED,
    ExecutionStatus.FAILED,
    ExecutionStatus.CANCELLED,
    ExecutionStatus.TIMED_OUT,
    ExecutionStatus.RESOURCE_LIMIT_EXCEEDED,
    ExecutionStatus.SECURITY_DENIED,
    ExecutionStatus.INFRASTRUCTURE_FAILED,
}

LEGAL_TRANSITIONS = {
    ExecutionStatus.CREATED: {
        ExecutionStatus.VALIDATING,
        ExecutionStatus.QUEUED,
        ExecutionStatus.FAILED,
        ExecutionStatus.SECURITY_DENIED,
        ExecutionStatus.CANCELLED,
    },
    ExecutionStatus.VALIDATING: {
        ExecutionStatus.QUEUED,
        ExecutionStatus.SECURITY_DENIED,
        ExecutionStatus.FAILED,
        ExecutionStatus.CANCELLED,
    },
    ExecutionStatus.QUEUED: {
        ExecutionStatus.PREPARING,
        ExecutionStatus.STARTING,
        ExecutionStatus.RUNNING,
        ExecutionStatus.CANCEL_REQUESTED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.FAILED,
    },
    ExecutionStatus.PREPARING: {
        ExecutionStatus.STARTING,
        ExecutionStatus.CANCEL_REQUESTED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.FAILED,
        ExecutionStatus.RESOURCE_LIMIT_EXCEEDED,
    },
    ExecutionStatus.STARTING: {
        ExecutionStatus.RUNNING,
        ExecutionStatus.CANCEL_REQUESTED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.FAILED,
    },
    ExecutionStatus.RUNNING: {
        ExecutionStatus.STREAMING,
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.CANCEL_REQUESTED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.TIMED_OUT,
        ExecutionStatus.RESOURCE_LIMIT_EXCEEDED,
    },
    ExecutionStatus.STREAMING: {
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.CANCEL_REQUESTED,
        ExecutionStatus.CANCELLED,
        ExecutionStatus.TIMED_OUT,
        ExecutionStatus.RESOURCE_LIMIT_EXCEEDED,
    },
    ExecutionStatus.CANCEL_REQUESTED: {
        ExecutionStatus.CANCELLED,
        ExecutionStatus.COMPLETED,
        ExecutionStatus.FAILED,
        ExecutionStatus.TIMED_OUT,
    },
}


class ExecutionStateMachine:
    """Enforces deterministic state transitions and prevents terminal status mutations."""

    @staticmethod
    def is_terminal(status: ExecutionStatus) -> bool:
        return status in TERMINAL_STATES

    @staticmethod
    def can_transition(current: ExecutionStatus, target: ExecutionStatus) -> bool:
        if current in TERMINAL_STATES:
            return False
        if current == target:
            return True
        allowed = LEGAL_TRANSITIONS.get(current, set())
        return target in allowed

    @staticmethod
    def validate_transition(current: ExecutionStatus, target: ExecutionStatus) -> None:
        if current in TERMINAL_STATES:
            raise TerminalExecutionInternalError(
                f"Cannot transition terminal execution from terminal state '{current.value}' to '{target.value}'."
            )
        if not ExecutionStateMachine.can_transition(current, target):
            raise TerminalExecutionInternalError(
                f"Illegal execution state transition from '{current.value}' to '{target.value}'."
            )
