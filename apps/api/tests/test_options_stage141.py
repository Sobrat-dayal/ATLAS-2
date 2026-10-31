"""Comprehensive Pytest Suite for ATLAS Options Analytics (Stage 141).

Tests:
- Reference Test Fixtures A through R:
  * Test A: Standard Call Intrinsic and Expiration Payoff ($1,500)
  * Test B: Standard Put Intrinsic and Expiration Payoff ($1,600)
  * Test C: Long Call Out-Of-The-Money Total Premium Loss (-$500)
  * Test D: Bull Call Spread (Net Debit $500, Max Profit $500, Max Loss $500, Breakeven $105)
  * Test E: Long Straddle (Debit $900, Breakevens $91 and $109, Max Loss $900)
  * Test F: Short Call Unbounded Upside Loss Classification (Max Loss is None)
  * Test G: Nonstandard Deliverables Excluded from Vanilla Payoff
  * Test H: Zero Bid Market Handling (No invented bid > 0)
  * Test I: Crossed Market Data Quality Flagging (Bid > Ask)
  * Test J: Stale Quote Flagging
  * Test K: Open Interest Prior Reporting Date Fidelity
  * Test L: Missing Greeks Fidelity (No artificial zeros)
  * Test M: Multi-Expiration Calendar Spread Exclusion (Stage 142 Boundary)
  * Test N: Non-100 Multipliers (Indian NSE NIFTY Lot Size 50 & INR Currency)
  * Test O: Corporate Action Reconciliation and Adjustment History
  * Test P: Private Portfolio Protection & Tenant Isolation
  * Test Q: Provider License Revocation Enforcement
  * Test R: No Broker Action or Order Routing
- Symbology (OSI 21-character format and Indian NSE)
- FastAPI REST Endpoints
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.options import (
    AtlasOptionsService,
    ContractAdjustmentStatus,
    LegSide,
    MoneynessState,
    OptionStrategyLeg,
    OptionType,
    OptionsAdjustedDeliverableUnsupportedError,
    OptionsEntitlementRequiredError,
    OptionsMultiExpirationPayoffUnsupportedError,
    OptionsTenantAccessDeniedError,
    QuoteQualityFlag,
)
from atlas.options.contracts.identifiers import format_osi_symbol, parse_osi_symbol
from atlas.options.market_data.capabilities import OptionsEntitlementRegistry
from atlas.options.strategies.payoff import calculate_leg_expiration_payoff
from atlas_api.main import app

client = TestClient(app)


# =============================================================================
# 1. CORE CAPABILITIES & SYMBOLOGY
# =============================================================================

def test_options_capabilities_and_disclaimers():
    service = AtlasOptionsService()
    caps = service.get_capabilities()

    assert caps["stage"] == 141
    assert caps["system_name"] == "ATLAS Options Analytics Terminal"
    assert "US_OPTIONS" in caps["supported_markets"]
    assert "NSE_DERIVATIVES" in caps["supported_markets"]
    assert "options_risk" in caps["disclaimers"]
    assert "execution" in caps["disclaimers"]
    assert "stage142_boundary" in caps["disclaimers"]


def test_osi_symbol_formatting_and_parsing():
    osi = format_osi_symbol("SPY", "2024-06-21", OptionType.CALL, 100.0)
    assert len(osi) == 21
    assert osi == "SPY   240621C00100000"

    parsed = parse_osi_symbol(osi)
    assert parsed["root"] == "SPY"
    assert parsed["expiration_date"] == "2024-06-21"
    assert parsed["option_type"] == OptionType.CALL
    assert parsed["strike_price"] == 100.0


# =============================================================================
# 2. REFERENCE TEST FIXTURES A THROUGH R
# =============================================================================

def test_fixture_a_standard_call_payoff():
    """Test A: S_T=$120, K=$100, P=$5, M=100 -> Intrinsic=$20, Expiration P&L=$1,500."""
    service = AtlasOptionsService()
    legs = [
        OptionStrategyLeg(
            contract_id="opt_spy_20240621_c_100",
            side=LegSide.LONG_CALL,
            quantity=1,
            entry_premium=5.0,
            multiplier=100.0,
        )
    ]
    res = service.analyze_strategy(legs, strategy_name="Standard Long Call", total_fees=0.0)

    # Net debit = $5 * 100 = -$500 cash flow
    assert res.net_opening_cash_flow == -500.0
    assert res.is_net_debit is True
    assert res.breakevens == [105.0]  # K + P = $100 + $5 = $105

    # Check payoff at S_T = $120
    coord_120 = next(c for c in res.payoff_curve if abs(c.underlying_price - 120.0) < 0.1)
    assert coord_120.payoff == 1500.0


def test_fixture_b_standard_put_payoff():
    """Test B: S_T=$80, K=$100, P=$4, M=100 -> Intrinsic=$20, Expiration P&L=$1,600."""
    service = AtlasOptionsService()
    legs = [
        OptionStrategyLeg(
            contract_id="opt_spy_20240621_p_100",
            side=LegSide.LONG_PUT,
            quantity=1,
            entry_premium=4.0,
            multiplier=100.0,
        )
    ]
    res = service.analyze_strategy(legs, strategy_name="Standard Long Put", total_fees=0.0)

    assert res.net_opening_cash_flow == -400.0
    assert res.breakevens == [96.0]  # K - P = $100 - $4 = $96

    # Check payoff at S_T = $80
    coord_80 = next(c for c in res.payoff_curve if abs(c.underlying_price - 80.0) < 0.1)
    assert coord_80.payoff == 1600.0


def test_fixture_c_long_call_loss():
    """Test C: K=$100, P=$5, S_T=$80, M=100 -> Intrinsic=$0, Expiration P&L=-$500."""
    service = AtlasOptionsService()
    legs = [
        OptionStrategyLeg(
            contract_id="opt_spy_20240621_c_100",
            side=LegSide.LONG_CALL,
            quantity=1,
            entry_premium=5.0,
            multiplier=100.0,
        )
    ]
    res = service.analyze_strategy(legs, total_fees=0.0)

    coord_80 = next(c for c in res.payoff_curve if abs(c.underlying_price - 80.0) < 0.1)
    assert coord_80.payoff == -500.0
    assert res.max_loss == 500.0


def test_fixture_d_bull_call_spread():
    """Test D: Buy 100 Call at $8, Sell 110 Call at $3 -> Net Debit $500, Max Profit $500, Max Loss $500, Breakeven $105."""
    service = AtlasOptionsService()
    legs = [
        OptionStrategyLeg(contract_id="opt_spy_20240621_c_100", side=LegSide.LONG_CALL, quantity=1, entry_premium=8.0, multiplier=100.0),
        OptionStrategyLeg(contract_id="opt_spy_20240621_c_110", side=LegSide.SHORT_CALL, quantity=1, entry_premium=3.0, multiplier=100.0),
    ]
    res = service.analyze_strategy(legs, strategy_name="Bull Call Spread", total_fees=0.0)

    assert res.net_opening_cash_flow == -500.0  # Net debit = ($8 - $3) * 100 = $500
    assert res.is_net_debit is True
    assert res.max_profit == 500.0  # ($10 strike diff - $5 debit) * 100 = $500
    assert res.max_loss == 500.0  # Net debit paid
    assert res.breakevens == [105.0]  # $100 + $5 = $105
    assert res.is_unbounded_loss is False


def test_fixture_e_long_straddle():
    """Test E: Buy 100 Call at $5, Buy 100 Put at $4 -> Debit $900, Breakevens $91 and $109, Max Loss $900."""
    service = AtlasOptionsService()
    legs = [
        OptionStrategyLeg(contract_id="opt_spy_20240621_c_100", side=LegSide.LONG_CALL, quantity=1, entry_premium=5.0, multiplier=100.0),
        OptionStrategyLeg(contract_id="opt_spy_20240621_p_100", side=LegSide.LONG_PUT, quantity=1, entry_premium=4.0, multiplier=100.0),
    ]
    res = service.analyze_strategy(legs, strategy_name="Long Straddle", total_fees=0.0)

    assert res.net_opening_cash_flow == -900.0
    assert res.breakevens == [91.0, 109.0]
    assert res.max_loss == 900.0
    assert res.is_unbounded_profit is True  # Unlimited upside


def test_fixture_f_short_call_unbounded_loss():
    """Test F: Sell 100 Call at $5 -> credit $500, unbounded upside loss flagged, max_loss is None."""
    service = AtlasOptionsService()
    legs = [
        OptionStrategyLeg(
            contract_id="opt_spy_20240621_c_100",
            side=LegSide.SHORT_CALL,
            quantity=1,
            entry_premium=5.0,
            multiplier=100.0,
        )
    ]
    res = service.analyze_strategy(legs, strategy_name="Short Call Naked", total_fees=0.0)

    assert res.net_opening_cash_flow == 500.0  # Credit received
    assert res.is_net_debit is False
    assert res.max_profit == 500.0
    # Crucial: Naked short call max loss is mathematically unbounded, NEVER capped!
    assert res.is_unbounded_loss is True
    assert res.max_loss is None
    assert any("UNBOUNDED" in w for w in res.risk_warnings)


def test_fixture_g_nonstandard_deliverable_rejection():
    """Test G: Adjusted option delivering nonstandard shares + cash is blocked from standard vanilla payoff."""
    service = AtlasOptionsService()
    adj_contract = service.get_contract("opt_xyz_adj_split_c_50")
    assert adj_contract.adjustment_status == ContractAdjustmentStatus.ADJUSTED_CORPORATE_ACTION
    assert adj_contract.deliverable.shares_count == 150.0
    assert adj_contract.deliverable.cash_amount == 250.0

    legs = [
        OptionStrategyLeg(
            contract_id="opt_xyz_adj_split_c_50",
            side=LegSide.LONG_CALL,
            quantity=1,
            entry_premium=6.0,
            multiplier=100.0,
        )
    ]
    with pytest.raises(OptionsAdjustedDeliverableUnsupportedError) as exc_info:
        service.analyze_strategy(legs)
    assert "nonstandard corporate-action adjusted deliverables" in str(exc_info.value)


def test_fixture_h_zero_bid_liquidity_flag():
    """Test H: Bid = 0, Ask = 0.50 -> Valid arithmetic, no invented bid > 0, ZERO_BID flag attached."""
    service = AtlasOptionsService()
    quote = service.get_quote("opt_spy_20240621_c_520")

    assert quote.bid == 0.0
    assert quote.ask == 0.50
    assert QuoteQualityFlag.ZERO_BID in quote.quality_flags


def test_fixture_i_crossed_market_flag():
    """Test I: Bid = 1.50, Ask = 1.20 -> CROSSED_MARKET quality flag attached."""
    service = AtlasOptionsService()
    quote = service.get_quote("opt_spy_20240621_p_80")

    assert quote.bid == 1.50
    assert quote.ask == 1.20
    assert QuoteQualityFlag.CROSSED_MARKET in quote.quality_flags


def test_fixture_j_stale_quote_flag():
    """Test J: Quote from prior session is marked with STALE_QUOTE quality flag."""
    service = AtlasOptionsService()
    quote = service.get_quote("opt_spy_20240621_p_90")

    assert QuoteQualityFlag.STALE_QUOTE in quote.quality_flags


def test_fixture_k_open_interest_reporting_date():
    """Test K: Open interest preserves its reporting date and is not claimed as intraday."""
    service = AtlasOptionsService()
    quote = service.get_quote("opt_spy_20240621_c_100")

    assert quote.open_interest == 45000
    assert quote.open_interest_as_of == "2024-05-19"


def test_fixture_l_missing_greeks_fidelity():
    """Test L: Quote without provider Greeks leaves Greeks as None; no fake zeros fabricated."""
    service = AtlasOptionsService()
    quote = service.get_quote("opt_spy_20240621_c_500")

    assert quote.bid == 8.20
    assert quote.ask == 8.60
    assert quote.volume == 6200
    # Crucial: Greeks must be None, NOT Delta=0.0!
    assert quote.greeks is None


def test_fixture_m_multi_expiration_calendar_exclusion():
    """Test M: Multi-expiration calendar spread is rejected from single-expiration payoff curve."""
    service = AtlasOptionsService()
    # Leg 1: June 2024 expiry, Leg 2: July 2024 expiry
    legs = [
        OptionStrategyLeg(contract_id="opt_aapl_20240621_c_180", side=LegSide.SHORT_CALL, quantity=1, entry_premium=4.0),
        OptionStrategyLeg(contract_id="opt_aapl_20240719_c_180", side=LegSide.LONG_CALL, quantity=1, entry_premium=6.5),
    ]

    with pytest.raises(OptionsMultiExpirationPayoffUnsupportedError) as exc_info:
        service.analyze_strategy(legs)
    assert "different expiration dates" in str(exc_info.value)
    assert "Stage 142" in str(exc_info.value)


def test_fixture_n_indian_lot_size_nifty():
    """Test N: Indian NSE option has lot size 50 and currency INR; amounts scale correctly by 50."""
    service = AtlasOptionsService()
    contract = service.get_contract("opt_nifty_20240627_c_22000")

    assert contract.contract_multiplier == 50.0  # Not 100!
    assert contract.strike_currency == "INR"
    assert contract.market_id == "NSE_DERIVATIVES"

    legs = [
        OptionStrategyLeg(
            contract_id="opt_nifty_20240627_c_22000",
            side=LegSide.LONG_CALL,
            quantity=1,
            entry_premium=180.0,
            multiplier=50.0,
        )
    ]
    res = service.analyze_strategy(legs, strategy_name="NIFTY Long Call", total_fees=0.0)

    # Net debit = 180.0 * 50 = INR -9,000
    assert res.net_opening_cash_flow == -9000.0
    assert res.breakevens == [22180.0]  # 22,000 + 180


def test_fixture_o_corporate_action_adjustment_record():
    """Test O: Corporate action reverse split is recorded with full deliverable history."""
    service = AtlasOptionsService()
    adjustments = service.contract_registry.adjustment_registry.list_adjustments_for_underlying("XYZ")

    assert len(adjustments) == 1
    adj = adjustments[0]
    assert adj.corporate_action_type == "STOCK_SPLIT"
    assert adj.adjusted_deliverable.shares_count == 150.0
    assert adj.adjusted_deliverable.cash_amount == 250.0


def test_fixture_p_private_portfolio_access_denied():
    """Test P: User B cannot access User A's private portfolio options positions."""
    service = AtlasOptionsService()
    unauthorized_principal = AuthPrincipal(sub="USER_B")

    with pytest.raises(OptionsTenantAccessDeniedError):
        service.get_portfolio_options("PORT_USER_A_FUND", principal=unauthorized_principal)

    # Authorized user succeeds
    authorized_principal = AuthPrincipal(sub="USER_A")
    positions = service.get_portfolio_options("PORT_USER_A_FUND", principal=authorized_principal)
    assert len(positions) == 1
    assert positions[0].underlying_symbol == "SPY"


