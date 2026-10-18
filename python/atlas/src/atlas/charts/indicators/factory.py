"""Production Technical Indicator Definitions for ATLAS Charts (Stage 70).

Provides verified indicator definitions and TA-Lib calculators for:
1. atlas.sma (Reference native Stage 69 calculator)
2. atlas.ema (TA-Lib Exponential Moving Average)
3. atlas.wma (TA-Lib Weighted Moving Average)
4. atlas.rsi (TA-Lib Relative Strength Index)
5. atlas.macd (TA-Lib Moving Average Convergence Divergence)
6. atlas.bbands (TA-Lib Bollinger Bands)
7. atlas.atr (TA-Lib Average True Range)
8. atlas.stoch (TA-Lib Stochastic Oscillator)
9. atlas.adx (TA-Lib Average Directional Index)
10. atlas.cci (TA-Lib Commodity Channel Index)
11. atlas.roc (TA-Lib Rate of Change Percentage)
12. atlas.mom (TA-Lib Momentum Price Difference)
13. atlas.obv (TA-Lib On-Balance Volume)
14. atlas.mfi (TA-Lib Money Flow Index)
"""

from typing import Any, Dict, List

from .calculators.base import IndicatorCalculator
from .calculators.sma import SmaCalculator
from .models import (
    IndicatorCategory,
    IndicatorDefinition,
    IndicatorParameterDefinition,
    IndicatorParameterType,
    IndicatorRenderingTarget,
)
from .talib_adapter import (
    TALibIndicatorCalculator,
    make_bbands_output_mapper,
    make_macd_output_mapper,
    make_single_line_output_mapper,
    make_stoch_output_mapper,
    talib,
)


def create_ema_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.ema",
        version=1,
        display_name="Exponential Moving Average",
        description="Exponentially smoothed moving average giving greater weight to recent prices.",
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
                description="Lookback smoothing period",
            )
        ],
        default_color="#38bdf8",
        default_line_width=2,
        min_history_bars=2,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.EMA if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 20))},
        lookback_calc=lambda p: int(p.get("period", 20)),
        output_mapper=make_single_line_output_mapper(
            "main", "EMA", "LINE", "price", defn.default_color
        ),
    )


def create_wma_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.wma",
        version=1,
        display_name="Weighted Moving Average",
        description="Weighted moving average assigning linear weight proportional to recency.",
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
                description="Lookback weighting period",
            )
        ],
        default_color="#a855f7",
        default_line_width=2,
        min_history_bars=2,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.WMA if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 20))},
        lookback_calc=lambda p: int(p.get("period", 20)),
        output_mapper=make_single_line_output_mapper(
            "main", "WMA", "LINE", "price", defn.default_color
        ),
    )


def create_rsi_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.rsi",
        version=1,
        display_name="Relative Strength Index",
        description=(
            "Momentum oscillator measuring speed and change of price movements on 0-100 scale."
        ),
        category=IndicatorCategory.MOMENTUM,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["close"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=14,
                required=True,
                min_value=2,
                max_value=100,
                description="RSI lookback period (typically 14)",
            )
        ],
        default_color="#ec4899",
        default_line_width=2,
        min_history_bars=15,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.RSI if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 14))},
        lookback_calc=lambda p: int(p.get("period", 14)) + 1,
        output_mapper=make_single_line_output_mapper(
            "main", "RSI", "LINE", "points", defn.default_color
        ),
    )


def create_macd_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.macd",
        version=1,
        display_name="Moving Average Convergence Divergence",
        description=(
            "Trend-following momentum study revealing relationship between two moving averages."
        ),
        category=IndicatorCategory.MOMENTUM,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["close"],
        parameters=[
            IndicatorParameterDefinition(
                name="fast_period",
                type=IndicatorParameterType.INTEGER,
                default=12,
                required=True,
                min_value=2,
                max_value=100,
                description="Fast EMA period (default 12)",
            ),
            IndicatorParameterDefinition(
                name="slow_period",
                type=IndicatorParameterType.INTEGER,
                default=26,
                required=True,
                min_value=3,
                max_value=200,
                description="Slow EMA period (default 26, must exceed fast period)",
            ),
            IndicatorParameterDefinition(
                name="signal_period",
                type=IndicatorParameterType.INTEGER,
                default=9,
                required=True,
                min_value=1,
                max_value=50,
                description="Signal smoothing period (default 9)",
            ),
        ],
        default_color="#38bdf8",
        default_line_width=2,
        min_history_bars=35,
        output_names=["macd", "signal", "histogram"],
    )

    class CustomMACDCalculator(TALibIndicatorCalculator):
        def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
            norm = super().validate_parameters(params)
            if norm["fast_period"] >= norm["slow_period"]:
                raise ValueError(
                    f"MACD fast_period ({norm['fast_period']}) must be strictly less than "
                    f"slow_period ({norm['slow_period']})."
                )
            return norm

    return CustomMACDCalculator(
        definition=defn,
        talib_func=talib.MACD if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {
            "fastperiod": int(p.get("fast_period", 12)),
            "slowperiod": int(p.get("slow_period", 26)),
            "signalperiod": int(p.get("signal_period", 9)),
        },
        lookback_calc=lambda p: int(p.get("slow_period", 26)) + int(p.get("signal_period", 9)),
        output_mapper=make_macd_output_mapper(),
    )


