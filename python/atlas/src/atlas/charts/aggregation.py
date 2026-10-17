"""Canonical OHLCV Bar Aggregation Engine for ATLAS Charts (Stage 68).

Implements mathematical and temporal aggregation of lower-interval market bars into
verified higher-interval bars (e.g. 1m -> 5m, 1h -> 4h, 1d -> 1w, 1d -> 1M).

Strict Financial Data Integrity Invariants:
1. Open = first constituent bar's Open in the chronological window.
2. High = maximum High observed across all constituent bars.
3. Low = minimum Low observed across all constituent bars.
4. Close = last constituent bar's Close in the chronological window.
5. Volume = sum of constituent bar volumes ONLY IF all constituent bars have genuine volume.
   If any constituent bar has missing volume (None), aggregate volume is strictly None (never 0!).
6. Decimal arithmetic: No floating-point inaccuracies.
7. Negative price preservation: Supports valid negative futures prices (e.g. WTI Crude CLZ26).
8. Calendar boundaries: Grouping for weekly (ISO week) and monthly (calendar month) uses
   calendar-aware boundaries, never naive fixed-day counts.
9. Envelope preservation: High >= max(Open, Close, Low) and Low <= min(Open, Close, High).
"""

from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .config import ChartInterval
from .models import ChartBarDTO

# Fixed durations in seconds for intraday intervals
INTERVAL_DURATION_SECONDS: Dict[str, int] = {
    ChartInterval.ONE_MINUTE.value: 60,
    ChartInterval.FIVE_MINUTES.value: 300,
    ChartInterval.FIFTEEN_MINUTES.value: 900,
    ChartInterval.THIRTY_MINUTES.value: 1800,
    ChartInterval.ONE_HOUR.value: 3600,
    ChartInterval.FOUR_HOURS.value: 14400,
    ChartInterval.ONE_DAY.value: 86400,
}


def get_interval_duration_seconds(interval: str) -> Optional[int]:
    """Returns canonical nominal duration in seconds for an interval, or None if calendar-based."""
    code = interval.strip()
    if code == "1m":
        return 60
    if code == "1M" or code.lower() == "1mo":
        return None
    if code.lower() == "1w":
        return None
    if code.lower() == "1d":
        return 86400
    if code.lower() == "5m":
        return 300
    if code.lower() == "15m":
        return 900
    if code.lower() == "30m":
        return 1800
    if code.lower() == "1h":
        return 3600
    if code.lower() == "4h":
        return 14400
    return INTERVAL_DURATION_SECONDS.get(code)