def test_fixture_q_license_revocation_enforcement():
    """Test Q: Revoking source license denies quote access."""
    entitlements = OptionsEntitlementRegistry()
    service = AtlasOptionsService(entitlements=entitlements)

    # Access quote before revocation succeeds
    quote_before = service.get_quote("opt_spy_20240621_c_100")
    assert quote_before is not None

    # Revoke license
    entitlements.revoke_source("SRC_CBOE_AUTHORIZED")

    # Access quote after revocation raises entitlement error
    with pytest.raises(OptionsEntitlementRequiredError):
        service.get_quote("opt_spy_20240621_c_100")


def test_fixture_r_no_broker_action_on_strategy_analysis():
    """Test R: Strategy analysis performs analytical computation without broker order placement."""
    service = AtlasOptionsService()
    # 4-leg Iron Condor
    legs = [
        OptionStrategyLeg(contract_id="opt_spy_20240621_p_80", side=LegSide.LONG_PUT, quantity=1, entry_premium=1.2, multiplier=100.0),
        OptionStrategyLeg(contract_id="opt_spy_20240621_p_90", side=LegSide.SHORT_PUT, quantity=1, entry_premium=2.2, multiplier=100.0),
        OptionStrategyLeg(contract_id="opt_spy_20240621_c_110", side=LegSide.SHORT_CALL, quantity=1, entry_premium=3.0, multiplier=100.0),
        OptionStrategyLeg(contract_id="opt_spy_20240621_c_120", side=LegSide.LONG_CALL, quantity=1, entry_premium=1.5, multiplier=100.0),
    ]
    res = service.analyze_strategy(legs, strategy_name="Iron Condor", total_fees=0.0)

    assert res.strategy_name == "Iron Condor"
    assert len(res.legs) == 4
    # No broker execution performed; disclaimers attached
    assert "no_broker_trading" in res.disclaimers


