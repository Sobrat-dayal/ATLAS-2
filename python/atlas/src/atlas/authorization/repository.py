from typing import Sequence, Optional, List
import uuid
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import AuthzRole, AuthzPermission, AuthzUserRole, AuthzRolePermission


class AuthorizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_explicit_user_roles(self, user_id: uuid.UUID | str) -> Sequence[AuthzRole]:
        """Get the roles explicitly assigned to a user."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        stmt = (
            select(AuthzRole)
            .join(AuthzUserRole)
            .where(AuthzUserRole.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_roles_by_keys(self, role_keys: Sequence[str]) -> Sequence[AuthzRole]:
        stmt = select(AuthzRole).where(AuthzRole.key.in_(role_keys))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_role_permissions(self, role_keys: Sequence[str]) -> Sequence[AuthzPermission]:
        """Get all permissions for a set of role keys."""
        if not role_keys:
            return []
            
        stmt = (
            select(AuthzPermission)
            .join(AuthzRolePermission)
            .join(AuthzRole)
            .where(AuthzRole.key.in_(role_keys))
            .distinct()
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_roles(self) -> Sequence[AuthzRole]:
        stmt = select(AuthzRole).order_by(AuthzRole.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_permissions(self) -> Sequence[AuthzPermission]:
        stmt = select(AuthzPermission).order_by(AuthzPermission.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_role_by_key(self, role_key: str) -> Optional[AuthzRole]:
        stmt = select(AuthzRole).where(AuthzRole.key == role_key)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def grant_role(
        self, user_id: uuid.UUID | str, role_key: str, assigned_by_user_id: Optional[uuid.UUID | str] = None
    ) -> bool:
        """Grant a role to a user. Returns True if granted, False if already had it."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        if isinstance(assigned_by_user_id, str):
            assigned_by_user_id = uuid.UUID(assigned_by_user_id)
            
        role = await self.get_role_by_key(role_key)
        if not role:
            return False
            
        stmt = select(AuthzUserRole).where(
            and_(AuthzUserRole.user_id == user_id, AuthzUserRole.role_id == role.id)
        )
        result = await self.session.execute(stmt)
        existing = result.scalars().first()
        
        if existing:
            return False
            
        user_role = AuthzUserRole(
            user_id=user_id,
            role_id=role.id,
            assigned_by_user_id=assigned_by_user_id
        )
        self.session.add(user_role)
        return True

    async def revoke_role(self, user_id: uuid.UUID | str, role_key: str) -> bool:
        """Revoke a role from a user. Returns True if revoked, False if didn't have it."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
            
        role = await self.get_role_by_key(role_key)
        if not role:
            return False
            
        stmt = delete(AuthzUserRole).where(
            and_(AuthzUserRole.user_id == user_id, AuthzUserRole.role_id == role.id)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
