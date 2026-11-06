"""Stage 148 Task Management and Multi-Agent Collaboration API."""

from __future__ import annotations

from typing import Annotated, Any

from atlas.agents.errors import (
    ApprovalExpiredError,
    BudgetExceededError,
    CollaborationError,
    SecurityViolationError,
    TaskNotFoundError,
    TaskValidationError,
)
from atlas.agents.tasks import (
    AgentMessage,
    AgentTask,
    AgentTaskReview,
    MessageType,
    ReviewStatus,
    TaskPriority,
    TaskService,
    TaskStatus,
)
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.agent_teams import get_team_service

router = APIRouter(prefix="/agents/tasks", tags=["Agent Tasks"])
_task_service: TaskService | None = None


def get_task_service() -> TaskService:
    global _task_service
    if _task_service is None:
        _task_service = TaskService(get_team_service())
    return _task_service


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4_000)
    priority: TaskPriority = TaskPriority.NORMAL
    department_id: str | None = None
    team_id: str | None = None
    project_id: str | None = None
    parent_task_id: str | None = None
    assigned_agent_id: str | None = None
    input_data: dict[str, Any] = Field(default_factory=dict)
    expected_output_schema: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    budget_limit_usd: float = Field(default=50.0, ge=0)
    deadline: str | None = None
    requires_human_approval: bool = False


class TaskAssignRequest(BaseModel):
    agent_id: str


class TaskReviewRequest(BaseModel):
    reviewer_agent_id: str
    status: ReviewStatus
    feedback: str = Field(default="", max_length=2_000)


class MessageSendRequest(BaseModel):
    team_id: str
    sender_agent_id: str
    recipient_agent_id: str
    message_type: MessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None


class MessageResponse(BaseModel):
    message_id: str
    team_id: str
    sender_agent_id: str
    recipient_agent_id: str
    message_type: str
    payload: dict[str, Any]
    task_id: str | None
    correlation_id: str | None
    created_at: str


class TaskResponse(BaseModel):
    task_id: str
    title: str
    description: str
    priority: str
    status: str
    department_id: str | None
    team_id: str | None
    project_id: str | None
    parent_task_id: str | None
    assigned_agent_id: str | None
    delegation_depth: int
    input_data: dict[str, Any]
    output_data: dict[str, Any] | None
    dependencies: list[str]
    subtask_ids: list[str]
    deadline: str | None
    budget_limit_usd: float
    cost_estimate_usd: float
    tokens_used: int
    model_calls: int
    error_message: str | None
    requires_human_approval: bool
    approval_id: str | None
    review_status: str | None
    artifacts: list[dict[str, Any]]
    created_at: str
    started_at: str | None
    completed_at: str | None


class TaskReviewResponse(BaseModel):
    review_id: str
    task_id: str
    reviewer_agent_id: str
    status: str
    criteria: dict[str, Any]
    feedback: str
    created_at: str


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    return str(principal.raw_claims.get("tenant_id", principal.sub)), principal.sub


def _task_response(t: AgentTask) -> TaskResponse:
    return TaskResponse(
        task_id=t.task_id,
        title=t.title,
        description=t.description,
        priority=t.priority.value,
        status=t.status.value,
        department_id=t.department_id,
        team_id=t.team_id,
        project_id=t.project_id,
        parent_task_id=t.parent_task_id,
        assigned_agent_id=t.assigned_agent_id,
        delegation_depth=t.delegation_depth,
        input_data=t.input_data,
        output_data=t.output_data,
        dependencies=list(t.dependencies),
        subtask_ids=list(t.subtask_ids),
        deadline=t.deadline,
        budget_limit_usd=t.budget_limit_usd,
        cost_estimate_usd=t.cost_estimate_usd,
        tokens_used=t.tokens_used,
        model_calls=t.model_calls,
        error_message=t.error_message,
        requires_human_approval=t.requires_human_approval,
        approval_id=t.approval_id,
        review_status=t.review_status.value if t.review_status else None,
        artifacts=list(t.artifacts),
        created_at=t.created_at.isoformat(),
        started_at=t.started_at.isoformat() if t.started_at else None,
        completed_at=t.completed_at.isoformat() if t.completed_at else None,
    )


