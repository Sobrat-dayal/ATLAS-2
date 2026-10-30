"""Tests for ATLAS Portfolio Optimization and Quantitative Construction Platform (Stage 114).

Verifies:
1. Part XXIX analytical minimum variance reference fixture (2 uncorrelated assets, var 0.04 & 0.09
   => w_A = 69.2308%, w_B = 30.7692%).
2. Part LXIV infeasible constraint fixture (4 assets capped at 20% each => sum 80% < 100% budget
   => precheck detects INFEASIBLE).
3. Mean-Variance Utility optimization across risk aversion levels (lambda = 1.0 vs 4.0).
4. Target return minimum variance optimization and maximum return optimization.
5. Maximum Sharpe ratio optimization.
6. Equal Risk Contribution (Risk Parity) Spinu solver.
7. Efficient Frontier generation, monotonicity, and Sharpe calculation.
8. Rebalancing engine turnover, trade value deltas, transaction costs, and budget reconciliation.
9. Sensitivity scenario analysis (+100 bps alpha, risk aversion shifts).
10. FastAPI REST API endpoints: studies lifecycle, execution runs, candidate allocations,
    frontier points, comparisons, diagnostics, universe, and methodologies.
11. Constraint validation endpoint pre-checks.
12. Multi-tenant security isolation across tenants and users.
"""

from datetime import datetime, timezone
from decimal import Decimal
import numpy as np
import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios import (
    AccountCreateRequest,
    PortfolioCreateRequest,
    PortfolioService,
    TransactionCreateRequest,
    TransactionType,
)
from atlas.portfolios.optimization import (
    CandidatePortfolio,
    ConstraintType,
    CovarianceEngine,
    CovarianceModel,
    CreateOptimizationStudyRequest,
    ExecuteOptimizationRequest,
    ExpectedReturnEngine,
    ExpectedReturnModel,
    FeasibilityStatus,
    OptimizationConstraintItem,
    OptimizationConstraintRequest,
    OptimizationObjective,
    PortfolioOptimizationAccessDeniedError,
    PortfolioOptimizationError,
    PortfolioOptimizationInfeasibleError,
    PortfolioOptimizationRun,
    PortfolioOptimizationService,
    SolverStatus,
    StudyStatus,
)
from atlas.portfolios.optimization.constraints import ConstraintEngine
from atlas.portfolios.optimization.frontier import EfficientFrontierBuilder
from atlas.portfolios.optimization.rebalancing import RebalancingEngine
from atlas.portfolios.optimization.sensitivity import SensitivityEngine
from atlas.portfolios.optimization.solvers import ConvexOptimizationSolver
from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers.portfolios import get_optimization_service, get_portfolio_service


# ---------------------------------------------------------------------------
# Test Fixtures & Utilities
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_services():
    """Provides isolated, clean service instances for testing."""
    port_svc = PortfolioService()
    opt_svc = PortfolioOptimizationService(portfolio_service=port_svc)
    return port_svc, opt_svc


