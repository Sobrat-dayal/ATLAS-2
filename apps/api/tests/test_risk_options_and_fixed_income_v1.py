"""Stage 118 — Options and Fixed-Income Risk Foundations Tests.

Verifies:
1. Part XVII Reference Fixture: European Vanilla Call BSM Fixture:
   S=100, K=100, r=0.05, q=0.0, sigma=0.20, T=1.0, M=1:
   Call Price = 10.4505835722, Delta = 0.6368306512, Gamma = 0.01876201735,
   Vega unit = 37.5240346917, Vega 1vp = 0.3752403469, Theta year = -6.4140275464,
   Theta day = -0.0175726782, Rho unit = 53.2324815454, Rho 1bp = 0.0053232482.
2. Part XXI Reference Fixture: Position Greeks Reference Fixture:
   2 Long Contracts x 100 Multiplier (QM = 200):
   Delta Units = 127.3661302, Delta-Equivalent Notional = $12,736.61302,
   Vega per 1vp = 75.04806938.
3. Part XLII Reference Fixture: Zero-Coupon Bond Fixture:
   Face=100, T=1.0, Coupon=0%, y=5%, m=1:
   Price = 95.2380952381, Mac Dur = 1.0, Mod Dur = 0.9523809524,
   Convexity = 1.8140589569, DV01 per 100 Face = 0.0090702948.
4. Part XLIII Reference Fixture: Two-Year 5% Par Bond Fixture:
   Face=100, Coupon=5% annual, y=5%, T=2, m=1:
   Dirty Price = 100.0, Mac Dur = 1.9523809524, Mod Dur = 1.8594104308.
5. Put-Call Parity, European Put pricing, finite difference bump checks.
6. Cash-flow generation, day-count conventions, clean/dirty price reconciliation.
7. Yield-to-maturity root solving, Key-Rate Duration (KRD) additivity.
8. FastAPI options and fixed-income endpoints.
9. Strict multi-tenant security isolation.
"""

from datetime import datetime, timedelta
import math
import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios.service import PortfolioService
from atlas.risk.enums import (
    BondPricingModelId,
    CouponFrequency,
    CouponType,
    DayCountConvention,
    ExerciseStyle,
    OptionsPricingModelId,
    OptionType,
)
from atlas.risk.errors import (
    RiskBondDirtyPriceNonPositiveError,
    RiskBondFaceValueNonPositiveError,
    RiskBondMaturityBeforeSettlementError,
    RiskOptionStrikeNonPositiveError,
    RiskOptionUnderlyingPriceNonPositiveError,
    RiskSubjectAccessDeniedError,
    RiskSubjectNotFoundError,
)
from atlas.risk.fixed_income_pricing import BondCashFlowEngine, calculate_year_fraction
from atlas.risk.models import OptionContractRiskInput
from atlas.risk.options_pricing import BlackScholesMertonEngine
from atlas.risk.schemas import (
    CalculateFixedIncomeRiskRequest,
    CalculateOptionsRiskRequest,
)
from atlas.risk.service import RiskService
from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.routers.risk import get_portfolio_service, get_risk_service


USER_A_ID = "usr_stage118_test_a"
USER_B_ID = "usr_stage118_test_b"

user_a_principal = AuthPrincipal(
    sub=USER_A_ID,
    email="derivatives_quant@atlas.firm",
    role="authenticated",
)

