"""Comprehensive Automated Tests for ATLAS Charts Stage 68.

Stage 68: Advanced Chart Intervals & Chart Types V1
- Typed canonical intervals: 1m, 5m, 15m, 30m, 1h, 4h, 1D, 1W, 1M
- Series-specific availability discovery (GET /api/v1/charts/intervals)
- Native vs. derived provenance (NATIVE, DERIVED, UNAVAILABLE)
- High-precision Decimal OHLCV mathematical and temporal aggregation
- Preservation of None volume (never 0 for OTC/missing volume)
- Negative futures price allowance (CLZ26)
- Calendar-aware weekly (ISO) and monthly aggregation boundaries
- Read-only historical query with target-bar pagination
- Rejection of unsupported/unentitled intervals with truthful explanations
"""

from decimal import Decimal

import pytest
from atlas.charts.aggregation import (
    aggregate_ohlcv,
    get_interval_duration_seconds,
)
from atlas.charts.config import (
    CANONICAL_INTERVAL_ORDER,
    ChartInterval,
    ChartRenderMode,
)
from atlas.charts.models import ChartBarDTO
from atlas.charts.repository import HistoricalChartRepository
from atlas.charts.service import HistoricalChartService
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.config import get_settings


@pytest.fixture
def chart_repo():
    return HistoricalChartRepository()


@pytest.fixture
def chart_service(chart_repo):
    return HistoricalChartService(repository=chart_repo)


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def settings():
    return get_settings()


# =========================================================================
# 1. INTERVAL CATALOG & CONFIG TESTS
# =========================================================================


def test_canonical_interval_catalog():
    """Verify all 9 canonical intervals are registered in stable canonical order."""
    expected_order = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
    assert CANONICAL_INTERVAL_ORDER == expected_order

    # Verify enum values
    assert ChartInterval.ONE_MINUTE.value == "1m"
    assert ChartInterval.FIVE_MINUTES.value == "5m"
    assert ChartInterval.FIFTEEN_MINUTES.value == "15m"
    assert ChartInterval.THIRTY_MINUTES.value == "30m"
    assert ChartInterval.ONE_HOUR.value == "1h"
    assert ChartInterval.FOUR_HOURS.value == "4h"
    assert ChartInterval.ONE_DAY.value == "1d"
    assert ChartInterval.ONE_WEEK.value == "1w"
    assert ChartInterval.ONE_MONTH.value == "1M"


def test_chart_render_modes():
    """Verify all 4 professional chart render modes are recognized."""
    assert ChartRenderMode.CANDLESTICK.value == "candlestick"
    assert ChartRenderMode.BAR.value == "bar"
    assert ChartRenderMode.LINE.value == "line"
    assert ChartRenderMode.AREA.value == "area"


def test_interval_duration_seconds():
    """Verify fixed intraday durations vs calendar intervals."""
    assert get_interval_duration_seconds("1m") == 60
    assert get_interval_duration_seconds("5m") == 300
    assert get_interval_duration_seconds("15m") == 900
    assert get_interval_duration_seconds("30m") == 1800
    assert get_interval_duration_seconds("1h") == 3600
    assert get_interval_duration_seconds("4h") == 14400
    assert get_interval_duration_seconds("1d") == 86400
    # 1w and 1M are calendar-based
    assert get_interval_duration_seconds("1w") is None
    assert get_interval_duration_seconds("1M") is None


# =========================================================================
# 2. OHLCV AGGREGATION MATHEMATICAL INTEGRITY TESTS
# =========================================================================