@pytest.fixture
def test_client(clean_services):
    """Provides TestClient with overridden service dependencies and user principal."""
    port_svc, opt_svc = clean_services
    user_a = AuthPrincipal(sub="usr_tenant_a", email="analyst@atlas.financial", role="authenticated")
    app.dependency_overrides[get_portfolio_service] = lambda: port_svc
    app.dependency_overrides[get_optimization_service] = lambda: opt_svc
    app.dependency_overrides[get_current_user] = lambda: user_a
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def setup_test_portfolio(port_svc: PortfolioService, user_id: str = "usr_tenant_a") -> str:
    """Creates a seeded portfolio with cash and stock holdings."""
    p = port_svc.create_portfolio(
        user_id=user_id,
        request=PortfolioCreateRequest(
            name="Global Growth Fund",
            base_currency="USD",
            description="Active quantitative equity portfolio",
        ),
    )
    accs = port_svc.list_accounts(p.id, user_id=user_id)
    acc_id = accs[0].id

    # Deposit $1,000,000 Cash
    port_svc.post_transaction(
        portfolio_id=p.id,
        user_id=user_id,
        request=TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            trade_date=datetime(2025, 1, 1),
            gross_amount=Decimal("1000000.00"),
            cash_currency="USD",
        ),
    )

    # Buy AAPL 2000 shares @ $150 = $300,000 (30%)
    port_svc.post_transaction(
        portfolio_id=p.id,
        user_id=user_id,
        request=TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.BUY,
            symbol="AAPL",
            quantity=Decimal("2000"),
            unit_price=Decimal("150.00"),
            gross_amount=Decimal("300000.00"),
            trade_date=datetime(2025, 1, 2),
            cash_currency="USD",
        ),
    )

    # Buy MSFT 1000 shares @ $300 = $300,000 (30%)
    port_svc.post_transaction(
        portfolio_id=p.id,
        user_id=user_id,
        request=TransactionCreateRequest(
            account_id=acc_id,
            transaction_type=TransactionType.BUY,
            symbol="MSFT",
            quantity=Decimal("1000"),
            unit_price=Decimal("300.00"),
            gross_amount=Decimal("300000.00"),
            trade_date=datetime(2025, 1, 2),
            cash_currency="USD",
        ),
    )

    # Remaining cash: $400,000 (40%)
    port_svc.calculate_portfolio_valuation(p.id, user_id=user_id)
    return p.id


# ---------------------------------------------------------------------------
# 1. Part XXIX — Analytical Minimum Variance Reference Fixture
# ---------------------------------------------------------------------------

def test_part_xxix_minimum_variance_reference_fixture():
    """
    Mandatory Part XXIX Reference Fixture:
    2 uncorrelated assets:
    Asset A: var = 0.04 (sigma_A = 20%)
    Asset B: var = 0.09 (sigma_B = 30%)
    Covariance = 0.0

    Analytical Minimum Variance Weights:
    w_A = var_B / (var_A + var_B) = 0.09 / 0.13 = 9/13 ≈ 0.6923077 (69.23077%)
    w_B = var_A / (var_A + var_B) = 0.04 / 0.13 = 4/13 ≈ 0.3076923 (30.76923%)

    Portfolio Minimum Variance:
    sigma_p^2 = (9/13)^2 * 0.04 + (4/13)^2 * 0.09
              = (81/169) * 0.04 + (16/169) * 0.09
              = 3.24/169 + 1.44/169 = 4.68/169 ≈ 0.0276923 (sigma_p ≈ 16.64%)
    """
    solver = ConvexOptimizationSolver()
    cov = np.array([
        [0.04, 0.00],
        [0.00, 0.09],
    ], dtype=float)

    weights, diag = solver.solve_minimum_variance(
        covariance_matrix=cov,
        is_long_only=True,
    )

    expected_w_a = 0.09 / 0.13
    expected_w_b = 0.04 / 0.13
    expected_var = (expected_w_a ** 2) * 0.04 + (expected_w_b ** 2) * 0.09

    assert diag.status == SolverStatus.OPTIMAL
    assert abs(weights[0] - expected_w_a) < 1e-4, f"w_A {weights[0]} != expected {expected_w_a}"
    assert abs(weights[1] - expected_w_b) < 1e-4, f"w_B {weights[1]} != expected {expected_w_b}"
    assert abs(weights.sum() - 1.0) < 1e-6

    actual_var = float(weights.T @ cov @ weights)
    assert abs(actual_var - expected_var) < 1e-5


# ---------------------------------------------------------------------------
# 2. Part LXIV — Infeasible Constraint Precheck Fixture
# ---------------------------------------------------------------------------

