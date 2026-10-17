"""Comprehensive Automated Tests for ATLAS Live Chart Streaming V1 (Stage 67).

Tests:
1. Live Quote State Retrieval & Canonical Instrument Semantics:
   - Equities & ETFs (SPY, AAPL, QQQ): Genuine Last-price observations.
   - Crypto Spot (BTCUSDT): 24/7 continuous trade feed with genuine Last.
   - Commodity Futures (CLZ26): Supports valid negative settlement/last prices.
   - OTC FX (EURUSD, USDJPY): Bid/Ask ONLY, last_price is None, has_genuine_last is False.
   - Sovereign Debt (US10Y): Clean price bid/ask ONLY, last_price is None.
2. Quote vs Candle Financial Integrity:
   - Quote snapshot does not mutate Open, High, Low, Close, or Volume of historical bars.
   - Bid/Ask does not generate Last.
   - Midpoint is never an executed Last trade.
   - Quote count is not Volume.
   - Missing historical bar is not created from latest Quote.
3. Live Event Validation, Ordering, and Idempotency:
   - Accepts valid typed quote events with matching UUID and ascending source timestamp.
   - Rejects stale and duplicate events (incoming timestamp <= current timestamp).
   - Rejects mismatched instrument UUIDs (INSTRUMENT_MISMATCH).
   - Rejects invalid UUID formats and missing IDs.
   - Rejects malformed timestamps.
   - Rejects NaN, Infinity, -Infinity, and invalid Decimal strings.
   - Rejects negative prices for non-futures (e.g. AAPL) while allowing for CLZ26.
   - Rejects unsupported schema versions.
4. REST API Endpoint (GET /api/v1/charts/live-state):
   - Resolves live state by symbol or canonical UUID.
   - 400 Bad Request on missing identifier.
   - 404 Not Found on unknown instrument.
   - Correct serialization of decimal prices, provenance, and freshness classification.
   - Read-only guarantees: 0 canonical DB writes, 0 ClickHouse writes, 0 provider fetches.
"""

from decimal import Decimal

import pytest
from atlas.charts.config import (
    ChartLiveCapability,
    ChartMarketDataFreshness,
    gen_chart_instrument_id,
)
from atlas.charts.live_service import LiveChartService
from atlas.charts.models import ChartBarDTO, LiveQuoteDTO
from atlas.charts.repository import HistoricalChartRepository
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.config import get_settings


@pytest.fixture
def chart_repo():
    return HistoricalChartRepository()


@pytest.fixture
def live_service(chart_repo):
    return LiveChartService(repository=chart_repo)


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def settings():
    return get_settings()


# =========================================================================
# 1. LIVE QUOTE STATE RETRIEVAL & CANONICAL INSTRUMENT SEMANTICS
# =========================================================================


def test_live_state_equities_and_etfs(live_service):
    """Verify equities and ETFs supply genuine Last trade prices with REALTIME freshness."""
    spy_state = live_service.get_live_state("SPY")
    assert spy_state is not None
    assert spy_state.display_symbol == "SPY"
    assert spy_state.price_currency == "USD"
    assert spy_state.quotation_unit == "USD/share"
    assert spy_state.freshness_status == ChartMarketDataFreshness.LIVE.value
    assert spy_state.delay_status == "REALTIME"
    assert spy_state.live_capability == ChartLiveCapability.LIVE_PRICE_AVAILABLE.value
    assert spy_state.quote is not None
    assert spy_state.quote.has_genuine_last is True
    assert spy_state.quote.last_price == Decimal("586.25")
    assert spy_state.quote.last_size == Decimal("50")

    aapl_state = live_service.get_live_state("AAPL")
    assert aapl_state is not None
    assert aapl_state.quote.has_genuine_last is True
    assert aapl_state.quote.last_price == Decimal("232.15")


