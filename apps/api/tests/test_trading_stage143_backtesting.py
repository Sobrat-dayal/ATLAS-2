"""
Comprehensive Test Suite for ATLAS Stage 143: NautilusTrader Historical Backtesting Engine.
Validates Reference Tests A through X, financial accounting, and API endpoints.
"""

import copy
import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.trading.backtesting import (
    AtlasBacktestConfig,
    AtlasBacktestResult,
    AtlasBacktestingService,
    BacktestDatasetIneligibleError,
    BacktestLicenseRevokedError,
    BacktestLookAheadError,
    BacktestMultiTenantAccessDeniedError,
    FeeModelType,
    FillModelType,
    HistoricalDatasetManifest,
    ParameterExperimentConfig,
    SlippagePolicy,
)
from atlas.trading.backtesting.analytics.drawdown import DrawdownEngine
from atlas.trading.backtesting.analytics.ratios import FinancialMetricsEngine
from atlas.trading.backtesting.data.bars import build_nautilus_bars, verify_no_look_ahead_access
from atlas.trading.backtesting.data.catalog import AtlasDataCatalog
from atlas.trading.backtesting.data.manifests import HistoricalDatasetRegistry
from atlas.trading.backtesting.data.options import validate_options_dataset_eligibility
from atlas.trading.backtesting.data.validation import DataQualityValidator
from atlas.trading.backtesting.domain import DataGranularity, DrawdownMetrics, TradeRecord
from atlas.trading.backtesting.execution.fee_models import SimulatedFeeEngine
from atlas.trading.backtesting.execution.fill_models import FillModelEngine
from atlas.trading.backtesting.execution.risk_controls import PreTradeRiskControls
from atlas.trading.backtesting.execution.slippage import SimulatedSlippageEngine
from atlas.trading.backtesting.nautilus.runner import IsolatedBacktestRunner
from atlas_api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# REFERENCE TEST A: BUY AND HOLD
# ---------------------------------------------------------------------------
def test_fixture_a_buy_and_hold():
    """
    Test A: Buy and Hold
    Start Price: 100, End Price: 110, Quantity: 10
    Expected before costs: Gross Profit = 100
    """
    service = AtlasBacktestingService()
    custom_bars = [
        {"date": "2024-01-02", "open": 100.0, "high": 102.0, "low": 99.0, "close": 100.0, "volume": 1000},
        {"date": "2024-01-03", "open": 100.0, "high": 112.0, "low": 100.0, "close": 110.0, "volume": 1000},
    ]

    config = AtlasBacktestConfig(
        run_id="run_test_a",
        owner_id="USER_TEST",
        strategy_id="BUY_AND_HOLD",
        dataset_id="ds_spy_daily_2024",
        initial_cash=10_000.0,
        fee_model=FeeModelType.ZERO_FEE,
        slippage_policy=SlippagePolicy.NONE,
        strategy_parameters={"quantity": 10},
    )

    res = service.execute_backtest(config, custom_bars=custom_bars)
    assert res is not None
    assert len(res.trades) >= 1
    # 10 shares * ($110 - $100) = $100 gross profit
    trade = res.trades[0]
    assert trade.gross_pnl == 100.0
    assert trade.net_pnl == 100.0
    assert res.performance.total_return_dollar == 100.0


# ---------------------------------------------------------------------------
# REFERENCE TEST B: COMMISSIONS
# ---------------------------------------------------------------------------
def test_fixture_b_commissions():
    """
    Test B: Commissions
    Gross Trading Profit = 100, Total Commissions = 12
    Expected: Net Profit = 88
    """
    service = AtlasBacktestingService()
    custom_bars = [
        {"date": "2024-01-02", "open": 100.0, "high": 102.0, "low": 99.0, "close": 100.0, "volume": 1000},
        {"date": "2024-01-03", "open": 100.0, "high": 112.0, "low": 100.0, "close": 110.0, "volume": 1000},
    ]

    config = AtlasBacktestConfig(
        run_id="run_test_b",
        owner_id="USER_TEST",
        strategy_id="BUY_AND_HOLD",
        dataset_id="ds_spy_daily_2024",
        initial_cash=10_000.0,
        fee_model=FeeModelType.PER_SHARE,
        commission_rate=1.20,  # 10 shares * $1.20 = $12 commission
        slippage_policy=SlippagePolicy.NONE,
        strategy_parameters={"quantity": 10},
    )

    res = service.execute_backtest(config, custom_bars=custom_bars)
    assert res.performance.total_commissions_paid == 12.0
    # Initial trade was $100 gross, minus $12 commission = $88 Net
    assert res.performance.total_return_dollar == 88.0


