"""ATLAS Financial Risk Foundation Tests (Stage 115).

Verifies mathematical reference fixtures, volatility calculations, drawdown analytics,
benchmark sensitivity, covariance-based Euler risk contributions, REST APIs,
and strict multi-tenant isolation.
"""

from datetime import datetime, timedelta
import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios.models import Portfolio
from atlas.portfolios.service import PortfolioService
from atlas.risk.benchmark import BenchmarkSensitivityEngine
from atlas.risk.covariance_risk import ModelRiskEngine
from atlas.risk.drawdown import DrawdownEngine
from atlas.risk.enums import (
    AnnualizationPolicy,
    DrawdownEpisodeStatus,
    RiskCalculationStatus,
    RiskMetricStatus,
    RiskReturnFrequency,
)
from atlas.risk.errors import (
    RiskBenchmarkVarianceZeroError,
    RiskCorrelationUndefinedError,
    RiskInsufficientObservationsError,
)
from atlas.risk.multi_currency import MultiCurrencyRiskEngine
from atlas.risk.reconciliation import RiskReconciliationEngine
from atlas.risk.schemas import CalculateRiskRequest
from atlas.risk.service import RiskService
from atlas.risk.volatility import HistoricalVolatilityEngine
from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user


# -------------------------------------------------------------------------
# Test Fixtures & Mocks
# -------------------------------------------------------------------------

USER_A_ID = "usr_risk_test_a_123"
USER_B_ID = "usr_risk_test_b_456"

user_a_principal = AuthPrincipal(
    sub=USER_A_ID,
    email="risk_lead@atlas.institution",
    role="authenticated",
)

user_b_principal = AuthPrincipal(
    sub=USER_B_ID,
    email="unauthorized_b@other.firm",
    role="authenticated",
)


@pytest.fixture
def risk_services():
    p_service = PortfolioService()
    r_service = RiskService(portfolio_service=p_service)
    return p_service, r_service


@pytest.fixture
def client_user_a(risk_services):
    p_service, r_service = risk_services
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: user_a_principal
    from atlas_api.routers.risk import get_portfolio_service, get_risk_service
    app.dependency_overrides[get_portfolio_service] = lambda: p_service
    app.dependency_overrides[get_risk_service] = lambda: r_service
    return TestClient(app)


@pytest.fixture
def client_user_b(risk_services):
    p_service, r_service = risk_services
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: user_b_principal
    from atlas_api.routers.risk import get_portfolio_service, get_risk_service
    app.dependency_overrides[get_portfolio_service] = lambda: p_service
    app.dependency_overrides[get_risk_service] = lambda: r_service
    return TestClient(app)


# -------------------------------------------------------------------------
# 1. Historical Volatility Engine & Part XV Reference Fixture
# -------------------------------------------------------------------------


def test_volatility_reference_fixture_part_xv():
    """Validates Part XV exact reference fixture: returns [+1%, -1%, +1%, -1%].

    Expected:
        Mean = 0.0
        Sample Variance = 4 * (0.01)^2 / 3 = 0.0004 / 3 ≈ 0.000133333333
        Sample Volatility = sqrt(0.0004 / 3) ≈ 0.01154700538
        Annualized Volatility (K=252) = s * sqrt(252) ≈ 0.1833030278 (18.3303%)
    """
    returns = [0.01, -0.01, 0.01, -0.01]

    mean = HistoricalVolatilityEngine.compute_sample_mean(returns)
    assert abs(mean - 0.0) < 1e-12

    var, period_vol, ann_vol = HistoricalVolatilityEngine.compute_realized_volatility(
        returns, annualization_factor=252.0
    )

    expected_var = 0.0004 / 3.0
    expected_period_vol = math.sqrt(expected_var)
    expected_ann_vol = expected_period_vol * math.sqrt(252.0)

    assert abs(var - expected_var) < 1e-9
    assert abs(period_vol - expected_period_vol) < 1e-9
    assert abs(ann_vol - expected_ann_vol) < 1e-6
    assert abs(ann_vol - 0.1833030278) < 1e-5


