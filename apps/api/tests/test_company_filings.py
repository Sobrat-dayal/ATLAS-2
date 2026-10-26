"""Unit and Integration Tests for Regulatory Company Filings Intelligence (Stage 86)."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies.filings import (
    CompanyFilingsRepository,
    CompanyFilingsService,
    FilingCategory,
    Regulator,
    XBRLUnitType,
    compare_regulatory_filings,
    extract_plain_text_from_html,
    sanitize_filing_html,
)
from atlas.companies.filings.sanitizer import defuse_xxe_payload
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.main import app
from atlas_api.routers.company_filings import get_filings_service

# ---------------------------------------------------------------------------
# 1. Repository & Identity Tests
# ---------------------------------------------------------------------------

def test_filings_repository_apple_catalog():
    repo = CompanyFilingsRepository()
    filings = repo.get_filings_by_company(repo.apple_company_id)

    assert len(filings) >= 6
    accessions = [f.accession_number for f in filings]
    assert "0000320193-24-000106" in accessions  # 10-K
    assert "0000320193-24-000115" in accessions  # 10-K/A
    assert "0000320193-24-000081" in accessions  # 10-Q
    assert "0000320193-24-000105" in accessions  # 8-K
    assert "0000320193-24-000006" in accessions  # DEF 14A

    # Verify Apple CIK
    for f in filings:
        if f.filer_cik == repo.apple_cik:
            assert f.filer_cik == "0000320193"
            assert f.regulator == Regulator.SEC_EDGAR


def test_filings_taxonomy_and_categories():
    repo = CompanyFilingsRepository()
    apple_id = repo.apple_company_id

    annuals = repo.get_filings_by_company(apple_id, category=FilingCategory.ANNUAL_REPORTS)
    assert len(annuals) >= 2  # 10-K and 10-K/A
    assert all(f.category == FilingCategory.ANNUAL_REPORTS for f in annuals)

    quarterlies = repo.get_filings_by_company(apple_id, category=FilingCategory.QUARTERLY_REPORTS)
    assert len(quarterlies) >= 1
    assert quarterlies[0].form_type == "10-Q"

    currents = repo.get_filings_by_company(apple_id, category=FilingCategory.CURRENT_REPORTS)
    assert len(currents) >= 1
    assert currents[0].form_type == "8-K"

    proxies = repo.get_filings_by_company(apple_id, category=FilingCategory.PROXY_STATEMENTS)
    assert len(proxies) >= 1
    assert proxies[0].form_type == "DEF 14A"


# ---------------------------------------------------------------------------
# 2. Security Sanitizer & Safe Extraction Tests
# ---------------------------------------------------------------------------

def test_html_sanitizer_disarms_scripts_and_events():
    malicious_html = """
    <html>
      <head>
        <script>alert('XSS execution');</script>
        <script src="https://evil.com/payload.js"></script>
      </head>
      <body onload="stealCookies()" onerror="sendData()">
        <h1>Apple Inc. Financial Statement</h1>
        <p><a href="javascript:alert(1)">Click for Report</a></p>
        <iframe src="https://phishing.site/login"></iframe>
        <table border="1">
          <tr><th>Item</th><th>Amount</th></tr>
          <tr><td>Revenue</td><td>$391,035M</td></tr>
        </table>
      </body>
    </html>
    """

    sanitized = sanitize_filing_html(malicious_html)

    # All active scripts and dangerous elements must be eliminated
    assert "<script" not in sanitized.lower()
    assert "alert(" not in sanitized
    assert "onload" not in sanitized.lower()
    assert "onerror" not in sanitized.lower()
    assert "<iframe" not in sanitized.lower()
    assert "javascript:" not in sanitized.lower()

    # Legitimate financial text and layout must be preserved
    assert "<h1>Apple Inc. Financial Statement</h1>" in sanitized
    assert "<table border=\"1\">" in sanitized
    assert "$391,035M" in sanitized


def test_xml_xxe_defuse():
    xxe_xml = """<?xml version="1.0"?>
    <!DOCTYPE test [
      <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <filing>
      <revenue>&xxe;</revenue>
    </filing>
    """
    defused = defuse_xxe_payload(xxe_xml)
    assert "<!DOCTYPE" not in defused
    assert "<!ENTITY" not in defused


def test_plain_text_extraction():
    sample_html = """
    <div>
      <h2>Item 1. Business</h2>
      <p>Apple Inc. designs, manufactures and markets smartphones.</p>
      <table>
        <tr><td>iPhone Sales</td><td>$201,183M</td></tr>
      </table>
    </div>
    """
    text = extract_plain_text_from_html(sample_html)
    assert "Item 1. Business" in text
    assert "Apple Inc. designs, manufactures" in text
    assert "iPhone Sales" in text
    assert "$201,183M" in text
    assert "<" not in text
    assert ">" not in text


# ---------------------------------------------------------------------------
# 3. XBRL Extraction & Fact Integrity Tests
# ---------------------------------------------------------------------------

def test_xbrl_facts_accuracy():
    repo = CompanyFilingsRepository()
    filing = repo.get_filing_by_accession("0000320193-24-000106")
    assert filing is not None

    facts_by_concept = {f.concept_name: f for f in filing.xbrl_facts}

    assert "Revenues" in facts_by_concept
    rev = facts_by_concept["Revenues"]
    assert rev.exact_value == Decimal("391035000000")
    assert rev.unit == XBRLUnitType.USD
    assert rev.taxonomy_namespace == "us-gaap"

    assert "NetIncomeLoss" in facts_by_concept
    net_inc = facts_by_concept["NetIncomeLoss"]
    assert net_inc.exact_value == Decimal("93736000000")

    assert "EarningsPerShareDiluted" in facts_by_concept
    eps = facts_by_concept["EarningsPerShareDiluted"]
    assert eps.exact_value == Decimal("6.08")
    assert eps.unit == XBRLUnitType.USD_PER_SHARE

    assert "CommonStockSharesOutstanding" in facts_by_concept
    shs = facts_by_concept["CommonStockSharesOutstanding"]
    assert shs.exact_value == Decimal("15115800000")
    assert shs.unit == XBRLUnitType.SHARES


# ---------------------------------------------------------------------------
# 4. Search Tests
# ---------------------------------------------------------------------------

def test_filings_search_functionality():
    service = CompanyFilingsService()
    apple_id = service.repository.apple_company_id

    # Search for "Services"
    resp = service.search_filings(apple_id, "Services")
    assert resp.total_hits > 0
    hit = resp.hits[0]
    assert hit.accession_number is not None
    assert "Services" in hit.matched_snippet or "services" in hit.matched_snippet.lower()
    assert hit.score > 0.0

    # Search for a financial value
    resp_val = service.search_filings(apple_id, "391,035")
    assert resp_val.total_hits > 0
    assert any("391,035" in h.matched_snippet for h in resp_val.hits)

    # Empty query produces 0 hits
    empty_resp = service.search_filings(apple_id, "")
    assert empty_resp.total_hits == 0


# ---------------------------------------------------------------------------
# 5. Amendment & Comparison Tests
# ---------------------------------------------------------------------------

def test_filing_comparison_amendment():
    service = CompanyFilingsService()
    f_orig = service.repository.get_filing_by_accession("0000320193-24-000106")
    f_amend = service.repository.get_filing_by_accession("0000320193-24-000115")
    assert f_orig is not None
    assert f_amend is not None

    res = compare_regulatory_filings(f_orig, f_amend)
    assert res.comparison_type == "AMENDMENT"
    assert res.left_accession == f_orig.accession_number
    assert res.right_accession == f_amend.accession_number
    assert res.total_text_changes > 0
    assert len(res.text_diff_sections) > 0


# ---------------------------------------------------------------------------
# 6. Service & Coverage Tests
# ---------------------------------------------------------------------------

def test_filings_service_coverage_and_provenance():
    service = CompanyFilingsService()
    apple_id = service.repository.apple_company_id

    coverage = service.get_filing_coverage(apple_id)
    assert coverage.total_filings >= 6
    assert "10-K" in coverage.forms_available
    assert "10-Q" in coverage.forms_available
    assert "8-K" in coverage.forms_available
    assert "10 requests/sec" in coverage.source_policy
    assert "ATLAS/2.0" in coverage.user_agent_configured

    f_10k = service.repository.get_filing_by_accession("0000320193-24-000106")
    source_ref = service.get_filing_source(f_10k.filing_id)
    assert source_ref.regulator == Regulator.SEC_EDGAR
    assert "sec.gov" in source_ref.official_url
    assert len(source_ref.content_hash) == 64  # SHA-256


# ---------------------------------------------------------------------------
# 7. FastAPI HTTP API Integration Tests
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    auth_user = AuthPrincipal(sub="usr_stage86_analyst", email="analyst@atlas.financial")
    app.dependency_overrides[get_current_user] = lambda: auth_user

    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    yield TestClient(app)
    app.dependency_overrides.clear()


def test_api_filings_catalog(api_client):
    service = get_filings_service()
    apple_id = service.repository.apple_company_id

    res = api_client.get(f"/api/v1/companies/{apple_id}/filings")
    assert res.status_code == 200
    data = res.json()
    assert data["company_id"] == apple_id
    assert data["total_count"] >= 6
    assert len(data["items"]) >= 6

    # Test category filter
    res_ann = api_client.get(
        f"/api/v1/companies/{apple_id}/filings",
        params={"category": FilingCategory.ANNUAL_REPORTS.value},
    )
    assert res_ann.status_code == 200
    data_ann = res_ann.json()
    assert all(item["category"] == FilingCategory.ANNUAL_REPORTS.value for item in data_ann["items"])


def test_api_filings_overview(api_client):
    service = get_filings_service()
    apple_id = service.repository.apple_company_id

    res = api_client.get(f"/api/v1/companies/{apple_id}/filings/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["company_id"] == apple_id
    assert data["latest_annual"]["form_type"] in ["10-K", "10-K/A"]
    assert data["latest_quarterly"]["form_type"] == "10-Q"


def test_api_filing_detail_and_content(api_client):
    service = get_filings_service()
    f_10k = service.repository.get_filing_by_accession("0000320193-24-000106")
    apple_id = service.repository.apple_company_id

    # Detail
    res_det = api_client.get(f"/api/v1/companies/{apple_id}/filings/{f_10k.filing_id}")
    assert res_det.status_code == 200
    det = res_det.json()
    assert det["accession_number"] == "0000320193-24-000106"
    assert len(det["documents"]) >= 3
    assert len(det["sections"]) >= 4

    # Documents list
    res_docs = api_client.get(f"/api/v1/companies/{apple_id}/filings/{f_10k.filing_id}/documents")
    assert res_docs.status_code == 200
    docs = res_docs.json()
    assert any(d["is_primary"] for d in docs)

    # Content
    res_cnt = api_client.get(f"/api/v1/companies/{apple_id}/filings/{f_10k.filing_id}/content")
    assert res_cnt.status_code == 200
    cnt = res_cnt.json()
    assert cnt["content_html"] is not None
    assert "<script" not in cnt["content_html"]
    assert "Apple Inc." in cnt["content_text"]


def test_api_filing_facts_xbrl(api_client):
    service = get_filings_service()
    f_10k = service.repository.get_filing_by_accession("0000320193-24-000106")
    apple_id = service.repository.apple_company_id

    res = api_client.get(f"/api/v1/companies/{apple_id}/filings/{f_10k.filing_id}/facts")
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] >= 10
    concepts = [f["concept_name"] for f in data["items"]]
    assert "Revenues" in concepts
    assert "NetIncomeLoss" in concepts


def test_api_filing_compare(api_client):
    service = get_filings_service()
    f_orig = service.repository.get_filing_by_accession("0000320193-24-000106")
    f_amend = service.repository.get_filing_by_accession("0000320193-24-000115")
    apple_id = service.repository.apple_company_id

    res = api_client.get(
        f"/api/v1/companies/{apple_id}/filings/compare",
        params={"left_id": f_orig.filing_id, "right_id": f_amend.filing_id},
    )
    assert res.status_code == 200
    comp = res.json()
    assert comp["comparison_type"] == "AMENDMENT"
    assert comp["total_text_changes"] > 0
