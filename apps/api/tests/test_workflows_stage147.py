import pytest
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
from atlas.workflows.validation import validate_and_compile
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers import workflows as workflows_router


def graph(*, edges: tuple[WorkflowEdge, ...] = ()) -> WorkflowGraph:
    return WorkflowGraph(
        nodes=(
            WorkflowNode("start", WorkflowNodeType.MANUAL_TRIGGER, output_type=WorkflowPortType.STRING),
            WorkflowNode("finish", WorkflowNodeType.RETURN, input_type=WorkflowPortType.STRING),
        ),
        edges=edges,
    )


def test_valid_graph_compiles_deterministically() -> None:
    compiled = validate_and_compile(
        graph(
            edges=(
                WorkflowEdge(
                    "edge-1",
                    "start",
                    "finish",
                    WorkflowPortType.STRING,
                    WorkflowPortType.STRING,
                ),
            )
        )
    )

    assert compiled.execution_order == ("start", "finish")
    assert compiled.node_count == 2
    assert compiled.edge_count == 1


def test_cycle_and_unreachable_nodes_are_rejected() -> None:
    cyclic = WorkflowGraph(
        nodes=(
            WorkflowNode("start", WorkflowNodeType.MANUAL_TRIGGER),
            WorkflowNode("finish", WorkflowNodeType.RETURN),
        ),
        edges=(WorkflowEdge("loop", "start", "start"),),
    )

    with pytest.raises(WorkflowValidationError, match="cannot connect"):
        validate_and_compile(cyclic)

    unreachable = WorkflowGraph(
        nodes=(
            WorkflowNode("start", WorkflowNodeType.MANUAL_TRIGGER),
            WorkflowNode("finish", WorkflowNodeType.RETURN),
            WorkflowNode("orphan", WorkflowNodeType.RETURN),
        ),
        edges=(WorkflowEdge("edge-1", "start", "finish"),),
    )

    with pytest.raises(WorkflowValidationError, match="Unreachable"):
        validate_and_compile(unreachable)


def test_incompatible_ports_are_rejected() -> None:
    invalid = graph(
        edges=(
            WorkflowEdge(
                "edge-1",
                "start",
                "finish",
                WorkflowPortType.STRING,
                WorkflowPortType.NUMBER,
            ),
        )
    )

    with pytest.raises(WorkflowValidationError, match="incompatible"):
        validate_and_compile(invalid)


def test_model_and_tool_nodes_require_registered_capabilities() -> None:
    invalid = WorkflowGraph(
        nodes=(
            WorkflowNode("start", WorkflowNodeType.MANUAL_TRIGGER),
            WorkflowNode("ai", WorkflowNodeType.AI_AGENT, {"model_id": "missing-model"}),
            WorkflowNode("tool", WorkflowNodeType.ATLAS_TOOL, {"tool_id": "missing-tool"}),
            WorkflowNode("finish", WorkflowNodeType.RETURN),
        ),
        edges=(
            WorkflowEdge("e1", "start", "ai"),
            WorkflowEdge("e2", "ai", "tool"),
            WorkflowEdge("e3", "tool", "finish"),
        ),
    )

    with pytest.raises(WorkflowValidationError) as error:
        validate_and_compile(invalid)
    assert "ineligible model" in str(error.value)
    assert "unregistered tool" in str(error.value)


@pytest.fixture()
def client():
    workflows_router._service = workflows_router.WorkflowRegistryService()
    principal = AuthPrincipal(sub="workflow-user", raw_claims={"tenant_id": "workflow-tenant"})
    app.dependency_overrides[get_current_user] = lambda: principal
    yield TestClient(app)
    app.dependency_overrides.clear()


def workflow_payload() -> dict:
    return {
        "name": "Research Pipeline",
        "description": "A validated graph definition",
        "graph": {
            "nodes": [
                {"node_id": "start", "node_type": "MANUAL_TRIGGER", "output_type": "STRING"},
                {"node_id": "finish", "node_type": "RETURN", "input_type": "STRING"},
            ],
            "edges": [
                {
                    "edge_id": "edge-1",
                    "source_node_id": "start",
                    "target_node_id": "finish",
                    "source_type": "STRING",
                    "target_type": "STRING",
                }
            ],
        },
    }


def test_workflow_api_validates_and_publishes(client: TestClient) -> None:
    created = client.post("/api/v1/workflows", json=workflow_payload())
    assert created.status_code == 201
    workflow_id = created.json()["workflow_id"]

    validation = client.post(f"/api/v1/workflows/{workflow_id}/validate")
    assert validation.status_code == 200
    assert validation.json()["valid"] is True
    assert validation.json()["execution_order"] == ["start", "finish"]

    published = client.post(f"/api/v1/workflows/{workflow_id}/publish")
    assert published.status_code == 200
    assert published.json()["status"] == "PUBLISHED"


def test_workflow_service_hides_other_tenant() -> None:
    service = WorkflowRegistryService()
    workflow = service.create(
        tenant_id="tenant-a",
        owner_id="user-a",
        name="Private",
        description="",
        graph=graph(
            edges=(WorkflowEdge("edge-1", "start", "finish"),),
        ),
    )

    with pytest.raises(WorkflowNotFoundError):
        service.get(workflow_id=workflow.workflow_id, tenant_id="tenant-b", owner_id="user-b")
