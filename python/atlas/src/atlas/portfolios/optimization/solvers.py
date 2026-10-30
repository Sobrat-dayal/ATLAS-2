"""ATLAS Portfolios V1 — Optimization Solvers Engine (Stage 114).

Numerical solver adapter executing convex quadratic, linear, and non-linear
portfolio optimization problems using scipy.optimize.
"""

from decimal import Decimal
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import scipy.optimize as opt

from atlas.portfolios.optimization.enums import OptimizationObjective, SolverStatus
from atlas.portfolios.optimization.errors import (
    PortfolioOptimizationInfeasibleError,
    PortfolioOptimizationNumericalFailureError,
    PortfolioOptimizationRiskFreeRateUnavailableError,
)
from atlas.portfolios.optimization.models import SolverDiagnostics

logger = logging.getLogger("atlas.portfolios.optimization.solvers")


class ConvexOptimizationSolver:
    """Numerical solver for portfolio optimization formulations using Scipy."""

    def solve(
        self,
        symbols: List[str],
        objective_type: OptimizationObjective,
        cov_matrix: np.ndarray,
        expected_returns: np.ndarray,
        bounds: List[Tuple[float, float]],
        constraints: List[Dict[str, Any]],
        risk_aversion: float = 2.0,
        risk_free_rate: float = 0.045,
        target_return: Optional[float] = None,
        benchmark_weights: Optional[np.ndarray] = None,
        initial_weights: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, SolverDiagnostics]:
        """Solves the portfolio optimization problem and returns (weights, diagnostics)."""
        n = len(symbols)
        start_time = time.perf_counter()

        # Initialize uniform or baseline weights
        if initial_weights is not None and len(initial_weights) == n:
            w0 = np.copy(initial_weights)
        else:
            w0 = np.ones(n) / float(n)

        # Clip w0 to bounds if necessary
        for i in range(n):
            lb = bounds[i][0] if bounds[i][0] is not None else -1e9
            ub = bounds[i][1] if bounds[i][1] is not None else 1e9
            w0[i] = min(max(w0[i], lb), ub)
        w0 = w0 / np.sum(w0)

        # Objective Function and Analytical Jacobian
        if objective_type in (OptimizationObjective.MINIMUM_VARIANCE, OptimizationObjective.TARGET_RETURN_MIN_VARIANCE):
            # min 0.5 * w^T * Sigma * w
            def obj(w: np.ndarray) -> float:
                return float(0.5 * np.dot(w, np.dot(cov_matrix, w)))

            def jac(w: np.ndarray) -> np.ndarray:
                return np.dot(cov_matrix, w)

        elif objective_type == OptimizationObjective.MEAN_VARIANCE_UTILITY:
            # min 0.5 * lambda * w^T * Sigma * w - mu^T * w
            lam = float(risk_aversion)

            def obj(w: np.ndarray) -> float:
                variance = float(0.5 * lam * np.dot(w, np.dot(cov_matrix, w)))
                ret = float(np.dot(expected_returns, w))
                return variance - ret

            def jac(w: np.ndarray) -> np.ndarray:
                return lam * np.dot(cov_matrix, w) - expected_returns

        elif objective_type == OptimizationObjective.MAXIMUM_EXPECTED_RETURN:
            # min -mu^T * w
            def obj(w: np.ndarray) -> float:
                return -float(np.dot(expected_returns, w))

            def jac(w: np.ndarray) -> np.ndarray:
                return -expected_returns

        elif objective_type == OptimizationObjective.MAXIMUM_SHARPE:
            rf = float(risk_free_rate)

            def obj(w: np.ndarray) -> float:
                excess = float(np.dot(expected_returns, w) - rf)
                var = float(np.dot(w, np.dot(cov_matrix, w)))
                vol = np.sqrt(max(var, 1e-9))
                # Negative Sharpe for minimization
                return -excess / vol

            def jac(w: np.ndarray) -> np.ndarray:
                excess = float(np.dot(expected_returns, w) - rf)
                var = float(np.dot(w, np.dot(cov_matrix, w)))
                vol = np.sqrt(max(var, 1e-9))
                grad = -expected_returns / vol + (excess * np.dot(cov_matrix, w)) / (vol**3)
                return grad

        elif objective_type == OptimizationObjective.BENCHMARK_TRACKING_ERROR:
            w_b = benchmark_weights if benchmark_weights is not None else (np.ones(n) / float(n))

            def obj(w: np.ndarray) -> float:
                diff = w - w_b
                return float(0.5 * np.dot(diff, np.dot(cov_matrix, diff)))

            def jac(w: np.ndarray) -> np.ndarray:
                diff = w - w_b
                return np.dot(cov_matrix, diff)

        elif objective_type == OptimizationObjective.RISK_PARITY:
            # Spinu (2013) convex formulation for equal risk contribution
            # min 0.5 * w^T * Sigma * w - (1/n) * sum(ln(w_i))
            c = 1.0 / float(n)

            def obj(w: np.ndarray) -> float:
                var = float(0.5 * np.dot(w, np.dot(cov_matrix, w)))
                log_barrier = c * float(np.sum(np.log(np.maximum(w, 1e-12))))
                return var - log_barrier

            def jac(w: np.ndarray) -> np.ndarray:
                return np.dot(cov_matrix, w) - (c / np.maximum(w, 1e-12))
        else:
            raise PortfolioOptimizationNumericalFailureError(f"Unsupported optimization objective {objective_type}")

        # Execute solver
        if objective_type == OptimizationObjective.RISK_PARITY:
            solver_method = "L-BFGS-B"
            solver_constraints = []
            solver_jac = jac
            solver_bounds = [(1e-6, None) for _ in range(n)]
        else:
            solver_method = "SLSQP"
            solver_constraints = constraints
            solver_jac = jac
            solver_bounds = bounds

        try:
            res = opt.minimize(
                fun=obj,
                x0=w0,
                method=solver_method,
                jac=solver_jac,
                bounds=solver_bounds,
                constraints=solver_constraints if solver_method == "SLSQP" else None,
                options={"maxiter": 500, "ftol": 1e-9, "disp": False},
            )
        except Exception as e:
            logger.exception("Numerical solver crashed during optimization: %s", e)
            raise PortfolioOptimizationNumericalFailureError(f"Numerical solver execution error: {str(e)}")

        solve_time_ms = (time.perf_counter() - start_time) * 1000.0

        if not res.success:
            logger.warning("SLSQP solver failed to find feasible optimum: %s", res.message)
            if "Infeasible" in res.message or "inequality" in res.message or "bounds" in res.message:
                raise PortfolioOptimizationInfeasibleError(
                    f"Solver could not find a feasible allocation: {res.message}"
                )
            # If numerical iteration limit or precision issue, flag as inaccurate or numerical failure
            status = SolverStatus.OPTIMAL_INACCURATE if res.status == 8 else SolverStatus.NUMERICAL_FAILURE
        else:
            status = SolverStatus.OPTIMAL

        raw_weights = res.x
        # Post-process for risk parity normalization if needed
        if objective_type == OptimizationObjective.RISK_PARITY and np.sum(raw_weights) > 0:
            raw_weights = raw_weights / np.sum(raw_weights)

        # Check max constraint violation
        max_viol = 0.0
        for c in constraints:
            val = c["fun"](raw_weights)
            if c["type"] == "eq":
                max_viol = max(max_viol, abs(float(val)))
            elif c["type"] == "ineq":
                if val < 0:
                    max_viol = max(max_viol, abs(float(val)))

        # Clean tiny floating point residuals (e.g. 1e-14)
        for i in range(n):
            if abs(raw_weights[i]) < 1e-7:
                raw_weights[i] = 0.0

        # Exact budget re-normalization
        tot = np.sum(raw_weights)
        if tot > 0:
            raw_weights = raw_weights / tot

        diag = SolverDiagnostics(
            solver_name="scipy.optimize.minimize",
            solver_version="1.18.1",
            problem_type=f"Convex Programming ({objective_type.value})",
            status=status,
            iterations=int(res.nit) if hasattr(res, "nit") else 0,
            objective_value=float(res.fun) if hasattr(res, "fun") else None,
            solve_time_ms=round(solve_time_ms, 2),
            max_constraint_violation=float(max_viol),
            warnings=[] if res.success else [res.message],
        )

        return raw_weights, diag

    def solve_minimum_variance(
        self,
        covariance_matrix: np.ndarray,
        is_long_only: bool = True,
        bounds: Optional[List[Tuple[float, float]]] = None,
    ) -> Tuple[np.ndarray, SolverDiagnostics]:
        """Convenience method for Global Minimum Variance optimization."""
        n = covariance_matrix.shape[0]
        bnds = bounds or ([(0.0, 1.0) for _ in range(n)] if is_long_only else [(-1.0, 1.0) for _ in range(n)])
        constraints = [{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}]
        return self.solve(
            symbols=[f"A{i}" for i in range(n)],
            objective_type=OptimizationObjective.MINIMUM_VARIANCE,
            cov_matrix=covariance_matrix,
            expected_returns=np.zeros(n),
            bounds=bnds,
            constraints=constraints,
        )

    def solve_mean_variance_utility(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        risk_aversion: float = 2.0,
        is_long_only: bool = True,
    ) -> Tuple[np.ndarray, SolverDiagnostics]:
        """Convenience method for Mean-Variance Quadratic Utility optimization."""
        n = len(expected_returns)
        bnds = [(0.0, 1.0) for _ in range(n)] if is_long_only else [(-1.0, 1.0) for _ in range(n)]
        constraints = [{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}]
        return self.solve(
            symbols=[f"A{i}" for i in range(n)],
            objective_type=OptimizationObjective.MEAN_VARIANCE_UTILITY,
            cov_matrix=covariance_matrix,
            expected_returns=expected_returns,
            bounds=bnds,
            constraints=constraints,
            risk_aversion=risk_aversion,
        )

    def solve_target_return_min_variance(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        target_return: float,
        is_long_only: bool = True,
    ) -> Tuple[np.ndarray, SolverDiagnostics]:
        """Convenience method for Target Return Minimum Variance optimization."""
        n = len(expected_returns)
        bnds = [(0.0, 1.0) for _ in range(n)] if is_long_only else [(-1.0, 1.0) for _ in range(n)]
        constraints = [
            {"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)},
            {"type": "ineq", "fun": lambda w: float(np.dot(expected_returns, w) - target_return)},
        ]
        return self.solve(
            symbols=[f"A{i}" for i in range(n)],
            objective_type=OptimizationObjective.TARGET_RETURN_MIN_VARIANCE,
            cov_matrix=covariance_matrix,
            expected_returns=expected_returns,
            bounds=bnds,
            constraints=constraints,
            target_return=target_return,
        )

    def solve_maximum_return(
        self,
        expected_returns: np.ndarray,
        is_long_only: bool = True,
    ) -> Tuple[np.ndarray, SolverDiagnostics]:
        """Convenience method for Maximum Expected Return optimization."""
        n = len(expected_returns)
        bnds = [(0.0, 1.0) for _ in range(n)] if is_long_only else [(-1.0, 1.0) for _ in range(n)]
        constraints = [{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}]
        return self.solve(
            symbols=[f"A{i}" for i in range(n)],
            objective_type=OptimizationObjective.MAXIMUM_EXPECTED_RETURN,
            cov_matrix=np.eye(n) * 1e-6,
            expected_returns=expected_returns,
            bounds=bnds,
            constraints=constraints,
        )

    def solve_maximum_sharpe(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        risk_free_rate: float = 0.045,
        is_long_only: bool = True,
    ) -> Tuple[np.ndarray, SolverDiagnostics]:
        """Convenience method for Maximum Sharpe Ratio optimization."""
        n = len(expected_returns)
        bnds = [(0.0, 1.0) for _ in range(n)] if is_long_only else [(-1.0, 1.0) for _ in range(n)]
        constraints = [{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}]
        return self.solve(
            symbols=[f"A{i}" for i in range(n)],
            objective_type=OptimizationObjective.MAXIMUM_SHARPE,
            cov_matrix=covariance_matrix,
            expected_returns=expected_returns,
            bounds=bnds,
            constraints=constraints,
            risk_free_rate=risk_free_rate,
        )

    def solve_risk_parity(
        self,
        covariance_matrix: np.ndarray,
    ) -> Tuple[np.ndarray, SolverDiagnostics]:
        """Convenience method for Equal Risk Contribution (Risk Parity) optimization."""
        n = covariance_matrix.shape[0]
        bnds = [(1e-6, None) for _ in range(n)]
        return self.solve(
            symbols=[f"A{i}" for i in range(n)],
            objective_type=OptimizationObjective.RISK_PARITY,
            cov_matrix=covariance_matrix,
            expected_returns=np.zeros(n),
            bounds=bnds,
            constraints=[],
        )