# =============================================================================
# 3. FASTAPI REST ENDPOINTS
# =============================================================================

def test_api_options_capabilities():
    resp = client.get("/api/v1/options/capabilities")
    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == 141
    assert "US_OPTIONS" in data["supported_markets"]


def test_api_options_underlyings_search():
    resp = client.get("/api/v1/options/underlyings?query=SPY")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["symbol"] == "SPY"


def test_api_options_expirations():
    resp = client.get("/api/v1/options/underlyings/SPY/expirations")
    assert resp.status_code == 200
    data = resp.json()
    assert "2024-06-21" in data


def test_api_options_chain():
    resp = client.get("/api/v1/options/underlyings/SPY/chains?expiration_date=2024-06-21&underlying_price=105")
    assert resp.status_code == 200
    data = resp.json()
    assert data["underlying_symbol"] == "SPY"
    assert len(data["rows"]) > 0


def test_api_options_contract_get():
    resp = client.get("/api/v1/options/contracts/opt_spy_20240621_c_100")
    assert resp.status_code == 200
    data = resp.json()
    assert data["strike_price"] == 100.0
    assert data["option_type"] == "CALL"


def test_api_options_quote_get():
    resp = client.get("/api/v1/options/contracts/opt_spy_20240621_c_100/quote")
    assert resp.status_code == 200
    data = resp.json()
    assert data["bid"] == 4.90
    assert data["ask"] == 5.10


def test_api_options_strategy_analyze_post():
    payload = {
        "strategy_name": "Bull Call Spread",
        "legs": [
            {"contract_id": "opt_spy_20240621_c_100", "side": "LONG_CALL", "quantity": 1, "entry_premium": 8.0, "multiplier": 100.0},
            {"contract_id": "opt_spy_20240621_c_110", "side": "SHORT_CALL", "quantity": 1, "entry_premium": 3.0, "multiplier": 100.0},
        ],
        "total_fees": 0.0,
    }
    resp = client.post("/api/v1/options/strategies/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["net_opening_cash_flow"] == -500.0
    assert data["breakevens"] == [105.0]
    assert data["max_profit"] == 500.0
    assert data["max_loss"] == 500.0


def test_api_options_volatility_get():
    resp = client.get("/api/v1/options/underlyings/SPY/volatility?expiration_date=2024-06-21")
    assert resp.status_code == 200
    data = resp.json()
    assert "calls_smile" in data
    assert "puts_smile" in data


def test_api_options_activity_get():
    resp = client.get("/api/v1/options/underlyings/SPY/activity?expiration_date=2024-06-21")
    assert resp.status_code == 200
    data = resp.json()
    assert "strikes" in data
    assert data["total_call_volume"] > 0

