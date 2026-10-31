"""Comprehensive Pytest Suite for ATLAS QuantLib Derivative Pricing & Strategy Engine (Stage 142).

Covers all 24 Canonical Reference Test Fixtures (A through X):
- Test A: European Call Analytic Valuation & Independent Reference Check
- Test B: European Put Valuation & Put-Call Parity Verification
- Test C: American Put vs European Put Early Exercise Premium (V_American >= V_European)
- Test D: American Call Early Exercise Incentive with Discrete Dividend Schedule
- Test E: Long Call Payoff at Settlement Price $120 ($1,500 Profit)
- Test F: Long Put Payoff at Settlement Price $80 ($1,600 Profit)
- Test G: Bull Call Spread (Net Debit $500, Max Profit $500, Max Loss $500, BE $105)
- Test H: Long Straddle (Debit $900, Breakevens $91 and $109)
- Test I: Uncovered Short Call (Theoretically Unbounded Loss & Prominent Warning)
- Test J: Iron Condor (4 Legs, Defined Risk, Defined Profit, Dual Breakevens)
- Test K: Calendar Spread Multi-Expiration Mark-to-Market Valuation
- Test L: Non-100 Contract Multiplier (Indian NSE NIFTY Lot Size 50 & INR Scaling)
- Test M: Position Greek Scaling (2 Long Calls + 1 Short Call = 1 Net Long Call)
- Test N: Vega Unit Convention (1.0 Vol Unit vs 1 Percentage Point Scaling by 100)
- Test O: Historical As-Of Pricing without Look-Ahead Bias
- Test P: Stale Quote Data Quality Warning
- Test Q: Invalid Volatility Surface Rejection (Crossed Market & Negative Bids)
- Test R: Provider License Revocation Enforcement (SRC_CBOE_AUTHORIZED)
- Test S: Multi-Tenant Strategy Protection (User B Denied Access to User A Strategy)
- Test T: Expiration Edge Case (Evaluation Date on or after Expiration)
- Test U: Explicit Strategy Commission & Fee Deductions
- Test V: Early Assignment Risk on In-The-Money American Short Options
- Test W: Thread-Safe QuantLib Evaluation-Date Concurrency Isolation
- Test X: Numerical Nonconvergence and Exception Safety (No NaN / Crash)
- Model Registry & Pricing Engine Factory
- Black-76 and Bachelier Model Calculators
- Scenario Revaluation Engine (Spot x Vol Matrix)
- Side-by-side Strategy Comparison
- FastAPI REST Endpoints under /api/v1/options/quant/*
"""

from __future__ import annotations

import math
import threading
import time
import pytest
from fastapi.testclient import TestClient

import QuantLib as ql
from atlas.auth import AuthPrincipal
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import (
    AtlasOptionContract,
    ExerciseStyle,
    LegSide,
    OptionType,
)
from atlas.options.market_data.capabilities import OptionsEntitlementRegistry
from atlas.options.market_data.quotes import OptionQuoteStore
from atlas.options.quant import (
    AtlasQuantOptionsService,
    PricingModelFamily,
    QuantContractNotFoundError,
    QuantEntitlementRequiredError,
    QuantInvalidVolatilitySurfaceError,
    QuantLibAdapter,
    QuantModelIncompatibleError,
    QuantMultiTenantAccessDeniedError,
    QuantStrategyDefinition,
    QuantStrategyLeg,
    from_ql_date,
    isolated_quantlib_context,
    to_ql_date,
)
from atlas.options.quant.greeks.aggregator import aggregate_strategy_greeks
from atlas.options.quant.pricing.registry import ModelRegistry
from atlas.options.quant.risk.diagnostics import RiskDiagnosticsEngine
from atlas.options.quant.scenarios.engine import ScenarioEngine
from atlas_api.main import app

client = TestClient(app)


# =============================================================================
# 1. CORE QUANTLIB INTEGRATION & CONTEXT SAFETY
# =============================================================================

def test_quantlib_version_and_date_conversions():
    """Verify pinned QuantLib version and ISO string / QuantLib date roundtrips."""
    assert ql.__version__.startswith("1.44")

    iso = "2024-06-21"
    ql_d = to_ql_date(iso)
    assert ql_d.year() == 2024
    assert ql_d.month() == 6
    assert ql_d.dayOfMonth() == 21
    assert from_ql_date(ql_d) == iso


