"""Comprehensive Automated Test Suite for Macroeconomic Comparisons & Benchmarking (Stage 93)."""

import pytest
from atlas.economics.comparisons import (
    CohortAggregateRequestDTO,
    ComparisonMatrixRequestDTO,
    ComparisonMetricKind,
    CompatibilityStatus,
    CorrelationAnalysisRequestDTO,
    CorrelationMethod,
    DistributionStatisticsRequestDTO,
    DivergenceAnalysisRequestDTO,
    EconomicRankingsRequestDTO,
    HistoricalTrendsRequestDTO,
    MacroComparisonQueryLimitExceededError,
    MacroComparisonsRepository,
    MacroComparisonsService,
    PeriodAlignmentPolicy,
    RankingDirection,
    TieBreakerPolicy,
    WeightingPolicy,
)

from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.routers.macro_comparisons import (
    get_comparison_service,
)
from atlas_api.routers.macro_comparisons import (
    router as macro_comparisons_router,
)


@pytest.fixture
def repo():
    return MacroComparisonsRepository()


@pytest.fixture
def service(repo):
    return MacroComparisonsService(repo=repo)


@pytest.fixture
def client(service: MacroComparisonsService) -> TestClient:
    app = FastAPI()
    app.include_router(macro_comparisons_router)
    app.dependency_overrides[get_comparison_service] = lambda: service
    return TestClient(app)


# =============================================================================
# 1. Country Identity & Cohorts
# =============================================================================

def test_country_identity_and_cohort_discovery(service: MacroComparisonsService):
    """Test discovery of sovereign economies and canonical cohorts."""
    geos = service.list_geographies()
    assert len(geos) == 6
    geo_ids = {g["geography_id"] for g in geos}
    assert {"geo-us", "geo-ea", "geo-gb", "geo-jp", "geo-in", "geo-cn"}.issubset(geo_ids)

    cohorts = service.list_cohorts()
    assert len(cohorts) >= 4
    cohort_ids = {c.cohort_id for c in cohorts}
    assert "cohort-g7" in cohort_ids
    assert "cohort-g20" in cohort_ids
    assert "cohort-brics" in cohort_ids


# =============================================================================
# 2. Indicator Compatibility & Eligibility
# =============================================================================

def test_indicator_compatibility_and_eligibility(service: MacroComparisonsService):
    """Test compatibility evaluation and caveats."""
    # US Nominal GDP should be directly comparable
    elig_us_gdp = service.check_eligibility("geo-us", ComparisonMetricKind.GDP_NOMINAL_USD)
    assert elig_us_gdp.is_eligible is True
    assert elig_us_gdp.status == CompatibilityStatus.DIRECTLY_COMPARABLE

    # Euro Area CPI has qualification caveat (HICP)
    elig_ea_cpi = service.check_eligibility("geo-ea", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY)
    assert elig_ea_cpi.is_eligible is True
    assert elig_ea_cpi.status == CompatibilityStatus.COMPARABLE_WITH_QUALIFICATION
    assert any("HICP" in c for c in elig_ea_cpi.caveats)

    # Invalid country
    elig_invalid = service.check_eligibility("geo-atlantis", ComparisonMetricKind.GDP_NOMINAL_USD)
    assert elig_invalid.is_eligible is False
    assert elig_invalid.status == CompatibilityStatus.INCOMPATIBLE


# =============================================================================
# 3. Comparison Matrix
# =============================================================================

def test_comparison_matrix_generation(service: MacroComparisonsService):
    """Test high-density cross-country matrix generation."""
    req = ComparisonMatrixRequestDTO(
        geography_ids=["geo-us", "geo-ea", "geo-in"],
        metric_kinds=[
            ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
            ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY,
            ComparisonMetricKind.POLICY_INTEREST_RATE,
        ],
        period_policy=PeriodAlignmentPolicy.LATEST_PER_COUNTRY,
    )
    matrix = service.get_comparison_matrix(req)
    assert matrix.total_countries == 3
    assert len(matrix.cells) == 9  # 3 countries * 3 metrics

    # Verify India GDP growth cell
    in_growth_cell = next(
        c for c in matrix.cells
        if c.geography_id == "geo-in" and c.metric_kind == ComparisonMetricKind.GDP_REAL_GROWTH_YOY
    )
    assert in_growth_cell.raw_value == 6.7
    assert in_growth_cell.unit == "PERCENT"


# =============================================================================
# 4. Economic Rankings & Ties
# =============================================================================