def test_ohlc_aggregation_math():
    """Verify Open=first, High=max, Low=min, Close=last, Volume=sum."""
    bars = [
        ChartBarDTO(
            timestamp="2026-10-16T13:30:00Z",
            time_unix=1792157400,
            open=Decimal("100.00"),
            high=Decimal("103.50"),
            low=Decimal("99.50"),
            close=Decimal("102.00"),
            volume=Decimal("1000"),
            is_final=True,
        ),
        ChartBarDTO(
            timestamp="2026-10-16T13:31:00Z",
            time_unix=1792157460,
            open=Decimal("102.00"),
            high=Decimal("105.00"),
            low=Decimal("101.00"),
            close=Decimal("104.00"),
            volume=Decimal("2000"),
            is_final=True,
        ),
        ChartBarDTO(
            timestamp="2026-10-16T13:32:00Z",
            time_unix=1792157520,
            open=Decimal("104.00"),
            high=Decimal("106.00"),
            low=Decimal("103.00"),
            close=Decimal("105.50"),
            volume=Decimal("3000"),
            is_final=True,
        ),
    ]

    # Aggregate into a 5-minute bar
    aggregated = aggregate_ohlcv(bars, target_interval="5m")
    assert len(aggregated) == 1
    bar = aggregated[0]

    assert bar.open == Decimal("100.00")  # first Open
    assert bar.high == Decimal("106.00")  # maximum High
    assert bar.low == Decimal("99.50")  # minimum Low
    assert bar.close == Decimal("105.50")  # last Close
    assert bar.volume == Decimal("6000")  # sum of genuine volumes
    assert bar.is_final is True


def test_ohlc_aggregation_missing_volume_is_none():
    """Critical rule: If any constituent bar has missing volume,
    aggregate volume is None (never 0).
    """
    bars = [
        ChartBarDTO(
            timestamp="2026-10-16T13:30:00Z",
            time_unix=1792157400,
            open=Decimal("1.0720"),
            high=Decimal("1.0735"),
            low=Decimal("1.0715"),
            close=Decimal("1.0730"),
            volume=None,  # OTC FX bar without volume
            is_final=True,
        ),
        ChartBarDTO(
            timestamp="2026-10-16T13:31:00Z",
            time_unix=1792157460,
            open=Decimal("1.0730"),
            high=Decimal("1.0740"),
            low=Decimal("1.0728"),
            close=Decimal("1.0738"),
            volume=Decimal("500"),  # partial volume observation
            is_final=True,
        ),
    ]

    aggregated = aggregate_ohlcv(bars, target_interval="5m")
    assert len(aggregated) == 1
    assert aggregated[0].volume is None  # Strictly None, never 0 or partial 500


def test_ohlc_aggregation_negative_prices_for_futures():
    """Verify negative prices are permitted when allows_negative_price=True (e.g. CLZ26)."""
    negative_bars = [
        ChartBarDTO(
            timestamp="2026-10-16T14:00:00Z",
            time_unix=1792159200,
            open=Decimal("-5.00"),
            high=Decimal("-2.00"),
            low=Decimal("-15.00"),
            close=Decimal("-10.00"),
            volume=Decimal("15000"),
            is_final=True,
        ),
        ChartBarDTO(
            timestamp="2026-10-16T14:01:00Z",
            time_unix=1792159260,
            open=Decimal("-10.00"),
            high=Decimal("-1.50"),
            low=Decimal("-12.00"),
            close=Decimal("-3.00"),
            volume=Decimal("10000"),
            is_final=True,
        ),
    ]

    # With negative allowed:
    agg = aggregate_ohlcv(negative_bars, target_interval="5m", allows_negative_price=True)
    assert len(agg) == 1
    assert agg[0].open == Decimal("-5.00")
    assert agg[0].high == Decimal("-1.50")
    assert agg[0].low == Decimal("-15.00")
    assert agg[0].close == Decimal("-3.00")

    # Without negative allowed: must raise ValueError
    with pytest.raises(ValueError, match="Envelope violation"):
        aggregate_ohlcv(negative_bars, target_interval="5m", allows_negative_price=False)


def test_ohlc_aggregation_envelope_violation_rejection():
    """Verify corrupted bars where high < low or high < max(open, close) raise ValueError."""
    invalid_bars = [
        ChartBarDTO(
            timestamp="2026-10-16T14:00:00Z",
            time_unix=1792159200,
            open=Decimal("100.00"),
            high=Decimal("95.00"),  # Corrupted: high lower than open
            low=Decimal("90.00"),
            close=Decimal("92.00"),
            volume=Decimal("100"),
            is_final=True,
        )
    ]
    with pytest.raises(ValueError, match="Envelope violation"):
        aggregate_ohlcv(invalid_bars, target_interval="5m")


