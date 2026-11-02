import pytest
from atlas.agents.errors import AgentNotFoundError
from atlas.agents.service import AgentRegistryService
from atlas.agents.teams import TeamMember, TeamRegistryService, TeamRole
from atlas.auth import AuthPrincipal
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers import agent_teams as teams_router
from atlas_api.routers import agents as agents_router


@pytest.fixture()
def client():
    agents = AgentRegistryService()
    agents_router._service = agents
    teams_router._service = TeamRegistryService(agents)
    principal = AuthPrincipal(sub="team-user", raw_claims={"tenant_id": "team-tenant"})
    app.dependency_overrides[get_current_user] = lambda: principal
    yield TestClient(app)
    app.dependency_overrides.clear()


def create_published_agent(client: TestClient, name: str) -> str:
    created = client.post(
        "/api/v1/agents",
        json={
            "name": name,
            "description": "A test team worker",
            "role": "Research",
            "model_id": "atlas-intelligence-v1",
            "instructions": "Use only authorized inputs.",
        },
    )
    assert created.status_code == 201
    agent_id = created.json()["agent_id"]
    published = client.post(f"/api/v1/agents/{agent_id}/publish")
    assert published.status_code == 200
    return agent_id


def team_payload(coordinator_id: str, specialist_id: str) -> dict:
    return {
        "name": "Research Team",
        "description": "Bounded research collaboration",
        "objective": "Produce source-grounded research inputs.",
        "members": [
            {"agent_id": coordinator_id, "role": "COORDINATOR"},
            {"agent_id": specialist_id, "role": "SPECIALIST"},
        ],
    }


def test_team_can_publish_but_is_not_execution_enabled(client: TestClient) -> None:
    coordinator = create_published_agent(client, "Coordinator")
    specialist = create_published_agent(client, "Researcher")

    created = client.post("/api/v1/agents/teams", json=team_payload(coordinator, specialist))
    assert created.status_code == 201
    team_id = created.json()["team_id"]
    assert created.json()["status"] == "DRAFT"
    assert created.json()["execution_enabled"] is False

    published = client.post(f"/api/v1/agents/teams/{team_id}/publish")
    assert published.status_code == 200
    assert published.json()["status"] == "PUBLISHED"
    assert published.json()["execution_enabled"] is False

    disabled = client.post(f"/api/v1/agents/teams/{team_id}/disable")
    assert disabled.status_code == 200
    assert disabled.json()["status"] == "DISABLED"


def test_team_requires_one_coordinator_and_published_agents(client: TestClient) -> None:
    coordinator = create_published_agent(client, "Coordinator")
    specialist = create_published_agent(client, "Researcher")
    payload = team_payload(coordinator, specialist)
    payload["members"][0]["role"] = "SPECIALIST"

    response = client.post("/api/v1/agents/teams", json=payload)

    assert response.status_code == 422
    assert "coordinator" in response.json()["error"]["message"]


def test_team_rejects_unknown_agent(client: TestClient) -> None:
    response = client.post(
        "/api/v1/agents/teams",
        json=team_payload("missing-coordinator", "missing-specialist"),
    )

    assert response.status_code == 422
    assert "not found" in response.json()["error"]["message"]


def test_team_service_enforces_tenant_isolation() -> None:
    agents = AgentRegistryService()
    agent = agents.create_agent(
        tenant_id="tenant-a",
        owner_id="user-a",
        name="Coordinator",
        description="",
        role="Research",
        model_id="atlas-intelligence-v1",
        instructions="Use authorized inputs.",
        tool_ids=[],
        execution_limits={},
    )
    agents.publish_agent(agent_id=agent.agent_id, tenant_id="tenant-a", owner_id="user-a")
    teams = TeamRegistryService(agents)
    team = teams.create(
        tenant_id="tenant-a",
        owner_id="user-a",
        name="Private Team",
        description="",
        objective="Private work.",
        members=[TeamMember(agent.agent_id, TeamRole.COORDINATOR)],
    )

    with pytest.raises(AgentNotFoundError, match="not found"):
        teams.get(team_id=team.team_id, tenant_id="tenant-b", owner_id="user-b")