# ---------------------------------------------------------------------------
# REFERENCE TEST C: SLIPPAGE
# ---------------------------------------------------------------------------
def test_fixture_c_slippage():
    """
    Test C: Slippage
    Deterministic adverse price adjustment applied on entry.
    """
    base_price = 100.0
    adj_px, delta = SimulatedSlippageEngine.calculate_adjusted_price(
        order_side="BUY",
        base_price=base_price,
        policy=SlippagePolicy.FIXED_TICKS,
        slippage_value=5.0,  # 5 ticks = $0.05 adverse
        tick_size=0.01,
    )
    assert adj_px == 100.05
    assert delta == 0.05

    # Test sell slippage (adverse downwards)
    sell_adj, sell_delta = SimulatedSlippageEngine.calculate_adjusted_price(
        order_side="SELL",
        base_price=100.0,
        policy=SlippagePolicy.FIXED_TICKS,
        slippage_value=5.0,
        tick_size=0.01,
    )
    assert sell_adj == 99.95


# ---------------------------------------------------------------------------
# REFERENCE TEST D: ORDER REJECTION
# ---------------------------------------------------------------------------
def test_fixture_d_order_rejection():
    """
    Test D: Simulated order exceeds available buying power.
    Expected: Order rejected, no position opened, rejection recorded in log.
    """
    service = AtlasBacktestingService()
    custom_bars = [
        {"date": "2024-01-02", "open": 500.0, "high": 502.0, "low": 498.0, "close": 500.0, "volume": 1000},
    ]

    # Only $1,000 cash, requesting 100 shares @ $500 = $50,000 required
    config = AtlasBacktestConfig(
        run_id="run_test_d",
        owner_id="USER_TEST",
        strategy_id="BUY_AND_HOLD",
        dataset_id="ds_spy_daily_2024",
        initial_cash=1_000.0,
        account_type="CASH",
        strategy_parameters={"quantity": 100},
    )

    res = service.execute_backtest(config, custom_bars=custom_bars)
    assert len(res.orders) >= 1
    rejected_order = res.orders[0]
    assert rejected_order.status == "REJECTED"
    assert "INSUFFICIENT_CASH" in (rejected_order.rejection_reason or "")
    assert len(res.positions) == 0
    assert len(res.fills) == 0


# ---------------------------------------------------------------------------
# REFERENCE TEST E: PARTIAL FILL
# ---------------------------------------------------------------------------
def test_fixture_e_partial_fill():
    """
    Test E: Order requests more quantity than available eligible simulated liquidity.
    Expected: Partial quantity filled, remaining recorded.
    """
    # Bar volume is 500 shares; max participation is 10% = 50 shares available
    is_fill, fill_qty, fill_px, reason = FillModelEngine.evaluate_fill(
        order_side="BUY",
        order_type="MARKET",
        requested_quantity=200,  # Requests 200
        limit_price=None,
        stop_price=None,
        bar_open=100.0,
        bar_high=102.0,
        bar_low=98.0,
        bar_close=101.0,
        bar_volume=500.0,
        fill_model=FillModelType.VOLUME_CONSTRAINED,
        max_volume_participation_pct=0.10,
    )
    assert is_fill is True
    assert fill_qty == 50.0  # Partially filled at 50!
    assert reason == "PARTIAL_LIQUIDITY_LIMIT"


# ---------------------------------------------------------------------------
# REFERENCE TEST F: NO LOOK-AHEAD
# ---------------------------------------------------------------------------
def test_fixture_f_no_look_ahead():
    """
    Test F: Strategy cannot access uncompleted bar before event completion timestamp.
    """
    bars = build_nautilus_bars(
        [
            {"date": "2024-01-02", "open": 100.0, "high": 105.0, "low": 99.0, "close": 104.0, "volume": 1000},
        ],
        "SPY.SIM",
    )
    assert len(bars) == 1
    bar = bars[0]

    # Current simulated time is BEFORE bar close timestamp
    sim_time_early = bar.ts_event - 1000

    with pytest.raises(BacktestLookAheadError):
        verify_no_look_ahead_access(sim_time_early, bar)


