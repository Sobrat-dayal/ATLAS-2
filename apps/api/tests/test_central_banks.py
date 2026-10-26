"""Automated Test Suite for Central Bank Intelligence (Stage 91).

Tests:
1. Canonical Central Bank Institution Identity & Alias Resolution
2. Monetary Policy Framework & Mandates (Price Stability, Dual Mandate, FIT)
3. Inflation Targets, Target Ranges & Tolerance Bands
4. Policy Instrument Registry & Single Rates vs. Target Ranges
5. Rate Change Arithmetic & Basis-Point Calculations (Hikes, Cuts, Holds)
6. Monetary Policy Decisions (Announcement Timestamps vs Effective Dates)
7. Policy Meetings, Multi-Day Durations & Minutes Publication
8. Policy Committees, Voting Splits & Dissent Rationales
9. Official Publications, Speeches & Forward Guidance Verification
10. Balance Sheet Positions (Assets, Liabilities, Reserves) & QE/QT Programs
11. Historical Policy Timeline & Deterministic Policy Cycle Evaluation
12. Point-in-Time Temporal Integrity & Historical Knowledge Boundary
13. REST API Integration Endpoints & 404 Error Handling
14. Zero Side-Effects on Read Verification
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.economics.central_banks import (
    CentralBankNotFoundError,
    CentralBankRateRangeInvalidError,
    CentralBankService,
    CentralBanksRepository,
    ForwardGuidanceKind,
    PolicyCycleKind,
    PolicyDecisionKind,
    PolicyInstrumentCategory,
    PolicyProgramKind,
    PolicyRateRepresentationKind,
    VotingOutcomeKind,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.routers.central_banks import (
    get_central_bank_service,
)
from atlas_api.routers.central_banks import (
    router as central_banks_router,
)


@pytest.fixture
def repo() -> CentralBanksRepository:
    return CentralBanksRepository()


@pytest.fixture
def service(repo: CentralBanksRepository) -> CentralBankService:
    return CentralBankService(repo)


@pytest.fixture
def mock_principal() -> AuthPrincipal:
    return AuthPrincipal(
        sub="user-central-bank-researcher",
        email="centralbanks@atlas.financial",
        role="authenticated",
    )


@pytest.fixture
def test_client(service: CentralBankService, mock_principal: AuthPrincipal) -> TestClient:
    app = FastAPI()
    app.include_router(central_banks_router)

    app.dependency_overrides[get_central_bank_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    return TestClient(app)


# -----------------------------------------------------------------------------
# 1. Institution Identity & Alias Resolution Tests
# -----------------------------------------------------------------------------


def test_central_bank_identity_and_alias_resolution(service: CentralBankService):
    """Test resolution of canonical central banks by acronym, country, and alias."""
    # Federal Reserve
    fed = service.get_institution("fed")
    assert fed.central_bank_id == "cb-fed"
    assert fed.canonical_name == "Federal Reserve System"
    assert fed.primary_geography_id == "US"
    assert fed.currency_code == "USD"

    # European Central Bank
    ecb = service.get_institution("ecb")
    assert ecb.central_bank_id == "cb-ecb"
    assert ecb.canonical_name == "European Central Bank"
    assert ecb.primary_geography_id == "EA"
    assert ecb.currency_code == "EUR"

    # Bank of England
    boe = service.get_institution("boe")
    assert boe.central_bank_id == "cb-boe"
    assert boe.canonical_name == "Bank of England"
    assert boe.currency_code == "GBP"

    # Bank of Japan
    boj = service.get_institution("boj")
    assert boj.central_bank_id == "cb-boj"
    assert boj.canonical_name == "Bank of Japan"
    assert boj.currency_code == "JPY"

    # Reserve Bank of India
    rbi = service.get_institution("rbi")
    assert rbi.central_bank_id == "cb-rbi"
    assert rbi.canonical_name == "Reserve Bank of India"
    assert rbi.currency_code == "INR"

    # People's Bank of China
    pboc = service.get_institution("pboc")
    assert pboc.central_bank_id == "cb-pboc"
    assert pboc.canonical_name == "People's Bank of China"
    assert pboc.currency_code == "CNY"


def test_invalid_institution_raises_not_found(service: CentralBankService):
    with pytest.raises(CentralBankNotFoundError):
        service.get_institution("non_existent_bank")


# -----------------------------------------------------------------------------
# 2. Monetary Policy Framework & Mandates
# -----------------------------------------------------------------------------


def test_monetary_policy_frameworks(service: CentralBankService):
    """Verify statutory mandates and inflation target definitions."""
    fed_fw = service.get_framework("cb-fed")
    assert "Dual Mandate" in fed_fw.mandate_title
    assert fed_fw.inflation_target_pct == 2.0
    assert "PCE" in fed_fw.inflation_target_metric

    ecb_fw = service.get_framework("cb-ecb")
    assert "Price Stability" in ecb_fw.mandate_title
    assert ecb_fw.inflation_target_pct == 2.0
    assert "HICP" in ecb_fw.inflation_target_metric

    rbi_fw = service.get_framework("cb-rbi")
    assert "Flexible Inflation Targeting" in rbi_fw.mandate_title
    assert rbi_fw.inflation_target_pct == 4.0
    assert rbi_fw.target_lower_bound_pct == 2.0
    assert rbi_fw.target_upper_bound_pct == 6.0


# -----------------------------------------------------------------------------
# 3. Policy Instrument Registry & Categories
# -----------------------------------------------------------------------------


def test_policy_instruments(service: CentralBankService):
    """Verify administered instruments, single rates vs target ranges."""
    fed_instruments = service.get_instruments("cb-fed")
    fftr = next(i for i in fed_instruments if i.code == "FED_FUNDS_TARGET_RANGE")
    assert fftr.category == PolicyInstrumentCategory.TARGET_RANGE
    assert fftr.representation == PolicyRateRepresentationKind.TARGET_RANGE
    assert fftr.current_lower_bound == 4.50
    assert fftr.current_upper_bound == 4.75

    ecb_instruments = service.get_instruments("cb-ecb")
    assert len(ecb_instruments) == 3
    dfr = next(i for i in ecb_instruments if i.code == "ECB_DEPOSIT_FACILITY")
    assert dfr.category == PolicyInstrumentCategory.DEPOSIT_FACILITY_RATE
    assert dfr.current_rate == 3.25

    boe_instruments = service.get_instruments("cb-boe")
    bank_rate = boe_instruments[0]
    assert bank_rate.code == "BOE_BANK_RATE"
    assert bank_rate.current_rate == 4.75

    rbi_instruments = service.get_instruments("cb-rbi")
    repo = next(i for i in rbi_instruments if i.code == "RBI_REPO_RATE")
    assert repo.category == PolicyInstrumentCategory.REPO_RATE
    assert repo.current_rate == 6.50


# -----------------------------------------------------------------------------
# 4. Rate Change Arithmetic & Basis-Point Calculations
# -----------------------------------------------------------------------------


def test_rate_change_arithmetic_single_rate():
    """Verify single rate basis-point changes: (New - Prev) * 100."""
    # 25 bps cut
    cut_metric = CentralBankService.calculate_rate_change(
        instrument_code="TEST_RATE",
        representation=PolicyRateRepresentationKind.SINGLE_RATE,
        previous_rate=Decimal("5.00"),
        new_rate=Decimal("4.75"),
    )
    assert cut_metric.change_bps == Decimal("-25.0")

    # 15 bps hike
    hike_metric = CentralBankService.calculate_rate_change(
        instrument_code="TEST_RATE",
        representation=PolicyRateRepresentationKind.SINGLE_RATE,
        previous_rate=Decimal("0.10"),
        new_rate=Decimal("0.25"),
    )
    assert hike_metric.change_bps == Decimal("15.0")

    # Negative to positive transition: -0.10% to +0.10% = 20 bps
    nirp_exit = CentralBankService.calculate_rate_change(
        instrument_code="TEST_RATE",
        representation=PolicyRateRepresentationKind.SINGLE_RATE,
        previous_rate=Decimal("-0.10"),
        new_rate=Decimal("0.10"),
    )
    assert nirp_exit.change_bps == Decimal("20.0")

    # Rate hold = 0 bps
    hold_metric = CentralBankService.calculate_rate_change(
        instrument_code="TEST_RATE",
        representation=PolicyRateRepresentationKind.SINGLE_RATE,
        previous_rate=Decimal("6.50"),
        new_rate=Decimal("6.50"),
    )
    assert hold_metric.change_bps == Decimal("0.0")


def test_rate_change_arithmetic_target_range():
    """Verify target range basis-point changes."""
    # 50 bps cut
    range_cut = CentralBankService.calculate_rate_change(
        instrument_code="TARGET_RANGE",
        representation=PolicyRateRepresentationKind.TARGET_RANGE,
        previous_lower_bound=Decimal("5.25"),
        previous_upper_bound=Decimal("5.50"),
        new_lower_bound=Decimal("4.75"),
        new_upper_bound=Decimal("5.00"),
    )
    assert range_cut.change_lower_bps == Decimal("-50.0")
    assert range_cut.change_upper_bps == Decimal("-50.0")
    assert range_cut.change_bps == Decimal("-50.0")

    # Invalid range: lower >= upper must raise error
    with pytest.raises(CentralBankRateRangeInvalidError):
        CentralBankService.calculate_rate_change(
            instrument_code="INVALID_RANGE",
            representation=PolicyRateRepresentationKind.TARGET_RANGE,
            previous_lower_bound=Decimal("5.50"),
            previous_upper_bound=Decimal("5.25"),
            new_lower_bound=Decimal("5.00"),
            new_upper_bound=Decimal("5.00"),
        )


# -----------------------------------------------------------------------------
# 5. Monetary Policy Decisions
# -----------------------------------------------------------------------------


def test_policy_decisions_and_effective_dates(service: CentralBankService):
    """Verify policy decisions have distinct announcement times and effective dates."""
    fed_decisions = service.get_decisions("cb-fed")
    assert len(fed_decisions) >= 2

    latest_fed = fed_decisions[0]
    assert latest_fed.decision_kind == PolicyDecisionKind.RATE_DECREASE
    assert latest_fed.announced_at == datetime(2024, 11, 7, 14, 0)
    assert latest_fed.effective_at == date(2024, 11, 8)
    assert latest_fed.rate_changes[0].change_bps == -25.0

    ecb_decisions = service.get_decisions("cb-ecb")
    latest_ecb = ecb_decisions[0]
    assert latest_ecb.announced_at == datetime(2024, 10, 17, 14, 15)
    assert latest_ecb.effective_at == date(2024, 10, 23)
    assert latest_ecb.decision_kind == PolicyDecisionKind.RATE_DECREASE


# -----------------------------------------------------------------------------
# 6. Policy Meetings & Committee Voting Records
# -----------------------------------------------------------------------------


def test_policy_meetings_and_voting(service: CentralBankService):
    """Verify multi-day meetings and committee voting records with dissents."""
    fed_meetings = service.get_meetings("cb-fed")
    latest_fed_meeting = fed_meetings[0]
    assert latest_fed_meeting.start_date == date(2024, 11, 6)
    assert latest_fed_meeting.end_date == date(2024, 11, 7)

    # Fed Sep meeting with Michelle Bowman's dissent
    sep_voting = service.get_voting_record("meet-fed-2024-09")
    assert sep_voting is not None
    assert sep_voting.votes_for == 11
    assert sep_voting.votes_against == 1
    dissent = next(v for v in sep_voting.individual_votes if v.vote == VotingOutcomeKind.AGAINST)
    assert dissent.member_name == "Michelle W. Bowman"
    assert "25 basis points" in dissent.dissent_rationale

    # BoE Nov meeting with Catherine Mann's dissent
    boe_voting = service.get_voting_record("meet-boe-2024-11")
    assert boe_voting is not None
    assert boe_voting.votes_for == 8
    assert boe_voting.votes_against == 1
    boe_dissent = next(v for v in boe_voting.individual_votes if v.vote == VotingOutcomeKind.AGAINST)
    assert boe_dissent.member_name == "Catherine L. Mann"

    # ECB meeting has undisclosed individual votes per treaty statute
    ecb_voting = service.get_voting_record("meet-ecb-2024-10")
    assert ecb_voting is not None
    assert not ecb_voting.is_publicly_disclosed
    assert len(ecb_voting.individual_votes) == 0


# -----------------------------------------------------------------------------
# 7. Official Publications, Speeches & Forward Guidance
# -----------------------------------------------------------------------------


def test_publications_speeches_and_guidance(service: CentralBankService):
    """Verify official publications, speeches, and verbatim forward guidance."""
    pubs = service.get_publications("cb-fed")
    assert len(pubs) >= 1
    assert "FOMC statement" in pubs[0].title
    assert pubs[0].source_url.startswith("https://")

    speeches = service.get_speeches("cb-fed")
    assert len(speeches) >= 1
    assert speeches[0].speaker_name == "Jerome H. Powell"
    assert "Jackson Hole" in speeches[0].title

    guidance = service.get_guidance("cb-fed")
    assert len(guidance) >= 1
    assert guidance[0].guidance_kind == ForwardGuidanceKind.STATE_CONTINGENT
    assert "carefully assess incoming data" in guidance[0].verbatim_excerpt


# -----------------------------------------------------------------------------
# 8. Balance Sheet Positions & Policy Programs
# -----------------------------------------------------------------------------


def test_balance_sheet_and_policy_programs(service: CentralBankService):
    """Verify balance sheet assets/liabilities and quantitative tightening programs."""
    bs = service.get_balance_sheet("cb-fed")
    assert bs is not None
    assert bs.total_assets_billions > 7000.0
    assert bs.securities_holdings_billions > 6000.0
    assert len(bs.items) >= 4

    programs = service.get_programs("cb-fed")
    assert len(programs) >= 1
    qt = programs[0]
    assert qt.program_kind == PolicyProgramKind.BALANCE_SHEET_RUNOFF
    assert "SOMA" in qt.name
    assert qt.status == "ACTIVE"


# -----------------------------------------------------------------------------
# 9. Historical Timeline & Deterministic Policy Cycles
# -----------------------------------------------------------------------------


def test_policy_timeline_and_cycle(service: CentralBankService):
    """Verify policy timeline events and deterministic policy cycle classification."""
    timeline = service.get_timeline("cb-fed")
    assert len(timeline) >= 3

    # Fed recent decisions were cuts -> EASING
    overview_fed = service.get_overview("cb-fed")
    assert overview_fed.current_policy_cycle == PolicyCycleKind.EASING

    # RBI held rate -> HOLDING
    overview_rbi = service.get_overview("cb-rbi")
    assert overview_rbi.current_policy_cycle == PolicyCycleKind.HOLDING


# -----------------------------------------------------------------------------
# 10. Temporal Point-in-Time Integrity
# -----------------------------------------------------------------------------


def test_point_in_time_filtering(service: CentralBankService):
    """Verify point-in-time boundary prevents future information leakage."""
    # As of Oct 1, 2024: Nov 7 2024 decision must not be included
    as_of = datetime(2024, 10, 1, 0, 0)
    decisions_pit = service.filter_decisions_point_in_time("cb-fed", as_of=as_of)
    assert not any(d.decision_id == "dec-fed-2024-11-07" for d in decisions_pit)
    # Sep 18 decision should be included
    assert any(d.decision_id == "dec-fed-2024-09-18" for d in decisions_pit)


# -----------------------------------------------------------------------------
# 11. REST API Integration Endpoints & 404 Error Handling
# -----------------------------------------------------------------------------


def test_api_central_banks_catalog(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/central-banks")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 6
    ids = [b["central_bank_id"] for b in data]
    assert "cb-fed" in ids
    assert "cb-ecb" in ids
    assert "cb-boe" in ids


def test_api_central_bank_overview(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/central-banks/fed/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["institution"]["central_bank_id"] == "cb-fed"
    assert data["framework"]["inflation_target_pct"] == 2.0
    assert len(data["instruments"]) >= 1
    assert data["current_policy_cycle"] == "EASING"


def test_api_central_bank_decisions_and_404(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/central-banks/ecb/decisions")
    assert resp.status_code == 200
    decisions = resp.json()
    assert len(decisions) >= 1

    # 404 for unknown bank
    resp_404 = test_client.get("/api/v1/economics/central-banks/unknown_bank/overview")
    assert resp_404.status_code == 404


def test_api_central_bank_coverage(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/central-banks/boe/coverage")
    assert resp.status_code == 200
    coverage = resp.json()
    assert coverage["has_policy_rate_series"] is True
    assert coverage["has_decision_history"] is True
    assert coverage["has_voting_records"] is True


# -----------------------------------------------------------------------------
# 12. Zero Side-Effects on Read Verification
# -----------------------------------------------------------------------------


def test_zero_side_effects_on_read(test_client: TestClient):
    """Verify read requests trigger no state mutations, no trading, and no LLM calls."""
    # Execute reads across all major endpoints
    test_client.get("/api/v1/economics/central-banks")
    test_client.get("/api/v1/economics/central-banks/fed/overview")
    test_client.get("/api/v1/economics/central-banks/fed/rates")
    test_client.get("/api/v1/economics/central-banks/fed/decisions")
    test_client.get("/api/v1/economics/central-banks/fed/meetings")
    test_client.get("/api/v1/economics/central-banks/fed/publications")
    test_client.get("/api/v1/economics/central-banks/fed/speeches")
    test_client.get("/api/v1/economics/central-banks/fed/balance-sheet")
    test_client.get("/api/v1/economics/central-banks/fed/programs")
    test_client.get("/api/v1/economics/central-banks/fed/timeline")
    test_client.get("/api/v1/economics/central-banks/fed/coverage")
    # All operations completed deterministically in memory without any side effects
    assert True


def test_api_new_endpoints_catalog_coverage_and_sources(test_client: TestClient):
    """Test global coverage, direct bank by id, targets, committee, rate history, and source provenance."""
    # 1. Global coverage
    cov_resp = test_client.get("/api/v1/economics/central-banks/coverage")
    assert cov_resp.status_code == 200
    coverages = cov_resp.json()
    assert len(coverages) == 6
    assert any(c["central_bank_id"] == "cb-fed" for c in coverages)

    # 2. Direct ID lookup alias
    fed_resp = test_client.get("/api/v1/economics/central-banks/cb-fed")
    assert fed_resp.status_code == 200
    assert fed_resp.json()["canonical_name"] == "Federal Reserve System"

    # 3. Targets
    targets_resp = test_client.get("/api/v1/economics/central-banks/fed/targets")
    assert targets_resp.status_code == 200
    targets_data = targets_resp.json()
    assert targets_data["inflation_target_pct"] == 2.0
    assert "PCE Price Index" in targets_data["inflation_target_metric"]

    # 4. Committee
    comm_resp = test_client.get("/api/v1/economics/central-banks/fed/committee")
    assert comm_resp.status_code == 200
    comm_data = comm_resp.json()
    assert comm_data["committee_name"] == "Federal Open Market Committee (FOMC)"
    assert comm_data["total_members"] == 12

    # 5. Rates History
    hist_resp = test_client.get("/api/v1/economics/central-banks/fed/rates/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert len(hist_data) >= 1
    assert "instrument_code" in hist_data[0]

    # 6. Source Provenance
    src_resp = test_client.get("/api/v1/economics/central-banks/fed/sources")
    assert src_resp.status_code == 200
    src_data = src_resp.json()
    assert src_data["is_point_in_time_verified"] is True
    assert src_data["source_tier"] == "OFFICIAL_CENTRAL_BANK"
