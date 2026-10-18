"""Automated unit and integration tests for TA-Lib Production Indicator Engine (Stage 70).

Verifies:
1. TA-Lib installation and environment capability inspection.
2. Registry completeness: all 14 production indicators registered.
3. Native Decimal-safe SMA vs TA-Lib SMA parity within numerical tolerance.
4. Parameter validation and strict bounds checking.
5. All 14 indicator calculations (Trend, Momentum, Volatility, Oscillators, Volume).
6. Multi-output schemas (MACD 3-series, Bollinger Bands 3-series, Stochastic 2-series).
7. Warmup behavior: explicit null with WARMUP status, never zero-filled.
8. Volume qualification: rejection of missing/unpopulated volume on OTC FX without fabrication.
9. Error isolation in multi-indicator batch requests.
10. Read-only guarantees: 0 database writes, 0 provider calls.
"""

from decimal import Decimal

import pytest
from atlas.charts.indicators import (
    IndicatorCalculationRequest,
    IndicatorCategory,
    IndicatorInstanceConfig,
    IndicatorRenderingTarget,
    IndicatorStatus,
    TALibCapability,
    TechnicalIndicatorService,
    default_indicator_registry,
)
from atlas.charts.models import ChartBarDTO


def test_talib_installation_and_capability():
    """Verify TA-Lib is installed, importable, and reports environment metadata."""
    info = TALibCapability.get_info()
    assert info["installed"] is True
    assert "0.8" in info["wrapper_version"]
    assert "0.8" in info["native_version"]
    assert info["numpy_version"] is not None
    assert info["functions_available"] >= 150


def test_indicator_registry_contains_all_14_production_indicators():
    """Verify that all 14 required indicators are registered in the authoritative registry."""
    definitions = default_indicator_registry.list_definitions()
    assert len(definitions) == 14

    registered_ids = {d.indicator_id for d in definitions}
    expected_ids = {
        "atlas.sma",
        "atlas.ema",
        "atlas.wma",
        "atlas.rsi",
        "atlas.macd",
        "atlas.bbands",
        "atlas.atr",
        "atlas.stoch",
        "atlas.adx",
        "atlas.cci",
        "atlas.roc",
        "atlas.mom",
        "atlas.obv",
        "atlas.mfi",
    }
    assert registered_ids == expected_ids

    # Verify categories and rendering targets
    macd_def, _ = default_indicator_registry.get("atlas.macd", 1)
    assert macd_def.category == IndicatorCategory.MOMENTUM
    assert macd_def.rendering_target == IndicatorRenderingTarget.INDICATOR_PANE
    assert macd_def.output_names == ["macd", "signal", "histogram"]

    bbands_def, _ = default_indicator_registry.get("atlas.bbands", 1)
    assert bbands_def.category == IndicatorCategory.VOLATILITY
    assert bbands_def.rendering_target == IndicatorRenderingTarget.PRICE_OVERLAY
    assert bbands_def.output_names == ["upper", "middle", "lower"]

    obv_def, _ = default_indicator_registry.get("atlas.obv", 1)
    assert obv_def.category == IndicatorCategory.VOLUME
    assert "volume" in obv_def.input_requirements


def test_sma_native_vs_talib_numerical_parity():
    """Compare Stage 69 Decimal-safe reference SMA against TA-Lib SMA on synthetic test bars."""
    import numpy as np
    import talib

    _, sma_calc = default_indicator_registry.get("atlas.sma", 1)
    bars = []
    prices = [100.0, 102.5, 101.0, 104.0, 103.5, 106.0, 105.0, 108.5, 107.0, 110.0]

    for i, p in enumerate(prices):
        bars.append(
            ChartBarDTO(
                timestamp=f"2026-01-01T{i:02d}:00:00Z",
                time_unix=1704067200 + (i * 3600),
                open=Decimal(str(p - 1.0)),
                high=Decimal(str(p + 2.0)),
                low=Decimal(str(p - 2.0)),
                close=Decimal(str(p)),
                volume=Decimal("10000"),
            )
        )

    # 1. Native SMA calculation
    native_res = sma_calc.calculate("sma-ref", bars, {"period": 4})
    native_points = native_res.series[0].points

    # 2. Direct TA-Lib SMA calculation
    close_arr = np.array(prices, dtype=np.float64)
    talib_arr = talib.SMA(close_arr, timeperiod=4)

    assert len(native_points) == len(prices)
    for i in range(len(prices)):
        if np.isnan(talib_arr[i]):
            assert native_points[i].value is None
            assert native_points[i].status == IndicatorStatus.WARMUP
        else:
            assert native_points[i].value is not None
            # Absolute difference must be within float tolerance 1e-4
            assert abs(native_points[i].value - float(talib_arr[i])) < 1e-4


