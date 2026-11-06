"""Stage 148 Multi-Agent Collaboration, Department Registry, and Enterprise Orchestration."""

from atlas.agents.departments import (
    DEPARTMENT_TEMPLATES,
    DepartmentDefinition,
    DepartmentRegistryService,
    DepartmentStatus,
    DepartmentTemplate,
)
from atlas.agents.domain import (
    AgentDefinition,
    AgentRun,
    AgentRunEvent,
    AgentRunStatus,
    AgentStatus,
    AgentVersion,
)
from atlas.agents.errors import (
    AgentError,
    AgentNotFoundError,
    AgentValidationError,
    ApprovalExpiredError,
    ApprovalNotFoundError,
    BudgetExceededError,
    CollaborationError,
    DepartmentNotFoundError,
    DepartmentValidationError,
    SecurityViolationError,
    TaskNotFoundError,
    TaskValidationError,
)
from atlas.agents.governance import AgentGovernance
from atlas.agents.operations import OperationsService
from atlas.agents.service import AgentRegistryService
from atlas.agents.tasks import (
    AgentMessage,
    AgentProject,
    AgentTask,
    AgentTaskReview,
    ApprovalRequest,
    ApprovalStatus,
    MessageType,
    ReviewStatus,
    TaskPriority,
    TaskService,
    TaskStatus,
)
from atlas.agents.teams import (
    TeamDefinition,
    TeamMember,
    TeamRegistryService,
    TeamRole,
    TeamStatus,
)

__all__ = [
    # Agents
    "AgentDefinition",
    "AgentRegistryService",
    "AgentRun",
    "AgentRunEvent",
    "AgentRunStatus",
    "AgentStatus",
    "AgentVersion",
    # Departments
    "DEPARTMENT_TEMPLATES",
    "DepartmentDefinition",
    "DepartmentRegistryService",
    "DepartmentStatus",
    "DepartmentTemplate",
    # Teams
    "TeamDefinition",
    "TeamMember",
    "TeamRegistryService",
    "TeamRole",
    "TeamStatus",
    # Tasks & Collaboration
    "AgentMessage",
    "AgentProject",
    "AgentTask",
    "AgentTaskReview",
    "ApprovalRequest",
    "ApprovalStatus",
    "MessageType",
    "ReviewStatus",
    "TaskPriority",
    "TaskService",
    "TaskStatus",
    # Governance & Operations
    "AgentGovernance",
    "OperationsService",
    # Errors
    "AgentError",
    "AgentNotFoundError",
    "AgentValidationError",
    "ApprovalExpiredError",
    "ApprovalNotFoundError",
    "BudgetExceededError",
    "CollaborationError",
    "DepartmentNotFoundError",
    "DepartmentValidationError",
    "SecurityViolationError",
    "TaskNotFoundError",
    "TaskValidationError",
]
