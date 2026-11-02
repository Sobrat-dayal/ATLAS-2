import pytest
from atlas.agents.service import AgentRegistryService
from atlas.auth import AuthPrincipal
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers import agents as agents_router


@pytest.fixture()
def client():
    agents_router._service = AgentRegistryService()
    principal = AuthPrincipal(
        sub="user-stage146",
        raw_claims={"tenant_id": "tenant-stage146"},
    )
    app.dependency_overrides[get_current_user] = lambda: principal
    yield TestClient(app)
    app.dependency_overrides.clear()


def create_draft(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "Research Agent",
            "description": "Controlled research configuration",
            "role": "Research",
            "model_id": "atlas-intelligence-v1",
            "instructions": "Summarize only authorized inputs.",
            "tool_ids": [],
            "execution_limits": {"max_model_calls": 3},
        },
    )
    assert response.status_code == 201
    return response.json()


def test_agent_can_publish_and_create_non_dispatching_run(client: TestClient) -> None:
    draft = create_draft(client)
    agent_id = draft["agent_id"]

    published = client.post(f"/api/v1/agents/{agent_id}/publish")
    assert published.status_code == 200
    assert published.json()["status"] == "PUBLISHED"

    run = client.post(f"/api/v1/agents/{agent_id}/runs", json={"input": {"query": "GDP"}})
    assert run.status_code == 202
    body = run.json()
    assert body["status"] == "QUEUED"
    assert body["execution_enabled"] is False
    assert body["events"][0]["event_type"] == "RUN_QUEUED"
    assert body["events"][0]["metadata"]["reason"] == "EXECUTION_WORKER_UNAVAILABLE"


def test_draft_cannot_create_run(client: TestClient) -> None:
    draft = create_draft(client)

    response = client.post(f"/api/v1/agents/{draft['agent_id']}/runs", json={"input": {}})

    assert response.status_code == 409
    assert "published" in response.json()["error"]["message"]


def test_invalid_model_and_tool_are_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "Invalid Agent",
            "model_id": "not-approved",
            "instructions": "No execution.",
            "tool_ids": ["atlas.not.registered"],
        },
    )

    assert response.status_code == 422
    assert "Model" in response.json()["error"]["message"]


def test_agent_isolation_hides_other_principal(client: TestClient) -> None:
    draft = create_draft(client)
    other = AuthPrincipal(sub="other-user", raw_claims={"tenant_id": "other-tenant"})
    app.dependency_overrides[get_current_user] = lambda: other

    response = client.get(f"/api/v1/agents/{draft['agent_id']}")

    assert response.status_code == 404