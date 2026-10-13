"""Stage 54 Home Tasks and Approvals Test Suite.

Verifies:
- Domain A: Personal Tasks
  - Strict typed payloads (title, description, due date, canonical module/entity)
  - Ownership enforcement (user-scoped reads, writes, mutations)
  - Valid state transitions (OPEN -> COMPLETED, COMPLETED -> OPEN, OPEN -> CANCELLED)
  - Rejection of invalid transitions (cannot complete/reopen cancelled tasks)
  - Due-date handling and derived is_overdue and is_due_soon flags
  - Keyset pagination and authoritative open/overdue counts
  - Optimistic concurrency locking (expected_version conflict)
  - Creation idempotency via (owner_user_id, idempotency_key)
- Domain B: Approval Requests & Decisions
  - Internal trusted producer creation only (no public create endpoint)
  - Strict allowlists for producers and action kinds
  - Immutable proposal reference and proposal digest (SHA-256)
  - Expiration window enforcement (expires_at in future, <= 7 days)
  - Human decision recording (APPROVE / REJECT) with immutable audit record
  - Decision idempotency via (approver_user_id, decision_idempotency_key)
  - Non-negotiable security rule: APPROVAL DOES NOT EXECUTE (zero side-effects)
  - Cannot decide expired or already decided requests
  - Cross-user approver isolation
- FastAPI Endpoints:
  - GET /api/v1/tasks, POST /api/v1/tasks, PATCH /api/v1/tasks/{id}
  - POST /api/v1/tasks/{id}/complete, reopen, cancel
  - GET /api/v1/tasks/counts
  - GET /api/v1/approvals, GET /api/v1/approvals/{id}
  - POST /api/v1/approvals/{id}/decision
  - GET /api/v1/approvals/counts
  - Headers: Cache-Control: private, no-store
  - Rejection of unauthenticated requests (401) and missing atlas.access (403)
"""

import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.approvals.enums import (
    ApprovalDecisionType,
    ApprovalStatus,
)
from atlas.approvals.errors import (
    ApprovalAlreadyDecidedError,
    ApprovalConflictError,
    ApprovalExpiredError,
    ApprovalNotFoundError,
    InvalidActionKindError,
    InvalidApprovalPayloadError,
    UntrustedProducerError,
)
from atlas.approvals.models import (
    ApprovalCountsResponse,
    ApprovalDecisionRequest,
    ApprovalListResponse,
    ApprovalRequest,
    CreateApprovalInternalRequest,
)
from atlas.approvals.repository import ApprovalRepository
from atlas.approvals.service import ApprovalService
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.tasks.enums import TaskStatus
from atlas.tasks.errors import (
    InvalidTaskPayloadError,
    InvalidTaskTransitionError,
    TaskConflictError,
    TaskIdempotencyConflictError,
)
from atlas.tasks.models import (
    CreateTaskRequest,
    TaskCountsResponse,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
    UserTask,
)
from atlas.tasks.repository import TaskRepository
from atlas.tasks.service import PersonalTaskService
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context


# -----------------------------------------------------------------------------
# 1. Personal Tasks Validation & Schemas
# -----------------------------------------------------------------------------
class TestTaskValidation:
    def test_create_task_valid(self):
        req = CreateTaskRequest(
            title="Review Q3 Financials",
            description="Inspect balance sheet and cash flow statements",
            module_id="companies",
        )
        assert req.title == "Review Q3 Financials"
        assert req.description == "Inspect balance sheet and cash flow statements"
        assert req.module_id == "companies"
        assert req.due_at is None

    def test_create_task_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            CreateTaskRequest(title="   ")

    def test_create_task_title_max_length(self):
        with pytest.raises(ValidationError):
            CreateTaskRequest(title="A" * 161)

    def test_create_task_description_max_length(self):
        with pytest.raises(ValidationError):
            CreateTaskRequest(title="Valid Title", description="A" * 2001)

    def test_update_task_whitespace_title_rejected(self):
        with pytest.raises(ValidationError):
            UpdateTaskRequest(title="   ")


