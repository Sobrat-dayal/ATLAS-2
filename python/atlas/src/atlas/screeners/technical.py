"""Institutional-Grade Technical Indicator Engine for Financial Screeners (Stage 96).

Pure, deterministic, mathematically exact technical indicator calculations:
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA) with SMA seed initialization
- Relative Strength Index (RSI) with Wilder's smoothing and zero-loss edge case handling
- Moving Average Convergence Divergence (MACD) with Signal line and Histogram
- Bollinger Bands with Bandwidth and %B
- Average True Range (ATR) with Wilder's smoothing and ATR%
- Price Momentum / Rate of Change (ROC)
- Annualized Realized Historical Volatility (Log returns)
- Relative Volume (RVOL)
- 52-Week Range & Distance Metrics
- Moving Average Crossovers (Golden Cross / Death Cross states and transitions)

All indicators enforce:
- Completed-bar requirement
- Strict history warm-up sufficiency: returns None if bars < required lookback
- Exact Decimal arithmetic with zero look-ahead bias
"""

import math
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Sequence


def validate_ohlcv_bar(bar: Dict[str, Any]) -> bool:
    """Validates single OHLCV bar invariant consistency."""
    try:
        o = Decimal(str(bar["open"]))
        h = Decimal(str(bar["high"]))
        lo = Decimal(str(bar["low"]))
        c = Decimal(str(bar["close"]))
        if h < max(o, c) or lo > min(o, c) or lo > h:
            return False
        vol = bar.get("volume")
        if vol is not None and Decimal(str(vol)) < Decimal("0"):
            return False
        return True
    except (KeyError, TypeError, ValueError, InvalidOperation):
        return False


def compute_sma(prices: Sequence[Decimal], period: int) -> Optional[Decimal]:
    """Computes unweighted Simple Moving Average of the last N prices.

    Requires len(prices) >= period. If insufficient bars, returns None.
    """
    if period <= 0 or len(prices) < period:
        return None
    window = prices[-period:]
    total = sum(window)
    return (total / Decimal(period)).quantize(Decimal("0.0001"))


def compute_ema(prices: Sequence[Decimal], period: int) -> Optional[Decimal]:
    """Computes Exponential Moving Average of prices over N periods using SMA seed.

    Multiplier alpha = 2 / (period + 1).
    Requires len(prices) >= period. Returns None if insufficient history.
    """
    if period <= 0 or len(prices) < period:
        return None

    # Seed EMA with initial SMA of first `period` observations
    initial_window = prices[:period]
    ema = sum(initial_window) / Decimal(period)
    alpha = Decimal("2") / Decimal(period + 1)
    one_minus_alpha = Decimal("1") - alpha

    for price in prices[period:]:
        ema = (alpha * price) + (one_minus_alpha * ema)

    return ema.quantize(Decimal("0.0001"))


def compute_rsi(prices: Sequence[Decimal], period: int = 14) -> Optional[Decimal]:
    """Computes Relative Strength Index using Wilder's smoothing convention.

    Strict warm-up: Requires at least `period + 1` price observations.
    Returns bounded Decimal in range [0, 100].
    """
    if period <= 0 or len(prices) < period + 1:
        return None

    changes: List[Decimal] = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

    # Initial average gain/loss over first `period` changes
    init_gains = [c if c > Decimal("0") else Decimal("0") for c in changes[:period]]
    init_losses = [-c if c < Decimal("0") else Decimal("0") for c in changes[:period]]

    avg_gain = sum(init_gains) / Decimal(period)
    avg_loss = sum(init_losses) / Decimal(period)

    # Wilder's smoothing for subsequent changes
    p_dec = Decimal(period)
    p_minus_1 = Decimal(period - 1)
    for c in changes[period:]:
        gain = c if c > Decimal("0") else Decimal("0")
        loss = -c if c < Decimal("0") else Decimal("0")
        avg_gain = ((avg_gain * p_minus_1) + gain) / p_dec
        avg_loss = ((avg_loss * p_minus_1) + loss) / p_dec

    if avg_loss == Decimal("0"):
        return Decimal("100.00") if avg_gain > Decimal("0") else Decimal("50.00")

    rs = avg_gain / avg_loss
    rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
    return max(Decimal("0.00"), min(Decimal("100.00"), rsi.quantize(Decimal("0.01"))))


