"""ATLAS Portfolios V1 — Efficient Frontier Builder (Stage 114).

Constructs discrete solver-computed efficient frontier points across feasible target returns.
Never fabricates decorative curves.
"""

from decimal import Decimal
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from atlas.portfolios.optimization.enums import OptimizationObjective, SolverStatus
from atlas.portfolios.optimization.models import EfficientFrontierPoint, OptimizationConstraintItem
from atlas.portfolios.optimization.solvers import ConvexOptimizationSolver

logger = logging.getLogger("atlas.portfolios.optimization.frontier")


class EfficientFrontierBuilder:
    """Builds true mathematical efficient frontier curves via parametric quadratic programming."""

    def __init__(self, solver: Optional[ConvexOptimizationSolver] = None) -> None:
        self.solver = solver or ConvexOptimizationSolver()

    def construct_frontier(
        self,
        symbols: List[str],
        cov_matrix: np.ndarray,
        expected_returns: np.ndarray,
        bounds: List[Tuple[float, float]],
        base_constraints: List[Dict[str, Any]],
        num_points: int = 15,
        risk_free_rate: float = 0.045,
    ) -> List[EfficientFrontierPoint]:
        """Constructs an ordered list of non-dominated efficient frontier points."""
        n = len(symbols)

        # 1. Find Minimum-Variance endpoint
        w_min, diag_min = self.solver.solve(
            symbols=symbols,
            objective_type=OptimizationObjective.MINIMUM_VARIANCE,
            cov_matrix=cov_matrix,
            expected_returns=expected_returns,
            bounds=bounds,
            constraints=base_constraints,
        )
        r_min = float(np.dot(expected_returns, w_min))

        # 2. Find Maximum-Return endpoint
        w_max, diag_max = self.solver.solve(
            symbols=symbols,
            objective_type=OptimizationObjective.MAXIMUM_EXPECTED_RETURN,
            cov_matrix=cov_matrix,
            expected_returns=expected_returns,
            bounds=bounds,
            constraints=base_constraints,
        )
        r_max = float(np.dot(expected_returns, w_max))

        # Guard against zero spread (all assets identical return)
        if r_max <= r_min + 1e-6:
            r_targets = [r_min]
        else:
            r_targets = np.linspace(r_min, r_max, num=num_points)

        points: List[EfficientFrontierPoint] = []

        for r_tgt in r_targets:
            # Build target constraint: mu^T * w >= r_tgt
            target_cons = list(base_constraints)
            target_cons.append({
                "type": "ineq",
                "fun": (lambda t: lambda w: np.dot(expected_returns, w) - t)(r_tgt),
                "jac": lambda w: expected_returns,
            })

            try:
                w_opt, diag = self.solver.solve(
                    symbols=symbols,
                    objective_type=OptimizationObjective.TARGET_RETURN_MIN_VARIANCE,
                    cov_matrix=cov_matrix,
                    expected_returns=expected_returns,
                    bounds=bounds,
                    constraints=target_cons,
                    target_return=float(r_tgt),
                )
                ret_val = float(np.dot(expected_returns, w_opt))
                var_val = float(np.dot(w_opt, np.dot(cov_matrix, w_opt)))
                vol_val = float(np.sqrt(max(var_val, 1e-9)))
                sharpe_val = (ret_val - risk_free_rate) / vol_val if vol_val > 1e-6 else 0.0

                weights_dict = {symbols[i]: Decimal(str(round(float(w_opt[i]), 6))) for i in range(n)}

                points.append(
                    EfficientFrontierPoint(
                        target_return=Decimal(str(round(float(r_tgt), 6))),
                        candidate_weights=weights_dict,
                        estimated_return=Decimal(str(round(ret_val, 6))),
                        estimated_volatility=Decimal(str(round(vol_val, 6))),
                        estimated_sharpe=Decimal(str(round(sharpe_val, 4))),
                        solver_status=diag.status,
                        is_dominated=False,
                    )
                )
            except Exception as e:
                logger.debug("Frontier grid point %.4f infeasible or failed: %s", r_tgt, e)
                continue

        # Sort points by volatility ascending
        points.sort(key=lambda p: float(p.estimated_volatility))

        # Mark dominated points (if any point has higher volatility and lower or equal return)
        max_seen_return = -1e9
        for p in points:
            r = float(p.estimated_return)
            if r < max_seen_return - 1e-5:
                p.is_dominated = True
            else:
                max_seen_return = max(max_seen_return, r)

        return points

    def build_frontier(
        self,
        symbols: List[str],
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.045,
        num_points: int = 15,
        is_long_only: bool = True,
    ) -> List[EfficientFrontierPoint]:
        """Convenience method constructing frontier for long-only or unconstrained portfolios."""
        n = len(symbols)
        bounds = [(0.0, 1.0) for _ in range(n)] if is_long_only else [(-1.0, 1.0) for _ in range(n)]
        constraints = [{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}]
        return self.construct_frontier(
            symbols=symbols,
            cov_matrix=covariance_matrix,
            expected_returns=expected_returns,
            bounds=bounds,
            base_constraints=constraints,
            num_points=num_points,
            risk_free_rate=risk_free_rate,
        )
