"""Accounting Period Compatibility Verification (Stage 137).

Enforces institutional invariants:
- A numerator and denominator must represent compatible reporting durations (e.g., annual vs annual, quarter vs quarter).
- Annual vs quarterly mixing without time-weighting or explicit annualized denominator is rejected.
"""

from typing import Tuple
from atlas.exposure.errors import IncompatiblePeriodError


def verify_period_compatibility(
    numerator_period: str,
    denominator_period: str,
    allow_annualized_quarter: bool = False
) -> Tuple[bool, str]:
    """Verify that two accounting periods are comparable for ratio calculation."""
    num_norm = numerator_period.strip().upper()
    den_norm = denominator_period.strip().upper()

    if num_norm == den_norm:
        return True, "EXACT_PERIOD_MATCH"

    # Both annual
    if ("FY" in num_norm or "YEAR" in num_norm or len(num_norm) == 4) and ("FY" in den_norm or "YEAR" in den_norm or len(den_norm) == 4):
        if num_norm == den_norm:
            return True, "ANNUAL_PERIOD_MATCH"
        raise IncompatiblePeriodError(
            f"Mismatched financial years: numerator is {numerator_period}, denominator is {denominator_period}."
        )

    # Quarterly mismatch
    if ("Q" in num_norm and "FY" in den_norm) or ("FY" in num_norm and "Q" in den_norm):
        if not allow_annualized_quarter:
            raise IncompatiblePeriodError(
                f"Cannot divide quarterly metric ({numerator_period}) by annual denominator ({denominator_period}) without annualization."
            )
        return True, "QUARTER_ANNUALIZED_ALLOWED"

    if num_norm != den_norm:
        raise IncompatiblePeriodError(
            f"Incompatible reporting periods: {numerator_period} vs {denominator_period}."
        )

    return True, "COMPATIBLE"
