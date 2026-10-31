"""Expiration Payoff Engine for Quant Strategies (Stage 142)."""

from __future__ import annotations

import math
from typing import List, Set
from atlas.options.domain import LegSide, PayoffCoordinate
from atlas.options.quant.domain import QuantStrategyLeg


def calculate_leg_expiration_payoff(
    leg: QuantStrategyLeg,
    underlying_settlement_price: float,
) -> float:
    """Calculate single leg intrinsic P&L at expiration settlement price."""
    s_t = underlying_settlement_price
    k = leg.strike_price
    q = float(leg.quantity)
    m = float(leg.multiplier)
    p = leg.entry_premium

    if leg.side == LegSide.LONG_CALL:
        intrinsic = max(0.0, s_t - k)
        return q * m * (intrinsic - p)

    elif leg.side == LegSide.SHORT_CALL:
        intrinsic = max(0.0, s_t - k)
        return q * m * (p - intrinsic)

    elif leg.side == LegSide.LONG_PUT:
        intrinsic = max(0.0, k - s_t)
        return q * m * (intrinsic - p)

    elif leg.side == LegSide.SHORT_PUT:
        intrinsic = max(0.0, k - s_t)
        return q * m * (p - intrinsic)

    return 0.0


def calculate_strategy_expiration_payoff(
    legs: List[QuantStrategyLeg],
    underlying_settlement_price: float,
    total_fees: float = 0.0,
) -> float:
    """Calculate aggregate strategy expiration P&L at settlement price S_T."""
    total_pnl = sum(calculate_leg_expiration_payoff(leg, underlying_settlement_price) for leg in legs)
    total_pnl -= total_fees
    return round(total_pnl, 2)


def generate_expiration_payoff_curve(
    legs: List[QuantStrategyLeg],
    breakevens: List[float],
    total_fees: float = 0.0,
    steps: int = 100,
) -> List[PayoffCoordinate]:
    """Generate high-fidelity expiration payoff curve over underlying settlement prices."""
    if not legs:
        return []

    strikes = [leg.strike_price for leg in legs]
    min_s = min(strikes)
    max_s = max(strikes)

    span = max(max_s - min_s, min_s * 0.4, 30.0)
    p_start = max(0.0, round(min_s - span, 1))
    p_end = round(max_s + span, 1)

    critical_points = set(strikes + breakevens)

    sample_prices: Set[float] = set()
    step_size = max(0.5, (p_end - p_start) / float(steps))
    curr = p_start
    while curr <= p_end + 1e-6:
        sample_prices.add(round(curr, 2))
        curr += step_size

    # Ensure integer milestones
    int_curr = int(math.ceil(p_start))
    int_end = int(math.floor(p_end))
    for ip in range(int_curr, int_end + 1):
        sample_prices.add(float(ip))

    all_prices = sorted(list(sample_prices.union({round(p, 2) for p in critical_points if p_start <= p <= p_end})))

    coordinates: List[PayoffCoordinate] = []
    for p in all_prices:
        val = calculate_strategy_expiration_payoff(legs, p, total_fees)
        is_be = any(abs(p - be) < 0.05 for be in breakevens)
        coordinates.append(PayoffCoordinate(underlying_price=p, payoff=val, is_breakeven=is_be))

    return coordinates
