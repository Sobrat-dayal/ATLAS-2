"""Strategy Comparison Engine (Stage 142)."""

from __future__ import annotations

from typing import List
from atlas.options.quant.domain import StrategyComparisonItem
from atlas.options.quant.strategies.models import StrategyValuationResult


def compare_strategies(
    results: List[StrategyValuationResult],
) -> List[StrategyComparisonItem]:
    """Produce standardized side-by-side strategy comparison records."""
    comparison: List[StrategyComparisonItem] = []

    for r in results:
        comparison.append(
            StrategyComparisonItem(
                strategy_id=f"strat_{r.strategy_name.lower().replace(' ', '_')}",
                strategy_name=r.strategy_name,
                net_opening_cash_flow=r.net_opening_cash_flow,
                is_net_debit=r.is_net_debit,
                max_profit=r.max_profit,
                max_loss=r.max_loss,
                is_unbounded_loss=r.is_unbounded_loss,
                breakevens=r.breakevens,
                net_delta=r.aggregate_greeks.delta,
                net_gamma=r.aggregate_greeks.gamma,
                net_theta_per_day=r.aggregate_greeks.theta_per_day,
                net_vega_per_point=r.aggregate_greeks.vega_per_point,
                legs_count=len(r.legs),
                underlying_symbol=r.underlying_symbol,
            )
        )

    return comparison