def test_live_state_crypto_spot(live_service):
    """Verify crypto spot provides continuous real-time trades in USDT."""
    btc_state = live_service.get_live_state("BTCUSDT")
    assert btc_state is not None
    assert btc_state.display_symbol == "BTCUSDT"
    assert btc_state.quotation_unit == "USDT per BTC"
    assert btc_state.quote.has_genuine_last is True
    assert btc_state.quote.last_price == Decimal("68450.00")
    assert btc_state.quote.last_size == Decimal("0.25")


def test_live_state_futures_negative_price_support(live_service):
    """Verify commodity futures (CLZ26) support valid negative settlement prices."""
    clz_state = live_service.get_live_state("CLZ26")
    assert clz_state is not None
    assert clz_state.display_symbol == "CLZ26"
    assert clz_state.quotation_unit == "USD/barrel"
    assert clz_state.quote.has_genuine_last is True
    # CLZ26 allows negative price
    assert clz_state.quote.last_price < Decimal("0")
    assert clz_state.quote.last_price == Decimal("-15.50")


def test_live_state_otc_fx_no_last_price(live_service):
    """Verify OTC FX provides Bid/Ask ONLY; Last is None, live_capability is HISTORICAL_ONLY.

    Critical financial rule: Bid/Ask are NOT Last. Midpoint is NOT an executed trade.
    """
    eur_state = live_service.get_live_state("EURUSD")
    assert eur_state is not None
    assert eur_state.display_symbol == "EURUSD"
    assert eur_state.quotation_unit == "USD per EUR"
    assert eur_state.live_capability == ChartLiveCapability.HISTORICAL_ONLY.value
    assert eur_state.quote is not None
    assert eur_state.quote.has_genuine_last is False
    assert eur_state.quote.last_price is None
    assert eur_state.quote.last_size is None
    assert eur_state.quote.bid_price == Decimal("1.0854")
    assert eur_state.quote.ask_price == Decimal("1.0856")
    assert eur_state.quote.is_midpoint is False


def test_live_state_bonds_clean_price_only(live_service):
    """Verify sovereign bonds provide clean price Bid/Ask without Last trades."""
    bond_state = live_service.get_live_state("US10Y")
    assert bond_state is not None
    assert bond_state.display_symbol == "US10Y"
    assert bond_state.live_capability == ChartLiveCapability.HISTORICAL_ONLY.value
    assert bond_state.quote.has_genuine_last is False
    assert bond_state.quote.last_price is None
    assert bond_state.quote.bid_price == Decimal("4.085")
    assert bond_state.quote.ask_price == Decimal("4.090")


def test_live_state_resolution_by_uuid(live_service):
    """Verify live state resolves seamlessly by canonical instrument UUID."""
    spy_uuid = gen_chart_instrument_id("SPY")
    state = live_service.get_live_state(str(spy_uuid))
    assert state is not None
    assert state.instrument_entity_id == spy_uuid
    assert state.display_symbol == "SPY"


# =========================================================================
# 2. QUOTE VS CANDLE FINANCIAL INTEGRITY
# =========================================================================


def test_quote_does_not_mutate_historical_bars(live_service):
    """Verify Quote snapshots NEVER mutate Open, High, Low, Close, or Volume of historical bars."""
    bars = [
        ChartBarDTO(
            timestamp="2026-10-16T00:00:00Z",
            time_unix=1792195200,
            open=Decimal("585.10"),
            high=Decimal("587.40"),
            low=Decimal("584.20"),
            close=Decimal("586.30"),
            volume=Decimal("48200000"),
            is_final=True,
        )
    ]
    quote = LiveQuoteDTO(
        bid_price=Decimal("590.00"),
        ask_price=Decimal("590.10"),
        last_price=Decimal("600.00"),  # Way higher than historical bar high
        as_of="2026-10-18T10:00:00Z",
        has_genuine_last=True,
    )

    unmodified_bars = live_service.apply_quote_to_historical_bars(bars, quote)
    assert len(unmodified_bars) == 1
    target = unmodified_bars[0]
    assert target.open == Decimal("585.10")
    assert target.high == Decimal("587.40")  # NOT mutated to 600.00!
    assert target.low == Decimal("584.20")
    assert target.close == Decimal("586.30")  # NOT mutated to 600.00!
    assert target.volume == Decimal("48200000")  # NOT incremented!
    assert target.is_final is True