def test_part_lxiv_infeasible_constraint_precheck():
    """
    Mandatory Part LXIV Infeasible Constraint Fixture:
    4 eligible assets, each constrained with upper bound <= 20% (0.20):
    Sum of upper bounds = 4 * 0.20 = 0.80 < 1.00 portfolio budget.

    Precheck feasibility MUST reject this immediately before numerical solver execution
    and produce clear diagnostic conflict explanation.
    """
    constraint_engine = ConstraintEngine()
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    constraints = [
        OptimizationConstraintItem(
            constraint_id=f"cap-{sym}",
            constraint_type=ConstraintType.SECURITY_WEIGHT_BOUND,
            scope="ASSET",
            target_id=sym,
            upper_bound=Decimal("0.20"),
        )
        for sym in symbols
    ]

    with pytest.raises(PortfolioOptimizationInfeasibleError) as exc_info:
        constraint_engine.precheck_feasibility(symbols=symbols, constraints=constraints)

    msg = str(exc_info.value)
    assert "80.0%" in msg
    assert "100%" in msg


# ---------------------------------------------------------------------------
# 3. Mean-Variance Utility Optimization Across Risk Aversions
# ---------------------------------------------------------------------------

def test_mean_variance_utility_risk_aversion_monotonicity():
    """
    Tests Mean-Variance Utility: max wᵀμ - 0.5 * λ * wᵀΣw.
    As risk aversion λ increases from 1.0 to 4.0:
    - Allocation to lower risk asset must increase.
    - Resulting portfolio volatility must decrease.
    """
    solver = ConvexOptimizationSolver()
    mu = np.array([0.15, 0.05], dtype=float)  # High return, low return
    cov = np.array([
        [0.09, 0.00],  # High risk (30%)
        [0.00, 0.01],  # Low risk (10%)
    ], dtype=float)

    # Aggressive (lambda = 1.0)
    w_agg, diag_agg = solver.solve_mean_variance_utility(mu, cov, risk_aversion=1.0)
    vol_agg = np.sqrt(w_agg.T @ cov @ w_agg)

    # Conservative (lambda = 4.0)
    w_cons, diag_cons = solver.solve_mean_variance_utility(mu, cov, risk_aversion=4.0)
    vol_cons = np.sqrt(w_cons.T @ cov @ w_cons)

    assert diag_agg.status == SolverStatus.OPTIMAL
    assert diag_cons.status == SolverStatus.OPTIMAL
    assert w_agg[0] > w_cons[0], "Aggressive portfolio should hold more high-risk/high-return asset"
    assert vol_agg > vol_cons, "Aggressive portfolio should have higher volatility"


# ---------------------------------------------------------------------------
# 4. Target Return Minimum Variance & Maximum Return
# ---------------------------------------------------------------------------

def test_target_return_min_variance_and_max_return():
    """Tests target return QP and linear maximum return solvers."""
    solver = ConvexOptimizationSolver()
    mu = np.array([0.14, 0.06], dtype=float)
    cov = np.array([[0.04, 0.00], [0.00, 0.01]], dtype=float)

    # Target return 10%
    target_r = 0.10
    w_target, diag_target = solver.solve_target_return_min_variance(mu, cov, target_return=target_r)
    port_r = float(w_target @ mu)

    assert diag_target.status == SolverStatus.OPTIMAL
    assert port_r >= target_r - 1e-5

    # Max Return long-only
    w_max, diag_max = solver.solve_maximum_return(mu)
    assert diag_max.status == SolverStatus.OPTIMAL
    assert abs(w_max[0] - 1.0) < 1e-4, "Long-only max return should allocate 100% to highest return asset"


# ---------------------------------------------------------------------------
# 5. Maximum Sharpe Ratio Optimization
# ---------------------------------------------------------------------------

def test_maximum_sharpe_ratio():
    """Tests non-linear Sharpe ratio maximization."""
    solver = ConvexOptimizationSolver()
    mu = np.array([0.12, 0.08], dtype=float)
    cov = np.array([[0.04, 0.01], [0.01, 0.02]], dtype=float)
    rf = 0.04

    w_sharpe, diag_sharpe = solver.solve_maximum_sharpe(mu, cov, risk_free_rate=rf)
    w_minvar, _ = solver.solve_minimum_variance(cov)

    sharpe_opt = (float(w_sharpe @ mu) - rf) / np.sqrt(float(w_sharpe.T @ cov @ w_sharpe))
    sharpe_minvar = (float(w_minvar @ mu) - rf) / np.sqrt(float(w_minvar.T @ cov @ w_minvar))

    assert diag_sharpe.status == SolverStatus.OPTIMAL
    assert sharpe_opt >= sharpe_minvar - 1e-4, "Max Sharpe portfolio must have Sharpe >= Min Variance"