def test_volatility_insufficient_observations():
    """Fewer than 2 observations must raise RiskInsufficientObservationsError (never fake 0)."""
    with pytest.raises(RiskInsufficientObservationsError):
        HistoricalVolatilityEngine.compute_realized_volatility([0.05])

    with pytest.raises(RiskInsufficientObservationsError):
        HistoricalVolatilityEngine.compute_realized_volatility([])


def test_rolling_volatility_no_hindsight_leakage():
    """Rolling volatility must compute over trailing windows without future information."""
    now = datetime(2026, 1, 1)
    dates = [now + timedelta(days=i) for i in range(50)]
    returns = [0.005 * (-1 if i % 2 == 0 else 1) for i in range(50)]

    rolling = HistoricalVolatilityEngine.compute_rolling_volatility(
        timestamps=dates, returns=returns, window_size=20, annualization_factor=252.0
    )

    # 50 total observations with window size 20 produces exactly 31 rolling points
    assert len(rolling) == 31
    assert rolling[0].window_end == dates[19]
    assert rolling[-1].window_end == dates[49]
    assert all(r.observation_count == 20 for r in rolling)


# -------------------------------------------------------------------------
# 2. Drawdown Analytics & Part XXI Reference Fixture
# -------------------------------------------------------------------------


def test_drawdown_reference_fixture_part_xxi():
    """Validates Part XXI exact reference fixture: wealth index [100, 120, 90, 99, 130].

    Expected:
        P = [100, 120, 120, 120, 130]
        D = [0%, 0%, -25%, -17.5%, 0%]
        Maximum Drawdown = -25%
        Recovery Observed = True (at index 4)
    """
    wealth = [100.0, 120.0, 90.0, 99.0, 130.0]
    peaks, drawdowns = DrawdownEngine.compute_drawdown_series(wealth)

    assert peaks == [100.0, 120.0, 120.0, 120.0, 130.0]
    assert drawdowns[0] == 0.0
    assert drawdowns[1] == 0.0
    assert abs(drawdowns[2] - (-0.25)) < 1e-9
    assert abs(drawdowns[3] - (-0.175)) < 1e-9
    assert drawdowns[4] == 0.0

    mdd = DrawdownEngine.compute_maximum_drawdown(drawdowns)
    assert abs(mdd - (-0.25)) < 1e-9

    # Episode extraction
    t0 = datetime(2026, 1, 1)
    dates = [t0 + timedelta(days=i * 10) for i in range(5)]
    episodes = DrawdownEngine.extract_drawdown_episodes(dates, wealth)

    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.peak_value == 120.0
    assert ep.trough_value == 90.0
    assert abs(ep.max_drawdown - (-0.25)) < 1e-9
    assert ep.status == DrawdownEpisodeStatus.RECOVERED
    assert ep.recovery_date == dates[4]


def test_ongoing_unrecovered_drawdown():
    """Unrecovered ongoing drawdown must retain status ONGOING and recovery_date None."""
    wealth = [100.0, 110.0, 80.0, 85.0]
    t0 = datetime(2026, 1, 1)
    dates = [t0 + timedelta(days=i * 10) for i in range(4)]

    episodes = DrawdownEngine.extract_drawdown_episodes(dates, wealth)
    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.status == DrawdownEpisodeStatus.ONGOING
    assert ep.recovery_date is None
    assert abs(ep.max_drawdown - (80.0 / 110.0 - 1.0)) < 1e-6


# -------------------------------------------------------------------------
# 3. Benchmark Sensitivity & Part XXVIII Reference Fixture
# -------------------------------------------------------------------------


def test_benchmark_sensitivity_reference_fixture_part_xxviii():
    """Validates Part XXVIII exact reference fixture: R_P = 2 * R_B.

    Benchmark = [-2%, -1%, +1%, +2%]
    Portfolio = [-4%, -2%, +2%, +4%]
    Expected:
        Beta = 2.0
        Correlation = 1.0
    """
    b_returns = [-0.02, -0.01, 0.01, 0.02]
    p_returns = [-0.04, -0.02, 0.02, 0.04]

    beta = BenchmarkSensitivityEngine.compute_beta(p_returns, b_returns)
    corr = BenchmarkSensitivityEngine.compute_correlation(p_returns, b_returns)

    assert abs(beta - 2.0) < 1e-9
    assert abs(corr - 1.0) < 1e-9