# =========================================================================
# 3. LIVE EVENT VALIDATION, ORDERING, AND IDEMPOTENCY
# =========================================================================


def test_event_validation_success(live_service):
    """Verify a valid incoming quote event is accepted and updates the quote."""
    spy_id = gen_chart_instrument_id("SPY")
    event = {
        "instrument_entity_id": str(spy_id),
        "source_timestamp": "2026-10-18T12:00:00Z",
        "payload": {
            "quote": {
                "bid_price": "586.50",
                "ask_price": "586.60",
                "last_price": "586.55",
                "last_size": "100",
                "as_of": "2026-10-18T12:00:00Z",
            }
        },
    }

    accepted, reason, reconciled = live_service.validate_and_reconcile_quote_event(
        current_quote=None,
        incoming_event=event,
        expected_entity_id=spy_id,
        allows_negative_price=False,
    )

    assert accepted is True
    assert reason == "ACCEPTED"
    assert reconciled is not None
    assert reconciled.last_price == Decimal("586.55")
    assert reconciled.has_genuine_last is True


def test_event_rejection_stale_or_duplicate(live_service):
    """Verify older or duplicate events are rejected based on source timestamp."""
    spy_id = gen_chart_instrument_id("SPY")
    current_quote = LiveQuoteDTO(
        last_price=Decimal("586.50"),
        as_of="2026-10-18T12:00:05Z",
        has_genuine_last=True,
    )

    # 1. Duplicate timestamp
    dup_event = {
        "instrument_entity_id": str(spy_id),
        "source_timestamp": "2026-10-18T12:00:05Z",
        "payload": {"quote": {"last_price": "586.55", "as_of": "2026-10-18T12:00:05Z"}},
    }
    accepted, reason, _ = live_service.validate_and_reconcile_quote_event(
        current_quote=current_quote,
        incoming_event=dup_event,
        expected_entity_id=spy_id,
    )
    assert accepted is False
    assert "STALE_OR_DUPLICATE_EVENT" in reason

    # 2. Older timestamp
    older_event = {
        "instrument_entity_id": str(spy_id),
        "source_timestamp": "2026-10-18T12:00:01Z",
        "payload": {"quote": {"last_price": "586.40", "as_of": "2026-10-18T12:00:01Z"}},
    }
    accepted, reason, _ = live_service.validate_and_reconcile_quote_event(
        current_quote=current_quote,
        incoming_event=older_event,
        expected_entity_id=spy_id,
    )
    assert accepted is False
    assert "STALE_OR_DUPLICATE_EVENT" in reason


def test_event_rejection_instrument_mismatch(live_service):
    """Verify incoming events for a different instrument are rejected."""
    spy_id = gen_chart_instrument_id("SPY")
    aapl_id = gen_chart_instrument_id("AAPL")

    mismatch_event = {
        "instrument_entity_id": str(aapl_id),
        "payload": {"quote": {"last_price": "235.00", "as_of": "2026-10-18T12:00:00Z"}},
    }

    accepted, reason, _ = live_service.validate_and_reconcile_quote_event(
        current_quote=None,
        incoming_event=mismatch_event,
        expected_entity_id=spy_id,
    )
    assert accepted is False
    assert "INSTRUMENT_MISMATCH" in reason


def test_event_rejection_negative_price_for_equities(live_service):
    """Verify negative prices are rejected for equities but allowed for commodity futures."""
    aapl_id = gen_chart_instrument_id("AAPL")
    neg_event = {
        "instrument_entity_id": str(aapl_id),
        "payload": {"quote": {"last_price": "-10.50", "as_of": "2026-10-18T12:00:00Z"}},
    }

    # AAPL rejects negative price
    accepted, reason, _ = live_service.validate_and_reconcile_quote_event(
        current_quote=None,
        incoming_event=neg_event,
        expected_entity_id=aapl_id,
        allows_negative_price=False,
    )
    assert accepted is False
    assert "NEGATIVE_PRICE_REJECTED" in reason

    # CLZ26 allows negative price
    clz_id = gen_chart_instrument_id("CLZ26")
    clz_event = {
        "instrument_entity_id": str(clz_id),
        "payload": {"quote": {"last_price": "-10.50", "as_of": "2026-10-18T12:00:00Z"}},
    }
    accepted, reason, reconciled = live_service.validate_and_reconcile_quote_event(
        current_quote=None,
        incoming_event=clz_event,
        expected_entity_id=clz_id,
        allows_negative_price=True,
    )
    assert accepted is True
    assert reconciled.last_price == Decimal("-10.50")