def create_bbands_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.bbands",
        version=1,
        display_name="Bollinger Bands",
        description=(
            "Volatility bands plotted at standard deviation intervals around a moving average."
        ),
        category=IndicatorCategory.VOLATILITY,
        rendering_target=IndicatorRenderingTarget.PRICE_OVERLAY,
        input_requirements=["close"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=20,
                required=True,
                min_value=2,
                max_value=200,
                description="Moving average lookback period",
            ),
            IndicatorParameterDefinition(
                name="nbdev_up",
                type=IndicatorParameterType.DECIMAL,
                default=2.0,
                required=True,
                min_value=0.1,
                max_value=10.0,
                description="Upper standard deviation multiplier",
            ),
            IndicatorParameterDefinition(
                name="nbdev_dn",
                type=IndicatorParameterType.DECIMAL,
                default=2.0,
                required=True,
                min_value=0.1,
                max_value=10.0,
                description="Lower standard deviation multiplier",
            ),
        ],
        default_color="#38bdf8",
        default_line_width=1,
        min_history_bars=20,
        output_names=["upper", "middle", "lower"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.BBANDS if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {
            "timeperiod": int(p.get("period", 20)),
            "nbdevup": float(p.get("nbdev_up", 2.0)),
            "nbdevdn": float(p.get("nbdev_dn", 2.0)),
            "matype": 0,
        },
        lookback_calc=lambda p: int(p.get("period", 20)),
        output_mapper=make_bbands_output_mapper(),
    )


def create_atr_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.atr",
        version=1,
        display_name="Average True Range",
        description="Market volatility indicator decomposing the entire range of an asset price.",
        category=IndicatorCategory.VOLATILITY,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["high", "low", "close"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=14,
                required=True,
                min_value=1,
                max_value=100,
                description="True range smoothing period",
            )
        ],
        default_color="#f59e0b",
        default_line_width=2,
        min_history_bars=15,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.ATR if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 14))},
        lookback_calc=lambda p: int(p.get("period", 14)) + 1,
        output_mapper=make_single_line_output_mapper(
            "main", "ATR", "LINE", "price_distance", defn.default_color
        ),
    )


def create_stoch_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.stoch",
        version=1,
        display_name="Stochastic Oscillator",
        description=(
            "Momentum indicator comparing closing price to high-low range over a given period."
        ),
        category=IndicatorCategory.MOMENTUM,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["high", "low", "close"],
        parameters=[
            IndicatorParameterDefinition(
                name="fastk_period",
                type=IndicatorParameterType.INTEGER,
                default=5,
                required=True,
                min_value=1,
                max_value=100,
                description="Fast %K calculation period",
            ),
            IndicatorParameterDefinition(
                name="slowk_period",
                type=IndicatorParameterType.INTEGER,
                default=3,
                required=True,
                min_value=1,
                max_value=50,
                description="Slow %K smoothing period",
            ),
            IndicatorParameterDefinition(
                name="slowd_period",
                type=IndicatorParameterType.INTEGER,
                default=3,
                required=True,
                min_value=1,
                max_value=50,
                description="Slow %D moving average period",
            ),
        ],
        default_color="#38bdf8",
        default_line_width=2,
        min_history_bars=15,
        output_names=["slowk", "slowd"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.STOCH if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {
            "fastk_period": int(p.get("fastk_period", 5)),
            "slowk_period": int(p.get("slowk_period", 3)),
            "slowk_matype": 0,
            "slowd_period": int(p.get("slowd_period", 3)),
            "slowd_matype": 0,
        },
        lookback_calc=lambda p: (
            int(p.get("fastk_period", 5))
            + int(p.get("slowk_period", 3))
            + int(p.get("slowd_period", 3))
        ),
        output_mapper=make_stoch_output_mapper(),
    )


def create_adx_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.adx",
        version=1,
        display_name="Average Directional Index",
        description=(
            "Trend strength indicator measuring directional price movement regardless of direction."
        ),
        category=IndicatorCategory.TREND,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["high", "low", "close"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=14,
                required=True,
                min_value=2,
                max_value=100,
                description="ADX directional period",
            )
        ],
        default_color="#10b981",
        default_line_width=2,
        min_history_bars=28,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.ADX if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 14))},
        lookback_calc=lambda p: int(p.get("period", 14)) * 2,
        output_mapper=make_single_line_output_mapper(
            "main", "ADX", "LINE", "points", defn.default_color
        ),
    )


