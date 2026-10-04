import os
from typing import FrozenSet

from atlas.auth import AuthPrincipal

from .errors import AuthorizationUnavailableError, PermissionDeniedError
from .repository import AuthorizationRepository
from .types import PermissionCode


class AuthorizationContext:
    def __init__(self, principal: AuthPrincipal, roles: FrozenSet[str], permissions: FrozenSet[str]):
        self.principal = principal
        self.roles = roles
        self.permissions = permissions

    def has_permission(self, permission: str | PermissionCode) -> bool:
        if isinstance(permission, PermissionCode):
            permission = permission.value
        return permission in self.permissions


class AuthorizationService:
    def __init__(self, repository: AuthorizationRepository):
        self.repository = repository
        self.default_role = os.environ.get("ATLAS_AUTHZ_DEFAULT_ROLE", "member")

    async def get_effective_roles(self, principal: AuthPrincipal) -> FrozenSet[str]:
        try:
            explicit_roles = await self.repository.get_explicit_user_roles(principal.user_id)
            roles = {self.default_role}
            for role in explicit_roles:
                roles.add(role.key)
            return frozenset(roles)
        except Exception as e:
            raise AuthorizationUnavailableError(f"Failed to resolve roles: {str(e)}") from e

    async def get_effective_permissions(self, principal: AuthPrincipal) -> FrozenSet[str]:
        try:
            roles = await self.get_effective_roles(principal)
            permissions_models = await self.repository.get_role_permissions(list(roles))
            permissions = {p.code for p in permissions_models}
            return frozenset(permissions)
        except AuthorizationUnavailableError:
            raise
        except Exception as e:
            raise AuthorizationUnavailableError(f"Failed to resolve permissions: {str(e)}") from e

    async def get_authorization_context(self, principal: AuthPrincipal) -> AuthorizationContext:
        try:
            roles = await self.get_effective_roles(principal)
            permissions_models = await self.repository.get_role_permissions(list(roles))
            permissions = {p.code for p in permissions_models}
            return AuthorizationContext(principal=principal, roles=roles, permissions=permissions)
        except AuthorizationUnavailableError:
            raise
        except Exception as e:
            raise AuthorizationUnavailableError(f"Failed to build authorization context: {str(e)}") from e

    async def has_permission(self, principal: AuthPrincipal, permission: str | PermissionCode) -> bool:
        context = await self.get_authorization_context(principal)
        return context.has_permission(permission)

    async def require_permission(self, principal: AuthPrincipal, permission: str | PermissionCode) -> None:
        if not await self.has_permission(principal, permission):
            raise PermissionDeniedError()
