"""Unit, Integration, and Security Tests for Institutional Financial Research Platform (Stage 104)."""

import pytest
from atlas.auth import AuthPrincipal
from atlas.research.repository import ResearchRepository
from atlas.research.schemas import CreateResearchInvestigationDTO
from atlas.research.service import ResearchService, get_research_service
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app


def _get_error_message(resp) -> str:
    data = resp.json()
    if isinstance(data, dict):
        if "error" in data and isinstance(data["error"], dict) and "message" in data["error"]:
            return data["error"]["message"]
        if "detail" in data:
            return str(data["detail"])
    return str(data)


# ---------------------------------------------------------------------------
# Fixtures & Test Setup
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_research_service():
    """Create an isolated test ResearchService with clean in-memory repository."""
    repo = ResearchRepository()
    return ResearchService(repository=repo)


@pytest.fixture
def test_client(clean_research_service):
    """FastAPI TestClient with overridden get_research_service and mock authenticated user."""
    mock_user = AuthPrincipal(
        sub="analyst-1",
        email="analyst1@atlas-research.local",
        role="authenticated",
    )

    app.dependency_overrides[get_research_service] = lambda: clean_research_service
    app.dependency_overrides[get_current_user] = lambda: mock_user

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 1. Investigation Lifecycle & Concurrency Tests
# ---------------------------------------------------------------------------

def test_investigation_creation_and_retrieval(test_client):
    payload = {
        "title": "NVIDIA Accelerated Computing & Data Center Demand FY2025",
        "research_type": "COMPANY_RESEARCH",
        "primary_subject_entity_id": "NVDA",
        "primary_subject_type": "COMPANY",
        "secondary_entity_ids": ["MSFT", "AAPL"],
        "research_objective": "Evaluate enterprise Hopper and Blackwell architecture revenue sustainability.",
        "description": "Comprehensive institutional study covering supply chain packaging and customer concentration.",
    }
    resp = test_client.post("/api/v1/research/investigations", json=payload)
    assert resp.status_code == 201
    data = resp.json()

    inv_id = data["investigation_id"]
    assert data["title"] == payload["title"]
    assert data["primary_subject_entity_id"] == "NVDA"
    assert data["status"] == "DRAFT"
    assert data["revision"] == 1

    # Read back details
    get_resp = test_client.get(f"/api/v1/research/investigations/{inv_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["investigation_id"] == inv_id


def test_investigation_optimistic_concurrency_conflict(test_client):
    # Create investigation
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Macro Inflation Outlook 2025", "research_type": "MACROECONOMIC_RESEARCH"},
    )
    assert create_resp.status_code == 201
    inv_id = create_resp.json()["investigation_id"]
    rev = create_resp.json()["revision"]

    # First update: expected_revision = 1 -> succeeds, increments to 2
    up1 = test_client.patch(
        f"/api/v1/research/investigations/{inv_id}",
        json={"expected_revision": rev, "title": "Updated Macro Inflation Outlook 2025"},
    )
    assert up1.status_code == 200
    assert up1.json()["revision"] == 2

    # Second update with stale expected_revision = 1 -> 409 Conflict
    up2 = test_client.patch(
        f"/api/v1/research/investigations/{inv_id}",
        json={"expected_revision": rev, "title": "Conflicting Concurrent Edit"},
    )
    assert up2.status_code == 409
    assert "Revision conflict" in _get_error_message(up2)


def test_investigation_filtering_and_search(test_client):
    # Create distinct investigations
    test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Apple Hardware Ecosystem", "primary_subject_entity_id": "AAPL", "research_type": "COMPANY_RESEARCH"},
    )
    test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Federal Reserve Liquidity Facility", "primary_subject_entity_id": "FED", "research_type": "MACROECONOMIC_RESEARCH"},
    )

    # Filter by entity
    resp = test_client.get("/api/v1/research/investigations?entity_id=AAPL")
    assert resp.status_code == 200
    data = resp.json()
    assert any(i["primary_subject_entity_id"] == "AAPL" for i in data["items"])

    # Search by text query
    q_resp = test_client.get("/api/v1/research/investigations?q=Liquidity")
    assert q_resp.status_code == 200
    assert any("Liquidity" in i["title"] for i in q_resp.json()["items"])


