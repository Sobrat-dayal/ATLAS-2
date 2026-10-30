"""ATLAS Portfolios V1 — Optimization Constraints Engine (Stage 114).

Implements feasibility prechecks, Scipy constraint formulation,
and independent solution constraint verification.
"""

from decimal import Decimal
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from atlas.portfolios.exposure.registry import get_instrument_classification
from atlas.portfolios.optimization.enums import ConstraintType, FeasibilityStatus
from atlas.portfolios.optimization.errors import (
    PortfolioOptimizationConstraintConflictError,
    PortfolioOptimizationInfeasibleError,
)
from atlas.portfolios.optimization.models import OptimizationConstraintItem

logger = logging.getLogger("atlas.portfolios.optimization.constraints")


class ConstraintEngine:
    """Validates and compiles mathematical constraints for portfolio optimization."""

    def precheck_feasibility(
        self,
        symbols: Any = None,
        constraints: Any = None,
        is_long_only: bool = True,
        **kwargs: Any,
    ) -> None:
        """Pre-checks feasibility before solver invocation.

        Detects contradictory bounds and impossible allocations (e.g. Part LXIV fixture).
        """
        if (
            isinstance(symbols, list)
            and len(symbols) > 0
            and isinstance(symbols[0], OptimizationConstraintItem)
        ):
            constraints, symbols = symbols, constraints

        if constraints is None:
            constraints = []
        if symbols is None:
            symbols = []

        n = len(symbols)
        lower_bounds = {s: Decimal("0.0") if is_long_only else Decimal("-1.0") for s in symbols}
        upper_bounds = {s: Decimal("1.0") for s in symbols}

        for c in constraints:
            if c.constraint_type == ConstraintType.SECURITY_WEIGHT_BOUND:
                target = c.target_id
                if target in symbols:
                    if c.lower_bound is not None:
                        lower_bounds[target] = max(lower_bounds[target], c.lower_bound)
                    if c.upper_bound is not None:
                        upper_bounds[target] = min(upper_bounds[target], c.upper_bound)
            elif c.constraint_type == ConstraintType.CASH_WEIGHT_BOUND:
                if "CASH" in symbols:
                    if c.lower_bound is not None:
                        lower_bounds["CASH"] = max(lower_bounds["CASH"], c.lower_bound)
                    if c.upper_bound is not None:
                        upper_bounds["CASH"] = min(upper_bounds["CASH"], c.upper_bound)

        # Check bounds consistency: lower <= upper for each asset
        for s in symbols:
            if lower_bounds[s] > upper_bounds[s]:
                raise PortfolioOptimizationConstraintConflictError(
                    f"Contradictory weight bounds for {s}: lower bound {lower_bounds[s]} exceeds upper bound {upper_bounds[s]}"
                )

        # Check budget feasibility: sum(lower) <= 1.0 and sum(upper) >= 1.0
        sum_lower = sum(lower_bounds.values())
        sum_upper = sum(upper_bounds.values())

        if sum_lower > Decimal("1.00001"):
            raise PortfolioOptimizationInfeasibleError(
                f"Combined minimum asset weight constraints total {sum_lower * 100:.2f}%, which exceeds 100% portfolio budget."
            )

        if sum_upper < Decimal("0.99999"):
            pct_val = float(sum_upper) * 100.0
            raise PortfolioOptimizationInfeasibleError(
                f"Maximum permitted combined asset weights total only {pct_val:.1f}%, which is less than the required 100% portfolio budget."
            )

    def build_scipy_bounds_and_constraints(
        self,
        symbols: List[str],
        constraints: List[OptimizationConstraintItem],
        expected_returns: Optional[np.ndarray] = None,
        target_return: Optional[float] = None,
        baseline_weights: Optional[Dict[str, Decimal]] = None,
        max_turnover: Optional[float] = None,
        is_long_only: bool = True,
    ) -> Tuple[List[Tuple[float, float]], List[Dict[str, Any]]]:
        """Builds Scipy-compatible bounds list and constraint dictionaries."""
        n = len(symbols)
        lower = [0.0 if is_long_only else -1.0] * n
        upper = [1.0] * n

        sym_to_idx = {s: i for i, s in enumerate(symbols)}

        for c in constraints:
            if c.constraint_type == ConstraintType.SECURITY_WEIGHT_BOUND and c.target_id in sym_to_idx:
                idx = sym_to_idx[c.target_id]
                if c.lower_bound is not None:
                    lower[idx] = max(lower[idx], float(c.lower_bound))
                if c.upper_bound is not None:
                    upper[idx] = min(upper[idx], float(c.upper_bound))
            elif c.constraint_type == ConstraintType.CASH_WEIGHT_BOUND and "CASH" in sym_to_idx:
                idx = sym_to_idx["CASH"]
                if c.lower_bound is not None:
                    lower[idx] = max(lower[idx], float(c.lower_bound))
                if c.upper_bound is not None:
                    upper[idx] = min(upper[idx], float(c.upper_bound))
            elif c.constraint_type == ConstraintType.FROZEN_HOLDING and c.target_id in sym_to_idx:
                idx = sym_to_idx[c.target_id]
                fixed_w = float(baseline_weights.get(c.target_id, Decimal("0.0"))) if baseline_weights else 0.0
                lower[idx] = fixed_w
                upper[idx] = fixed_w

        bounds = [(lower[i], upper[i]) for i in range(n)]

        scipy_constraints: List[Dict[str, Any]] = []

        # 1. Fully invested budget constraint: sum(w) = 1.0
        scipy_constraints.append({
            "type": "eq",
            "fun": lambda w: np.sum(w) - 1.0,
            "jac": lambda w: np.ones(n),
        })

        # 2. Target return constraint: mu^T * w >= target_return
        if target_return is not None and expected_returns is not None:
            scipy_constraints.append({
                "type": "ineq",
                "fun": lambda w: np.dot(expected_returns, w) - target_return,
                "jac": lambda w: expected_returns,
            })

        # 3. Sector exposure constraints: sum_{i in sector} w_i <= sector_cap
        sector_caps: Dict[str, float] = {}
        for c in constraints:
            if c.constraint_type == ConstraintType.SECTOR_WEIGHT_BOUND and c.target_id:
                if c.upper_bound is not None:
                    sector_caps[c.target_id.lower().replace(" ", "_")] = float(c.upper_bound)

        for sec_id, cap in sector_caps.items():
            sector_mask = np.zeros(n, dtype=float)
            for s, idx in sym_to_idx.items():
                meta = get_instrument_classification(s)
                if meta and meta.sector.lower().replace(" ", "_") == sec_id:
                    sector_mask[idx] = 1.0
            if np.sum(sector_mask) > 0:
                scipy_constraints.append({
                    "type": "ineq",
                    "fun": (lambda mask, limit: lambda w: limit - np.dot(mask, w))(sector_mask, cap),
                    "jac": (lambda mask: lambda w: -mask)(sector_mask),
                })

        # 4. Turnover constraint: 0.5 * sum(|w_i - w_0,i|) <= max_turnover
        if max_turnover is not None and baseline_weights:
            w0 = np.array([float(baseline_weights.get(s, Decimal("0.0"))) for s in symbols])
            scipy_constraints.append({
                "type": "ineq",
                "fun": lambda w: max_turnover - 0.5 * np.sum(np.abs(w - w0)),
            })

        return bounds, scipy_constraints

    def verify_solution(
        self,
        symbols: List[str],
        weights: Dict[str, Decimal],
        constraints: List[OptimizationConstraintItem],
        tolerance: Decimal = Decimal("0.001"),
    ) -> Tuple[FeasibilityStatus, Dict[str, Decimal], List[str]]:
        """Independently verifies candidate weights against all constraints.

        Returns (FeasibilityStatus, constraint_slacks, active_constraints).
        """
        slacks: Dict[str, Decimal] = {}
        active_constraints: List[str] = []
        is_feasible = True

        # Check budget constraint
        total_w = sum(weights.values(), Decimal("0.0"))
        budget_err = abs(total_w - Decimal("1.0"))
        slacks["FULLY_INVESTED"] = Decimal("1.0") - total_w
        if budget_err > tolerance:
            is_feasible = False
        if budget_err < Decimal("0.0001"):
            active_constraints.append("Budget constraint (Sum = 100%)")

        for c in constraints:
            cid = f"{c.constraint_type.value}:{c.target_id or 'GLOBAL'}"
            if c.constraint_type == ConstraintType.SECURITY_WEIGHT_BOUND and c.target_id in weights:
                w = weights[c.target_id]
                if c.upper_bound is not None:
                    slack = c.upper_bound - w
                    slacks[f"{cid}:UPPER"] = slack
                    if slack < -tolerance and c.is_hard:
                        is_feasible = False
                    elif abs(slack) < Decimal("0.0005"):
                        active_constraints.append(f"{c.target_id} Max Weight Cap ({float(c.upper_bound)*100:.1f}%)")
                if c.lower_bound is not None:
                    slack = w - c.lower_bound
                    slacks[f"{cid}:LOWER"] = slack
                    if slack < -tolerance and c.is_hard:
                        is_feasible = False
                    elif abs(slack) < Decimal("0.0005"):
                        active_constraints.append(f"{c.target_id} Min Weight Floor ({float(c.lower_bound)*100:.1f}%)")
            elif c.constraint_type == ConstraintType.CASH_WEIGHT_BOUND and "CASH" in weights:
                w = weights["CASH"]
                if c.upper_bound is not None:
                    slack = c.upper_bound - w
                    slacks[f"{cid}:UPPER"] = slack
                    if slack < -tolerance and c.is_hard:
                        is_feasible = False
                if c.lower_bound is not None:
                    slack = w - c.lower_bound
                    slacks[f"{cid}:LOWER"] = slack
                    if slack < -tolerance and c.is_hard:
                        is_feasible = False
                    elif abs(slack) < Decimal("0.0005"):
                        active_constraints.append(f"Cash Floor ({float(c.lower_bound)*100:.1f}%)")

        status = FeasibilityStatus.FEASIBLE if is_feasible else FeasibilityStatus.TOLERANCE_VIOLATION
        return status, slacks, active_constraints