def _msg_response(m: AgentMessage) -> MessageResponse:
    return MessageResponse(
        message_id=m.message_id,
        team_id=m.team_id,
        sender_agent_id=m.sender_agent_id,
        recipient_agent_id=m.recipient_agent_id,
        message_type=m.message_type.value,
        payload=m.payload,
        task_id=m.task_id,
        correlation_id=m.correlation_id,
        created_at=m.created_at.isoformat(),
    )


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
    department_id: str | None = None,
    team_id: str | None = None,
    project_id: str | None = None,
    status: TaskStatus | None = None,
) -> list[TaskResponse]:
    tenant_id, owner_id = _identity(current_user)
    return [
        _task_response(t)
        for t in service.list_tasks(
            tenant_id=tenant_id,
            owner_id=owner_id,
            department_id=department_id,
            team_id=team_id,
            project_id=project_id,
            status=status,
        )
    ]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    request: TaskCreateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        task = service.create_task(
            tenant_id=tenant_id,
            owner_id=owner_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            department_id=request.department_id,
            team_id=request.team_id,
            project_id=request.project_id,
            parent_task_id=request.parent_task_id,
            assigned_agent_id=request.assigned_agent_id,
            input_data=request.input_data,
            expected_output_schema=request.expected_output_schema,
            dependencies=request.dependencies,
            budget_limit_usd=request.budget_limit_usd,
            deadline=request.deadline,
            requires_human_approval=request.requires_human_approval,
        )
    except (TaskValidationError, CollaborationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _task_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _task_response(service.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id))
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc


@router.post("/{task_id}/plan", response_model=list[TaskResponse])
def plan_task(
    task_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> list[TaskResponse]:
    tenant_id, owner_id = _identity(current_user)
    try:
        _, subtasks = service.plan_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
        return [_task_response(s) for s in subtasks]
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
    except TaskValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    task_id: str,
    request: TaskAssignRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _task_response(
            service.assign_task(
                task_id=task_id,
                agent_id=request.agent_id,
                tenant_id=tenant_id,
                owner_id=owner_id,
            )
        )
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
    except TaskValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{task_id}/run", response_model=TaskResponse)
def run_task(
    task_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _task_response(service.run_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id))
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
    except (BudgetExceededError, SecurityViolationError) as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(
    task_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _task_response(service.cancel_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id))
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc


@router.get("/{task_id}/messages", response_model=list[MessageResponse])
def get_task_messages(
    task_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> list[MessageResponse]:
    tenant_id, owner_id = _identity(current_user)
    task = service.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
    if not task.team_id:
        return []
    return [
        _msg_response(m)
        for m in service.list_messages(tenant_id=tenant_id, team_id=task.team_id, task_id=task_id)
    ]


@router.post("/{task_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_task_message(
    task_id: str,
    request: MessageSendRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> MessageResponse:
    tenant_id, owner_id = _identity(current_user)
    task = service.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
    try:
        msg = service.send_message(
            tenant_id=tenant_id,
            team_id=request.team_id,
            sender_agent_id=request.sender_agent_id,
            recipient_agent_id=request.recipient_agent_id,
            message_type=request.message_type,
            payload=request.payload,
            task_id=task.task_id,
            correlation_id=request.correlation_id,
        )
    except CollaborationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _msg_response(msg)


@router.post("/{task_id}/review", response_model=TaskReviewResponse)
def submit_task_review(
    task_id: str,
    request: TaskReviewRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskReviewResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        rev = service.submit_review(
            task_id=task_id,
            reviewer_agent_id=request.reviewer_agent_id,
            status=request.status,
            feedback=request.feedback,
            tenant_id=tenant_id,
            owner_id=owner_id,
        )
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
    except CollaborationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return TaskReviewResponse(
        review_id=rev.review_id,
        task_id=rev.task_id,
        reviewer_agent_id=rev.reviewer_agent_id,
        status=rev.status.value,
        criteria=rev.criteria,
        feedback=rev.feedback,
        created_at=rev.created_at.isoformat(),
    )


@router.get("/{task_id}/artifacts", response_model=list[dict[str, Any]])
def get_task_artifacts(
    task_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> list[dict[str, Any]]:
    tenant_id, owner_id = _identity(current_user)
    try:
        task = service.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
        return list(task.artifacts)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
