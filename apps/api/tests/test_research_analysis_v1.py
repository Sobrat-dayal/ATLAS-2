"""Institutional-Grade Financial Research Analysis & Hypothesis Evaluation Tests (Stage 106).

Comprehensive verification covering:
1. Analysis type registry taxonomy
2. Specification validation and temporal eligibility
3. Research Analysis CRUD, optimistic locking revision control, and duplication
4. Analysis Run execution, source manifest, and calculation provenance
5. Quantitative financial metrics: period deltas, CAGR, percentage growth, and safe division
6. Peer group benchmarking and cross-sectional quartile statistics
7. Macroeconomic time-series alignment
8. Deterministic hypothesis evaluation (criteria met, criteria not met, mixed results, evidence links)
9. Research findings lifecycle, review status, and limitation disclosures
10. Analyst assumption management and what-if sensitivity scenario matrices
11. Safe AST formula evaluator security checks (zero division, prohibited execution)
12. Strict user ownership isolation and RLS access control
"""

import pytest
from atlas.auth import AuthPrincipal
from atlas.research.analysis.calculations import (
    SafeExpressionEvaluator,
    calculate_mean,
    calculate_median,
    calculate_pearson_correlation,
    calculate_quartiles,
    calculate_standard_deviation,
    compute_cagr,
    compute_percentage_growth,
)
from atlas.research.errors import (
    ResearchAnalysisDivisionByZeroError,
    ResearchAnalysisFormulaInvalidError,
)
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
    """FastAPI TestClient with overridden get_research_service and mock authenticated user A."""
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
def test_client_user_b(clean_research_service):
    """FastAPI TestClient with overridden get_research_service and mock authenticated user B."""
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
# 1. Calculation Unit Tests
# ---------------------------------------------------------------------------

def test_arithmetic_growth_and_cagr_protections():
    """Verify safe percentage growth and CAGR calculations."""
    # Normal positive growth
    assert compute_percentage_growth(110.0, 100.0) == 10.0
    # Normal negative growth
    assert compute_percentage_growth(90.0, 100.0) == -10.0
    # Zero baseline returns None (preventing division by zero or infinite growth)
    assert compute_percentage_growth(50.0, 0.0) is None
    # None input returns None
    assert compute_percentage_growth(100.0, None) is None

    # Valid CAGR over 4 years: 100 to 146.41 is 10%
    cagr = compute_cagr(100.0, 146.41, 4)
    assert cagr is not None
    assert abs(cagr - 10.0) < 0.01

    # Invalid CAGR: negative endpoint or non-positive baseline
    assert compute_cagr(-50.0, 100.0, 3) is None
    assert compute_cagr(100.0, -50.0, 3) is None
    assert compute_cagr(0.0, 100.0, 3) is None
    assert compute_cagr(100.0, 100.0, 0) is None


def test_descriptive_and_correlation_statistics():
    """Verify sample and population statistics, quartiles, and Pearson correlation."""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert calculate_mean(values) == 30.0
    assert calculate_median(values) == 30.0
    assert calculate_standard_deviation(values, is_sample=True) is not None

    q1, q3 = calculate_quartiles(values)
    assert q1 is not None and q3 is not None
    assert q1 < q3

    # Perfect correlation
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    corr = calculate_pearson_correlation(x, y)
    assert corr is not None
    assert abs(corr - 1.0) < 1e-4

    # Zero variance correlation guard
    z = [5.0, 5.0, 5.0, 5.0, 5.0]
    assert calculate_pearson_correlation(x, z) is None


def test_safe_expression_evaluator_security():
    """Ensure safe arithmetic evaluator strictly forbids eval, builtins, and division by zero."""
    evaluator = SafeExpressionEvaluator()

    # Valid arithmetic expression
    res = evaluator.evaluate("revenue * 0.30 + other_income", {"revenue": 1000.0, "other_income": 50.0})
    assert res == 350.0

    # Zero division
    with pytest.raises(ResearchAnalysisDivisionByZeroError):
        evaluator.evaluate("revenue / 0", {"revenue": 1000.0})

    # Prohibited functions/builtins
    with pytest.raises(ResearchAnalysisFormulaInvalidError):
        evaluator.evaluate("__import__('os').system('ls')", {})

    with pytest.raises(ResearchAnalysisFormulaInvalidError):
        evaluator.evaluate("eval('2 + 2')", {})