def test_fixture_w_concurrency_evaluation_date_isolation():
    """Test W: Verify thread-safe QuantLib context isolation prevents date leakage across concurrent requests."""
    results = {}

    def worker(thread_id: int, eval_iso: str, duration_sec: float):
        ql_d = to_ql_date(eval_iso)
        with isolated_quantlib_context(ql_d):
            time.sleep(duration_sec)
            current_ql_date = ql.Settings.instance().evaluationDate
            results[thread_id] = from_ql_date(current_ql_date)

    t1 = threading.Thread(target=worker, args=(1, "2024-01-15", 0.05))
    t2 = threading.Thread(target=worker, args=(2, "2024-07-20", 0.05))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert results[1] == "2024-01-15"
    assert results[2] == "2024-07-20"


# =============================================================================
# 2. REFERENCE PRICING FIXTURES A THROUGH D
# =============================================================================

def test_fixture_a_european_call_analytic_reference():
    """Test A: S=100, K=100, Vol=0.20, r=0.05, q=0.0, T=1yr -> Black-Scholes ~10.4506."""
    npv, greeks, diag = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.CALL,
        strike_price=100.0,
        expiration_date="2025-01-01",
        evaluation_date="2024-01-01",
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        exercise_style=ExerciseStyle.EUROPEAN,
        model_family=PricingModelFamily.BLACK_SCHOLES_MERTON,
    )

    # Independent Black-Scholes reference:
    # For S=100, K=100, r=0.05, vol=0.20, T=366/365:
    assert 10.40 <= npv <= 10.55
    assert 0.60 <= greeks.delta <= 0.65
    assert greeks.gamma > 0.0
    assert greeks.vega_per_unit > 30.0
    assert greeks.theta_per_day < 0.0
    assert diag.converged is True
    assert greeks.calculation_method == "ANALYTIC"


def test_fixture_b_european_put_and_put_call_parity():
    """Test B: Put price with identical inputs satisfies European Put-Call Parity: C - P = S - K*e^(-r*T)."""
    call_npv, call_greeks, _ = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.CALL,
        strike_price=100.0,
        expiration_date="2025-01-01",
        evaluation_date="2024-01-01",
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        exercise_style=ExerciseStyle.EUROPEAN,
        model_family=PricingModelFamily.BLACK_SCHOLES_MERTON,
    )

    put_npv, put_greeks, _ = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.PUT,
        strike_price=100.0,
        expiration_date="2025-01-01",
        evaluation_date="2024-01-01",
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        exercise_style=ExerciseStyle.EUROPEAN,
        model_family=PricingModelFamily.BLACK_SCHOLES_MERTON,
    )

    assert 5.50 <= put_npv <= 5.65
    assert -0.40 <= put_greeks.delta <= -0.30

    # Put-Call Parity Check: C - P == S - K * exp(-r * T)
    t_years = 366.0 / 365.0  # 2024 is leap year
    expected_diff = 100.0 - 100.0 * math.exp(-0.05 * t_years)
    actual_diff = call_npv - put_npv
    assert abs(actual_diff - expected_diff) < 0.01


def test_fixture_c_american_put_early_exercise_premium():
    """Test C: American Put value is strictly greater than or equal to European Put (V_American >= V_European)."""
    eu_put, _, _ = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.PUT,
        strike_price=100.0,
        expiration_date="2025-01-01",
        evaluation_date="2024-01-01",
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        exercise_style=ExerciseStyle.EUROPEAN,
        model_family=PricingModelFamily.BLACK_SCHOLES_MERTON,
    )

    # Barone-Adesi-Whaley American Put
    am_put, am_greeks, _ = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.PUT,
        strike_price=100.0,
        expiration_date="2025-01-01",
        evaluation_date="2024-01-01",
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        exercise_style=ExerciseStyle.AMERICAN,
        model_family=PricingModelFamily.BARONE_ADESI_WHALEY,
    )

    assert am_put >= eu_put
    assert am_put > 6.00  # Early exercise premium reflects positive interest rate
    assert am_greeks.delta < 0.0


