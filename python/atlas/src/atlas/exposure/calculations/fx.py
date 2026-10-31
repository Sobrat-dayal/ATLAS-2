"""Point-in-time Foreign Exchange Conversion Engine (Stage 137).

Enforces institutional FX invariants:
- Conversions MUST use historical point-in-time rates matching the financial reporting or market data date.
- Explicit quote direction verification (EUR/USD vs USD/EUR).
- If historical rate is missing, raises MissingCurrencyRateError. Substituting current rates is strictly prohibited.
- Exact Decimal precision.
"""

from __future__ import annotations
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Dict, Optional, Tuple
from atlas.exposure.errors import MissingCurrencyRateError, CurrencyMismatchError

# Point-in-time rate registry: (from_currency, to_currency, as_of_date_str) -> rate
# Example: ("EUR", "USD", "2024-12-31") -> Decimal("1.1000") means 1 EUR = 1.1000 USD
KNOWN_HISTORICAL_FX_RATES: Dict[Tuple[str, str, str], Decimal] = {
    ("EUR", "USD", "2024-12-31"): Decimal("1.1000"),
    ("USD", "EUR", "2024-12-31"): Decimal("0.909090909"),
    ("GBP", "USD", "2024-12-31"): Decimal("1.2700"),
    ("USD", "JPY", "2024-12-31"): Decimal("155.00"),
    ("JPY", "USD", "2024-12-31"): Decimal("0.006451613"),
    ("EUR", "USD", "2023-12-31"): Decimal("1.0800"),
    ("GBP", "USD", "2023-12-31"): Decimal("1.2500"),
}


def convert_currency_point_in_time(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    as_of_date: str,
    custom_rate_table: Optional[Dict[Tuple[str, str, str], Decimal]] = None
) -> Tuple[Decimal, Decimal]:
    """Convert an amount from from_currency to to_currency as of a specific date.
    
    Returns:
        Tuple[converted_amount, applied_rate]
    
    Raises:
        MissingCurrencyRateError: If no point-in-time rate is found.
    """
    if from_currency.upper() == to_currency.upper():
        return amount, Decimal("1.0")

    rates = custom_rate_table if custom_rate_table is not None else KNOWN_HISTORICAL_FX_RATES

    # Check direct quote: 1 from_currency = R to_currency
    key_direct = (from_currency.upper(), to_currency.upper(), as_of_date)
    if key_direct in rates:
        rate = rates[key_direct]
        converted = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        return converted, rate

    # Check inverse quote: 1 to_currency = R from_currency
    key_inverse = (to_currency.upper(), from_currency.upper(), as_of_date)
    if key_inverse in rates:
        inv_rate = rates[key_inverse]
        if inv_rate == Decimal("0"):
            raise CurrencyMismatchError(f"Zero inverse FX rate found for {key_inverse}")
        rate = Decimal("1.0") / inv_rate
        converted = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        return converted, rate

    # Invariant: Never fabricate or substitute a current rate for a missing historical rate
    raise MissingCurrencyRateError(
        from_currency=from_currency.upper(),
        to_currency=to_currency.upper(),
        as_of=as_of_date
    )