# ---------------------------------------------------------------------------
# 2. Analysis Types Taxonomy & Specification Validation
# ---------------------------------------------------------------------------

def test_analysis_types_catalog(test_client):
    """Verify catalog of institutional analysis types."""
    res = test_client.get("/api/v1/research/analysis-types")
    assert res.status_code == 200
    data = res.json()
    assert "analysis_types" in data
    assert data["total_count"] >= 10

    types_list = [t["type_id"] for t in data["analysis_types"]]
    assert "COMPANY_FINANCIAL_TREND" in types_list
    assert "COMPANY_RATIO_ANALYSIS" in types_list
    assert "PEER_BENCHMARKING" in types_list
    assert "MACROECONOMIC_TIME_SERIES" in types_list


def test_validate_analysis_specification(test_client):
    """Verify specification pre-execution validation endpoint."""
    # Valid specification
    valid_payload = {
        "specification": {
            "analysis_type": "COMPANY_FINANCIAL_TREND",
            "primary_entity_id": "AAPL",
            "metric_ids": ["operating_income"],
            "frequency": "ANNUAL",
            "input_version_policy": "PINNED_SOURCE_VERSION",
            "outlier_policy": "INCLUDE_ALL",
            "methodology_version": 1,
        }
    }
    res = test_client.post("/api/v1/research/analyses/validate", json=valid_payload)
    assert res.status_code == 200
    body = res.json()
    assert body["is_valid"] is True
    assert len(body["errors"]) == 0
    assert body["estimated_observation_count"] > 0

    # Invalid specification (missing primary entity)
    invalid_payload = {
        "specification": {
            "analysis_type": "COMPANY_FINANCIAL_TREND",
            "primary_entity_id": "",
            "metric_ids": [],
            "frequency": "ANNUAL",
            "input_version_policy": "PINNED_SOURCE_VERSION",
            "outlier_policy": "INCLUDE_ALL",
            "methodology_version": 1,
        }
    }
    res_inv = test_client.post("/api/v1/research/analyses/validate", json=invalid_payload)
    assert res_inv.status_code == 200
    body_inv = res_inv.json()
    assert body_inv["is_valid"] is False
    assert len(body_inv["errors"]) > 0


# ---------------------------------------------------------------------------
# 3. Analysis CRUD, Concurrency, and Duplication
# ---------------------------------------------------------------------------

def test_analysis_crud_and_optimistic_concurrency(test_client):
    """Test analysis creation, reading, revision-safe updating, duplication, and deletion."""
    create_payload = {
        "title": "Alphabet Inc. Capital Structure & Operating Margins",
        "description": "Multi-year trend analysis of Google operational efficiency and debt coverage.",
        "analysis_type": "COMPANY_FINANCIAL_TREND",
        "research_objective": "Determine whether operating margins have remained above 25% post-reorganization.",
        "primary_subject_entity_id": "GOOGL",
        "primary_subject_type": "COMPANY",
        "secondary_entity_ids": ["MSFT", "AAPL"],
        "specification": {
            "analysis_type": "COMPANY_FINANCIAL_TREND",
            "primary_entity_id": "GOOGL",
            "secondary_entity_ids": ["MSFT", "AAPL"],
            "metric_ids": ["operating_income", "revenue"],
            "frequency": "ANNUAL",
            "input_version_policy": "PINNED_SOURCE_VERSION",
            "outlier_policy": "INCLUDE_ALL",
            "currency": "USD",
            "methodology_version": 1,
        },
        "linked_question_ids": [],
        "linked_hypothesis_ids": [],
    }

    # 1. Create Analysis
    res_create = test_client.post("/api/v1/research/analyses", json=create_payload)
    assert res_create.status_code == 201
    analysis = res_create.json()
    analysis_id = analysis["analysis_id"]
    assert analysis["current_revision"] == 1
    assert analysis["owner_user_id"] == "analyst-1"

    # 2. Read Analysis
    res_get = test_client.get(f"/api/v1/research/analyses/{analysis_id}")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == create_payload["title"]

    # 3. Update Analysis with correct expected_revision
    update_payload = {
        "expected_revision": 1,
        "title": "Alphabet Inc. Capital Structure & Operating Margins (Updated)",
        "description": "Updated description with latest FY24 notes.",
    }
    res_upd = test_client.patch(f"/api/v1/research/analyses/{analysis_id}", json=update_payload)
    assert res_upd.status_code == 200
    updated = res_upd.json()
    assert updated["current_revision"] == 2
    assert updated["title"] == update_payload["title"]

    # 4. Update with stale revision -> 409 Conflict
    stale_payload = {
        "expected_revision": 1,  # Stale, should be 2
        "title": "Stale edit attempt",
    }
    res_stale = test_client.patch(f"/api/v1/research/analyses/{analysis_id}", json=stale_payload)
    assert res_stale.status_code == 409

    # 5. Duplicate Analysis
    res_dup = test_client.post(f"/api/v1/research/analyses/{analysis_id}/duplicate")
    assert res_dup.status_code == 201
    dup_analysis = res_dup.json()
    assert dup_analysis["analysis_id"] != analysis_id
    assert "Copy" in dup_analysis["title"]
    assert dup_analysis["current_revision"] == 1

    # 6. Delete Analysis
    res_del = test_client.delete(f"/api/v1/research/analyses/{analysis_id}")
    assert res_del.status_code == 200
    # Confirm deletion
    res_missing = test_client.get(f"/api/v1/research/analyses/{analysis_id}")
    assert res_missing.status_code == 404


