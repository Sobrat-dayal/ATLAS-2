"""Pre-Expiration Mark-to-Market Strategy Valuation Engine (Stage 142).

Enables true multi-model valuation at intermediate dates t < T, allowing:
- Multi-expiration Calendar Spreads and Diagonal Spreads (Test K).
- T+0 pre-expiration curves overlaid against expiration payoff diagrams.
- Real-time mark-to-market Greek tracking across underlying prices.
"""

from __future__ import annotations

import math
from typing import List, Tuple
from atlas.options.domain import LegSide, OptionType
from atlas.options.quant.domain import (
    PreExpirationValuationPoint,
    PricingModelFamily,
    QuantModelGreeks,
    QuantStrategyLeg,
)
from atlas.options.quant.greeks.aggregator import aggregate_strategy_greeks
from atlas.options.quant.quantlib.adapter import QuantLibAdapter


def value_strategy_mark_to_market(
    legs: List[QuantStrategyLeg],
    spot_price: float,
    evaluation_date: str,
    risk_free_rate: float = 0.05,
    dividend_yield: float = 0.0,
    volatility: float = 0.20,
    model_family: PricingModelFamily = PricingModelFamily.BLACK_SCHOLES_MERTON,
    net_opening_cash_flow: float = 0.0,
    total_fees: float = 0.0,
) -> Tuple[float, float, QuantModelGreeks]:
    """Calculate strategy mark-to-market market value, P&L, and aggregate Greeks at date t.

    Returns:
        (strategy_market_value, strategy_unrealized_pnl, aggregate_greeks)
    """
    total_mv = 0.0
    leg_greeks: List[QuantModelGreeks] = []

    for leg in legs:
        # Determine appropriate model family for leg exercise style
        leg_model = model_family
        if leg.exercise_style.value == "AMERICAN" and model_family == PricingModelFamily.BLACK_SCHOLES_MERTON:
            leg_model = PricingModelFamily.BARONE_ADESI_WHALEY

        theo_p, g, _ = QuantLibAdapter.price_vanilla_contract(
            option_type=leg.option_type,
            strike_price=leg.strike_price,
            expiration_date=leg.expiration_date,
            evaluation_date=evaluation_date,
            spot_price=spot_price,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=volatility,
            exercise_style=leg.exercise_style,
            model_family=leg_model,
        )

        sign = 1.0 if leg.side in (LegSide.LONG_CALL, LegSide.LONG_PUT) else -1.0
        leg_mv = sign * float(leg.quantity) * float(leg.multiplier) * theo_p
        total_mv += leg_mv
        leg_greeks.append(g)

    # Strategy aggregate Greeks
    agg_greeks = aggregate_strategy_greeks(legs, leg_greeks, include_multipliers=True)

    # Strategy P&L = Current Market Value + Opening Cash Flow - Fees
    # (Opening cash flow is negative for net debit paid, positive for net credit received)
    pnl = total_mv + net_opening_cash_flow - total_fees

    return round(total_mv, 2), round(pnl, 2), agg_greeks


def generate_pre_expiration_curve(
    legs: List[QuantStrategyLeg],
    evaluation_date: str,
    net_opening_cash_flow: float,
    total_fees: float = 0.0,
    risk_free_rate: float = 0.05,
    dividend_yield: float = 0.0,
    volatility: float = 0.20,
    model_family: PricingModelFamily = PricingModelFamily.BLACK_SCHOLES_MERTON,
    steps: int = 50,
) -> List[PreExpirationValuationPoint]:
    """Generate pre-expiration mark-to-market curve across underlying prices."""
    if not legs:
        return []

    strikes = [leg.strike_price for leg in legs]
    min_s = min(strikes)
    max_s = max(strikes)

    span = max(max_s - min_s, min_s * 0.4, 30.0)
    p_start = max(0.01, round(min_s - span, 1))
    p_end = round(max_s + span, 1)

    step_size = max(0.5, (p_end - p_start) / float(steps))

    curve: List[PreExpirationValuationPoint] = []
    curr = p_start
    while curr <= p_end + 1e-6:
        s_price = round(curr, 2)
        mv, pnl, g = value_strategy_mark_to_market(
            legs=legs,
            spot_price=s_price,
            evaluation_date=evaluation_date,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=volatility,
            model_family=model_family,
            net_opening_cash_flow=net_opening_cash_flow,
            total_fees=total_fees,
        )

        curve.append(
            PreExpirationValuationPoint(
                underlying_price=s_price,
                strategy_mark_to_market=mv,
                pnl_versus_opening=pnl,
                aggregate_delta=g.delta,
                aggregate_gamma=g.gamma,
                aggregate_vega=g.vega_per_point,
                aggregate_theta=g.theta_per_day,
            )
        )
        curr += step_size

    return curve
