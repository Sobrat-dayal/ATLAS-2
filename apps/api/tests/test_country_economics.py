"""Automated Test Suite for Country Economics Intelligence (Stage 90).

Tests:
1. Sovereign Country Entity Identity & ISO Code Resolution
2. National Accounts & GDP Expenditure Decomposition
3. Chain-Linked Volume Non-Additivity & Reconciliations
4. Gross Value Added by Sector (Production Approach)
5. GDP Per Capita & Demographic Population Alignment
6. Headline CPI vs. Core vs. Component Inflation
7. Labor Market Survey Methodologies & Participation
8. Fiscal Accounts, Primary Balances & Sovereign Debt-to-GDP
9. International Trade vs. Current Account & Balance of Payments
10. Demographics, Age Dependency & Urbanization
11. REST API Integration Endpoints & 404 Error Handling
12. Zero Side-Effects on Read Verification
"""

from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.economics.countries import (
    CountryEconomicsRepository,
    CountryEconomicsService,
    CountryGeographyNotFoundError,
    GDPApproachKind,
    GovernmentAccountingScope,
)
from atlas.economics.v1.enums import (
    GeographicScopeKind,
    PriceBasisKind,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.routers.country_economics import (
    get_country_economics_service,
)
from atlas_api.routers.country_economics import (
    router as country_economics_router,
)


@pytest.fixture
def repo() -> CountryEconomicsRepository:
    return CountryEconomicsRepository()


@pytest.fixture
def service(repo: CountryEconomicsRepository) -> CountryEconomicsService:
    return CountryEconomicsService(repo)


@pytest.fixture
def mock_principal() -> AuthPrincipal:
    return AuthPrincipal(
        sub="user-macro-analyst",
        email="macro@atlas.financial",
        role="authenticated",
    )


@pytest.fixture
def test_client(service: CountryEconomicsService, mock_principal: AuthPrincipal) -> TestClient:
    app = FastAPI()
    app.include_router(country_economics_router)

    app.dependency_overrides[get_country_economics_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    return TestClient(app)


# -----------------------------------------------------------------------------
# 1. Country Identity & ISO Resolution Tests
# -----------------------------------------------------------------------------


def test_country_identity_resolution(service: CountryEconomicsService):
    """Test resolution by UUID, ISO code, and case-insensitivity."""
    # Resolve by UUID
    prof_uuid = service.get_profile("geo-us")
    assert prof_uuid.iso_code == "US"
    assert prof_uuid.name == "United States"
    assert prof_uuid.scope_kind == GeographicScopeKind.COUNTRY

    # Resolve by uppercase ISO
    prof_iso = service.get_profile("US")
    assert prof_iso.geography_id == "geo-us"

    # Resolve by lowercase ISO
    prof_lower = service.get_profile("us")
    assert prof_lower.geography_id == "geo-us"

    # Resolve Euro Area
    prof_ea = service.get_profile("EA")
    assert prof_ea.scope_kind == GeographicScopeKind.ECONOMIC_AREA
    assert prof_ea.currency_code == "EUR"
    assert prof_ea.central_bank_name == "European Central Bank (ECB)"


def test_invalid_country_raises_404(service: CountryEconomicsService):
    """Test that non-existent country identifiers raise CountryGeographyNotFoundError."""
    with pytest.raises(CountryGeographyNotFoundError):
        service.get_profile("XYZ_UNKNOWN_TERRITORY")


def test_g6_all_countries_profile_coverage(service: CountryEconomicsService):
    """Verify all G6 economies have registered profiles."""
    countries = service.list_countries()
    iso_codes = {c.iso_code for c in countries}
    expected = {"US", "EA", "CN", "IN", "JP", "GB"}
    assert expected.issubset(iso_codes)


# -----------------------------------------------------------------------------
# 2. GDP Expenditure Decomposition & Additivity Tests
# -----------------------------------------------------------------------------


def test_us_gdp_expenditure_decomposition(service: CountryEconomicsService):
    """Test US GDP expenditure components and nominal additivity."""
    gdp = service.get_gdp("US", GDPApproachKind.EXPENDITURE)

    assert gdp.reference_period == "2024-Q3"
    assert gdp.price_basis == PriceBasisKind.CURRENT_PRICES
    assert gdp.nominal_gdp_billions == 29350.4
    assert gdp.real_gdp_billions == 23150.2
    assert gdp.real_growth_qoq_ann == 2.8

    # Verify components presence
    codes = {c.code for c in gdp.components}
    assert {"PCEC", "GPDI", "GovCons", "EXP", "IMP", "NETEXP"}.issubset(codes)

    # Verify net exports formula: Exports - Imports
    exp_item = next(c for c in gdp.components if c.code == "EXP")
    imp_item = next(c for c in gdp.components if c.code == "IMP")
    netexp_item = next(c for c in gdp.components if c.code == "NETEXP")

    assert round(exp_item.value - imp_item.value, 1) == round(netexp_item.value, 1)

    # Verify nominal additivity
    pce = next(c for c in gdp.components if c.code == "PCEC").value
    gpdi = next(c for c in gdp.components if c.code == "GPDI").value
    gov = next(c for c in gdp.components if c.code == "GovCons").value
    netexp = netexp_item.value

    nominal_sum = pce + gpdi + gov + netexp
    assert round(nominal_sum, 1) == round(gdp.nominal_gdp_billions, 1)
    assert gdp.is_strictly_additive is True


def test_gdp_per_capita_population_alignment(service: CountryEconomicsService):
    """Verify GDP per capita aligns with annual demographic population."""
    gdp = service.get_gdp("US")
    assert gdp.gdp_per_capita_usd is not None
    assert gdp.gdp_per_capita_usd > 80000.0
    # Must document the population reference year
    assert gdp.per_capita_population_period == "2023"


# -----------------------------------------------------------------------------
# 3. Production Sector Value Added Tests
# -----------------------------------------------------------------------------


def test_us_sector_value_added(service: CountryEconomicsService):
    """Test US sector value-added GVA shares."""
    prod = service.get_production("US")
    assert prod.total_gva_billions > 25000.0

    agri = next((s for s in prod.sectors if s.sector_code == "AGRICULTURE"), None)
    ind = next((s for s in prod.sectors if s.sector_code == "INDUSTRY"), None)
    serv = next((s for s in prod.sectors if s.sector_code == "SERVICES"), None)

    assert agri is not None and agri.share_of_gva_pct < 5.0
    assert ind is not None and ind.share_of_gva_pct > 15.0
    assert serv is not None and serv.share_of_gva_pct > 75.0


# -----------------------------------------------------------------------------
# 4. Inflation & CPI Components Tests
# -----------------------------------------------------------------------------


def test_country_inflation_headline_vs_core(service: CountryEconomicsService):
    """Test distinction between headline CPI, core CPI, food, and energy."""
    inf = service.get_inflation("US")
    assert inf.reference_period == "2024-09"
    assert inf.cpi_index_level == 314.796
    assert inf.headline_yoy == 2.4
    assert inf.core_yoy == 3.3
    # Core is distinct from headline
    assert inf.headline_yoy != inf.core_yoy
    assert inf.food_inflation_yoy == 2.3
    assert inf.energy_inflation_yoy == -6.8


# -----------------------------------------------------------------------------
# 5. Labor Market Survey & Participation Tests
# -----------------------------------------------------------------------------


def test_labor_market_survey_methodology(service: CountryEconomicsService):
    """Test labor market statistics and survey methodology qualification."""
    labor = service.get_labor("US")
    assert labor.reference_period == "2024-09"
    assert labor.unemployment_rate == 4.1
    assert labor.labor_force_participation_rate == 62.7
    assert labor.employment_level_thousands == 161400.0
    assert "Current Population Survey" in labor.survey_methodology


# -----------------------------------------------------------------------------
# 6. Fiscal Accounts & Sovereign Debt-to-GDP Tests
# -----------------------------------------------------------------------------


def test_fiscal_accounts_and_debt_ratio(service: CountryEconomicsService):
    """Test government fiscal balance and gross debt-to-GDP ratio."""
    fiscal = service.get_fiscal("US")
    assert fiscal.fiscal_year_label.startswith("FY2024")
    assert fiscal.accounting_scope == GovernmentAccountingScope.GENERAL_GOVERNMENT
    assert fiscal.fiscal_balance_pct_gdp == -6.4
    assert fiscal.primary_balance_pct_gdp == -3.5
    assert fiscal.gross_debt_pct_gdp == 120.8
    assert fiscal.net_debt_pct_gdp == 96.1
    # Primary balance is more favorable than overall balance due to interest
    assert fiscal.primary_balance_pct_gdp > fiscal.fiscal_balance_pct_gdp


# -----------------------------------------------------------------------------
# 7. International Trade vs. Current Account Tests
# -----------------------------------------------------------------------------


def test_trade_balance_vs_current_account(service: CountryEconomicsService):
    """Test that trade balance is strictly differentiated from current account."""
    ext = service.get_external("US")
    assert ext.reference_period == "2024-Q2"
    assert ext.merchandise_trade_balance_billions == -282.8
    assert ext.services_trade_balance_billions == 85.1
    assert ext.total_trade_balance_billions == -197.7
    assert ext.current_account_balance_billions == -266.8
    # Current account includes primary/secondary income flows, so differs from trade balance
    assert ext.total_trade_balance_billions != ext.current_account_balance_billions
    assert ext.foreign_exchange_reserves_billions == 242.0


# -----------------------------------------------------------------------------
# 8. Demographics & Structural Tests
# -----------------------------------------------------------------------------


def test_country_demographics(service: CountryEconomicsService):
    """Test demographic totals, working-age share, and urbanization."""
    demo = service.get_demographics("US")
    assert demo.reference_period == "2023"
    assert demo.total_population_millions == 336.8
    assert demo.working_age_population_pct == 64.9
    assert demo.urbanization_rate_pct == 83.3
    assert demo.age_dependency_ratio_pct == 54.1


# -----------------------------------------------------------------------------
# 9. Master Overview Snapshot Test
# -----------------------------------------------------------------------------


def test_country_economics_overview(service: CountryEconomicsService):
    """Test master country overview assembly with independent observation periods."""
    overview = service.get_overview("US")
    assert overview.profile.iso_code == "US"
    assert overview.headline_real_gdp_growth_qoq == 2.8
    assert overview.headline_gdp_period == "2024-Q3"
    assert overview.headline_cpi_inflation_yoy == 2.4
    assert overview.headline_cpi_period == "2024-09"
    assert overview.unemployment_rate == 4.1
    assert overview.general_gov_debt_pct_gdp == 120.8
    assert overview.total_population_millions == 336.8


# -----------------------------------------------------------------------------
# 10. REST API Endpoints Integration Tests
# -----------------------------------------------------------------------------


def test_api_list_countries(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 6
    assert any(c["iso_code"] == "US" for c in data)


def test_api_get_country_overview(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/US/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["profile"]["iso_code"] == "US"
    assert data["headline_real_gdp_growth_qoq"] == 2.8


def test_api_get_country_gdp(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/US/gdp")
    assert res.status_code == 200
    data = res.json()
    assert data["nominal_gdp_billions"] == 29350.4
    assert len(data["components"]) > 0


def test_api_get_country_inflation(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/EA/inflation")
    assert res.status_code == 200
    data = res.json()
    assert data["geography_id"] == "geo-ea"
    assert data["headline_yoy"] == 1.7


def test_api_get_country_fiscal(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/US/fiscal")
    assert res.status_code == 200
    data = res.json()
    assert data["fiscal_balance_pct_gdp"] == -6.4


def test_api_get_country_external(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/CN/external")
    assert res.status_code == 200
    data = res.json()
    assert data["geography_id"] == "geo-cn"
    assert data["foreign_exchange_reserves_billions"] == 3261.0


def test_api_get_country_demographics(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/IN/demographics")
    assert res.status_code == 200
    data = res.json()
    assert data["geography_id"] == "geo-in"
    assert data["total_population_millions"] == 1428.6


def test_api_get_country_coverage(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/GB/coverage")
    assert res.status_code == 200
    data = res.json()
    assert data["iso_code"] == "GB"
    assert data["has_gdp_expenditure"] is True
    assert data["has_demographics"] is True


def test_api_unknown_country_404(test_client: TestClient):
    res = test_client.get("/api/v1/economics/countries/NON_EXISTENT_COUNTRY/overview")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# -----------------------------------------------------------------------------
# 11. Zero Side-Effects on Read Verification
# -----------------------------------------------------------------------------


def test_zero_side_effects_on_read(repo: CountryEconomicsRepository):
    """Verify that multiple reads cause zero state mutations in repository."""
    initial_profiles_len = len(repo._profiles)
    initial_gdp_len = len(repo._gdp_expenditure)

    service = CountryEconomicsService(repo)
    for _ in range(5):
        service.get_overview("US")
        service.get_gdp("US")
        service.get_inflation("EA")
        service.get_fiscal("CN")
        service.get_external("IN")
        service.get_demographics("JP")

    assert len(repo._profiles) == initial_profiles_len
    assert len(repo._gdp_expenditure) == initial_gdp_len
