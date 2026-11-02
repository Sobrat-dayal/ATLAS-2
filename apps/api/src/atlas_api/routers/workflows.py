"""Stage 147 workflow definition and validation API."""

from __future__ import annotations

from typing import Annotated, Any

from atlas.auth import AuthPrincipal
from atlas.workflows.domain import (
    WorkflowEdge,
    WorkflowGraph,
    WorkflowNode,
    WorkflowNodeType,
    WorkflowPortType,
)
from atlas.workflows.errors import WorkflowNotFoundError, WorkflowValidationError
from atlas.workflows.service import WorkflowRegistryService
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/workflows", tags=["Workflows"])
_service = WorkflowRegistryService()


class WorkflowNodeRequest(BaseModel):
    node_id: str = Field(min_length=1, max_length=100)
    node_type: WorkflowNodeType
    config: dict[str, Any] = Field(default_factory=dict)
    input_type: WorkflowPortType = WorkflowPortType.ANY
    output_type: WorkflowPortType = WorkflowPortType.ANY


class WorkflowEdgeRequest(BaseModel):
    edge_id: str = Field(min_length=1, max_length=100)
    source_node_id: str
    target_node_id: str
    source_type: WorkflowPortType = WorkflowPortType.ANY
    target_type: WorkflowPortType = WorkflowPortType.ANY


class WorkflowGraphRequest(BaseModel):
    nodes: list[WorkflowNodeRequest] = Field(max_length=100)
    edges: list[WorkflowEdgeRequest] = Field(default_factory=list, max_length=300)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)

    def to_domain(self) -> WorkflowGraph:
        return WorkflowGraph(
            nodes=tuple(
                WorkflowNode(
                    node_id=node.node_id,
                    node_type=node.node_type,
                    config=node.config,
                    input_type=node.input_type,
                    output_type=node.output_type,
                )
                for node in self.nodes
            ),
            edges=tuple(
                WorkflowEdge(
                    edge_id=edge.edge_id,
                    source_node_id=edge.source_node_id,
                    target_node_id=edge.target_node_id,
                    source_type=edge.source_type,
                    target_type=edge.target_type,
                )
                for edge in self.edges
            ),
            input_schema=self.input_schema,
            output_schema=self.output_schema,
        )


class WorkflowCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2_000)
    graph: WorkflowGraphRequest


class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    description: str
    status: str
    version_id: str
    version: int


class WorkflowValidationResponse(BaseModel):
    valid: bool
    execution_order: list[str] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    errors: list[str] = Field(default_factory=list)


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    return str(principal.raw_claims.get("tenant_id", principal.sub)), principal.sub


def _response(workflow) -> WorkflowResponse:
    version = workflow.versions[-1]
    return WorkflowResponse(
        workflow_id=workflow.workflow_id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
        version_id=version.version_id,
        version=version.version,
    )


@router.get("", response_model=list[WorkflowResponse])
def list_workflows(current_user: Annotated[AuthPrincipal, Depends(get_current_user)]) -> list[WorkflowResponse]:
    tenant_id, owner_id = _identity(current_user)
    return [_response(item) for item in _service.list(tenant_id=tenant_id, owner_id=owner_id)]


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(
    request: WorkflowCreateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> WorkflowResponse:
    tenant_id, owner_id = _identity(current_user)
    workflow = _service.create(
        tenant_id=tenant_id,
        owner_id=owner_id,
        name=request.name,
        description=request.description,
        graph=request.graph.to_domain(),
    )
    return _response(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> WorkflowResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(_service.get(workflow_id=workflow_id, tenant_id=tenant_id, owner_id=owner_id))
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc


@router.post("/{workflow_id}/validate", response_model=WorkflowValidationResponse)
def validate_workflow(
    workflow_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> WorkflowValidationResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        compiled = _service.validate(workflow_id=workflow_id, tenant_id=tenant_id, owner_id=owner_id)
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc
    except WorkflowValidationError as exc:
        return WorkflowValidationResponse(valid=False, errors=exc.messages)
    return WorkflowValidationResponse(
        valid=True,
        execution_order=list(compiled.execution_order),
        node_count=compiled.node_count,
        edge_count=compiled.edge_count,
    )


@router.post("/{workflow_id}/publish", response_model=WorkflowResponse)
def publish_workflow(
    workflow_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> WorkflowResponse:
    tenant_id, owner_id = _identity(current_user)
    try:
        return _response(_service.publish(workflow_id=workflow_id, tenant_id=tenant_id, owner_id=owner_id))
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Workflow not found") from exc
    except WorkflowValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.messages) from exc