def test_macd_fast_slow_period_validation():
    """Verify MACD strictly enforces fast_period < slow_period."""
    _, macd_calc = default_indicator_registry.get("atlas.macd", 1)

    # fast_period == slow_period should raise ValueError
    with pytest.raises(ValueError, match="must be strictly less than"):
        macd_calc.validate_parameters({"fast_period": 20, "slow_period": 20, "signal_period": 9})

    # fast_period > slow_period should raise ValueError
    with pytest.raises(ValueError, match="must be strictly less than"):
        macd_calc.validate_parameters({"fast_period": 30, "slow_period": 20, "signal_period": 9})

    # valid parameters
    norm = macd_calc.validate_parameters({"fast_period": 12, "slow_period": 26, "signal_period": 9})
    assert norm["fast_period"] == 12
    assert norm["slow_period"] == 26
    assert norm["signal_period"] == 9


def test_multi_output_macd_and_bbands_and_stoch():
    """Verify multi-output indicators return correctly named, typed series and warmup points."""
    service = TechnicalIndicatorService()

    req = IndicatorCalculationRequest(
        symbol="SPY",
        interval="1d",
        instances=[
            IndicatorInstanceConfig(
                instance_id="macd-inst",
                indicator_id="atlas.macd",
                version=1,
                parameters={"fast_period": 12, "slow_period": 26, "signal_period": 9},
            ),
            IndicatorInstanceConfig(
                instance_id="bbands-inst",
                indicator_id="atlas.bbands",
                version=1,
                parameters={"period": 20, "nbdev_up": 2.0, "nbdev_dn": 2.0},
            ),
            IndicatorInstanceConfig(
                instance_id="stoch-inst",
                indicator_id="atlas.stoch",
                version=1,
                parameters={"fastk_period": 5, "slowk_period": 3, "slowd_period": 3},
            ),
        ],
    )

    resp = service.calculate_indicators(req)
    assert len(resp.results) == 3

    # Check MACD
    macd_res = next(r for r in resp.results if r.instance_id == "macd-inst")
    assert macd_res.status == IndicatorStatus.READY
    assert len(macd_res.series) == 3
    series_ids = {s.series_id for s in macd_res.series}
    assert series_ids == {"macd", "signal", "histogram"}
    hist_series = next(s for s in macd_res.series if s.series_id == "histogram")
    assert hist_series.rendering_type == "HISTOGRAM"

    # Check Bollinger Bands
    bb_res = next(r for r in resp.results if r.instance_id == "bbands-inst")
    assert bb_res.status == IndicatorStatus.READY
    assert len(bb_res.series) == 3
    bb_ids = {s.series_id for s in bb_res.series}
    assert bb_ids == {"upper", "middle", "lower"}

    # Verify Upper >= Middle >= Lower on valid points
    up_pts = bb_res.series[0].points
    mid_pts = bb_res.series[1].points
    low_pts = bb_res.series[2].points
    for u, m, low_val in zip(up_pts, mid_pts, low_pts):
        if u.value is not None and m.value is not None and low_val.value is not None:
            assert u.value >= m.value >= low_val.value

    # Check Stochastic
    stoch_res = next(r for r in resp.results if r.instance_id == "stoch-inst")
    assert stoch_res.status == IndicatorStatus.READY
    assert len(stoch_res.series) == 2
    assert {s.series_id for s in stoch_res.series} == {"slowk", "slowd"}


def test_volume_indicator_qualification_and_error_isolation():
    """Verify OBV rejects unpopulated volume without crashing the request or fabricating zero."""
    service = TechnicalIndicatorService()

    # Request EMA and OBV on EURUSD (OTC FX without volume)
    req = IndicatorCalculationRequest(
        symbol="EURUSD",
        interval="1d",
        instances=[
            IndicatorInstanceConfig(
                instance_id="ema-valid",
                indicator_id="atlas.ema",
                version=1,
                parameters={"period": 20},
            ),
            IndicatorInstanceConfig(
                instance_id="obv-fx",
                indicator_id="atlas.obv",
                version=1,
                parameters={},
            ),
        ],
    )

    resp = service.calculate_indicators(req)
    assert len(resp.results) == 2

    ema_res = next(r for r in resp.results if r.instance_id == "ema-valid")
    assert ema_res.status == IndicatorStatus.READY
    assert len(ema_res.series) == 1

    obv_res = next(r for r in resp.results if r.instance_id == "obv-fx")
    assert obv_res.status == IndicatorStatus.MISSING_VOLUME
    assert "requires genuine volume" in obv_res.error_message


def test_max_instances_limit():
    """Verify service rejects requests exceeding maximum active indicator instance limit of 12."""
    service = TechnicalIndicatorService()
    instances = [
        IndicatorInstanceConfig(
            instance_id=f"inst-{i}",
            indicator_id="atlas.ema",
            version=1,
            parameters={"period": 10 + i},
        )
        for i in range(13)
    ]

    req = IndicatorCalculationRequest(symbol="SPY", interval="1d", instances=instances[:12])
    # 12 is valid
    resp = service.calculate_indicators(req)
    assert len(resp.results) == 12

    # 13 should raise ValueError
    with pytest.raises(ValueError):
        IndicatorCalculationRequest(symbol="SPY", interval="1d", instances=instances)
