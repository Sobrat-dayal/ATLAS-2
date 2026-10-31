"""Date Conversion Utilities for QuantLib (Stage 142)."""

from __future__ import annotations

from datetime import date, datetime
import QuantLib as ql
from atlas.options.quant.errors import QuantEvaluationDateError


def to_ql_date(d: date | datetime | str) -> ql.Date:
    """Convert a Python date, datetime, or ISO string (YYYY-MM-DD) into a QuantLib Date object."""
    if isinstance(d, str):
        try:
            dt = datetime.strptime(d[:10], "%Y-%m-%d").date()
        except ValueError as e:
            raise QuantEvaluationDateError(f"Invalid date format '{d}'. Expected 'YYYY-MM-DD'.") from e
    elif isinstance(d, datetime):
        dt = d.date()
    elif isinstance(d, date):
        dt = d
    else:
        raise QuantEvaluationDateError(f"Unsupported date type: {type(d)}")

    return ql.Date(dt.day, dt.month, dt.year)


def from_ql_date(ql_d: ql.Date) -> str:
    """Convert a QuantLib Date object into an ISO string (YYYY-MM-DD)."""
    return f"{ql_d.year():04d}-{ql_d.month():02d}-{ql_d.dayOfMonth():02d}"


def get_actual365_year_fraction(start_d: ql.Date, end_d: ql.Date) -> float:
    """Compute year fraction using Actual/365 Fixed convention."""
    dc = ql.Actual365Fixed()
    return dc.yearFraction(start_d, end_d)

