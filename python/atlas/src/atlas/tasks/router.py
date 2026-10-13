"""FastAPI router for ATLAS Personal Tasks (Stage 54)."""

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

from .enums import TaskStatusFilter
from .errors import (
    InvalidTaskPayloadError,
    InvalidTaskTransitionError,
    TaskConflictError,
    TaskIdempotencyConflictError,
    TaskNotFoundError,
)
from .models import (
    CreateTaskRequest,
    TaskCountsResponse,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)
from .repository import TaskRepository
from .service import PersonalTaskService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Personal Tasks"])


def get_task_service(
    session: AsyncSession = Depends(get_db_session),
) -> PersonalTaskService:
    """Dependency factory for PersonalTaskService."""
    repo = TaskRepository(session)
    return PersonalTaskService(session=session, repository=repo)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List personal tasks",
    description="List tasks for the authenticated user using keyset pagination.",
)
async def list_tasks(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[PersonalTaskService, Depends(get_task_service)],
    status_filter: TaskStatusFilter = Query(TaskStatusFilter.OPEN, alias="status"),
    limit: int = Query(10, ge=1, le=50),
    cursor: Optional[str] = Query(None),
) -> TaskListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.list_tasks(
            owner_user_id=uuid.UUID(principal.user_id),
            status_filter=status_filter,
            limit=limit,
            cursor=cursor,
        )
    except InvalidTaskPayloadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/counts",
    response_model=TaskCountsResponse,
    summary="Get task counts",
    description="Retrieve authoritative open and overdue task counts.",
)
async def get_task_counts(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[PersonalTaskService, Depends(get_task_service)],
) -> TaskCountsResponse:
    response.headers["Cache-Control"] = "private, no-store"
    return await service.get_counts(owner_user_id=uuid.UUID(principal.user_id))


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a personal task",
    description="Creates a new personal task belonging to the authenticated user.",
)
async def create_task(
    request: CreateTaskRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[PersonalTaskService, Depends(get_task_service)],
) -> TaskResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.create_task(
            owner_user_id=uuid.UUID(principal.user_id),
            request=request,
        )
    except TaskIdempotencyConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except InvalidTaskPayloadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a personal task",
    description="Update mutable fields with optimistic concurrency locking.",
)
async def update_task(
    task_id: uuid.UUID,
    request: UpdateTaskRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[PersonalTaskService, Depends(get_task_service)],
) -> TaskResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.update_task(
            owner_user_id=uuid.UUID(principal.user_id),
            task_id=task_id,
            request=request,
        )
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except TaskConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except InvalidTaskPayloadError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Complete a task",
    description="Mark an open task as completed.",
)
async def complete_task(
    task_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[PersonalTaskService, Depends(get_task_service)],
) -> TaskResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.complete_task(
            owner_user_id=uuid.UUID(principal.user_id),
            task_id=task_id,
        )
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidTaskTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/{task_id}/reopen",
    response_model=TaskResponse,
    summary="Reopen a task",
    description="Reopen a completed task back to open.",
)
async def reopen_task(
    task_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[PersonalTaskService, Depends(get_task_service)],
) -> TaskResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.reopen_task(
            owner_user_id=uuid.UUID(principal.user_id),
            task_id=task_id,
        )
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidTaskTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/{task_id}/cancel",
    response_model=TaskResponse,
    summary="Cancel a task",
    description="Cancel an open task.",
)
async def cancel_task(
    task_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _authz: Annotated[None, Depends(RequirePermission(PermissionCode.ATLAS_ACCESS))],
    service: Annotated[PersonalTaskService, Depends(get_task_service)],
) -> TaskResponse:
    response.headers["Cache-Control"] = "private, no-store"
    try:
        return await service.cancel_task(
            owner_user_id=uuid.UUID(principal.user_id),
            task_id=task_id,
        )
    except TaskNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidTaskTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
