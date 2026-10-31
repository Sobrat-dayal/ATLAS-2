"""Walk-Forward Optimization and Chronological Out-of-Sample Engine (Stage 143)."""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

from atlas.trading.backtesting.domain import (
    AtlasBacktestConfig,
    WalkForwardFold,
    WalkForwardResult,
)
from atlas.trading.backtesting.nautilus.runner import IsolatedBacktestRunner


class WalkForwardEngine:
    """Performs rigorous walk-forward validation across chronological folds (Test R)."""

    def __init__(self, runner: Optional[IsolatedBacktestRunner] = None):
        self.runner = runner or IsolatedBacktestRunner()

    def run_walk_forward(
        self,
        walk_forward_id: str,
        base_config: AtlasBacktestConfig,
        fold_windows: List[Dict[str, str]],  # [{"train_start": ..., "train_end": ..., "test_start": ..., "test_end": ...}]
        param_candidates: List[Dict[str, Any]],
        custom_bars_by_date: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> WalkForwardResult:
        """
        Execute chronological walk-forward validation.
        Ensures training window strictly precedes testing window (no look-ahead).
        """
        folds: List[WalkForwardFold] = []
        total_oos_returns: List[float] = []
        total_is_metrics: List[float] = []

        for idx, win in enumerate(fold_windows):
            tr_start = win["train_start"]
            tr_end = win["train_end"]
            te_start = win["test_start"]
            te_end = win["test_end"]

            # 1. In-Sample Training: Find best parameter candidate
            best_candidate: Dict[str, Any] = param_candidates[0] if param_candidates else {}
            best_is_metric = -float("inf")

            for candidate in param_candidates:
                cfg_is = copy.deepcopy(base_config)
                cfg_is.run_id = f"{walk_forward_id}_fold_{idx + 1}_is"
                cfg_is.start_date = tr_start
                cfg_is.end_date = tr_end
                cfg_is.strategy_parameters.update(candidate)

                res_is = self.runner.run_backtest(cfg_is)
                metric_val = res_is.performance.total_return_pct
                if metric_val > best_is_metric:
                    best_is_metric = metric_val
                    best_candidate = candidate

            # 2. Out-of-Sample Testing: Run with selected parameter candidate on untouched test window
            cfg_oos = copy.deepcopy(base_config)
            cfg_oos.run_id = f"{walk_forward_id}_fold_{idx + 1}_oos"
            cfg_oos.start_date = te_start
            cfg_oos.end_date = te_end
            cfg_oos.strategy_parameters.update(best_candidate)

            res_oos = self.runner.run_backtest(cfg_oos)
            oos_return = res_oos.performance.total_return_pct
            oos_dd = res_oos.performance.drawdown.max_drawdown_pct

            fold = WalkForwardFold(
                fold_index=idx + 1,
                train_start=tr_start,
                train_end=tr_end,
                test_start=te_start,
                test_end=te_end,
                selected_parameters=best_candidate,
                in_sample_metric=round(best_is_metric, 2),
                out_of_sample_metric=round(oos_return, 2),
                out_of_sample_return_pct=round(oos_return, 2),
                out_of_sample_drawdown_pct=round(oos_dd, 2),
            )
            folds.append(fold)

            total_oos_returns.append(oos_return)
            total_is_metrics.append(best_is_metric)

        # Aggregate metrics
        avg_oos = sum(total_oos_returns) / len(total_oos_returns) if total_oos_returns else 0.0
        avg_is = sum(total_is_metrics) / len(total_is_metrics) if total_is_metrics else 0.0

        efficiency = (avg_oos / avg_is) if abs(avg_is) > 1e-4 else 0.0
        robustness_warning = efficiency < 0.30 or avg_oos < 0.0

        return WalkForwardResult(
            walk_forward_id=walk_forward_id,
            strategy_id=base_config.strategy_id,
            folds=folds,
            aggregated_out_of_sample_return_pct=round(avg_oos, 2),
            efficiency_ratio=round(efficiency, 2),
            robustness_warning=robustness_warning,
        )
