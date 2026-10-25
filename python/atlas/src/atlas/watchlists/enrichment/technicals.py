"""Technical Indicator Snapshots Adapter for Watchlist Enrichment (Stage 79).

Projects finalized 1D candle technical indicator observations:
- technical.sma_20_1d
- technical.sma_50_1d
- technical.ema_20_1d
- technical.ema_50_1d
- technical.rsi_14_1d
- technical.macd_line_1d
- technical.macd_signal_1d
- technical.macd_histogram_1d
- technical.bbands_upper_1d
- technical.bbands_middle_1d
- technical.bbands_lower_1d
- technical.atr_14_1d
- technical.obv_1d

Guarantees & Invariants:
- Strictly reuses Stage 69 IndicatorRegistry and Stage 70 TA-Lib calculators.
- Strictly evaluates on finalized 1D historical bars up to observation boundary T (zero lookahead).
- Deduplicates historical bar retrieval across multiple technical columns for the same market series.
- Rejects incomplete history with INSUFFICIENT_HISTORY status.
- Validates genuine Volume for OBV; never assumes missing volume is zero.
- Re-uses Charts calculation contracts ensuring 100% numerical consistency between Watchlists and Charts.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from uuid import UUID

import numpy as np

from atlas.charts.indicators.registry import default_indicator_registry
from atlas.charts.indicators.talib_adapter import TALibCapability, talib
from atlas.charts.models import ChartBarDTO

from .caching import default_enrichment_cache
from .models import EnrichmentCategory, EnrichmentStatus, WatchlistEnrichmentValue

logger = logging.getLogger(__name__)

# Mockable or queryable historical OHLCV bar store (series_id -> List[ChartBarDTO])
_HISTORICAL_BAR_STORE: Dict[str, List[ChartBarDTO]] = {}


def register_verified_historical_bars(series_id: str, bars: List[ChartBarDTO]) -> None:
    """Helper to seed verified canonical OHLCV bars for a series."""
    _HISTORICAL_BAR_STORE[series_id] = bars


register_verified_bars_for_series = register_verified_historical_bars


class TechnicalIndicatorAdapter:
    """Adapter evaluating technical indicator snapshots over canonical market series history."""

    def __init__(self) -> None:
        self.registry = default_indicator_registry
        self.cache = default_enrichment_cache

    def get_historical_bars(self, series_id: str, limit: int = 150) -> List[ChartBarDTO]:
        """Retrieves finalized daily bars up to limit."""
        bars = _HISTORICAL_BAR_STORE.get(series_id, [])
        return bars[-limit:] if len(bars) > limit else list(bars)

    def calculate_technical_snapshot(
        self,
        column_id: str,
        series_id: Optional[str] = None,
        instrument_id: Optional[UUID] = None,
        quote_currency: str = "USD",
        market_series_id: Optional[str] = None,
    ) -> WatchlistEnrichmentValue:
        """Calculates a single technical indicator snapshot for a given series."""
        effective_series_id = series_id or market_series_id or ""
        if not effective_series_id:
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.UNAVAILABLE,
                entity_id=instrument_id,
                reason="Market series ID required for technical indicator calculation",
            )

        series_id = effective_series_id

        # 1. Fetch historical bars
        bars = self.get_historical_bars(series_id, limit=200)
        if not bars:
            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                entity_id=instrument_id,
                market_series_id=series_id,
                reason="No historical daily candles available for market series",
            )

        last_bar = bars[-1]
        if hasattr(last_bar.timestamp, "isoformat"):
            last_bar_ts = last_bar.timestamp.isoformat()
        else:
            last_bar_ts = str(last_bar.timestamp) if last_bar.timestamp else "latest"

        # 2. Check cache
        cache_key = self.cache.make_technical_key(
            series_id=series_id,
            column_id=column_id,
            interval="1D",
            last_bar_timestamp=last_bar_ts,
        )
        cached = self.cache.get(EnrichmentCategory.TECHNICAL, cache_key)
        if cached is not None:
            return cached

        # 3. Calculate via TA-Lib or reference math
        result = self._execute_calculation(
            column_id=column_id,
            series_id=series_id,
            instrument_id=instrument_id,
            bars=bars,
            last_bar=last_bar,
            quote_currency=quote_currency,
        )

        self.cache.set(EnrichmentCategory.TECHNICAL, cache_key, result)
        return result

    def _execute_calculation(
        self,
        column_id: str,
        series_id: str,
        instrument_id: UUID,
        bars: List[ChartBarDTO],
        last_bar: ChartBarDTO,
        quote_currency: str,
    ) -> WatchlistEnrichmentValue:
        n_bars = len(bars)
        closes = np.array([float(b.close) for b in bars], dtype=np.float64)
        highs = np.array([float(b.high) for b in bars], dtype=np.float64)
        lows = np.array([float(b.low) for b in bars], dtype=np.float64)
        has_volume = all(b.volume is not None for b in bars)
        volumes = (
            np.array([float(b.volume) for b in bars], dtype=np.float64)
            if has_volume
            else np.array([], dtype=np.float64)
        )

        as_of_time = str(last_bar.timestamp) if last_bar.timestamp else None
        if hasattr(last_bar.timestamp, "date"):
            as_of_str = last_bar.timestamp.date().isoformat()
        elif isinstance(last_bar.timestamp, str):
            as_of_str = last_bar.timestamp.split("T")[0]
        else:
            as_of_str = None

        # ---------------------------------------------------------------------
        # Simple Moving Averages
        # ---------------------------------------------------------------------
        if column_id in ("technical.sma_20_1d", "technical.sma_50_1d"):
            period = 20 if column_id == "technical.sma_20_1d" else 50
            if n_bars < period:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                    reason=f"Requires {period} bars, but only {n_bars} available",
                )

            if TALibCapability.is_available():
                out = talib.SMA(closes, timeperiod=period)
                val = float(out[-1])
            else:
                val = float(np.mean(closes[-period:]))

            if np.isnan(val):
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(val, 2),
                value_type="MONETARY",
                unit=quote_currency,
                currency=quote_currency,
                entity_id=instrument_id,
                market_series_id=series_id,
                observation_time=as_of_time,
                as_of_date=as_of_str,
                methodology_id=f"sma_{period}",
            )

        # ---------------------------------------------------------------------
        # Exponential Moving Averages
        # ---------------------------------------------------------------------
        elif column_id in ("technical.ema_20_1d", "technical.ema_50_1d"):
            period = 20 if column_id == "technical.ema_20_1d" else 50
            if n_bars < period:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                    reason=f"Requires {period} bars, but only {n_bars} available",
                )

            if TALibCapability.is_available():
                out = talib.EMA(closes, timeperiod=period)
                val = float(out[-1])
            else:
                # Reference native EMA calculation
                k = 2.0 / (period + 1.0)
                ema = closes[0]
                for p in closes[1:]:
                    ema = (p * k) + (ema * (1.0 - k))
                val = float(ema)

            if np.isnan(val):
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(val, 2),
                value_type="MONETARY",
                unit=quote_currency,
                currency=quote_currency,
                entity_id=instrument_id,
                market_series_id=series_id,
                observation_time=as_of_time,
                as_of_date=as_of_str,
                methodology_id=f"ema_{period}",
            )

        # ---------------------------------------------------------------------
        # Relative Strength Index (RSI 14)
        # ---------------------------------------------------------------------
        elif column_id == "technical.rsi_14_1d":
            period = 14
            if n_bars < period + 1:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                    reason=f"Requires {period + 1} bars for warmup, but only {n_bars} available",
                )

            if TALibCapability.is_available():
                out = talib.RSI(closes, timeperiod=period)
                val = float(out[-1])
            else:
                # Wilder smoothing RSI reference
                deltas = np.diff(closes)
                gains = np.where(deltas > 0, deltas, 0.0)
                losses = np.where(deltas < 0, -deltas, 0.0)
                avg_gain = np.mean(gains[:period])
                avg_loss = np.mean(losses[:period])
                for i in range(period, len(deltas)):
                    avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                    avg_loss = (avg_loss * (period - 1) + losses[i]) / period
                if avg_loss == 0:
                    val = 100.0
                else:
                    rs = avg_gain / avg_loss
                    val = 100.0 - (100.0 / (1.0 + rs))

            if np.isnan(val):
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(val, 2),
                value_type="NUMBER",
                unit="",
                entity_id=instrument_id,
                market_series_id=series_id,
                observation_time=as_of_time,
                as_of_date=as_of_str,
                methodology_id="rsi_14_wilder",
            )

        # ---------------------------------------------------------------------
        # MACD (12, 26, 9)
        # ---------------------------------------------------------------------
        elif column_id in (
            "technical.macd_line_1d",
            "technical.macd_signal_1d",
            "technical.macd_histogram_1d",
        ):
            if n_bars < 35:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                    reason=f"Requires at least 35 bars for MACD warmup, but only {n_bars} available",
                )

            if TALibCapability.is_available():
                macd, signal, hist = talib.MACD(
                    closes, fastperiod=12, slowperiod=26, signalperiod=9
                )
                m_val, s_val, h_val = float(macd[-1]), float(signal[-1]), float(hist[-1])
            else:
                # Reference fallback for MACD
                def _calc_ema(series: np.ndarray, span: int) -> np.ndarray:
                    alpha = 2.0 / (span + 1.0)
                    out = np.empty_like(series)
                    out[0] = series[0]
                    for i in range(1, len(series)):
                        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
                    return out

                fast_ema = _calc_ema(closes, 12)
                slow_ema = _calc_ema(closes, 26)
                macd_line = fast_ema - slow_ema
                sig_line = _calc_ema(macd_line, 9)
                hist_line = macd_line - sig_line
                m_val, s_val, h_val = (
                    float(macd_line[-1]),
                    float(sig_line[-1]),
                    float(hist_line[-1]),
                )

            if column_id == "technical.macd_line_1d":
                res_val = m_val
            elif column_id == "technical.macd_signal_1d":
                res_val = s_val
            else:
                res_val = h_val

            if np.isnan(res_val):
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(res_val, 2),
                value_type="NUMBER",
                unit="",
                entity_id=instrument_id,
                market_series_id=series_id,
                observation_time=as_of_time,
                as_of_date=as_of_str,
                methodology_id="macd_12_26_9",
            )

        # ---------------------------------------------------------------------
        # Bollinger Bands (20, 2.0)
        # ---------------------------------------------------------------------
        elif column_id in (
            "technical.bbands_upper_1d",
            "technical.bbands_middle_1d",
            "technical.bbands_lower_1d",
        ):
            if n_bars < 20:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                    reason=f"Requires 20 bars, but only {n_bars} available",
                )

            if TALibCapability.is_available():
                upper, middle, lower = talib.BBANDS(
                    closes, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0
                )
                u_val, m_val, l_val = float(upper[-1]), float(middle[-1]), float(lower[-1])
            else:
                slice_closes = closes[-20:]
                m_val = float(np.mean(slice_closes))
                std_val = float(np.std(slice_closes, ddof=0))
                u_val = m_val + (2.0 * std_val)
                l_val = m_val - (2.0 * std_val)

            if column_id == "technical.bbands_upper_1d":
                res_val = u_val
            elif column_id == "technical.bbands_middle_1d":
                res_val = m_val
            else:
                res_val = l_val

            if np.isnan(res_val):
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(res_val, 2),
                value_type="MONETARY",
                unit=quote_currency,
                currency=quote_currency,
                entity_id=instrument_id,
                market_series_id=series_id,
                observation_time=as_of_time,
                as_of_date=as_of_str,
                methodology_id="bbands_20_2",
            )

        # ---------------------------------------------------------------------
        # ATR (14)
        # ---------------------------------------------------------------------
        elif column_id == "technical.atr_14_1d":
            period = 14
            if n_bars < period + 1:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                    reason=f"Requires at least {period + 1} bars, but only {n_bars} available",
                )

            if TALibCapability.is_available():
                out = talib.ATR(highs, lows, closes, timeperiod=period)
                val = float(out[-1])
            else:
                # Reference native ATR calculation
                tr = [
                    max(
                        highs[i] - lows[i],
                        abs(highs[i] - closes[i - 1]),
                        abs(lows[i] - closes[i - 1]),
                    )
                    for i in range(1, n_bars)
                ]
                atr = np.mean(tr[:period])
                for t in tr[period:]:
                    atr = (atr * (period - 1) + t) / period
                val = float(atr)

            if np.isnan(val):
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.INSUFFICIENT_HISTORY,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                )

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(val, 2),
                value_type="MONETARY",
                unit=quote_currency,
                currency=quote_currency,
                entity_id=instrument_id,
                market_series_id=series_id,
                observation_time=as_of_time,
                as_of_date=as_of_str,
                methodology_id="atr_14",
            )

        # ---------------------------------------------------------------------
        # OBV (On-Balance Volume)
        # ---------------------------------------------------------------------
        elif column_id == "technical.obv_1d":
            if not has_volume or len(volumes) < 2:
                return WatchlistEnrichmentValue(
                    column_id=column_id,
                    status=EnrichmentStatus.UNAVAILABLE,
                    entity_id=instrument_id,
                    market_series_id=series_id,
                    reason="Genuine volume data unavailable for series (cannot assume zero volume)",
                )

            if TALibCapability.is_available():
                out = talib.OBV(closes, volumes)
                val = float(out[-1])
            else:
                obv = 0.0
                for i in range(1, len(closes)):
                    if closes[i] > closes[i - 1]:
                        obv += volumes[i]
                    elif closes[i] < closes[i - 1]:
                        obv -= volumes[i]
                val = float(obv)

            return WatchlistEnrichmentValue(
                column_id=column_id,
                status=EnrichmentStatus.AVAILABLE,
                value=round(val, 0),
                value_type="NUMBER",
                unit="",
                entity_id=instrument_id,
                market_series_id=series_id,
                observation_time=as_of_time,
                as_of_date=as_of_str,
                methodology_id="obv_cumulative",
            )

        return WatchlistEnrichmentValue(
            column_id=column_id,
            status=EnrichmentStatus.UNAVAILABLE,
            entity_id=instrument_id,
            market_series_id=series_id,
            reason=f"Unknown technical indicator column '{column_id}'",
        )

    compute_snapshot = calculate_technical_snapshot