def test_investigation_archiving_and_deletion(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Temporary Investigation for Deletion", "research_type": "GENERAL_FINANCIAL_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Archive
    arch_resp = test_client.post(f"/api/v1/research/investigations/{inv_id}/archive")
    assert arch_resp.status_code == 200
    assert arch_resp.json()["status"] == "ARCHIVED"
    assert arch_resp.json()["archived_at"] is not None

    # Delete
    del_resp = test_client.delete(f"/api/v1/research/investigations/{inv_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True

    # 404 after deletion
    assert test_client.get(f"/api/v1/research/investigations/{inv_id}").status_code == 404


# ---------------------------------------------------------------------------
# 2. Cross-User Privacy & RLS Isolation Tests
# ---------------------------------------------------------------------------

def test_cross_user_investigation_access_denied(test_client, clean_research_service):
    # Create investigation as analyst-1
    inv_dto = clean_research_service.create_investigation(
        CreateResearchInvestigationDTO(title="Confidential Hedge Fund Investigation"),
        user_id="analyst-1",
    )
    inv_id = inv_dto.investigation_id

    # Switch user to analyst-2
    app.dependency_overrides[get_current_user] = lambda: AuthPrincipal(
        sub="analyst-2",
        email="analyst2@other-fund.local",
        role="authenticated",
    )

    # Attempt to read analyst-1's investigation -> 403 Forbidden
    resp = test_client.get(f"/api/v1/research/investigations/{inv_id}")
    assert resp.status_code == 403

    # Attempt to update analyst-1's investigation -> 403 Forbidden
    up_resp = test_client.patch(
        f"/api/v1/research/investigations/{inv_id}",
        json={"expected_revision": 1, "title": "Hacked Title"},
    )
    assert up_resp.status_code == 403

    # Attempt to delete -> 403 Forbidden
    del_resp = test_client.delete(f"/api/v1/research/investigations/{inv_id}")
    assert del_resp.status_code == 403


# ---------------------------------------------------------------------------
# 3. Research Questions & Hypotheses Tests
# ---------------------------------------------------------------------------

def test_research_questions_lifecycle(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Semiconductor CapEx Inquiries", "research_type": "INDUSTRY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Add question
    q_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/questions",
        json={"question_text": "What is the expected leading-edge wafer pricing for 2nm nodes in 2025?", "related_entity_ids": ["TSM"]},
    )
    assert q_resp.status_code == 201
    q_id = q_resp.json()["question_id"]
    assert q_resp.json()["status"] == "OPEN"

    # Update question to ADDRESSED
    up_q = test_client.patch(
        f"/api/v1/research/questions/{q_id}",
        json={"status": "ADDRESSED"},
    )
    assert up_q.status_code == 200
    assert up_q.json()["status"] == "ADDRESSED"

    # List questions
    list_q = test_client.get(f"/api/v1/research/investigations/{inv_id}/questions")
    assert list_q.status_code == 200
    assert len(list_q.json()["items"]) == 1

    # Delete question
    del_q = test_client.delete(f"/api/v1/research/questions/{q_id}")
    assert del_q.status_code == 200
    assert del_q.json()["deleted"] is True


def test_research_hypotheses_lifecycle_and_non_automatic_truth(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Hypothesis Validation Study", "research_type": "SECURITY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Propose hypothesis
    h_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/hypotheses",
        json={"statement": "Customer concentration among top 5 hyperscalers will decline below 40% of revenues in FY2026."},
    )
    assert h_resp.status_code == 201
    h_id = h_resp.json()["hypothesis_id"]
    assert h_resp.json()["status"] == "PROPOSED"

    # Transition status based on evidence (analyst controlled, never automatic)
    up_h = test_client.patch(
        f"/api/v1/research/hypotheses/{h_id}",
        json={"status": "INCONCLUSIVE"},
    )
    assert up_h.status_code == 200
    assert up_h.json()["status"] == "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# 4. Research Notes, Revisions & Sanitization Tests
# ---------------------------------------------------------------------------

def test_research_note_crud_and_revisions(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Analyst Notebook Workspace", "research_type": "COMPANY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Create Note
    note_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/notes",
        json={
            "title": "Initial Assessment of Services Gross Margin",
            "body_document": "## Margin Observations\n\nServices gross margin rose 70 bps sequentially.",
            "note_type": "OBSERVATION",
        },
    )
    assert note_resp.status_code == 201
    note_id = note_resp.json()["note_id"]
    assert note_resp.json()["revision"] == 1

    # Update Note -> revisions recorded
    up_note = test_client.patch(
        f"/api/v1/research/notes/{note_id}",
        json={
            "expected_revision": 1,
            "title": "Revised Assessment of Services Gross Margin",
            "body_document": "## Margin Observations\n\nServices gross margin rose 85 bps sequentially on FX adjustments.",
        },
    )
    assert up_note.status_code == 200
    assert up_note.json()["revision"] == 2

    # Check revisions history
    revs_resp = test_client.get(f"/api/v1/research/notes/{note_id}/revisions")
    assert revs_resp.status_code == 200
    revisions = revs_resp.json()
    assert len(revisions) == 2
    assert revisions[0]["revision_number"] == 1
    assert revisions[1]["revision_number"] == 2


def test_research_note_xss_sanitization(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Sanitization Testing", "research_type": "GENERAL_FINANCIAL_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    malicious_body = "Legitimate thesis.<script>alert('xss')</script><iframe src='http://evil.com'></iframe>Safe conclusion."
    note_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/notes",
        json={"title": "Security Test Note", "body_document": malicious_body},
    )
    assert note_resp.status_code == 201
    clean_body = note_resp.json()["body_document"]
    assert "<script>" not in clean_body
    assert "alert('xss')" not in clean_body
    assert "<iframe" not in clean_body
    assert "Safe conclusion." in clean_body


# ---------------------------------------------------------------------------
# 5. Research Claims: Fact vs Interpretation
# ---------------------------------------------------------------------------

def test_research_claim_categorization_and_status(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Claims Categorization", "research_type": "COMPANY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # 1. Source reported fact
    c1 = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/claims",
        json={
            "statement": "Apple reported FY2024 Total Net Sales of $391,035 million USD in its Form 10-K.",
            "claim_category": "SOURCE_REPORTED_FACT",
            "evidence_status": "SUPPORTED_BY_CITED_SOURCE",
        },
    )
    assert c1.status_code == 201
    assert c1.json()["claim_category"] == "SOURCE_REPORTED_FACT"
    assert c1.json()["evidence_status"] == "SUPPORTED_BY_CITED_SOURCE"

    # 2. Analyst interpretation (clearly distinct)
    c2 = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/claims",
        json={
            "statement": "Hardware replacement cycles are extending beyond 36 months in North America.",
            "claim_category": "ANALYST_INTERPRETATION",
            "evidence_status": "PARTIALLY_SUPPORTED",
        },
    )
    assert c2.status_code == 201
    assert c2.json()["claim_category"] == "ANALYST_INTERPRETATION"


# ---------------------------------------------------------------------------
# 6. Source Catalog, Deduplication & External URL Security
# ---------------------------------------------------------------------------

def test_canonical_sources_catalog_and_search(test_client):
    resp = test_client.get("/api/v1/research/sources")
    assert resp.status_code == 200
    sources = resp.json()["items"]
    assert len(sources) >= 6

    # Verify presence of SEC Filings, Fundamental facts, News, and Economics
    types = {s["source_type"] for s in sources}
    assert "ANNUAL_REPORT" in types
    assert "FINANCIAL_STATEMENT" in types
    assert "NEWS_ARTICLE" in types
    assert "ECONOMIC_RELEASE" in types

    # Filter by entity
    aapl_sources = test_client.get("/api/v1/research/sources?entity_id=AAPL").json()["items"]
    assert len(aapl_sources) >= 3


def test_link_source_and_deduplication(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Source Linking Investigation", "research_type": "COMPANY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Link existing source
    link_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/sources",
        json={"source_reference_id": "src-filing-aapl-10k-2024"},
    )
    assert link_resp.status_code == 201
    assert link_resp.json()["source_reference_id"] == "src-filing-aapl-10k-2024"

    # Duplicate link is idempotent
    link_again = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/sources",
        json={"source_reference_id": "src-filing-aapl-10k-2024"},
    )
    assert link_again.status_code == 201

    # Verify only 1 instance linked
    inv_sources = test_client.get(f"/api/v1/research/investigations/{inv_id}/sources").json()["items"]
    assert sum(1 for s in inv_sources if s["source_reference_id"] == "src-filing-aapl-10k-2024") == 1


