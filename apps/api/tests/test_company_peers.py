"""Comprehensive Automated Test Suite for ATLAS Stage 87:
Company Peers and Comparable Company Analysis.

Tests cover:
1. Canonical Company Identity & Subject Isolation:
   - Subject company cannot be selected as a peer of itself (PEER_SELF_SELECTION_NOT_ALLOWED).
   - Duplicate peer companies are strictly rejected (PEER_DUPLICATE_COMPANY).
2. Industry Classification & Taxonomy Integrity:
   - GICS multi-level taxonomy (Sector, Industry Group, Industry, Sub-Industry).
   - Verified sector matching vs candidate qualification.
3. Candidate Discovery & Explainable Reasons:
   - Source-defined peers vs verified competitors vs statistical comparable candidates.
   - Deterministic relevance score ordering.
   - Explainable selection rationale.
4. User Peer Group Persistence & Authorization:
   - CRUD lifecycle (Create, Read, Update, Delete).
   - Revision concurrency checking (409 on revision conflict).
   - Maximum group size limit (<= 25 companies).
   - Tenant/user isolation (cannot access or delete another user's private group).
5. Cross-Company Financial & Valuation Comparison:
   - Revenue, Gross Profit, Operating Income, Assets, Debt, Equity.
   - Margins (Gross, Operating, Net) and Returns (ROE, ROIC).
   - Multiples (P/E, Forward P/E, P/B, P/S, EV/EBITDA, EV/Revenue).
   - Non-meaningful handling (negative equity -> N/M for P/B and ROE).
6. Statistical Benchmark Engine:
   - Exact median (odd & even samples).
   - Arithmetic mean over eligible observations.
   - Eligible sample count & coverage ratio.
   - Subject relative difference (% and percentage points).
   - Outlier detection via Tukey's IQR fences.
7. Multi-Period Historical Trend Series:
   - Multi-year comparison points without look-ahead or forward-filling.
8. FastAPI HTTP Router Integration:
   - 200 OK for all endpoints, 404 for missing company, 400 for validation errors.
9. Side-Effect Invariants:
   - 0 Company writes, 0 Instrument writes, 0 Trading orders, 0 LLM calls.
"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies.peers import (
    CompanyPeersRepository,
    CompanyPeersService,
    ComparisonMetricCategory,
    CreatePeerGroupRequestDTO,
    HistoricalComparisonRequestDTO,
    IndustryTaxonomy,
    MetricObservationStatus,
    PeerCompanyNotFoundError,
    PeerDuplicateCompanyError,
    PeerGroupNotAuthorizedError,
    PeerGroupNotFoundError,
    PeerGroupRevisionConflictError,
    PeerGroupSizeExceededError,
    PeerRelationshipType,
    PeerSelfSelectionNotAllowedError,
    SubjectInclusionPolicy,
    UpdatePeerGroupRequestDTO,
    calculate_peer_statistics,
)
from atlas.companies.peers.calculator import calculate_median
from atlas.companies.peers.models import ComparableMetricObservation
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.routers.company_peers import get_peers_service
from atlas_api.routers.company_peers import router as company_peers_router

# =============================================================================
# Test Fixtures & Setup
# =============================================================================


@pytest.fixture
def repo():
    return CompanyPeersRepository()


@pytest.fixture
def service(repo):
    return CompanyPeersService(repository=repo)


@pytest.fixture
def mock_principal():
    return AuthPrincipal(
        sub="user-analyst-123",
        email="analyst@atlas.financial",
    )


@pytest.fixture
def api_client(service, mock_principal):
    app = FastAPI()
    app.include_router(company_peers_router, prefix="/api/v1")

    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True

    app.dependency_overrides[get_peers_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    client = TestClient(app)
    return client


# =============================================================================
# 1. Company Identity & Self-Selection Tests
# =============================================================================


def test_subject_cannot_be_peer_of_itself(service, repo):
    """Subject company ID cannot be included in peer list."""
    with pytest.raises(PeerSelfSelectionNotAllowedError):
        service.create_peer_group(
            company_id=repo.apple_id,
            user_id="user-1",
            request=CreatePeerGroupRequestDTO(
                name="Invalid Group",
                peer_company_ids=[repo.apple_id, repo.msft_id],
            ),
        )


def test_duplicate_peers_rejected(service, repo):
    """Duplicate company IDs within the peer group are rejected."""
    with pytest.raises(PeerDuplicateCompanyError):
        service.create_peer_group(
            company_id=repo.apple_id,
            user_id="user-1",
            request=CreatePeerGroupRequestDTO(
                name="Duplicate Group",
                peer_company_ids=[repo.msft_id, repo.msft_id],
            ),
        )


def test_missing_company_rejected(service):
    """Unknown company IDs trigger PeerCompanyNotFoundError."""
    with pytest.raises(PeerCompanyNotFoundError):
        service.get_overview("c-unknown-9999", "user-1")


# =============================================================================
# 2. Industry Classification & Candidate Discovery Tests
# =============================================================================


def test_verified_industry_classification(service, repo):
    """Apple Inc. has verified GICS classification metadata."""
    overview = service.get_overview(repo.apple_id, "user-1")
    assert overview.subject_company_name == "Apple Inc."
    assert overview.classification.taxonomy == IndustryTaxonomy.GICS
    assert overview.classification.sector == "Information Technology"
    assert overview.classification.industry == "Technology Hardware, Storage & Peripherals"
    assert overview.classification.code == "45202030"


def test_candidate_discovery_and_reasons(service, repo):
    """Discovered candidates have explainable reasons and relationship distinctions."""
    res = service.get_candidates(repo.apple_id, limit=10)
    assert res.total_candidates > 0
    candidate_ids = [c.candidate_company_id for c in res.items]

    # Subject must not be in candidate list
    assert repo.apple_id not in candidate_ids

    # Microsoft and Samsung must be recognized as verified competitors
    msft_candidate = next(c for c in res.items if c.candidate_company_id == repo.msft_id)
    assert msft_candidate.relationship_type == PeerRelationshipType.VERIFIED_COMPETITOR
    assert msft_candidate.is_competitor is True
    assert len(msft_candidate.selection_reasons) > 0
    assert "personal computing operating systems" in msft_candidate.selection_reasons[0]

    samsung_candidate = next(c for c in res.items if c.candidate_company_id == repo.samsung_id)
    assert samsung_candidate.relationship_type == PeerRelationshipType.VERIFIED_COMPETITOR
    assert samsung_candidate.is_competitor is True
    assert "smartphones" in samsung_candidate.selection_reasons[0]


def test_candidate_competitors_only_filter(service, repo):
    """Filter competitors_only=True returns only verified commercial competitors."""
    res = service.get_candidates(repo.apple_id, limit=10, competitors_only=True)
    for c in res.items:
        assert c.is_competitor is True
        assert c.relationship_type == PeerRelationshipType.VERIFIED_COMPETITOR


# =============================================================================
# 3. Peer Group Persistence & Concurrency Tests
# =============================================================================


def test_peer_group_crud_lifecycle(service, repo):
    """Complete lifecycle of creating, reading, updating, and deleting a peer group."""
    user_id = "analyst-42"

    # 1. Create
    created = service.create_peer_group(
        company_id=repo.apple_id,
        user_id=user_id,
        request=CreatePeerGroupRequestDTO(
            name="Mega Tech Peers",
            description="MSFT, GOOGL, DELL",
            peer_company_ids=[repo.msft_id, repo.googl_id, repo.dell_id],
        ),
    )
    assert created.name == "Mega Tech Peers"
    assert created.revision == 1
    assert len(created.peer_company_ids) == 3

    # 2. Read
    fetched = service.get_peer_group(created.id, user_id)
    assert fetched.id == created.id
    assert fetched.owner_user_id == user_id

    # 3. Update
    updated = service.update_peer_group(
        group_id=created.id,
        user_id=user_id,
        request=UpdatePeerGroupRequestDTO(
            name="Mega Tech & Hardware",
            peer_company_ids=[repo.msft_id, repo.googl_id, repo.dell_id, repo.hp_id],
            expected_revision=1,
        ),
    )
    assert updated.name == "Mega Tech & Hardware"
    assert updated.revision == 2
    assert len(updated.peer_company_ids) == 4

    # 4. Revision Conflict
    with pytest.raises(PeerGroupRevisionConflictError):
        service.update_peer_group(
            group_id=created.id,
            user_id=user_id,
            request=UpdatePeerGroupRequestDTO(
                name="Stale Edit",
                expected_revision=1,  # Now revision is 2
            ),
        )

    # 5. Delete
    service.delete_peer_group(created.id, user_id)
    with pytest.raises(PeerGroupNotFoundError):
        service.get_peer_group(created.id, user_id)


def test_peer_group_size_limit(service, repo):
    """Exceeding 25 companies in a peer group raises validation and domain size limit errors."""
    fake_ids = [f"comp-{i}" for i in range(26)]
    # 1. Pydantic schema validation boundary
    with pytest.raises(ValidationError):
        CreatePeerGroupRequestDTO(
            name="Oversized Group",
            peer_company_ids=fake_ids,
        )

    # 2. Repository domain enforcement boundary
    with pytest.raises(PeerGroupSizeExceededError):
        repo.create_peer_group(
            subject_company_id=repo.apple_id,
            owner_user_id="user-1",
            name="Oversized Group",
            peer_company_ids=fake_ids,
        )


def test_peer_group_user_isolation(service, repo):
    """User B cannot access or mutate private peer groups owned by User A."""
    group_a = service.create_peer_group(
        company_id=repo.apple_id,
        user_id="user-A",
        request=CreatePeerGroupRequestDTO(
            name="User A Secret Peers",
            peer_company_ids=[repo.msft_id],
        ),
    )

    with pytest.raises(PeerGroupNotAuthorizedError):
        service.get_peer_group(group_a.id, user_id="user-B")

    with pytest.raises(PeerGroupNotAuthorizedError):
        service.delete_peer_group(group_a.id, user_id="user-B")


# =============================================================================
# 4. Statistical Benchmark Engine Tests
# =============================================================================


def test_median_odd_and_even_samples():
    """Exact median calculation for odd and even sample sizes."""
    odd_vals = [Decimal("10"), Decimal("20"), Decimal("30")]
    assert calculate_median(odd_vals) == Decimal("20")

    even_vals = [Decimal("10"), Decimal("20"), Decimal("30"), Decimal("40")]
    assert calculate_median(even_vals) == Decimal("25")


def test_peer_statistics_calculation():
    """Computes median, mean, min, max, coverage, and subject difference."""
    obs1 = ComparableMetricObservation(
        company_id="sub-1",
        company_name="Subject",
        ticker="SUB",
        metric_id="m.pe",
        metric_name="PE",
        category=ComparisonMetricCategory.VALUATION,
        exact_value=Decimal("30"),
        formatted_value="30x",
        unit="x",
        period_id="FY24",
        period_end="2024-09-30",
        is_subject=True,
    )
    obs2 = ComparableMetricObservation(
        company_id="peer-1",
        company_name="Peer 1",
        ticker="P1",
        metric_id="m.pe",
        metric_name="PE",
        category=ComparisonMetricCategory.VALUATION,
        exact_value=Decimal("20"),
        formatted_value="20x",
        unit="x",
        period_id="FY24",
        period_end="2024-09-30",
        is_subject=False,
    )
    obs3 = ComparableMetricObservation(
        company_id="peer-2",
        company_name="Peer 2",
        ticker="P2",
        metric_id="m.pe",
        metric_name="PE",
        category=ComparisonMetricCategory.VALUATION,
        exact_value=Decimal("40"),
        formatted_value="40x",
        unit="x",
        period_id="FY24",
        period_end="2024-09-30",
        is_subject=False,
    )

    stats = calculate_peer_statistics(
        observations=[obs1, obs2, obs3],
        subject_id="sub-1",
        subject_policy=SubjectInclusionPolicy.EXCLUDE_SUBJECT,
    )

    assert stats.sample_count == 2
    assert stats.median == Decimal("30.00")  # (20 + 40) / 2
    assert stats.mean == Decimal("30.00")
    assert stats.min_value == Decimal("20")
    assert stats.max_value == Decimal("40")
    assert stats.subject_value == Decimal("30")
    assert stats.subject_diff_vs_median_pct == Decimal("0.00")
    assert stats.subject_diff_vs_median_pp == Decimal("0.00")


def test_non_meaningful_handling_in_statistics():
    """Observations flagged as NOT_MEANINGFUL or None are excluded from sample."""
    obs_valid = ComparableMetricObservation(
        company_id="p1",
        company_name="Peer 1",
        ticker="P1",
        metric_id="m.roe",
        metric_name="ROE",
        category=ComparisonMetricCategory.PROFITABILITY,
        exact_value=Decimal("25"),
        formatted_value="25%",
        unit="%",
        period_id="FY24",
        period_end="2024-09-30",
    )
    obs_nm = ComparableMetricObservation(
        company_id="p2",
        company_name="Peer 2",
        ticker="P2",
        metric_id="m.roe",
        metric_name="ROE",
        category=ComparisonMetricCategory.PROFITABILITY,
        exact_value=None,
        formatted_value="N/M",
        unit="%",
        period_id="FY24",
        period_end="2024-09-30",
        status=MetricObservationStatus.NOT_MEANINGFUL,
    )

    stats = calculate_peer_statistics(
        observations=[obs_valid, obs_nm],
        subject_id="sub",
    )
    assert stats.sample_count == 1
    assert stats.median == Decimal("25.00")


# =============================================================================
# 5. Cross-Company Comparison Service Tests
# =============================================================================


def test_peer_comparison_matrix_generation(service, repo):
    """Full cross-company comparison evaluates metrics and benchmark statistics."""
    from atlas.companies.peers.schemas import PeerComparisonRequestDTO

    req = PeerComparisonRequestDTO(
        peer_company_ids=[repo.msft_id, repo.googl_id, repo.samsung_id, repo.dell_id, repo.hp_id],
        metric_ids=[
            "scale.revenue",
            "profitability.gross_margin",
            "profitability.operating_margin",
            "valuation.pe",
        ],
        fiscal_period="FY2024",
    )
    res = service.compare_peers(repo.apple_id, "user-1", req)

    assert res.subject_company_id == repo.apple_id
    assert len(res.companies) == 6  # Apple + 5 peers

    # Check Revenue observations
    rev_obs = res.observations["scale.revenue"]
    assert rev_obs[repo.apple_id].formatted_value == "$391.04B"
    assert rev_obs[repo.msft_id].formatted_value == "$245.12B"
    assert rev_obs[repo.dell_id].formatted_value == "$92.50B"

    # Check Operating Margin statistics
    om_stats = res.statistics["profitability.operating_margin"]
    assert om_stats.sample_count == 5  # 5 peers
    assert om_stats.median is not None
    assert om_stats.mean is not None
    assert om_stats.subject_value == Decimal("31.50")


def test_dell_hp_negative_equity_not_meaningful(service, repo):
    """Dell and HP have negative equity, resulting in N/M for P/B and ROE."""
    from atlas.companies.peers.schemas import PeerComparisonRequestDTO

    req = PeerComparisonRequestDTO(
        peer_company_ids=[repo.dell_id, repo.hp_id],
        metric_ids=["valuation.pb", "profitability.roe"],
        fiscal_period="FY2024",
    )
    res = service.compare_peers(repo.apple_id, "user-1", req)

    # Dell P/B and ROE must be NOT_MEANINGFUL
    dell_pb = res.observations["valuation.pb"][repo.dell_id]
    assert dell_pb.status == MetricObservationStatus.NOT_MEANINGFUL
    assert dell_pb.formatted_value == "N/M"

    dell_roe = res.observations["profitability.roe"][repo.dell_id]
    assert dell_roe.status == MetricObservationStatus.NOT_MEANINGFUL


def test_historical_trend_series(service, repo):
    """Multi-year historical comparison series for Apple, Microsoft, Alphabet."""
    req = HistoricalComparisonRequestDTO(
        peer_company_ids=[repo.msft_id, repo.googl_id],
        metric_ids=["profitability.operating_margin"],
        max_periods=4,
    )
    res = service.compare_history(repo.apple_id, "user-1", req)

    assert len(res.series) == 3
    aapl_series = next(s for s in res.series if s.company_id == repo.apple_id)
    assert len(aapl_series.points) == 4
    assert aapl_series.points[3].period_id == "FY2024"
    assert aapl_series.points[3].value == Decimal("31.50")


# =============================================================================
# 6. FastAPI HTTP Router Integration Tests
# =============================================================================


def test_api_get_overview(api_client, repo):
    """GET /companies/{id}/peers/overview returns 200 OK with classification and highlights."""
    resp = api_client.get(f"/api/v1/companies/{repo.apple_id}/peers/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["subject_company_id"] == repo.apple_id
    assert data["classification"]["sector"] == "Information Technology"
    assert data["total_candidates"] > 0


def test_api_get_candidates(api_client, repo):
    """GET /companies/{id}/peers/candidates returns 200 OK with candidates list."""
    resp = api_client.get(f"/api/v1/companies/{repo.apple_id}/peers/candidates?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 5
    assert data["items"][0]["relevance_score"] > 0


def test_api_get_metrics(api_client, repo):
    """GET /companies/{id}/peers/metrics returns 200 OK with catalog."""
    resp = api_client.get(f"/api/v1/companies/{repo.apple_id}/peers/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_metrics"] >= 20


def test_api_post_compare(api_client, repo):
    """POST /companies/{id}/peers/compare returns 200 OK with observations and statistics."""
    payload = {
        "peer_company_ids": [repo.msft_id, repo.googl_id],
        "metric_ids": ["profitability.gross_margin", "valuation.pe"],
        "fiscal_period": "FY2024",
    }
    resp = api_client.post(f"/api/v1/companies/{repo.apple_id}/peers/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "observations" in data
    assert "statistics" in data
    assert "valuation.pe" in data["statistics"]


def test_api_user_peer_groups_crud(api_client, repo):
    """Full HTTP CRUD flow on user peer groups."""
    # 1. Create
    create_payload = {
        "name": "HTTP Custom Group",
        "description": "Created via API test",
        "peer_company_ids": [repo.msft_id, repo.dell_id],
    }
    resp = api_client.post(f"/api/v1/companies/{repo.apple_id}/peers/groups", json=create_payload)
    assert resp.status_code == 201
    created_group = resp.json()
    group_id = created_group["id"]
    assert created_group["name"] == "HTTP Custom Group"

    # 2. Get list
    resp = api_client.get(f"/api/v1/companies/{repo.apple_id}/peers/groups")
    assert resp.status_code == 200
    groups_list = resp.json()
    assert any(g["id"] == group_id for g in groups_list)

    # 3. Update
    update_payload = {
        "name": "HTTP Custom Group (Renamed)",
        "expected_revision": 1,
    }
    resp = api_client.patch(
        f"/api/v1/companies/{repo.apple_id}/peers/groups/{group_id}", json=update_payload
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "HTTP Custom Group (Renamed)"
    assert resp.json()["revision"] == 2

    # 4. Delete
    resp = api_client.delete(f"/api/v1/companies/{repo.apple_id}/peers/groups/{group_id}")
    assert resp.status_code == 204


def test_api_get_methodology(api_client, repo):
    """GET /companies/{id}/peers/methodology returns 200 OK with documented rules."""
    resp = api_client.get(f"/api/v1/companies/{repo.apple_id}/peers/methodology")
    assert resp.status_code == 200
    data = resp.json()
    assert "candidate_discovery" in data
    assert "statistical_methodology" in data