def test_economic_rankings_and_tie_breaking(service: MacroComparisonsService):
    """Test sovereign ranking computation with ascending and descending directions."""
    # 1. Real GDP Growth (Descending: highest growth is #1)
    req_growth = EconomicRankingsRequestDTO(
        metric_kind=ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
        direction=RankingDirection.DESCENDING,
        tie_policy=TieBreakerPolicy.STANDARD_COMPETITION,
    )
    res_growth = service.calculate_rankings(req_growth)
    assert res_growth.total_eligible == 6
    # India (6.7%) should be rank 1
    assert res_growth.rankings[0].country_name == "India"
    assert res_growth.rankings[0].rank == 1

    # 2. Headline Inflation (Ascending: lowest inflation is #1)
    req_infl = EconomicRankingsRequestDTO(
        metric_kind=ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY,
        direction=RankingDirection.ASCENDING,
        tie_policy=TieBreakerPolicy.STANDARD_COMPETITION,
    )
    res_infl = service.calculate_rankings(req_infl)
    # China (0.4%) should be rank 1
    assert res_infl.rankings[0].country_name == "China"
    assert res_infl.rankings[0].rank == 1


# =============================================================================
# 5. Distribution Statistics
# =============================================================================

def test_distribution_statistics(service: MacroComparisonsService):
    """Test mean, median, quartiles, and sample standard deviation."""
    req = DistributionStatisticsRequestDTO(
        metric_kind=ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
        geography_ids=["geo-us", "geo-ea", "geo-gb", "geo-jp", "geo-in", "geo-cn"],
        weighting_policy=WeightingPolicy.EQUAL_WEIGHT,
    )
    dist = service.calculate_distributions(req)
    assert dist.sample_size == 6
    # Values: 2.8 (US), 0.9 (EA), 1.1 (GB), 0.3 (JP), 6.7 (IN), 4.8 (CN)
    # Mean: (2.8 + 0.9 + 1.1 + 0.3 + 6.7 + 4.8) / 6 = 16.6 / 6 = 2.7667
    assert pytest.approx(dist.mean, 0.01) == 2.77
    assert dist.minimum == 0.3
    assert dist.maximum == 6.7
    assert dist.median > dist.minimum
    assert dist.q1 <= dist.median <= dist.q3
    assert dist.standard_deviation > 0.0


def test_distribution_weighting(service: MacroComparisonsService):
    """Test population-weighted distribution mean calculation."""
    req_pop = DistributionStatisticsRequestDTO(
        metric_kind=ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
        geography_ids=["geo-us", "geo-in"],  # US: 2.8% (336M pop), India: 6.7% (1440M pop)
        weighting_policy=WeightingPolicy.POPULATION_WEIGHT,
    )
    dist_pop = service.calculate_distributions(req_pop)
    # Expected weighted mean: (2.8 * 336 + 6.7 * 1440) / (336 + 1440) = (940.8 + 9648) / 1776 = 10588.8 / 1776 = 5.962
    assert pytest.approx(dist_pop.mean, 0.05) == 5.96


# =============================================================================
# 6. Historical Trends & Normalization
# =============================================================================

def test_historical_trends_and_base_indexing(service: MacroComparisonsService):
    """Test multi-country historical time series and index-to-100 normalization."""
    # 1. Raw historical trend
    req_raw = HistoricalTrendsRequestDTO(
        metric_kind=ComparisonMetricKind.GDP_NOMINAL_USD,
        geography_ids=["geo-us", "geo-cn"],
        start_period="2021",
        end_period="2024",
    )
    res_raw = service.get_historical_trends(req_raw)
    assert len(res_raw.points) >= 8
    assert "2021" in res_raw.common_periods
    assert "2024" in res_raw.common_periods

    # 2. Normalized to base period 2021 = 100
    req_indexed = HistoricalTrendsRequestDTO(
        metric_kind=ComparisonMetricKind.GDP_NOMINAL_USD,
        geography_ids=["geo-us", "geo-cn"],
        base_period="2021",
    )
    res_indexed = service.get_historical_trends(req_indexed)
    us_2021 = next(p for p in res_indexed.points if p.geography_id == "geo-us" and p.reference_period == "2021")
    assert us_2021.indexed_value == 100.0

    us_2024 = next(p for p in res_indexed.points if p.geography_id == "geo-us" and p.reference_period == "2024")
    # US GDP 2021 = 23315, 2024 = 28781.1 -> (28781.1 / 23315) * 100 = 123.44
    assert pytest.approx(us_2024.indexed_value, 0.1) == 123.44


# =============================================================================
# 7. Pairwise Divergence
# =============================================================================

