"""Expiration Payoff Calculation Engine (Stage 141).

Exact mathematical formulation for standard vanilla option strategies at expiration cutoff:
- Long Call:  Q * M * (max(S_T - K, 0) - P)
- Short Call: Q * M * (P - max(S_T - K, 0))
- Long Put:   Q * M * (max(K - S_T, 0) - P)
- Short Put:  Q * M * (P - max(K - S_T, 0))
"""

from __future__ import annotations

import math
from typing import List, Tuple
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import (
    LegSide,
    OptionStrategyLeg,
    PayoffCoordinate,
)


def calculate_leg_expiration_payoff(
    leg: OptionStrategyLeg,
    strike_price: float,
    underlying_settlement_price: float,
) -> float:
    """Calculate single leg P&L at expiration settlement price."""
    s_t = underlying_settlement_price
    k = strike_price
    q = leg.quantity
    m = leg.multiplier
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
    legs: List[OptionStrategyLeg],
    contract_registry: OptionContractRegistry,
    underlying_settlement_price: float,
    total_fees: float = 0.0,
) -> float:
    """Calculate total multi-leg strategy expiration P&L at settlement price S_T."""
    total_payoff = 0.0
    for leg in legs:
        contract = contract_registry.get_contract(leg.contract_id)
        if not contract:
            continue
        leg_pnl = calculate_leg_expiration_payoff(leg, contract.strike_price, underlying_settlement_price)
        total_payoff += leg_pnl

    return round(total_payoff - total_fees, 2)


def generate_payoff_curve(
    legs: List[OptionStrategyLeg],
    contract_registry: OptionContractRegistry,
    breakevens: List[float],
    total_fees: float = 0.0,
    steps: int = 100,
) -> List[PayoffCoordinate]:
    """Generate high-fidelity expiration payoff curve across underlying settlement prices."""
    strikes = []
    for leg in legs:
        c = contract_registry.get_contract(leg.contract_id)
        if c:
            strikes.append(c.strike_price)

    if not strikes:
        return []

    min_s = min(strikes)
    max_s = max(strikes)

    # Wide coverage: at least +/- 30% or +/- 30 points beyond the min/max strike
    span = max(max_s - min_s, min_s * 0.4, 30.0)
    p_start = max(0.0, round(min_s - span, 1))
    p_end = round(max_s + span, 1)

    # Include grid points plus all strikes, breakevens, and integer key checkpoints
    critical_points = set(strikes + breakevens)

    sample_prices = set()
    step_size = max(0.5, (p_end - p_start) / float(steps))
    curr = p_start
    while curr <= p_end + 1e-6:
        sample_prices.add(round(curr, 2))
        curr += step_size

    # Ensure integer milestones (like 80.0, 120.0, etc.) are present
    int_curr = int(math.ceil(p_start))
    int_end = int(math.floor(p_end))
    for ip in range(int_curr, int_end + 1):
        sample_prices.add(float(ip))

    all_prices = sorted(list(sample_prices.union({round(p, 2) for p in critical_points if p_start <= p <= p_end})))

    coordinates: List[PayoffCoordinate] = []
    for p in all_prices:
        val = calculate_strategy_expiration_payoff(legs, contract_registry, p, total_fees)
        is_be = any(abs(p - be) < 0.05 for be in breakevens)
        coordinates.append(PayoffCoordinate(underlying_price=p, payoff=val, is_breakeven=is_be))

    return coordinates