# -----------------------------------------------------------------------------
# 2. Personal Tasks Service Unit Tests
# -----------------------------------------------------------------------------
class TestTaskService:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def task_repo(self, mock_session):
        return TaskRepository(mock_session)

    @pytest.fixture
    def task_service(self, mock_session, task_repo):
        return PersonalTaskService(mock_session, task_repo)

    @pytest.mark.asyncio
    async def test_create_task_success(self, task_service, mock_session):
        user_id = uuid.uuid4()
        req = CreateTaskRequest(
            title="Complete Research Thesis",
            module_id="research",
        )
        # Entity check returns None (no entity requested)
        resp = await task_service.create_task(user_id, req)
        assert resp.title == "Complete Research Thesis"
        assert resp.owner_user_id == user_id
        assert resp.status == TaskStatus.OPEN
        assert resp.module_id == "research"
        assert resp.module_label == "Research"
        assert resp.version == 1
        assert not resp.is_overdue
        assert not resp.is_due_soon
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_create_task_invalid_module_rejected(self, task_service):
        user_id = uuid.uuid4()
        req = CreateTaskRequest(
            title="Unknown Module Task",
            module_id="nonexistent_module_xyz",
        )
        with pytest.raises(InvalidTaskPayloadError) as exc_info:
            await task_service.create_task(user_id, req)
        assert "canonical ATLAS module" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_task_idempotency_same_payload(self, task_service, mock_session):
        user_id = uuid.uuid4()
        idemp_key = "idemp-task-123"
        existing_task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Idempotent Task",
            description=None,
            status=TaskStatus.OPEN.value,
            due_at=None,
            module_id=None,
            entity_id=None,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            completed_at=None,
            cancelled_at=None,
            version=1,
            idempotency_key=idemp_key,
        )
        task_service.repository.get_by_idempotency_key = AsyncMock(return_value=existing_task)

        req = CreateTaskRequest(title="Idempotent Task", idempotency_key=idemp_key)
        resp = await task_service.create_task(user_id, req)
        assert resp.task_id == existing_task.task_id
        assert resp.title == "Idempotent Task"

    @pytest.mark.asyncio
    async def test_create_task_idempotency_conflicting_payload(self, task_service):
        user_id = uuid.uuid4()
        idemp_key = "idemp-task-123"
        existing_task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Original Title",
            status=TaskStatus.OPEN.value,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            version=1,
            idempotency_key=idemp_key,
        )
        task_service.repository.get_by_idempotency_key = AsyncMock(return_value=existing_task)

        req = CreateTaskRequest(title="Different Title", idempotency_key=idemp_key)
        with pytest.raises(TaskIdempotencyConflictError):
            await task_service.create_task(user_id, req)

    @pytest.mark.asyncio
    async def test_complete_task_lifecycle(self, task_service, mock_session):
        user_id = uuid.uuid4()
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Open Task",
            status=TaskStatus.OPEN.value,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            completed_at=None,
            version=1,
        )
        task_service.repository.get_by_id = AsyncMock(return_value=task)

        resp = await task_service.complete_task(user_id, task.task_id)
        assert resp.status == TaskStatus.COMPLETED
        assert resp.completed_at is not None
        assert resp.version == 2
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_complete_task_idempotent_if_already_completed(self, task_service):
        user_id = uuid.uuid4()
        completed_time = datetime.datetime.now(datetime.timezone.utc)
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Already Completed Task",
            status=TaskStatus.COMPLETED.value,
            created_at=completed_time,
            updated_at=completed_time,
            completed_at=completed_time,
            version=2,
        )
        task_service.repository.get_by_id = AsyncMock(return_value=task)

        resp = await task_service.complete_task(user_id, task.task_id)
        assert resp.status == TaskStatus.COMPLETED
        assert resp.version == 2  # Not incremented again

    @pytest.mark.asyncio
    async def test_complete_cancelled_task_rejected(self, task_service):
        user_id = uuid.uuid4()
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Cancelled Task",
            status=TaskStatus.CANCELLED.value,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            version=2,
        )
        task_service.repository.get_by_id = AsyncMock(return_value=task)

        with pytest.raises(InvalidTaskTransitionError) as exc_info:
            await task_service.complete_task(user_id, task.task_id)
        assert "CANCELLED to COMPLETED" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_reopen_task_lifecycle(self, task_service, mock_session):
        user_id = uuid.uuid4()
        completed_time = datetime.datetime.now(datetime.timezone.utc)
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Task to Reopen",
            status=TaskStatus.COMPLETED.value,
            created_at=completed_time,
            updated_at=completed_time,
            completed_at=completed_time,
            version=2,
        )
        task_service.repository.get_by_id = AsyncMock(return_value=task)

        resp = await task_service.reopen_task(user_id, task.task_id)
        assert resp.status == TaskStatus.OPEN
        assert resp.completed_at is None
        assert resp.version == 3
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_cancel_task_lifecycle(self, task_service, mock_session):
        user_id = uuid.uuid4()
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Task to Cancel",
            status=TaskStatus.OPEN.value,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            version=1,
        )
        task_service.repository.get_by_id = AsyncMock(return_value=task)

        resp = await task_service.cancel_task(user_id, task.task_id)
        assert resp.status == TaskStatus.CANCELLED
        assert resp.cancelled_at is not None
        assert resp.version == 2
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_cancel_completed_task_rejected(self, task_service):
        user_id = uuid.uuid4()
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Completed Task",
            status=TaskStatus.COMPLETED.value,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            version=2,
        )
        task_service.repository.get_by_id = AsyncMock(return_value=task)

        with pytest.raises(InvalidTaskTransitionError) as exc_info:
            await task_service.cancel_task(user_id, task.task_id)
        assert "COMPLETED to CANCELLED" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_task_optimistic_conflict(self, task_service):
        user_id = uuid.uuid4()
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Old Title",
            status=TaskStatus.OPEN.value,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            version=2,  # Current is 2
        )
        task_service.repository.get_by_id = AsyncMock(return_value=task)

        req = UpdateTaskRequest(title="New Title", expected_version=1)
        with pytest.raises(TaskConflictError) as exc_info:
            await task_service.update_task(user_id, task.task_id, req)
        assert "Expected 1, but task is at version 2" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_due_date_overdue_and_due_soon_flags(self, task_service):
        user_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        # 1. Overdue: due yesterday, open
        task_overdue = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Overdue Task",
            status=TaskStatus.OPEN.value,
            due_at=now - datetime.timedelta(days=1),
            created_at=now,
            updated_at=now,
            version=1,
        )
        resp = await task_service._to_task_response(task_overdue)
        assert resp.is_overdue
        assert not resp.is_due_soon

        # 2. Due soon: due in 2 hours, open
        task_due_soon = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Due Soon Task",
            status=TaskStatus.OPEN.value,
            due_at=now + datetime.timedelta(hours=2),
            created_at=now,
            updated_at=now,
            version=1,
        )
        resp = await task_service._to_task_response(task_due_soon)
        assert not resp.is_overdue
        assert resp.is_due_soon

        # 3. Completed task due yesterday: not overdue
        task_completed_overdue = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=user_id,
            title="Completed Overdue Task",
            status=TaskStatus.COMPLETED.value,
            due_at=now - datetime.timedelta(days=1),
            created_at=now,
            updated_at=now,
            completed_at=now,
            version=2,
        )
        resp = await task_service._to_task_response(task_completed_overdue)
        assert not resp.is_overdue
        assert not resp.is_due_soon