def test_pairwise_divergence_analysis(service: MacroComparisonsService):
    """Test divergence differentials between US and Euro Area inflation."""
    req = DivergenceAnalysisRequestDTO(
        metric_kind=ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY,
        geography_a_id="geo-us",
        geography_b_id="geo-ea",
        start_period="2021",
        end_period="2024",
    )
    div = service.calculate_divergence(req)
    assert div.country_a_name == "United States"
    assert div.country_b_name == "Euro Area"
    assert len(div.points) >= 4

    p_2024 = next(p for p in div.points if p.reference_period == "2024")
    # US 2024: 2.6%, Euro Area 2024: 2.0% -> Diff = +0.6 percentage points
    assert pytest.approx(p_2024.differential_value, 0.01) == 0.6
    assert pytest.approx(p_2024.ratio, 0.01) == 1.3


# =============================================================================
# 8. Correlation Analysis
# =============================================================================

def test_correlation_analysis(service: MacroComparisonsService):
    """Test Pearson and Spearman correlation across aligned time series."""
    req = CorrelationAnalysisRequestDTO(
        series_pairs=[
            {
                "geo_a": "geo-us",
                "metric_a": ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
                "geo_b": "geo-ea",
                "metric_b": ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
            }
        ],
        method=CorrelationMethod.PEARSON,
    )
    res = service.calculate_correlations(req)
    assert len(res.results) == 1
    corr = res.results[0]
    assert corr.is_valid is True
    assert corr.sample_size == 4
    assert -1.0 <= corr.coefficient <= 1.0
    assert any("causality" in w for w in corr.warnings)


def test_correlation_guards(service: MacroComparisonsService):
    """Test correlation minimum sample size and zero-variance guards."""
    # Constant series (zero variance)
    req = CorrelationAnalysisRequestDTO(
        series_pairs=[
            {
                "geo_a": "geo-us",
                "metric_a": "INVALID_METRIC",
                "geo_b": "geo-ea",
                "metric_b": "INVALID_METRIC",
            }
        ],
    )
    res = service.calculate_correlations(req)
    assert len(res.results) == 0


# =============================================================================
# 9. Query Limits & Coverage
# =============================================================================

def test_query_limits_enforced(service: MacroComparisonsService):
    """Test that query limits protect backend performance."""
    oversized_geos = [f"geo-{i}" for i in range(30)]
    req = ComparisonMatrixRequestDTO(geography_ids=oversized_geos)
    with pytest.raises(MacroComparisonQueryLimitExceededError):
        service.get_comparison_matrix(req)


def test_coverage_summary(service: MacroComparisonsService):
    """Test coverage summary across sovereign economies and harmonized providers."""
    cov = service.get_coverage_summary()
    assert len(cov.supported_geographies) == 6
    assert len(cov.supported_metrics) >= 15
    assert cov.total_observations_count > 50
    assert len(cov.harmonized_sources) >= 5


# =============================================================================
# 10. FastAPI REST API Integration
# =============================================================================

def test_rest_api_endpoints(client: TestClient):
    """Test all Macro Comparisons HTTP endpoints."""
    # 1. GET /indicators
    res_ind = client.get("/api/v1/economics/comparisons/indicators")
    assert res_ind.status_code == 200
    assert len(res_ind.json()) >= 15

    # 2. GET /geographies
    res_geo = client.get("/api/v1/economics/comparisons/geographies")
    assert res_geo.status_code == 200
    assert len(res_geo.json()) == 6

    # 3. GET /cohorts
    res_coh = client.get("/api/v1/economics/comparisons/cohorts")
    assert res_coh.status_code == 200
    assert len(res_coh.json()) >= 4

    # 4. POST /eligibility
    res_elig = client.post(
        "/api/v1/economics/comparisons/eligibility?geography_id=geo-us&metric_kind=GDP_REAL_GROWTH_YOY"
    )
    assert res_elig.status_code == 200
    assert res_elig.json()["is_eligible"] is True

    # 5. POST /matrix
    res_mat = client.post(
        "/api/v1/economics/comparisons/matrix",
        json={"geography_ids": ["geo-us", "geo-gb"], "metric_kinds": ["GDP_NOMINAL_USD"]},
    )
    assert res_mat.status_code == 200
    assert len(res_mat.json()["cells"]) == 2

    # 6. POST /rankings
    res_rank = client.post(
        "/api/v1/economics/comparisons/rankings",
        json={"metric_kind": "GDP_NOMINAL_USD", "direction": "DESCENDING"},
    )
    assert res_rank.status_code == 200
    assert len(res_rank.json()["rankings"]) == 6

    # 7. POST /distributions
    res_dist = client.post(
        "/api/v1/economics/comparisons/distributions",
        json={"metric_kind": "UNEMPLOYMENT_RATE"},
    )
    assert res_dist.status_code == 200
    assert res_dist.json()["mean"] > 0

    # 8. POST /history
    res_hist = client.post(
        "/api/v1/economics/comparisons/history",
        json={"metric_kind": "GDP_REAL_GROWTH_YOY", "geography_ids": ["geo-us", "geo-in"]},
    )
    assert res_hist.status_code == 200
    assert len(res_hist.json()["points"]) >= 8

    # 9. POST /divergence
    res_div = client.post(
        "/api/v1/economics/comparisons/divergence",
        json={"metric_kind": "POLICY_INTEREST_RATE", "geography_a_id": "geo-us", "geography_b_id": "geo-jp"},
    )
    assert res_div.status_code == 200
    assert "differential_value" in res_div.json()["points"][-1]

    # 10. POST /correlations
    res_corr = client.post(
        "/api/v1/economics/comparisons/correlations",
        json={
            "series_pairs": [
                {
                    "geo_a": "geo-us",
                    "metric_a": "GDP_NOMINAL_USD",
                    "geo_b": "geo-ea",
                    "metric_b": "GDP_NOMINAL_USD",
                }
            ],
            "method": "PEARSON",
        },
    )
    assert res_corr.status_code == 200
    assert res_corr.json()["results"][0]["is_valid"] is True

    # 11. GET /coverage
    res_cov = client.get("/api/v1/economics/comparisons/coverage")
    assert res_cov.status_code == 200
    assert res_cov.json()["total_observations_count"] > 50