def test_iso_weekly_aggregation():
    """Verify daily bars are grouped according to Monday-aligned ISO calendar weeks."""
    # Monday 2026-10-12 to Friday 2026-10-16
    daily_bars = [
        ChartBarDTO(
            timestamp=f"2026-10-{day:02d}T00:00:00Z",
            time_unix=1791763200 + (day - 12) * 86400,
            open=Decimal(str(100 + day)),
            high=Decimal(str(105 + day)),
            low=Decimal(str(95 + day)),
            close=Decimal(str(102 + day)),
            volume=Decimal("100000"),
            is_final=True,
        )
        for day in range(12, 17)  # Mon-Fri
    ]
    weekly = aggregate_ohlcv(daily_bars, target_interval="1w")
    assert len(weekly) == 1
    w_bar = weekly[0]
    # Timestamp should align to Monday 2026-10-12
    assert "2026-10-12" in w_bar.timestamp
    assert w_bar.open == Decimal("112")  # Mon open (100+12)
    assert w_bar.close == Decimal("118")  # Fri close (102+16)
    assert w_bar.volume == Decimal("500000")


def test_calendar_monthly_aggregation():
    """Verify bars across month boundaries are grouped strictly by calendar month."""
    # 2 bars in October, 2 bars in November
    bars = [
        ChartBarDTO(
            timestamp="2026-10-30T00:00:00Z",
            time_unix=1793318400,
            open=Decimal("100.00"),
            high=Decimal("102.00"),
            low=Decimal("99.00"),
            close=Decimal("101.00"),
            volume=Decimal("10000"),
            is_final=True,
        ),
        ChartBarDTO(
            timestamp="2026-10-31T00:00:00Z",
            time_unix=1793404800,
            open=Decimal("101.00"),
            high=Decimal("104.00"),
            low=Decimal("100.00"),
            close=Decimal("103.00"),
            volume=Decimal("12000"),
            is_final=True,
        ),
        ChartBarDTO(
            timestamp="2026-11-01T00:00:00Z",
            time_unix=1793491200,
            open=Decimal("103.00"),
            high=Decimal("107.00"),
            low=Decimal("102.00"),
            close=Decimal("106.00"),
            volume=Decimal("15000"),
            is_final=True,
        ),
    ]

    monthly = aggregate_ohlcv(bars, target_interval="1M")
    assert len(monthly) == 2
    assert "2026-10-01" in monthly[0].timestamp
    assert monthly[0].close == Decimal("103.00")
    assert monthly[0].volume == Decimal("22000")

    assert "2026-11-01" in monthly[1].timestamp
    assert monthly[1].open == Decimal("103.00")
    assert monthly[1].close == Decimal("106.00")
    assert monthly[1].volume == Decimal("15000")


# =========================================================================
# 3. INTERVAL DISCOVERY API TESTS (GET /api/v1/charts/intervals)
# =========================================================================


@pytest.mark.asyncio
async def test_api_interval_discovery_equity(app, settings):
    """Test GET /api/v1/charts/intervals for AAPL returns native intraday
    and derived higher timeframes.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/intervals?symbol=AAPL")
        assert res.status_code == 200
        data = res.json()

        assert data["schema_version"] == "1.0.0"
        assert data["instrument"]["display_symbol"] == "AAPL"
        assert data["default_interval"] == "1d"

        options = {opt["interval_id"]: opt for opt in data["intervals"]}
        assert len(options) == 9

        # Check native intervals
        for int_id in ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]:
            assert int_id in options
            assert options[int_id]["availability"] == "AVAILABLE_NATIVE"
            assert options[int_id]["native_or_derived"] == "NATIVE"

        # Check derived intervals
        for int_id in ["1w", "1M"]:
            assert int_id in options
            assert options[int_id]["availability"] == "AVAILABLE_DERIVED"
            assert options[int_id]["native_or_derived"] == "DERIVED"
            assert options[int_id]["source_interval"] == "1d"


@pytest.mark.asyncio
async def test_api_interval_discovery_bonds_us10y(app, settings):
    """Test US10Y OTC Treasury note has 1d native and truthful unavailable intraday status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/intervals?symbol=US10Y")
        assert res.status_code == 200
        data = res.json()

        options = {opt["interval_id"]: opt for opt in data["intervals"]}

        # 1d is native
        assert options["1d"]["availability"] == "AVAILABLE_NATIVE"
        # 1w, 1M are derived
        assert options["1w"]["availability"] == "AVAILABLE_DERIVED"
        assert options["1M"]["availability"] == "AVAILABLE_DERIVED"

        # Intraday intervals must be UNAVAILABLE with explicit reasons
        for int_id in ["1m", "5m", "15m", "30m", "1h", "4h"]:
            assert options[int_id]["availability"] == "UNAVAILABLE"
            assert "OTC" in options[int_id]["unavailability_reason"]


