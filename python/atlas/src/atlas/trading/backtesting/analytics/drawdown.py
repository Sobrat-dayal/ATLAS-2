"""Peak-to-Trough Drawdown Analysis Engine (Stage 143)."""

from __future__ import annotations

from typing import List, Tuple
from atlas.trading.backtesting.domain import DrawdownMetrics, EquitySnapshot


class DrawdownEngine:
    """Calculates running peak equity, drawdown time series, and maximum drawdown metrics."""

    @staticmethod
    def compute_drawdowns(
        equity_series: List[Tuple[str, float]],
    ) -> Tuple[List[float], DrawdownMetrics]:
        """
        Compute percentage drawdowns across an equity series.
        Returns: (drawdowns_pct_series, DrawdownMetrics).
        """
        if not equity_series:
            return [], DrawdownMetrics()

        drawdowns_pct: List[float] = []
        running_peak = -float("inf")
        peak_ts = equity_series[0][0]
        max_dd_dollar = 0.0
        max_dd_pct = 0.0
        max_dd_peak_ts = peak_ts
        max_dd_trough_ts = peak_ts

        # Tracking duration
        cur_dd_duration_points = 0
        max_dd_duration_points = 0

        for ts, eq in equity_series:
            if eq > running_peak:
                running_peak = eq
                peak_ts = ts
                cur_dd_duration_points = 0
            else:
                cur_dd_duration_points += 1

            dd_dollar = running_peak - eq
            dd_pct = (dd_dollar / running_peak * 100.0) if running_peak > 0 else 0.0
            drawdowns_pct.append(round(dd_pct, 4))

            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct
                max_dd_dollar = dd_dollar
                max_dd_peak_ts = peak_ts
                max_dd_trough_ts = ts

            if cur_dd_duration_points > max_dd_duration_points:
                max_dd_duration_points = cur_dd_duration_points

        metrics = DrawdownMetrics(
            max_drawdown_dollar=round(max_dd_dollar, 2),
            max_drawdown_pct=round(max_dd_pct, 2),
            max_drawdown_duration_days=float(max_dd_duration_points),
            peak_timestamp=max_dd_peak_ts,
            trough_timestamp=max_dd_trough_ts,
            recovery_timestamp=equity_series[-1][0] if max_dd_pct == 0 else None,
            is_recovered=(drawdowns_pct[-1] == 0.0),
        )

        return drawdowns_pct, metrics
