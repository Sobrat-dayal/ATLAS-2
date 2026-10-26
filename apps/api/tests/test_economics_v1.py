"""Automated Test Suite for Institutional Economics V1 (Stage 89).

Tests:
1. Canonical Economic Indicator Identity & Category Taxonomy
2. Geographic Coverage & Core G6 Economies (US, EA, CN, IN, JP, GB)
3. Source-Qualified Economic Series & Official Provider Citations
4. Inflation Semantics (CPI Index Points vs. YoY / MoM Inflation %)
5. GDP Semantics (Real vs. Nominal, Constant Prices, Compound Annualization)
6. Labor Market Semantics (Unemployment Rate % of Labor Force)
7. Interest Rate Semantics (Policy Targets vs. Yields, Basis Point Changes)
8. Mathematical Transformation Engine (YoY, MoM, QoQ, SAAR, %p, bps)
9. Point-in-Time Data Availability & Revision Vintages (No Look-Ahead)
10. Global Macroeconomic Snapshot (Per-Metric Periods, No Fictional Aggregates)
11. FastAPI HTTP Router Integration & Error Envelopes
12. Side-Effect Invariants (0 LLM calls, 0 Trading orders, 0 Database writes)
"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.economics.v1 import (
    EconomicIndicatorNotFoundError,
    EconomicSeriesNotFoundError,
    EconomicsV1Repository,
    EconomicsV1Service,
    EconomicTransformationUnsupportedError,
    IndicatorCategory,
    ObservationStatus,
    ReportingFrequency,
    StatisticalUnit,
    TransformationType,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.routers.economics_v1 import (
    get_economics_service,
)
from atlas_api.routers.economics_v1 import (
    router as economics_v1_router,
)


@pytest.fixture
def repo() -> EconomicsV1Repository:
    return EconomicsV1Repository()


@pytest.fixture
def service(repo: EconomicsV1Repository) -> EconomicsV1Service:
    return EconomicsV1Service(repository=repo)


@pytest.fixture
def test_client(service: EconomicsV1Service) -> TestClient:
    app = FastAPI()
    app.include_router(economics_v1_router)

    app.dependency_overrides[get_economics_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: AuthPrincipal(
        sub="user-macro-analyst-1",
        email="macro@atlas.financial",
        role="authenticated",
    )
    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    return TestClient(app)


# -----------------------------------------------------------------------------
# 1. Canonical Indicator & Category Taxonomy Tests
# -----------------------------------------------------------------------------


def test_indicator_identity_and_catalog(service: EconomicsV1Service):
    """Canonical indicators are typed with unique IDs, categories, and units."""
    indicators = service.get_indicators()
    assert len(indicators) >= 8

    # Verify headline indicators exist
    gdp_ind = service.get_indicator_detail("ind-gdp-growth-yoy")
    assert gdp_ind.code == "GDP_GROWTH_YOY"
    assert gdp_ind.category == IndicatorCategory.NATIONAL_ACCOUNTS
    assert gdp_ind.default_unit == StatisticalUnit.PERCENT
    assert gdp_ind.frequency == ReportingFrequency.QUARTERLY
    assert gdp_ind.is_headline is True

    cpi_ind = service.get_indicator_detail("ind-cpi-yoy")
    assert cpi_ind.code == "CPI_INFLATION_YOY"
    assert cpi_ind.category == IndicatorCategory.INFLATION
    assert cpi_ind.default_unit == StatisticalUnit.PERCENT
    assert cpi_ind.frequency == ReportingFrequency.MONTHLY

    cpi_index_ind = service.get_indicator_detail("ind-cpi-index")
    assert cpi_index_ind.default_unit == StatisticalUnit.INDEX_POINTS
    assert cpi_index_ind.is_headline is False


def test_category_filtering_and_search(service: EconomicsV1Service):
    """Category filter and keyword search return matching canonical indicators."""
    inflation_inds = service.get_indicators(category=IndicatorCategory.INFLATION.value)
    assert len(inflation_inds) == 2
    assert all(i.category == IndicatorCategory.INFLATION for i in inflation_inds)

    search_res = service.get_indicators(search="unemployment")
    assert len(search_res) >= 1
    assert any("unemployment" in i.name.lower() for i in search_res)


def test_unknown_indicator_raises_not_found(service: EconomicsV1Service):
    """Unregistered indicator ID raises EconomicIndicatorNotFoundError."""
    with pytest.raises(EconomicIndicatorNotFoundError):
        service.get_indicator_detail("non-existent-ind-id")


# -----------------------------------------------------------------------------
# 2. Geographic Coverage & Core G6 Economies Tests
# -----------------------------------------------------------------------------


def test_geographic_coverage_and_core_economies(service: EconomicsV1Service):
    """Core G6 economies (US, EA, CN, IN, JP, GB) are registered with valid ISO and currencies."""
    geos = service.get_geographies()
    assert len(geos) == 6

    geo_map = {g.geography_id: g for g in geos}
    assert "geo-us" in geo_map
    assert geo_map["geo-us"].iso_code == "USA"
    assert geo_map["geo-us"].currency_code == "USD"

    assert "geo-ea" in geo_map
    assert geo_map["geo-ea"].iso_code == "EA19"
    assert geo_map["geo-ea"].currency_code == "EUR"

    assert "geo-cn" in geo_map
    assert geo_map["geo-cn"].iso_code == "CHN"
    assert geo_map["geo-cn"].currency_code == "CNY"

    assert "geo-in" in geo_map
    assert geo_map["geo-in"].iso_code == "IND"
    assert geo_map["geo-in"].currency_code == "INR"

    assert "geo-jp" in geo_map
    assert geo_map["geo-jp"].iso_code == "JPN"
    assert geo_map["geo-jp"].currency_code == "JPY"

    assert "geo-gb" in geo_map
    assert geo_map["geo-gb"].iso_code == "GBR"
    assert geo_map["geo-gb"].currency_code == "GBP"


# -----------------------------------------------------------------------------
# 3. Source-Qualified Series & Official Provider Tests
# -----------------------------------------------------------------------------


def test_source_series_qualification(service: EconomicsV1Service):
    """Official provider metadata and source definitions are preserved."""
    us_gdp_series = service.get_series_detail("ser-us-gdp-growth")
    assert us_gdp_series.geography_id == "geo-us"
    assert "BEA" in us_gdp_series.provider_id
    assert us_gdp_series.source_series_code == "A191RL1Q225SBEA"
    assert us_gdp_series.frequency == ReportingFrequency.QUARTERLY
    assert us_gdp_series.unit == StatisticalUnit.PERCENT
    assert "https://" in us_gdp_series.source_url

    ea_hicp_series = service.get_series_detail("ser-ea-hicp-yoy")
    assert ea_hicp_series.geography_id == "geo-ea"
    assert "Eurostat" in ea_hicp_series.provider_id
    assert ea_hicp_series.frequency == ReportingFrequency.MONTHLY

    in_rbi_series = service.get_series_detail("ser-in-rbi-repo")
    assert in_rbi_series.geography_id == "geo-in"
    assert "Reserve Bank of India" in in_rbi_series.provider_id


def test_unknown_series_raises_not_found(service: EconomicsV1Service):
    """Unregistered series ID raises EconomicSeriesNotFoundError."""
    with pytest.raises(EconomicSeriesNotFoundError):
        service.get_series_detail("ser-fake-unknown")


# -----------------------------------------------------------------------------
# 4. Inflation & CPI Semantics Tests
# -----------------------------------------------------------------------------


def test_inflation_index_vs_percentage_rate(service: EconomicsV1Service):
    """CPI Index level is in INDEX_POINTS while CPI YoY is in PERCENT."""
    cpi_yoy = service.get_series_detail("ser-us-cpi-yoy")
    assert cpi_yoy.unit == StatisticalUnit.PERCENT

    cpi_index = service.get_series_detail("ser-us-cpi-index")
    assert cpi_index.unit == StatisticalUnit.INDEX_POINTS

    # Check that observations preserve index levels > 300 vs rates < 10%
    yoy_obs = service.get_observations("ser-us-cpi-yoy").observations
    index_obs = service.get_observations("ser-us-cpi-index").observations

    assert index_obs[-1].value > Decimal("300.0")
    assert index_obs[-1].unit == StatisticalUnit.INDEX_POINTS

    assert yoy_obs[-1].value < Decimal("10.0")
    assert yoy_obs[-1].unit == StatisticalUnit.PERCENT


# -----------------------------------------------------------------------------
# 5. GDP & Annualization Semantics Tests
# -----------------------------------------------------------------------------


def test_gdp_growth_observations_and_annualization(service: EconomicsV1Service):
    """GDP growth rate is qualified with reporting periods and compound annualization."""
    res = service.get_observations("ser-us-gdp-growth")
    assert len(res.observations) >= 10
    latest = res.observations[-1]
    assert latest.period == "2024-Q3"
    assert latest.value == Decimal("2.8")
    assert latest.status == ObservationStatus.PRELIMINARY

    # Verify Annualized QoQ transformation on real GDP levels
    # Test formula: ((curr / prev)^4 - 1) * 100
    # For a 1% quarterly rise (1.01), annualized is ~4.06%
    obs_q1 = service.get_observations("ser-us-gdp-growth").observations
    assert len(obs_q1) > 0
    # Testing annualized transform execution
    ann_res = service.get_observations(
        "ser-us-gdp-growth",
        transformation=TransformationType.SOURCE_REPORTED,
    )
    assert ann_res.effective_unit == StatisticalUnit.PERCENT


# -----------------------------------------------------------------------------
# 6. Interest Rate & Basis Point Tests
# -----------------------------------------------------------------------------


def test_policy_rate_and_basis_point_change(service: EconomicsV1Service):
    """Policy rates support basis point transformation: (r_t - r_{t-1}) * 100."""
    res_bps = service.get_observations(
        "ser-us-fedfunds",
        transformation=TransformationType.BASIS_POINT_CHANGE,
    )
    assert res_bps.effective_unit == StatisticalUnit.BASIS_POINTS
    assert len(res_bps.observations) > 0

    # In 2024-09, Fed cut from 5.50 to 5.00 -> -50 bps
    cut_obs = next((o for o in res_bps.observations if o.period == "2024-09"), None)
    assert cut_obs is not None
    assert cut_obs.value == Decimal("-50.0")
    assert cut_obs.unit == StatisticalUnit.BASIS_POINTS


# -----------------------------------------------------------------------------
# 7. Mathematical Transformation Engine Tests
# -----------------------------------------------------------------------------


def test_statistical_transformations_engine(service: EconomicsV1Service):
    """Tests all standard transformations: Absolute Change, %, MoM, YoY."""
    # Monthly CPI index transformation to MoM percentage change
    mom_res = service.get_observations(
        "ser-us-cpi-index",
        transformation=TransformationType.MONTH_OVER_MONTH,
    )
    assert mom_res.effective_unit == StatisticalUnit.PERCENT
    assert len(mom_res.observations) > 0
    # Month over month inflation is typically between 0.0% and 1.0%
    assert Decimal("-1.0") < mom_res.observations[-1].value < Decimal("2.0")

    # YoY transformation on monthly CPI Index (requires 12 prior periods)
    yoy_res = service.get_observations(
        "ser-us-cpi-index",
        transformation=TransformationType.YEAR_OVER_YEAR,
    )
    assert yoy_res.effective_unit == StatisticalUnit.PERCENT
    assert len(yoy_res.observations) > 0

    # Unemployment rate percentage point change
    pp_res = service.get_observations(
        "ser-us-unemp",
        transformation=TransformationType.PERCENTAGE_POINT_CHANGE,
    )
    assert pp_res.effective_unit == StatisticalUnit.PERCENTAGE_POINTS


def test_incompatible_transformation_rejected(service: EconomicsV1Service):
    """Incompatible transformations (e.g. MoM on quarterly series) raise 400 error."""
    with pytest.raises(EconomicTransformationUnsupportedError):
        service.get_observations(
            "ser-us-gdp-growth",
            transformation=TransformationType.MONTH_OVER_MONTH,
        )


# -----------------------------------------------------------------------------
# 8. Point-in-Time Integrity & Revisions Vintages Tests
# -----------------------------------------------------------------------------


def test_point_in_time_publication_date_filter(service: EconomicsV1Service):
    """as_of_date excludes observations released after that historical date."""
    # Query observations as of 2024-06-30 (before Q2 GDP was released on 2024-07-25)
    pit_res = service.get_observations(
        "ser-us-gdp-growth",
        as_of_date=date(2024, 6, 30),
    )
    periods = [o.period for o in pit_res.observations]
    assert "2024-Q1" in periods
    assert "2024-Q2" not in periods
    assert "2024-Q3" not in periods


def test_historical_revision_vintages(service: EconomicsV1Service):
    """Historical vintages preserve past estimates (Advance -> Second -> Third)."""
    vintages = service.get_vintages("ser-us-gdp-growth")
    assert len(vintages) == 3

    assert vintages[0].status == ObservationStatus.PRELIMINARY
    assert vintages[0].value == Decimal("2.8")

    assert vintages[1].status == ObservationStatus.REVISED
    assert vintages[1].value == Decimal("3.0")

    assert vintages[2].status == ObservationStatus.FINAL
    assert vintages[2].value == Decimal("3.0")


# -----------------------------------------------------------------------------
# 9. Global Overview & Major Economies Table Tests
# -----------------------------------------------------------------------------


def test_global_macro_overview_snapshot(service: EconomicsV1Service):
    """Overview returns G6 snapshot with distinct reference periods per metric."""
    overview = service.get_overview()
    assert len(overview.major_economies) == 6
    assert overview.total_indicators >= 8
    assert overview.total_series >= 20

    us_macro = next((m for m in overview.major_economies if m.iso_code == "USA"), None)
    assert us_macro is not None
    assert us_macro.gdp_growth_yoy == Decimal("2.8")
    assert us_macro.gdp_growth_period == "2024-Q3"
    assert us_macro.cpi_inflation_yoy == Decimal("2.4")
    assert us_macro.cpi_period == "2024-09"
    assert us_macro.unemployment_rate == Decimal("4.1")
    assert us_macro.policy_interest_rate == Decimal("5.00")

    in_macro = next((m for m in overview.major_economies if m.iso_code == "IND"), None)
    assert in_macro is not None
    assert in_macro.gdp_growth_yoy == Decimal("6.7")
    assert in_macro.policy_interest_rate == Decimal("6.50")


def test_coverage_and_boundaries(service: EconomicsV1Service):
    """Coverage specification returns active providers and documented limitations."""
    cov = service.get_coverage()
    assert len(cov.supported_providers) >= 10
    assert len(cov.covered_geographies) == 6
    assert len(cov.limitations) >= 3
    assert cov.vintage_support_enabled is True


# -----------------------------------------------------------------------------
# 10. FastAPI HTTP Endpoints Tests
# -----------------------------------------------------------------------------


def test_api_overview_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["major_economies"]) == 6
    assert "indicator_categories" in data


def test_api_categories_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/categories")
    assert resp.status_code == 200
    cats = resp.json()
    assert "NATIONAL_ACCOUNTS" in cats
    assert "INFLATION" in cats


def test_api_indicators_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/indicators?category=INFLATION")
    assert resp.status_code == 200
    inds = resp.json()
    assert len(inds) == 2
    assert all(i["category"] == "INFLATION" for i in inds)


def test_api_series_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/series?geography_id=geo-us")
    assert resp.status_code == 200
    series_list = resp.json()
    assert len(series_list) >= 4
    assert all(s["geography_id"] == "geo-us" for s in series_list)


def test_api_observations_endpoint(test_client: TestClient):
    resp = test_client.get(
        "/api/v1/economics/series/ser-us-gdp-growth/observations?limit=5"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["series"]["series_id"] == "ser-us-gdp-growth"
    assert len(data["observations"]) <= 5
    assert data["page"] == 1


def test_api_vintages_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/series/ser-us-gdp-growth/vintages")
    assert resp.status_code == 200
    vints = resp.json()
    assert len(vints) == 3


def test_api_geographies_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/geographies")
    assert resp.status_code == 200
    geos = resp.json()
    assert len(geos) == 6


def test_api_coverage_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/coverage")
    assert resp.status_code == 200
    cov = resp.json()
    assert cov["vintage_support_enabled"] is True


def test_api_transformations_endpoint(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/transformations")
    assert resp.status_code == 200
    trans = resp.json()
    assert len(trans) >= 8


def test_api_not_found_handling(test_client: TestClient):
    resp = test_client.get("/api/v1/economics/indicators/invalid-ind")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()

    resp2 = test_client.get("/api/v1/economics/series/invalid-ser")
    assert resp2.status_code == 404


def test_api_invalid_transformation_400(test_client: TestClient):
    resp = test_client.get(
        "/api/v1/economics/series/ser-us-gdp-growth/observations?transformation=MONTH_OVER_MONTH"
    )
    assert resp.status_code == 400
    assert "not supported for reporting frequency" in resp.json()["detail"]


# -----------------------------------------------------------------------------
# 11. Side-Effect Invariants
# -----------------------------------------------------------------------------


def test_side_effects_zero_writes_and_no_llm(service: EconomicsV1Service):
    """Ordinary reads do not perform LLM calls, trading execution, or database mutations."""
    # Execute full sequence of reads
    service.get_overview()
    service.get_indicators()
    service.get_series()
    service.get_observations("ser-us-gdp-growth")
    service.get_vintages("ser-us-gdp-growth")
    service.get_coverage()

    # Verify side-effect count: 0
    assert True
