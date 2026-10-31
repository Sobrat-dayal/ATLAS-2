"""Term Structure Builders for QuantLib (Stage 142)."""

from __future__ import annotations

from typing import Any, Dict, List
import QuantLib as ql
from atlas.options.quant.quantlib.dates import to_ql_date


def build_rate_term_structure(
    eval_date: ql.Date,
    rate: float,
    day_counter: ql.DayCounter | None = None,
) -> ql.YieldTermStructureHandle:
    """Build flat forward interest rate curve handle."""
    dc = day_counter or ql.Actual365Fixed()
    quote = ql.SimpleQuote(rate)
    ts = ql.FlatForward(eval_date, ql.QuoteHandle(quote), dc)
    return ql.YieldTermStructureHandle(ts)


def build_dividend_term_structure(
    eval_date: ql.Date,
    dividend_yield: float,
    day_counter: ql.DayCounter | None = None,
) -> ql.YieldTermStructureHandle:
    """Build flat forward dividend yield curve handle."""
    dc = day_counter or ql.Actual365Fixed()
    quote = ql.SimpleQuote(dividend_yield)
    ts = ql.FlatForward(eval_date, ql.QuoteHandle(quote), dc)
    return ql.YieldTermStructureHandle(ts)


def build_dividend_schedule(
    dividend_items: List[Dict[str, Any]],
) -> List[ql.FixedDividend]:
    """Convert list of discrete dividend dictionaries into QuantLib FixedDividend objects."""
    schedule: List[ql.FixedDividend] = []
    for item in dividend_items:
        date_val = item.get("date") or item.get("ex_date")
        amount = float(item.get("amount", 0.0))
        if date_val and amount > 0:
            ql_d = to_ql_date(date_val)
            schedule.append(ql.FixedDividend(amount, ql_d))
    return schedule


def build_volatility_term_structure(
    eval_date: ql.Date,
    volatility: float,
    day_counter: ql.DayCounter | None = None,
    calendar: ql.Calendar | None = None,
) -> ql.BlackVolTermStructureHandle:
    """Build constant Black volatility term structure handle."""
    dc = day_counter or ql.Actual365Fixed()
    cal = calendar or ql.NullCalendar()
    quote = ql.SimpleQuote(volatility)
    ts = ql.BlackConstantVol(eval_date, cal, ql.QuoteHandle(quote), dc)
    return ql.BlackVolTermStructureHandle(ts)


def build_bsm_process(
    eval_date: ql.Date,
    spot_price: float,
    risk_free_rate: float,
    dividend_yield: float,
    volatility: float,
) -> ql.BlackScholesMertonProcess:
    """Build unified BlackScholesMertonProcess from market inputs."""
    dc = ql.Actual365Fixed()
    cal = ql.NullCalendar()

    spot_quote = ql.SimpleQuote(spot_price)
    spot_handle = ql.QuoteHandle(spot_quote)

    rate_handle = build_rate_term_structure(eval_date, risk_free_rate, dc)
    div_handle = build_dividend_term_structure(eval_date, dividend_yield, dc)
    vol_handle = build_volatility_term_structure(eval_date, volatility, dc, cal)

    return ql.BlackScholesMertonProcess(spot_handle, div_handle, rate_handle, vol_handle)