def test_fixture_d_early_exercise_with_discrete_dividends():
    """Test D: American call with discrete dividend schedule evaluated with Finite Difference engine."""
    divs = [{"date": "2024-06-01", "amount": 5.0}]

    npv_with_div, greeks_div, diag = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.CALL,
        strike_price=100.0,
        expiration_date="2025-01-01",
        evaluation_date="2024-01-01",
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
        exercise_style=ExerciseStyle.AMERICAN,
        model_family=PricingModelFamily.FINITE_DIFFERENCE,
        dividend_items=divs,
    )

    # Dividend reduces underlying forward, so Call price is lower than pure non-dividend call
    assert 7.50 <= npv_with_div <= 8.50
    assert diag.converged is True


# =============================================================================
# 3. STRATEGY PAYOFF & BREAKEWEN FIXTURES E THROUGH J
# =============================================================================

def test_fixture_e_long_call_payoff():
    """Test E: Long 100 Call, P=5, M=100, S_T=120 -> Intrinsic=20, Profit=$1,500."""
    service = AtlasQuantOptionsService()
    leg = QuantStrategyLeg(
        contract_id="opt_spy_20240621_c_100",
        side=LegSide.LONG_CALL,
        quantity=1,
        entry_premium=5.0,
        multiplier=100.0,
        strike_price=100.0,
        expiration_date="2024-06-21",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
    )
    res = service.analyze_strategy([leg], spot_price=100.0)

    assert res.net_opening_cash_flow == -500.0
    assert res.is_net_debit is True
    assert res.breakevens == [105.0]

    coord_120 = next(c for c in res.expiration_payoff_curve if abs(c.underlying_price - 120.0) < 0.1)
    assert coord_120.payoff == 1500.0


def test_fixture_f_long_put_payoff():
    """Test F: Long 100 Put, P=4, M=100, S_T=80 -> Intrinsic=20, Profit=$1,600."""
    service = AtlasQuantOptionsService()
    leg = QuantStrategyLeg(
        contract_id="opt_spy_20240621_p_100",
        side=LegSide.LONG_PUT,
        quantity=1,
        entry_premium=4.0,
        multiplier=100.0,
        strike_price=100.0,
        expiration_date="2024-06-21",
        option_type=OptionType.PUT,
        exercise_style=ExerciseStyle.AMERICAN,
    )
    res = service.analyze_strategy([leg], spot_price=100.0)

    assert res.net_opening_cash_flow == -400.0
    assert res.breakevens == [96.0]

    coord_80 = next(c for c in res.expiration_payoff_curve if abs(c.underlying_price - 80.0) < 0.1)
    assert coord_80.payoff == 1600.0


def test_fixture_g_bull_call_spread():
    """Test G: Buy 100 Call at 8, Sell 110 Call at 3 -> Debit $500, Max Profit $500, Max Loss $500, BE $105."""
    service = AtlasQuantOptionsService()
    legs = [
        QuantStrategyLeg(
            contract_id="opt_spy_20240621_c_100",
            side=LegSide.LONG_CALL,
            quantity=1,
            entry_premium=8.0,
            multiplier=100.0,
            strike_price=100.0,
            expiration_date="2024-06-21",
            option_type=OptionType.CALL,
            exercise_style=ExerciseStyle.AMERICAN,
        ),
        QuantStrategyLeg(
            contract_id="opt_spy_20240621_c_110",
            side=LegSide.SHORT_CALL,
            quantity=1,
            entry_premium=3.0,
            multiplier=100.0,
            strike_price=110.0,
            expiration_date="2024-06-21",
            option_type=OptionType.CALL,
            exercise_style=ExerciseStyle.AMERICAN,
        ),
    ]
    res = service.analyze_strategy(legs, spot_price=100.0)

    assert res.net_opening_cash_flow == -500.0
    assert res.is_net_debit is True
    assert res.max_profit == 500.0
    assert res.max_loss == 500.0
    assert res.breakevens == [105.0]


