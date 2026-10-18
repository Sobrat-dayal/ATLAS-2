"""TA-Lib Indicator Adapter and Production Calculation Engine for ATLAS Charts (Stage 70).

Provides:
- TALibCapability: environment inspection, version verification, and function check.
- TALibIndicatorCalculator: extensible IndicatorCalculator adapter wrapping TA-Lib functions.
- Canonical Decimal -> float64 conversion boundary with strict finite checks.
- Genuine Volume qualification (never zero-fills missing volume).
- Multi-output support (MACD, Bollinger Bands, Stochastic).
- Deterministic lookback and explicit NaN-to-null warmup handling.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

try:
    import talib

    TALIB_AVAILABLE = True
    TALIB_VERSION = getattr(talib, "__version__", "unknown")
    try:
        raw_ta_ver = getattr(talib, "__ta_version__", b"unknown")
        TALIB_NATIVE_VERSION = (
            raw_ta_ver.decode("utf-8") if isinstance(raw_ta_ver, bytes) else str(raw_ta_ver)
        )
    except Exception:
        TALIB_NATIVE_VERSION = "unknown"
except ImportError:
    talib = None  # type: ignore
    TALIB_AVAILABLE = False
    TALIB_VERSION = "unavailable"
    TALIB_NATIVE_VERSION = "unavailable"

from ..models import ChartBarDTO
from .calculators.base import IndicatorCalculator
from .models import (
    IndicatorCalculationResult,
    IndicatorDefinition,
    IndicatorOutputSeries,
    IndicatorPoint,
    IndicatorStatus,
)

logger = logging.getLogger(__name__)


class TALibCapability:
    """Readiness inspector and metadata provider for TA-Lib native library integration."""

    @classmethod
    def is_available(cls) -> bool:
        return TALIB_AVAILABLE and talib is not None

    @classmethod
    def get_info(cls) -> Dict[str, Any]:
        return {
            "installed": TALIB_AVAILABLE,
            "wrapper_version": TALIB_VERSION,
            "native_version": TALIB_NATIVE_VERSION,
            "numpy_version": np.__version__,
            "functions_available": len(talib.get_functions()) if talib and hasattr(talib, "get_functions") else 0,
        }


def extract_finite_float_series(bars: List[ChartBarDTO], field: str) -> Tuple[np.ndarray, bool]:
    """Extract a named field from bars into a float64 numpy array.

    Returns:
        (array, has_all_valid)
    """
    arr = np.empty(len(bars), dtype=np.float64)
    has_valid = True

    for i, bar in enumerate(bars):
        val = getattr(bar, field, None)
        if val is None:
            arr[i] = np.nan
            has_valid = False
            continue

        try:
            fval = float(val)
            if np.isnan(fval) or np.isinf(fval):
                arr[i] = np.nan
                has_valid = False
            else:
                arr[i] = fval
        except (ValueError, TypeError):
            arr[i] = np.nan
            has_valid = False

    return arr, has_valid


class TALibIndicatorCalculator(IndicatorCalculator):
    """Production TA-Lib indicator adapter bridging ATLAS registry schemas to TA-Lib functions."""

    def __init__(
        self,
        definition: IndicatorDefinition,
        talib_func: Callable[..., Any],
        param_mapper: Callable[[Dict[str, Any]], Dict[str, Any]],
        lookback_calc: Callable[[Dict[str, Any]], int],
        output_mapper: Callable[
            [Any, List[ChartBarDTO], Dict[str, Any]], List[IndicatorOutputSeries]
        ],
        requires_volume: bool = False,
    ) -> None:
        self._definition = definition
        self._talib_func = talib_func
        self._param_mapper = param_mapper
        self._lookback_calc = lookback_calc
        self._output_mapper = output_mapper
        self._requires_volume = requires_volume

    @property
    def definition(self) -> IndicatorDefinition:
        return self._definition

    def get_required_lookback(self, params: Dict[str, Any]) -> int:
        return self._lookback_calc(params)

    def calculate(
        self,
        instance_id: str,
        bars: List[ChartBarDTO],
        params: Dict[str, Any],
        requested_start: Optional[datetime] = None,
        requested_end: Optional[datetime] = None,
    ) -> IndicatorCalculationResult:
        if not TALIB_AVAILABLE or talib is None:
            return IndicatorCalculationResult(
                instance_id=instance_id,
                indicator_id=self.definition.indicator_id,
                version=self.definition.version,
                parameters=params,
                rendering_target=self.definition.rendering_target,
                status=IndicatorStatus.TALIB_UNAVAILABLE,
                error_message=(
                    "TA-Lib native calculation library is not available in backend environment."
                ),
                required_lookback_bars=self.get_required_lookback(params),
                series=[],
            )

        if not bars:
            return IndicatorCalculationResult(
                instance_id=instance_id,
                indicator_id=self.definition.indicator_id,
                version=self.definition.version,
                parameters=params,
                rendering_target=self.definition.rendering_target,
                status=IndicatorStatus.INSUFFICIENT_HISTORY,
                error_message="No historical bars provided for indicator calculation.",
                required_lookback_bars=self.get_required_lookback(params),
                series=[],
            )

        lookback = self.get_required_lookback(params)
        if len(bars) < max(2, lookback):
            return IndicatorCalculationResult(
                instance_id=instance_id,
                indicator_id=self.definition.indicator_id,
                version=self.definition.version,
                parameters=params,
                rendering_target=self.definition.rendering_target,
                status=IndicatorStatus.INSUFFICIENT_HISTORY,
                error_message=(
                    f"Insufficient historical bars: received {len(bars)} bars, but indicator "
                    f"requires at least {lookback} bars for warmup."
                ),
                required_lookback_bars=lookback,
                series=[],
            )

        # Volume validation: never fabricate volume
        if self._requires_volume or "volume" in self.definition.input_requirements:
            has_genuine_volume = any(
                bar.volume is not None and float(bar.volume) > 0 for bar in bars
            )
            if not has_genuine_volume:
                return IndicatorCalculationResult(
                    instance_id=instance_id,
                    indicator_id=self.definition.indicator_id,
                    version=self.definition.version,
                    parameters=params,
                    rendering_target=self.definition.rendering_target,
                    status=IndicatorStatus.MISSING_VOLUME,
                    error_message=(
                        f"Indicator '{self.definition.indicator_id}' requires genuine volume, "
                        "which is unavailable or unpopulated for this financial instrument."
                    ),
                    required_lookback_bars=lookback,
                    series=[],
                )

        # Extract required numerical inputs
        close_arr, _ = extract_finite_float_series(bars, "close")
        high_arr, _ = extract_finite_float_series(bars, "high")
        low_arr, _ = extract_finite_float_series(bars, "low")
        open_arr, _ = extract_finite_float_series(bars, "open")
        vol_arr, _ = extract_finite_float_series(bars, "volume")

        # Map parameters to TA-Lib kwargs
        mapped_kwargs = self._param_mapper(params)

        # Execute TA-Lib calculation
        try:
            req_inputs = self.definition.input_requirements
            if req_inputs == ["close"]:
                raw_out = self._talib_func(close_arr, **mapped_kwargs)
            elif req_inputs == ["high", "low", "close"]:
                raw_out = self._talib_func(high_arr, low_arr, close_arr, **mapped_kwargs)
            elif req_inputs == ["close", "volume"]:
                raw_out = self._talib_func(close_arr, vol_arr, **mapped_kwargs)
            elif req_inputs == ["high", "low", "close", "volume"]:
                raw_out = self._talib_func(high_arr, low_arr, close_arr, vol_arr, **mapped_kwargs)
            elif req_inputs == ["open", "high", "low", "close"]:
                raw_out = self._talib_func(open_arr, high_arr, low_arr, close_arr, **mapped_kwargs)
            else:
                raw_out = self._talib_func(close_arr, **mapped_kwargs)

            # Map raw TA-Lib outputs to IndicatorOutputSeries
            series_list = self._output_mapper(raw_out, bars, params)

            return IndicatorCalculationResult(
                instance_id=instance_id,
                indicator_id=self.definition.indicator_id,
                version=self.definition.version,
                parameters=params,
                rendering_target=self.definition.rendering_target,
                status=IndicatorStatus.READY,
                required_lookback_bars=lookback,
                series=series_list,
            )
        except Exception as e:
            logger.error(
                f"TA-Lib execution failed for '{self.definition.indicator_id}': {e}", exc_info=True
            )
            return IndicatorCalculationResult(
                instance_id=instance_id,
                indicator_id=self.definition.indicator_id,
                version=self.definition.version,
                parameters=params,
                rendering_target=self.definition.rendering_target,
                status=IndicatorStatus.CALCULATION_ERROR,
                error_message=f"TA-Lib calculation error: {str(e)}",
                required_lookback_bars=lookback,
                series=[],
            )


# ---------------------------------------------------------------------------
# Helper output mappers for 1-output, 2-output, and 3-output indicators
# ---------------------------------------------------------------------------


def make_single_line_output_mapper(
    series_id: str,
    series_name: str,
    rendering_type: str = "LINE",
    unit: str = "price",
    color: Optional[str] = None,
):
    def mapper(raw_out: np.ndarray, bars: List[ChartBarDTO], params: Dict[str, Any]):
        points: List[IndicatorPoint] = []
        for i, bar in enumerate(bars):
            val = raw_out[i]
            if np.isnan(val) or np.isinf(val):
                points.append(
                    IndicatorPoint(
                        timestamp=bar.timestamp,
                        time_unix=bar.time_unix,
                        value=None,
                        status=IndicatorStatus.WARMUP,
                    )
                )
            else:
                points.append(
                    IndicatorPoint(
                        timestamp=bar.timestamp,
                        time_unix=bar.time_unix,
                        value=round(float(val), 6),
                        status=IndicatorStatus.READY,
                    )
                )
        return [
            IndicatorOutputSeries(
                series_id=series_id,
                name=series_name,
                rendering_type=rendering_type,
                unit=unit,
                color=color,
                points=points,
            )
        ]

    return mapper


def make_macd_output_mapper():
    def mapper(
        raw_out: Tuple[np.ndarray, np.ndarray, np.ndarray],
        bars: List[ChartBarDTO],
        params: Dict[str, Any],
    ):
        macd_arr, signal_arr, hist_arr = raw_out
        macd_pts: List[IndicatorPoint] = []
        sig_pts: List[IndicatorPoint] = []
        hist_pts: List[IndicatorPoint] = []

        for i, bar in enumerate(bars):
            m_val = macd_arr[i]
            s_val = signal_arr[i]
            h_val = hist_arr[i]

            macd_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(m_val) or np.isinf(m_val) else round(float(m_val), 6),
                    status=IndicatorStatus.WARMUP if np.isnan(m_val) else IndicatorStatus.READY,
                )
            )
            sig_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(s_val) or np.isinf(s_val) else round(float(s_val), 6),
                    status=IndicatorStatus.WARMUP if np.isnan(s_val) else IndicatorStatus.READY,
                )
            )
            hist_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(h_val) or np.isinf(h_val) else round(float(h_val), 6),
                    status=IndicatorStatus.WARMUP if np.isnan(h_val) else IndicatorStatus.READY,
                )
            )

        return [
            IndicatorOutputSeries(
                series_id="macd",
                name="MACD Line",
                rendering_type="LINE",
                unit="difference",
                color="#38bdf8",
                points=macd_pts,
            ),
            IndicatorOutputSeries(
                series_id="signal",
                name="Signal Line",
                rendering_type="LINE",
                unit="difference",
                color="#f59e0b",
                points=sig_pts,
            ),
            IndicatorOutputSeries(
                series_id="histogram",
                name="Histogram",
                rendering_type="HISTOGRAM",
                unit="difference",
                color="#10b981",
                points=hist_pts,
            ),
        ]

    return mapper


def make_bbands_output_mapper():
    def mapper(
        raw_out: Tuple[np.ndarray, np.ndarray, np.ndarray],
        bars: List[ChartBarDTO],
        params: Dict[str, Any],
    ):
        upper_arr, middle_arr, lower_arr = raw_out
        up_pts: List[IndicatorPoint] = []
        mid_pts: List[IndicatorPoint] = []
        low_pts: List[IndicatorPoint] = []

        for i, bar in enumerate(bars):
            u_val = upper_arr[i]
            m_val = middle_arr[i]
            l_val = lower_arr[i]

            up_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(u_val) or np.isinf(u_val) else round(float(u_val), 6),
                    status=IndicatorStatus.WARMUP if np.isnan(u_val) else IndicatorStatus.READY,
                )
            )
            mid_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(m_val) or np.isinf(m_val) else round(float(m_val), 6),
                    status=IndicatorStatus.WARMUP if np.isnan(m_val) else IndicatorStatus.READY,
                )
            )
            low_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(l_val) or np.isinf(l_val) else round(float(l_val), 6),
                    status=IndicatorStatus.WARMUP if np.isnan(l_val) else IndicatorStatus.READY,
                )
            )

        return [
            IndicatorOutputSeries(
                series_id="upper",
                name="Upper Band",
                rendering_type="LINE",
                unit="price",
                color="#38bdf8",
                points=up_pts,
            ),
            IndicatorOutputSeries(
                series_id="middle",
                name="Middle Band",
                rendering_type="LINE",
                unit="price",
                color="#a1a1aa",
                points=mid_pts,
            ),
            IndicatorOutputSeries(
                series_id="lower",
                name="Lower Band",
                rendering_type="LINE",
                unit="price",
                color="#38bdf8",
                points=low_pts,
            ),
        ]

    return mapper


def make_stoch_output_mapper():
    def mapper(
        raw_out: Tuple[np.ndarray, np.ndarray], bars: List[ChartBarDTO], params: Dict[str, Any]
    ):
        slowk_arr, slowd_arr = raw_out
        k_pts: List[IndicatorPoint] = []
        d_pts: List[IndicatorPoint] = []

        for i, bar in enumerate(bars):
            k_val = slowk_arr[i]
            d_val = slowd_arr[i]

            k_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(k_val) or np.isinf(k_val) else round(float(k_val), 4),
                    status=IndicatorStatus.WARMUP if np.isnan(k_val) else IndicatorStatus.READY,
                )
            )
            d_pts.append(
                IndicatorPoint(
                    timestamp=bar.timestamp,
                    time_unix=bar.time_unix,
                    value=None if np.isnan(d_val) or np.isinf(d_val) else round(float(d_val), 4),
                    status=IndicatorStatus.WARMUP if np.isnan(d_val) else IndicatorStatus.READY,
                )
            )

        return [
            IndicatorOutputSeries(
                series_id="slowk",
                name="%K (Slow)",
                rendering_type="LINE",
                unit="points",
                color="#38bdf8",
                points=k_pts,
            ),
            IndicatorOutputSeries(
                series_id="slowd",
                name="%D (Slow)",
                rendering_type="LINE",
                unit="points",
                color="#f59e0b",
                points=d_pts,
            ),
        ]

    return mapper
