"""Unit, Integration, and Security Tests for Stage 105:
Institutional Financial Research Source Discovery, Document Intelligence and Evidence Extraction.
"""

import pytest
from atlas.auth import AuthPrincipal
from atlas.research.repository import ResearchRepository
from atlas.research.service import ResearchService, get_research_service
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app

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
# 1. Advanced Research Source Discovery Tests
# ---------------------------------------------------------------------------

def test_source_discovery_search_apple_filings(test_client):
    """Verify multi-facet discovery filtering by company and text query."""
    payload = {
        "text_query": "net sales",
        "entity_ids": ["AAPL"],
        "filing_types": ["10-K"],
        "limit": 10,
    }
    resp = test_client.post("/api/v1/research/sources/search", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_count"] >= 1
    assert len(data["hits"]) >= 1

    # Check top hit structure
    hit = data["hits"][0]
    assert hit["canonical_entity_id"] == "AAPL"
    assert hit["score"] > 0.0
    assert len(hit["matched_snippet"]) > 0


def test_source_discovery_empty_query_lists_all(test_client):
    """Empty query should list all available catalog sources matching facets."""
    payload = {
        "text_query": "",
        "limit": 20,
    }
    resp = test_client.post("/api/v1/research/sources/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] >= 5
    assert len(data["hits"]) >= 5


def test_source_types_taxonomy(test_client):
    """Verify source type taxonomy endpoint returns categories with descriptions."""
    resp = test_client.get("/api/v1/research/source-types")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] > 0
    type_names = [item["source_type"] for item in data["items"]]
    assert "ANNUAL_REPORT" in type_names
    assert "REGULATORY_FILING" in type_names
    assert "ECONOMIC_RELEASE" in type_names


# ---------------------------------------------------------------------------
# 2. Document Exploration & Processing Status Tests
# ---------------------------------------------------------------------------

def test_get_document_metadata_and_processing_status(test_client):
    """Verify document metadata and processing audit record."""
    doc_id = "src-filing-aapl-10k-2024"
    resp = test_client.get(f"/api/v1/research/documents/{doc_id}")
    assert resp.status_code == 200
    doc_data = resp.json()
    assert doc_data["source_reference_id"] == doc_id
    assert doc_data["canonical_entity_id"] == "AAPL"

    # Processing status
    status_resp = test_client.get(f"/api/v1/research/documents/{doc_id}/processing-status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["canonical_document_id"] == "0000320193-24-000106"
    assert status_data["source_reference_id"] == doc_id
    assert status_data["processing_status"] == "COMPLETED"
    assert status_data["extracted_section_count"] >= 4
    assert status_data["extracted_table_count"] >= 1


def test_get_document_outline_and_sections(test_client):
    """Verify hierarchical outline navigation and section text retrieval."""
    doc_id = "src-filing-aapl-10k-2024"
    outline_resp = test_client.get(f"/api/v1/research/documents/{doc_id}/outline")
    assert outline_resp.status_code == 200
    outline_data = outline_resp.json()
    assert outline_data["total_sections"] >= 4
    assert len(outline_data["sections"]) >= 4

    # List sections
    sections_resp = test_client.get(f"/api/v1/research/documents/{doc_id}/sections")
    assert sections_resp.status_code == 200
    sections = sections_resp.json()
    assert len(sections) >= 4

    # Retrieve specific section
    sec_id = "sec-aapl-2024-item7"
    sec_resp = test_client.get(f"/api/v1/research/documents/{doc_id}/sections/{sec_id}")
    assert sec_resp.status_code == 200
    sec_data = sec_resp.json()
    assert sec_data["section_id"] == sec_id
    assert "MD&A" in sec_data["heading"] or "Item 7" in sec_data["heading"]
    assert len(sec_data["text_preview"]) > 50


def test_search_within_document(test_client):
    """Verify in-document search produces exact snippets and character span locations."""
    doc_id = "src-filing-aapl-10k-2024"
    payload = {
        "query": "iPhone",
        "limit": 5,
    }
    resp = test_client.post(f"/api/v1/research/documents/{doc_id}/search", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_matches"] >= 1
    hit = data["hits"][0]
    assert hit["section_id"] is not None
    assert "iPhone" in hit["snippet"]


# ---------------------------------------------------------------------------
# 3. Financial Table Extraction Tests
# ---------------------------------------------------------------------------

def test_document_tables_extraction(test_client):
    """Verify structured financial table rows, columns, scale, and currency."""
    doc_id = "src-filing-aapl-10k-2024"
    tables_resp = test_client.get(f"/api/v1/research/documents/{doc_id}/tables")
    assert tables_resp.status_code == 200
    tables_data = tables_resp.json()
    assert tables_data["total_count"] >= 1

    # Check operations table
    table_id = "tbl-aapl-2024-operations"
    table_resp = test_client.get(f"/api/v1/research/documents/{doc_id}/tables/{table_id}")
    assert table_resp.status_code == 200
    tbl = table_resp.json()
    assert tbl["table_id"] == table_id
    assert tbl["currency"] == "USD"
    assert tbl["unit_scale"] == "MILLIONS"
    assert len(tbl["headers"]) >= 3
    assert len(tbl["cells"]) >= 3
    # Check cell values
    assert "Total net sales" in tbl["cells"][0][0]


# ---------------------------------------------------------------------------
# 4. Evidence Candidates & Location Resolution Tests
# ---------------------------------------------------------------------------

def test_evidence_candidates_listing(test_client):
    """Verify listing pre-extracted candidates for a document."""
    doc_id = "src-filing-aapl-10k-2024"
    resp = test_client.post(f"/api/v1/research/evidence/candidates?document_id={doc_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] >= 2
    cand = data["items"][0]
    assert cand["canonical_document_id"] == "0000320193-24-000106"
    assert cand["extracted_text"] is not None


def test_resolve_source_location_anchor(test_client):
    """Verify source location validation anchor."""
    # Valid anchor
    valid_payload = {
        "source_reference_id": "src-filing-aapl-10k-2024",
        "location_type": "SECTION",
        "location_reference": "Item 7",
        "section_name": "Item 7",
    }
    resp = test_client.post("/api/v1/research/evidence/resolve-location", json=valid_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert len(data["context_snippet"]) > 0

    # Nonexistent document anchor
    invalid_payload = {
        "source_reference_id": "nonexistent-doc-999",
        "location_type": "PAGE",
        "location_reference": "page-999",
    }
    resp_invalid = test_client.post("/api/v1/research/evidence/resolve-location", json=invalid_payload)
    assert resp_invalid.status_code == 200
    data_inv = resp_invalid.json()
    assert data_inv["is_valid"] is False
    assert data_inv["error_message"] is not None


def test_convert_candidate_to_evidence(test_client):
    """Verify promoting an evidence candidate into Stage 104 ResearchEvidence for an investigation."""
    # Create investigation first
    inv_payload = {
        "title": "Apple Hardware & Services Margin Analysis FY2024",
        "research_type": "COMPANY_RESEARCH",
        "primary_subject_entity_id": "AAPL",
    }
    inv_resp = test_client.post("/api/v1/research/investigations", json=inv_payload)
    assert inv_resp.status_code == 201
    inv_id = inv_resp.json()["investigation_id"]

    # Fetch candidate dynamically from repository pool
    cand_resp = test_client.post("/api/v1/research/evidence/candidates?document_id=src-filing-aapl-10k-2024")
    assert cand_resp.status_code == 200
    cands = cand_resp.json()["items"]
    assert len(cands) > 0
    candidate = cands[0]
    cand_id = candidate["candidate_id"]

    # Convert candidate
    convert_payload = {
        "investigation_id": inv_id,
        "candidate_id": cand_id,
    }
    conv_resp = test_client.post("/api/v1/research/evidence/convert-candidate", json=convert_payload)
    assert conv_resp.status_code == 201
    ev_data = conv_resp.json()
    assert ev_data["investigation_id"] == inv_id
    assert ev_data["source_reference_id"] == "src-filing-aapl-10k-2024"

    # Verify evidence appears in investigation list
    list_resp = test_client.get(f"/api/v1/research/investigations/{inv_id}/evidence")
    assert list_resp.status_code == 200
    assert list_resp.json()["total_count"] == 1


# ---------------------------------------------------------------------------
# 5. Two-Document Comparison Tests
# ---------------------------------------------------------------------------

def test_compare_two_filings_section_diff(test_client):
    """Verify comparing Apple FY2023 Form 10-K with FY2024 Form 10-K produces unified diffs."""
    payload = {
        "left_document_id": "src-filing-aapl-10k-2023",
        "right_document_id": "src-filing-aapl-10k-2024",
        "comparison_mode": "FULL_TEXT",
    }
    resp = test_client.post("/api/v1/research/documents/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["left_document_id"] == "0000320193-23-000106"
    assert data["right_document_id"] == "0000320193-24-000106"
    assert len(data["section_diffs"]) >= 3

    # Check for MD&A diff
    mda_diff = next((d for d in data["section_diffs"] if "MD&A" in d["section_name"] or "Item 7" in d["section_name"]), None)
    assert mda_diff is not None
    assert mda_diff["alignment_status"] == "MATCHED"
    assert mda_diff["added_lines_count"] > 0
    assert mda_diff["removed_lines_count"] > 0


def test_compare_financial_facts_variance(test_client):
    """Verify numerical variance calculation between FY 2023 and FY 2024."""
    payload = {
        "entity_id": "AAPL",
        "left_period": "FY 2023",
        "right_period": "FY 2024",
    }
    resp = test_client.post("/api/v1/research/financial-facts/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_concepts_compared"] >= 1
    assert len(data["fact_diffs"]) >= 1

    # Check Net Sales / Revenue comparison
    rev_diff = data["fact_diffs"][0]
    assert rev_diff["currency"] == "USD"
    assert rev_diff["absolute_delta"] != 0.0
    assert rev_diff["percentage_delta"] is not None
    assert rev_diff["compatibility_status"] == "COMPATIBLE"


# ---------------------------------------------------------------------------
# 6. Error & Security Tests
# ---------------------------------------------------------------------------

def test_document_not_found_returns_404(test_client):
    """Requesting non-existent document yields 404."""
    resp = test_client.get("/api/v1/research/documents/nonexistent-id-999")
    assert resp.status_code == 404


def test_compare_incompatible_documents(test_client):
    """Comparing non-existent document in compare endpoint yields 404."""
    payload = {
        "left_document_id": "src-filing-aapl-10k-2023",
        "right_document_id": "nonexistent-doc-xyz",
    }
    resp = test_client.post("/api/v1/research/documents/compare", json=payload)
    assert resp.status_code == 404