def test_zero_benchmark_variance_behavior():
    """Benchmark with zero return variance must raise RiskBenchmarkVarianceZeroError (never fake 0)."""
    b_returns = [0.01, 0.01, 0.01, 0.01]
    p_returns = [0.02, -0.01, 0.03, -0.02]

    with pytest.raises(RiskBenchmarkVarianceZeroError):
        BenchmarkSensitivityEngine.compute_beta(p_returns, b_returns)


# -------------------------------------------------------------------------
# 4. Covariance Model Risk & Part XXXV / XL Reference Fixture
# -------------------------------------------------------------------------


def test_model_volatility_and_risk_contributions_reference_fixture():
    """Validates Part XXXV & XL reference fixture: 2 uncorrelated assets.

    Sigma = diag(0.04, 0.09)
    w = [0.5, 0.5]

    Expected:
        Variance = 0.5^2(0.04) + 0.5^2(0.09) = 0.0325
        Volatility = sqrt(0.0325) ≈ 0.1802775638 (18.027756%)
        VC_A = 0.01, VC_B = 0.0225 -> Sum = 0.0325
        CRC_A = 0.01 / sqrt(0.0325) ≈ 0.0554700
        CRC_B = 0.0225 / sqrt(0.0325) ≈ 0.1248075 -> Sum = sqrt(0.0325)
        PCR_A = 4/13 ≈ 30.7692%, PCR_B = 9/13 ≈ 69.2308% -> Sum = 100%
    """
    symbols = ["ASSET_A", "ASSET_B"]
    cov = np.array([[0.04, 0.0], [0.0, 0.09]], dtype=float)
    weights = np.array([0.5, 0.5], dtype=float)

    var = ModelRiskEngine.compute_portfolio_variance(weights, cov)
    vol = ModelRiskEngine.compute_portfolio_volatility(weights, cov)

    assert abs(var - 0.0325) < 1e-9
    assert abs(vol - math.sqrt(0.0325)) < 1e-9
    assert abs(vol - 0.1802775638) < 1e-6

    var_out, vol_out, contributions = ModelRiskEngine.compute_risk_contributions(
        symbols=symbols,
        names=["Asset A", "Asset B"],
        categories=["Tech", "Health"],
        weights=weights,
        covariance=cov,
    )

    assert abs(var_out - 0.0325) < 1e-9
    assert abs(vol_out - vol) < 1e-9
    assert len(contributions) == 2

    c_a = contributions[0]
    c_b = contributions[1]

    # Variance contributions
    assert abs(c_a.variance_contribution - 0.01) < 1e-9
    assert abs(c_b.variance_contribution - 0.0225) < 1e-9
    assert abs((c_a.variance_contribution + c_b.variance_contribution) - 0.0325) < 1e-9

    # Component volatility contributions (Euler additivity)
    expected_crc_a = 0.01 / math.sqrt(0.0325)
    expected_crc_b = 0.0225 / math.sqrt(0.0325)
    assert abs(c_a.component_volatility_contribution - expected_crc_a) < 1e-9
    assert abs(c_b.component_volatility_contribution - expected_crc_b) < 1e-9
    assert abs((c_a.component_volatility_contribution + c_b.component_volatility_contribution) - vol) < 1e-9

    # Percentage contributions
    assert abs(c_a.percentage_volatility_contribution - (4.0 / 13.0)) < 1e-6
    assert abs(c_b.percentage_volatility_contribution - (9.0 / 13.0)) < 1e-6
    assert abs((c_a.percentage_volatility_contribution + c_b.percentage_volatility_contribution) - 1.0) < 1e-6

    # Euler reconciliation engine check
    is_reconciled, errors = RiskReconciliationEngine.reconcile_risk_contributions(
        model_variance=var,
        model_volatility=vol,
        contributions=contributions,
    )
    assert is_reconciled
    assert len(errors) == 0


def test_multi_currency_composition():
    """Validates multi-currency compounding: 1 + R_base = (1 + R_local) * (1 + R_FX)."""
    r_local = 0.10
    r_fx = 0.125
    r_base = MultiCurrencyRiskEngine.compose_base_return(r_local, r_fx)
    assert abs(r_base - 0.2375) < 1e-9


