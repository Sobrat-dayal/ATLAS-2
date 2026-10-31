"""Historical OHLCV Bar Normalization and Point-in-Time Availability (Stage 143)."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Price, Quantity

from atlas.trading.backtesting.domain import DataGranularity
from atlas.trading.backtesting.errors import BacktestLookAheadError


def date_str_to_ns(date_str: str, hour: int = 20, minute: int = 0) -> int:
    """Convert YYYY-MM-DD string to epoch nanoseconds at standard daily close."""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(
        hour=hour, minute=minute, second=0, tzinfo=datetime.timezone.utc
    )
    return int(dt.timestamp() * 1_000_000_000)


def build_nautilus_bars(
    raw_bars: List[Dict[str, Any]],
    instrument_id_str: str,
    granularity: DataGranularity = DataGranularity.BARS_1D,
) -> List[Bar]:
    """
    Convert dictionary of historical bar observations into validated Nautilus Bar objects.
    Enforces point-in-time correctness: bars are ordered chronologically and timestamps
    reflect completed intervals to prevent same-bar future look-ahead.
    """
    if not raw_bars:
        return []

    # Format bar type specifier string
    granularity_map = {
        DataGranularity.BARS_1D: "1-DAY-LAST-EXTERNAL",
        DataGranularity.BARS_1H: "1-HOUR-LAST-EXTERNAL",
        DataGranularity.BARS_1M: "1-MINUTE-LAST-EXTERNAL",
    }
    spec_str = granularity_map.get(granularity, "1-DAY-LAST-EXTERNAL")
    bar_type = BarType.from_str(f"{instrument_id_str}-{spec_str}")

    nautilus_bars: List[Bar] = []
    last_ts = -1

    for item in raw_bars:
        date_val = item["date"]
        # Handle string or timestamp
        if isinstance(date_val, str):
            ts_ns = date_str_to_ns(date_val)
        else:
            ts_ns = int(date_val)

        # Temporal integrity: timestamps must be strictly non-decreasing
        if ts_ns < last_ts:
            raise BacktestLookAheadError(
                f"Out-of-order historical bar detected: {ts_ns} < previous {last_ts}."
            )
        last_ts = ts_ns

        o = float(item["open"])
        h = float(item["high"])
        l = float(item["low"])
        c = float(item["close"])
        v = float(item.get("volume", 1000))

        bar = Bar(
            bar_type=bar_type,
            open=Price.from_str(f"{o:.2f}"),
            high=Price.from_str(f"{h:.2f}"),
            low=Price.from_str(f"{l:.2f}"),
            close=Price.from_str(f"{c:.2f}"),
            volume=Quantity.from_int(int(v)),
            ts_event=ts_ns,
            ts_init=ts_ns,
        )
        nautilus_bars.append(bar)

    return nautilus_bars


def verify_no_look_ahead_access(
    current_time_ns: int,
    target_bar: Bar,
) -> None:
    """Validate that strategy logic is not attempting to access bar data prior to bar completion."""
    if current_time_ns < target_bar.ts_event:
        raise BacktestLookAheadError(
            f"Strategy attempted to access bar timestamp {target_bar.ts_event} "
            f"before bar completion time {current_time_ns}."
        )