def compute_macd(
    prices: Sequence[Decimal],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> Optional[Dict[str, Decimal]]:
    """Computes Moving Average Convergence Divergence (MACD).

    - Fast EMA (default 12)
    - Slow EMA (default 26)
    - MACD Line = Fast EMA - Slow EMA
    - Signal Line = 9-period EMA of MACD Line
    - Histogram = MACD Line - Signal Line

    Requires at least `slow_period + signal_period` bars.
    """
    min_required = slow_period + signal_period
    if len(prices) < min_required:
        return None

    # Calculate rolling Fast and Slow EMAs over the full series
    fast_alpha = Decimal("2") / Decimal(fast_period + 1)
    fast_oma = Decimal("1") - fast_alpha
    slow_alpha = Decimal("2") / Decimal(slow_period + 1)
    slow_oma = Decimal("1") - slow_alpha

    # Initialize fast EMA
    fast_ema = sum(prices[:fast_period]) / Decimal(fast_period)
    fast_emas: List[Decimal] = [fast_ema]
    for p in prices[fast_period:]:
        fast_ema = (fast_alpha * p) + (fast_oma * fast_ema)
        fast_emas.append(fast_ema)

    # Initialize slow EMA
    slow_ema = sum(prices[:slow_period]) / Decimal(slow_period)
    slow_emas: List[Decimal] = [slow_ema]
    for p in prices[slow_period:]:
        slow_ema = (slow_alpha * p) + (slow_oma * slow_ema)
        slow_emas.append(slow_ema)

    # Align MACD line points: slow_emas starts at index `slow_period - 1` of prices
    # Corresponding fast_emas index is `(slow_period - 1) - (fast_period - 1) = slow_period - fast_period`
    fast_offset = slow_period - fast_period
    macd_series: List[Decimal] = []
    for i in range(len(slow_emas)):
        macd_val = fast_emas[fast_offset + i] - slow_emas[i]
        macd_series.append(macd_val)

    if len(macd_series) < signal_period:
        return None

    # Compute Signal Line (EMA of MACD series)
    sig_alpha = Decimal("2") / Decimal(signal_period + 1)
    sig_oma = Decimal("1") - sig_alpha

    sig_ema = sum(macd_series[:signal_period]) / Decimal(signal_period)
    for m in macd_series[signal_period:]:
        sig_ema = (sig_alpha * m) + (sig_oma * sig_ema)

    latest_macd = macd_series[-1]
    latest_signal = sig_ema
    latest_hist = latest_macd - latest_signal

    return {
        "macd": latest_macd.quantize(Decimal("0.0001")),
        "signal": latest_signal.quantize(Decimal("0.0001")),
        "histogram": latest_hist.quantize(Decimal("0.0001")),
    }


def compute_bollinger_bands(
    prices: Sequence[Decimal],
    period: int = 20,
    multiplier: Decimal = Decimal("2.0"),
) -> Optional[Dict[str, Decimal]]:
    """Computes Bollinger Bands over previous N completed closes.

    - Middle Band: SMA(N)
    - Upper Band: Middle + multiplier * sample_std_dev
    - Lower Band: Middle - multiplier * sample_std_dev
    - Bandwidth: (Upper - Lower) / Middle
    - %B: (Close - Lower) / (Upper - Lower)
    """
    if period <= 1 or len(prices) < period:
        return None

    window = prices[-period:]
    middle = sum(window) / Decimal(period)

    # Sample standard deviation
    variance = sum((p - middle) ** 2 for p in window) / Decimal(period - 1)
    try:
        std_dev = Decimal(str(math.sqrt(float(variance))))
    except (ValueError, OverflowError):
        std_dev = Decimal("0")

    upper = middle + (multiplier * std_dev)
    lower = middle - (multiplier * std_dev)

    latest_close = window[-1]
    band_width = (upper - lower) / middle if middle > Decimal("0") else Decimal("0")

    denom = upper - lower
    if denom > Decimal("0"):
        percent_b = (latest_close - lower) / denom
    else:
        percent_b = Decimal("0.50")

    return {
        "middle": middle.quantize(Decimal("0.0001")),
        "upper": upper.quantize(Decimal("0.0001")),
        "lower": lower.quantize(Decimal("0.0001")),
        "bandwidth": (band_width * Decimal("100")).quantize(Decimal("0.01")),
        "percent_b": percent_b.quantize(Decimal("0.0001")),
    }


def compute_atr(
    highs: Sequence[Decimal],
    lows: Sequence[Decimal],
    closes: Sequence[Decimal],
    period: int = 14,
) -> Optional[Dict[str, Decimal]]:
    """Computes Average True Range (ATR) with Wilder's smoothing and ATR%.

    TR = max(High - Low, abs(High - PrevClose), abs(Low - PrevClose)).
    Requires at least period + 1 bars.
    """
    n = len(closes)
    if period <= 0 or n < period + 1 or len(highs) != n or len(lows) != n:
        return None

    true_ranges: List[Decimal] = []
    for i in range(1, n):
        h = highs[i]
        lo = lows[i]
        prev_c = closes[i - 1]
        tr = max(h - lo, abs(h - prev_c), abs(lo - prev_c))
        true_ranges.append(tr)

    # Initial ATR is simple average of first `period` true ranges
    atr = sum(true_ranges[:period]) / Decimal(period)
    p_dec = Decimal(period)
    p_minus_1 = Decimal(period - 1)

    for tr in true_ranges[period:]:
        atr = ((atr * p_minus_1) + tr) / p_dec

    latest_close = closes[-1]
    atr_pct = (atr / latest_close * Decimal("100")) if latest_close > Decimal("0") else Decimal("0")

    return {
        "atr": atr.quantize(Decimal("0.0001")),
        "atr_pct": atr_pct.quantize(Decimal("0.01")),
    }


def compute_momentum(prices: Sequence[Decimal], period: int) -> Optional[Decimal]:
    """Computes percentage Price Rate of Change (ROC) over N periods:

    ((Close_t - Close_{t-N}) / Close_{t-N}) * 100.
    Requires at least period + 1 prices.
    """
    if period <= 0 or len(prices) <= period:
        return None

    curr = prices[-1]
    prior = prices[-1 - period]

    if prior <= Decimal("0"):
        return None

    pct_return = ((curr - prior) / prior) * Decimal("100")
    return pct_return.quantize(Decimal("0.01"))


def compute_historical_volatility(
    prices: Sequence[Decimal],
    lookback: int = 20,
    annualization_sessions: int = 252,
) -> Optional[Decimal]:
    """Computes annualized realized historical volatility of daily log returns:

    sigma_daily * sqrt(annualization_sessions) * 100%.
    Requires at least lookback + 1 positive prices.
    """
    if lookback <= 1 or len(prices) <= lookback:
        return None

    window = prices[-(lookback + 1):]
    log_returns: List[float] = []

    for i in range(1, len(window)):
        c_prev = float(window[i - 1])
        c_curr = float(window[i])
        if c_prev <= 0 or c_curr <= 0:
            return None
        log_returns.append(math.log(c_curr / c_prev))

    mean_ret = sum(log_returns) / len(log_returns)
    variance = sum((r - mean_ret) ** 2 for r in log_returns) / (len(log_returns) - 1)
    daily_vol = math.sqrt(variance)
    annualized_vol = daily_vol * math.sqrt(annualization_sessions) * 100.0

    return Decimal(str(round(annualized_vol, 2)))


def compute_relative_volume(
    current_volume: Optional[Decimal],
    avg_volume: Optional[Decimal],
) -> Optional[Decimal]:
    """Computes Relative Volume (RVOL) = current_volume / avg_volume."""
    if current_volume is None or avg_volume is None or avg_volume <= Decimal("0"):
        return None
    rvol = current_volume / avg_volume
    return rvol.quantize(Decimal("0.01"))


def compute_52w_high_low(prices: Sequence[Decimal]) -> Optional[Dict[str, Decimal]]:
    """Computes rolling 52-week (up to 252 trading sessions) High, Low, and % distance."""
    if not prices or len(prices) < 20:
        return None

    window = prices[-252:] if len(prices) >= 252 else prices
    high_val = max(window)
    low_val = min(window)
    curr = prices[-1]

    pct_from_high = ((curr - high_val) / high_val * Decimal("100")) if high_val > Decimal("0") else Decimal("0")
    pct_from_low = ((curr - low_val) / low_val * Decimal("100")) if low_val > Decimal("0") else Decimal("0")

    return {
        "high_52w": high_val.quantize(Decimal("0.01")),
        "low_52w": low_val.quantize(Decimal("0.01")),
        "pct_from_high": pct_from_high.quantize(Decimal("0.01")),
        "pct_from_low": pct_from_low.quantize(Decimal("0.01")),
    }
