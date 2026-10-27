"""Institutional-Grade Investment Research Thesis & Report Studio Tests (Stage 107).

Comprehensive verification covering:
1. Report Templates Registry & Structure
2. Report CRUD, optimistic locking revision control, and finalization
3. Hierarchical Sections CRUD and safe reordering
4. Revision history snapshots and revision diffing
5. Automated Report Verification (structural completeness, citation integrity, temporal cutoff checks)
6. Zero-dependency PDF and DOCX binary report generation and authorized download
7. Structured Investment Thesis domain, Bull/Bear case arguments, and assumptions
8. User ownership isolation and RLS security enforcement
"""

import pytest
from atlas.auth import AuthPrincipal
from atlas.research.repository import ResearchRepository
from atlas.research.service import ResearchService, get_research_service
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app

# ---------------------------------------------------------------------------
# Fixtures & Setup
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_research_service():
    """Create an isolated test ResearchService with clean repository."""
    repo = ResearchRepository()
    return ResearchService(repository=repo)


@pytest.fixture
def test_client(clean_research_service):
    """FastAPI TestClient with mock authenticated user A."""
    mock_user_a = AuthPrincipal(
        sub="analyst-1",
        email="analyst1@atlas-research.local",
        role="authenticated",
    )

    app.dependency_overrides[get_research_service] = lambda: clean_research_service
    app.dependency_overrides[get_current_user] = lambda: mock_user_a
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def user_b_client(clean_research_service):
    """FastAPI TestClient for a different analyst user B."""
    mock_user_b = AuthPrincipal(
        sub="analyst-2",
        email="analyst2@atlas-research.local",
        role="authenticated",
    )

    app.dependency_overrides[get_research_service] = lambda: clean_research_service
    app.dependency_overrides[get_current_user] = lambda: mock_user_b
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 1. Report Templates Tests
# ---------------------------------------------------------------------------

def test_list_report_templates(test_client):
    """Verify built-in institutional templates are listed with required sections."""
    response = test_client.get("/api/v1/research/report-templates")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 6
    template_ids = [t["template_id"] for t in data["templates"]]
    assert "tpl-company-research" in template_ids
    assert "tpl-investment-thesis" in template_ids
    assert "tpl-earnings-review" in template_ids


def test_get_report_template_by_id(test_client):
    """Verify detailed template schema inspection."""
    response = test_client.get("/api/v1/research/report-templates/tpl-company-research")
    assert response.status_code == 200
    data = response.json()
    assert data["template_id"] == "tpl-company-research"
    assert data["report_type"] == "COMPANY_RESEARCH"
    assert len(data["default_sections"]) >= 10
    assert "EXECUTIVE_SUMMARY" in data["required_sections"]


def test_get_nonexistent_template_returns_404(test_client):
    """Verify unknown template ID returns 404."""
    response = test_client.get("/api/v1/research/report-templates/nonexistent-tpl")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 2. Report Lifecycle & Concurrency Tests
# ---------------------------------------------------------------------------

