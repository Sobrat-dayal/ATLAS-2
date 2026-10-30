"""Stage 116 — Value at Risk, Expected Shortfall, Scenario Testing & Diagnostics Tests.

Verifies:
1. Part XVI: Historical Simulation VaR and fractional tail Expected Shortfall fixture.
2. Part XX: Parametric Normal VaR and closed-form Expected Shortfall fixture.
3. Monte Carlo Gaussian simulation VaR/ES reproducibility, seed determinism, and ES >= VaR.
4. Part XXXIV: Multi-currency multiplicative compounding fixture ((1+s_p)*(1+s_fx)-1).
5. Part XLIII: Portfolio scenario shock evaluation and exact position/portfolio P&L reconciliation.
6. Shock collision priority precedence (Security overrides Sector overrides Portfolio).
7. Kupiec POF coverage likelihood ratio test, chi-square p-value, and sample adequacy.
8. FastAPI risk router endpoints for tail risk, scenario library, execution, comparison, and backtesting.
9. Strict multi-tenant isolation.
"""

from datetime import datetime
import math
from typing import Dict, List
import pytest
import numpy as np
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios.service import PortfolioService
from atlas.risk.enums import (
    ExpectedShortfallMethod,
    KupiecTestStatus,
    ScenarioShockType,
    ScenarioType,
    ShockTargetType,
    VaRModelType,
)
from atlas.risk.errors import (
    RiskScenarioNotFoundError,
    RiskScenarioShockInvalidError,
    RiskVaRConfidenceInvalidError,
    RiskVaRHorizonInvalidError,
)
from atlas.risk.models import (
    RiskScenario,
    ScenarioShock,
)
from atlas.risk.tail_var import TailRiskEngine
from atlas.risk.scenarios import ScenarioEngine, PREDEFINED_SCENARIOS
from atlas.risk.diagnostics import VaRDiagnosticsEngine
from atlas.risk.service import RiskService
from atlas.risk.schemas import (
    CalculateTailRiskRequest,
    CreateScenarioRequest,
    ExecuteScenarioRequest,
    RunVaRBacktestRequest,
    ScenarioComparisonRequest,
    ScenarioShockDTO,
)
from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user


USER_A_ID = "usr_stage116_test_a"
USER_B_ID = "usr_stage116_test_b"

user_a_principal = AuthPrincipal(
    sub=USER_A_ID,
    email="risk_officer@atlas.firm",
    role="authenticated",
)