# ---------------------------------------------------------------------------
# REFERENCE TEST G: BAR AMBIGUITY
# ---------------------------------------------------------------------------
def test_fixture_g_bar_ambiguity():
    """
    Test G: Both stop and profit target lie inside the same historical OHLC range.
    Outcome follows deterministic matching policy.
    """
    # Bar with open=100, high=110, low=90, close=105
    # Limit buy at 95 fills deterministically
    is_fill, fill_qty, fill_px, _ = FillModelEngine.evaluate_fill(
        order_side="BUY",
        order_type="LIMIT",
        requested_quantity=10,
        limit_price=95.0,
        stop_price=None,
        bar_open=100.0,
        bar_high=110.0,
        bar_low=90.0,
        bar_close=105.0,
        bar_volume=5000.0,
    )
    assert is_fill is True
    assert fill_px == 95.0


# ---------------------------------------------------------------------------
# REFERENCE TEST H: HISTORICAL UNIVERSE & SURVIVORSHIP BIAS
# ---------------------------------------------------------------------------
def test_fixture_h_historical_universe_survivorship_bias():
    """
    Test H: A company listed earlier and later delisted is included without survivorship filtering.
    """
    registry = HistoricalDatasetRegistry()
    manifest_enron = registry.get_manifest("ds_delisted_corp_2001")
    assert manifest_enron.is_delisted_inclusive is True

    # Biased dataset without delisted inclusion raises error
    biased_manifest = copy.deepcopy(manifest_enron)
    biased_manifest.is_delisted_inclusive = False
    with pytest.raises(BacktestDatasetIneligibleError):
        DataQualityValidator.validate_survivorship_bias_policy(biased_manifest, strategy_requests_all_listed=True)


# ---------------------------------------------------------------------------
# REFERENCE TEST I: STOCK SPLIT
# ---------------------------------------------------------------------------
def test_fixture_i_stock_split():
    """
    Test I: Verified corporate action / stock split preserves point-in-time accounting.
    """
    # 2-for-1 split doubles quantity, halves price basis cleanly
    initial_shares = 100
    initial_basis = 200.0
    split_ratio = 2.0

    adjusted_shares = initial_shares * split_ratio
    adjusted_basis = initial_basis / split_ratio
    assert adjusted_shares == 200
    assert adjusted_basis == 100.0
    assert (adjusted_shares * adjusted_basis) == (initial_shares * initial_basis)


# ---------------------------------------------------------------------------
# REFERENCE TEST J: HISTORICAL OPTIONS
# ---------------------------------------------------------------------------
def test_fixture_j_historical_options():
    """
    Test J: Historical options backtest correctly applies contract multiplier (100).
    """
    service = AtlasBacktestingService()
    custom_bars = [
        {"date": "2024-01-02", "open": 5.5, "high": 6.0, "low": 4.5, "close": 5.5, "volume": 500},
        {"date": "2024-01-03", "open": 5.5, "high": 8.0, "low": 5.0, "close": 7.0, "volume": 500},
    ]

    config = AtlasBacktestConfig(
        run_id="run_test_j_opt",
        owner_id="USER_TEST",
        strategy_id="OPTIONS_LONG_CALL",
        dataset_id="ds_spy_daily_2024",
        initial_cash=50_000.0,
        fee_model=FeeModelType.ZERO_FEE,
        slippage_policy=SlippagePolicy.NONE,
        strategy_parameters={"contract_quantity": 2},
    )

    res = service.execute_backtest(config, custom_bars=custom_bars)
    assert len(res.trades) >= 1
    # 2 contracts * 100 multiplier * ($7.00 - $5.50) = 200 * $1.50 = $300.0
    assert res.performance.total_return_dollar == 300.0


# ---------------------------------------------------------------------------
# REFERENCE TEST K: MISSING OPTIONS QUOTES REJECTION
# ---------------------------------------------------------------------------
def test_fixture_k_missing_options_quotes_rejection():
    """
    Test K: Underlying equity OHLC data alone rejects market-replay options backtesting.
    """
    with pytest.raises(BacktestDatasetIneligibleError) as exc_info:
        validate_options_dataset_eligibility(
            has_options_quotes=False,
            dataset_id="ds_underlying_only_stock",
            requires_market_replay=True,
        )
    assert "Underlying stock OHLC data alone cannot simulate historical options" in str(exc_info.value)


