"""Moneyness, Intrinsic Value, Extrinsic Value and DTE Analytics (Stage 141).

Mathematical formulas for standard vanilla equity/ETF options:
- Call Intrinsic = max(S - K, 0)
- Put Intrinsic = max(K - S, 0)
- Extrinsic Value = Option Premium - Intrinsic Value
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from atlas.options.domain import MoneynessState, OptionType


def calculate_intrinsic_value(underlying_price: float, strike_price: float, option_type: OptionType) -> float:
    """Calculate deterministic intrinsic value per contract unit for standard vanilla options."""
    if option_type == OptionType.CALL:
        return max(0.0, round(underlying_price - strike_price, 4))
    else:
        return max(0.0, round(strike_price - underlying_price, 4))


def calculate_extrinsic_value(
    premium: float,
    underlying_price: float,
    strike_price: float,
    option_type: OptionType,
) -> float:
    """Calculate extrinsic (time) value per contract unit."""
    intrinsic = calculate_intrinsic_value(underlying_price, strike_price, option_type)
    return max(0.0, round(premium - intrinsic, 4))


def calculate_days_to_expiration(expiration_date_str: str, as_of: Optional[datetime] = None) -> int:
    """Calculate calendar days to expiration."""
    exp_dt = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
    ref_dt = (as_of or datetime.now(timezone.utc)).date()
    return max(0, (exp_dt - ref_dt).days)