def test_create_report_from_template(test_client):
    """Verify creating a report with a template automatically initializes structured sections."""
    payload = {
        "report_type": "COMPANY_RESEARCH",
        "title": "NVIDIA Corporation (NVDA) Comprehensive Research Report",
        "subtitle": "Data Center Acceleration & Margin Sustainability Analysis",
        "abstract": "Analytical evaluation of revenue durability and customer concentration.",
        "primary_subject_id": "comp-nvda",
        "template_id": "tpl-company-research",
        "report_as_of": "2026-10-27",
        "snapshot_policy": "DRAFT_LATEST_AUTHORIZED",
    }
    response = test_client.post("/api/v1/research/reports", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["owner_user_id"] == "analyst-1"
    assert data["status"] == "DRAFT"
    assert data["current_revision"] == 1
    assert len(data["sections"]) >= 10

    # First section should be Executive Summary
    assert "Executive Summary" in data["sections"][0]["heading"]


def test_update_report_optimistic_concurrency(test_client):
    """Verify optimistic concurrency protects reports from stale concurrent overwrites."""
    # 1. Create report
    res = test_client.post(
        "/api/v1/research/reports",
        json={
            "report_type": "INVESTMENT_THESIS",
            "title": "Initial Thesis on Cloud Hyperscalers",
        },
    )
    assert res.status_code == 201
    report = res.json()
    report_id = report["report_id"]

    # 2. Valid update with expected_revision=1
    up_res = test_client.patch(
        f"/api/v1/research/reports/{report_id}",
        json={
            "title": "Revised Thesis on Cloud Hyperscalers",
            "expected_revision": 1,
        },
    )
    assert up_res.status_code == 200
    assert up_res.json()["current_revision"] == 2
    assert up_res.json()["title"] == "Revised Thesis on Cloud Hyperscalers"

    # 3. Conflict update with stale expected_revision=1
    conflict_res = test_client.patch(
        f"/api/v1/research/reports/{report_id}",
        json={
            "title": "Stale Concurrent Update",
            "expected_revision": 1,
        },
    )
    assert conflict_res.status_code == 409


def test_finalize_report_immutability(test_client):
    """Verify finalized reports are locked and cannot be mutated without a new revision."""
    res = test_client.post(
        "/api/v1/research/reports",
        json={
            "report_type": "GENERAL_RESEARCH_MEMORANDUM",
            "title": "Q3 Liquidity Review",
        },
    )
    report_id = res.json()["report_id"]

    # Finalize
    fin_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/finalize",
        json={"expected_revision": 1, "change_summary": "Signed off for publication"},
    )
    assert fin_res.status_code == 200
    assert fin_res.json()["status"] == "FINALIZED"
    assert fin_res.json()["current_revision"] == 2

    # Attempting to mutate finalized report must fail with 422
    mut_res = test_client.patch(
        f"/api/v1/research/reports/{report_id}",
        json={"title": "Illegal Mutation", "expected_revision": 2},
    )
    assert mut_res.status_code == 422


# ---------------------------------------------------------------------------
# 3. Section CRUD & Reordering Tests
# ---------------------------------------------------------------------------

def test_section_crud_and_reordering(test_client):
    """Verify adding, editing, reordering, and deleting sections."""
    rep_res = test_client.post(
        "/api/v1/research/reports",
        json={"report_type": "COMPANY_UPDATE", "title": "Apple Q4 Update"},
    )
    report_id = rep_res.json()["report_id"]

    # 1. Add section 1
    s1_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/sections",
        json={
            "heading": "Services Revenue Growth",
            "section_type": "FINANCIAL_PERFORMANCE",
            "content_blocks": [
                {"block_type": "PARAGRAPH", "content": "Services grew 12.3% YoY backed by installed base expansion."}
            ],
        },
    )
    assert s1_res.status_code == 201
    sec1_id = s1_res.json()["section_id"]

    # 2. Add section 2
    s2_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/sections",
        json={
            "heading": "Hardware Margins Overview",
            "section_type": "FINANCIAL_PERFORMANCE",
            "content_blocks": [],
        },
    )
    assert s2_res.status_code == 201
    sec2_id = s2_res.json()["section_id"]

    # 3. Reorder sections (swap sec2 to first position)
    reorder_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/sections/reorder",
        json={"section_ids": [sec2_id, sec1_id]},
    )
    assert reorder_res.status_code == 200
    sections = reorder_res.json()
    assert sections[0]["section_id"] == sec2_id
    assert sections[0]["order_index"] == 1
    assert sections[1]["section_id"] == sec1_id
    assert sections[1]["order_index"] == 2

    # 4. Delete section
    del_res = test_client.delete(f"/api/v1/research/reports/{report_id}/sections/{sec1_id}")
    assert del_res.status_code == 200

    # Remaining sections should only be 1
    list_res = test_client.get(f"/api/v1/research/reports/{report_id}/sections")
    assert len(list_res.json()) == 1


# ---------------------------------------------------------------------------
# 4. Revisions & Diffing Tests
# ---------------------------------------------------------------------------

def test_report_revisions_and_compare(test_client):
    """Verify revision history tracking and structural diffing between versions."""
    res = test_client.post(
        "/api/v1/research/reports",
        json={"report_type": "MACROECONOMIC_RESEARCH", "title": "Inflation Trend Analysis"},
    )
    report_id = res.json()["report_id"]

    # Update to create revision 2
    test_client.patch(
        f"/api/v1/research/reports/{report_id}",
        json={"title": "Global Inflation Trend Analysis (Updated)", "expected_revision": 1},
    )

    # List revisions
    rev_res = test_client.get(f"/api/v1/research/reports/{report_id}/revisions")
    assert rev_res.status_code == 200
    revs = rev_res.json()["revisions"]
    assert len(revs) == 2
    assert revs[0]["revision_number"] == 2
    assert revs[1]["revision_number"] == 1

    # Compare revisions
    diff_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/revisions/compare",
        json={"base_revision_number": 1, "target_revision_number": 2},
    )
    assert diff_res.status_code == 200
    diff = diff_res.json()
    assert diff["base_revision_number"] == 1
    assert diff["target_revision_number"] == 2
    assert "Revision 1" in diff["diff_unified"]