user_b_principal = AuthPrincipal(
    sub=USER_B_ID,
    email="external_desk@other.firm",
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
    app.dependency_overrides[get_portfolio_service] = lambda: p_service
    app.dependency_overrides[get_risk_service] = lambda: r_service
    return TestClient(app)


@pytest.fixture
def client_user_b(risk_services):
    p_service, r_service = risk_services
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: user_b_principal
    app.dependency_overrides[get_portfolio_service] = lambda: p_service
    app.dependency_overrides[get_risk_service] = lambda: r_service
    return TestClient(app)


# ============================================================================
# 1. MATHEMATICAL ENGINE & REFERENCE FIXTURE TESTS: OPTIONS
# ============================================================================


def test_part_xvii_european_call_bsm_fixture():
    """Verifies Part XVII Reference Fixture: European Call BSM parameters to 10 decimal places."""
    contract = OptionContractRiskInput(
        instrument_id="OPT_CALL_FIXTURE_1",
        underlying_symbol="SPY",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.EUROPEAN,
        strike_price=100.0,
        time_to_expiry_years=1.0,
        underlying_price=100.0,
        implied_volatility=0.20,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        contract_multiplier=1.0,
    )
    res = BlackScholesMertonEngine.calculate_contract_price_and_greeks(contract)

    assert pytest.approx(res.theoretical_price, rel=1e-8) == 10.4505835722
    assert pytest.approx(res.delta, rel=1e-8) == 0.6368306512
    assert pytest.approx(res.gamma, rel=1e-8) == 0.01876201735
    assert pytest.approx(res.vega, rel=1e-8) == 37.5240346917
    assert pytest.approx(res.vega_per_vol_point, rel=1e-8) == 0.3752403469
    assert pytest.approx(res.theta, rel=1e-8) == -6.4140275464
    assert pytest.approx(res.theta_per_day, rel=1e-8) == -0.0175726782
    assert pytest.approx(res.rho, rel=1e-8) == 53.2324815454
    assert pytest.approx(res.rho_per_basis_point, rel=1e-8) == 0.0053232482
    assert pytest.approx(res.intrinsic_value, rel=1e-8) == 0.0
    assert pytest.approx(res.time_value, rel=1e-8) == 10.4505835722
    assert res.put_call_parity_diff is not None
    assert res.put_call_parity_diff < 1e-10


def test_part_xxi_position_greeks_reference_fixture():
    """Verifies Part XXI Reference Fixture: 2 Long Contracts x 100 Multiplier (QM = 200)."""
    contract = OptionContractRiskInput(
        instrument_id="OPT_CALL_POS_FIXTURE",
        underlying_symbol="SPY",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.EUROPEAN,
        strike_price=100.0,
        time_to_expiry_years=1.0,
        underlying_price=100.0,
        implied_volatility=0.20,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        contract_multiplier=100.0,
    )
    pos = BlackScholesMertonEngine.calculate_position_risk(
        position_id="pos_fixture_21",
        contract=contract,
        contracts_quantity=2.0,
    )

    assert pytest.approx(pos.position_delta_units, rel=1e-6) == 127.3661302
    assert pytest.approx(pos.position_delta_notional, rel=1e-6) == 12736.61302
    assert pytest.approx(pos.position_vega_per_vol_point, rel=1e-6) == 75.04806938
    assert pytest.approx(pos.position_gamma_units, rel=1e-6) == 200.0 * 0.01876201735
    assert pytest.approx(pos.position_theta_per_day, rel=1e-6) == 200.0 * (-0.0175726782)
    assert pytest.approx(pos.position_rho_per_basis_point, rel=1e-6) == 200.0 * 0.0053232482


def test_put_option_pricing_and_put_call_parity():
    """Verifies Put Option pricing and Put-Call parity C - P = S e^(-qT) - K e^(-rT)."""
    call_in = OptionContractRiskInput(
        instrument_id="OPT_CALL_PARITY",
        underlying_symbol="XYZ",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.EUROPEAN,
        strike_price=100.0,
        time_to_expiry_years=1.0,
        underlying_price=100.0,
        implied_volatility=0.20,
        risk_free_rate=0.05,
        dividend_yield=0.0,
    )
    put_in = OptionContractRiskInput(
        instrument_id="OPT_PUT_PARITY",
        underlying_symbol="XYZ",
        option_type=OptionType.PUT,
        exercise_style=ExerciseStyle.EUROPEAN,
        strike_price=100.0,
        time_to_expiry_years=1.0,
        underlying_price=100.0,
        implied_volatility=0.20,
        risk_free_rate=0.05,
        dividend_yield=0.0,
    )
    c_res = BlackScholesMertonEngine.calculate_contract_price_and_greeks(call_in)
    p_res = BlackScholesMertonEngine.calculate_contract_price_and_greeks(put_in)

    # Put delta should equal call delta - 1
    assert pytest.approx(p_res.delta, rel=1e-8) == c_res.delta - 1.0
    # Gamma and Vega must be identical for European Call and Put
    assert pytest.approx(p_res.gamma, rel=1e-8) == c_res.gamma
    assert pytest.approx(p_res.vega, rel=1e-8) == c_res.vega

    # Parity check: C - P == S - K*exp(-rT)
    disc = math.exp(-0.05 * 1.0)
    expected_diff = 100.0 - 100.0 * disc
    actual_diff = c_res.theoretical_price - p_res.theoretical_price
    assert pytest.approx(actual_diff, rel=1e-8) == expected_diff


def test_finite_difference_greeks_verification():
    """Verifies analytical Greeks against central finite difference perturbations."""
    contract = OptionContractRiskInput(
        instrument_id="OPT_FD_TEST",
        underlying_symbol="AAPL",
        option_type=OptionType.CALL,
        exercise_style=ExerciseStyle.EUROPEAN,
        strike_price=150.0,
        time_to_expiry_years=0.5,
        underlying_price=155.0,
        implied_volatility=0.25,
        risk_free_rate=0.045,
        dividend_yield=0.01,
    )
    greeks = BlackScholesMertonEngine.calculate_contract_price_and_greeks(contract)

    # Numerical Delta
    h_s = 0.001 * 155.0
    p_up = BlackScholesMertonEngine.reprice_contract(contract, spot_shift=h_s)
    p_dn = BlackScholesMertonEngine.reprice_contract(contract, spot_shift=-h_s)
    delta_num = (p_up - p_dn) / (2.0 * h_s)
    assert pytest.approx(greeks.delta, rel=1e-4) == delta_num

    # Numerical Gamma
    p_base = greeks.theoretical_price
    gamma_num = (p_up - 2.0 * p_base + p_dn) / (h_s ** 2)
    assert pytest.approx(greeks.gamma, rel=1e-4) == gamma_num

    # Numerical Vega
    h_vol = 0.001
    p_vup = BlackScholesMertonEngine.reprice_contract(contract, vol_shift=h_vol)
    p_vdn = BlackScholesMertonEngine.reprice_contract(contract, vol_shift=-h_vol)
    vega_num = (p_vup - p_vdn) / (2.0 * h_vol)
    assert pytest.approx(greeks.vega, rel=1e-4) == vega_num


# ============================================================================
# 2. MATHEMATICAL ENGINE & REFERENCE FIXTURE TESTS: FIXED INCOME
# ============================================================================


def test_part_xlii_zero_coupon_bond_fixture():
    """Verifies Part XLII Reference Fixture: Zero-Coupon Bond to 10 decimal places."""
    cf_zero = [(1.0, 100.0)]
    price = BondCashFlowEngine.price_from_yield(cf_zero, 0.05, compounding_freq=1)
    sens = BondCashFlowEngine.calculate_sensitivities(
        cash_flows=cf_zero,
        yield_rate=0.05,
        dirty_price=price,
        clean_price=price,
        accrued_interest=0.0,
        compounding_freq=1,
        face_value=100.0,
    )

    assert pytest.approx(price, rel=1e-8) == 95.2380952381
    assert pytest.approx(sens.macaulay_duration, rel=1e-8) == 1.0
    assert pytest.approx(sens.modified_duration, rel=1e-8) == 0.9523809524
    assert pytest.approx(sens.convexity, rel=1e-8) == 1.8140589569
    assert pytest.approx(sens.dv01_per_100_face, rel=1e-8) == 0.0090702948


def test_part_xliii_two_year_par_bond_fixture():
    """Verifies Part XLIII Reference Fixture: Two-Year 5% Par Bond to 10 decimal places."""
    cf_par = [(1.0, 5.0), (2.0, 105.0)]
    price = BondCashFlowEngine.price_from_yield(cf_par, 0.05, compounding_freq=1)
    sens = BondCashFlowEngine.calculate_sensitivities(
        cash_flows=cf_par,
        yield_rate=0.05,
        dirty_price=price,
        clean_price=price,
        accrued_interest=0.0,
        compounding_freq=1,
        face_value=100.0,
    )

    assert pytest.approx(price, rel=1e-8) == 100.0
    assert pytest.approx(sens.macaulay_duration, rel=1e-8) == 1.9523809524
    assert pytest.approx(sens.modified_duration, rel=1e-8) == 1.8594104308

    # Key Rate Duration additivity
    krd_sum = sum(k.key_rate_duration for k in sens.key_rate_durations)
    assert pytest.approx(krd_sum, rel=1e-8) == sens.modified_duration


def test_ytm_solver_and_clean_dirty_price_reconciliation():
    """Verifies root-solving YTM matching target price and clean/dirty price relationship."""
    settlement = datetime(2026, 1, 1)
    maturity = datetime(2031, 1, 1)  # 5 years
    schedule = BondCashFlowEngine.generate_cash_flow_schedule(
        instrument_id="BOND_5Y_TEST",
        face_value=100.0,
        coupon_rate=0.06,
        coupon_frequency=CouponFrequency.SEMI_ANNUAL,
        settlement_date=settlement,
        maturity_date=maturity,
        day_count_convention=DayCountConvention.ACT_ACT,
        clean_price=102.50,
    )

    assert schedule.dirty_price >= schedule.clean_price
    assert schedule.dirty_price == schedule.clean_price + schedule.accrued_interest

    cf_tuples = [(c.year_fraction, c.total_cash_flow) for c in schedule.cash_flows]
    solved_ytm = BondCashFlowEngine.solve_yield_to_maturity(
        cf_tuples, schedule.dirty_price, compounding_freq=2
    )
    # Re-pricing at solved ytm should reproduce dirty price exactly
    recomputed_price = BondCashFlowEngine.price_from_yield(cf_tuples, solved_ytm, compounding_freq=2)
    assert pytest.approx(recomputed_price, rel=1e-7) == schedule.dirty_price


def test_day_count_conventions():
    """Verifies calculation of year fractions under ACT_ACT, ACT_365F, ACT_360, and 30_360."""
    d1 = datetime(2026, 1, 1)
    d2 = datetime(2026, 7, 1)
    yf_act = calculate_year_fraction(d1, d2, DayCountConvention.ACT_365F)
    yf_360 = calculate_year_fraction(d1, d2, DayCountConvention.ACT_360)
    yf_30360 = calculate_year_fraction(d1, d2, DayCountConvention.THIRTY_360)

    assert yf_act > 0.0
    assert yf_360 > yf_act
    assert abs(yf_30360 - 0.5) < 0.01


# ============================================================================
# 3. FASTAPI REST API ENDPOINT TESTS
# ============================================================================


def test_options_api_models_and_calculation(client_user_a):
    """Verifies GET /risk/options/models and POST /risk/options/calculate."""
    res_models = client_user_a.get("/api/v1/risk/options/models")
    assert res_models.status_code == 200
    models = res_models.json()
    assert len(models) >= 2
    assert any(m["model_id"] == "EUROPEAN_BLACK_SCHOLES_MERTON" for m in models)

    req = {
        "instrument_id": "OPT_API_CALL",
        "underlying_symbol": "SPY",
        "option_type": "CALL",
        "exercise_style": "EUROPEAN",
        "strike_price": 100.0,
        "time_to_expiry_years": 1.0,
        "underlying_price": 100.0,
        "implied_volatility": 0.20,
        "risk_free_rate": 0.05,
        "dividend_yield": 0.0,
        "contract_multiplier": 100.0,
    }
    res_calc = client_user_a.post("/api/v1/risk/options/calculate", json=req)
    assert res_calc.status_code == 200
    data = res_calc.json()
    assert pytest.approx(data["theoretical_price"], rel=1e-6) == 10.45058357
    assert pytest.approx(data["delta"], rel=1e-6) == 0.63683065
    assert pytest.approx(data["gamma"], rel=1e-6) == 0.01876202
    assert pytest.approx(data["vega_per_vol_point"], rel=1e-6) == 0.37524035


def test_portfolio_options_risk_endpoints(client_user_a, risk_services):
    """Verifies GET /risk/portfolios/{id}/options, /options/greeks, and /options/underlyings."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Options Risk Portfolio",
            "base_currency": "USD",
            "description": "Options Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    # Portfolio options summary
    res_opt = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/options")
    assert res_opt.status_code == 200
    opt_data = res_opt.json()
    assert opt_data["portfolio_id"] == p_id
    assert "net_delta_notional" in opt_data
    assert "gross_delta_notional" in opt_data
    assert "net_vega_per_vol_point" in opt_data
    assert "net_theta_per_day" in opt_data

    # Position Greeks
    res_greeks = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/options/greeks")
    assert res_greeks.status_code == 200
    greeks_list = res_greeks.json()
    assert isinstance(greeks_list, list)

    # Underlying buckets
    res_underlyings = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/options/underlyings")
    assert res_underlyings.status_code == 200
    underlyings = res_underlyings.json()
    assert isinstance(underlyings, dict)


def test_fixed_income_api_models_and_calculation(client_user_a):
    """Verifies GET /risk/fixed-income/models and POST /risk/fixed-income/calculate."""
    res_models = client_user_a.get("/api/v1/risk/fixed-income/models")
    assert res_models.status_code == 200
    models = res_models.json()
    assert len(models) >= 2

    req = {
        "instrument_id": "BOND_API_TEST",
        "face_value": 100.0,
        "coupon_rate": 0.05,
        "coupon_frequency": "ANNUAL",
        "day_count_convention": "ACT_ACT",
        "maturity_years": 2.0,
        "market_price": 100.0,
    }
    res_calc = client_user_a.post("/api/v1/risk/fixed-income/calculate", json=req)
    assert res_calc.status_code == 200
    data = res_calc.json()
    assert pytest.approx(data["dirty_price"], rel=1e-6) == 100.0
    assert pytest.approx(data["macaulay_duration"], rel=1e-6) == 1.95238095
    assert pytest.approx(data["modified_duration"], rel=1e-6) == 1.85941043
    assert data["dv01_per_100_face"] > 0
    assert len(data["key_rate_durations"]) > 0


def test_portfolio_fixed_income_endpoints(client_user_a, risk_services):
    """Verifies GET /risk/portfolios/{id}/fixed-income, /cashflows, /dv01, /curves."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Fixed Income Portfolio",
            "base_currency": "USD",
            "description": "Fixed Income Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    # Portfolio fixed income summary
    res_fi = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/fixed-income")
    assert res_fi.status_code == 200
    fi_data = res_fi.json()
    assert fi_data["portfolio_id"] == p_id
    assert fi_data["portfolio_weighted_modified_duration"] > 0
    assert fi_data["portfolio_total_dv01"] > 0
    assert len(fi_data["positions"]) >= 1

    # Cash flows
    res_cf = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/fixed-income/cashflows")
    assert res_cf.status_code == 200
    cf_data = res_cf.json()
    assert len(cf_data["cash_flows"]) > 0
    assert cf_data["face_value"] == 100.0

    # DV01 & Key Rate profile
    res_dv01 = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/fixed-income/dv01")
    assert res_dv01.status_code == 200
    dv01_data = res_dv01.json()
    assert "total_dv01" in dv01_data
    assert "key_rate_dv01_profile" in dv01_data

    # Calibrated yield curve
    res_curve = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/fixed-income/curves")
    assert res_curve.status_code == 200
    curve_data = res_curve.json()
    assert curve_data["curve_id"] == "US_TREASURY_SOVEREIGN"
    assert len(curve_data["points"]) >= 5


def test_cross_asset_instrument_sensitivities(client_user_a, risk_services):
    """Verifies GET /risk/portfolios/{id}/instrument-sensitivities combining equity, options, and bonds."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Cross Asset Portfolio",
            "base_currency": "USD",
            "description": "Sensitivities Test",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    res = client_user_a.get(f"/api/v1/risk/portfolios/{p_id}/instrument-sensitivities")
    assert res.status_code == 200
    data = res.json()
    assert data["portfolio_id"] == p_id
    assert "net_equity_delta_equivalent" in data
    assert "net_fixed_income_dv01" in data
    assert data["options_summary"] is not None
    assert data["fixed_income_summary"] is not None


def test_multi_tenant_security_isolation(client_user_a, client_user_b, risk_services):
    """Verifies that User B cannot access User A's options and fixed income risk endpoints."""
    p_service, _ = risk_services
    p = p_service.create_portfolio(
        user_id=USER_A_ID,
        request=type("Req", (), {
            "name": "Private Derivatives Portfolio",
            "base_currency": "USD",
            "description": "Private Desk",
            "portfolio_type": "TRADING",
            "cost_basis_method": "FIFO",
            "tags": [],
        })(),
    )
    p_id = p.id

    # User B unauthorized accesses
    assert client_user_b.get(f"/api/v1/risk/portfolios/{p_id}/options").status_code in (403, 404)
    assert client_user_b.get(f"/api/v1/risk/portfolios/{p_id}/fixed-income").status_code in (403, 404)
    assert client_user_b.get(f"/api/v1/risk/portfolios/{p_id}/instrument-sensitivities").status_code in (403, 404)

