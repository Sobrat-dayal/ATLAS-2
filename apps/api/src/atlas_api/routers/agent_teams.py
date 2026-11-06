"""Stage 148 team-definition and collaboration API."""

from __future__ import annotations

from typing import Annotated

from atlas.agents.errors import AgentNotFoundError, AgentValidationError
from atlas.agents.teams import TeamDefinition, TeamMember, TeamRegistryService, TeamRole
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.agents import get_agent_service

router = APIRouter(prefix="/agents/teams", tags=["Agent Teams"])
_service: TeamRegistryService | None = None


class TeamMemberRequest(BaseModel):
    agent_id: str
    role: TeamRole
    max_concurrency: int = Field(default=1, ge=1, le=10)
    capability_profile_id: str | None = None


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2_000)
    objective: str = Field(min_length=1, max_length=2_000)
    members: list[TeamMemberRequest] = Field(min_length=1, max_length=25)
    department_id: str | None = None
    budget_limit_usd: float = Field(default=100.0, ge=0)
    max_concurrency: int = Field(default=5, ge=1, le=50)
    review_required: bool = True


class TeamMemberResponse(BaseModel):
    agent_id: str
    role: str
    max_concurrency: int
    capability_profile_id: str | None = None


class TeamResponse(BaseModel):
    team_id: str
    name: str
    description: str
    objective: str
    status: str
    version: int
    execution_enabled: bool
    department_id: str | None = None
    coordinator_agent_id: str = ""
    budget_limit_usd: float = 100.0
    max_concurrency: int = 5
    review_required: bool = True
    members: list[TeamMemberResponse]


def get_team_service() -> TeamRegistryService:
    global _service
    if _service is None:
        _service = TeamRegistryService(get_agent_service())
    return _service


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    return str(principal.raw_claims.get("tenant_id", principal.sub)), principal.sub


def _response(team: TeamDefinition) -> TeamResponse:
    return TeamResponse(
        team_id=team.team_id,
        name=team.name,
        description=team.description,
        objective=team.objective,
        status=team.status.value,
        version=team.version,
        execution_enabled=False,
        department_id=team.department_id,
        coordinator_agent_id=team.coordinator_agent_id,
        budget_limit_usd=team.budget_limit_usd,
        max_concurrency=team.max_concurrency,
        review_required=team.review_required,
        members=[
            TeamMemberResponse(
                agent_id=member.agent_id,
                role=member.role.value,
                max_concurrency=member.max_concurrency,
                capability_profile_id=member.capability_profile_id,
            )
            for member in team.members
        ],
    )


@router.get("", response_model=list[TeamResponse])
def list_teams(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
    department_id: str | None = None,
) -> list[TeamResponse]:
    tenant_id, owner_id = _identity(current_user)
    return [
        _response(team)
        for team in service.list(tenant_id=tenant_id, owner_id=owner_id, department_id=department_id)
    ]


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    request: TeamCreateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
) -> TeamResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        team = service.create(
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=request.name,
            description=request.description,
            objective=request.objective,
            department_id=request.department_id,
            budget_limit_usd=request.budget_limit_usd,
            max_concurrency=request.max_concurrency,
            review_required=request.review_required,
            members=[
                TeamMember(
                    agent_id=member.agent_id,
                    role=member.role,
                    max_concurrency=member.max_concurrency,
                    capability_profile_id=member.capability_profile_id,
                )
                for member in request.members
            ],
        )
    except (AgentNotFoundError, AgentValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _response(team)


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
) -> TeamResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id))
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc


@router.post("/{team_id}/publish", response_model=TeamResponse)
def publish_team(
    team_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
) -> TeamResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.publish(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id))
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc
    except AgentValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{team_id}/activate", response_model=TeamResponse)
def activate_team(
    team_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
) -> TeamResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.activate(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id))
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc
    except AgentValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{team_id}/pause", response_model=TeamResponse)
def pause_team(
    team_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
) -> TeamResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.pause(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id))
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc


@router.post("/{team_id}/disable", response_model=TeamResponse)
def disable_team(
    team_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
) -> TeamResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(service.disable(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id))
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
def get_team_members(
    team_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[TeamRegistryService, Depends(get_team_service)],
) -> list[TeamMemberResponse]:
    tenant_id, owner_id = _identity(current_user)
    try:
        team = service.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        return [
            TeamMemberResponse(
                agent_id=m.agent_id,
                role=m.role.value,
                max_concurrency=m.max_concurrency,
                capability_profile_id=m.capability_profile_id,
            )
            for m in team.members
        ]
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Team not found") from exc