def test_analysis_list_and_facets(test_client):
    """Verify list endpoint with facet filters."""
    res = test_client.get("/api/v1/research/analyses")
    assert res.status_code == 200
    data = res.json()
    assert "analyses" in data
    assert data["total_count"] >= 2


# ---------------------------------------------------------------------------
# 4. Analysis Execution, Runs, Results & Provenance
# ---------------------------------------------------------------------------

def test_execute_company_financial_trend_run(test_client):
    """Verify executing an institutional financial trend run over genuine 10-K data."""
    # Use seeded analysis "an-aapl-margin-trend"
    res_run = test_client.post(
        "/api/v1/research/analyses/an-aapl-margin-trend/runs?input_policy=PINNED_SOURCE_VERSION"
    )
    assert res_run.status_code == 201
    run = res_run.json()
    run_id = run["run_id"]
    assert run["execution_status"] == "COMPLETED"
    assert run["observations_count"] == 5

    # Fetch run results
    res_result = test_client.get(f"/api/v1/research/analysis-runs/{run_id}/results")
    assert res_result.status_code == 200
    result = res_result.json()
    assert result["primary_subject_id"] == "AAPL"
    assert result["metric_id"] == "operating_income"
    assert len(result["observations"]) == 5

    # Check CAGR and summary statistics
    stats = result["summary_statistics"]
    assert stats["sample_size_n"] == 5
    assert stats["cagr_percentage"] is not None
    assert abs(stats["cagr_percentage"] - 16.75) < 0.1

    # Verify source data manifest contains exact Form 10-K accession numbers
    manifest = result["source_data_manifest"]
    assert len(manifest) == 5
    assert any("0000320193-20-000096" in item.get("accession", "") for item in manifest)

    # Check provenance inspector endpoint
    res_prov = test_client.get(f"/api/v1/research/analysis-runs/{run_id}/provenance")
    assert res_prov.status_code == 200
    prov = res_prov.json()
    assert "formula_definitions" in prov
    assert "source_manifest" in prov


def test_peer_benchmarking_execution(test_client):
    """Verify cross-sectional peer benchmarking and quartile calculations."""
    res_run = test_client.post(
        "/api/v1/research/analyses/an-aapl-peer-benchmark/runs"
    )
    assert res_run.status_code == 201
    run = res_run.json()
    assert run["observations_count"] == 8

    res_result = test_client.get(f"/api/v1/research/analysis-runs/{run['run_id']}/results")
    assert res_result.status_code == 200
    result = res_result.json()
    stats = result["summary_statistics"]
    assert stats["sample_size_n"] == 8
    # Peer median margin
    assert stats["median"] is not None
    assert abs(stats["median"] - 20.70) < 0.1
    # Comparability warnings preserved
    assert len(result["comparability_warnings"]) > 0


# ---------------------------------------------------------------------------
# 5. Hypothesis Evaluation Engine
# ---------------------------------------------------------------------------