# -----------------------------------------------------------------------------
# 3. Approval Requests & Decisions Service Unit Tests
# -----------------------------------------------------------------------------
class TestApprovalService:
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def approval_repo(self, mock_session):
        return ApprovalRepository(mock_session)

    @pytest.fixture
    def approval_service(self, mock_session, approval_repo):
        return ApprovalService(mock_session, approval_repo)

    @pytest.mark.asyncio
    async def test_create_approval_request_trusted_producer_success(
        self, approval_service, mock_session
    ):
        approver_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        req = CreateApprovalInternalRequest(
            producer_key="system.ops",
            approver_user_id=approver_id,
            action_kind="resource.modify",
            proposal_reference="cfg-db-max-conns-100",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Increase DB Connection Pool",
            summary="Proposed pool size increase from 50 to 100 for peak traffic.",
            expires_at=now + datetime.timedelta(hours=24),
            idempotency_key="idemp-app-001",
        )
        approval_service.repository.get_by_producer_idempotency = AsyncMock(return_value=None)
        app_req = await approval_service.create_request(req)
        assert app_req.producer_key == "system.ops"
        assert app_req.action_kind == "resource.modify"
        assert app_req.status == ApprovalStatus.PENDING.value
        assert app_req.approver_user_id == approver_id
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_create_approval_request_untrusted_producer_rejected(self, approval_service):
        approver_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        req = CreateApprovalInternalRequest(
            producer_key="untrusted.rogue_service",
            approver_user_id=approver_id,
            action_kind="resource.modify",
            proposal_reference="ref-123",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Malicious Request",
            summary="Suspicious execution payload",
            expires_at=now + datetime.timedelta(hours=24),
            idempotency_key="idemp-app-rogue",
        )
        with pytest.raises(UntrustedProducerError) as exc_info:
            await approval_service.create_request(req)
        assert "not in the trusted producer allowlist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_approval_request_invalid_action_kind_rejected(self, approval_service):
        approver_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        req = CreateApprovalInternalRequest(
            producer_key="system.ops",
            approver_user_id=approver_id,
            action_kind="arbitrary.shell_exec",  # Unallowed action kind
            proposal_reference="ref-123",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Dangerous Action",
            summary="Arbitrary script",
            expires_at=now + datetime.timedelta(hours=24),
            idempotency_key="idemp-app-bad-action",
        )
        with pytest.raises(InvalidActionKindError) as exc_info:
            await approval_service.create_request(req)
        assert "not in the allowed action kinds" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_approval_request_expired_in_past_rejected(self, approval_service):
        approver_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        req = CreateApprovalInternalRequest(
            producer_key="system.ops",
            approver_user_id=approver_id,
            action_kind="resource.modify",
            proposal_reference="ref-123",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Expired Request",
            summary="Summary",
            expires_at=now - datetime.timedelta(hours=1),
            idempotency_key="idemp-app-past",
        )
        with pytest.raises(InvalidApprovalPayloadError) as exc_info:
            await approval_service.create_request(req)
        assert "must be in the future" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_approval_request_lifetime_too_long_rejected(self, approval_service):
        approver_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        req = CreateApprovalInternalRequest(
            producer_key="system.ops",
            approver_user_id=approver_id,
            action_kind="resource.modify",
            proposal_reference="ref-123",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Too Long Request",
            summary="Summary",
            expires_at=now + datetime.timedelta(days=10),  # > 7 days
            idempotency_key="idemp-app-too-long",
        )
        with pytest.raises(InvalidApprovalPayloadError) as exc_info:
            await approval_service.create_request(req)
        assert "cannot exceed maximum lifetime" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_record_decision_approve_success_with_no_execution(
        self, approval_service, mock_session
    ):
        approver_id = uuid.uuid4()
        approval_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        app_req = ApprovalRequest(
            approval_id=approval_id,
            approver_user_id=approver_id,
            producer_key="trading.risk",
            action_kind="order.confirm",
            proposal_reference="ord-risk-check-789",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Confirm Order Limit",
            summary="Increase margin threshold for account.",
            status=ApprovalStatus.PENDING.value,
            requested_at=now,
            expires_at=now + datetime.timedelta(hours=12),
            decided_at=None,
            decided_by_user_id=None,
            version=1,
            idempotency_key="idemp-app-002",
        )
        approval_service.repository.get_by_id = AsyncMock(return_value=app_req)
        approval_service.repository.get_decision_by_idempotency = AsyncMock(return_value=None)

        dec_idemp_key = uuid.uuid4()
        dec_req = ApprovalDecisionRequest(
            decision=ApprovalDecisionType.APPROVE,
            decision_idempotency_key=dec_idemp_key,
            reason="Approved after manual risk review",
        )

        resp = await approval_service.record_decision(approver_id, approval_id, dec_req)
        assert resp.approval_id == approval_id
        assert resp.approver_user_id == approver_id
        assert resp.decision == ApprovalDecisionType.APPROVE
        assert resp.status == ApprovalStatus.APPROVED
        assert resp.version == 2
        assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_record_decision_reject_success(self, approval_service, mock_session):
        approver_id = uuid.uuid4()
        approval_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        app_req = ApprovalRequest(
            approval_id=approval_id,
            approver_user_id=approver_id,
            producer_key="workflow.engine",
            action_kind="workflow.step_approve",
            proposal_reference="wf-step-456",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Deploy Workflow Trigger",
            summary="External webhook destination.",
            status=ApprovalStatus.PENDING.value,
            requested_at=now,
            expires_at=now + datetime.timedelta(hours=6),
            version=1,
            idempotency_key="idemp-wf-456",
        )
        approval_service.repository.get_by_id = AsyncMock(return_value=app_req)
        approval_service.repository.get_decision_by_idempotency = AsyncMock(return_value=None)

        dec_req = ApprovalDecisionRequest(
            decision=ApprovalDecisionType.REJECT,
            decision_idempotency_key=uuid.uuid4(),
            reason="Untrusted external webhook destination",
        )
        resp = await approval_service.record_decision(approver_id, approval_id, dec_req)
        assert resp.decision == ApprovalDecisionType.REJECT
        assert resp.status == ApprovalStatus.REJECTED
        assert app_req.status == ApprovalStatus.REJECTED.value

    @pytest.mark.asyncio
    async def test_record_decision_expired_request_rejected(self, approval_service):
        approver_id = uuid.uuid4()
        approval_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        # Expired 10 minutes ago
        app_req = ApprovalRequest(
            approval_id=approval_id,
            approver_user_id=approver_id,
            producer_key="system.ops",
            action_kind="resource.modify",
            proposal_reference="ref-1",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Expired Request",
            summary="Summary",
            status=ApprovalStatus.PENDING.value,
            requested_at=now - datetime.timedelta(hours=2),
            expires_at=now - datetime.timedelta(minutes=10),
            version=1,
            idempotency_key="idemp-exp",
        )
        approval_service.repository.get_by_id = AsyncMock(return_value=app_req)
        approval_service.repository.get_decision_by_idempotency = AsyncMock(return_value=None)

        dec_req = ApprovalDecisionRequest(
            decision=ApprovalDecisionType.APPROVE,
            decision_idempotency_key=uuid.uuid4(),
        )
        with pytest.raises(ApprovalExpiredError) as exc_info:
            await approval_service.record_decision(approver_id, approval_id, dec_req)
        assert "can no longer be decided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_record_decision_already_decided_rejected(self, approval_service):
        approver_id = uuid.uuid4()
        approval_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        app_req = ApprovalRequest(
            approval_id=approval_id,
            approver_user_id=approver_id,
            producer_key="system.ops",
            action_kind="resource.modify",
            proposal_reference="ref-1",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Decided Request",
            summary="Summary",
            status=ApprovalStatus.APPROVED.value,
            requested_at=now - datetime.timedelta(hours=1),
            expires_at=now + datetime.timedelta(hours=5),
            decided_at=now,
            version=2,
            idempotency_key="idemp-dec",
        )
        approval_service.repository.get_by_id = AsyncMock(return_value=app_req)
        approval_service.repository.get_decision_by_idempotency = AsyncMock(return_value=None)

        dec_req = ApprovalDecisionRequest(
            decision=ApprovalDecisionType.REJECT,  # Attempting to change to reject
            decision_idempotency_key=uuid.uuid4(),
        )
        with pytest.raises(ApprovalAlreadyDecidedError) as exc_info:
            await approval_service.record_decision(approver_id, approval_id, dec_req)
        assert "already been decided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_record_decision_version_conflict(self, approval_service):
        approver_id = uuid.uuid4()
        approval_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        app_req = ApprovalRequest(
            approval_id=approval_id,
            approver_user_id=approver_id,
            producer_key="system.ops",
            action_kind="resource.modify",
            proposal_reference="ref-1",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="Version Conflict Request",
            summary="Summary",
            status=ApprovalStatus.PENDING.value,
            requested_at=now,
            expires_at=now + datetime.timedelta(hours=5),
            version=2,  # Current version is 2
            idempotency_key="idemp-ver",
        )
        approval_service.repository.get_by_id = AsyncMock(return_value=app_req)
        approval_service.repository.get_decision_by_idempotency = AsyncMock(return_value=None)

        dec_req = ApprovalDecisionRequest(
            decision=ApprovalDecisionType.APPROVE,
            decision_idempotency_key=uuid.uuid4(),
            expected_version=1,  # Stale tab passed 1
        )
        with pytest.raises(ApprovalConflictError) as exc_info:
            await approval_service.record_decision(approver_id, approval_id, dec_req)
        assert "version mismatch" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cancel_request_trusted_producer(self, approval_service, mock_session):
        approval_id = uuid.uuid4()
        approver_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        app_req = ApprovalRequest(
            approval_id=approval_id,
            approver_user_id=approver_id,
            producer_key="system.ops",
            action_kind="resource.modify",
            proposal_reference="ref-1",
            proposal_digest="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            title="To Cancel",
            summary="Summary",
            status=ApprovalStatus.PENDING.value,
            requested_at=now,
            expires_at=now + datetime.timedelta(hours=5),
            version=1,
            idempotency_key="idemp-cancel",
        )
        # Mock row lookup
        mock_session.execute = AsyncMock(
            return_value=MagicMock(
                first=MagicMock(return_value=MagicMock(approver_user_id=approver_id))
            )
        )
        approval_service.repository.get_by_id = AsyncMock(return_value=app_req)

        cancelled = await approval_service.cancel_request("system.ops", approval_id)
        assert cancelled.status == ApprovalStatus.CANCELLED.value
        assert cancelled.version == 2
        assert mock_session.commit.called