@pytest.mark.asyncio
async def test_api_interval_discovery_fx_eurusd(app, settings):
    """Test EURUSD has 1m unavailable due to institutional licensing restrictions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/intervals?symbol=EURUSD")
        assert res.status_code == 200
        data = res.json()

        options = {opt["interval_id"]: opt for opt in data["intervals"]}
        assert options["1m"]["availability"] == "UNAVAILABLE"
        assert "license" in options["1m"]["unavailability_reason"].lower()
        assert options["5m"]["availability"] == "AVAILABLE_NATIVE"


@pytest.mark.asyncio
async def test_api_interval_discovery_unknown_instrument(app, settings):
    """Test GET /api/v1/charts/intervals with invalid instrument returns 404 Not Found."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/intervals?symbol=NONEXISTENT_XYZ")
        assert res.status_code == 404
        data = res.json()
        error_msg = data["error"]["message"] if "error" in data else data.get("detail", "")
        assert "Unknown or non-chartable instrument" in error_msg


# =========================================================================
# 4. MULTI-INTERVAL HISTORICAL API TESTS (GET /api/v1/charts/history)
# =========================================================================


@pytest.mark.asyncio
async def test_api_history_native_intraday(app, settings):
    """Test GET /api/v1/charts/history with 1m returns native intraday bars."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(
            f"{settings.api_prefix}/charts/history?symbol=AAPL&interval=1m&limit=50"
        )
        assert res.status_code == 200
        data = res.json()

        assert data["interval"] == "1m"
        assert data["interval_source_kind"] == "NATIVE"
        assert data["derived_source_interval"] is None
        assert len(data["bars"]) == 50
        # Envelope validation
        for bar in data["bars"]:
            assert bar["high"] >= bar["low"]
            assert bar["high"] >= max(bar["open"], bar["close"])
            assert bar["low"] <= min(bar["open"], bar["close"])


@pytest.mark.asyncio
async def test_api_history_derived_weekly(app, settings):
    """Test GET /api/v1/charts/history with 1w returns derived weekly bars with source lineage."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(
            f"{settings.api_prefix}/charts/history?symbol=SPY&interval=1w&limit=20"
        )
        assert res.status_code == 200
        data = res.json()

        assert data["interval"] == "1w"
        assert data["interval_source_kind"] == "DERIVED"
        assert data["derived_source_interval"] == "1d"
        assert len(data["bars"]) > 0


@pytest.mark.asyncio
async def test_api_history_unsupported_interval_rejected(app, settings):
    """Test requesting unsupported intraday interval on US10Y returns 400 with explanation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/history?symbol=US10Y&interval=15m")
        assert res.status_code == 400
        data = res.json()
        error_msg = data["error"]["message"] if "error" in data else data.get("detail", "")
        assert "Unsupported interval '15m'" in error_msg
        assert "US10Y" in error_msg
        assert "OTC" in error_msg


@pytest.mark.asyncio
async def test_api_history_pagination_on_target_interval(app, settings):
    """Verify cursor pagination operates on target-interval bars without splitting."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Page 1
        res1 = await client.get(
            f"{settings.api_prefix}/charts/history?symbol=AAPL&interval=1h&limit=10"
        )
        assert res1.status_code == 200
        data1 = res1.json()
        bars1 = data1["bars"]
        assert len(bars1) == 10
        cursor1 = data1["pagination"]["next_cursor"]

        if cursor1:
            # Page 2 (older bars)
            res2 = await client.get(
                f"{settings.api_prefix}/charts/history?symbol=AAPL&interval=1h&limit=10&before={cursor1}"
            )
            assert res2.status_code == 200
            data2 = res2.json()
            bars2 = data2["bars"]
            assert len(bars2) > 0
            # Ensure chronological order: bars2 are strictly older than bars1
            assert bars2[-1]["timestamp"] < bars1[0]["timestamp"]
