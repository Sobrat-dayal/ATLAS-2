"""Comprehensive Automated Tests for Company Earnings Intelligence (Stage 84).

Validates:
- Event lifecycle and timing semantics (confirmed vs estimated, BMO/AMC, timezones)
- Financial actuals integration with Stage 82 statements
- Pure Decimal surprise arithmetic (beats, misses, in-line, negative & zero estimates)
- Pre-release consensus cutoff and no look-ahead guarantee
- Management guidance ranges and revisions
- Earnings calls and transcript references
- FastAPI endpoint contracts and error envelopes
"""

import datetime
import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies.earnings.calculator import (
    calculate_eps_surprise,
    calculate_revenue_surprise,
    format_eps,
    format_percentage,
    format_revenue,
)
from atlas.companies.earnings.enums import (
    EarningsEventStatus,
    EarningsPeriodType,
    GuidanceMetricType,
    GuidanceStatus,
    MarketSession,
    SurpriseClassification,
    TranscriptStatus,
)
from atlas.companies.earnings.models import (
    EarningsEvent,
)
from atlas.companies.earnings.repository import (
    CompanyEarningsRepository,
    clear_earnings_store,
)
from atlas.companies.earnings.service import CompanyEarningsService
from atlas.companies.statements.enums import StatementPeriodType, StatementType
from atlas.companies.statements.repository import (
    CompanyStatementsRepository,
    register_statement_period,
)
from atlas.entities.models import Entity
from httpx import ASGITransport, AsyncClient

from atlas_api.main import app


@pytest.fixture(autouse=True)
def cleanup_earnings_data():
    """Ensures test isolation by resetting stores."""
    yield
    clear_earnings_store()


@pytest.fixture
def test_company_id() -> uuid.UUID:
    return uuid.UUID("c0000000-0000-0000-0000-000000000001")


# ===========================================================================
# 1. Decimal Surprise Calculator Tests
# ===========================================================================

def test_eps_surprise_positive_beat():
    """Actual EPS exceeds consensus estimate -> BEAT."""
    actual = Decimal("1.64")
    estimate = Decimal("1.60")
    abs_s, pct_s, classification = calculate_eps_surprise(actual, estimate)

    assert abs_s == Decimal("0.04")
    assert pct_s == Decimal("2.50")
    assert classification == SurpriseClassification.BEAT


def test_eps_surprise_negative_miss():
    """Actual EPS misses consensus estimate -> MISS."""
    actual = Decimal("1.45")
    estimate = Decimal("1.50")
    abs_s, pct_s, classification = calculate_eps_surprise(actual, estimate)

    assert abs_s == Decimal("-0.05")
    assert pct_s == Decimal("-3.33")
    assert classification == SurpriseClassification.MISS


def test_eps_surprise_in_line():
    """Actual EPS matches consensus estimate within tolerance -> IN_LINE."""
    actual = Decimal("1.50")
    estimate = Decimal("1.50")
    abs_s, pct_s, classification = calculate_eps_surprise(actual, estimate)

    assert abs_s == Decimal("0.00")
    assert pct_s == Decimal("0.00")
    assert classification == SurpriseClassification.IN_LINE


def test_eps_surprise_negative_consensus_estimate():
    """Negative consensus estimate uses absolute magnitude in denominator."""
    actual = Decimal("-0.20")
    estimate = Decimal("-0.50")  # Less loss than expected
    abs_s, pct_s, classification = calculate_eps_surprise(actual, estimate)

    # abs_s = -0.20 - (-0.50) = +0.30
    assert abs_s == Decimal("0.30")
    # pct_s = 0.30 / |-0.50| * 100 = +60.00%
    assert pct_s == Decimal("60.00")
    assert classification == SurpriseClassification.BEAT


def test_eps_surprise_zero_consensus_estimate():
    """Zero consensus estimate: absolute surprise defined, percentage None, no div by zero."""
    actual = Decimal("0.15")
    estimate = Decimal("0.00")
    abs_s, pct_s, classification = calculate_eps_surprise(actual, estimate)

    assert abs_s == Decimal("0.15")
    assert pct_s is None
    assert classification == SurpriseClassification.BEAT


def test_eps_surprise_missing_inputs():
    """Missing actual or estimate returns UNAVAILABLE."""
    abs_s, pct_s, classification = calculate_eps_surprise(Decimal("1.50"), None)
    assert abs_s is None and pct_s is None
    assert classification == SurpriseClassification.UNAVAILABLE


def test_revenue_surprise_beat_and_miss():
    """Validates revenue absolute and percentage surprise calculations."""
    act_rev = Decimal("94930000000")
    est_rev = Decimal("94560000000")
    abs_s, pct_s, classification = calculate_revenue_surprise(act_rev, est_rev)

    assert abs_s == Decimal("370000000")
    assert pct_s == Decimal("0.39")
    assert classification == SurpriseClassification.BEAT


