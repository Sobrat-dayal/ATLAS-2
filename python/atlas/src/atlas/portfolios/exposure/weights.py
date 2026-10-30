"""ATLAS Portfolios V1 — Mathematical Weight & Concentration Calculations (Stage 112).

Pure financial arithmetic with Decimal precision:
- Valid positive NAV denominator validation
- NAV-proportional weight and percentage computation
- Herfindahl-Hirschman Index (HHI) and Effective Number of Holdings
- Top-N concentration summation
- Complete disjoint partition reconciliation verification
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple

from atlas.portfolios.exposure.errors import PortfolioExposureNavInvalidError


def validate_nav_denominator(nav: Decimal) -> None:
    """Verifies that the portfolio NAV is strictly positive."""
    if nav <= Decimal("0.00"):
        raise PortfolioExposureNavInvalidError(
            f"Portfolio NAV denominator must be strictly positive (received: {nav})."
        )


def calculate_weight(value: Decimal, nav: Decimal) -> Tuple[Decimal, Decimal]:
    """Calculates decimal fraction weight and percentage for a monetary value against NAV."""
    validate_nav_denominator(nav)
    w = value / nav
    pct = w * Decimal("100.0")
    return w, pct


def calculate_concentration_hhi(
    weights: List[Decimal],
) -> Tuple[Decimal, Decimal, Optional[Decimal]]:
    """Calculates Herfindahl-Hirschman Index (HHI) and Effective Number of Holdings.

    Args:
        weights: List of decimal weights as fractions (e.g. 0.50, 0.25, 0.25).

    Returns:
        Tuple of (hhi_decimal, hhi_conventional, effective_n)
        - hhi_decimal: sum(w_i^2) between 0.0 and 1.0 (e.g., 0.375)
        - hhi_conventional: hhi_decimal * 10,000 (e.g., 3750)
        - effective_n: 1 / hhi_decimal (e.g., 2.6667)
    """
    if not weights:
        return Decimal("0.0"), Decimal("0.0"), None

    hhi_dec = Decimal("0.0")
    for w in weights:
        hhi_dec += w * w

    hhi_conv = (hhi_dec * Decimal("10000.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if hhi_dec > Decimal("0.0"):
        eff_n = (Decimal("1.0") / hhi_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        eff_n = None

    return hhi_dec, hhi_conv, eff_n


def calculate_top_n_weights(sorted_weights: List[Decimal]) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    """Calculates Top-1, Top-3, Top-5, Top-10, and Top-20 cumulative weights from a descending sorted list."""
    w1 = sorted_weights[0] if len(sorted_weights) >= 1 else Decimal("0.00")
    w3 = sum(sorted_weights[:3]) if len(sorted_weights) >= 1 else Decimal("0.00")
    w5 = sum(sorted_weights[:5]) if len(sorted_weights) >= 1 else Decimal("0.00")
    w10 = sum(sorted_weights[:10]) if len(sorted_weights) >= 1 else Decimal("0.00")
    w20 = sum(sorted_weights[:20]) if len(sorted_weights) >= 1 else Decimal("0.00")
    return w1, w3, w5, w10, w20


def verify_partition_reconciliation(
    values: List[Decimal],
    nav: Decimal,
    tolerance: Decimal = Decimal("0.05"),
) -> Tuple[bool, Decimal]:
    """Verifies that the sum of partitioned category values reconciles to total NAV.

    Returns:
        (is_reconciled, discrepancy_amount)
    """
    total = sum(values) if values else Decimal("0.00")
    discrepancy = abs(total - nav)
    is_reconciled = discrepancy <= tolerance
    return is_reconciled, discrepancy