# ---------------------------------------------------------------------------
# 6. Equal Risk Contribution (Risk Parity) Solver
# ---------------------------------------------------------------------------

def test_risk_parity_equal_risk_contribution():
    """Tests Spinu logarithmic barrier equal risk contribution solver."""
    solver = ConvexOptimizationSolver()
    # 3 uncorrelated assets with variances 0.09, 0.04, 0.01 (vols 30%, 20%, 10%)
    cov = np.diag([0.09, 0.04, 0.01])

    w_rp, diag_rp = solver.solve_risk_parity(cov)

    assert diag_rp.status == SolverStatus.OPTIMAL
    assert np.all(w_rp > 0.0), "Risk parity weights must be strictly positive"
    assert abs(w_rp.sum() - 1.0) < 1e-6

    # Lower variance asset must receive higher weight to achieve equal risk contribution
    assert w_rp[2] > w_rp[1] > w_rp[0]

    # Verify marginal risk contributions w_i * (Sigma w)_i / sigma_p are equal
    sigma_p = np.sqrt(w_rp.T @ cov @ w_rp)
    mrc = (w_rp * (cov @ w_rp)) / sigma_p
    for i in range(len(mrc)):
        assert abs(mrc[i] - mrc[0]) < 1e-3, f"MRC not equal: {mrc}"


# ---------------------------------------------------------------------------
# 7. Efficient Frontier Construction
# ---------------------------------------------------------------------------

def test_efficient_frontier_generation():
    """Tests parametric efficient frontier generation and Pareto optimality."""
    builder = EfficientFrontierBuilder()
    symbols = ["AAPL", "MSFT", "GOOGL"]
    mu = np.array([0.15, 0.10, 0.08], dtype=float)
    cov = np.array([
        [0.05, 0.01, 0.01],
        [0.01, 0.03, 0.005],
        [0.01, 0.005, 0.02],
    ], dtype=float)

    points = builder.build_frontier(
        symbols=symbols,
        expected_returns=mu,
        covariance_matrix=cov,
        risk_free_rate=0.04,
        num_points=12,
    )

    assert len(points) >= 5
    # Verify non-dominated points are monotonic in return vs volatility
    valid_points = [p for p in points if not p.is_dominated]
    for i in range(1, len(valid_points)):
        assert valid_points[i].estimated_return >= valid_points[i - 1].estimated_return
        assert valid_points[i].estimated_volatility >= valid_points[i - 1].estimated_volatility - Decimal("0.001")


# ---------------------------------------------------------------------------
# 8. Rebalancing Engine Turnover & Cost Modeling
# ---------------------------------------------------------------------------

def test_rebalancing_turnover_and_transaction_costs():
    """
    Tests one-way turnover: 0.5 * sum(|w_cand - w_curr|)
    NAV = $1,000,000
    AAPL: 50% -> 40% (delta -10%, -$100k sell)
    MSFT: 30% -> 40% (delta +10%, +$100k buy)
    CASH: 20% -> 20% (delta 0%)
    One-way turnover = 10%
    Cost rate = 10 bps (0.0010)
    Estimated cost = $1,000,000 * 0.0010 * (0.10 + 0.10) = $200
    """
    engine = RebalancingEngine()
    nav = Decimal("1000000.00")
    curr_weights = {"AAPL": Decimal("0.50"), "MSFT": Decimal("0.30"), "CASH": Decimal("0.20")}
    cand_weights = {"AAPL": Decimal("0.40"), "MSFT": Decimal("0.40"), "CASH": Decimal("0.20")}

    turnover, cost, items = engine.compute_rebalancing(
        current_weights=curr_weights,
        candidate_weights=cand_weights,
        nav=nav,
        proportional_cost_rate=Decimal("0.0010"),
    )

    assert turnover == Decimal("0.1000"), f"Turnover {turnover} != 0.1000"
    assert cost == Decimal("200.00"), f"Cost {cost} != 200.00"

    item_map = {item.symbol: item for item in items}
    assert item_map["AAPL"].trade_direction == "SELL"
    assert item_map["AAPL"].trade_value_delta == Decimal("-100000.00")
    assert item_map["MSFT"].trade_direction == "BUY"
    assert item_map["MSFT"].trade_value_delta == Decimal("100000.00")

    # Trade values sum to zero
    sum_deltas = sum(item.trade_value_delta for item in items)
    assert sum_deltas == Decimal("0.00")


