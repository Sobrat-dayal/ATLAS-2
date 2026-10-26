"""Pure, decimal-safe financial calculation functions for Company Ownership Intelligence (Stage 85).

Guarantees exact numerical precision for ownership percentages, position changes,
percentage-point differentials, concentration metrics, and formatted financial outputs.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Dict, List, Optional, Union


def to_decimal(val: Optional[Union[Decimal, int, float, str]]) -> Optional[Decimal]:
    """Safely converts arbitrary input to Decimal or returns None."""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return val
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError, TypeError):
        return None


def calculate_ownership_percentage(
    shares_held: Optional[Union[Decimal, int, float, str]],
    shares_outstanding: Optional[Union[Decimal, int, float, str]],
) -> Optional[Decimal]:
    """Calculates ownership percentage against a compatible shares-outstanding denominator.

    Formula:
        Ownership % = (Shares Held / Shares Outstanding) * 100

    Guarantees:
        - Returns None if either parameter is None, missing, or shares_outstanding <= 0.
        - Quantizes to 4 decimal places (ROUND_HALF_UP).
        - Traps zero division and numerical overflow cleanly.
    """
    d_held = to_decimal(shares_held)
    d_out = to_decimal(shares_outstanding)

    if d_held is None or d_out is None or d_out <= Decimal("0"):
        return None

    try:
        pct = (d_held / d_out) * Decimal("100")
        return pct.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    except (ZeroDivisionError, InvalidOperation):
        return None


def calculate_shares_change(
    current_shares: Optional[Union[Decimal, int, float, str]],
    prior_shares: Optional[Union[Decimal, int, float, str]],
) -> Decimal:
    """Calculates absolute change in shares held between two comparable snapshots.

    Formula:
        Δ Shares = Current Shares - Prior Shares
    """
    d_curr = to_decimal(current_shares) or Decimal("0")
    d_prior = to_decimal(prior_shares) or Decimal("0")
    return d_curr - d_prior


def calculate_position_percentage_change(
    current_shares: Optional[Union[Decimal, int, float, str]],
    prior_shares: Optional[Union[Decimal, int, float, str]],
) -> Optional[Decimal]:
    """Calculates relative percentage change in an investor's position.

    Formula:
        Position Change % = ((Current Shares - Prior Shares) / |Prior Shares|) * 100

    Guarantees:
        - If prior_shares is zero or missing, returns None (classified as NEW_POSITION).
        - Quantizes to 2 decimal places.
    """
    d_curr = to_decimal(current_shares)
    d_prior = to_decimal(prior_shares)

    if d_curr is None or d_prior is None or d_prior == Decimal("0"):
        return None

    try:
        abs_prior = abs(d_prior)
        diff = d_curr - d_prior
        pct = (diff / abs_prior) * Decimal("100")
        return pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (ZeroDivisionError, InvalidOperation):
        return None


def calculate_percentage_points_change(
    current_pct: Optional[Union[Decimal, float, str]],
    prior_pct: Optional[Union[Decimal, float, str]],
) -> Optional[Decimal]:
    """Calculates percentage-point change in ownership stake.

    Formula:
        Δ Ownership (pp) = Current % - Prior %
    """
    d_curr = to_decimal(current_pct)
    d_prior = to_decimal(prior_pct)

    if d_curr is None or d_prior is None:
        return None

    diff = d_curr - d_prior
    return diff.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def calculate_concentration_metrics(
    holdings: List[Union[Decimal, int, float]],
    shares_outstanding: Optional[Union[Decimal, int, float, str]] = None,
) -> Dict[str, Optional[Decimal]]:
    """Calculates top holder concentration metrics (Top 1, Top 5, Top 10, Total Disclosed).

    Accepts a list of shares held (sorted descending or unsorted) and an optional
    shares-outstanding denominator.
    """
    dec_holdings = sorted([to_decimal(h) or Decimal("0") for h in holdings], reverse=True)
    d_out = to_decimal(shares_outstanding)

    top_1_shares = sum(dec_holdings[:1]) if dec_holdings else Decimal("0")
    top_5_shares = sum(dec_holdings[:5]) if dec_holdings else Decimal("0")
    top_10_shares = sum(dec_holdings[:10]) if dec_holdings else Decimal("0")
    total_disclosed = sum(dec_holdings) if dec_holdings else Decimal("0")

    return {
        "top_1_shares": top_1_shares,
        "top_1_pct": calculate_ownership_percentage(top_1_shares, d_out) if d_out else None,
        "top_5_shares": top_5_shares,
        "top_5_pct": calculate_ownership_percentage(top_5_shares, d_out) if d_out else None,
        "top_10_shares": top_10_shares,
        "top_10_pct": calculate_ownership_percentage(top_10_shares, d_out) if d_out else None,
        "total_disclosed_shares": total_disclosed,
        "total_disclosed_pct": calculate_ownership_percentage(total_disclosed, d_out) if d_out else None,
    }


def format_shares_count(shares: Optional[Union[Decimal, int, float, str]], compact: bool = True) -> str:
    """Formats share counts into readable financial notation."""
    d = to_decimal(shares)
    if d is None:
        return "—"

    if compact:
        abs_d = abs(d)
        sign = "-" if d < 0 else ""
        if abs_d >= Decimal("1000000000"):
            scaled = (abs_d / Decimal("1000000000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return f"{sign}{scaled}B"
        if abs_d >= Decimal("1000000"):
            scaled = (abs_d / Decimal("1000000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return f"{sign}{scaled}M"
        if abs_d >= Decimal("1000"):
            scaled = (abs_d / Decimal("1000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return f"{sign}{scaled}K"

    # Full comma-separated representation
    return f"{int(d):,}"


def format_percentage(pct: Optional[Union[Decimal, float, str]], include_sign: bool = False) -> str:
    """Formats an ownership percentage with 2 decimal places."""
    d = to_decimal(pct)
    if d is None:
        return "—"

    q = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if include_sign and q > Decimal("0"):
        return f"+{q}%"
    return f"{q}%"


def format_indicative_value(
    shares: Optional[Union[Decimal, int, float, str]],
    price: Optional[Union[Decimal, float, str]],
    currency: str = "USD",
) -> str:
    """Computes indicative market value = shares * price and formats in Billions/Millions."""
    d_shares = to_decimal(shares)
    d_price = to_decimal(price)

    if d_shares is None or d_price is None or d_shares <= 0 or d_price <= 0:
        return "—"

    val = d_shares * d_price
    prefix = "$" if currency == "USD" else f"{currency} "

    if val >= Decimal("1000000000"):
        scaled = (val / Decimal("1000000000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{prefix}{scaled}B"
    if val >= Decimal("1000000"):
        scaled = (val / Decimal("1000000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{prefix}{scaled}M"

    return f"{prefix}{val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,}"
