import logging
import uuid
from typing import Annotated, List

from atlas.auth import AuthPrincipal
from atlas.authorization import AuthorizationContext, AuthorizationService, PermissionCode
from fastapi import APIRouter, Depends, Response

from atlas_api.auth.dependencies import get_current_user

from .dependencies import RequirePermission, get_authorization_context, get_authorization_service
from .schemas import (
    AuthorizationMeResponse,
    PermissionResponse,
    RoleResponse,
    UserRolesResponse,
)

logger = logging.getLogger("atlas.api.authz")

router = APIRouter(prefix="/authz", tags=["Authorization"])


@router.get("/me", response_model=AuthorizationMeResponse)
async def get_me(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
):
    """
    Return the authenticated user's current effective roles and permissions.
    """
    response.headers["Cache-Control"] = "no-store"
    return AuthorizationMeResponse(
        user_id=uuid.UUID(principal.user_id),
        roles=sorted(list(context.roles)),
        permissions=sorted(list(context.permissions)),
    )


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    _: None = Depends(RequirePermission(PermissionCode.AUTHZ_READ)),
    service: AuthorizationService = Depends(get_authorization_service),
):
    """List all available roles in the system."""
    roles = await service.repository.list_roles()
    return roles


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    _: None = Depends(RequirePermission(PermissionCode.AUTHZ_READ)),
    service: AuthorizationService = Depends(get_authorization_service),
):
    """List all available permissions in the system."""
    permissions = await service.repository.list_permissions()
    return permissions


@router.get("/users/{user_id}/roles", response_model=UserRolesResponse)
async def get_user_roles(
    user_id: uuid.UUID,
    _: None = Depends(RequirePermission(PermissionCode.AUTHZ_READ)),
    service: AuthorizationService = Depends(get_authorization_service),
):
    """Get the roles for a specific user."""
    explicit_roles_models = await service.repository.get_explicit_user_roles(user_id)
    explicit_roles = [r.key for r in explicit_roles_models]
    implicit_roles = [service.default_role]
    effective_roles = list(set(explicit_roles + implicit_roles))

    return UserRolesResponse(
        implicit_roles=implicit_roles,
        explicit_roles=sorted(explicit_roles),
        effective_roles=sorted(effective_roles),
    )


@router.put("/users/{user_id}/roles/{role_key}", status_code=204)
async def grant_user_role(
    user_id: uuid.UUID,
    role_key: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _: None = Depends(RequirePermission(PermissionCode.AUTHZ_MANAGE)),
    service: AuthorizationService = Depends(get_authorization_service),
):
    """Grant a role to a user."""
    granted = await service.repository.grant_role(
        user_id=user_id, role_key=role_key, assigned_by_user_id=principal.user_id
    )

    # Audit log
    logger.info(
        "authorization.role_granted",
        extra={
            "actor_user_id": principal.user_id,
            "target_user_id": str(user_id),
            "role_key": role_key,
            "result": "granted" if granted else "already_assigned",
        },
    )


@router.delete("/users/{user_id}/roles/{role_key}", status_code=204)
async def revoke_user_role(
    user_id: uuid.UUID,
    role_key: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    _: None = Depends(RequirePermission(PermissionCode.AUTHZ_MANAGE)),
    service: AuthorizationService = Depends(get_authorization_service),
):
    """Revoke a role from a user."""
    from fastapi import HTTPException

    if role_key == service.default_role:
        raise HTTPException(
            status_code=400, detail=f"Cannot revoke implicit default role '{service.default_role}'"
        )

    revoked = await service.repository.revoke_role(user_id=user_id, role_key=role_key)

    # Audit log
    logger.info(
        "authorization.role_revoked",
        extra={
            "actor_user_id": principal.user_id,
            "target_user_id": str(user_id),
            "role_key": role_key,
            "result": "revoked" if revoked else "not_assigned",
        },
    )