# =============================================================================
# 11. Side-Effect Free Reads
# =============================================================================

def test_zero_read_side_effects(client: TestClient, repo: MacroComparisonsRepository):
    """Verify comparison read queries cause zero canonical mutations."""
    initial_count = len(repo._observations)
    client.get("/api/v1/economics/comparisons/indicators")
    client.post("/api/v1/economics/comparisons/matrix", json={})
    client.post("/api/v1/economics/comparisons/rankings", json={"metric_kind": "GDP_REAL_GROWTH_YOY"})
    assert len(repo._observations) == initial_count


# =============================================================================
# 12. Regional Aggregates & Overlap Protection
# =============================================================================

def test_cohort_aggregates_computation(service: MacroComparisonsService, client: TestClient):
    """Test regional and group macroeconomic aggregation with overlap protection."""
    # 1. Level sum (Nominal GDP USD for G7 economies)
    req_sum = CohortAggregateRequestDTO(
        cohort_id="cohort-g7",
        metric_kind=ComparisonMetricKind.GDP_NOMINAL_USD,
        period="2024",
    )
    agg_sum = service.calculate_aggregates(req_sum)
    assert agg_sum.is_valid is True
    assert agg_sum.aggregate_type == "SUM"
    # US (28781.1) + GB (3495.0) + JP (4210.0) = 36486.1
    assert pytest.approx(agg_sum.value, 0.1) == 36486.1

    # 2. Growth rate (GDP-weighted growth, not arithmetic sum!)
    req_growth = CohortAggregateRequestDTO(
        cohort_id="cohort-g7",
        metric_kind=ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
        period="2024",
    )
    agg_growth = service.calculate_aggregates(req_growth)
    assert agg_growth.is_valid is True
    assert agg_growth.aggregate_type == "GDP_WEIGHTED_GROWTH"
    assert any("cannot be summed arithmetically" in n for n in agg_growth.notes)

    # 3. HTTP endpoint POST /api/v1/economics/comparisons/aggregates
    res_agg = client.post(
        "/api/v1/economics/comparisons/aggregates",
        json={"cohort_id": "cohort-g7", "metric_kind": "GDP_NOMINAL_USD"},
    )
    assert res_agg.status_code == 200
    assert res_agg.json()["value"] > 30000.0


# =============================================================================
# 13. Case-Insensitive Enums & Aliases
# =============================================================================

def test_case_insensitive_enum_resolution(service: MacroComparisonsService, client: TestClient):
    """Test case-insensitive resolution of metric kinds, policies, and aliases."""
    # Lowercase in REST matrix query
    res_mat = client.post(
        "/api/v1/economics/comparisons/matrix",
        json={
            "geography_ids": ["geo-us", "geo-gb"],
            "metric_kinds": ["gdp_real_growth_yoy", "cpi_headline_yoy"],
            "period_policy": "latest_per_country",
        },
    )
    assert res_mat.status_code == 200
    assert len(res_mat.json()["cells"]) == 4

    # POST body eligibility check
    res_elig = client.post(
        "/api/v1/economics/comparisons/eligibility",
        json={"geography_id": "geo-us", "metric_kind": "gdp_nominal_usd"},
    )
    assert res_elig.status_code == 200
    assert res_elig.json()["is_eligible"] is True