def test_external_url_ssrf_mitigation(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "SSRF Security Test", "research_type": "GENERAL_FINANCIAL_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # 1. Localhost attempt
    resp_local = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/sources",
        json={"source_title": "Internal Service", "source_url": "http://localhost:8000/admin"},
    )
    assert resp_local.status_code == 400
    assert "prohibited" in _get_error_message(resp_local).lower()

    # 2. AWS / GCP Cloud Metadata IP attempt
    resp_meta = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/sources",
        json={"source_title": "Cloud Metadata", "source_url": "http://169.254.169.254/latest/meta-data/"},
    )
    assert resp_meta.status_code == 400
    assert "prohibited" in _get_error_message(resp_meta).lower()

    # 3. Private IP attempt
    resp_private = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/sources",
        json={"source_title": "Private Subnet", "source_url": "http://192.168.1.100/data.json"},
    )
    assert resp_private.status_code == 400

    # 4. Dangerous scheme attempt
    resp_scheme = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/sources",
        json={"source_title": "FTP Link", "source_url": "ftp://files.sec.gov/filing.txt"},
    )
    assert resp_scheme.status_code == 400
    assert "scheme" in _get_error_message(resp_scheme).lower()


# ---------------------------------------------------------------------------
# 7. Research Evidence & Citations Integrity Tests
# ---------------------------------------------------------------------------

