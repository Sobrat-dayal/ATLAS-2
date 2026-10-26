"""Deterministic pure Decimal calculations for Earnings Surprises (Stage 84).

Invariants:
- Zero binary float conversions; strictly lossless Python Decimal arithmetic.
- Division-by-zero protection: zero consensus denominator yields None / NOT_COMPARABLE.
- Negative consensus estimate protection: percentage uses |estimate| with explicit qualification.
- No NaN or Infinity propagation.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Optional, Tuple

from atlas.companies.earnings.enums import SurpriseClassification

EPS_IN_LINE_TOLERANCE = Decimal("0.0001")
REVENUE_IN_LINE_PCT_TOLERANCE = Decimal("0.05")  # 0.05% tolerance for revenue in-line classification


def calculate_eps_surprise(
    actual: Optional[Decimal],
    estimate: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[Decimal], SurpriseClassification]:
    """Calculates absolute and percentage EPS surprises with beat/miss classification.
    
    Returns:
        (absolute_surprise, percentage_surprise, classification)
    """
    if actual is None or estimate is None:
        return None, None, SurpriseClassification.UNAVAILABLE

    abs_diff = actual - estimate

    # In-line evaluation within numerical tolerance
    if abs(abs_diff) <= EPS_IN_LINE_TOLERANCE:
        zero_pct = Decimal("0.00")
        return Decimal("0.00"), zero_pct, SurpriseClassification.IN_LINE

    # Zero denominator protection
    if estimate == Decimal("0"):
        # Absolute difference is mathematically defined, percentage is undefined
        classification = (
            SurpriseClassification.BEAT
            if actual > Decimal("0")
            else SurpriseClassification.MISS
        )
        return abs_diff.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), None, classification

    # Standard percentage surprise formula: (Actual - Estimate) / |Estimate| * 100
    denom = abs(estimate)
    pct = ((actual - estimate) / denom) * Decimal("100")
    pct_quantized = pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    abs_quantized = abs_diff.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    classification = (
        SurpriseClassification.BEAT
        if actual > estimate
        else SurpriseClassification.MISS
    )

    return abs_quantized, pct_quantized, classification


def calculate_revenue_surprise(
    actual: Optional[Decimal],
    estimate: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[Decimal], SurpriseClassification]:
    """Calculates absolute and percentage Revenue surprises with beat/miss classification.
    
    Returns:
        (absolute_surprise, percentage_surprise, classification)
    """
    if actual is None or estimate is None:
        return None, None, SurpriseClassification.UNAVAILABLE

    abs_diff = actual - estimate

    if estimate <= Decimal("0"):
        # Non-positive revenue consensus is not economically meaningful
        classification = (
            SurpriseClassification.BEAT if actual > estimate else SurpriseClassification.MISS
        )
        return abs_diff.quantize(Decimal("1"), rounding=ROUND_HALF_UP), None, classification

    pct = ((actual - estimate) / estimate) * Decimal("100")
    pct_quantized = pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    abs_quantized = abs_diff.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    # In-line check if within 0.05% difference
    if abs(pct_quantized) <= REVENUE_IN_LINE_PCT_TOLERANCE:
        return abs_quantized, pct_quantized, SurpriseClassification.IN_LINE

    classification = (
        SurpriseClassification.BEAT
        if actual > estimate
        else SurpriseClassification.MISS
    )

    return abs_quantized, pct_quantized, classification


def format_eps(value: Optional[Decimal], currency: str = "USD") -> str:
    """Formats an EPS value with currency symbol and 2 decimal places."""
    if value is None:
        return "—"
    prefix = "$" if currency == "USD" else f"{currency} "
    sign = "-" if value < 0 else ""
    return f"{sign}{prefix}{abs(value):.2f}"


def format_revenue(value: Optional[Decimal], currency: str = "USD") -> str:
    """Formats large revenue figures into human-readable B/M scales."""
    if value is None:
        return "—"
    prefix = "$" if currency == "USD" else f"{currency} "
    abs_v = abs(value)
    sign = "-" if value < 0 else ""

    if abs_v >= Decimal("1000000000"):
        scaled = abs_v / Decimal("1000000000")
        return f"{sign}{prefix}{scaled:.2f}B"
    elif abs_v >= Decimal("1000000"):
        scaled = abs_v / Decimal("1000000")
        return f"{sign}{prefix}{scaled:.2f}M"
    else:
        return f"{sign}{prefix}{abs_v:,.0f}"


def format_percentage(value: Optional[Decimal]) -> str:
    """Formats a percentage value with sign and 2 decimal places."""
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"
