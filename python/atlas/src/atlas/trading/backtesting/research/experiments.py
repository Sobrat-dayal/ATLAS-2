"""Parameter Sweeps, Sensitivity Matrices and Overfitting Safeguards (Stage 143)."""

from __future__ import annotations

import copy
import itertools
from typing import Any, Dict, List, Optional

from atlas.trading.backtesting.domain import (
    AtlasBacktestConfig,
    AtlasBacktestResult,
    ParameterExperimentConfig,
    ParameterExperimentResult,
)
from atlas.trading.backtesting.errors import BacktestResourceQuotaExceededError
from atlas.trading.backtesting.nautilus.runner import IsolatedBacktestRunner


class ParameterExperimentEngine:
    """Executes multi-parameter grid searches and evaluates sensitivity matrices."""

    def __init__(self, runner: Optional[IsolatedBacktestRunner] = None):
        self.runner = runner or IsolatedBacktestRunner()

    def run_parameter_sweep(
        self,
        exp_config: ParameterExperimentConfig,
        custom_bars: Optional[List[Dict[str, Any]]] = None,
    ) -> ParameterExperimentResult:
        """
        Execute parameter grid search with resource quota enforcement.
        Enforces Test Q & Part LXXVII.
        """
        keys = list(exp_config.parameter_grid.keys())
        values_lists = [exp_config.parameter_grid[k] for k in keys]
        combinations = [dict(zip(keys, prod)) for prod in itertools.product(*values_lists)]

        if len(combinations) > exp_config.max_combinations:
            raise BacktestResourceQuotaExceededError(
                resource_type="parameter_combinations",
                requested=len(combinations),
                maximum=exp_config.max_combinations,
            )

        results_matrix: List[Dict[str, Any]] = []
        best_params: Dict[str, Any] = {}
        best_metric_val = -float("inf")

        for idx, params in enumerate(combinations):
            # Create isolated run config for combination
            cfg = copy.deepcopy(exp_config.base_config)
            cfg.run_id = f"{exp_config.experiment_id}_combo_{idx + 1}"
            cfg.strategy_parameters.update(params)

            res = self.runner.run_backtest(cfg, custom_bars=custom_bars)

            # Extract metric
            metric_val = 0.0
            if exp_config.objective_metric == "sharpe_ratio":
                metric_val = res.performance.sharpe_ratio or 0.0
            elif exp_config.objective_metric == "total_return_pct":
                metric_val = res.performance.total_return_pct
            elif exp_config.objective_metric == "profit_factor":
                metric_val = res.performance.profit_factor or 0.0

            row = dict(params)
            row["metric_value"] = metric_val
            row["total_return_pct"] = res.performance.total_return_pct
            row["max_drawdown_pct"] = res.performance.drawdown.max_drawdown_pct
            row["trades_count"] = res.performance.total_trades_count
            results_matrix.append(row)

            if metric_val > best_metric_val:
                best_metric_val = metric_val
                best_params = params

        # Overfitting check: if best metric is an extreme outlier compared to neighborhood
        overfitting = False
        memo = None
        metric_vals = [r["metric_value"] for r in results_matrix]
        if len(metric_vals) >= 3:
            avg_m = sum(metric_vals) / len(metric_vals)
            if best_metric_val > avg_m * 3.0 and best_metric_val > 1.0:
                overfitting = True
                memo = "WARNING: In-sample peak is an isolated outlier (>3x grid average). High probability of historical curve fitting."

        return ParameterExperimentResult(
            experiment_id=exp_config.experiment_id,
            combinations_tested=len(combinations),
            results_matrix=results_matrix,
            best_parameters=best_params,
            best_metric_value=round(best_metric_val, 4),
            overfitting_warning=overfitting,
            warning_memo=memo,
        )