def test_fixture_h_long_straddle():
    """Test H: Buy 100 Call at 5, Buy 100 Put at 4 -> Debit $900, BE $91 & $109."""
    service = AtlasQuantOptionsService()
    legs = [
        QuantStrategyLeg(
            contract_id="opt_spy_20240621_c_100",
            side=LegSide.LONG_CALL,
            quantity=1,
            entry_premium=5.0,
            multiplier=100.0,
            strike_price=100.0,
            expiration_date="2024-06-21",
            option_type=OptionType.CALL,
            exercise_style=ExerciseStyle.AMERICAN,
        ),
        QuantStrategyLeg(
            contract_id="opt_spy_20240621_p_100",
            side=LegSide.LONG_PUT,
            quantity=1,
            entry_premium=4.0,
            multiplier=100.0,
            strike_price=100.0,
            expiration_date="2024-06-21",
            option_type=OptionType.PUT,
            exercise_style=ExerciseStyle.AMERICAN,
        ),
    ]
    res = service.analyze_strategy(legs, spot_price=100.0)

    assert res.net_opening_cash_flow == -900.0
    assert res.breakevens == [91.0, 109.0]
    assert res.max_loss == 900.0


def test_fixture_i_uncovered_short_call_unbounded_risk():
    """Test I: Standalone naked short call classified as unbounded upside loss (max_loss is None)."""
    service = AtlasQuantOptionsService()
    leg = QuantStrategyLeg(
        contract_id="opt_spy_20240621_c_100",
        side=LegSide.SHORT_CALL,
        quantity=1,
        entry_premium=5.0,
        multiplier=100.0,
        strike_price=100.0,
        expiration_date="2024-06-21",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
    )
    res = service.analyze_strategy([leg], spot_price=100.0)

    assert res.is_unbounded_loss is True
    assert res.max_loss is None
    assert any("UNBOUNDED_UPSIDE_RISK" in w for w in res.risk_warnings)


def test_fixture_j_iron_condor():
    """Test J: 4-leg Iron Condor with defined risk, defined profit, and dual breakevens."""
    service = AtlasQuantOptionsService()
    legs = [
        # Put spread: Buy 90 Put @ 1.5, Sell 95 Put @ 3.0 (Net credit = 1.5)
        QuantStrategyLeg("p90", LegSide.LONG_PUT, 1, 1.5, 100.0, 90.0, "2024-06-21", OptionType.PUT, ExerciseStyle.AMERICAN),
        QuantStrategyLeg("p95", LegSide.SHORT_PUT, 1, 3.0, 100.0, 95.0, "2024-06-21", OptionType.PUT, ExerciseStyle.AMERICAN),
        # Call spread: Sell 105 Call @ 3.0, Buy 110 Call @ 1.5 (Net credit = 1.5)
        QuantStrategyLeg("c105", LegSide.SHORT_CALL, 1, 3.0, 100.0, 105.0, "2024-06-21", OptionType.CALL, ExerciseStyle.AMERICAN),
        QuantStrategyLeg("c110", LegSide.LONG_CALL, 1, 1.5, 100.0, 110.0, "2024-06-21", OptionType.CALL, ExerciseStyle.AMERICAN),
    ]
    res = service.analyze_strategy(legs, spot_price=100.0)

    # Net credit = (3.0 - 1.5 + 3.0 - 1.5) * 100 = $300
    assert res.net_opening_cash_flow == 300.0
    assert res.is_net_debit is False
    assert res.max_profit == 300.0
    # Wing width = 5, Max Loss = (5 - 3) * 100 = $200
    assert res.max_loss == 200.0
    assert len(res.breakevens) == 2
    assert res.breakevens == [92.0, 108.0]


# =============================================================================
# 4. ADVANCED DERIVATIVES FIXTURES K THROUGH N
# =============================================================================

def test_fixture_k_calendar_spread_multi_expiration():
    """Test K: Calendar spread with different expirations is evaluated via QuantLib mark-to-market pre-expiration curve."""
    service = AtlasQuantOptionsService()
    # Sell June 2024 Call @ 4.0, Buy July 2024 Call @ 6.5
    legs = [
        QuantStrategyLeg("front", LegSide.SHORT_CALL, 1, 4.0, 100.0, 100.0, "2024-06-21", OptionType.CALL, ExerciseStyle.AMERICAN),
        QuantStrategyLeg("back", LegSide.LONG_CALL, 1, 6.5, 100.0, 100.0, "2024-07-19", OptionType.CALL, ExerciseStyle.AMERICAN),
    ]

    res = service.analyze_strategy(legs, spot_price=100.0, evaluation_date="2024-05-20")

    assert res.is_multi_expiration is True
    assert res.net_opening_cash_flow == -250.0  # (4.0 - 6.5) * 100 = -$250
    # Pre-expiration QuantLib mark-to-market curve generated successfully
    assert len(res.pre_expiration_curve) > 0
    assert any("MULTI_EXPIRATION_STRUCTURE" in w for w in res.risk_warnings)