def test_deterministic_hypothesis_evaluation(test_client):
    """Verify deterministic criteria evaluation against an analytical run."""
    eval_payload = {
        "analysis_run_id": "run-aapl-margin-01",
        "criteria": {
            "metric_id": "operating_income",
            "operator": "GTE",
            "threshold_value": 60000.0,
            "required_periods_count": 5,
            "allow_missing": False,
        },
        "eligible_universe": ["AAPL"],
    }

    # Evaluate against seeded hypothesis "hyp-aapl-01"
    res_eval = test_client.post(
        "/api/v1/research/hypotheses/hyp-aapl-01/evaluations",
        json=eval_payload,
    )
    assert res_eval.status_code == 201
    ev = res_eval.json()
    # Operating income was >= 60,000 across all 5 years (66.2B, 108.9B, 119.4B, 114.3B, 123.1B)
    assert ev["result_status"] == "CRITERIA_MET"
    assert len(ev["supporting_evidence_ids"]) == 5
    assert len(ev["contradicting_evidence_ids"]) == 0

    # Now evaluate with a threshold that fails (threshold = 120,000)
    fail_payload = {
        "analysis_run_id": "run-aapl-margin-01",
        "criteria": {
            "metric_id": "operating_income",
            "operator": "GTE",
            "threshold_value": 120000.0,
            "required_periods_count": 5,
            "allow_missing": False,
        },
        "eligible_universe": ["AAPL"],
    }
    res_fail = test_client.post(
        "/api/v1/research/hypotheses/hyp-aapl-01/evaluations",
        json=fail_payload,
    )
    assert res_fail.status_code == 201
    ev_fail = res_fail.json()
    # Only FY2024 is >= 120,000 -> MIXED_RESULTS
    assert ev_fail["result_status"] == "MIXED_RESULTS"
    assert len(ev_fail["supporting_evidence_ids"]) == 1
    assert len(ev_fail["contradicting_evidence_ids"]) == 4

    # List evaluation history
    res_hist = test_client.get("/api/v1/research/hypotheses/hyp-aapl-01/evaluations")
    assert res_hist.status_code == 200
    assert len(res_hist.json()["evaluations"]) >= 2


# ---------------------------------------------------------------------------
# 6. Research Findings Workspace
# ---------------------------------------------------------------------------

def test_research_findings_lifecycle(test_client):
    """Verify finding creation, citation linking, optimistic concurrency, and listing."""
    create_finding = {
        "analysis_id": "an-aapl-margin-trend",
        "analysis_run_id": "run-aapl-margin-01",
        "finding_type": "CALCULATED_RESULT",
        "statement": "Apple Inc. operating cash flow exceeded $100B in 4 out of the last 5 reported fiscal years.",
        "methodology_description": "Direct derivation from SEC Form 10-K Item 8 Consolidated Statements of Cash Flows.",
        "supporting_evidence_ids": ["ev-aapl-opinc-01"],
        "contradicting_evidence_ids": [],
        "calculated_result_references": {"min_operating_cf": 80674.0, "max_operating_cf": 122151.0},
        "limitations": ["Cash flow statements prepared under U.S. GAAP."],
    }

    res_post = test_client.post(
        "/api/v1/research/analyses/an-aapl-margin-trend/findings",
        json=create_finding,
    )
    assert res_post.status_code == 201
    finding = res_post.json()
    finding_id = finding["finding_id"]
    assert finding["review_status"] == "DRAFT"
    assert finding["revision"] == 1

    # Update review status
    update_finding = {
        "expected_revision": 1,
        "review_status": "READY_FOR_REVIEW",
        "statement": "Apple Inc. operating cash flow exceeded $100B in 4 out of 5 fiscal years (FY2021-FY2024).",
    }
    res_patch = test_client.patch(f"/api/v1/research/findings/{finding_id}", json=update_finding)
    assert res_patch.status_code == 200
    assert res_patch.json()["revision"] == 2
    assert res_patch.json()["review_status"] == "READY_FOR_REVIEW"

    # List findings
    res_list = test_client.get(
        "/api/v1/research/analyses/an-aapl-margin-trend/findings"
    )
    assert res_list.status_code == 200
    assert res_list.json()["total_count"] >= 2

    # Delete finding
    res_del = test_client.delete(f"/api/v1/research/findings/{finding_id}")
    assert res_del.status_code == 200


# ---------------------------------------------------------------------------
# 7. Assumptions & Scenario Sensitivity Workspace
# ---------------------------------------------------------------------------

