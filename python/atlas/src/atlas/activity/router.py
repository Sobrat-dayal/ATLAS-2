"""FastAPI router for ATLAS Home Personalized Activity (Stage 53)."""

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
from atlas.preferences import UserPreferenceRepository, UserPreferenceService

from .canonical_modules import CANONICAL_MODULES
from .enums import ActivityEventType
from .errors import (
    ActivityHistoryDisabledError,
    IdempotencyConflictError,
    InvalidCursorError,
    InvalidEntityError,
    InvalidModuleIdError,
    ModuleAccessDeniedError,
)
from .models import (
    ActivityConsentRequest,
    ActivityConsentResponse,
    ClearActivityResponse,
    RecordActivityEventRequest,
    UserActivityItem,
    UserActivityListResponse,
)
from .repository import UserActivityRepository
from .service import UserActivityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/home/activity", tags=["Home Personalized Activity"])


def get_activity_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserActivityService:
    """Dependency factory for UserActivityService."""
    act_repo = UserActivityRepository(session)
    pref_repo = UserPreferenceRepository(session)
    pref_service = UserPreferenceService(pref_repo)
    return UserActivityService(
        session=session,
        repository=act_repo,
        preference_service=pref_service,
    )


@router.get(
    "",
    response_model=UserActivityListResponse,
    summary="List recent user activity",
    description=(
        "Returns recent activity events for the authenticated user using keyset pagination."
    ),
)
async def list_user_activity(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserActivityService, Depends(get_activity_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
    limit: Annotated[int, Query(ge=1, le=50, description="Page limit (default 10, max 50)")] = 10,
    cursor: Annotated[Optional[str], Query(description="Opaque keyset pagination cursor")] = None,
) -> UserActivityListResponse:
    """Reads authenticated user activity with private caching headers."""
    response.headers["Cache-Control"] = "private, no-store"
    user_id = principal.user_id or uuid.UUID(str(principal.sub))
    try:
        return await service.list_activity(user_id=user_id, limit=limit, cursor=cursor)
    except InvalidCursorError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/events",
    response_model=UserActivityItem,
    status_code=status.HTTP_201_CREATED,
    summary="Record an explicit user activity event",
    description="Captures an explicit module navigation or entity selection action.",
)
async def record_user_activity(
    request: RecordActivityEventRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserActivityService, Depends(get_activity_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UserActivityItem:
    """Best-effort capture of explicit user interactions."""
    user_id = principal.user_id or uuid.UUID(str(principal.sub))
    try:
        event = await service.record_event(user_id=user_id, request=request)
    except ActivityHistoryDisabledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ACTIVITY_HISTORY_DISABLED",
        ) from exc
    except IdempotencyConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except (InvalidModuleIdError, InvalidEntityError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ModuleAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    # Map created event to UserActivityItem
    event_type = ActivityEventType(event.event_type)
    if event_type == ActivityEventType.MODULE_OPENED:
        mod_info = CANONICAL_MODULES.get(event.module_id or "")
        label = mod_info.label if mod_info else event.module_id
        route = mod_info.route if mod_info else f"/{event.module_id}"
        return UserActivityItem(
            activity_id=event.activity_id,
            event_type=event_type,
            module_id=event.module_id,
            module_label=label,
            entity_id=None,
            entity_display_name=None,
            entity_type=None,
            occurred_at=event.occurred_at,
            resume_target=route,
            is_accessible=True,
        )
    else:
        return UserActivityItem(
            activity_id=event.activity_id,
            event_type=event_type,
            module_id=None,
            module_label=None,
            entity_id=event.entity_id,
            entity_display_name="Selected Entity",
            entity_type="entity",
            occurred_at=event.occurred_at,
            resume_target=f"/entities/{event.entity_id}",
            is_accessible=True,
        )


@router.put(
    "/consent",
    response_model=ActivityConsentResponse,
    summary="Update activity history recording consent",
    description=(
        "Enables or disables activity history recording. Disabling transactionally purges history."
    ),
)
async def update_activity_consent(
    request: ActivityConsentRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserActivityService, Depends(get_activity_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> ActivityConsentResponse:
    """Updates authoritative Stage 15 consent preference."""
    user_id = principal.user_id or uuid.UUID(str(principal.sub))
    return await service.set_consent(user_id=user_id, enabled=request.enabled)


@router.delete(
    "",
    response_model=ClearActivityResponse,
    summary="Clear recorded activity history",
    description=(
        "Securely deletes all Stage 53 activity records belonging to the authenticated user."
    ),
)
async def clear_activity_history(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserActivityService, Depends(get_activity_service)],
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> ClearActivityResponse:
    """User-scoped deletion of activity records."""
    user_id = principal.user_id or uuid.UUID(str(principal.sub))
    return await service.clear_history(user_id=user_id)
