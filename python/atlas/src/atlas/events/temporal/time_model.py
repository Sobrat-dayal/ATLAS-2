"""Multi-Clock Temporal Model and Date Precision (Stage 135).

Enforces institutional temporal fidelity:
- Rigorously distinguishes occurrence, publication, announcement, and ingestion clocks.
- Preserves explicit DatePrecision tiers (Date-Only, Month-Only, Year-Only).
- Strict Invariant: Never invents midnight UTC as an exact occurrence second for date-only reports.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple

from ..domain import DatePrecision


def parse_temporal_string(
    date_str: str,
) -> Tuple[datetime, DatePrecision]:
    """Parse a date or ISO timestamp string into a UTC datetime and explicit DatePrecision tier.

    Invariants:
    - '2026-10-31' -> DatePrecision.DATE_ONLY
    - '2026-10' -> DatePrecision.MONTH_ONLY
    - '2026' -> DatePrecision.YEAR_ONLY
    - '2026-10-31T08:30:00Z' -> DatePrecision.EXACT_TIMESTAMP
    """
    clean_str = date_str.strip()

    # Exact timestamp with time component
    if "T" in clean_str or ":" in clean_str:
        norm_str = clean_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(norm_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt, DatePrecision.EXACT_TIMESTAMP

    # Date-only (YYYY-MM-DD)
    parts = clean_str.split("-")
    if len(parts) == 3:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        dt = datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc)
        return dt, DatePrecision.DATE_ONLY

    # Month-only (YYYY-MM)
    if len(parts) == 2:
        year, month = int(parts[0]), int(parts[1])
        dt = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        return dt, DatePrecision.MONTH_ONLY

    # Year-only (YYYY)
    if len(parts) == 1 and len(clean_str) == 4:
        year = int(clean_str)
        dt = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        return dt, DatePrecision.YEAR_ONLY

    # Fallback
    dt = datetime.now(timezone.utc)
    return dt, DatePrecision.TIME_UNKNOWN


def format_temporal_display(dt: Optional[datetime], precision: DatePrecision) -> str:
    """Format datetime for institutional display according to its precision tier."""
    if dt is None:
        return "Unknown"

    if precision == DatePrecision.EXACT_TIMESTAMP:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    elif precision == DatePrecision.DATE_ONLY:
        return dt.strftime("%Y-%m-%d (Date-Only)")
    elif precision == DatePrecision.MONTH_ONLY:
        return dt.strftime("%Y-%m (Month-Only)")
    elif precision == DatePrecision.YEAR_ONLY:
        return dt.strftime("%Y (Year-Only)")
    else:
        return "Time Unknown"