# ---------------------------------------------------------------------------
# 9. Sensitivity Scenario Engine
# ---------------------------------------------------------------------------

def test_sensitivity_scenario_engine():
    """Tests sensitivity analysis under parameter perturbations."""
    engine = SensitivityEngine()
    symbols = ["AAPL", "MSFT"]
    mu = np.array([0.12, 0.08], dtype=float)
    cov = np.diag([0.04, 0.02])
    base_weights = {"AAPL": Decimal("0.50"), "MSFT": Decimal("0.50")}

    scenarios = engine.evaluate_sensitivity(
        symbols=symbols,
        base_expected_returns=mu,
        base_covariance=cov,
        base_weights=base_weights,
        risk_aversion=2.0,
    )

    assert len(scenarios) >= 3
    scenario_names = [s.scenario_name for s in scenarios]
    assert any("Alpha" in name for name in scenario_names)
    assert any("Risk Aversion" in name for name in scenario_names)


# ---------------------------------------------------------------------------
# 10. REST API: Studies Lifecycle & Execution Runs
# ---------------------------------------------------------------------------

def test_rest_api_studies_lifecycle_and_runs(test_client, clean_services):
    """Verifies study CRUD, run execution, and subresource querying."""
    port_svc, opt_svc = clean_services
    pid = setup_test_portfolio(port_svc, "usr_tenant_a")

    # 1. Create Study
    create_study_payload = {
        "name": "Q1 Mean-Variance Study",
        "description": "Baseline optimization research",
        "default_objective": "MINIMUM_VARIANCE",
        "universe_symbols": ["AAPL", "MSFT", "CASH"],
    }
    r = test_client.post(f"/api/v1/portfolios/{pid}/optimization/studies", json=create_study_payload)
    assert r.status_code == 201
    study = r.json()
    assert study["name"] == "Q1 Mean-Variance Study"
    sid = study["study_id"]

    # 2. List Studies
    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/studies")
    assert r.status_code == 200
    assert r.json()["total"] >= 1

    # 3. Get Study by ID
    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/studies/{sid}")
    assert r.status_code == 200
    assert r.json()["study_id"] == sid

    # 4. Execute Optimization Run
    exec_payload = {
        "study_id": sid,
        "objective_type": "MINIMUM_VARIANCE",
        "universe_symbols": ["AAPL", "MSFT", "CASH"],
        "is_long_only": True,
    }
    r = test_client.post(f"/api/v1/portfolios/{pid}/optimization/runs", json=exec_payload)
    assert r.status_code == 201
    run_data = r.json()
    run_id = run_data["run_id"]
    assert run_data["candidate"]["feasibility_status"] == "FEASIBLE"
    assert len(run_data["frontier_points"]) > 0

    # 5. Query Run Subresources
    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/runs/{run_id}/candidate")
    assert r.status_code == 200
    assert "AAPL" in r.json()["weights"]

    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/runs/{run_id}/frontier")
    assert r.status_code == 200
    assert len(r.json()) > 0

    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/runs/{run_id}/comparison")
    assert r.status_code == 200
    assert len(r.json()) > 0

    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/runs/{run_id}/diagnostics")
    assert r.status_code == 200
    assert r.json()["status"] == "OPTIMAL"

    # 6. Archive Study
    r = test_client.delete(f"/api/v1/portfolios/{pid}/optimization/studies/{sid}")
    assert r.status_code == 200
    assert r.json()["status"] == "ARCHIVED"