user_b_principal = AuthPrincipal(
    sub=USER_B_ID,
    email="intruder@external.firm",
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


# ============================================================================
# 1. PART XVI: HISTORICAL SIMULATION FIXTURE
# ============================================================================

def test_historical_simulation_part_xvi_fixture():
    """Validates Part XVI Reference Fixture:
    Losses = [-0.02, -0.01, 0.00, +0.01, +0.03], N = 5, alpha = 0.80.
    Returns = [+0.02, +0.01, 0.00, -0.01, -0.03].
    k = ceil(0.80 * 5) = 4 -> VaR = +0.01 (+1.0%).
    Tail tail-weighted expectation -> ES = +0.03 (+3.0%).
    """
    returns = [+0.02, +0.01, 0.00, -0.01, -0.03]
    var_res, es_res, _ = TailRiskEngine.calculate_historical_var_and_es(
        returns=returns,
        confidence_level=0.80,
        horizon_days=1,
        baseline_portfolio_value=100_000.0,
        method=ExpectedShortfallMethod.EMPIRICAL_TAIL_MEAN,
    )

    # VaR return must be exactly 1.0%
    assert math.isclose(var_res.var_return, 0.01, rel_tol=1e-5)
    assert math.isclose(var_res.var_amount, 1000.0, rel_tol=1e-5)

    # Expected Shortfall return must be exactly 3.0%
    assert math.isclose(es_res.es_return, 0.03, rel_tol=1e-5)
    assert math.isclose(es_res.es_amount, 3000.0, rel_tol=1e-5)

    # Invariant: ES >= VaR
    assert es_res.es_return >= var_res.var_return


# ============================================================================
# 2. PART XX: PARAMETRIC NORMAL FIXTURE
# ============================================================================

def test_parametric_normal_part_xx_fixture():
    """Validates Part XX Reference Fixture:
    mu = 0, sigma = 0.02, alpha = 0.95.
    z_0.95 approx 1.6448536.
    VaR_0.95 = 0.02 * 1.6448536 = 3.289707% = 0.032897.
    ES_0.95 = 0.02 * phi(1.6448536) / 0.05 approx 4.1254%.
    """
    mu = 0.0
    sigma = 0.02
    alpha = 0.95

    var_res, es_res = TailRiskEngine.calculate_parametric_var_and_es(
        mean=mu,
        standard_deviation=sigma,
        confidence_level=alpha,
        horizon_days=1,
        baseline_portfolio_value=100_000.0,
    )

    expected_var = 0.02 * 1.6448536269514722
    assert math.isclose(var_res.var_return, expected_var, rel_tol=1e-4)
    assert math.isclose(var_res.var_amount, expected_var * 100_000.0, rel_tol=1e-4)

    # Invariant: ES strictly exceeds VaR under Gaussian continuous distribution
    assert es_res.es_return > var_res.var_return
    assert math.isclose(es_res.es_return, 0.041254, rel_tol=1e-3)


# ============================================================================
# 3. MONTE CARLO SIMULATION REPRODUCIBILITY & INVARIANTS
# ============================================================================

def test_monte_carlo_gaussian_reproducibility():
    """Validates Monte Carlo simulation produces deterministic results given a fixed seed,
    bounded paths, and maintains ES >= VaR."""
    weights = np.array([0.5, 0.5])
    means = np.array([0.0005, 0.0003])
    # 2x2 positive definite covariance matrix
    cov = np.array([
        [0.0004, 0.0001],
        [0.0001, 0.0003],
    ])

    var1, es1, dist1 = TailRiskEngine.calculate_monte_carlo_var_and_es(
        weights=weights,
        means=means,
        covariance_matrix=cov,
        num_simulations=1000,
        confidence_level=0.95,
        horizon_days=1,
        baseline_portfolio_value=500_000.0,
        seed=12345,
    )

    var2, es2, dist2 = TailRiskEngine.calculate_monte_carlo_var_and_es(
        weights=weights,
        means=means,
        covariance_matrix=cov,
        num_simulations=1000,
        confidence_level=0.95,
        horizon_days=1,
        baseline_portfolio_value=500_000.0,
        seed=12345,
    )

    # Exact deterministic identity across identical seeds
    assert math.isclose(var1.var_return, var2.var_return, abs_tol=1e-12)
    assert math.isclose(es1.es_return, es2.es_return, abs_tol=1e-12)

    # Mathematical Invariant
    assert es1.es_return >= var1.var_return
    assert var1.var_amount > 0.0


# ============================================================================
# 4. PART XXXIV: MULTI-CURRENCY COMPOUNDING FIXTURE
# ============================================================================

def test_multi_currency_compounding_part_xxxiv():
    """Validates Part XXXIV Reference Fixture:
    Local equity shock: -10% (-0.10).
    FX shock: -5% (-0.05).
    Compounded return = (1 - 0.10) * (1 - 0.05) - 1 = 0.855 - 1 = -0.145 (-14.5%).
    Loss is +14.5% (strictly distinct from linear addition -15%).
    """
    compounded = ScenarioEngine.compound_return_with_fx(price_shock=-0.10, fx_shock=-0.05)
    assert math.isclose(compounded, -0.145, rel_tol=1e-6)
    assert compounded != -0.150


# ============================================================================
# 5. PART XLIII: SCENARIO RECONCILIATION FIXTURE
# ============================================================================

def test_scenario_reconciliation_part_xliii_fixture():
    """Validates Part XLIII Scenario Reference Fixture:
    Baseline NAV: $100,000.
    Security A (60% weight, $60,000): -10% shock -> Delta V_A = -$6,000.
    Security B (40% weight, $40,000): +5% shock -> Delta V_B = +$2,000.
    Portfolio P&L: -$4,000.
    Shocked NAV: $96,000.
    Scenario Return: -4.0%.
    Strict reconciliation: sum Delta V_i == Delta V_P, discrepancy == 0.
    """
    positions = [
        {
            "instrument_id": "INST_A",
            "symbol": "AAPL",
            "name": "Apple Inc",
            "category_label": "Information Technology",
            "currency": "USD",
            "base_value": 60_000.0,
        },
        {
            "instrument_id": "INST_B",
            "symbol": "MSFT",
            "name": "Microsoft Corp",
            "category_label": "Information Technology",
            "currency": "USD",
            "base_value": 40_000.0,
        },
    ]

    scenario = RiskScenario(
        scenario_id="SCEN_CUSTOM_TEST",
        owner_user_id="USER_1",
        organization_id=None,
        name="Custom Dual Security Shock",
        description="A shocked -10%, B shocked +5%",
        scenario_type=ScenarioType.HYPOTHETICAL_USER_DEFINED,
        historical_episode_id=None,
        shocks=[
            ScenarioShock(
                shock_id="SHK_1",
                shock_type=ScenarioShockType.SECURITY_PRICE_PERCENT_SHOCK,
                target_type=ShockTargetType.SECURITY,
                target_id="AAPL",
                shock_value=-0.10,
                description="Apple -10%",
            ),
            ScenarioShock(
                shock_id="SHK_2",
                shock_type=ScenarioShockType.SECURITY_PRICE_PERCENT_SHOCK,
                target_type=ShockTargetType.SECURITY,
                target_id="MSFT",
                shock_value=+0.05,
                description="Microsoft +5%",
            ),
        ],
    )

    run = ScenarioEngine.evaluate_scenario(
        portfolio_positions=positions,
        portfolio_nav=100_000.0,
        scenario=scenario,
        portfolio_id="PORT_1",
    )

    assert math.isclose(run.baseline_nav, 100_000.0, rel_tol=1e-5)
    assert math.isclose(run.shocked_nav, 96_000.0, rel_tol=1e-5)
    assert math.isclose(run.portfolio_pnl, -4_000.0, rel_tol=1e-5)
    assert math.isclose(run.scenario_return, -0.04, rel_tol=1e-5)
    assert run.reconciled is True
    assert math.isclose(run.reconciliation_difference, 0.0, abs_tol=1e-7)

    # Position checks
    a_res = next(p for p in run.position_results if p.symbol == "AAPL")
    assert math.isclose(a_res.pnl, -6000.0, rel_tol=1e-5)
    assert math.isclose(a_res.shocked_value, 54000.0, rel_tol=1e-5)

    b_res = next(p for p in run.position_results if p.symbol == "MSFT")
    assert math.isclose(b_res.pnl, +2000.0, rel_tol=1e-5)
    assert math.isclose(b_res.shocked_value, 42000.0, rel_tol=1e-5)


# ============================================================================
# 6. SHOCK COLLISION PRECEDENCE TEST
# ============================================================================

def test_shock_collision_precedence():
    """Verifies that Security Shock overrides Sector Shock, which overrides Portfolio-wide Shock."""
    positions = [
        {
            "instrument_id": "INST_TECH_1",
            "symbol": "NVDA",
            "name": "Nvidia",
            "category_label": "Information Technology",
            "currency": "USD",
            "base_value": 50_000.0,
        },
        {
            "instrument_id": "INST_TECH_2",
            "symbol": "AMD",
            "name": "Advanced Micro Devices",
            "category_label": "Information Technology",
            "currency": "USD",
            "base_value": 50_000.0,
        },
    ]

    scenario = RiskScenario(
        scenario_id="SCEN_PRECEDENCE",
        owner_user_id="USER_1",
        organization_id=None,
        name="Precedence Test",
        description="Portfolio broad shock vs Sector shock vs Specific NVDA shock",
        scenario_type=ScenarioType.HYPOTHETICAL_USER_DEFINED,
        historical_episode_id=None,
        shocks=[
            # 1. Broad portfolio shock -5%
            ScenarioShock(
                shock_id="S1",
                shock_type=ScenarioShockType.PORTFOLIO_WIDE_ELIGIBLE_SHOCK,
                target_type=ShockTargetType.PORTFOLIO,
                target_id="ALL",
                shock_value=-0.05,
            ),
            # 2. Sector shock -10% for Information Technology
            ScenarioShock(
                shock_id="S2",
                shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                target_type=ShockTargetType.SECTOR,
                target_id="Information Technology",
                shock_value=-0.10,
            ),
            # 3. Security shock -20% specifically for NVDA
            ScenarioShock(
                shock_id="S3",
                shock_type=ScenarioShockType.SECURITY_PRICE_PERCENT_SHOCK,
                target_type=ShockTargetType.SECURITY,
                target_id="NVDA",
                shock_value=-0.20,
            ),
        ],
    )

    run = ScenarioEngine.evaluate_scenario(
        portfolio_positions=positions,
        portfolio_nav=100_000.0,
        scenario=scenario,
        portfolio_id="PORT_PRECEDENCE",
    )

    nvda_res = next(p for p in run.position_results if p.symbol == "NVDA")
    amd_res = next(p for p in run.position_results if p.symbol == "AMD")

    # NVDA must receive the specific security shock of -20%
    assert math.isclose(nvda_res.shock_applied, -0.20, rel_tol=1e-6)
    assert math.isclose(nvda_res.pnl, -10_000.0, rel_tol=1e-5)

    # AMD must inherit the sector shock of -10% (overriding portfolio -5%)
    assert math.isclose(amd_res.shock_applied, -0.10, rel_tol=1e-6)
    assert math.isclose(amd_res.pnl, -5_000.0, rel_tol=1e-5)


# ============================================================================
# 7. KUPIEC POF COVERAGE TEST DIAGNOSTICS
# ============================================================================

def test_kupiec_pof_test_evaluation():
    """Tests Kupiec POF likelihood ratio test:
    N = 250, alpha = 0.95 -> p0 = 0.05, expected exceptions = 12.5.
    1. x = 12 -> lr_statistic small (< 3.841) -> ACCEPT_UNCONDITIONAL_COVERAGE.
    2. x = 30 -> lr_statistic large (> 3.841) -> REJECT_TOO_MANY_EXCEPTIONS.
    3. N = 20 -> sample_adequate = False.
    """
    # 1. Healthy model
    res_pass = VaRDiagnosticsEngine.evaluate_kupiec_test(
        total_observations=250,
        exception_count=12,
        confidence_level=0.95,
    )
    assert res_pass.status == KupiecTestStatus.ACCEPT_UNCONDITIONAL_COVERAGE
    assert res_pass.likelihood_ratio_stat < 3.841459
    assert res_pass.is_sample_adequate is True

    # 2. Defective model with too many exceptions
    res_fail = VaRDiagnosticsEngine.evaluate_kupiec_test(
        total_observations=250,
        exception_count=35,
        confidence_level=0.95,
    )
    assert res_fail.status == KupiecTestStatus.REJECT_TOO_MANY_EXCEPTIONS
    assert res_fail.likelihood_ratio_stat > 3.841459

    # 3. Inadequate sample
    res_small = VaRDiagnosticsEngine.evaluate_kupiec_test(
        total_observations=20,
        exception_count=1,
        confidence_level=0.95,
    )
    assert res_small.is_sample_adequate is False
    assert res_small.status == KupiecTestStatus.INSUFFICIENT_SAMPLE


# ============================================================================
# 8. RISK SERVICE & FASTAPI ROUTER TESTS
# ============================================================================

def test_risk_service_tail_and_scenarios(risk_services):
    """Tests RiskService end-to-end integration for Stage 116."""
    p_service, r_service = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Stage 116 Portfolio",
            "base_currency": "USD",
            "description": "Tail Risk Test Portfolio",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    portfolio_id = p.id

    # 1. Historical Simulation VaR
    tail_run = r_service.calculate_tail_risk(
        portfolio_id=portfolio_id,
        user_id=USER_A_ID,
        request=CalculateTailRiskRequest(
            portfolio_id=portfolio_id,
            model_type=VaRModelType.HISTORICAL_SIMULATION,
            confidence_level=0.95,
            horizon_days=1,
        ),
    )
    assert tail_run.var.var_return > 0
    assert tail_run.expected_shortfall.es_return >= tail_run.var.var_return

    # 2. Parametric Normal VaR
    param_run = r_service.calculate_tail_risk(
        portfolio_id=portfolio_id,
        user_id=USER_A_ID,
        request=CalculateTailRiskRequest(
            portfolio_id=portfolio_id,
            model_type=VaRModelType.PARAMETRIC_NORMAL,
            confidence_level=0.95,
            horizon_days=1,
        ),
    )
    assert param_run.var.var_return > 0
    assert param_run.expected_shortfall.es_return > param_run.var.var_return

    # 3. Monte Carlo Gaussian VaR
    mc_run = r_service.calculate_tail_risk(
        portfolio_id=portfolio_id,
        user_id=USER_A_ID,
        request=CalculateTailRiskRequest(
            portfolio_id=portfolio_id,
            model_type=VaRModelType.MONTE_CARLO_GAUSSIAN,
            confidence_level=0.95,
            horizon_days=1,
            mc_simulations=500,
        ),
    )
    assert mc_run.var.var_return > 0
    assert mc_run.expected_shortfall.es_return >= mc_run.var.var_return

    # 4. Scenario Library Listing
    scenarios = r_service.list_scenarios(user_id=USER_A_ID)
    assert len(scenarios) >= 4  # Predefined library

    # 5. Create Custom Scenario
    custom_scen = r_service.create_scenario(
        user_id=USER_A_ID,
        request=CreateScenarioRequest(
            name="Tech Selloff",
            description="Tech drops 15%",
            shocks=[
                ScenarioShockDTO(
                    shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                    target_type=ShockTargetType.SECTOR,
                    target_id="Information Technology",
                    shock_percentage=-0.15,
                )
            ],
        ),
    )
    assert custom_scen.name == "Tech Selloff"

    # 6. Execute Scenario
    scen_run = r_service.execute_scenario(
        portfolio_id=portfolio_id,
        scenario_id=custom_scen.scenario_id,
        user_id=USER_A_ID,
    )
    assert scen_run.reconciled is True

    # 7. Compare Scenarios
    compared = r_service.compare_scenarios(
        portfolio_id=portfolio_id,
        scenario_ids=[custom_scen.scenario_id, "HIST_COVID_2020"],
        user_id=USER_A_ID,
    )
    assert len(compared) == 2

    # 8. VaR Backtest & Kupiec Test
    backtest = r_service.run_var_backtest(
        portfolio_id=portfolio_id,
        user_id=USER_A_ID,
        confidence_level=0.95,
        horizon_days=1,
        model_type=VaRModelType.HISTORICAL_SIMULATION,
        window_size=252,
    )
    assert backtest.kupiec_test is not None
    assert backtest.kupiec_test.total_observations > 0
    assert len(backtest.observations) > 0


# ============================================================================
# 9. FASTAPI REST API END-TO-END & MULTI-TENANT ISOLATION TESTS
# ============================================================================

def test_fastapi_tail_and_scenario_endpoints(client_user_a, client_user_b, risk_services):
    """Verifies all new REST API endpoints and multi-tenant security gates."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "API Alpha Portfolio",
            "base_currency": "USD",
            "description": "API Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    portfolio_id = p.id

    # 1. Models endpoint
    res_models = client_user_a.get("/api/v1/risk/tail/models")
    assert res_models.status_code == 200
    models_data = res_models.json()
    assert len(models_data) == 3

    # 2. Portfolio tail risk endpoint
    res_tail = client_user_a.get(f"/api/v1/risk/portfolios/{portfolio_id}/tail?confidence_level=0.95&horizon_days=1")
    assert res_tail.status_code == 200
    tail_dto = res_tail.json()
    assert tail_dto["portfolio_id"] == portfolio_id
    assert tail_dto["var"]["var_return"] > 0
    assert tail_dto["expected_shortfall"]["es_return"] >= tail_dto["var"]["var_return"]
    run_id = tail_dto["run_id"]

    # 3. Distribution endpoint
    res_dist = client_user_a.get(f"/api/v1/risk/tail/runs/{run_id}/distribution")
    assert res_dist.status_code == 200
    dist_dto = res_dist.json()
    assert dist_dto["total_observations"] > 0
    assert len(dist_dto["bins"]) > 0

    # 4. Scenarios listing
    res_scen_list = client_user_a.get("/api/v1/risk/scenarios")
    assert res_scen_list.status_code == 200
    scenarios = res_scen_list.json()
    assert len(scenarios) >= 4

    # 5. Execute predefined COVID scenario
    res_exec = client_user_a.post(f"/api/v1/risk/scenarios/HIST_COVID_2020/execute?portfolio_id={portfolio_id}")
    assert res_exec.status_code == 200
    exec_dto = res_exec.json()
    assert exec_dto["portfolio_id"] == portfolio_id
    assert exec_dto["is_reconciled"] is True
    scen_run_id = exec_dto["run_id"]

    # 6. Fetch scenario run
    res_run = client_user_a.get(f"/api/v1/risk/scenarios/runs/{scen_run_id}")
    assert res_run.status_code == 200

    # 7. Multi-scenario comparison
    res_comp = client_user_a.post(
        "/api/v1/risk/scenarios/compare",
        json={
            "portfolio_id": portfolio_id,
            "scenario_ids": ["HIST_COVID_2020", "HIST_GFC_2008"],
        },
    )
    assert res_comp.status_code == 200
    comp_dto = res_comp.json()
    assert len(comp_dto["items"]) == 2

    # 8. VaR Backtest & Kupiec
    res_backtest = client_user_a.post(
        "/api/v1/risk/tail/backtests",
        json={
            "portfolio_id": portfolio_id,
            "confidence_level": 0.95,
            "horizon_days": 1,
            "model_type": "HISTORICAL_SIMULATION",
            "window_size": 252,
        },
    )
    assert res_backtest.status_code == 200
    bt_dto = res_backtest.json()
    assert bt_dto["kupiec_test"]["status"] in [s.value for s in KupiecTestStatus]
    bt_id = bt_dto["backtest_id"]

    # Fetch backtest
    res_bt_get = client_user_a.get(f"/api/v1/risk/tail/backtests/{bt_id}")
    assert res_bt_get.status_code == 200

    # 9. Multi-tenant isolation test: User B cannot access User A's runs
    res_unauth = client_user_b.get(f"/api/v1/risk/portfolios/{portfolio_id}/tail")
    assert res_unauth.status_code in (403, 404)

    res_unauth_scen = client_user_b.post(f"/api/v1/risk/scenarios/HIST_COVID_2020/execute?portfolio_id={portfolio_id}")
    assert res_unauth_scen.status_code in (403, 404)
