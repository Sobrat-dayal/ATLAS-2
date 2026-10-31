"""Analytical Breakeven, Maximum Profit and Maximum Loss Engine (Stage 141).

Exact root finding across piecewise linear option payoff segments.
Accurately detects unbounded upside loss for short call positions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import LegSide, OptionStrategyLeg
from atlas.options.strategies.payoff import calculate_strategy_expiration_payoff


def calculate_strategy_breakevens_and_bounds(
    legs: List[OptionStrategyLeg],
    contract_registry: OptionContractRegistry,
    total_fees: float = 0.0,
) -> Dict[str, Any]:
    """Calculate exact mathematical breakeven prices, max profit, max loss, and unbounded risk flags."""
    if not legs:
        return {
            "breakevens": [],
            "max_profit": 0.0,
            "max_loss": 0.0,
            "is_unbounded_profit": False,
            "is_unbounded_loss": False,
        }

    # Extract strikes and multipliers
    strike_info = []
    for leg in legs:
        c = contract_registry.get_contract(leg.contract_id)
        if c:
            strike_info.append((c.strike_price, leg))

    if not strike_info:
        return {
            "breakevens": [],
            "max_profit": 0.0,
            "max_loss": 0.0,
            "is_unbounded_profit": False,
            "is_unbounded_loss": False,
        }

    strikes = sorted(list(set(s for s, _ in strike_info)))

    # Compute asymptotic slopes:
    # As S_T -> infinity, Call intrinsic = (S_T - K), Put intrinsic = 0.
    # Long call contributes +Q * M slope; Short call contributes -Q * M slope.
    inf_slope = 0.0
    zero_slope = 0.0  # As S_T -> 0, Put intrinsic = (K - S_T) -> slope is -1. Long put: -Q*M slope; Short put: +Q*M slope.

    for s, leg in strike_info:
        qm = leg.quantity * leg.multiplier
        if leg.side == LegSide.LONG_CALL:
            inf_slope += qm
        elif leg.side == LegSide.SHORT_CALL:
            inf_slope -= qm
        elif leg.side == LegSide.LONG_PUT:
            zero_slope -= qm
        elif leg.side == LegSide.SHORT_PUT:
            zero_slope += qm

    is_unbounded_profit = inf_slope > 0.0
    # Naked short call has inf_slope < 0.0 => Unbounded loss! (Fixture F)
    is_unbounded_loss = inf_slope < 0.0

    # Test knot points (strikes + 0)
    test_points = sorted(list(set([0.0] + strikes)))
    knot_payoffs = [
        (p, calculate_strategy_expiration_payoff(legs, contract_registry, p, total_fees))
        for p in test_points
    ]

    # Find roots between adjacent knot points:
    breakevens: List[float] = []

    for i in range(len(knot_payoffs) - 1):
        p1, val1 = knot_payoffs[i]
        p2, val2 = knot_payoffs[i + 1]

        if abs(val1) < 1e-4:
            if not any(abs(p1 - be) < 0.01 for be in breakevens):
                breakevens.append(round(p1, 2))
        elif abs(val2) < 1e-4:
            if not any(abs(p2 - be) < 0.01 for be in breakevens):
                breakevens.append(round(p2, 2))
        elif (val1 < 0 and val2 > 0) or (val1 > 0 and val2 < 0):
            # Exact linear interpolation root: val(p) = val1 + (val2 - val1) * (p - p1)/(p2 - p1) = 0
            root = p1 - val1 * (p2 - p1) / (val2 - val1)
            breakevens.append(round(root, 2))

    # Check root beyond the largest strike (if inf_slope != 0)
    last_strike, last_val = knot_payoffs[-1]
    if abs(inf_slope) > 0.0:
        # Payoff for S >= last_strike: P(S) = last_val + inf_slope * (S - last_strike) = 0
        root_high = last_strike - (last_val / inf_slope)
        if root_high > last_strike:
            breakevens.append(round(root_high, 2))

    breakevens = sorted(list(set(breakevens)))

    # Compute Max Profit & Max Loss:
    # Sample extreme points if bounded
    extreme_high = strikes[-1] * 2.0
    extreme_val_high = calculate_strategy_expiration_payoff(legs, contract_registry, extreme_high, total_fees)
    all_sample_vals = [val for _, val in knot_payoffs] + [extreme_val_high]

    if is_unbounded_profit:
        max_profit = None
    else:
        max_profit = round(max(all_sample_vals), 2)

    if is_unbounded_loss:
        max_loss = None  # Crucial for naked short calls! (Fixture F)
    else:
        min_finite_val = min(all_sample_vals)
        # Loss is conventionally expressed as positive dollar amount or signed; we report positive maximum loss amount
        max_loss = round(abs(min_finite_val) if min_finite_val < 0.0 else 0.0, 2)

    return {
        "breakevens": breakevens,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "is_unbounded_profit": is_unbounded_profit,
        "is_unbounded_loss": is_unbounded_loss,
    }