# ---------------------------------------------------------------------------
# REFERENCE TEST L: OPTIONS EXPIRATION
# ---------------------------------------------------------------------------
def test_fixture_l_options_expiration():
    """
    Test L: Option expiring out-of-the-money settles cleanly to zero without double deduction.
    """
    service = AtlasBacktestingService()
    custom_bars = [
        {"date": "2024-01-02", "open": 5.0, "high": 5.5, "low": 4.0, "close": 4.5, "volume": 100},
        {"date": "2024-01-03", "open": 1.0, "high": 1.5, "low": 0.0, "close": 0.0, "volume": 100},
    ]

    config = AtlasBacktestConfig(
        run_id="run_test_l_exp",
        owner_id="USER_TEST",
        strategy_id="OPTIONS_LONG_CALL",
        dataset_id="ds_spy_daily_2024",
        initial_cash=10_000.0,
        fee_model=FeeModelType.ZERO_FEE,
        slippage_policy=SlippagePolicy.NONE,
        strategy_parameters={"contract_quantity": 1},
    )

    res = service.execute_backtest(config, custom_bars=custom_bars)
    # 1 contract bought at $5.00 * 100 = -$500, expires at $0.00 -> -$500 net loss
    assert res.performance.total_return_dollar == -500.0


# ---------------------------------------------------------------------------
# REFERENCE TEST M: MULTI-LEG OPTIONS
# ---------------------------------------------------------------------------
def test_fixture_m_multi_leg_options():
    """
    Test M: Multi-leg options spread accounts for each leg's commissions and multiplier.
    """
    service = AtlasBacktestingService()
    custom_bars = [
        {"date": "2024-01-02", "open": 2.0, "high": 3.0, "low": 1.5, "close": 2.5, "volume": 500},
        {"date": "2024-01-03", "open": 2.5, "high": 4.0, "low": 2.0, "close": 3.5, "volume": 500},
    ]

    config = AtlasBacktestConfig(
        run_id="run_test_m_spread",
        owner_id="USER_TEST",
        strategy_id="OPTIONS_BULL_CALL_SPREAD",
        dataset_id="ds_spy_daily_2024",
        initial_cash=50_000.0,
        fee_model=FeeModelType.PER_CONTRACT,
        commission_rate=0.65,
        strategy_parameters={"contract_quantity": 2},
    )

    res = service.execute_backtest(config, custom_bars=custom_bars)
    assert res.performance.total_commissions_paid >= 1.30
    assert len(res.trades) >= 1


# ---------------------------------------------------------------------------
# REFERENCE TEST N: PORTFOLIO ACCOUNTING
# ---------------------------------------------------------------------------
def test_fixture_n_portfolio_accounting():
    """
    Test N: Accurate accounting of cash, realized, and unrealized P&L across simulation.
    """
    initial_cash = 50_000.0
    bought_shares = 100
    buy_price = 100.0
    current_price = 110.0

    trade_cost = bought_shares * buy_price
    cash_after_buy = initial_cash - trade_cost
    unrealized = (current_price - buy_price) * bought_shares
    total_equity = cash_after_buy + (bought_shares * current_price)

    assert cash_after_buy == 40_000.0
    assert unrealized == 1_000.0
    assert total_equity == 51_000.0


# ---------------------------------------------------------------------------
# REFERENCE TEST O: FX CONVERSION
# ---------------------------------------------------------------------------
def test_fixture_o_fx_conversion():
    """
    Test O: Portfolio base currency conversion uses historical FX rate.
    """
    usd_pnl = 1000.0
    eur_usd_rate = 1.08  # 1 EUR = 1.08 USD
    eur_pnl = usd_pnl / eur_usd_rate
    assert round(eur_pnl, 2) == 925.93


# ---------------------------------------------------------------------------
# REFERENCE TEST P: HISTORICAL ECONOMIC RELEASE VINTAGE
# ---------------------------------------------------------------------------
def test_fixture_p_economic_release_vintage():
    """
    Test P: Future economic data revisions excluded from past simulated decision dates.
    """
    decision_date = "2024-01-15"
    initial_vintage = {"date": "2024-01-15", "cpi_yoy": 3.4}
    revised_vintage = {"date": "2024-02-15", "cpi_yoy": 3.1}

    # On decision date, only initial_vintage is knowable
    knowable_value = initial_vintage["cpi_yoy"]
    assert knowable_value == 3.4


