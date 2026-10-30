"""ATLAS Portfolios V1 — Optimization Sensitivity Analysis (Stage 114).

Evaluates bounded assumption perturbations to demonstrate model sensitivity
without making false forecast claims.
"""

from decimal import Decimal
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from atlas.portfolios.optimization.enums import OptimizationObjective
from atlas.portfolios.optimization.models import (
    OptimizationConstraintItem,
    SensitivityScenarioResult,
)
from atlas.portfolios.optimization.solvers import ConvexOptimizationSolver

logger = logging.getLogger("atlas.portfolios.optimization.sensitivity")


class SensitivityEngine:
    """Executes sensitivity scenarios over return assumptions, risk aversion, and caps."""

    def __init__(self, solver: Optional[ConvexOptimizationSolver] = None) -> None:
        self.solver = solver or ConvexOptimizationSolver()

    def run_scenarios(
        self,
        symbols: List[str],
        base_cov: np.ndarray,
        base_returns: np.ndarray,
        base_bounds: List[Tuple[float, float]],
        base_constraints: List[Dict[str, Any]],
        baseline_weights: Dict[str, Decimal],
        risk_aversion: float = 2.0,
    ) -> List[SensitivityScenarioResult]:
        """Runs standard sensitivity scenarios across model inputs."""
        n = len(symbols)
        results: List[SensitivityScenarioResult] = []

        # Scenario 1: Expected Returns +100 bps (+1.0%)
        try:
            r_high = base_returns + 0.01
            w_high, _ = self.solver.solve(
                symbols=symbols,
                objective_type=OptimizationObjective.MEAN_VARIANCE_UTILITY,
                cov_matrix=base_cov,
                expected_returns=r_high,
                bounds=base_bounds,
                constraints=base_constraints,
                risk_aversion=risk_aversion,
            )
            ret_val = Decimal(str(round(float(np.dot(r_high, w_high)), 6)))
            vol_val = Decimal(str(round(float(np.sqrt(np.dot(w_high, np.dot(base_cov, w_high)))), 6)))
            w_dict = {symbols[i]: Decimal(str(round(float(w_high[i]), 6))) for i in range(n)}
            turnover = sum(abs(w_dict[s] - baseline_weights.get(s, Decimal("0.0"))) for s in symbols) / Decimal("2.0")

            results.append(
                SensitivityScenarioResult(
                    scenario_name="Optimistic Alpha (+100 bps)",
                    parameter_name="Expected Return Delta",
                    parameter_value="+1.0%",
                    estimated_return=ret_val,
                    estimated_volatility=vol_val,
                    estimated_turnover=turnover,
                    candidate_weights=w_dict,
                )
            )
        except Exception as e:
            logger.debug("Scenario Expected Return +100 bps failed: %s", e)

        # Scenario 2: Conservative Risk Aversion (lambda = 4.0)
        try:
            w_cons, _ = self.solver.solve(
                symbols=symbols,
                objective_type=OptimizationObjective.MEAN_VARIANCE_UTILITY,
                cov_matrix=base_cov,
                expected_returns=base_returns,
                bounds=base_bounds,
                constraints=base_constraints,
                risk_aversion=4.0,
            )
            ret_val = Decimal(str(round(float(np.dot(base_returns, w_cons)), 6)))
            vol_val = Decimal(str(round(float(np.sqrt(np.dot(w_cons, np.dot(base_cov, w_cons)))), 6)))
            w_dict = {symbols[i]: Decimal(str(round(float(w_cons[i]), 6))) for i in range(n)}
            turnover = sum(abs(w_dict[s] - baseline_weights.get(s, Decimal("0.0"))) for s in symbols) / Decimal("2.0")

            results.append(
                SensitivityScenarioResult(
                    scenario_name="Conservative Risk Aversion (λ = 4.0)",
                    parameter_name="Risk Aversion Parameter",
                    parameter_value="4.0",
                    estimated_return=ret_val,
                    estimated_volatility=vol_val,
                    estimated_turnover=turnover,
                    candidate_weights=w_dict,
                )
            )
        except Exception as e:
            logger.debug("Scenario Conservative lambda=4.0 failed: %s", e)

        # Scenario 3: Aggressive Risk Aversion (lambda = 1.0)
        try:
            w_aggr, _ = self.solver.solve(
                symbols=symbols,
                objective_type=OptimizationObjective.MEAN_VARIANCE_UTILITY,
                cov_matrix=base_cov,
                expected_returns=base_returns,
                bounds=base_bounds,
                constraints=base_constraints,
                risk_aversion=1.0,
            )
            ret_val = Decimal(str(round(float(np.dot(base_returns, w_aggr)), 6)))
            vol_val = Decimal(str(round(float(np.sqrt(np.dot(w_aggr, np.dot(base_cov, w_aggr)))), 6)))
            w_dict = {symbols[i]: Decimal(str(round(float(w_aggr[i]), 6))) for i in range(n)}
            turnover = sum(abs(w_dict[s] - baseline_weights.get(s, Decimal("0.0"))) for s in symbols) / Decimal("2.0")

            results.append(
                SensitivityScenarioResult(
                    scenario_name="Aggressive Risk Aversion (λ = 1.0)",
                    parameter_name="Risk Aversion Parameter",
                    parameter_value="1.0",
                    estimated_return=ret_val,
                    estimated_volatility=vol_val,
                    estimated_turnover=turnover,
                    candidate_weights=w_dict,
                )
            )
        except Exception as e:
            logger.debug("Scenario Aggressive lambda=1.0 failed: %s", e)

        return results

    def evaluate_sensitivity(
        self,
        symbols: List[str],
        base_expected_returns: np.ndarray,
        base_covariance: np.ndarray,
        base_weights: Dict[str, Decimal],
        risk_aversion: float = 2.0,
        is_long_only: bool = True,
    ) -> List[SensitivityScenarioResult]:
        """Convenience method running standard sensitivity perturbations."""
        n = len(symbols)
        bounds = [(0.0, 1.0) for _ in range(n)] if is_long_only else [(-1.0, 1.0) for _ in range(n)]
        constraints = [{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}]
        return self.run_scenarios(
            symbols=symbols,
            base_cov=base_covariance,
            base_returns=base_expected_returns,
            base_bounds=bounds,
            base_constraints=constraints,
            baseline_weights=base_weights,
            risk_aversion=risk_aversion,
        )
