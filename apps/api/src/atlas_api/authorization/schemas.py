import uuid
from typing import List

from pydantic import BaseModel, ConfigDict


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    name: str
    description: str | None
    is_system: bool


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str | None
    risk_class: str


class AuthorizationMeResponse(BaseModel):
    user_id: uuid.UUID
    roles: List[str]
    permissions: List[str]


class UserRolesResponse(BaseModel):
    implicit_roles: List[str]
    explicit_roles: List[str]
    effective_roles: List[str]