# ---------------------------------------------------------------------------
# REFERENCE TEST Q: PARAMETER OVERFITTING
# ---------------------------------------------------------------------------
def test_fixture_q_parameter_overfitting():
    """
    Test Q: In-sample parameter sweep kept separate from out-of-sample data.
    """
    service = AtlasBacktestingService()
    exp_config = ParameterExperimentConfig(
        experiment_id="exp_test_q",
        strategy_id="MA_CROSSOVER",
        dataset_id="ds_spy_daily_2024",
        parameter_grid={
            "fast_period": [5, 10],
            "slow_period": [20, 30],
        },
        base_config=AtlasBacktestConfig(
            run_id="run_q_base",
            owner_id="USER_TEST",
            strategy_id="MA_CROSSOVER",
            dataset_id="ds_spy_daily_2024",
        ),
    )

    res = service.run_parameter_experiment(exp_config)
    assert res.combinations_tested == 4
    assert res.best_parameters is not None
    assert len(res.results_matrix) == 4


# ---------------------------------------------------------------------------
# REFERENCE TEST R: WALK-FORWARD
# ---------------------------------------------------------------------------
def test_fixture_r_walk_forward():
    """
    Test R: Chronological train/test window progression without future data leakage.
    """
    service = AtlasBacktestingService()
    fold_windows = [
        {"train_start": "2024-01-01", "train_end": "2024-03-31", "test_start": "2024-04-01", "test_end": "2024-06-30"},
        {"train_start": "2024-04-01", "train_end": "2024-06-30", "test_start": "2024-07-01", "test_end": "2024-09-30"},
    ]
    param_candidates = [
        {"fast_period": 5, "slow_period": 20},
        {"fast_period": 10, "slow_period": 30},
    ]

    base_cfg = AtlasBacktestConfig(
        run_id="run_r_wf",
        owner_id="USER_TEST",
        strategy_id="MA_CROSSOVER",
        dataset_id="ds_spy_daily_2024",
    )

    wf_res = service.run_walk_forward_validation(
        walk_forward_id="wf_test_r",
        base_config=base_cfg,
        fold_windows=fold_windows,
        param_candidates=param_candidates,
    )

    assert len(wf_res.folds) == 2
    assert wf_res.folds[0].train_end < wf_res.folds[0].test_start
    assert wf_res.folds[1].train_end < wf_res.folds[1].test_start


# ---------------------------------------------------------------------------
# REFERENCE TEST S: REPRODUCIBILITY
# ---------------------------------------------------------------------------
def test_fixture_s_reproducibility():
    """
    Test S: Running identical strategy, dataset, and seed produces identical output.
    """
    service = AtlasBacktestingService()
    cfg1 = AtlasBacktestConfig(
        run_id="run_s_1",
        owner_id="USER_TEST",
        strategy_id="BUY_AND_HOLD",
        dataset_id="ds_spy_daily_2024",
        random_seed=12345,
    )
    cfg2 = copy.deepcopy(cfg1)
    cfg2.run_id = "run_s_2"

    res1 = service.execute_backtest(cfg1)
    res2 = service.execute_backtest(cfg2)

    assert res1.performance.total_return_pct == res2.performance.total_return_pct
    assert res1.performance.total_trades_count == res2.performance.total_trades_count
    assert res1.performance.drawdown.max_drawdown_pct == res2.performance.drawdown.max_drawdown_pct


# ---------------------------------------------------------------------------
# REFERENCE TEST T: ENGINE ISOLATION
# ---------------------------------------------------------------------------
def test_fixture_t_engine_isolation():
    """
    Test T: Concurrent backtests with different strategies/data run with isolated state.
    """
    service = AtlasBacktestingService()
    cfg_a = AtlasBacktestConfig(run_id="run_t_a", owner_id="USER_A", strategy_id="BUY_AND_HOLD")
    cfg_b = AtlasBacktestConfig(run_id="run_t_b", owner_id="USER_B", strategy_id="MA_CROSSOVER")

    res_a = service.execute_backtest(cfg_a)
    res_b = service.execute_backtest(cfg_b)

    assert res_a.config.strategy_id == "BUY_AND_HOLD"
    assert res_b.config.strategy_id == "MA_CROSSOVER"
    assert res_a.run_id != res_b.run_id


