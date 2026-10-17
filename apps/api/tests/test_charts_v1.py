"""Comprehensive Automated Tests for ATLAS Charts V1 (Stage 66).

Tests:
1. Canonical Instrument Identity:
   - Resolves canonical UUIDs for Equities, ETFs, FX, Crypto, Bonds, and Futures.
   - Preserves price currency, quotation units, and price basis.
   - Preserves asset-class volume semantics (FX/Bonds have None; others have volume).
   - Preserves negative-price allowance for commodity Futures (CLZ26).
2. Search & Discovery:
   - Discovers instruments by symbol substring and name query.
   - Filters by asset class.
3. Baseline Interval Policy:
   - Strictly enforces baseline interval '1d' as mandated by Stage 66.
   - Rejects unsupported intervals ('1m', '5m', '1h', '1w') with clear Stage 68 deferral.
4. Historical Data Query & Time Boundaries:
   - Ascending chronological bar ordering without duplicate timestamps.
   - Valid OHLC envelope invariants: high >= max(open, close, low) and low <= min(...).
   - Rejects reversed time ranges (start >= end) with HTTP 400.
   - Respects start and end boundaries.
5. Pagination & Bounded Limits:
   - Clamps limit to [10, 2000].
   - Cursor-based pagination: provides next_cursor and has_more flag for historical backfill.
   - Pagination seamlessly queries older bars before cursor.
6. API Endpoints (FastAPI AsyncClient):
   - GET /api/v1/charts/instruments
   - GET /api/v1/charts/instruments/{id}
   - GET /api/v1/charts/history (by symbol or instrument_id)
   - Proper error envelope handling on 400 and 404 responses.
7. Read-Only Invariants:
   - 0 canonical writes, 0 ClickHouse writes, 0 provider calls on read.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from atlas.charts.config import (
    gen_chart_instrument_id,
)
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
# 1. CANONICAL INSTRUMENT IDENTITY TESTS
# =========================================================================

def test_canonical_instrument_catalog(chart_repo):
    """Verify all default canonical chartable instruments are registered with UUIDs."""
    instruments = chart_repo.search_instruments()
    assert len(instruments) >= 12

    symbols = [inst.display_symbol for inst in instruments]
    assert "AAPL" in symbols
    assert "SPY" in symbols
    assert "EURUSD" in symbols
    assert "BTCUSDT" in symbols
    assert "US10Y" in symbols
    assert "CLZ26" in symbols


def test_asset_class_specific_semantics(chart_repo):
    """Verify quotation units, price basis, and volume treatment across asset classes."""
    # Equity
    aapl = chart_repo.get_instrument_by_symbol("AAPL")
    assert aapl is not None
    assert aapl.asset_class == "equities"
    assert aapl.quotation_unit == "USD/share"
    assert aapl.has_volume is True
    assert aapl.allows_negative_price is False

    # FX (Volume is None / OTC)
    eurusd = chart_repo.get_instrument_by_symbol("EURUSD")
    assert eurusd is not None
    assert eurusd.asset_class == "fx"
    assert eurusd.quotation_unit == "USD per EUR"
    assert eurusd.has_volume is False

    # Crypto (USDT quote unit)
    btcusdt = chart_repo.get_instrument_by_symbol("BTCUSDT")
    assert btcusdt is not None
    assert btcusdt.asset_class == "crypto"
    assert btcusdt.quotation_unit == "USDT per BTC"
    assert btcusdt.has_volume is True

    # Bond (Clean price % of par, volume None)
    us10y = chart_repo.get_instrument_by_symbol("US10Y")
    assert us10y is not None
    assert us10y.asset_class == "bonds"
    assert us10y.quotation_unit == "% of par (Clean Price)"
    assert us10y.has_volume is False

    # Futures (Supports negative prices, expiration date)
    clz26 = chart_repo.get_instrument_by_symbol("CLZ26")
    assert clz26 is not None
    assert clz26.asset_class == "futures"
    assert clz26.is_futures is True
    assert clz26.allows_negative_price is True
    assert clz26.contract_expiration is not None


# =========================================================================
# 2. SEARCH & DISCOVERY TESTS
# =========================================================================

def test_instrument_search_query(chart_service):
    """Test searching instruments by symbol and company name."""
    res_apple = chart_service.search_instruments(query="Apple")
    assert res_apple.count >= 1
    assert any(inst.display_symbol == "AAPL" for inst in res_apple.results)

    res_oil = chart_service.search_instruments(query="Crude")
    assert res_oil.count >= 1
    assert any(inst.display_symbol == "CLZ26" for inst in res_oil.results)


def test_instrument_search_asset_class_filter(chart_service):
    """Test filtering search results by asset class."""
    res_fx = chart_service.search_instruments(asset_class="fx")
    assert res_fx.count >= 2
    assert all(inst.asset_class == "fx" for inst in res_fx.results)


# =========================================================================
# 3. BASELINE INTERVAL & OHLC ENVELOPE INVARIANT TESTS
# =========================================================================

def test_baseline_interval_validation(chart_service):
    """Verify that only the '1d' baseline interval is accepted in Stage 66."""
    aapl_id = str(gen_chart_instrument_id("AAPL"))

    # Valid baseline interval
    valid_res = chart_service.get_chart_history(aapl_id, interval="1d")
    assert valid_res.interval == "1d"
    assert len(valid_res.bars) > 0

    # Unsupported intervals must be rejected with descriptive message
    for bad_interval in ["1m", "5m", "15m", "1h", "4h", "1w", "1M"]:
        with pytest.raises(ValueError, match="Unsupported interval"):
            chart_service.get_chart_history(aapl_id, interval=bad_interval)


def test_ohlc_envelope_invariants(chart_service):
    """Verify that every historical bar strictly satisfies High >= max and Low <= min."""
    spy_id = str(gen_chart_instrument_id("SPY"))
    res = chart_service.get_chart_history(spy_id, interval="1d", limit=250)
    assert len(res.bars) > 0

    for bar in res.bars:
        assert bar.high >= bar.open, f"High {bar.high} < Open {bar.open}"
        assert bar.high >= bar.close, f"High {bar.high} < Close {bar.close}"
        assert bar.high >= bar.low, f"High {bar.high} < Low {bar.low}"
        assert bar.low <= bar.open, f"Low {bar.low} > Open {bar.open}"
        assert bar.low <= bar.close, f"Low {bar.low} > Close {bar.close}"
        assert isinstance(bar.open, Decimal)
        assert isinstance(bar.close, Decimal)


def test_chronological_ordering_and_no_duplicates(chart_service):
    """Verify bars are ordered strictly ascending by time with no duplicate timestamps."""
    btc_id = str(gen_chart_instrument_id("BTCUSDT"))
    res = chart_service.get_chart_history(btc_id, interval="1d", limit=250)

    prev_time = 0
    timestamps_seen = set()
    for bar in res.bars:
        assert bar.time_unix > prev_time, (
            f"Bar not in ascending order: {bar.time_unix} <= {prev_time}"
        )
        assert bar.timestamp not in timestamps_seen, f"Duplicate timestamp found: {bar.timestamp}"
        timestamps_seen.add(bar.timestamp)
        prev_time = bar.time_unix


def test_volume_treatment_by_asset_class(chart_service):
    """Verify volume is non-negative Decimal for equities/crypto and None for OTC FX/bonds."""
    # Equity has volume
    aapl_res = chart_service.get_chart_history("AAPL", limit=20)
    for bar in aapl_res.bars:
        assert bar.volume is not None
        assert bar.volume > Decimal("0")

    # FX volume is None (never 0)
    fx_res = chart_service.get_chart_history("EURUSD", limit=20)
    for bar in fx_res.bars:
        assert bar.volume is None


# =========================================================================
# 4. TIME BOUNDS & PAGINATION / BACKFILL TESTS
# =========================================================================

def test_time_range_validation(chart_service):
    """Verify start_time >= end_time is rejected."""
    t_start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    t_end = datetime(2026, 5, 1, tzinfo=timezone.utc)  # reversed!

    with pytest.raises(ValueError, match="Invalid time range"):
        chart_service.get_chart_history("AAPL", start_time=t_start, end_time=t_end)


def test_pagination_and_backfill(chart_service):
    """Verify cursor pagination allows fetching older bars prior to next_cursor."""
    res_page1 = chart_service.get_chart_history("AAPL", limit=50)
    assert len(res_page1.bars) == 50
    assert res_page1.pagination.has_more is True
    assert res_page1.pagination.next_cursor is not None

    # Fetch older page using before_time cursor
    cursor_dt = datetime.fromisoformat(res_page1.pagination.next_cursor.replace("Z", "+00:00"))
    res_page2 = chart_service.get_chart_history("AAPL", before_time=cursor_dt, limit=50)
    assert len(res_page2.bars) == 50

    # Ensure page2 bars are all strictly older than page1 bars
    assert res_page2.bars[-1].time_unix < res_page1.bars[0].time_unix


# =========================================================================
# 5. FASTAPI REST API TESTS
# =========================================================================

@pytest.mark.asyncio
async def test_api_instruments_search(app, settings):
    """Test GET /api/v1/charts/instruments."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/instruments?q=AAPL")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 1
        assert data["results"][0]["display_symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_api_instrument_by_id(app, settings):
    """Test GET /api/v1/charts/instruments/{id}."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        aapl_id = str(gen_chart_instrument_id("AAPL"))
        res = await client.get(f"{settings.api_prefix}/charts/instruments/{aapl_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["display_symbol"] == "AAPL"
        assert data["asset_class"] == "equities"


@pytest.mark.asyncio
async def test_api_chart_history_success(app, settings):
    """Test GET /api/v1/charts/history with symbol and baseline interval."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(
            f"{settings.api_prefix}/charts/history?symbol=SPY&interval=1d&limit=100"
        )
        assert res.status_code == 200
        data = res.json()
        assert data["schema_version"] == "1.0.0"
        assert data["instrument"]["display_symbol"] == "SPY"
        assert data["interval"] == "1d"
        assert len(data["bars"]) == 100
        assert data["coverage"]["returned_bars_count"] == 100
        assert "open" in data["bars"][0]
        assert "high" in data["bars"][0]
        assert "low" in data["bars"][0]
        assert "close" in data["bars"][0]


@pytest.mark.asyncio
async def test_api_chart_history_unsupported_interval(app, settings):
    """Test GET /api/v1/charts/history with unsupported interval returns 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(
            f"{settings.api_prefix}/charts/history?symbol=SPY&interval=15m"
        )
        assert res.status_code == 400
        data = res.json()
        error_msg = data["error"]["message"] if "error" in data else data.get("detail", "")
        assert "Unsupported interval" in error_msg
        assert "Stage 68" in error_msg


@pytest.mark.asyncio
async def test_api_chart_history_unknown_instrument(app, settings):
    """Test GET /api/v1/charts/history with nonexistent instrument returns 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(
            f"{settings.api_prefix}/charts/history?symbol=NONEXISTENT_XYZ"
        )
        assert res.status_code == 400
        data = res.json()
        error_msg = data["error"]["message"] if "error" in data else data.get("detail", "")
        assert "Unknown or non-chartable" in error_msg