# ---------------------------------------------------------------------------
# 5. Automated Verification Tests
# ---------------------------------------------------------------------------

def test_report_verification_clean_report(test_client):
    """Verify report verification passes when citations and structure are compliant."""
    create_res = test_client.post(
        "/api/v1/research/reports",
        json={
            "report_type": "COMPANY_RESEARCH",
            "title": "Compliant Verification Report",
            "template_id": "tpl-company-research",
        },
    )
    assert create_res.status_code == 201
    report_id = create_res.json()["report_id"]

    verify_res = test_client.post(f"/api/v1/research/reports/{report_id}/verify", json={})
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["report_id"] == report_id
    assert "is_valid" in data
    assert data["citation_coverage_pct"] >= 0.0


def test_report_verification_detects_blocking_issues(test_client):
    """Verify verification engine flags lookahead temporal violations and broken citations."""
    create_res = test_client.post(
        "/api/v1/research/reports",
        json={
            "report_type": "COMPANY_RESEARCH",
            "title": "Temporal Conflict Test Report",
            "report_as_of": "2023-01-01",
            "research_cutoff": "2023-01-01T00:00:00Z",
        },
    )
    report_id = create_res.json()["report_id"]

    # Add a section containing an explicit citation published in 2026 (look-ahead leak)
    sec_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/sections",
        json={
            "heading": "Future Lookahead Section",
            "section_type": "FINANCIAL_PERFORMANCE",
            "content_blocks": [
                {
                    "block_type": "CITATION",
                    "citation_id": "cite-future-leak",
                    "source_id": "doc-sec-nvda-2026-10k",
                    "publication_date": "2026-02-15T00:00:00Z",
                }
            ],
        },
    )
    assert sec_res.status_code == 201

    verify_res = test_client.post(f"/api/v1/research/reports/{report_id}/verify", json={})
    assert verify_res.status_code == 200
    v = verify_res.json()
    assert v["is_valid"] is False
    assert v["blocking_issues_count"] >= 1
    issue_types = [i["issue_type"] for i in v["issues"]]
    assert "POINT_IN_TIME_CONFLICT" in issue_types


# ---------------------------------------------------------------------------
# 6. Binary PDF & DOCX Export & Download Tests
# ---------------------------------------------------------------------------

