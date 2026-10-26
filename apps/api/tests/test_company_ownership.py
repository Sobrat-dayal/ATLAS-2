"""Unit and integration tests for Company Ownership Intelligence (Stage 85).

Covers:
- Pure Decimal percentage and position change calculations
- Zero and negative denominator protection
- Concentration metrics and formatting utilities
- Repository reference holdings and historical snapshot integrity
- Institutional, insider, beneficial, and shareholding pattern queries
- FastAPI endpoint contracts and authorization
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies.ownership.calculator import (
    calculate_concentration_metrics,
    calculate_ownership_percentage,
    calculate_percentage_points_change,
    calculate_position_percentage_change,
    calculate_shares_change,
    format_indicative_value,
    format_percentage,
    format_shares_count,
)
from atlas.companies.ownership.enums import (
    PositionChangeStatus,
)
from atlas.companies.ownership.repository import CompanyOwnershipRepository
from atlas.companies.ownership.service import CompanyOwnershipService
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers.companies import get_company_service
from atlas_api.routers.company_ownership import get_ownership_service

# ---------------------------------------------------------------------------
# Unit Tests: Pure Decimal Financial Calculator
# ---------------------------------------------------------------------------

def test_calculate_ownership_percentage():
    # Standard: 1,332,450,120 / 15,115,800,000 = 8.8149%
    pct = calculate_ownership_percentage(Decimal("1332450120"), Decimal("15115800000"))
    assert pct == Decimal("8.8149")

    # Zero shares held
    assert calculate_ownership_percentage(0, Decimal("1000000")) == Decimal("0.0000")

    # Missing or invalid denominator
    assert calculate_ownership_percentage(Decimal("100"), Decimal("0")) is None
    assert calculate_ownership_percentage(Decimal("100"), Decimal("-500")) is None
    assert calculate_ownership_percentage(None, Decimal("1000000")) is None
    assert calculate_ownership_percentage(Decimal("100"), None) is None


def test_calculate_shares_change():
    # Increasing
    assert calculate_shares_change(Decimal("1332450120"), Decimal("1310000000")) == Decimal("22450120")
    # Decreasing
    assert calculate_shares_change(Decimal("300000000"), Decimal("400000000")) == Decimal("-100000000")
    # Unchanged
    assert calculate_shares_change(Decimal("500"), Decimal("500")) == Decimal("0")


def test_calculate_position_percentage_change():
    # 400M -> 300M = -25%
    pct = calculate_position_percentage_change(Decimal("300000000"), Decimal("400000000"))
    assert pct == Decimal("-25.00")

    # 1.31B -> 1.332B = +1.71%
    pct = calculate_position_percentage_change(Decimal("1332450120"), Decimal("1310000000"))
    assert pct == Decimal("1.71")

    # New position (prior shares 0)
    assert calculate_position_percentage_change(Decimal("500000"), Decimal("0")) is None
    assert calculate_position_percentage_change(Decimal("500000"), None) is None


def test_calculate_percentage_points_change():
    # 8.81% - 8.67% = +0.1400 pp
    diff = calculate_percentage_points_change(Decimal("8.8149"), Decimal("8.6664"))
    assert diff == Decimal("0.1485")


def test_calculate_concentration_metrics():
    holdings = [
        Decimal("1332450120"),
        Decimal("1043210000"),
        Decimal("562400000"),
        Decimal("335100000"),
        Decimal("308500000"),
        Decimal("300000000"),
    ]
    denom = Decimal("15115800000")
    conc = calculate_concentration_metrics(holdings, denom)

    assert conc["top_1_shares"] == Decimal("1332450120")
    assert conc["top_1_pct"] == Decimal("8.8149")
    assert conc["top_5_shares"] == Decimal("3581660120")
    assert conc["top_5_pct"] == Decimal("23.6948")
    assert conc["total_disclosed_shares"] == Decimal("3881660120")


def test_formatting_utilities():
    assert format_shares_count(Decimal("1332450120")) == "1.33B"
    assert format_shares_count(Decimal("562400000")) == "562.40M"
    assert format_shares_count(Decimal("450000")) == "450.00K"
    assert format_shares_count(Decimal("1332450120"), compact=False) == "1,332,450,120"
    assert format_shares_count(None) == "—"

    assert format_percentage(Decimal("8.8149")) == "8.81%"
    assert format_percentage(Decimal("2.45"), include_sign=True) == "+2.45%"
    assert format_percentage(None) == "—"

    assert format_indicative_value(Decimal("1000000000"), Decimal("225.00")) == "$225.00B"
    assert format_indicative_value(Decimal("1000000"), Decimal("150.00")) == "$150.00M"
    assert format_indicative_value(None, Decimal("225.00")) == "—"


# ---------------------------------------------------------------------------
# Integration Tests: Repository & Service Layer
# ---------------------------------------------------------------------------

def test_repository_apple_reference_holdings():
    repo = CompanyOwnershipRepository()
    apple_id = repo.apple_company_id
    sec_id = repo.apple_security_id

    # Verify Securities
    secs = repo.get_securities(apple_id)
    assert len(secs) == 1
    assert secs[0]["ticker"] == "AAPL"
    assert secs[0]["shares_outstanding"] == Decimal("15115800000")

    # Latest Snapshot (2024-Q3)
    snap = repo.get_latest_snapshot(apple_id, sec_id)
    assert snap is not None
    assert snap.reporting_period == "2024-Q3"
    assert snap.reporting_date == "2024-09-30"
    assert snap.filing_date == "2024-11-14"

    # Verify top institutional holders
    holders = {p.holder.name: p for p in snap.positions}
    assert "The Vanguard Group, Inc." in holders
    assert "BlackRock, Inc." in holders
    assert "Berkshire Hathaway Inc." in holders
    assert "State Street Corporation" in holders

    vanguard_pos = holders["The Vanguard Group, Inc."]
    assert vanguard_pos.shares_held == Decimal("1332450120")
    assert vanguard_pos.filing_delay_days == 45
    assert vanguard_pos.calculated_percentage == Decimal("8.8149")

    # Verify insiders
    assert "Timothy D. Cook" in holders
    cook_pos = holders["Timothy D. Cook"]
    assert cook_pos.holder.is_insider is True
    assert cook_pos.insider_role == "Chief Executive Officer"
    assert cook_pos.shares_held == Decimal("3280053")


def test_repository_historical_position_changes():
    repo = CompanyOwnershipRepository()
    apple_id = repo.apple_company_id
    sec_id = repo.apple_security_id

    changes = repo.calculate_position_changes(apple_id, sec_id, "2024-Q3", "2024-Q2")
    assert len(changes) > 0

    change_map = {c.holder.name: c for c in changes}

    # Berkshire decreased shares from 400M to 300M (-100M, -25%)
    assert "Berkshire Hathaway Inc." in change_map
    brk_change = change_map["Berkshire Hathaway Inc."]
    assert brk_change.shares_change == Decimal("-100000000")
    assert brk_change.percentage_change == Decimal("-25.00")
    assert brk_change.status == PositionChangeStatus.DECREASED

    # Vanguard increased from 1.31B to 1.332B (+22.45M)
    assert "The Vanguard Group, Inc." in change_map
    vg_change = change_map["The Vanguard Group, Inc."]
    assert vg_change.shares_change == Decimal("22450120")
    assert vg_change.status == PositionChangeStatus.INCREASED


def test_service_ownership_overview():
    service = CompanyOwnershipService()
    apple_id = service.repository.apple_company_id

    overview = service.get_ownership_overview(apple_id)
    assert overview.company_id == apple_id
    assert overview.selected_security.ticker == "AAPL"
    assert overview.reporting_period == "2024-Q3"
    assert len(overview.top_holders) > 0
    assert overview.concentration.top_1_pct is not None
    assert overview.institutional_summary["percentage"] > 20.0
    assert overview.patterns.categories[0].percentage_of_total > 50.0
    assert overview.insider_summary["holder_count"] >= 4
    assert overview.patterns is not None
    assert len(overview.patterns.categories) == 3


def test_service_institutional_and_insiders():
    service = CompanyOwnershipService()
    apple_id = service.repository.apple_company_id

    # Institutional
    inst_resp = service.get_institutional_holdings(apple_id)
    assert inst_resp.total_count >= 5
    assert inst_resp.items[0].holder.name == "The Vanguard Group, Inc."
    assert inst_resp.items[0].indicative_value_formatted != "—"

    # Insiders
    insider_resp = service.get_insider_holdings(apple_id)
    assert insider_resp.total_count >= 4
    names = [i.holder.name for i in insider_resp.items]
    assert "Timothy D. Cook" in names
    assert "Arthur D. Levinson" in names


def test_service_beneficial_owners():
    service = CompanyOwnershipService()
    apple_id = service.repository.apple_company_id

    beneficial_resp = service.get_beneficial_ownership(apple_id)
    assert beneficial_resp.total_count >= 2
    holders = {b.holder.name: b for b in beneficial_resp.items}
    assert "The Vanguard Group, Inc." in holders
    assert "BlackRock, Inc." in holders
    assert holders["The Vanguard Group, Inc."].calculated_percentage >= 5.0
    assert holders["The Vanguard Group, Inc."].shared_voting_power is not None


# ---------------------------------------------------------------------------
# FastAPI Router HTTP Endpoint Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ownership_services():
    apple_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")

    mock_entity = MagicMock()
    mock_entity.display_name = "Apple Inc."
    mock_entity.canonical_name = "Apple Inc."

    mock_company = MagicMock()
    mock_company.legal_name = "Apple Inc."
    mock_company.primary_ticker = "AAPL"

    class MockCompanyService:
        async def get_company(self, cid):
            if cid == apple_id:
                return mock_entity, mock_company
            from atlas.companies.errors import CompanyNotFoundError
            raise CompanyNotFoundError(str(cid))

    mock_comp_service = MockCompanyService()
    mock_own_service = CompanyOwnershipService()

    from atlas_api.authorization.dependencies import get_authorization_context

    auth_user = AuthPrincipal(sub="usr_stage85_analyst", email="analyst@atlas.financial")
    app.dependency_overrides[get_current_user] = lambda: auth_user

    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    app.dependency_overrides[get_company_service] = lambda: mock_comp_service
    app.dependency_overrides[get_ownership_service] = lambda: mock_own_service

    yield mock_own_service

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_ownership_endpoints(mock_ownership_services):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        apple_id = "c0000000-0000-0000-0000-000000000001"

        # 1. GET /overview
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/overview")
        assert r.status_code == 200
        data = r.json()
        assert data["company_id"] == apple_id
        assert data["selected_security"]["ticker"] == "AAPL"
        assert len(data["top_holders"]) > 0

        # 2. GET /securities
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/securities")
        assert r.status_code == 200
        data = r.json()
        assert len(data["securities"]) >= 1

        # 3. GET /holders
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/holders")
        assert r.status_code == 200
        data = r.json()
        assert data["total_count"] > 0

        # 4. GET /institutions
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/institutions")
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) >= 5

        # 5. GET /insiders
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/insiders")
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) >= 4

        # 6. GET /beneficial
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/beneficial")
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) >= 2

        # 7. GET /patterns
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/patterns")
        assert r.status_code == 200
        data = r.json()
        assert len(data["categories"]) == 3

        # 8. GET /history
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/history")
        assert r.status_code == 200
        data = r.json()
        assert len(data["snapshots"]) >= 2

        # 9. GET /changes
        r = await client.get(f"/api/v1/companies/{apple_id}/ownership/changes")
        assert r.status_code == 200
        data = r.json()
        assert len(data["changes"]) > 0

        # 10. 404 for unknown company
        unknown_id = "c0000000-0000-0000-0000-999999999999"
        r = await client.get(f"/api/v1/companies/{unknown_id}/ownership/overview")
        assert r.status_code == 404
