"""Stage 148 AI Department Registry API."""

from __future__ import annotations

from typing import Annotated

from atlas.agents.departments import (
    DepartmentDefinition,
    DepartmentRegistryService,
    DepartmentTemplate,
)
from atlas.agents.errors import DepartmentNotFoundError, DepartmentValidationError
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/agents/departments", tags=["Agent Departments"])
_department_service: DepartmentRegistryService | None = None


def get_department_service() -> DepartmentRegistryService:
    global _department_service
    if _department_service is None:
        _department_service = DepartmentRegistryService()
    return _department_service


class DepartmentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2_000)
    purpose: str = Field(default="", max_length=2_000)
    knowledge_scope: str = Field(default="DEPARTMENT_ONLY")
    budget_limit_usd: float = Field(default=500.0, ge=0)
    template_id: str | None = None


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2_000)
    purpose: str | None = Field(default=None, max_length=2_000)
    knowledge_scope: str | None = None
    budget_limit_usd: float | None = Field(default=None, ge=0)


class DepartmentTemplateResponse(BaseModel):
    template_id: str
    name: str
    description: str
    purpose: str
    recommended_roles: list[str]
    default_tools: list[str]
    knowledge_scope: str


class DepartmentResponse(BaseModel):
    department_id: str
    name: str
    description: str
    purpose: str
    status: str
    knowledge_scope: str
    budget_limit_usd: float
    template_id: str | None
    created_at: str
    updated_at: str


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    return str(principal.raw_claims.get("tenant_id", principal.sub)), principal.sub


def _response(d: DepartmentDefinition) -> DepartmentResponse:
    return DepartmentResponse(
        department_id=d.department_id,
        name=d.name,
        description=d.description,
        purpose=d.purpose,
        status=d.status.value,
        knowledge_scope=d.knowledge_scope,
        budget_limit_usd=d.budget_limit_usd,
        template_id=d.template_id,
        created_at=d.created_at.isoformat(),
        updated_at=d.updated_at.isoformat(),
    )


@router.get("/templates", response_model=list[DepartmentTemplateResponse])
def list_department_templates(
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> list[DepartmentTemplateResponse]:
    return [
        DepartmentTemplateResponse(
            template_id=t.template_id,
            name=t.name,
            description=t.description,
            purpose=t.purpose,
            recommended_roles=list(t.recommended_roles),
            default_tools=list(t.default_tools),
            knowledge_scope=t.knowledge_scope,
        )
        for t in service.get_templates()
    ]


@router.get("", response_model=list[DepartmentResponse])
def list_departments(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> list[DepartmentResponse]:
    tenant_id, owner_id = _identity(current_user)
    return [_response(d) for d in service.list(tenant_id=tenant_id, owner_id=owner_id)]


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    request: DepartmentCreateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> DepartmentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        if request.template_id:
            dept = service.create_from_template(
                tenant_id=tenant_id,
                owner_id=owner_id,
                template_id=request.template_id,
                budget_limit_usd=request.budget_limit_usd,
            )
        else:
            dept = service.create(
                tenant_id=tenant_id,
                owner_id=owner_id,
                name=request.name,
                description=request.description,
                purpose=request.purpose,
                knowledge_scope=request.knowledge_scope,
                budget_limit_usd=request.budget_limit_usd,
                template_id=request.template_id,
            )
    except DepartmentValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _response(dept)


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> DepartmentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.get(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id))
    except DepartmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Department not found") from exc


@router.patch("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: str,
    request: DepartmentUpdateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> DepartmentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(
            service.update(
                department_id=department_id,
                tenant_id=tenant_id,
                owner_id=owner_id,
                name=request.name,
                description=request.description,
                purpose=request.purpose,
                budget_limit_usd=request.budget_limit_usd,
                knowledge_scope=request.knowledge_scope,
            )
        )
    except DepartmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Department not found") from exc
    except DepartmentValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{department_id}/activate", response_model=DepartmentResponse)
def activate_department(
    department_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> DepartmentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.activate(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id))
    except DepartmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Department not found") from exc


@router.post("/{department_id}/pause", response_model=DepartmentResponse)
def pause_department(
    department_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> DepartmentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.pause(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id))
    except DepartmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Department not found") from exc


@router.post("/{department_id}/disable", response_model=DepartmentResponse)
def disable_department(
    department_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[DepartmentRegistryService, Depends(get_department_service)],
) -> DepartmentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.disable(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id))
    except DepartmentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Department not found") from exc

