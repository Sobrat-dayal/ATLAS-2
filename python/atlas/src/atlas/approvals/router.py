"""FastAPI router for ATLAS Approval Inbox and Decision Architecture (Stage 54)."""

import logging
import uuid
from typing import Annotated, Optional

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode

from .enums import ApprovalStatusFilter
from .errors import (
    ApprovalAlreadyDecidedError,
    ApprovalConflictError,
    ApprovalExpiredError,
    ApprovalIdempotencyConflictError,
    ApprovalNotFoundError,
    InvalidApprovalPayloadError,
)
from .models import (
    ApprovalCountsResponse,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalDetailResponse,
    ApprovalListResponse,
)
from .repository import ApprovalRepository
from .service import ApprovalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/approvals", tags=["Approval Inbox"])


def get_approval_service(
    session: AsyncSession = Depends(get_db_session),
) -> ApprovalService:
    """Dependency factory for ApprovalService."""
    repo = ApprovalRepository(session)
    return ApprovalService(session=session, repository=repo)


@router.get(
    "",
    response_model=ApprovalListResponse,
    summary="List approval requests",
    description="List approval requests assigned to user using keyset pagination.",
)
async def list_approvals(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[ApprovalService, Depends(get_approval_service)],
    status_filter: ApprovalStatusFilter = Query(ApprovalStatusFilter.PENDING, alias="status"),
    limit: int = Query(10, ge=1, le=50),
    cursor: Optional[str] = Query(None),
) -> ApprovalListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.list_approvals(
            approver_user_id=uuid.UUID(principal.user_id),
            status_filter=status_filter,
            limit=limit,
            cursor=cursor,
        )
    except InvalidApprovalPayloadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/counts",
    response_model=ApprovalCountsResponse,
    summary="Get pending approval count",
    description="Retrieve authoritative count of active pending approval requests.",
)
async def get_approval_counts(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[ApprovalService, Depends(get_approval_service)],
) -> ApprovalCountsResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_counts(approver_user_id=uuid.UUID(principal.user_id))


@router.get(
    "/{approval_id}",
    response_model=ApprovalDetailResponse,
    summary="Get approval request details",
    description="Inspect full proposal context, digest, and status before rendering a decision.",
)
async def get_approval_detail(
    approval_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[ApprovalService, Depends(get_approval_service)],
) -> ApprovalDetailResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.get_approval_detail(
            approver_user_id=uuid.UUID(principal.user_id),
            approval_id=approval_id,
        )
    except ApprovalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{approval_id}/decision",
    response_model=ApprovalDecisionResponse,
    summary="Record human approval decision",
    description="Atomically record APPROVE/REJECT decision. Does not execute the action.",
)
async def record_decision(
    approval_id: uuid.UUID,
    request: ApprovalDecisionRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[ApprovalService, Depends(get_approval_service)],
) -> ApprovalDecisionResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.record_decision(
            approver_user_id=uuid.UUID(principal.user_id),
            approval_id=approval_id,
            request=request,
        )
    except ApprovalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ApprovalExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(exc),
        ) from exc
    except ApprovalAlreadyDecidedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ApprovalConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ApprovalIdempotencyConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