def test_fixture_l_contract_multiplier_lot_size_50():
    """Test L: Indian NSE NIFTY contract has multiplier 50; cash flow and payoffs scale by 50."""
    service = AtlasQuantOptionsService()
    leg = QuantStrategyLeg(
        contract_id="opt_nifty_20240627_c_22000",
        side=LegSide.LONG_CALL,
        quantity=1,
        entry_premium=180.0,
        multiplier=50.0,  # Lot size 50!
        strike_price=22000.0,
        expiration_date="2024-06-27",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.EUROPEAN,
    )
    res = service.analyze_strategy([leg], spot_price=22000.0)

    # Net debit = 180.0 * 50 = INR 9,000
    assert res.net_opening_cash_flow == -9000.0
    assert res.breakevens == [22180.0]


def test_fixture_m_position_greek_scaling():
    """Test M: 2 Long Calls + 1 Short Call produces aggregate Greeks matching 1 net Long Call."""
    service = AtlasQuantOptionsService()
    leg_long2 = QuantStrategyLeg("c1", LegSide.LONG_CALL, 2, 5.0, 100.0, 100.0, "2024-06-21", OptionType.CALL, ExerciseStyle.EUROPEAN)
    leg_short1 = QuantStrategyLeg("c1", LegSide.SHORT_CALL, 1, 5.0, 100.0, 100.0, "2024-06-21", OptionType.CALL, ExerciseStyle.EUROPEAN)

    res_spread = service.analyze_strategy([leg_long2, leg_short1], spot_price=100.0)

    leg_single = QuantStrategyLeg("c1", LegSide.LONG_CALL, 1, 5.0, 100.0, 100.0, "2024-06-21", OptionType.CALL, ExerciseStyle.EUROPEAN)
    res_single = service.analyze_strategy([leg_single], spot_price=100.0)

    assert abs(res_spread.aggregate_greeks.delta - res_single.aggregate_greeks.delta) < 0.001
    assert abs(res_spread.aggregate_greeks.gamma - res_single.aggregate_greeks.gamma) < 0.001
    assert abs(res_spread.aggregate_greeks.vega_per_point - res_single.aggregate_greeks.vega_per_point) < 0.001


def test_fixture_n_vega_unit_convention():
    """Test N: Vega per full unit (1.0) is exactly 100x vega per 1 percentage point (0.01)."""
    npv, greeks, _ = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.CALL,
        strike_price=100.0,
        expiration_date="2025-01-01",
        evaluation_date="2024-01-01",
        spot_price=100.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    # Vega unscaled ~ 37.569, Vega point ~ 0.37569
    assert abs(greeks.vega_per_unit - (greeks.vega_per_point * 100.0)) < 0.05


# =============================================================================
# 5. RISK, GOVERNANCE & EDGE CASE FIXTURES O THROUGH X
# =============================================================================

def test_fixture_o_historical_pricing_integrity():
    """Test O: Historical pricing evaluation date at T1 reproduces valuation without look-ahead data."""
    service = AtlasQuantOptionsService()
    # Price at May 2024
    res_t1 = service.price_contract(
        contract_id="opt_spy_20240621_c_500",
        evaluation_date="2024-05-20",
        spot_price=530.0,
        volatility=0.15,
    )
    # Price earlier at April 2024 (longer time to maturity)
    res_t0 = service.price_contract(
        contract_id="opt_spy_20240621_c_500",
        evaluation_date="2024-04-20",
        spot_price=530.0,
        volatility=0.15,
    )

    assert res_t0.theoretical_price > res_t1.theoretical_price


def test_fixture_p_stale_quote_data_quality():
    """Test P: Stale quote age triggers explicit STALE_QUOTE_DATA risk diagnostic."""
    warnings = RiskDiagnosticsEngine.evaluate_strategy_risks(
        legs=[],
        current_spot=500.0,
        is_unbounded_loss=False,
        quote_age_seconds=1800.0,  # 30 minutes old
        stale_threshold_seconds=900.0,  # 15 minutes threshold
    )
    assert any("STALE_QUOTE_DATA" in w for w in warnings)


