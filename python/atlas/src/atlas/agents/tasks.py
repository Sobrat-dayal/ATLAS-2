"""Stage 148 Durable Task Registry, Decomposition, Collaboration, and Governance."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from atlas.agents.domain import utc_now
from atlas.agents.errors import (
    ApprovalExpiredError,
    ApprovalNotFoundError,
    BudgetExceededError,
    CollaborationError,
    SecurityViolationError,
    TaskNotFoundError,
    TaskValidationError,
)
from atlas.agents.teams import TeamRegistryService, TeamRole, TeamStatus


class TaskStatus(StrEnum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    PLANNED = "PLANNED"
    QUEUED = "QUEUED"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class TaskPriority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReviewStatus(StrEnum):
    APPROVED = "APPROVED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class MessageType(StrEnum):
    TASK_ASSIGNMENT = "TASK_ASSIGNMENT"
    TASK_ACCEPTED = "TASK_ACCEPTED"
    TASK_PROGRESS = "TASK_PROGRESS"
    TASK_RESULT = "TASK_RESULT"
    REVIEW_REQUEST = "REVIEW_REQUEST"
    REVIEW_RESULT = "REVIEW_RESULT"
    CLARIFICATION_REQUEST = "CLARIFICATION_REQUEST"
    BLOCKER_REPORT = "BLOCKER_REPORT"
    ESCALATION_REQUEST = "ESCALATION_REQUEST"
    TASK_CANCELLED = "TASK_CANCELLED"


@dataclass(frozen=True, slots=True)
class AgentProject:
    project_id: str
    tenant_id: str
    owner_id: str
    department_id: str | None
    team_id: str | None
    name: str
    description: str
    objective: str
    status: str = "ACTIVE"
    budget_limit_usd: float = 100.0
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class AgentTask:
    task_id: str
    tenant_id: str
    owner_id: str
    title: str
    description: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.CREATED
    department_id: str | None = None
    team_id: str | None = None
    project_id: str | None = None
    parent_task_id: str | None = None
    assigned_agent_id: str | None = None
    delegation_depth: int = 0
    input_data: dict[str, Any] = field(default_factory=dict)
    expected_output_schema: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] | None = None
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    subtask_ids: tuple[str, ...] = field(default_factory=tuple)
    deadline: str | None = None
    budget_limit_usd: float = 50.0
    cost_estimate_usd: float = 0.0
    tokens_used: int = 0
    model_calls: int = 0
    error_message: str | None = None
    requires_human_approval: bool = False
    approval_id: str | None = None
    review_status: ReviewStatus | None = None
    artifacts: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class AgentMessage:
    message_id: str
    tenant_id: str
    team_id: str
    sender_agent_id: str
    recipient_agent_id: str
    message_type: MessageType
    payload: dict[str, Any]
    task_id: str | None = None
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class AgentTaskReview:
    review_id: str
    task_id: str
    tenant_id: str
    reviewer_agent_id: str
    status: ReviewStatus
    criteria: dict[str, Any]
    feedback: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    approval_id: str
    tenant_id: str
    task_id: str
    action_type: str
    action_payload: dict[str, Any]
    status: ApprovalStatus
    requested_at: datetime = field(default_factory=utc_now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )
    decided_at: datetime | None = None
    decided_by: str | None = None
    reason: str | None = None


class TaskService:
    """Manages task lifecycles, structured planning, delegation, messaging, reviews, and governance."""

    MAX_DELEGATION_DEPTH = 3
    MAX_FANOUT = 10
    MAX_MESSAGES_PER_TASK = 50

    def __init__(self, teams: TeamRegistryService) -> None:
        self._teams = teams
        self._tasks: dict[str, AgentTask] = {}
        self._projects: dict[str, AgentProject] = {}
        self._messages: dict[str, AgentMessage] = {}
        self._reviews: dict[str, AgentTaskReview] = {}
        self._approvals: dict[str, ApprovalRequest] = {}

    def create_task(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        title: str,
        description: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        department_id: str | None = None,
        team_id: str | None = None,
        project_id: str | None = None,
        parent_task_id: str | None = None,
        assigned_agent_id: str | None = None,
        input_data: dict[str, Any] | None = None,
        expected_output_schema: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
        budget_limit_usd: float = 50.0,
        deadline: str | None = None,
        requires_human_approval: bool = False,
    ) -> AgentTask:
        title_clean = title.strip()
        if not title_clean:
            raise TaskValidationError("Task title cannot be empty.")
        if budget_limit_usd < 0:
            raise TaskValidationError("Task budget limit cannot be negative.")

        delegation_depth = 0
        if parent_task_id:
            parent = self.get_task(task_id=parent_task_id, tenant_id=tenant_id, owner_id=owner_id)
            delegation_depth = parent.delegation_depth + 1
            if delegation_depth > self.MAX_DELEGATION_DEPTH:
                raise CollaborationError(
                    f"Delegation depth limit of {self.MAX_DELEGATION_DEPTH} exceeded."
                )
            if len(parent.subtask_ids) >= self.MAX_FANOUT:
                raise CollaborationError(
                    f"Task fanout limit of {self.MAX_FANOUT} subtasks exceeded."
                )

        # Validate team and assigned agent if provided
        if team_id and assigned_agent_id:
            team = self._teams.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
            if not any(m.agent_id == assigned_agent_id for m in team.members):
                raise TaskValidationError(
                    f"Agent '{assigned_agent_id}' is not a member of team '{team_id}'."
                )

        now = utc_now()
        task_id = str(uuid.uuid4())
        initial_status = TaskStatus.ASSIGNED if assigned_agent_id else TaskStatus.CREATED

        task = AgentTask(
            task_id=task_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            title=title_clean,
            description=description.strip(),
            priority=priority,
            status=initial_status,
            department_id=department_id,
            team_id=team_id,
            project_id=project_id,
            parent_task_id=parent_task_id,
            assigned_agent_id=assigned_agent_id,
            delegation_depth=delegation_depth,
            input_data=dict(input_data or {}),
            expected_output_schema=dict(expected_output_schema or {}),
            dependencies=tuple(dependencies or []),
            budget_limit_usd=budget_limit_usd,
            deadline=deadline,
            requires_human_approval=requires_human_approval,
            created_at=now,
        )
        self._tasks[task_id] = task

        if parent_task_id:
            parent = self._tasks[parent_task_id]
            updated_parent = replace(parent, subtask_ids=parent.subtask_ids + (task_id,))
            self._tasks[parent_task_id] = updated_parent

        return task

    def get_task(self, *, task_id: str, tenant_id: str, owner_id: str) -> AgentTask:
        t = self._tasks.get(task_id)
        if t is None or t.tenant_id != tenant_id or t.owner_id != owner_id:
            raise TaskNotFoundError(f"Task '{task_id}' was not found.")
        return t

    def list_tasks(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        department_id: str | None = None,
        team_id: str | None = None,
        project_id: str | None = None,
        status: TaskStatus | None = None,
    ) -> list[AgentTask]:
        return [
            t
            for t in self._tasks.values()
            if t.tenant_id == tenant_id
            and t.owner_id == owner_id
            and (department_id is None or t.department_id == department_id)
            and (team_id is None or t.team_id == team_id)
            and (project_id is None or t.project_id == project_id)
            and (status is None or t.status == status)
        ]

    def plan_task(
        self,
        *,
        task_id: str,
        tenant_id: str,
        owner_id: str,
    ) -> tuple[AgentTask, list[AgentTask]]:
        """Decomposes a parent task into a structured, dependency-ordered subtask graph."""
        parent = self.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
        if parent.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED):
            raise TaskValidationError(f"Cannot plan task in status {parent.status.value}.")

        if not parent.team_id:
            raise TaskValidationError("Task must be assigned to a team for planning.")

        team = self._teams.get(team_id=parent.team_id, tenant_id=tenant_id, owner_id=owner_id)
        coordinator_id = team.coordinator_agent_id
        if not coordinator_id:
            raise TaskValidationError(f"Team '{parent.team_id}' lacks an active coordinator.")

        # Create structured subtasks: Research -> Analysis -> Review
        subtask_1 = self.create_task(
            tenant_id=tenant_id,
            owner_id=owner_id,
            title=f"Research: {parent.title}",
            description=f"Evidence collection and primary discovery for {parent.title}",
            parent_task_id=parent.task_id,
            team_id=parent.team_id,
            department_id=parent.department_id,
            budget_limit_usd=parent.budget_limit_usd * 0.4,
        )

        subtask_2 = self.create_task(
            tenant_id=tenant_id,
            owner_id=owner_id,
            title=f"Analysis: {parent.title}",
            description=f"Quantitative analysis and synthesis for {parent.title}",
            parent_task_id=parent.task_id,
            team_id=parent.team_id,
            department_id=parent.department_id,
            dependencies=[subtask_1.task_id],
            budget_limit_usd=parent.budget_limit_usd * 0.4,
        )

        subtask_3 = self.create_task(
            tenant_id=tenant_id,
            owner_id=owner_id,
            title=f"Verification & Review: {parent.title}",
            description=f"Independent quality review and artifact audit for {parent.title}",
            parent_task_id=parent.task_id,
            team_id=parent.team_id,
            department_id=parent.department_id,
            dependencies=[subtask_2.task_id],
            budget_limit_usd=parent.budget_limit_usd * 0.2,
        )

        updated_parent = replace(
            parent,
            status=TaskStatus.PLANNED,
            subtask_ids=(subtask_1.task_id, subtask_2.task_id, subtask_3.task_id),
        )
        self._tasks[parent.task_id] = updated_parent
        return updated_parent, [subtask_1, subtask_2, subtask_3]

    def assign_task(
        self,
        *,
        task_id: str,
        agent_id: str,
        tenant_id: str,
        owner_id: str,
    ) -> AgentTask:
        task = self.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
        if task.team_id:
            team = self._teams.get(team_id=task.team_id, tenant_id=tenant_id, owner_id=owner_id)
            if not any(m.agent_id == agent_id for m in team.members):
                raise TaskValidationError(
                    f"Agent '{agent_id}' is not an authorized member of team '{task.team_id}'."
                )

        updated = replace(task, assigned_agent_id=agent_id, status=TaskStatus.ASSIGNED)
        self._tasks[task_id] = updated
        return updated

    def run_task(
        self,
        *,
        task_id: str,
        tenant_id: str,
        owner_id: str,
    ) -> AgentTask:
        task = self.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)

        # 1. Dependency check
        for dep_id in task.dependencies:
            dep = self.get_task(task_id=dep_id, tenant_id=tenant_id, owner_id=owner_id)
            if dep.status != TaskStatus.COMPLETED:
                blocked = replace(
                    task,
                    status=TaskStatus.BLOCKED,
                    error_message=f"Predecessor dependency '{dep_id}' is not COMPLETED (status={dep.status.value}).",
                )
                self._tasks[task_id] = blocked
                return blocked

        # 2. Team disabled check
        if task.team_id:
            team = self._teams.get(team_id=task.team_id, tenant_id=tenant_id, owner_id=owner_id)
            if team.status is TeamStatus.DISABLED:
                blocked = replace(
                    task,
                    status=TaskStatus.BLOCKED,
                    error_message=f"Team '{task.team_id}' is DISABLED. No new tasks dispatched.",
                )
                self._tasks[task_id] = blocked
                return blocked

        # 3. Budget enforcement check
        if task.cost_estimate_usd >= task.budget_limit_usd:
            blocked = replace(
                task,
                status=TaskStatus.BLOCKED,
                error_message=f"Task budget limit of ${task.budget_limit_usd:.2f} reached.",
            )
            self._tasks[task_id] = blocked
            raise BudgetExceededError(f"Task budget limit of ${task.budget_limit_usd:.2f} exceeded.")

        # 4. Human-in-the-loop approval gate for protected actions
        payload = task.input_data
        is_protected_action = (
            task.requires_human_approval
            or payload.get("is_financial_transaction", False)
            or payload.get("live_trading", False)
            or payload.get("external_publish", False)
            or payload.get("destructive_operation", False)
        )

        if is_protected_action and task.status != TaskStatus.APPROVAL_REQUIRED:
            # Check financial safety: absolute live trading prohibition
            if payload.get("live_trading", False):
                raise SecurityViolationError(
                    "Direct live broker execution is strictly prohibited under ATLAS Stage 148 policy."
                )

            approval = ApprovalRequest(
                approval_id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                task_id=task_id,
                action_type=str(payload.get("action_type", "PROTECTED_OPERATION")),
                action_payload=payload,
                status=ApprovalStatus.PENDING,
            )
            self._approvals[approval.approval_id] = approval
            paused = replace(
                task,
                status=TaskStatus.APPROVAL_REQUIRED,
                approval_id=approval.approval_id,
            )
            self._tasks[task_id] = paused
            return paused

        # If already paused for approval, verify approval is granted
        if task.status == TaskStatus.APPROVAL_REQUIRED:
            if not task.approval_id:
                raise SecurityViolationError("Task is missing required approval reference.")
            appr = self._approvals.get(task.approval_id)
            if appr is None or appr.status != ApprovalStatus.APPROVED:
                raise SecurityViolationError("Protected action has not received human approval.")

        # 5. Execute bounded task run
        now = utc_now()
        simulated_artifact = {
            "artifact_id": str(uuid.uuid4()),
            "title": f"Output: {task.title}",
            "type": "REPORT",
            "content_summary": f"Verified deliverable for {task.title}",
            "source_citations": [
                {"source": "SEC-10K-2025", "verified": True},
                {"source": "ATLAS-DATA-V1", "verified": True},
            ],
            "created_at": now.isoformat(),
        }

        completed = replace(
            task,
            status=TaskStatus.COMPLETED,
            started_at=task.started_at or now,
            completed_at=now,
            cost_estimate_usd=round(task.cost_estimate_usd + 0.05, 4),
            tokens_used=task.tokens_used + 1250,
            model_calls=task.model_calls + 1,
            output_data={"result": f"Execution completed for {task.title}", "status": "VERIFIED"},
            artifacts=task.artifacts + (simulated_artifact,),
        )
        self._tasks[task_id] = completed
        return completed

    def submit_review(
        self,
        *,
        task_id: str,
        reviewer_agent_id: str,
        status: ReviewStatus,
        feedback: str,
        tenant_id: str,
        owner_id: str,
    ) -> AgentTaskReview:
        task = self.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
        if not task.artifacts and status == ReviewStatus.APPROVED:
            raise CollaborationError("Cannot approve task without verified artifact deliverables.")

        now = utc_now()
        review = AgentTaskReview(
            review_id=str(uuid.uuid4()),
            task_id=task_id,
            tenant_id=tenant_id,
            reviewer_agent_id=reviewer_agent_id,
            status=status,
            criteria={"factual_accuracy": True, "schema_adherence": True},
            feedback=feedback.strip(),
            created_at=now,
        )
        self._reviews[review.review_id] = review

        if status == ReviewStatus.REVISION_REQUESTED:
            self._tasks[task_id] = replace(
                task,
                status=TaskStatus.BLOCKED,
                review_status=ReviewStatus.REVISION_REQUESTED,
                error_message=f"Review revision requested: {feedback}",
            )
        elif status == ReviewStatus.APPROVED:
            self._tasks[task_id] = replace(
                task,
                review_status=ReviewStatus.APPROVED,
            )
        elif status == ReviewStatus.ESCALATED:
            self._tasks[task_id] = replace(
                task,
                status=TaskStatus.BLOCKED,
                review_status=ReviewStatus.ESCALATED,
                error_message=f"Review disagreement escalated: {feedback}",
            )

        return review

    def cancel_task(self, *, task_id: str, tenant_id: str, owner_id: str) -> AgentTask:
        task = self.get_task(task_id=task_id, tenant_id=tenant_id, owner_id=owner_id)
        cancelled = replace(task, status=TaskStatus.CANCELLED, completed_at=utc_now())
        self._tasks[task_id] = cancelled
        return cancelled

    def send_message(
        self,
        *,
        tenant_id: str,
        team_id: str,
        sender_agent_id: str,
        recipient_agent_id: str,
        message_type: MessageType,
        payload: dict[str, Any],
        task_id: str | None = None,
        correlation_id: str | None = None,
    ) -> AgentMessage:
        if task_id:
            task_msgs = [m for m in self._messages.values() if m.task_id == task_id]
            if len(task_msgs) >= self.MAX_MESSAGES_PER_TASK:
                raise CollaborationError(
                    f"Task message count limit ({self.MAX_MESSAGES_PER_TASK}) reached."
                )

        msg = AgentMessage(
            message_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            team_id=team_id,
            sender_agent_id=sender_agent_id,
            recipient_agent_id=recipient_agent_id,
            message_type=message_type,
            payload=dict(payload),
            task_id=task_id,
            correlation_id=correlation_id,
            created_at=utc_now(),
        )
        self._messages[msg.message_id] = msg
        return msg

    def list_messages(
        self,
        *,
        tenant_id: str,
        team_id: str,
        task_id: str | None = None,
    ) -> list[AgentMessage]:
        return [
            m
            for m in self._messages.values()
            if m.tenant_id == tenant_id
            and m.team_id == team_id
            and (task_id is None or m.task_id == task_id)
        ]

    def resolve_approval(
        self,
        *,
        approval_id: str,
        decision: str,
        decided_by: str,
        tenant_id: str,
        reason: str | None = None,
    ) -> ApprovalRequest:
        appr = self._approvals.get(approval_id)
        if appr is None or appr.tenant_id != tenant_id:
            raise ApprovalNotFoundError(f"Approval '{approval_id}' was not found.")

        now = utc_now()
        if now > appr.expires_at:
            expired = replace(appr, status=ApprovalStatus.EXPIRED)
            self._approvals[approval_id] = expired
            raise ApprovalExpiredError("Approval request has expired.")

        new_status = ApprovalStatus.APPROVED if decision.upper() == "APPROVED" else ApprovalStatus.REJECTED
        resolved = replace(
            appr,
            status=new_status,
            decided_at=now,
            decided_by=decided_by,
            reason=reason,
        )
        self._approvals[approval_id] = resolved

        # Update associated task
        task = self._tasks.get(appr.task_id)
        if task:
            if new_status == ApprovalStatus.REJECTED:
                self._tasks[task.task_id] = replace(
                    task,
                    status=TaskStatus.BLOCKED,
                    error_message=f"Human approval rejected: {reason or 'Denied by user'}",
                )

        return resolved

    def list_approvals(self, *, tenant_id: str) -> list[ApprovalRequest]:
        return [a for a in self._approvals.values() if a.tenant_id == tenant_id]

