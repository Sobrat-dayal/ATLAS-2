"""Deliverable specifications for options contracts (Stage 141).

Handles:
- Standard 100-share deliverables
- Exchange-specific lot sizes (e.g. NSE India 50/25/250 shares)
- Cash index deliverables
- Corporate-action adjusted deliverables (nonstandard share counts, mixed cash)
"""

from __future__ import annotations

from typing import Optional
from atlas.options.domain import DeliverableType, OptionDeliverable


def make_standard_equity_deliverable(symbol: str) -> OptionDeliverable:
    """Create a standard U.S. 100-share deliverable."""
    return OptionDeliverable(
        deliverable_type=DeliverableType.STANDARD_100_SHARES,
        shares_count=100.0,
        cash_amount=0.0,
        underlying_symbol=symbol.upper(),
        summary=f"100 shares of {symbol.upper()} common stock",
    )


def make_custom_lot_deliverable(symbol: str, lot_size: float) -> OptionDeliverable:
    """Create an exchange-specific custom lot deliverable (e.g. Indian NSE options)."""
    return OptionDeliverable(
        deliverable_type=DeliverableType.CUSTOM_LOT_SHARES,
        shares_count=float(lot_size),
        cash_amount=0.0,
        underlying_symbol=symbol.upper(),
        summary=f"{int(lot_size)} units of {symbol.upper()} under exchange lot rules",
    )


def make_cash_index_deliverable(index_symbol: str) -> OptionDeliverable:
    """Create a cash-settled index deliverable."""
    return OptionDeliverable(
        deliverable_type=DeliverableType.CASH_INDEX,
        shares_count=0.0,
        cash_amount=0.0,
        underlying_symbol=index_symbol.upper(),
        summary=f"Cash settlement based on official settlement value of {index_symbol.upper()}",
    )


def make_adjusted_deliverable(
    symbol: str,
    shares_count: float,
    cash_amount: float = 0.0,
    memo: Optional[str] = None,
) -> OptionDeliverable:
    """Create a nonstandard adjusted corporate-action deliverable."""
    summary_parts = []
    if shares_count > 0:
        summary_parts.append(f"{shares_count:g} shares of {symbol.upper()}")
    if cash_amount > 0:
        summary_parts.append(f"${cash_amount:,.2f} cash in lieu")

    summary_text = " + ".join(summary_parts)
    if memo:
        summary_text += f" ({memo})"

    return OptionDeliverable(
        deliverable_type=DeliverableType.NONSTANDARD_CASH_AND_SHARES,
        shares_count=float(shares_count),
        cash_amount=float(cash_amount),
        underlying_symbol=symbol.upper(),
        summary=summary_text,
    )
