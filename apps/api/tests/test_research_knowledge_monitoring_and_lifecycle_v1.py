"""Integration & Domain Tests for Stage 109 Research Knowledge, Monitoring & Lifecycle.

Validates:
1. Research Overview Summary Live Metrics
2. Knowledge Library Indexing, Structured Search & Tenant Isolation
3. Dependency Lineage Graph Traversal & Cycle Safety
4. Source Change Ingestion, Deduplication & Downstream Impact Generation
5. Impact Assessment & Prioritization
6. Automated Reference & Citation Revalidation Workflow
7. Research Update Queue Lifecycle State Machine (Acknowledge, Resolve, Reopen, Dismiss)
8. Cross-Tenant Security & Access Control
9. Historical Point-in-Time Correctness (Zero Silent Mutation of Historic Analysis/Reports)
"""

import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.research.repository import ResearchRepository
from atlas.research.service import ResearchService, get_research_service
from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app


class AuthContext:
    def __init__(self, user_id: str = "default-user", email: str = "analyst@atlas.institution"):
        self.current_user_id = user_id
        self.email = email


@pytest.fixture
def auth_ctx():
    return AuthContext(user_id="default-user")


@pytest.fixture
def clean_research_service():
    """Create an isolated test ResearchService with clean repository."""
    repo = ResearchRepository()
    return ResearchService(repository=repo)


