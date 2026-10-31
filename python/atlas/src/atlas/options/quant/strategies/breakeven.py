"""Analytical Breakeven and Payoff Bounds Engine (Stage 142)."""

from __future__ import annotations

from typing import List, Optional, Tuple
from atlas.options.domain import LegSide
from atlas.options.quant.domain import QuantStrategyLeg
from atlas.options.quant.strategies.payoff import calculate_strategy_expiration_payoff


def calculate_breakevens_and_bounds(
    legs: List[QuantStrategyLeg],
    total_fees: float = 0.0,
) -> Tuple[List[float], Optional[float], Optional[float], bool, bool]:
    """Calculate analytical breakevens, max profit, max loss, and unbounded flags.

    Returns:
        (breakevens, max_profit, max_loss, is_unbounded_profit, is_unbounded_loss)
    """
    if not legs:
        return [], 0.0, 0.0, False, False

    strikes = sorted(list({leg.strike_price for leg in legs}))
    min_k = strikes[0]
    max_k = strikes[-1]

    # Evaluate slopes at extremes to test for unbounded upside and downside
    far_below = max(0.0, min_k - 100.0)
    far_above = max_k + 200.0

    pnl_below1 = calculate_strategy_expiration_payoff(legs, far_below, total_fees)
    pnl_below2 = calculate_strategy_expiration_payoff(legs, far_below + 10.0, total_fees)
    slope_down = (pnl_below2 - pnl_below1) / 10.0

    pnl_above1 = calculate_strategy_expiration_payoff(legs, far_above, total_fees)
    pnl_above2 = calculate_strategy_expiration_payoff(legs, far_above + 10.0, total_fees)
    slope_up = (pnl_above2 - pnl_above1) / 10.0

    is_unbounded_profit = slope_up > 0.01
    # Check for naked short calls where slope_up < -0.01 (unbounded loss on rally)
    is_unbounded_loss = slope_up < -0.01

    # Check for naked short puts or slope_down
    # Standalone short puts have finite max loss at S_T = 0.0 under standard nonnegative underlying prices.
    # But uncovered short calls rise without upper bound.
    has_naked_short_call = any(leg.side == LegSide.SHORT_CALL for leg in legs) and not any(
        leg.side == LegSide.LONG_CALL for leg in legs
    )
    if has_naked_short_call:
        is_unbounded_loss = True

    # Knot points for piecewise linear function
    knot_points = sorted(list(set([0.0] + strikes + [max_k + 100.0])))

    # Sample intermediate test points
    test_points = list(knot_points)
    for i in range(len(knot_points) - 1):
        mid = (knot_points[i] + knot_points[i + 1]) / 2.0
        test_points.append(mid)

    # 1. Root finding (Breakevens)
    breakevens: List[float] = []
    # Check each linear segment [x_i, x_{i+1}]
    for i in range(len(knot_points) - 1):
        x1 = knot_points[i]
        x2 = knot_points[i + 1]
        y1 = calculate_strategy_expiration_payoff(legs, x1, total_fees)
        y2 = calculate_strategy_expiration_payoff(legs, x2, total_fees)

        if abs(y1) < 1e-4:
            if not any(abs(x1 - b) < 0.05 for b in breakevens):
                breakevens.append(round(x1, 2))
        elif abs(y2) < 1e-4:
            if not any(abs(x2 - b) < 0.05 for b in breakevens):
                breakevens.append(round(x2, 2))
        elif (y1 < 0 and y2 > 0) or (y1 > 0 and y2 < 0):
            # Exact linear root
            slope = (y2 - y1) / (x2 - x1)
            root = x1 - (y1 / slope)
            if not any(abs(root - b) < 0.05 for b in breakevens):
                breakevens.append(round(root, 2))

    # Also check beyond max_k if slope_up != 0
    if abs(slope_up) > 1e-4:
        y_maxk = calculate_strategy_expiration_payoff(legs, max_k, total_fees)
        root_beyond = max_k - (y_maxk / slope_up)
        if root_beyond > max_k and not any(abs(root_beyond - b) < 0.05 for b in breakevens):
            breakevens.append(round(root_beyond, 2))

    breakevens.sort()

    # 2. Max profit and Max loss evaluation across finite domain
    sample_eval_prices = [0.0] + strikes + [max(0.0, min_k - 20.0), max_k + 20.0]
    pnl_samples = [calculate_strategy_expiration_payoff(legs, p, total_fees) for p in sample_eval_prices]

    max_pnl_sample = max(pnl_samples)
    min_pnl_sample = min(pnl_samples)

    max_profit: Optional[float] = None if is_unbounded_profit else round(max_pnl_sample, 2)
    max_loss: Optional[float] = None if is_unbounded_loss else round(abs(min(0.0, min_pnl_sample)), 2)

    return breakevens, max_profit, max_loss, is_unbounded_profit, is_unbounded_loss