def test_evidence_attachment_and_citation_generation(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Evidence Integrity Investigation", "research_type": "COMPANY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Attach evidence referencing SEC 10-K
    ev_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/evidence",
        json={
            "source_reference_id": "src-filing-aapl-10k-2024",
            "evidence_type": "REGULATORY_DISCLOSURE",
            "source_location_type": "SECTION",
            "source_location_reference": "Item 7 Management's Discussion - Gross Margin by Segment",
            "page_number": 34,
            "section_name": "Item 7. MD&A",
            "allowed_excerpt": "Products gross margin was 36.7% compared with 36.5% in the prior year.",
        },
    )
    assert ev_resp.status_code == 201
    ev_data = ev_resp.json()
    assert ev_data["page_number"] == 34
    assert ev_data["source_title"] is not None

    # Verify citation generated automatically
    cit_resp = test_client.get(f"/api/v1/research/investigations/{inv_id}/citations")
    assert cit_resp.status_code == 200
    cits = cit_resp.json()["items"]
    assert len(cits) == 1
    assert "p. 34" in cits[0]["citation_label"]
    assert cits[0]["is_broken"] is False


def test_evidence_nonexistent_source_fails(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Missing Source Test", "research_type": "COMPANY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Reference nonexistent source ID
    ev_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/evidence",
        json={
            "source_reference_id": "src-nonexistent-document-999",
            "source_location_reference": "Page 1",
        },
    )
    assert ev_resp.status_code == 404


def test_remove_evidence_marks_citations_broken(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Evidence Deletion & Broken Citations", "research_type": "COMPANY_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    ev_resp = test_client.post(
        f"/api/v1/research/investigations/{inv_id}/evidence",
        json={
            "source_reference_id": "src-filing-aapl-10k-2024",
            "source_location_reference": "Item 1 Business",
        },
    )
    ev_id = ev_resp.json()["evidence_id"]

    # Delete evidence
    del_resp = test_client.delete(f"/api/v1/research/evidence/{ev_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["removed"] is True

    # Citations now marked as broken
    cits = test_client.get(f"/api/v1/research/investigations/{inv_id}/citations").json()["items"]
    assert any(c["is_broken"] is True for c in cits)


# ---------------------------------------------------------------------------
# 8. Activity Timeline & Overview Tests
# ---------------------------------------------------------------------------

def test_research_activity_audit_timeline(test_client):
    create_resp = test_client.post(
        "/api/v1/research/investigations",
        json={"title": "Audit Timeline Investigation", "research_type": "MARKET_RESEARCH"},
    )
    inv_id = create_resp.json()["investigation_id"]

    # Perform mutations
    test_client.post(
        f"/api/v1/research/investigations/{inv_id}/questions",
        json={"question_text": "How did market liquidity evolve during the session?"},
    )
    test_client.post(
        f"/api/v1/research/investigations/{inv_id}/notes",
        json={"title": "Trading Session Observations", "body_document": "Spread widening observed in early trading."},
    )

    # Fetch activity timeline
    act_resp = test_client.get(f"/api/v1/research/investigations/{inv_id}/activity")
    assert act_resp.status_code == 200
    activities = act_resp.json()["items"]
    assert len(activities) >= 3
    action_types = [a["action_type"] for a in activities]
    assert "INVESTIGATION_CREATED" in action_types
    assert "QUESTION_ADDED" in action_types
    assert "NOTE_CREATED" in action_types


def test_research_overview_summary(test_client):
    resp = test_client.get("/api/v1/research/overview")
    assert resp.status_code == 200
    summary = resp.json()
    assert "active_investigations_count" in summary
    assert "total_notes_count" in summary
    assert "recent_investigations" in summary
    assert "recent_activities" in summary