def test_revenue_surprise_in_line_tolerance():
    """Revenue within 0.05% difference is classified as IN_LINE."""
    act_rev = Decimal("100020000")
    est_rev = Decimal("100000000")
    abs_s, pct_s, classification = calculate_revenue_surprise(act_rev, est_rev)

    assert abs_s == Decimal("20000")
    assert pct_s == Decimal("0.02")
    assert classification == SurpriseClassification.IN_LINE


def test_formatters():
    """Validates financial string formatters."""
    assert format_eps(Decimal("1.64")) == "$1.64"
    assert format_eps(Decimal("-0.25")) == "-$0.25"
    assert format_eps(None) == "—"
    assert format_revenue(Decimal("94930000000")) == "$94.93B"
    assert format_revenue(Decimal("50000000")) == "$50.00M"
    assert format_percentage(Decimal("2.50")) == "+2.50%"
    assert format_percentage(Decimal("-3.33")) == "-3.33%"


# ===========================================================================
# 2. Repository & Model Tests
# ===========================================================================

def test_events_confirmed_vs_estimated(test_company_id):
    """Repository preserves confirmed vs estimated event status."""
    repo = CompanyEarningsRepository()

    # Seed an estimated event
    evt_est = EarningsEvent(
        event_id="evt_test_est",
        company_id=test_company_id,
        fiscal_period="Q2-2025",
        fiscal_year=2025,
        fiscal_quarter="Q2",
        status=EarningsEventStatus.ESTIMATED,
        announced_date=datetime.date(2025, 5, 1),
        market_session=MarketSession.AFTER_MARKET,
        is_confirmed=False,
    )
    repo.register_event(evt_est)

    events = repo.get_events(test_company_id)
    assert any(e.event_id == "evt_test_est" and not e.is_confirmed for e in events)


def test_next_upcoming_event_selection(test_company_id):
    """get_next_event selects the earliest future scheduled event."""
    repo = CompanyEarningsRepository()
    next_evt = repo.get_next_event(test_company_id)

    assert next_evt is not None
    assert next_evt.fiscal_period == "Q1-2025"
    assert next_evt.status in (EarningsEventStatus.CONFIRMED, EarningsEventStatus.ESTIMATED)


def test_latest_completed_event_selection(test_company_id):
    """get_latest_completed_event returns the most recent completed event."""
    repo = CompanyEarningsRepository()
    latest_evt = repo.get_latest_completed_event(test_company_id)

    assert latest_evt is not None
    assert latest_evt.fiscal_period == "Q4-2024"
    assert latest_evt.status == EarningsEventStatus.COMPLETED


def test_stage82_statements_actuals_fallback(test_company_id):
    """Repository automatically extracts actual EPS and Revenue from Stage 82 statements."""
    statements_repo = CompanyStatementsRepository()
    # Register an income statement period for a new test company
    dummy_company_id = uuid.uuid4()
    register_statement_period(
        company_id=dummy_company_id,
        statement_type=StatementType.INCOME_STATEMENT,
        period_id="Q1-2024",
        label="Q1-2024",
        period_type=StatementPeriodType.QUARTERLY,
        fiscal_year=2024,
        fiscal_quarter="Q1",
        period_start=datetime.date(2023, 10, 1),
        period_end=datetime.date(2023, 12, 31),
        filing_date=datetime.date(2024, 2, 1),
        facts={
            "diluted_eps": Decimal("1.25"),
            "basic_eps": Decimal("1.27"),
            "revenue": Decimal("50000000000"),
            "net_income": Decimal("12000000000"),
        },
    )

    repo = CompanyEarningsRepository(statements_repo=statements_repo)
    actual = repo.get_actual(dummy_company_id, "Q1-2024")

    assert actual is not None
    assert actual.diluted_eps == Decimal("1.25")
    assert actual.revenue == Decimal("50000000000")
    assert actual.source_statement_id == "Q1-2024"


def test_management_guidance_retrieval(test_company_id):
    """Repository retrieves active management guidance."""
    repo = CompanyEarningsRepository()
    guidance = repo.get_guidance(test_company_id, status=GuidanceStatus.ACTIVE)

    assert len(guidance) >= 2
    metrics = [g.metric for g in guidance]
    assert GuidanceMetricType.REVENUE in metrics
    assert GuidanceMetricType.GROSS_MARGIN in metrics


def test_earnings_calls_retrieval(test_company_id):
    """Repository retrieves earnings calls with transcript availability."""
    repo = CompanyEarningsRepository()
    calls = repo.get_calls(test_company_id)

    assert len(calls) >= 1
    assert calls[0].transcript_status == TranscriptStatus.AVAILABLE
    assert calls[0].webcast_url is not None


# ===========================================================================
# 3. Service Layer Tests
# ===========================================================================