# -------------------------------------------------------------------------
# 5. REST APIs & Service Lifecycle Tests
# -------------------------------------------------------------------------


def test_rest_api_metrics_and_models(client_user_a):
    """GET /api/v1/risk/metrics and /models returns canonical catalog."""
    res_m = client_user_a.get("/api/v1/risk/metrics")
    assert res_m.status_code == 200
    metrics = res_m.json()
    assert len(metrics) >= 10
    codes = [m["metric_code"] for m in metrics]
    assert "HISTORICAL_REALIZED_VOLATILITY" in codes
    assert "HISTORICAL_MAX_DRAWDOWN" in codes
    assert "BENCHMARK_BETA" in codes

    res_models = client_user_a.get("/api/v1/risk/models")
    assert res_models.status_code == 200
    models = res_models.json()
    assert len(models) >= 4


def test_rest_api_portfolio_risk_flow(client_user_a, risk_services):
    """End-to-end execution of risk calculation, summary, volatility, drawdowns, and contributions."""
    p_service, r_service = risk_services
    # Create test portfolio for User A
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Global Tech Alpha",
            "base_currency": "USD",
            "description": "Risk Test Portfolio",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
        })(),
    )

    # 1. GET Summary (triggers auto-calculation if none exists)
    res_sum = client_user_a.get(f"/api/v1/risk/portfolios/{p.id}")
    assert res_sum.status_code == 200
    summary = res_sum.json()
    assert summary["portfolio_id"] == p.id
    assert summary["historical_volatility"] is not None
    assert summary["max_drawdown"] is not None
    assert summary["coverage_ratio"] > 0

    # 2. GET Volatility
    res_vol = client_user_a.get(f"/api/v1/risk/portfolios/{p.id}/volatility")
    assert res_vol.status_code == 200
    vol_data = res_vol.json()
    assert vol_data["historical_volatility_annualized"] is not None
    assert len(vol_data["rolling_series"]) > 0

    # 3. GET Drawdowns
    res_dd = client_user_a.get(f"/api/v1/risk/portfolios/{p.id}/drawdowns")
    assert res_dd.status_code == 200
    dd_data = res_dd.json()
    assert dd_data["max_drawdown"] is not None
    assert len(dd_data["drawdown_series"]) > 0

    # 4. GET Benchmark Sensitivity
    res_bench = client_user_a.get(f"/api/v1/risk/portfolios/{p.id}/benchmark")
    assert res_bench.status_code == 200
    b_data = res_bench.json()
    assert b_data["beta"] is not None
    assert b_data["correlation"] is not None

    # 5. GET Contributions
    res_cont = client_user_a.get(f"/api/v1/risk/portfolios/{p.id}/contributions")
    assert res_cont.status_code == 200
    c_data = res_cont.json()
    assert c_data["model_volatility"] is not None
    assert len(c_data["contributions"]) > 0

    # 6. GET Data Quality
    res_q = client_user_a.get(f"/api/v1/risk/portfolios/{p.id}/quality")
    assert res_q.status_code == 200
    q_data = res_q.json()
    assert q_data["coverage_ratio"] > 0

    # 7. GET Runs List
    res_runs = client_user_a.get(f"/api/v1/risk/portfolios/{p.id}/runs")
    assert res_runs.status_code == 200
    runs = res_runs.json()
    assert runs["total"] >= 1


def test_multi_tenant_isolation(client_user_a, client_user_b, risk_services):
    """User B must be rejected (HTTP 404 or 403) when attempting to access User A's risk calculations."""
    p_service, r_service = risk_services
    p_a = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Secret Wealth Fund",
            "base_currency": "USD",
            "description": "User A Private",
            "portfolio_type": "INVESTMENT",
            "cost_basis_method": "FIFO",
        })(),
    )

    # User B attempting to view User A's risk
    res = client_user_b.get(f"/api/v1/risk/portfolios/{p_a.id}")
    assert res.status_code in (403, 404)

    # User B attempting to calculate risk on User A's portfolio
    res_calc = client_user_b.post(
        "/api/v1/risk/calculations",
        json={"subject_id": p_a.id, "subject_type": "PORTFOLIO"},
    )
    assert res_calc.status_code in (403, 404)