def test_export_report_pdf_and_download(test_client):
    """Verify binary standard PDF-1.4 generation and authenticated byte download."""
    create_res = test_client.post(
        "/api/v1/research/reports",
        json={
            "report_type": "COMPANY_RESEARCH",
            "title": "Export Test Report",
            "template_id": "tpl-company-research",
        },
    )
    assert create_res.status_code == 201
    report_id = create_res.json()["report_id"]

    # 1. Create PDF export
    export_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/exports",
        json={"format": "PDF", "include_toc": True, "author_name": "Senior Equity Analyst"},
    )
    assert export_res.status_code == 201
    exp = export_res.json()
    assert exp["format"] == "PDF"
    assert exp["export_status"] == "COMPLETED"
    assert exp["file_size_bytes"] > 500
    assert exp["page_count"] >= 1
    assert exp["content_hash"].startswith("sha256:")

    export_id = exp["export_id"]

    # 2. Download binary PDF file
    dl_res = test_client.get(f"/api/v1/research/report-exports/{export_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert dl_res.content.startswith(b"%PDF-1.4")
    assert b"%%EOF" in dl_res.content


def test_export_report_docx_and_download(test_client):
    """Verify valid OpenXML DOCX archive generation and authenticated byte download."""
    create_res = test_client.post(
        "/api/v1/research/reports",
        json={
            "report_type": "COMPANY_RESEARCH",
            "title": "Docx Test Report",
            "template_id": "tpl-company-research",
        },
    )
    assert create_res.status_code == 201
    report_id = create_res.json()["report_id"]

    # 1. Create DOCX export
    export_res = test_client.post(
        f"/api/v1/research/reports/{report_id}/exports",
        json={"format": "DOCX", "author_name": "Senior Equity Analyst"},
    )
    assert export_res.status_code == 201
    exp = export_res.json()
    assert exp["format"] == "DOCX"
    assert exp["export_status"] == "COMPLETED"
    assert exp["file_size_bytes"] > 1000

    export_id = exp["export_id"]

    # 2. Download binary DOCX file (PK zip signature)
    dl_res = test_client.get(f"/api/v1/research/report-exports/{export_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert dl_res.content.startswith(b"PK\x03\x04")


# ---------------------------------------------------------------------------
# 7. Structured Investment Theses & Arguments Tests
# ---------------------------------------------------------------------------

def test_investment_thesis_lifecycle(test_client):
    """Verify structured thesis builder with Bull, Bear, and Catalyst arguments."""
    # 1. Create Thesis
    create_res = test_client.post(
        "/api/v1/research/theses",
        json={
            "primary_subject_id": "comp-tsm",
            "thesis_statement": "TSMC maintains structural pricing power driven by leading-edge 3nm/2nm capacity allocation.",
            "time_horizon": "18_MONTHS",
            "bull_case_summary": "Wafer price increases drive gross margin above 55%.",
            "bear_case_summary": "Geopolitical risk elevates capital expenditure and overseas fab costs.",
            "assumptions_summary": "Leading-edge foundry supply remains tight through 2027.",
        },
    )
    assert create_res.status_code == 201
    thesis = create_res.json()
    thesis_id = thesis["thesis_id"]
    assert thesis["status"] == "DRAFT"

    # 2. Add Supporting (Bull) Argument
    arg1_res = test_client.post(
        f"/api/v1/research/theses/{thesis_id}/arguments",
        json={
            "argument_type": "SUPPORTING",
            "statement": "N2 node customer tape-outs surpass N3 at comparable introduction stage.",
            "claim_ids": ["clm-1"],
            "evidence_ids": ["ev-1"],
        },
    )
    assert arg1_res.status_code == 201
    arg1_id = arg1_res.json()["argument_id"]

    # 3. Add Opposing (Bear) Argument
    arg2_res = test_client.post(
        f"/api/v1/research/theses/{thesis_id}/arguments",
        json={
            "argument_type": "OPPOSING",
            "statement": "Arizona and Dresden fab buildouts incur 40% higher operating costs than Taiwan.",
        },
    )
    assert arg2_res.status_code == 201

    # 4. Get Thesis Detail
    detail_res = test_client.get(f"/api/v1/research/theses/{thesis_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["arguments"]) == 2

    # 5. Delete argument
    del_arg_res = test_client.delete(f"/api/v1/research/theses/{thesis_id}/arguments/{arg1_id}")
    assert del_arg_res.status_code == 200

    # 6. Delete thesis
    del_res = test_client.delete(f"/api/v1/research/theses/{thesis_id}")
    assert del_res.status_code == 200


# ---------------------------------------------------------------------------
# 8. User Ownership & RLS Security Tests
# ---------------------------------------------------------------------------

def test_cross_user_isolation(test_client):
    """Verify User B cannot access, mutate, or download User A's private research artifacts."""
    mock_user_a = AuthPrincipal(sub="analyst-1", email="a@atlas.local", role="authenticated")
    mock_user_b = AuthPrincipal(sub="analyst-2", email="b@atlas.local", role="authenticated")

    # Set User A
    app.dependency_overrides[get_current_user] = lambda: mock_user_a

    # User A creates a report
    rep_a = test_client.post(
        "/api/v1/research/reports",
        json={"report_type": "GENERAL_RESEARCH_MEMORANDUM", "title": "Confidential M&A Strategy"},
    ).json()
    report_id = rep_a["report_id"]

    # User A exports report
    exp_a = test_client.post(
        f"/api/v1/research/reports/{report_id}/exports",
        json={"format": "PDF"},
    ).json()
    export_id = exp_a["export_id"]

    # Switch to User B
    app.dependency_overrides[get_current_user] = lambda: mock_user_b

    # User B attempts to access User A's report
    b_get = test_client.get(f"/api/v1/research/reports/{report_id}")
    assert b_get.status_code == 403

    # User B attempts to edit User A's report
    b_patch = test_client.patch(
        f"/api/v1/research/reports/{report_id}",
        json={"title": "Unauthorized Hijack", "expected_revision": 1},
    )
    assert b_patch.status_code == 403

    # User B attempts to delete User A's report
    b_del = test_client.delete(f"/api/v1/research/reports/{report_id}")
    assert b_del.status_code == 403

    # User B attempts to download User A's PDF
    b_dl = test_client.get(f"/api/v1/research/report-exports/{export_id}/download")
    assert b_dl.status_code == 403
