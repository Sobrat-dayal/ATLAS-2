"""Numerical Finite-Difference Sensitivities Engine (Stage 142)."""

from __future__ import annotations

from typing import Callable, Tuple
import QuantLib as ql
from atlas.options.quant.domain import QuantModelGreeks
from atlas.options.quant.greeks.conventions import (
    rho_unit_to_bp,
    rho_unit_to_point,
    theta_annual_to_per_day,
    vega_unit_to_point,
)


def compute_numerical_greeks(
    pricing_fn: Callable[[float, float, float, ql.Date], float],
    spot: float,
    vol: float,
    rate: float,
    eval_date: ql.Date,
) -> QuantModelGreeks:
    """Compute complete suite of Greeks via high-accuracy central finite differences.

    pricing_fn signature: pricing_fn(spot, vol, rate, eval_date) -> float (NPV)
    """
    base_val = pricing_fn(spot, vol, rate, eval_date)

    # 1. Delta & Gamma bumps (spot)
    h_s = max(spot * 0.005, 0.01)
    val_s_up = pricing_fn(spot + h_s, vol, rate, eval_date)
    val_s_down = pricing_fn(max(0.01, spot - h_s), vol, rate, eval_date)

    delta = (val_s_up - val_s_down) / (2.0 * h_s)
    gamma = (val_s_up - 2.0 * base_val + val_s_down) / (h_s * h_s)

    # 2. Vega bumps (volatility)
    h_v = 0.005  # 0.5% volatility bump
    val_v_up = pricing_fn(spot, vol + h_v, rate, eval_date)
    val_v_down = pricing_fn(spot, max(0.001, vol - h_v), rate, eval_date)

    vega_unscaled = (val_v_up - val_v_down) / (2.0 * h_v)
    vega_per_point = vega_unit_to_point(vega_unscaled)

    # Volga (vomma): d^2 V / d sigma^2
    volga_raw = (val_v_up - 2.0 * base_val + val_v_down) / (h_v * h_v)
    volga = volga_raw / 100.0

    # 3. Theta (time forward 1 day)
    next_day = eval_date + 1
    val_t_up = pricing_fn(spot, vol, rate, next_day)
    # Theta represents decay over time, so standard market convention is V(t+1) - V(t)
    theta_per_day = val_t_up - base_val
    theta_annual = theta_per_day * 365.0

    # 4. Rho (interest rate)
    h_r = 0.0005  # 5 bps
    val_r_up = pricing_fn(spot, vol, rate + h_r, eval_date)
    val_r_down = pricing_fn(spot, vol, max(0.0, rate - h_r), eval_date)

    rho_unscaled = (val_r_up - val_r_down) / (2.0 * h_r)
    rho_per_point = rho_unit_to_point(rho_unscaled)
    rho_per_bp = rho_unit_to_bp(rho_unscaled)

    # 5. Vanna: d^2 V / (d S d sigma)
    val_s_up_v_up = pricing_fn(spot + h_s, vol + h_v, rate, eval_date)
    val_s_down_v_up = pricing_fn(max(0.01, spot - h_s), vol + h_v, rate, eval_date)
    val_s_up_v_down = pricing_fn(spot + h_s, max(0.001, vol - h_v), rate, eval_date)
    val_s_down_v_down = pricing_fn(max(0.01, spot - h_s), max(0.001, vol - h_v), rate, eval_date)

    vanna_raw = (val_s_up_v_up - val_s_down_v_up - val_s_up_v_down + val_s_down_v_down) / (4.0 * h_s * h_v)
    vanna = vanna_raw / 100.0

    return QuantModelGreeks(
        delta=round(delta, 5),
        gamma=round(gamma, 6),
        theta_per_day=round(theta_per_day, 5),
        theta_annual=round(theta_annual, 4),
        vega_per_point=round(vega_per_point, 5),
        vega_per_unit=round(vega_unscaled, 4),
        rho_per_point=round(rho_per_point, 5),
        rho_per_bp=round(rho_per_bp, 6),
        vanna=round(vanna, 6),
        volga=round(volga, 6),
        calculation_method="NUMERICAL_FINITE_DIFFERENCE",
        bump_size_used=h_s,
    )
