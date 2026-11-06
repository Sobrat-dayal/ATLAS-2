"""Stage 148 Operations, Workforce Monitoring, and Approvals API."""

from __future__ import annotations

from typing import Annotated, Any

from atlas.agents.errors import ApprovalExpiredError, ApprovalNotFoundError
from atlas.agents.operations import OperationsService
from atlas.agents.tasks import ApprovalRequest, TaskService
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.agent_departments import get_department_service
from atlas_api.routers.agent_tasks import get_task_service
from atlas_api.routers.agent_teams import get_team_service

router = APIRouter(prefix="/agents", tags=["Agent Operations & Governance"])
_operations_service: OperationsService | None = None


def get_operations_service() -> OperationsService:
    global _operations_service
    if _operations_service is None:
        _operations_service = OperationsService(
            get_department_service(),
            get_team_service(),
            get_task_service(),
        )
    return _operations_service


class ApprovalResolveRequest(BaseModel):
    decision: str = Field(description="'APPROVED' or 'REJECTED'")
    reason: str | None = None


class ApprovalResponse(BaseModel):
    approval_id: str
    task_id: str
    action_type: str
    action_payload: dict[str, Any]
    status: str
    requested_at: str
    expires_at: str
    decided_at: str | None
    decided_by: str | None
    reason: str | None


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    return str(principal.raw_claims.get("tenant_id", principal.sub)), principal.sub


def _appr_response(a: ApprovalRequest) -> ApprovalResponse:
    return ApprovalResponse(
        approval_id=a.approval_id,
        task_id=a.task_id,
        action_type=a.action_type,
        action_payload=a.action_payload,
        status=a.status.value,
        requested_at=a.requested_at.isoformat(),
        expires_at=a.expires_at.isoformat(),
        decided_at=a.decided_at.isoformat() if a.decided_at else None,
        decided_by=a.decided_by,
        reason=a.reason,
    )


@router.get("/operations/overview", response_model=dict[str, Any])
def get_operations_overview(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[OperationsService, Depends(get_operations_service)],
) -> dict[str, Any]:
    tenant_id, owner_id = _identity(current_user)
    return service.get_overview(tenant_id=tenant_id, owner_id=owner_id)


@router.get("/operations/health", response_model=dict[str, Any])
def get_operations_health(
    service: Annotated[OperationsService, Depends(get_operations_service)],
) -> dict[str, Any]:
    return service.get_health()


@router.get("/operations/usage", response_model=dict[str, Any])
def get_operations_usage(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[OperationsService, Depends(get_operations_service)],
) -> dict[str, Any]:
    tenant_id, owner_id = _identity(current_user)
    return service.get_usage(tenant_id=tenant_id, owner_id=owner_id)


@router.get("/approvals", response_model=list[ApprovalResponse])
def list_approvals(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> list[ApprovalResponse]:
    tenant_id, _ = _identity(current_user)
    return [_appr_response(a) for a in task_service.list_approvals(tenant_id=tenant_id)]


@router.post("/approvals/{approval_id}/resolve", response_model=ApprovalResponse)
def resolve_approval(
    approval_id: str,
    request: ApprovalResolveRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
) -> ApprovalResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        resolved = task_service.resolve_approval(
            approval_id=approval_id,
            decision=request.decision,
            decided_by=owner_id,
            tenant_id=tenant_id,
            reason=request.reason,
        )
        return _appr_response(resolved)
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Approval request not found") from exc
    except ApprovalExpiredError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