# ---------------------------------------------------------------------------
# 11. REST API: Universe, Methodologies & Constraint Pre-check
# ---------------------------------------------------------------------------

def test_rest_api_universe_methodologies_and_constraints(test_client, clean_services):
    """Tests universe, methodologies, and precheck validation endpoints."""
    port_svc, opt_svc = clean_services
    pid = setup_test_portfolio(port_svc, "usr_tenant_a")

    # 1. Universe Endpoint
    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/universe")
    assert r.status_code == 200
    symbols = [u["symbol"] for u in r.json()]
    assert "AAPL" in symbols
    assert "MSFT" in symbols
    assert "CASH" in symbols

    # 2. Methodologies Endpoint
    r = test_client.get(f"/api/v1/portfolios/{pid}/optimization/methodologies")
    assert r.status_code == 200
    methodologies = r.json()
    assert len(methodologies["objectives"]) >= 8
    assert len(methodologies["expected_return_models"]) >= 3

    # 3. Feasible Constraints Validation
    feasible_constraints = [
        {
            "constraint_type": "SECURITY_WEIGHT_BOUND",
            "scope": "ASSET",
            "target_id": "AAPL",
            "upper_bound": "0.50",
            "lower_bound": "0.05",
        }
    ]
    r = test_client.post(
        f"/api/v1/portfolios/{pid}/optimization/constraints/validate",
        json=feasible_constraints,
    )
    assert r.status_code == 200
    assert r.json()["is_feasible"] is True

    # 4. Infeasible Constraints Validation (Part LXIV 4x20% cap)
    infeasible_constraints = [
        {"constraint_type": "SECURITY_WEIGHT_BOUND", "scope": "ASSET", "target_id": sym, "upper_bound": "0.20"}
        for sym in ["AAPL", "MSFT", "GOOGL", "AMZN"]
    ]
    r = test_client.post(
        f"/api/v1/portfolios/{pid}/optimization/constraints/validate?universe_symbols=AAPL&universe_symbols=MSFT&universe_symbols=GOOGL&universe_symbols=AMZN",
        json=infeasible_constraints,
    )
    assert r.status_code == 200
    assert r.json()["is_feasible"] is False
    assert len(r.json()["conflicts"]) > 0


# ---------------------------------------------------------------------------
# 12. Multi-Tenant Isolation
# ---------------------------------------------------------------------------

def test_multi_tenant_isolation(test_client, clean_services):
    """Verifies that User B cannot access or mutate User A's optimization studies and runs."""
    port_svc, opt_svc = clean_services
    user_a = AuthPrincipal(sub="usr_tenant_a", email="alice@atlas.financial", role="authenticated")
    user_b = AuthPrincipal(sub="usr_tenant_b", email="bob@atlas.financial", role="authenticated")

    # User A creates portfolio and study
    app.dependency_overrides[get_current_user] = lambda: user_a
    pid_a = setup_test_portfolio(port_svc, "usr_tenant_a")

    r = test_client.post(
        f"/api/v1/portfolios/{pid_a}/optimization/studies",
        json={"name": "Tenant A Secret Alpha Study", "default_objective": "MINIMUM_VARIANCE"},
    )
    assert r.status_code == 201
    sid = r.json()["study_id"]

    # Switch to User B
    app.dependency_overrides[get_current_user] = lambda: user_b

    # User B tries to read User A's study -> 403 or 404
    r = test_client.get(f"/api/v1/portfolios/{pid_a}/optimization/studies/{sid}")
    assert r.status_code in [403, 404]

    # User B tries to execute run on User A's portfolio -> 403 or 404
    r = test_client.post(
        f"/api/v1/portfolios/{pid_a}/optimization/runs",
        json={"objective_type": "MINIMUM_VARIANCE"},
    )
    assert r.status_code in [403, 404]