def create_cci_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.cci",
        version=1,
        display_name="Commodity Channel Index",
        description=(
            "Versatile oscillator assessing price deviation relative to its statistical average."
        ),
        category=IndicatorCategory.MOMENTUM,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["high", "low", "close"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=14,
                required=True,
                min_value=2,
                max_value=100,
                description="CCI calculation period",
            )
        ],
        default_color="#6366f1",
        default_line_width=2,
        min_history_bars=15,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.CCI if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 14))},
        lookback_calc=lambda p: int(p.get("period", 14)),
        output_mapper=make_single_line_output_mapper(
            "main", "CCI", "LINE", "points", defn.default_color
        ),
    )


def create_roc_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.roc",
        version=1,
        display_name="Rate of Change",
        description=(
            "Momentum oscillator measuring percentage price change over a specified period."
        ),
        category=IndicatorCategory.MOMENTUM,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["close"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=10,
                required=True,
                min_value=1,
                max_value=100,
                description="Rate of change comparison lookback",
            )
        ],
        default_color="#f59e0b",
        default_line_width=2,
        min_history_bars=11,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.ROC if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 10))},
        lookback_calc=lambda p: int(p.get("period", 10)),
        output_mapper=make_single_line_output_mapper(
            "main", "ROC", "LINE", "percent", defn.default_color
        ),
    )


def create_mom_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.mom",
        version=1,
        display_name="Momentum",
        description="Absolute price difference between current close and close N bars ago.",
        category=IndicatorCategory.MOMENTUM,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["close"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=10,
                required=True,
                min_value=1,
                max_value=100,
                description="Momentum comparison period",
            )
        ],
        default_color="#10b981",
        default_line_width=2,
        min_history_bars=11,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.MOM if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 10))},
        lookback_calc=lambda p: int(p.get("period", 10)),
        output_mapper=make_single_line_output_mapper(
            "main", "MOM", "LINE", "difference", defn.default_color
        ),
    )


def create_obv_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.obv",
        version=1,
        display_name="On-Balance Volume",
        description=(
            "Cumulative volume measure adding or subtracting volume by directional price changes."
        ),
        category=IndicatorCategory.VOLUME,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["close", "volume"],
        parameters=[],
        default_color="#38bdf8",
        default_line_width=2,
        min_history_bars=2,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.OBV if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {},
        lookback_calc=lambda p: 1,
        output_mapper=make_single_line_output_mapper(
            "main", "OBV", "LINE", "volume_units", defn.default_color
        ),
        requires_volume=True,
    )


def create_mfi_calculator() -> IndicatorCalculator:
    defn = IndicatorDefinition(
        indicator_id="atlas.mfi",
        version=1,
        display_name="Money Flow Index",
        description=(
            "Volume-weighted momentum study assessing buying and selling pressure on 0-100 scale."
        ),
        category=IndicatorCategory.VOLUME,
        rendering_target=IndicatorRenderingTarget.INDICATOR_PANE,
        input_requirements=["high", "low", "close", "volume"],
        parameters=[
            IndicatorParameterDefinition(
                name="period",
                type=IndicatorParameterType.INTEGER,
                default=14,
                required=True,
                min_value=2,
                max_value=100,
                description="Money flow lookback period",
            )
        ],
        default_color="#ec4899",
        default_line_width=2,
        min_history_bars=15,
        output_names=["main"],
    )
    return TALibIndicatorCalculator(
        definition=defn,
        talib_func=talib.MFI if talib else lambda *a, **kw: None,
        param_mapper=lambda p: {"timeperiod": int(p.get("period", 14))},
        lookback_calc=lambda p: int(p.get("period", 14)) + 1,
        output_mapper=make_single_line_output_mapper(
            "main", "MFI", "LINE", "points", defn.default_color
        ),
        requires_volume=True,
    )


def get_all_production_calculators() -> List[IndicatorCalculator]:
    """Return all 14 canonical Stage 70 production indicator calculators."""
    return [
        SmaCalculator(),  # Stage 69 Native Reference SMA
        create_ema_calculator(),
        create_wma_calculator(),
        create_rsi_calculator(),
        create_macd_calculator(),
        create_bbands_calculator(),
        create_atr_calculator(),
        create_stoch_calculator(),
        create_adx_calculator(),
        create_cci_calculator(),
        create_roc_calculator(),
        create_mom_calculator(),
        create_obv_calculator(),
        create_mfi_calculator(),
    ]
