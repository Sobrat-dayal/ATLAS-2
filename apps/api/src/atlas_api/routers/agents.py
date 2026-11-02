"""Stage 146 Agent Registry and truthful run-ledger API."""

from __future__ import annotations

from typing import Annotated, Any

from atlas.agents.domain import AgentDefinition, AgentRun
from atlas.agents.errors import AgentNotFoundError, AgentValidationError
from atlas.agents.service import AgentRegistryService
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/agents", tags=["Agents"])
_service = AgentRegistryService()


class AgentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2_000)
    role: str = Field(default="General Assistant", min_length=1, max_length=80)
    model_id: str
    instructions: str = Field(min_length=1, max_length=20_000)
    tool_ids: list[str] = Field(default_factory=list, max_length=50)
    execution_limits: dict[str, int] = Field(default_factory=dict)


class AgentVersionResponse(BaseModel):
    version_id: str
    version: int
    model_id: str
    tool_ids: list[str]
    execution_limits: dict[str, int]


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    description: str
    role: str
    status: str
    versions: list[AgentVersionResponse]


class AgentRunRequest(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    run_id: str
    agent_id: str
    version_id: str
    status: str
    execution_enabled: bool
    input: dict[str, Any]
    events: list[dict[str, Any]]


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    tenant_id = str(principal.raw_claims.get("tenant_id", principal.sub))
    return tenant_id, principal.sub


def _agent_response(agent: AgentDefinition) -> AgentResponse:
    return AgentResponse(
        agent_id=agent.agent_id,
        name=agent.name,
        description=agent.description,
        role=agent.role,
        status=agent.status.value,
        versions=[
            AgentVersionResponse(
                version_id=version.version_id,
                version=version.version,
                model_id=version.model_id,
                tool_ids=list(version.tool_ids),
                execution_limits=version.execution_limits,
            )
            for version in agent.versions
        ],
    )


def _run_response(run: AgentRun) -> AgentRunResponse:
    return AgentRunResponse(
        run_id=run.run_id,
        agent_id=run.agent_id,
        version_id=run.version_id,
        status=run.status.value,
        execution_enabled=run.execution_enabled,
        input=run.input,
        events=[
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "created_at": event.created_at,
                "metadata": event.metadata,
            }
            for event in run.events
        ],
    )


@router.get("", response_model=list[AgentResponse])
def list_agents(current_user: Annotated[AuthPrincipal, Depends(get_current_user)]) -> list[AgentResponse]:
    tenant_id, owner_id = _identity(current_user)
    return [_agent_response(agent) for agent in _service.list_agents(tenant_id=tenant_id, owner_id=owner_id)]


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    request: AgentCreateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AgentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        agent = _service.create_agent(
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=request.name,
            description=request.description,
            role=request.role,
            model_id=request.model_id,
            instructions=request.instructions,
            tool_ids=request.tool_ids,
            execution_limits=request.execution_limits,
        )
    except AgentValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _agent_response(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AgentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _agent_response(_service.get_agent(agent_id=agent_id, tenant_id=tenant_id, owner_id=owner_id))
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Agent not found") from exc


@router.post("/{agent_id}/publish", response_model=AgentResponse)
def publish_agent(
    agent_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AgentResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _agent_response(
            _service.publish_agent(agent_id=agent_id, tenant_id=tenant_id, owner_id=owner_id)
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Agent not found") from exc


@router.post("/{agent_id}/runs", response_model=AgentRunResponse, status_code=status.HTTP_202_ACCEPTED)
def create_run(
    agent_id: str,
    request: AgentRunRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AgentRunResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        run = _service.create_run(
            agent_id=agent_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            input_data=request.input,
        )
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Agent not found") from exc
    except AgentValidationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _run_response(run)


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
def get_run(
    run_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AgentRunResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _run_response(_service.get_run(run_id=run_id, tenant_id=tenant_id, owner_id=owner_id))
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc