from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.authorization import (
    AuthorizationRepository,
    AuthorizationService,
    PermissionCode,
    AuthorizationContext
)
from atlas.authorization.errors import PermissionDeniedError

from atlas_api.dependencies import get_db_session
from atlas_api.auth.dependencies import get_current_user


def get_authorization_service(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> AuthorizationService:
    repository = AuthorizationRepository(session)
    return AuthorizationService(repository)


async def get_authorization_context(
    request: Request,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AuthorizationService, Depends(get_authorization_service)]
) -> AuthorizationContext:
    if hasattr(request.state, "authz_context"):
        return request.state.authz_context

    context = await service.get_authorization_context(principal)
    request.state.authz_context = context
    return context


class RequirePermission:
    def __init__(self, permission: PermissionCode | str):
        self.permission = permission if isinstance(permission, str) else permission.value

    async def __call__(
        self,
        context: Annotated[AuthorizationContext, Depends(get_authorization_context)]
    ):
        if not context.has_permission(self.permission):
            raise PermissionDeniedError()