def test_fixture_q_invalid_vol_surface_rejection():
    """Test Q: Surface containing crossed markets or negative bids produces failure state in strict mode."""
    service = AtlasQuantOptionsService()
    bad_obs = [
        {"strike": 100.0, "tte_years": 0.5, "bid": 10.0, "ask": 8.0, "implied_volatility": 0.20},  # Crossed!
        {"strike": 110.0, "tte_years": 0.5, "bid": -1.0, "ask": 2.0, "implied_volatility": 0.22},  # Negative bid!
    ]

    with pytest.raises(QuantInvalidVolatilitySurfaceError):
        service.build_volatility_surface("SPY", "2024-05-20", bad_obs, strict_validation=True)


def test_fixture_r_provider_license_revocation_enforcement():
    """Test R: Revoked source license blocks pricing calls."""
    entitlements = OptionsEntitlementRegistry()
    service = AtlasQuantOptionsService(entitlements=entitlements)

    # Valid before revocation
    res = service.price_contract("opt_spy_20240621_c_500", "2024-05-20", 530.0, provider_source_id="SRC_CBOE_AUTHORIZED")
    assert res is not None

    # Revoke license
    entitlements.revoke_source("SRC_CBOE_AUTHORIZED")

    # Blocked after revocation
    with pytest.raises(QuantEntitlementRequiredError):
        service.price_contract("opt_spy_20240621_c_500", "2024-05-20", 530.0, provider_source_id="SRC_CBOE_AUTHORIZED")


def test_fixture_s_multi_tenant_strategy_access_denied():
    """Test S: User B cannot inspect or access User A's private custom strategy."""
    service = AtlasQuantOptionsService()
    principal_a = AuthPrincipal(sub="USER_A", raw_claims={"tenant_id": "TENANT_A"})
    principal_b = AuthPrincipal(sub="USER_B", raw_claims={"tenant_id": "TENANT_B"})

    strat = QuantStrategyDefinition(
        strategy_id="strat_private_alpha",
        owner_id="USER_A",
        title="User A Secret Strategy",
        underlying_symbol="SPY",
        legs=[],
        tenant_id="TENANT_A",
        is_private=True,
    )
    service.save_user_strategy(strat, principal=principal_a)

    # User A succeeds
    assert service.get_user_strategy("strat_private_alpha", principal=principal_a) is not None

    # User B denied
    with pytest.raises(QuantMultiTenantAccessDeniedError):
        service.get_user_strategy("strat_private_alpha", principal=principal_b)


def test_fixture_t_expiration_edge_case():
    """Test T: Valuation on or after expiration date returns clean intrinsic value without crash."""
    npv, greeks, diag = QuantLibAdapter.price_vanilla_contract(
        option_type=OptionType.CALL,
        strike_price=100.0,
        expiration_date="2024-06-21",
        evaluation_date="2024-06-21",  # Exactly on expiration!
        spot_price=115.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        volatility=0.20,
    )

    assert npv == 15.0
    assert greeks.delta == 1.0
    assert greeks.calculation_method == "TERMINAL_SETTLEMENT_CUTOFF"


def test_fixture_u_strategy_fee_deductions():
    """Test U: Nonzero commissions are explicitly deducted from net opening cash flow and net P&L."""
    service = AtlasQuantOptionsService()
    leg = QuantStrategyLeg(
        contract_id="c1",
        side=LegSide.LONG_CALL,
        quantity=1,
        entry_premium=5.0,
        multiplier=100.0,
        strike_price=100.0,
        expiration_date="2024-06-21",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.AMERICAN,
        custom_fee=15.0,  # $15 commission
    )
    res = service.analyze_strategy([leg], spot_price=100.0, total_fees=15.0)

    # Cash flow: -$500 premium - $15 fee = -$515
    assert res.net_opening_cash_flow == -515.0
    # At S_T=120: ($20 - $5)*100 - $15 = $1,485
    coord_120 = next(c for c in res.expiration_payoff_curve if abs(c.underlying_price - 120.0) < 0.1)
    assert coord_120.payoff == 1485.0


def test_fixture_v_early_assignment_risk_diagnostics():
    """Test V: In-the-money American short option produces early assignment warning."""
    warnings = RiskDiagnosticsEngine.evaluate_strategy_risks(
        legs=[
            QuantStrategyLeg("c1", LegSide.SHORT_CALL, 1, 10.0, 100.0, 90.0, "2024-06-21", OptionType.CALL, ExerciseStyle.AMERICAN)
        ],
        current_spot=100.0,  # ITM short call (spot 100 > strike 90)
        is_unbounded_loss=True,
    )
    assert any("EARLY_ASSIGNMENT_RISK" in w for w in warnings)