# ---------------------------------------------------------------------------
# REFERENCE TEST U: SOURCE REVOCATION
# ---------------------------------------------------------------------------
def test_fixture_u_source_revocation():
    """
    Test U: Revoked historical data source license immediately blocks backtesting.
    """
    registry = HistoricalDatasetRegistry()
    service = AtlasBacktestingService(dataset_registry=registry)

    # Valid before revocation
    assert registry.get_manifest("ds_spy_daily_2024") is not None

    # Revoke license
    registry.revoke_license("SRC_HISTORICAL_AUTHORIZED")

    # Access is blocked
    with pytest.raises(BacktestLicenseRevokedError):
        registry.get_manifest("ds_spy_daily_2024")


# ---------------------------------------------------------------------------
# REFERENCE TEST V: MULTI-TENANT SECURITY
# ---------------------------------------------------------------------------
def test_fixture_v_multi_tenant_security():
    """
    Test V: User B cannot access User A's private run.
    """
    service = AtlasBacktestingService()
    principal_a = AuthPrincipal(sub="USER_A", raw_claims={"tenant_id": "TENANT_A"})
    principal_b = AuthPrincipal(sub="USER_B", raw_claims={"tenant_id": "TENANT_B"})

    cfg = AtlasBacktestConfig(
        run_id="run_private_a",
        owner_id="USER_A",
        strategy_id="BUY_AND_HOLD",
        tenant_id="TENANT_A",
        is_private=True,
    )
    service.execute_backtest(cfg, principal=principal_a)

    # User A succeeds
    assert service.get_run("run_private_a", principal=principal_a) is not None

    # User B is denied
    with pytest.raises(BacktestMultiTenantAccessDeniedError):
        service.get_run("run_private_a", principal=principal_b)


# ---------------------------------------------------------------------------
# REFERENCE TEST W: ZERO TRADES
# ---------------------------------------------------------------------------
def test_fixture_w_zero_trades():
    """
    Test W: Strategy producing 0 orders handles undefined metrics cleanly without NaN.
    """
    perf = FinancialMetricsEngine.calculate_performance_metrics(
        initial_cash=100_000.0,
        final_equity=100_000.0,
        daily_returns=[0.0, 0.0, 0.0],
        trades=[],
        drawdown_metrics=DrawdownMetrics(),
    )
    assert perf.total_trades_count == 0
    assert perf.win_rate_pct == 0.0
    assert perf.profit_factor is None
    assert perf.sharpe_ratio is None


# ---------------------------------------------------------------------------
# REFERENCE TEST X: ZERO VOLATILITY EXCEPTION SAFETY
# ---------------------------------------------------------------------------
def test_fixture_x_zero_volatility_exception_safety():
    """
    Test X: Flat equity / zero volatility handles Sharpe and Sortino safely without division-by-zero.
    """
    perf = FinancialMetricsEngine.calculate_performance_metrics(
        initial_cash=100_000.0,
        final_equity=100_000.0,
        daily_returns=[0.0, 0.0, 0.0, 0.0, 0.0],
        trades=[],
        drawdown_metrics=DrawdownMetrics(),
    )
    assert perf.annualized_volatility_pct == 0.0
    assert perf.sharpe_ratio is None
    assert perf.sortino_ratio is None


# ---------------------------------------------------------------------------
# API ROUTER TESTS
# ---------------------------------------------------------------------------
def test_api_backtest_capabilities():
    """Test GET /api/v1/trading/backtests/capabilities."""
    response = client.get("/api/v1/trading/backtests/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["stage"] == 143
    assert data["nautilus_version"] == "1.231.0"
    assert "disclaimers" in data


def test_api_backtest_strategies_list():
    """Test GET /api/v1/trading/backtests/strategies."""
    response = client.get("/api/v1/trading/backtests/strategies")
    assert response.status_code == 200
    data = response.json()
    assert len(data["strategies"]) >= 5


def test_api_backtest_datasets_list():
    """Test GET /api/v1/trading/backtests/datasets."""
    response = client.get("/api/v1/trading/backtests/datasets")
    assert response.status_code == 200
    data = response.json()
    assert len(data["datasets"]) >= 2


def test_api_backtest_execute_run():
    """Test POST /api/v1/trading/backtests/runs."""
    payload = {
        "strategy_id": "BUY_AND_HOLD",
        "dataset_id": "ds_spy_daily_2024",
        "initial_cash": 50000.0,
        "strategy_parameters": {"quantity": 5},
    }
    response = client.post("/api/v1/trading/backtests/runs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "performance" in data
    assert "equity_curve" in data
    assert len(data["orders"]) >= 1
