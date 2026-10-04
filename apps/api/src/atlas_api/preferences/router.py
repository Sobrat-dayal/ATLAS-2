import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from atlas.auth import AuthPrincipal
from atlas.authorization import PermissionCode
from atlas.preferences import UserPreferenceService

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission
from .dependencies import get_preference_service
from .schemas import (
    PreferenceResponse,
    PreferenceListResponse,
    PreferenceUpdateRequest
)

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("", response_model=PreferenceListResponse)
async def list_preferences(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserPreferenceService, Depends(get_preference_service)],
    _: None = Depends(RequirePermission(PermissionCode.SETTINGS_READ))
):
    """
    List all account-synced preferences for the current authenticated user.
    """
    response.headers["Cache-Control"] = "private, no-store"
    user_id = uuid.UUID(principal.user_id)
    prefs = await service.list_preferences(user_id)
    return PreferenceListResponse(preferences=prefs)


@router.get("/{preference_key}", response_model=PreferenceResponse)
async def get_preference(
    preference_key: str,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserPreferenceService, Depends(get_preference_service)],
    _: None = Depends(RequirePermission(PermissionCode.SETTINGS_READ))
):
    """
    Get a specific preference namespace for the current user.
    """
    response.headers["Cache-Control"] = "private, no-store"
    user_id = uuid.UUID(principal.user_id)
    pref = await service.get_preference(user_id, preference_key)
    return pref


@router.put("/{preference_key}", response_model=PreferenceResponse)
async def update_preference(
    preference_key: str,
    request: PreferenceUpdateRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserPreferenceService, Depends(get_preference_service)],
    _: None = Depends(RequirePermission(PermissionCode.SETTINGS_WRITE_SELF))
):
    """
    Create or update a preference namespace for the current user.
    Uses optimistic concurrency with `expected_revision`.
    """
    user_id = uuid.UUID(principal.user_id)
    pref = await service.set_preference(
        user_id=user_id,
        key=preference_key,
        schema_version=request.schema_version,
        payload=request.payload,
        expected_revision=request.expected_revision
    )
    return pref


@router.delete("/{preference_key}", status_code=204)
async def delete_preference(
    preference_key: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserPreferenceService, Depends(get_preference_service)],
    _: None = Depends(RequirePermission(PermissionCode.SETTINGS_WRITE_SELF))
):
    """
    Delete a specific preference namespace, causing it to revert to ATLAS defaults.
    """
    user_id = uuid.UUID(principal.user_id)
    await service.delete_preference(user_id, preference_key)


@router.delete("", status_code=204)
async def reset_all_preferences(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[UserPreferenceService, Depends(get_preference_service)],
    _: None = Depends(RequirePermission(PermissionCode.SETTINGS_WRITE_SELF))
):
    """
    Delete all account-synced preferences for the current user, reverting everything to defaults.
    """
    user_id = uuid.UUID(principal.user_id)
    await service.reset_all_preferences(user_id)