def _get_bucket_key(bar: ChartBarDTO, target_interval: str) -> Tuple[int, datetime, str]:
    """Computes the target interval bucket identifier and start timestamp for a bar.

    Returns:
        (bucket_order_key, bucket_start_datetime, formatted_timestamp_string)
    """
    norm = target_interval.strip()
    dt = datetime.fromtimestamp(bar.time_unix, tz=timezone.utc)

    # 1. Weekly Aggregation (Calendar-aware ISO week grouping)
    if norm.lower() == "1w":
        # Group by (iso_year, iso_week)
        iso_year, iso_week, _ = dt.isocalendar()
        # Monday of the ISO week at 00:00:00 UTC
        monday_date = date.fromisocalendar(iso_year, iso_week, 1)
        bucket_dt = datetime.combine(monday_date, datetime.min.time(), tzinfo=timezone.utc)
        order_key = int(bucket_dt.timestamp())
        return order_key, bucket_dt, bucket_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 2. Monthly Aggregation (Calendar month grouping)
    if norm == "1M" or norm.lower() == "1mo":
        # First day of the calendar month at 00:00:00 UTC
        first_of_month = date(dt.year, dt.month, 1)
        bucket_dt = datetime.combine(first_of_month, datetime.min.time(), tzinfo=timezone.utc)
        order_key = int(bucket_dt.timestamp())
        return order_key, bucket_dt, bucket_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 3. Daily Aggregation
    if norm.lower() == "1d":
        day_date = dt.date()
        bucket_dt = datetime.combine(day_date, datetime.min.time(), tzinfo=timezone.utc)
        order_key = int(bucket_dt.timestamp())
        return order_key, bucket_dt, bucket_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 4. Intraday Fixed-Duration Aggregation (e.g. 1m, 5m, 15m, 30m, 1h, 4h)
    duration = get_interval_duration_seconds(norm) or 60
    bucket_unix = (bar.time_unix // duration) * duration
    bucket_dt = datetime.fromtimestamp(bucket_unix, tz=timezone.utc)
    return bucket_unix, bucket_dt, bucket_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def aggregate_ohlcv(
    bars: List[ChartBarDTO],
    target_interval: str,
    allows_negative_price: bool = False,
    current_time: Optional[datetime] = None,
) -> List[ChartBarDTO]:
    """Aggregates a chronological sequence of canonical bars into the target interval.

    Args:
        bars: Chronologically ordered constituent bars.
        target_interval: Target interval code ('5m', '15m', '30m', '1h', '4h', '1w', '1M').
        allows_negative_price: If True, negative settlement/close prices are legal (e.g. CLZ26).
        current_time: Optional reference UTC timestamp for determining bar finality.

    Returns:
        List of aggregated ChartBarDTO observations in chronological order.

    Raises:
        ValueError: If constituent bars are malformed or envelope invariant is violated.
    """
    if not bars:
        return []

    # Validate each constituent bar
    for b in bars:
        if b.high < b.low:
            raise ValueError(f"Envelope violation: Bar High ({b.high}) < Low ({b.low}).")
        if b.high < max(b.open, b.close):
            raise ValueError(
                f"Envelope violation: Bar High ({b.high}) must be >= max(Open, Close)."
            )
        if b.low > min(b.open, b.close):
            raise ValueError(f"Envelope violation: Bar Low ({b.low}) must be <= min(Open, Close).")
        if not allows_negative_price:
            if (
                b.low < Decimal("0")
                or b.open < Decimal("0")
                or b.close < Decimal("0")
                or b.high < Decimal("0")
            ):
                raise ValueError(
                    "Envelope violation: Negative price not permitted for this asset class."
                )

    norm_target = target_interval.strip()
    now_utc = current_time or datetime.now(timezone.utc)

    # Group bars into target buckets
    groups: Dict[int, List[ChartBarDTO]] = defaultdict(list)
    bucket_meta: Dict[int, Tuple[datetime, str]] = {}

    for bar in bars:
        order_key, bucket_dt, ts_str = _get_bucket_key(bar, norm_target)
        groups[order_key].append(bar)
        if order_key not in bucket_meta:
            bucket_meta[order_key] = (bucket_dt, ts_str)

    aggregated: List[ChartBarDTO] = []
    sorted_keys = sorted(groups.keys())

    for key in sorted_keys:
        bucket_bars = groups[key]
        bucket_dt, ts_str = bucket_meta[key]

        # Ensure constituent bars are sorted by timestamp
        bucket_bars.sort(key=lambda b: b.time_unix)

        # 1. Open: from first bar in interval
        open_val = bucket_bars[0].open

        # 2. Close: from last bar in interval
        close_val = bucket_bars[-1].close

        # 3. High: maximum High across constituent bars
        high_val = max(b.high for b in bucket_bars)

        # 4. Low: minimum Low across constituent bars
        low_val = min(b.low for b in bucket_bars)

        # 5. Volume: sum ONLY if all bars have non-null volume
        has_any_missing_volume = any(b.volume is None for b in bucket_bars)
        if has_any_missing_volume:
            aggregate_volume: Optional[Decimal] = None
        else:
            aggregate_volume = sum((b.volume for b in bucket_bars), Decimal("0"))

        # 6. Envelope invariant verification
        if high_val < max(open_val, close_val, low_val):
            raise ValueError(
                "Envelope violation: Aggregated High must be >= max(Open, Close, Low)."
            )
        if low_val > min(open_val, close_val, high_val):
            raise ValueError(
                "Envelope violation: Aggregated Low must be <= min(Open, Close, High)."
            )

        # Negative price protection
        if not allows_negative_price and (
            low_val < Decimal("0") or open_val < Decimal("0") or close_val < Decimal("0")
        ):
            raise ValueError(
                "Envelope violation: Negative price not permitted for this asset class."
            )

        # 7. Finality determination
        duration_sec = get_interval_duration_seconds(norm_target)
        if duration_sec:
            bucket_end_unix = key + duration_sec
        elif norm_target.lower() == "1w":
            bucket_end_unix = key + 7 * 86400
        else:
            # 1M
            bucket_end_unix = key + 31 * 86400
        is_final = bucket_end_unix <= int(now_utc.timestamp())

        agg_bar = ChartBarDTO(
            timestamp=ts_str,
            time_unix=key,
            open=open_val,
            high=high_val,
            low=low_val,
            close=close_val,
            volume=aggregate_volume,
            is_final=is_final,
        )
        aggregated.append(agg_bar)

    return aggregated