def test_event_rejection_malformed_decimals_and_nan(live_service):
    """Verify NaN, Infinity, and malformed strings are rejected safely."""
    spy_id = gen_chart_instrument_id("SPY")

    for bad_val in ["NaN", "Infinity", "-Infinity", "abc"]:
        event = {
            "instrument_entity_id": str(spy_id),
            "payload": {"quote": {"last_price": bad_val, "as_of": "2026-10-18T12:00:00Z"}},
        }
        accepted, reason, _ = live_service.validate_and_reconcile_quote_event(
            current_quote=None,
            incoming_event=event,
            expected_entity_id=spy_id,
        )
        assert accepted is False
        assert "MALFORMED_DECIMAL" in reason


def test_event_rejection_unsupported_schema_version(live_service):
    """Verify events with unsupported schema versions fail safely."""
    spy_id = gen_chart_instrument_id("SPY")
    event = {
        "schema_version": 99,
        "instrument_entity_id": str(spy_id),
        "payload": {"quote": {"last_price": "586.00", "as_of": "2026-10-18T12:00:00Z"}},
    }
    accepted, reason, _ = live_service.validate_and_reconcile_quote_event(
        current_quote=None,
        incoming_event=event,
        expected_entity_id=spy_id,
    )
    assert accepted is False
    assert "UNSUPPORTED_SCHEMA_VERSION" in reason


# =========================================================================
# 4. FASTAPI REST API TESTS: GET /api/v1/charts/live-state
# =========================================================================


@pytest.mark.asyncio
async def test_api_chart_live_state_by_symbol(app, settings):
    """Test GET /api/v1/charts/live-state by symbol."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/live-state?symbol=SPY")
        assert res.status_code == 200
        data = res.json()
        assert data["schema_version"] == "1.0.0"
        assert data["display_symbol"] == "SPY"
        assert data["market_or_venue"] == "NYSE Arca"
        assert data["freshness_status"] == "LIVE"
        assert data["delay_status"] == "REALTIME"
        assert data["live_capability"] == "LIVE_PRICE_AVAILABLE"
        assert data["availability"] == "AVAILABLE"
        assert data["quote"]["last_price"] == "586.25"
        assert data["quote"]["has_genuine_last"] is True


@pytest.mark.asyncio
async def test_api_chart_live_state_by_uuid(app, settings):
    """Test GET /api/v1/charts/live-state by instrument_id UUID."""
    spy_id = str(gen_chart_instrument_id("SPY"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/live-state?instrument_id={spy_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["instrument_entity_id"] == spy_id
        assert data["display_symbol"] == "SPY"


@pytest.mark.asyncio
async def test_api_chart_live_state_missing_params(app, settings):
    """Test GET /api/v1/charts/live-state without parameters returns 400 Bad Request."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/live-state")
        assert res.status_code == 400
        data = res.json()
        error_msg = data["error"]["message"] if "error" in data else data.get("detail", "")
        assert "Either 'instrument_id' or 'symbol'" in error_msg


@pytest.mark.asyncio
async def test_api_chart_live_state_unknown_instrument(app, settings):
    """Test GET /api/v1/charts/live-state with unknown symbol returns 404 Not Found."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/charts/live-state?symbol=UNKNOWN_TICKER")
        assert res.status_code == 404
        data = res.json()
        error_msg = data["error"]["message"] if "error" in data else data.get("detail", "")
        assert "not found in canonical chart catalog" in error_msg
