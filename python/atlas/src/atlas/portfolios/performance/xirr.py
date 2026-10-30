"""Money-Weighted Return (MWR) and XIRR Numerical Solver for ATLAS (Stage 111).

Implements bounded root finding for annualized XIRR using the ACT/365 convention.
Provides convergence diagnostics and explicit multiple-root detection.
"""

from datetime import datetime
from decimal import Decimal
import math
from typing import List, Optional, Tuple

from atlas.portfolios.performance.errors import (
    PortfolioPerformanceXirrInvalidCashFlowsError,
    PortfolioPerformanceXirrNoSolutionError,
    PortfolioPerformanceXirrNonConvergenceError,
)


def calculate_xirr(
    # dated_flows: list of (datetime, Decimal) where Decimal is INVESTOR perspective flow
    # (negative for capital deposited, positive for capital withdrawn or terminal value)
    dated_flows: List[Tuple[datetime, Decimal]],
    max_iterations: int = 100,
    tolerance: float = 1e-7,
) -> Tuple[Decimal, bool, str]:
    """Calculates annualized Money-Weighted Return via XIRR.

    Equation:
        f(r) = Sum( C_i / (1 + r)^((t_i - t_0)/365) ) = 0

    Returns:
        (xirr_rate, multiple_roots_possible, diagnostic_status)

    Raises:
        PortfolioPerformanceXirrInvalidCashFlowsError: If flows lack sign variation.
        PortfolioPerformanceXirrNoSolutionError: If no valid root exists.
    """
    if not dated_flows or len(dated_flows) < 2:
        raise PortfolioPerformanceXirrInvalidCashFlowsError(
            "XIRR requires at least two dated cash flows"
        )

    # Sort chronologically
    sorted_flows = sorted(dated_flows, key=lambda x: x[0])
    t0 = sorted_flows[0][0]

    # Convert to float tuples (days_from_t0, amount)
    float_flows: List[Tuple[float, float]] = []
    has_pos = False
    has_neg = False
    sign_changes = 0
    last_sign = 0

    for dt, amt in sorted_flows:
        amount_float = float(amt)
        if abs(amount_float) < 1e-12:
            continue
        days = (dt - t0).total_seconds() / 86400.0
        float_flows.append((days, amount_float))

        current_sign = 1 if amount_float > 0 else -1
        if last_sign != 0 and current_sign != last_sign:
            sign_changes += 1
        last_sign = current_sign

        if amount_float > 0:
            has_pos = True
        elif amount_float < 0:
            has_neg = True

    if not has_pos or not has_neg:
        raise PortfolioPerformanceXirrInvalidCashFlowsError(
            "Cash flow schedule must contain at least one positive and one negative flow for XIRR"
        )

    multiple_roots = sign_changes > 1

    # Define objective function and its first derivative
    def f(r: float) -> float:
        if r <= -1.0:
            return float("inf")
        val = 0.0
        for days, c in float_flows:
            try:
                val += c / math.pow(1.0 + r, days / 365.0)
            except OverflowError:
                return float("inf")
        return val

    def df(r: float) -> float:
        if r <= -1.0:
            return float("-inf")
        val = 0.0
        for days, c in float_flows:
            try:
                power = days / 365.0
                val -= (power * c) / math.pow(1.0 + r, power + 1.0)
            except OverflowError:
                return float("-inf")
        return val

    # Bounded Newton-Raphson with bracket fallback
    r = 0.10  # Initial guess of 10%
    low_bound = -0.9999
    high_bound = 50.0

    for iteration in range(max_iterations):
        val = f(r)
        if abs(val) < tolerance:
            return Decimal(str(round(r, 6))), multiple_roots, "CONVERGED_NEWTON"

        deriv = df(r)
        if abs(deriv) < 1e-14:
            break

        step = val / deriv
        new_r = r - step

        # If step leaves acceptable domain, clamp or fallback
        if new_r <= low_bound or new_r > high_bound or math.isnan(new_r):
            break
        r = new_r

    # Fallback to Bisection search if Newton did not converge
    b_low = -0.9999
    b_high = 20.0
    f_low = f(b_low)
    f_high = f(b_high)

    # Check if a sign change exists across the bracket
    if f_low * f_high > 0:
        # Search for a bracket
        found_bracket = False
        candidates = [-0.99, -0.9, -0.5, -0.2, 0.0, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
        vals = [f(c) for c in candidates]
        for i in range(len(candidates) - 1):
            if vals[i] * vals[i + 1] <= 0:
                b_low, b_high = candidates[i], candidates[i + 1]
                f_low, f_high = vals[i], vals[i + 1]
                found_bracket = True
                break

        if not found_bracket:
            raise PortfolioPerformanceXirrNoSolutionError(
                "XIRR solver could not find a sign-reversing bracket for the cash flow schedule"
            )

    # Bisection
    for _ in range(100):
        mid = (b_low + b_high) / 2.0
        f_mid = f(mid)
        if abs(f_mid) < tolerance or (b_high - b_low) < tolerance:
            return Decimal(str(round(mid, 6))), multiple_roots, "CONVERGED_BISECTION"
        if f_low * f_mid < 0:
            b_high = mid
            f_high = f_mid
        else:
            b_low = mid
            f_low = f_mid

    # Final residual validation
    final_val = f(b_low)
    if abs(final_val) < 1e-4:
        return Decimal(str(round(b_low, 6))), multiple_roots, "CONVERGED_WITH_RESIDUAL"

    raise PortfolioPerformanceXirrNonConvergenceError(
        f"XIRR solver failed to converge within {max_iterations} iterations"
    )

