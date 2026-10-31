"""Scenario Revaluation Engine and Matrix Generator (Stage 142)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import QuantLib as ql

from atlas.options.quant.domain import PricingModelFamily, QuantStrategyLeg
from atlas.options.quant.quantlib.dates import from_ql_date, to_ql_date
from atlas.options.quant.strategies.valuation import value_strategy_mark_to_market


@dataclass
class ScenarioOutcome:
    """Hypothetical valuation outcome for a specific scenario parameter combination."""

    spot_price: float
    spot_shock_pct: float
    volatility: float
    vol_shock_pct: float
    evaluation_date: str
    days_forward: int
    risk_free_rate: float
    strategy_market_value: float
    conditional_pnl: float
    net_delta: float
    net_gamma: float
    net_vega: float
    net_theta: float


@dataclass
class ScenarioMatrixCell:
    """Single cell in a 2D scenario heatmap grid."""

    row_param: float
    col_param: float
    conditional_pnl: float
    strategy_market_value: float


@dataclass
class ScenarioMatrixResult:
    """Complete 2D scenario matrix output."""

    row_dimension: str   # e.g. "SPOT"
    col_dimension: str   # e.g. "VOLATILITY" or "TIME"
    row_values: List[float]
    col_values: List[float]
    cells: List[List[ScenarioMatrixCell]]


class ScenarioEngine:
    """Deterministic scenario execution engine performing full model revaluations."""

    @classmethod
    def run_multi_factor_scenario(
        cls,
        legs: List[QuantStrategyLeg],
        base_spot: float,
        base_eval_date: str,
        spot_shock_pct: float = 0.0,
        vol_shock_points: float = 0.0,
        days_forward: int = 0,
        rate_shift_bps: float = 0.0,
        base_vol: float = 0.20,
        base_rate: float = 0.05,
        dividend_yield: float = 0.0,
        net_opening_cash_flow: float = 0.0,
        total_fees: float = 0.0,
        model_family: PricingModelFamily = PricingModelFamily.BLACK_SCHOLES_MERTON,
    ) -> ScenarioOutcome:
        """Execute a single multi-factor deterministic scenario."""
        # 1. Transform spot price
        shocked_spot = round(base_spot * (1.0 + spot_shock_pct / 100.0), 2)

        # 2. Transform volatility
        shocked_vol = max(0.01, round(base_vol + vol_shock_points / 100.0, 4))

        # 3. Transform evaluation date
        ql_base = to_ql_date(base_eval_date)
        ql_forward = ql_base + days_forward
        shocked_date = from_ql_date(ql_forward)

        # 4. Transform interest rate
        shocked_rate = max(0.0, round(base_rate + rate_shift_bps / 10000.0, 5))

        # 5. Full mark-to-market revaluation
        mv, pnl, greeks = value_strategy_mark_to_market(
            legs=legs,
            spot_price=shocked_spot,
            evaluation_date=shocked_date,
            risk_free_rate=shocked_rate,
            dividend_yield=dividend_yield,
            volatility=shocked_vol,
            model_family=model_family,
            net_opening_cash_flow=net_opening_cash_flow,
            total_fees=total_fees,
        )

        return ScenarioOutcome(
            spot_price=shocked_spot,
            spot_shock_pct=spot_shock_pct,
            volatility=shocked_vol,
            vol_shock_pct=vol_shock_points,
            evaluation_date=shocked_date,
            days_forward=days_forward,
            risk_free_rate=shocked_rate,
            strategy_market_value=mv,
            conditional_pnl=pnl,
            net_delta=greeks.delta,
            net_gamma=greeks.gamma,
            net_vega=greeks.vega_per_point,
            net_theta=greeks.theta_per_day,
        )

    @classmethod
    def generate_spot_vol_matrix(
        cls,
        legs: List[QuantStrategyLeg],
        base_spot: float,
        base_eval_date: str,
        base_vol: float = 0.20,
        base_rate: float = 0.05,
        dividend_yield: float = 0.0,
        net_opening_cash_flow: float = 0.0,
        total_fees: float = 0.0,
        spot_pct_steps: Optional[List[float]] = None,
        vol_point_steps: Optional[List[float]] = None,
        model_family: PricingModelFamily = PricingModelFamily.BLACK_SCHOLES_MERTON,
    ) -> ScenarioMatrixResult:
        """Generate 2D Spot Price Shock vs Implied Volatility Shift scenario heatmap."""
        spots = spot_pct_steps or [-10.0, -5.0, 0.0, 5.0, 10.0]
        vols = vol_point_steps or [-5.0, -2.5, 0.0, 2.5, 5.0]

        cells: List[List[ScenarioMatrixCell]] = []

        for s_pct in spots:
            row: List[ScenarioMatrixCell] = []
            for v_pts in vols:
                outcome = cls.run_multi_factor_scenario(
                    legs=legs,
                    base_spot=base_spot,
                    base_eval_date=base_eval_date,
                    spot_shock_pct=s_pct,
                    vol_shock_points=v_pts,
                    days_forward=0,
                    rate_shift_bps=0.0,
                    base_vol=base_vol,
                    base_rate=base_rate,
                    dividend_yield=dividend_yield,
                    net_opening_cash_flow=net_opening_cash_flow,
                    total_fees=total_fees,
                    model_family=model_family,
                )
                row.append(
                    ScenarioMatrixCell(
                        row_param=s_pct,
                        col_param=v_pts,
                        conditional_pnl=outcome.conditional_pnl,
                        strategy_market_value=outcome.strategy_market_value,
                    )
                )
            cells.append(row)

        return ScenarioMatrixResult(
            row_dimension="SPOT_SHOCK_PCT",
            col_dimension="VOL_SHOCK_POINTS",
            row_values=spots,
            col_values=vols,
            cells=cells,
        )