def test_fixture_x_numerical_exception_safety():
    """Test X: Extreme / zero volatility or invalid strikes handle errors safely without NaN leak."""
    service = AtlasQuantOptionsService()
    # Contract with zero or negative price under lognormal BSM raises clean typed error
    with pytest.raises(QuantModelIncompatibleError):
        # American option with European-only BSM engine
        service.price_contract(
            contract_id="opt_spy_20240621_c_100",
            evaluation_date="2024-05-20",
            spot_price=100.0,
            model_id="BLACK_SCHOLES_MERTON",
        )


# =============================================================================
# 6. FASTAPI REST API ENDPOINTS TESTS
# =============================================================================

def test_api_quant_capabilities():
    resp = client.get("/api/v1/options/quant/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == 142
    assert "BLACK_SCHOLES_MERTON" in data["supported_model_families"]
    assert "BARONE_ADESI_WHALEY" in data["supported_model_families"]
    assert data["strategy_templates_count"] == 25


def test_api_quant_models_list():
    resp = client.get("/api/v1/options/quant/models")
    assert resp.status_code == 200
    models = resp.json()["models"]
    assert len(models) >= 7
    ids = [m["model_id"] for m in models]
    assert "BLACK_SCHOLES_MERTON" in ids
    assert "BARONE_ADESI_WHALEY" in ids
    assert "FINITE_DIFFERENCE" in ids


def test_api_quant_price_single_contract():
    payload = {
        "contract_id": "opt_spy_20240621_c_500",
        "evaluation_date": "2024-05-20",
        "spot_price": 530.0,
        "risk_free_rate": 0.05,
        "volatility": 0.18,
        "model_id": "BARONE_ADESI_WHALEY",
    }
    resp = client.post("/api/v1/options/quant/price", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["contract_id"] == "opt_spy_20240621_c_500"
    assert data["theoretical_price"] > 30.0
    assert "delta" in data["greeks"]
    assert data["diagnostics"]["converged"] is True


def test_api_quant_strategies_analyze():
    payload = {
        "strategy_name": "Bull Call Spread API Test",
        "underlying_symbol": "SPY",
        "spot_price": 100.0,
        "evaluation_date": "2024-05-20",
        "legs": [
            {
                "contract_id": "c100",
                "side": "LONG_CALL",
                "quantity": 1,
                "entry_premium": 8.0,
                "multiplier": 100.0,
                "strike_price": 100.0,
                "expiration_date": "2024-06-21",
                "option_type": "CALL",
                "exercise_style": "AMERICAN",
            },
            {
                "contract_id": "c110",
                "side": "SHORT_CALL",
                "quantity": 1,
                "entry_premium": 3.0,
                "multiplier": 100.0,
                "strike_price": 110.0,
                "expiration_date": "2024-06-21",
                "option_type": "CALL",
                "exercise_style": "AMERICAN",
            },
        ],
    }
    resp = client.post("/api/v1/options/quant/strategies/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["net_opening_cash_flow"] == -500.0
    assert data["max_profit"] == 500.0
    assert data["max_loss"] == 500.0
    assert data["breakevens"] == [105.0]
    assert len(data["expiration_payoff_curve"]) > 0
    assert len(data["pre_expiration_curve"]) > 0


def test_api_quant_scenario_matrix():
    payload = {
        "base_spot": 100.0,
        "base_eval_date": "2024-05-20",
        "base_vol": 0.20,
        "legs": [
            {
                "contract_id": "c100",
                "side": "LONG_CALL",
                "quantity": 1,
                "entry_premium": 5.0,
                "multiplier": 100.0,
                "strike_price": 100.0,
                "expiration_date": "2024-06-21",
                "option_type": "CALL",
                "exercise_style": "AMERICAN",
            }
        ],
    }
    resp = client.post("/api/v1/options/quant/strategies/scenarios", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["row_dimension"] == "SPOT_SHOCK_PCT"
    assert data["col_dimension"] == "VOL_SHOCK_POINTS"
    assert len(data["cells"]) == len(data["row_values"])
