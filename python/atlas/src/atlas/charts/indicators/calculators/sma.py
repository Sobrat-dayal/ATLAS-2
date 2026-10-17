"""Simple Moving Average (SMA) reference calculator implementation (Stage 69).

Computes the unweighted arithmetic mean of the previous N qualified Close observations:
    SMA_t = (1 / N) * sum_{i=0}^{N-1} Close_{t-i}

Enforces:
- Deterministic O(N) rolling arithmetic with Decimal precision.
- First N-1 bars marked as WARMUP with value=None (never 0!).
- INSUFFICIENT_HISTORY when total available bars < N.
- DATA_GAP if any constituent Close price in window is None.
- Exact time alignment with canonical bar timestamps.
- Zero look-ahead: point at T depends strictly on bars <= T.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from ...models import ChartBarDTO
from ..models import (
    IndicatorCalculationResult,
    IndicatorCategory,
    IndicatorDefinition,
    IndicatorOutputSeries,
    IndicatorParameterDefinition,
    IndicatorParameterType,
    IndicatorPoint,
    IndicatorRenderingTarget,
    IndicatorStatus,
)
from .base import IndicatorCalculator


class SmaCalculator(IndicatorCalculator):
    """Reference implementation of Simple Moving Average (atlas.sma)."""

    def __init__(self) -> None:
        self._definition = IndicatorDefinition(
            indicator_id="atlas.sma",
            version=1,
            display_name="Simple Moving Average",
            description=(
                "Calculates the unweighted arithmetic mean of the previous "
                "N qualified Close observations."
            ),
            category=IndicatorCategory.TREND,
            rendering_target=IndicatorRenderingTarget.PRICE_OVERLAY,
            input_requirements=["close"],
            parameters=[
                IndicatorParameterDefinition(
                    name="period",
                    type=IndicatorParameterType.INTEGER,
                    default=20,
                    required=True,
                    min_value=2,
                    max_value=500,
                    description="Number of constituent bars in rolling window (2-500)",
                ),
                IndicatorParameterDefinition(
                    name="source",
                    type=IndicatorParameterType.STRING,
                    default="close",
                    required=False,
                    allowed_values=["close"],
                    description="Price field used for calculation (Close)",
                ),
            ],
            default_color="#38bdf8",
            default_line_width=2,
            supported_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
            min_history_bars=2,
        )

    @property
    def definition(self) -> IndicatorDefinition:
        return self._definition

    def get_required_lookback(self, params: Dict[str, Any]) -> int:
        norm_params = self.validate_parameters(params)
        return int(norm_params["period"])

    def calculate(
        self,
        instance_id: str,
        bars: List[ChartBarDTO],
        params: Dict[str, Any],
        requested_start: Optional[datetime] = None,
        requested_end: Optional[datetime] = None,
    ) -> IndicatorCalculationResult:
        norm_params = self.validate_parameters(params)
        period = int(norm_params["period"])

        if len(bars) == 0:
            return IndicatorCalculationResult(
                instance_id=instance_id,
                indicator_id=self.definition.indicator_id,
                version=self.definition.version,
                parameters=norm_params,
                rendering_target=self.definition.rendering_target,
                status=IndicatorStatus.INSUFFICIENT_HISTORY,
                error_message="No historical bars available for calculation.",
                required_lookback_bars=period,
                series=[],
            )

        # Ensure bars are chronologically ordered
        sorted_bars = sorted(bars, key=lambda b: b.time_unix)

        if len(sorted_bars) < period:
            # Insufficient history to calculate even a single valid SMA point
            insufficient_points: List[IndicatorPoint] = [
                IndicatorPoint(
                    timestamp=b.timestamp,
                    time_unix=b.time_unix,
                    value=None,
                    status=IndicatorStatus.INSUFFICIENT_HISTORY,
                )
                for b in sorted_bars
            ]
            return IndicatorCalculationResult(
                instance_id=instance_id,
                indicator_id=self.definition.indicator_id,
                version=self.definition.version,
                parameters=norm_params,
                rendering_target=self.definition.rendering_target,
                status=IndicatorStatus.INSUFFICIENT_HISTORY,
                error_message=(
                    f"Insufficient history: requested period is {period}, but only "
                    f"{len(sorted_bars)} bars were provided."
                ),
                required_lookback_bars=period,
                series=[
                    IndicatorOutputSeries(
                        series_id="main",
                        name=f"SMA ({period})",
                        rendering_type="LINE",
                        color=norm_params.get("color") or self.definition.default_color,
                        line_width=norm_params.get("line_width")
                        or self.definition.default_line_width,
                        points=insufficient_points,
                    )
                ],
            )

        # O(N) rolling calculation with Decimal precision
        all_points: List[IndicatorPoint] = []
        d_period = Decimal(period)

        # Pre-extract Close prices as Decimal or None
        close_decimals: List[Optional[Decimal]] = []
        for b in sorted_bars:
            if b.close is None:
                close_decimals.append(None)
            else:
                try:
                    close_decimals.append(Decimal(str(b.close)))
                except Exception:
                    close_decimals.append(None)

        current_window_sum = Decimal(0)
        gap_count_in_window = 0

        for i in range(len(sorted_bars)):
            bar = sorted_bars[i]
            val = close_decimals[i]

            if val is None:
                gap_count_in_window += 1
            else:
                current_window_sum += val

            # If window exceeds period, subtract outgoing bar
            if i >= period:
                outgoing_val = close_decimals[i - period]
                if outgoing_val is None:
                    gap_count_in_window -= 1
                else:
                    current_window_sum -= outgoing_val

            if i < period - 1:
                # Still in warmup window
                all_points.append(
                    IndicatorPoint(
                        timestamp=bar.timestamp,
                        time_unix=bar.time_unix,
                        value=None,
                        status=IndicatorStatus.WARMUP,
                    )
                )
            else:
                if gap_count_in_window > 0:
                    # Missing price within current rolling window
                    all_points.append(
                        IndicatorPoint(
                            timestamp=bar.timestamp,
                            time_unix=bar.time_unix,
                            value=None,
                            status=IndicatorStatus.DATA_GAP,
                        )
                    )
                else:
                    sma_val = float(current_window_sum / d_period)
                    all_points.append(
                        IndicatorPoint(
                            timestamp=bar.timestamp,
                            time_unix=bar.time_unix,
                            value=sma_val,
                            status=IndicatorStatus.READY,
                        )
                    )

        # Align to requested window if specified
        output_points = all_points
        if requested_start is not None or requested_end is not None:
            filtered: List[IndicatorPoint] = []
            for pt in all_points:
                pt_dt = datetime.fromtimestamp(pt.time_unix, tz=timezone.utc)
                if requested_start is not None and pt_dt < requested_start:
                    continue
                if requested_end is not None and pt_dt >= requested_end:
                    continue
                filtered.append(pt)
            output_points = filtered

        return IndicatorCalculationResult(
            instance_id=instance_id,
            indicator_id=self.definition.indicator_id,
            version=self.definition.version,
            parameters=norm_params,
            rendering_target=self.definition.rendering_target,
            status=IndicatorStatus.READY,
            error_message=None,
            required_lookback_bars=period,
            series=[
                IndicatorOutputSeries(
                    series_id="main",
                    name=f"SMA ({period})",
                    rendering_type="LINE",
                    color=norm_params.get("color") or self.definition.default_color,
                    line_width=norm_params.get("line_width") or self.definition.default_line_width,
                    points=output_points,
                )
            ],
        )