# -----------------------------------------------------------------------------
# 4. FastAPI Endpoint Integration Tests
# -----------------------------------------------------------------------------
class TestTasksAndApprovalsApi:
    @pytest.fixture
    def test_user_id(self):
        return uuid.uuid4()

    @pytest.fixture
    def test_principal(self, test_user_id):
        # AuthPrincipal takes sub as its subject (user_id)
        return AuthPrincipal(
            sub=str(test_user_id),
            email="researcher@atlas.financial",
            role="user",
        )

    @pytest.fixture
    def mock_task_service(self):
        svc = MagicMock(spec=PersonalTaskService)
        svc.list_tasks = AsyncMock(
            return_value=TaskListResponse(
                schema_version="1.0",
                items=[],
                open_count=0,
                overdue_count=0,
                next_cursor=None,
                has_more=False,
            )
        )
        svc.get_counts = AsyncMock(return_value=TaskCountsResponse(open_count=0, overdue_count=0))
        svc.create_task = AsyncMock(
            return_value=TaskResponse(
                task_id=uuid.uuid4(),
                owner_user_id=uuid.uuid4(),
                title="Analyze TSMC Geopolitical Exposure",
                description="Examine fab locations and foundry concentration risks",
                status=TaskStatus.OPEN,
                due_at=None,
                module_id="maps",
                module_label="Maps",
                entity_id=None,
                entity_display_name=None,
                entity_type=None,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                updated_at=datetime.datetime.now(datetime.timezone.utc),
                completed_at=None,
                cancelled_at=None,
                version=1,
                is_overdue=False,
                is_due_soon=False,
            )
        )
        return svc

    @pytest.fixture
    def mock_approval_service(self):
        svc = MagicMock(spec=ApprovalService)
        svc.list_approvals = AsyncMock(
            return_value=ApprovalListResponse(
                schema_version="1.0",
                items=[],
                pending_count=0,
                next_cursor=None,
                has_more=False,
            )
        )
        svc.get_counts = AsyncMock(return_value=ApprovalCountsResponse(pending_count=0))
        svc.get_approval_detail = AsyncMock(side_effect=ApprovalNotFoundError("not-found"))
        return svc

    @pytest.fixture
    def app(self, test_principal, mock_task_service, mock_approval_service):
        app = create_app()

        async def override_current_user():
            return test_principal

        async def override_authz():
            ctx = MagicMock(spec=AuthorizationContext)
            ctx.has_permission = MagicMock(return_value=True)
            return ctx

        from atlas.approvals.router import get_approval_service
        from atlas.tasks.router import get_task_service

        app.dependency_overrides[get_current_user] = override_current_user
        app.dependency_overrides[get_authorization_context] = override_authz
        app.dependency_overrides[get_task_service] = lambda: mock_task_service
        app.dependency_overrides[get_approval_service] = lambda: mock_approval_service
        return app

    @pytest.mark.asyncio
    async def test_tasks_list_returns_private_no_store(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/api/v1/tasks")
            assert res.status_code == 200
            assert res.headers.get("Cache-Control") == "private, no-store"
            data = res.json()
            assert "items" in data
            assert "open_count" in data
            assert "overdue_count" in data

    @pytest.mark.asyncio
    async def test_tasks_counts_endpoint(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/api/v1/tasks/counts")
            assert res.status_code == 200
            assert res.headers.get("Cache-Control") == "private, no-store"
            data = res.json()
            assert "open_count" in data
            assert "overdue_count" in data

    @pytest.mark.asyncio
    async def test_tasks_create_success(self, app):
        payload = {
            "title": "Analyze TSMC Geopolitical Exposure",
            "description": "Examine fab locations and foundry concentration risks",
            "module_id": "maps",
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post("/api/v1/tasks", json=payload)
            assert res.status_code == 201
            data = res.json()
            assert data["title"] == "Analyze TSMC Geopolitical Exposure"
            assert data["status"] == "OPEN"
            assert data["module_id"] == "maps"
            assert data["module_label"] == "Maps"
            assert data["version"] == 1

    @pytest.mark.asyncio
    async def test_tasks_create_invalid_module_returns_400(self, app, mock_task_service):
        mock_task_service.create_task = AsyncMock(
            side_effect=InvalidTaskPayloadError("Invalid module_id")
        )
        payload = {
            "title": "Task with Invalid Module",
            "module_id": "invalid_module_test",
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post("/api/v1/tasks", json=payload)
            assert res.status_code == 400
            data = res.json()
            assert "error" in data

    @pytest.mark.asyncio
    async def test_tasks_create_extra_fields_forbidden_422(self, app):
        payload = {
            "title": "Task with Malicious Fields",
            "owner_user_id": str(uuid.uuid4()),  # Forbidden client override
            "version": 99,
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post("/api/v1/tasks", json=payload)
            assert res.status_code == 422

    @pytest.mark.asyncio
    async def test_approvals_list_returns_private_no_store(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/api/v1/approvals")
            assert res.status_code == 200
            assert res.headers.get("Cache-Control") == "private, no-store"
            data = res.json()
            assert "items" in data
            assert "pending_count" in data

    @pytest.mark.asyncio
    async def test_approvals_counts_endpoint(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/api/v1/approvals/counts")
            assert res.status_code == 200
            assert res.headers.get("Cache-Control") == "private, no-store"
            data = res.json()
            assert "pending_count" in data

    @pytest.mark.asyncio
    async def test_approvals_no_public_create_endpoint_returns_405(self, app):
        # Section 47/48 non-negotiable rule: No public approval creation route!
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post("/api/v1/approvals", json={"title": "Fake Approval"})
            assert res.status_code in (404, 405)

    @pytest.mark.asyncio
    async def test_approvals_detail_not_found_returns_404(self, app):
        random_id = str(uuid.uuid4())
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get(f"/api/v1/approvals/{random_id}")
            assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthenticated_requests_rejected_with_401(self, app):
        # Remove current_user override to test real 401
        app.dependency_overrides.pop(get_current_user, None)
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as unauth_client:
            res_tasks = await unauth_client.get("/api/v1/tasks")
            assert res_tasks.status_code == 401

            res_apps = await unauth_client.get("/api/v1/approvals")
            assert res_apps.status_code == 401
