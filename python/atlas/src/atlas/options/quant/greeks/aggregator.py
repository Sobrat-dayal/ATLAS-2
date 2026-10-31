"""Aggregate Strategy Greeks Engine (Stage 142)."""

from __future__ import annotations

from typing import List, Tuple
from atlas.options.domain import LegSide
from atlas.options.quant.domain import QuantModelGreeks, QuantStrategyLeg


def aggregate_strategy_greeks(
    legs: List[QuantStrategyLeg],
    leg_greeks: List[QuantModelGreeks],
    include_multipliers: bool = True,
) -> QuantModelGreeks:
    """Aggregate per-contract sensitivities into position/strategy-level Greeks.

    Formula: Sum( PositionSign * Quantity * Multiplier * PerContractGreek )
    """
    total_delta = 0.0
    total_gamma = 0.0
    total_theta_day = 0.0
    total_theta_annual = 0.0
    total_vega_point = 0.0
    total_vega_unit = 0.0
    total_rho_point = 0.0
    total_rho_bp = 0.0
    total_vanna = 0.0
    total_volga = 0.0

    for leg, g in zip(legs, leg_greeks):
        sign = 1.0 if leg.side in (LegSide.LONG_CALL, LegSide.LONG_PUT) else -1.0
        scale = float(leg.quantity)
        if include_multipliers:
            scale *= float(leg.multiplier)

        total_delta += sign * scale * g.delta
        total_gamma += sign * scale * g.gamma
        total_theta_day += sign * scale * g.theta_per_day
        total_theta_annual += sign * scale * g.theta_annual
        total_vega_point += sign * scale * g.vega_per_point
        total_vega_unit += sign * scale * g.vega_per_unit
        total_rho_point += sign * scale * g.rho_per_point
        total_rho_bp += sign * scale * g.rho_per_bp

        if g.vanna is not None:
            total_vanna += sign * scale * g.vanna
        if g.volga is not None:
            total_volga += sign * scale * g.volga

    return QuantModelGreeks(
        delta=round(total_delta, 4),
        gamma=round(total_gamma, 5),
        theta_per_day=round(total_theta_day, 4),
        theta_annual=round(total_theta_annual, 3),
        vega_per_point=round(total_vega_point, 4),
        vega_per_unit=round(total_vega_unit, 3),
        rho_per_point=round(total_rho_point, 4),
        rho_per_bp=round(total_rho_bp, 5),
        vanna=round(total_vanna, 5),
        volga=round(total_volga, 5),
        calculation_method="STRATEGY_PORTFOLIO_AGGREGATE",
    )
