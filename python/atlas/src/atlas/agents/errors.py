"""Errors raised by the ATLAS agent and team orchestration foundation."""

from __future__ import annotations


class AgentError(Exception):
    """Base error for agent and team registry operations."""


class AgentNotFoundError(AgentError):
    """The requested agent, team, department, or task is not visible to the caller."""


class AgentValidationError(AgentError):
    """The requested agent or team configuration is invalid."""


class DepartmentNotFoundError(AgentError):
    """The requested department does not exist or is inaccessible."""


class DepartmentValidationError(AgentError):
    """The department configuration violates policy or validation constraints."""


class TaskNotFoundError(AgentError):
    """The requested task does not exist or is inaccessible."""


class TaskValidationError(AgentError):
    """Task input, dependencies, or parameters are invalid."""


class ApprovalNotFoundError(AgentError):
    """The approval request was not found."""


class ApprovalExpiredError(AgentError):
    """The approval request has expired and cannot be acted upon."""


class BudgetExceededError(AgentError):
    """Task or team resource limits (tokens, cost, calls) have been exceeded."""


class SecurityViolationError(AgentError):
    """An operation attempted to violate tenant isolation, safety boundaries, or permissions."""


class CollaborationError(AgentError):
    """Inter-agent communication, delegation, or review failed."""