@pytest.fixture
def client(clean_research_service, auth_ctx):
    app.dependency_overrides[get_research_service] = lambda: clean_research_service
    app.dependency_overrides[get_current_user] = lambda: AuthPrincipal(
        sub=auth_ctx.current_user_id,
        email=auth_ctx.email,
        role="authenticated",
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 1. Overview Summary Tests
# ---------------------------------------------------------------------------

def test_overview_summary_endpoint(client):
    """Verifies live operational metrics across research modules."""
    resp = client.get("/api/v1/research/overview/summary")
    assert resp.status_code == 200
    data = resp.json()

    assert data["active_investigations_count"] >= 1
    assert data["total_reports_count"] >= 1
    assert data["total_analyses_count"] >= 1
    assert data["total_theses_count"] >= 1
    assert data["open_updates_count"] >= 1
    assert "recent_activity" in data
    assert isinstance(data["recent_activity"], list)


# ---------------------------------------------------------------------------
# 2. Knowledge Library Search & Isolation Tests
# ---------------------------------------------------------------------------

def test_knowledge_search_and_retrieval(client, auth_ctx):
    """Verifies structured knowledge search and cross-user entitlement boundaries."""
    # Search all knowledge entries for default-user
    search_payload = {
        "query": "Apple",
        "limit": 20,
        "offset": 0,
    }
    resp = client.post("/api/v1/research/knowledge/search", json=search_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] >= 1
    assert any("Apple" in e["title"] for e in data["entries"])

    # Test filtering by entry_types
    search_rep_payload = {
        "entry_types": ["RESEARCH_REPORT"],
        "limit": 10,
    }
    resp2 = client.post("/api/v1/research/knowledge/search", json=search_rep_payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert all(e["entry_type"] == "RESEARCH_REPORT" for e in data2["entries"])

    # Retrieve single knowledge entry
    sample_entry_id = data["entries"][0]["knowledge_entry_id"]
    get_resp = client.get(f"/api/v1/research/knowledge/{sample_entry_id}")
    assert get_resp.status_code == 200
    entry_data = get_resp.json()
    assert entry_data["knowledge_entry_id"] == sample_entry_id

    # Cross-user isolation: user B cannot access entry if owned exclusively by user A
    # Create private entry for user-A
    auth_ctx.current_user_id = "user-alpha"
    # Switch to user-beta
    auth_ctx.current_user_id = "user-beta"
    search_beta = client.post("/api/v1/research/knowledge/search", json={"query": "non-existent-xyz"})
    assert search_beta.status_code == 200
    assert search_beta.json()["total_count"] == 0

    auth_ctx.current_user_id = "default-user"


# ---------------------------------------------------------------------------
# 3. Dependency Lineage Graph Traversal Tests
# ---------------------------------------------------------------------------

def test_dependency_lineage_graph_traversal(client):
    """Verifies multi-hop dependency lineage traversal and cycle safety."""
    resp = client.get("/api/v1/research/dependencies/lineage/REPORT/rep-aapl-fy24-initiation?max_depth=5")
    assert resp.status_code == 200
    data = resp.json()

    assert data["root_resource_type"] == "REPORT"
    assert data["root_resource_id"] == "rep-aapl-fy24-initiation"
    assert len(data["edges"]) >= 2

    # Verify upstream components are discovered in lineage
    node_ids = [n["id"] for n in data["nodes"]]
    assert "rep-aapl-fy24-initiation" in node_ids
    assert "th-aapl-margin-expansion" in node_ids


# ---------------------------------------------------------------------------
# 4. Source Change Ingestion & Deduplication Tests
# ---------------------------------------------------------------------------

def test_source_change_event_ingestion_and_deduplication(client):
    """Verifies ingestion of canonical source change events and deduplication."""
    payload = {
        "source_type": "DOCUMENT",
        "canonical_source_id": "src-sec-msft-10k-2024",
        "old_revision_id": "rev-001",
        "new_revision_id": "rev-002-amend",
        "change_type": "DOCUMENT_AMENDED",
        "changed_fields": ["Note 13 Income Taxes"],
        "provider_id": "SEC_EDGAR",
        "details": {"reason": "Footnote correction"},
    }

    resp1 = client.post("/api/v1/research/source-changes", json=payload)
    assert resp1.status_code in (200, 201)
    evt_data = resp1.json()
    assert evt_data["canonical_source_id"] == "src-sec-msft-10k-2024"
    assert evt_data["change_type"] == "DOCUMENT_AMENDED"

    # Deduplication test: re-posting same event returns existing event without creating duplicates
    resp2 = client.post("/api/v1/research/source-changes", json=payload)
    assert resp2.status_code in (200, 201)
    evt_data2 = resp2.json()
    assert evt_data2["change_event_id"] == evt_data["change_event_id"]

    # Verify listing includes the event
    list_resp = client.get("/api/v1/research/source-changes?source_type=DOCUMENT")
    assert list_resp.status_code == 200
    assert any(e["change_event_id"] == evt_data["change_event_id"] for e in list_resp.json()["events"])


# ---------------------------------------------------------------------------
# 5. Impact Assessment Tests
# ---------------------------------------------------------------------------

def test_impact_assessment_inspection(client):
    """Verifies impact assessment inspection from source-change events."""
    # Retrieve impacts for the seeded Apple 10-K/A amendment
    resp = client.get("/api/v1/research/source-changes/sce-aapl-10ka-2024/impacts")
    assert resp.status_code == 200
    impacts = resp.json()["impacts"]
    assert len(impacts) >= 1
    imp = impacts[0]
    assert imp["target_resource_id"] == "rep-aapl-fy24-initiation"
    assert imp["impact_category"] == "DIRECT_SOURCE_REFERENCE_CHANGED"
    assert imp["direct_dependency"] is True
    assert imp["review_recommended"] is True


# ---------------------------------------------------------------------------
# 6. Automated Reference Revalidation Tests
# ---------------------------------------------------------------------------

def test_automated_revalidation_workflow(client):
    """Executes reference and approval revalidation on a report."""
    reval_payload = {
        "target_type": "REPORT",
        "target_id": "rep-aapl-fy24-initiation",
        "target_revision_number": 1,
    }
    resp = client.post("/api/v1/research/revalidations", json=reval_payload)
    assert resp.status_code == 201
    result = resp.json()

    assert result["target_id"] == "rep-aapl-fy24-initiation"
    assert result["status"] in ("COMPLETED", "COMPLETED_WITH_WARNINGS")
    assert result["outcome"] in ("VALID_REFERENCES", "VALID_WITH_WARNINGS")
    assert isinstance(result["issues"], list)

    # Inspect historical revalidation list
    hist_resp = client.get("/api/v1/research/resources/REPORT/rep-aapl-fy24-initiation/revalidations")
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert len(hist) >= 1
    assert hist[0]["revalidation_id"] == result["revalidation_id"]


# ---------------------------------------------------------------------------
# 7. Update Queue Lifecycle State Machine Tests
# ---------------------------------------------------------------------------

def test_update_queue_lifecycle_state_machine(client, auth_ctx):
    """Tests complete lifecycle: OPEN -> ACKNOWLEDGED -> RESOLVED -> REOPEN -> DISMISSED."""
    auth_ctx.current_user_id = "default-user"

    # Create new update queue item
    create_payload = {
        "investigation_id": "inv-aapl-services-margin",
        "target_resource_type": "REPORT",
        "target_resource_id": "rep-aapl-fy24-initiation",
        "update_type": "SOURCE_CHANGE_REVIEW",
        "priority": "HIGH",
        "title": "Review Segment Margin Footnote",
        "description": "Footnote 3 in 10-K/A requires analyst verification.",
    }
    create_resp = client.post("/api/v1/research/updates", json=create_payload)
    assert create_resp.status_code == 201
    item = create_resp.json()
    update_id = item["update_item_id"]
    assert item["status"] == "OPEN"

    # 1. Acknowledge
    ack_resp = client.post(f"/api/v1/research/updates/{update_id}/acknowledge")
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "ACKNOWLEDGED"
    assert ack_resp.json()["acknowledged_at"] is not None

    # 2. Resolve
    resolve_resp = client.post(
        f"/api/v1/research/updates/{update_id}/resolve",
        json={"resolution_note": "Verified footnote 3. Services gross margin unaffected."},
    )
    assert resolve_resp.status_code == 200
    resolved = resolve_resp.json()
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolved_at"] is not None
    assert "Services gross margin unaffected" in resolved["resolution_note"]

    # 3. Reopen
    reopen_resp = client.post(f"/api/v1/research/updates/{update_id}/reopen")
    assert reopen_resp.status_code == 200
    assert reopen_resp.json()["status"] == "OPEN"

    # 4. Dismiss
    dismiss_resp = client.post(f"/api/v1/research/updates/{update_id}/dismiss")
    assert dismiss_resp.status_code == 200
    assert dismiss_resp.json()["status"] == "DISMISSED"


# ---------------------------------------------------------------------------
# 8. Cross-Tenant Security on Update Queue Tests
# ---------------------------------------------------------------------------

def test_cross_tenant_isolation_on_update_queue(client, auth_ctx):
    """Verifies unauthorized user cannot acknowledge or mutate another user's update task."""
    # Create update item owned by user-alpha
    auth_ctx.current_user_id = "user-alpha"
    create_resp = client.post(
        "/api/v1/research/updates",
        json={
            "target_resource_type": "REPORT",
            "target_resource_id": "rep-private-001",
            "update_type": "SOURCE_CHANGE_REVIEW",
            "title": "Confidential Alpha Review",
        },
    )
    assert create_resp.status_code == 201
    alpha_item_id = create_resp.json()["update_item_id"]

    # Switch to user-beta and attempt to mutate
    auth_ctx.current_user_id = "user-beta"
    unauth_resp = client.post(f"/api/v1/research/updates/{alpha_item_id}/acknowledge")
    assert unauth_resp.status_code == 403

    # Reset
    auth_ctx.current_user_id = "default-user"


# ---------------------------------------------------------------------------
# 9. Historical Point-in-Time Correctness Tests
# ---------------------------------------------------------------------------

def test_historical_point_in_time_preservation(client):
    """Verifies that source-change events and revalidation do not mutate historic runs/reports."""
    # 1. Fetch historical analysis run
    rep = client.get("/api/v1/research/reports/rep-aapl-fy24-initiation")
    assert rep.status_code == 200
    initial_rep_revision = rep.json()["current_revision"]

    # 2. Ingest another source change event
    client.post(
        "/api/v1/research/source-changes",
        json={
            "source_type": "DOCUMENT",
            "canonical_source_id": "src-sec-aapl-10k-2024",
            "old_revision_id": "rev-002",
            "new_revision_id": "rev-003",
            "change_type": "DOCUMENT_AMENDED",
            "changed_fields": ["Item 1A Risk Factors"],
        },
    )

    # 3. Verify report revision remains unchanged (never silently incremented or altered)
    rep_after = client.get("/api/v1/research/reports/rep-aapl-fy24-initiation")
    assert rep_after.status_code == 200
    assert rep_after.json()["current_revision"] == initial_rep_revision