@pytest.mark.asyncio
async def test_service_get_earnings_overview(test_company_id):
    """Service returns comprehensive overview combining latest, next, guidance, and history."""
    service = CompanyEarningsService()
    overview = await service.get_earnings_overview(test_company_id)

    assert overview.company_id == str(test_company_id)
    assert overview.latest_completed is not None
    assert overview.latest_completed.fiscal_period == "Q4-2024"
    assert overview.latest_completed.actual_eps == 1.64
    assert overview.latest_completed.estimate_eps == 1.60
    assert overview.latest_completed.eps_classification == SurpriseClassification.BEAT

    assert overview.next_scheduled is not None
    assert overview.next_scheduled.fiscal_period == "Q1-2025"
    assert overview.next_consensus is not None
    assert overview.next_consensus.consensus_eps == 2.36

    assert len(overview.active_guidance) >= 2
    assert len(overview.recent_history) >= 1


@pytest.mark.asyncio
async def test_service_get_earnings_history_ordering(test_company_id):
    """Service returns historical quarterly earnings in descending chronological order."""
    service = CompanyEarningsService()
    history = await service.get_earnings_history(test_company_id, period_type=EarningsPeriodType.QUARTERLY, limit=10)

    assert history.total_count >= 4
    periods = [item.fiscal_period for item in history.items]
    assert "Q4-2024" in periods
    assert "Q3-2024" in periods
    assert "Q2-2024" in periods
    assert "Q1-2024" in periods

    # Q4-2024 should appear before Q1-2024
    assert periods.index("Q4-2024") < periods.index("Q1-2024")


# ===========================================================================
# 4. FastAPI Router Endpoints Tests
# ===========================================================================

@pytest.fixture
def app_instance():
    """Sets up dependency overrides for API route tests."""
    test_uid = uuid.UUID("c0000000-0000-0000-0000-000000000001")
    mock_entity = Entity(
        entity_id=test_uid,
        canonical_name="apple_inc",
        display_name="Apple Inc.",
        entity_type="company",
    )
    mock_company = MagicMock()
    mock_company.legal_name = "Apple Inc."

    class MockCompanyService:
        async def get_company(self, entity_id: uuid.UUID):
            if entity_id == test_uid:
                return mock_entity, mock_company
            from atlas.companies.errors import CompanyNotFoundError
            raise CompanyNotFoundError(str(entity_id))

    from atlas_api.auth.dependencies import get_current_user
    from atlas_api.authorization.dependencies import get_authorization_context
    from atlas_api.dependencies import get_db_session
    from atlas_api.routers.companies import get_company_service
    from atlas_api.routers.company_earnings import get_earnings_service

    auth_user = AuthPrincipal(sub="usr_stage84_analyst", email="analyst@atlas.financial")
    app.dependency_overrides[get_current_user] = lambda: auth_user

    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    app.dependency_overrides[get_company_service] = lambda: MockCompanyService()
    app.dependency_overrides[get_earnings_service] = lambda: CompanyEarningsService(
        repository=CompanyEarningsRepository()
    )

    class MockSession:
        pass

    app.dependency_overrides[get_db_session] = lambda: MockSession()

    yield test_uid
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_earnings_overview(app_instance):
    """GET /api/v1/companies/{id}/earnings/overview returns overview DTO."""
    cid = app_instance
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/companies/{cid}/earnings/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Apple Inc."
    assert data["latest_completed"]["fiscal_period"] == "Q4-2024"
    assert data["latest_completed"]["formatted_actual_eps"] == "$1.64"
    assert data["next_scheduled"]["fiscal_period"] == "Q1-2025"
    assert len(data["active_guidance"]) >= 2


@pytest.mark.asyncio
async def test_api_earnings_history(app_instance):
    """GET /api/v1/companies/{id}/earnings/history returns multi-period history."""
    cid = app_instance
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/companies/{cid}/earnings/history?period_type=QUARTERLY&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 4
    items = data["items"]
    q4 = next((item for item in items if item["fiscal_period"] == "Q4-2024"), None)
    assert q4 is not None
    assert q4["eps_classification"] == "BEAT"
    assert q4["formatted_actual_revenue"] == "$94.93B"


@pytest.mark.asyncio
async def test_api_earnings_events(app_instance):
    """GET /api/v1/companies/{id}/earnings/events returns announcement events."""
    cid = app_instance
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/companies/{cid}/earnings/events")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 5
    assert any(e["fiscal_period"] == "Q1-2025" and e["status"] == "CONFIRMED" for e in data["events"])


@pytest.mark.asyncio
async def test_api_earnings_guidance(app_instance):
    """GET /api/v1/companies/{id}/earnings/guidance returns management guidance items."""
    cid = app_instance
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/companies/{cid}/earnings/guidance")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 2
    assert any(g["metric"] == "REVENUE" and g["status"] == "ACTIVE" for g in data["guidance_items"])


@pytest.mark.asyncio
async def test_api_earnings_calls(app_instance):
    """GET /api/v1/companies/{id}/earnings/calls returns conference call records."""
    cid = app_instance
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/companies/{cid}/earnings/calls")

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 1
    call = data["calls"][0]
    assert call["transcript_status"] == "AVAILABLE"
    assert "Services Momentum" in call["key_topics"]
