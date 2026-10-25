"""Financial Statement Derivations & Arithmetic Engine (Stage 82).

Strict rules:
1. All arithmetic uses lossless Python Decimal.
2. TTM is calculated ONLY by summing 4 consecutive standalone quarters or via annual-YTD bridge.
   NEVER quarter * 4. NEVER sum Balance Sheet items.
3. Standalone quarters from cumulative YTD:
   Q1 = YTD1
   Q2 = YTD2 - YTD1
   Q3 = YTD3 - YTD2
   Q4 = FY - YTD3
   Strictly verify currency, entity, scope, and revision match.
4. Negative values formatted with accounting parentheses: (123.45).
5. Zero is 0.00; missing is "—".
6. Non-positive bases for percentage change return "N/M" (Not Meaningful).
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional, Tuple

from atlas.companies.statements.enums import ScaleType


def format_financial_value(
    value: Optional[Decimal],
    unit_category: str = "currency",
    scale: ScaleType = ScaleType.MILLIONS,
    currency_symbol: str = "$",
    max_decimals: int = 2,
) -> Tuple[str, str]:
    """
    Formats a Decimal value according to scale and financial accounting conventions.
    Returns (formatted_string, scale_used).
    """
    if value is None:
        return "—", "none"

    # Per-share numbers and share counts are NOT scaled to billions/millions
    if unit_category == "currency_per_share":
        rounded = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if rounded < 0:
            return f"({currency_symbol}{abs(rounded):.2f})", "exact"
        return f"{currency_symbol}{rounded:.2f}", "exact"

    if unit_category == "shares":
        # Format in millions or exact
        val_m = value / Decimal("1000000")
        rounded = val_m.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{rounded:,.2f}M", "millions"

    if unit_category == "percent":
        rounded = value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        if rounded < 0:
            return f"({abs(rounded):.1f}%)", "percent"
        return f"{rounded:.1f}%", "percent"

    # Standard currency scaling
    val_float = float(value)
    abs_val = abs(val_float)

    selected_scale = scale
    if scale == ScaleType.AUTO:
        if abs_val >= 1e9:
            selected_scale = ScaleType.BILLIONS
        elif abs_val >= 1e6:
            selected_scale = ScaleType.MILLIONS
        elif abs_val >= 1e3:
            selected_scale = ScaleType.THOUSANDS
        else:
            selected_scale = ScaleType.ORIGINAL

    divisor = Decimal("1")
    suffix = ""
    scale_label = "original"

    if selected_scale == ScaleType.BILLIONS:
        divisor = Decimal("1000000000")
        suffix = "B"
        scale_label = "billions"
    elif selected_scale == ScaleType.MILLIONS:
        divisor = Decimal("1000000")
        suffix = "M"
        scale_label = "millions"
    elif selected_scale == ScaleType.THOUSANDS:
        divisor = Decimal("1000")
        suffix = "K"
        scale_label = "thousands"

    scaled = (value / divisor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if scaled < 0:
        return f"({abs(scaled):,.2f}{suffix})", scale_label
    return f"{scaled:,.2f}{suffix}", scale_label


def derive_standalone_quarter_value(
    current_ytd: Optional[Decimal],
    prior_ytd: Optional[Decimal],
) -> Optional[Decimal]:
    """
    Derives standalone flow for a quarter: Q_n = YTD_n - YTD_{n-1}.
    Requires both facts to be non-None and compatible.
    """
    if current_ytd is None or prior_ytd is None:
        return None
    return current_ytd - prior_ytd


def derive_q4_from_annual_and_9m(
    annual_val: Optional[Decimal],
    nine_month_ytd: Optional[Decimal],
) -> Optional[Decimal]:
    """
    Derives standalone Q4 flow: Q4 = FY - 9M_YTD.
    """
    if annual_val is None or nine_month_ytd is None:
        return None
    return annual_val - nine_month_ytd


def calculate_ttm_sum(
    quarters_values: List[Optional[Decimal]],
) -> Tuple[Optional[Decimal], bool, str]:
    """
    Calculates TTM sum from 4 consecutive standalone quarters.
    Returns (ttm_value, is_valid, reason).
    """
    if len(quarters_values) != 4:
        return None, False, f"Expected 4 quarters, got {len(quarters_values)}"

    if any(q is None for q in quarters_values):
        missing_count = sum(1 for q in quarters_values if q is None)
        return None, False, f"Missing {missing_count} quarter(s) required for TTM sum"

    ttm_val = sum(quarters_values, Decimal("0"))  # type: ignore[arg-type]
    return ttm_val, True, "Sum of 4 consecutive standalone quarters"


def calculate_ttm_annual_bridge(
    prior_fy: Optional[Decimal],
    current_ytd: Optional[Decimal],
    prior_ytd: Optional[Decimal],
) -> Tuple[Optional[Decimal], bool, str]:
    """
    Calculates TTM via bridge: TTM = FY_{prior} + YTD_{current} - YTD_{prior}.
    """
    if prior_fy is None or current_ytd is None or prior_ytd is None:
        return None, False, "Missing required FY or YTD components for annual bridge"

    ttm_val = prior_fy + current_ytd - prior_ytd
    return ttm_val, True, "Annual/YTD bridge calculation"


def calculate_yoy_absolute_change(
    current_val: Optional[Decimal],
    prior_val: Optional[Decimal],
) -> Optional[Decimal]:
    """Calculates YoY absolute change: Current - Prior."""
    if current_val is None or prior_val is None:
        return None
    return current_val - prior_val


def calculate_percentage_change(
    current_val: Optional[Decimal],
    prior_val: Optional[Decimal],
) -> Tuple[Optional[Decimal], bool, str]:
    """
    Calculates percentage change: (Current - Prior) / |Prior| * 100.
    Returns (percentage, is_not_meaningful, formatted_text).
    """
    if current_val is None or prior_val is None:
        return None, False, "—"

    if prior_val == Decimal("0"):
        return None, True, "N/M"

    if prior_val < Decimal("0"):
        # Percentage changes with negative baselines are misleading in financial statements
        return None, True, "N/M"

    diff = current_val - prior_val
    pct = (diff / abs(prior_val)) * Decimal("100")
    rounded = pct.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    if rounded < 0:
        return pct, False, f"({abs(rounded):.1f}%)"
    return pct, False, f"+{rounded:.1f}%"


def calculate_common_size(
    line_item_val: Optional[Decimal],
    denominator_val: Optional[Decimal],
) -> Tuple[Optional[Decimal], str]:
    """
    Calculates common-size percentage: (Line Item / Denominator) * 100.
    Denominator is typically Revenue (Income Statement) or Total Assets (Balance Sheet).
    """
    if line_item_val is None or denominator_val is None:
        return None, "—"

    if denominator_val <= Decimal("0"):
        return None, "N/M"

    pct = (line_item_val / denominator_val) * Decimal("100")
    rounded = pct.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    if rounded < 0:
        return pct, f"({abs(rounded):.1f}%)"
    return pct, f"{rounded:.1f}%"
