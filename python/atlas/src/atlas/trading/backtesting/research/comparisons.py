"""Multi-Strategy Comparative Analytics (Stage 143)."""

from __future__ import annotations

from typing import Any, Dict, List
from atlas.trading.backtesting.domain import AtlasBacktestResult


def compare_backtest_runs(
    runs: List[AtlasBacktestResult],
) -> List[Dict[str, Any]]:
    """Compare multiple completed backtest runs across standardized risk/return metrics."""
    comparison: List[Dict[str, Any]] = []

    for r in runs:
        comparison.append({
            "run_id": r.run_id,
            "strategy_id": r.config.strategy_id,
            "strategy_version": r.config.strategy_version,
            "dataset_id": r.config.dataset_id,
            "initial_cash": r.config.initial_cash,
            "final_equity": r.equity_curve[-1].equity if r.equity_curve else r.config.initial_cash,
            "total_return_pct": r.performance.total_return_pct,
            "cagr_pct": r.performance.cagr_pct,
            "max_drawdown_pct": r.performance.drawdown.max_drawdown_pct,
            "sharpe_ratio": r.performance.sharpe_ratio,
            "sortino_ratio": r.performance.sortino_ratio,
            "profit_factor": r.performance.profit_factor,
            "win_rate_pct": r.performance.win_rate_pct,
            "expectancy_dollar": r.performance.expectancy_dollar,
            "total_trades": r.performance.total_trades_count,
            "commissions_paid": r.performance.total_commissions_paid,
            "slippage_cost": r.performance.total_slippage_cost,
            "execution_time_seconds": r.execution_time_seconds,
        })

    return comparison