def test_assumptions_and_sensitivity_scenarios(test_client):
    """Verify explicit analyst assumptions and deterministic sensitivity matrices."""
    # Create an assumption
    assump_payload = {
        "label": "Custom Terminal Growth Rate",
        "parameter_id": "terminal_growth",
        "value": 3.5,
        "unit": "%",
        "source_type": "ANALYST_ASSUMED",
        "analyst_note": "Long-term inflation plus real GDP anchor assumption.",
    }
    res_assump = test_client.post(
        "/api/v1/research/analyses/an-aapl-margin-trend/assumptions",
        json=assump_payload,
    )
    assert res_assump.status_code == 201
    assump = res_assump.json()
    assump_id = assump["assumption_id"]

    # List assumptions
    res_list = test_client.get(
        "/api/v1/research/analyses/an-aapl-margin-trend/assumptions"
    )
    assert res_list.status_code == 200
    assert res_list.json()["total_count"] >= 3

    # Execute deterministic sensitivity matrix
    scen_payload = {
        "base_metric_value": 391035.0,  # Apple FY24 revenue
        "metric_name": "Revenue",
        "unit": "$M",
        "growth_rates": [-0.05, 0.0, 0.05, 0.10],
        "margin_rates": [0.30, 0.32, 0.34],
    }
    res_scen = test_client.post(
        "/api/v1/research/analyses/an-aapl-margin-trend/scenarios/sensitivity",
        json=scen_payload,
    )
    assert res_scen.status_code == 200
    matrix_res = res_scen.json()
    assert matrix_res["is_non_predictive_illustrative"] is True
    assert "qualification_notice" in matrix_res
    # Matrix dimensions: 4 rows (growth rates) x 3 columns (margin rates)
    assert len(matrix_res["scenario_matrix"]) == 4
    assert len(matrix_res["scenario_matrix"][0]) == 3

    # At 0.0% growth and 0.30 margin: 391035 * 1.0 * 0.30 = 117,310.5
    val_zero_growth_30_margin = matrix_res["scenario_matrix"][1][0]
    assert abs(val_zero_growth_30_margin - 117310.5) < 1.0

    # Delete assumption
    res_del = test_client.delete(f"/api/v1/research/assumptions/{assump_id}")
    assert res_del.status_code == 200


# ---------------------------------------------------------------------------
# 8. User Ownership & RLS Isolation
# ---------------------------------------------------------------------------

def test_user_ownership_and_rls_isolation(test_client):
    """Verify that private analyses created by User A cannot be accessed or manipulated by User B."""
    mock_user_a = AuthPrincipal(
        sub="analyst-1",
        email="analyst1@atlas-research.local",
        role="authenticated",
    )
    mock_user_b = AuthPrincipal(
        sub="analyst-2",
        email="analyst2@atlas-research.local",
        role="authenticated",
    )

    create_payload = {
        "title": "Confidential Alpha Semiconductor Analysis",
        "description": "Private thesis on chip margin compression.",
        "analysis_type": "COMPANY_FINANCIAL_TREND",
        "primary_subject_entity_id": "NVDA",
        "specification": {
            "analysis_type": "COMPANY_FINANCIAL_TREND",
            "primary_entity_id": "NVDA",
            "metric_ids": ["gross_profit"],
            "frequency": "ANNUAL",
            "methodology_version": 1,
        },
    }

    # User A creates analysis
    app.dependency_overrides[get_current_user] = lambda: mock_user_a
    res_a = test_client.post("/api/v1/research/analyses", json=create_payload)
    assert res_a.status_code == 201
    analysis_id = res_a.json()["analysis_id"]

    # Switch identity to User B
    app.dependency_overrides[get_current_user] = lambda: mock_user_b

    # User B attempts to access -> 403 Forbidden
    res_b_get = test_client.get(f"/api/v1/research/analyses/{analysis_id}")
    assert res_b_get.status_code == 403

    # User B attempts to update -> 403 Forbidden
    res_b_patch = test_client.patch(
        f"/api/v1/research/analyses/{analysis_id}",
        json={"expected_revision": 1, "title": "Tampered Title"},
    )
    assert res_b_patch.status_code == 403

    # User B attempts to delete -> 403 Forbidden
    res_b_del = test_client.delete(f"/api/v1/research/analyses/{analysis_id}")
    assert res_b_del.status_code == 403

    # User B attempts to execute run -> 403 Forbidden
    res_b_run = test_client.post(f"/api/v1/research/analyses/{analysis_id}/runs")
    assert res_b_run.status_code == 403

    # Restore User A for subsequent tests if any
    app.dependency_overrides[get_current_user] = lambda: mock_user_a
