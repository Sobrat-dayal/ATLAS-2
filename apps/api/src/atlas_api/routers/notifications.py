"""FastAPI router for ATLAS persistent notifications."""

import logging
import time
import uuid
from typing import Annotated

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.notifications import (
    MarkAllReadResponse,
    NotificationListFilter,
    NotificationListResponse,
    NotificationResponse,
    NotificationService,
    UnreadCountResponse,
)
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_notification_service(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    return NotificationService(session)


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List persistent notifications for authenticated user",
    description="Deterministic keyset-paginated list of user notifications, filtered by state.",
)
async def list_notifications(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    filter: NotificationListFilter = Query(default=NotificationListFilter.ALL),
    limit: int = Query(default=25, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> NotificationListResponse:
    start_time = time.perf_counter()
    response.headers["Cache-Control"] = "private, no-store"

    user_id = uuid.UUID(principal.user_id)
    result = await service.list_notifications(
        recipient_user_id=user_id,
        filter_mode=filter,
        limit=limit,
        cursor=cursor,
    )

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "notification_list_retrieved",
        extra={
            "component": "notifications",
            "operation": "list",
            "filter": filter.value,
            "limit": limit,
            "count": len(result.items),
            "has_more": result.has_more,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return result


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    summary="Get unread notification count",
    description=(
        "Lightweight endpoint returning total unread, non-archived notifications for current user."
    ),
)
async def get_unread_count(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UnreadCountResponse:
    start_time = time.perf_counter()
    response.headers["Cache-Control"] = "private, no-store"

    user_id = uuid.UUID(principal.user_id)
    count = await service.get_unread_count(recipient_user_id=user_id)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "notification_unread_count_retrieved",
        extra={
            "component": "notifications",
            "operation": "unread_count",
            "duration_ms": round(duration_ms, 2),
        },
    )
    return UnreadCountResponse(unread_count=count)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
    description="Idempotently sets read_at timestamp for a notification owned by the current user.",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> NotificationResponse:
    start_time = time.perf_counter()
    response.headers["Cache-Control"] = "private, no-store"

    user_id = uuid.UUID(principal.user_id)
    result = await service.mark_read(
        notification_id=notification_id,
        recipient_user_id=user_id,
    )

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "notification_marked_read",
        extra={
            "component": "notifications",
            "operation": "mark_read",
            "notification_id": str(notification_id),
            "duration_ms": round(duration_ms, 2),
        },
    )
    return result


@router.post(
    "/{notification_id}/unread",
    response_model=NotificationResponse,
    summary="Mark notification as unread",
    description="Sets read_at to NULL for a non-archived notification owned by the current user.",
)
async def mark_notification_unread(
    notification_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> NotificationResponse:
    start_time = time.perf_counter()
    response.headers["Cache-Control"] = "private, no-store"

    user_id = uuid.UUID(principal.user_id)
    result = await service.mark_as_unread(
        notification_id=notification_id,
        recipient_user_id=user_id,
    )

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "notification_marked_unread",
        extra={
            "component": "notifications",
            "operation": "mark_unread",
            "notification_id": str(notification_id),
            "duration_ms": round(duration_ms, 2),
        },
    )
    return result


@router.post(
    "/read-all",
    response_model=MarkAllReadResponse,
    summary="Mark all visible notifications as read",
    description="Marks all unread, non-archived notifications owned by current user as read.",
)
async def mark_all_notifications_read(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> MarkAllReadResponse:
    start_time = time.perf_counter()
    response.headers["Cache-Control"] = "private, no-store"

    user_id = uuid.UUID(principal.user_id)
    updated_count = await service.mark_all_read(recipient_user_id=user_id)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "notification_mark_all_read_completed",
        extra={
            "component": "notifications",
            "operation": "mark_all_read",
            "updated_count": updated_count,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return MarkAllReadResponse(updated_count=updated_count)


@router.post(
    "/{notification_id}/archive",
    response_model=NotificationResponse,
    summary="Archive notification",
    description=(
        "Idempotently sets archived_at (and read_at if not already read) "
        "for current user's notification."
    ),
)
async def archive_notification(
    notification_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> NotificationResponse:
    start_time = time.perf_counter()
    response.headers["Cache-Control"] = "private, no-store"

    user_id = uuid.UUID(principal.user_id)
    result = await service.archive(
        notification_id=notification_id,
        recipient_user_id=user_id,
    )

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "notification_archived",
        extra={
            "component": "notifications",
            "operation": "archive",
            "notification_id": str(notification_id),
            "duration_ms": round(duration_ms, 2),
        },
    )
    return result
