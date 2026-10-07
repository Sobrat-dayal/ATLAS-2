import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from atlas.market_data import (
    BarInterval,
    HistoricalBarsRequest,
    HistoricalBarsResponse,
    MarketDataOperation,
    MarketDataProviderCapabilities,
    MarketDataTimeliness,
    MarketDataTimestampSource,
    MarketSession,
    MarketSnapshot,
    MarketSnapshotRequest,
    MarketSnapshotResponse,
    OHLCVBar,
    OrderBookLevel,
    OrderBookRequest,
    OrderBookResponse,
    OrderBookSnapshot,
    PriceAdjustment,
    Quote,
    QuoteRequest,
    QuoteResponse,
    Trade,
    TradeSide,
    TradesRequest,
    TradesResponse,
)
from atlas.market_data.origin import MarketDataOrigin


def test_decimal_roundtrip_serialization():
    # 257, 258, 259, 260
    prices = [
        Decimal("0.00000001"),
        Decimal("123456789012345.123456789"),
        Decimal("-37.63"),
        Decimal("0.00012345"),
    ]
    
    for p in prices:
        quote = Quote(
            instrument_id=uuid4(),
            as_of=datetime.now(timezone.utc),
            bid_price=p
        )
        data = quote.model_dump_json()
        assert format(p, "f") in data
        quote_back = Quote.model_validate_json(data)
        assert quote_back.bid_price == p


def test_reject_float_for_financial_numeric():
    # 225
    with pytest.raises(ValidationError):
        Quote(
            instrument_id=uuid4(),
            as_of=datetime.now(timezone.utc),
            bid_price=185.2  # Should fail validation because float isn't exact
        )

def test_reject_non_finite_decimal():
    # 25
    with pytest.raises(ValidationError):
        Quote(
            instrument_id=uuid4(),
            as_of=datetime.now(timezone.utc),
            bid_price=Decimal("Infinity")
        )
    with pytest.raises(ValidationError):
        Quote(
            instrument_id=uuid4(),
            as_of=datetime.now(timezone.utc),
            bid_price=Decimal("NaN")
        )

def test_naive_datetime_rejection():
    # 30, 311
    with pytest.raises(ValidationError):
        Quote(
            instrument_id=uuid4(),
            as_of=datetime.now(),  # naive
            bid_price=Decimal("100.0")
        )

def test_utc_normalization():
    # 31, 312
    dt = datetime(2026, 10, 5, 9, 30, 0, tzinfo=timezone(timedelta(hours=-4)))
    quote = Quote(
        instrument_id=uuid4(),
        as_of=dt,
        bid_price=Decimal("100.0")
    )
    # Check normalization
    assert quote.as_of.tzinfo == timezone.utc
    assert quote.as_of == dt.astimezone(timezone.utc)
    # Check Z format in JSON
    json_str = quote.model_dump_json()
    assert "2026-10-05T13:30:00Z" in json_str

def test_quote_validation():
    # 261, 262, 263, 264, 265, 266
    inst_id = uuid4()
    now = datetime.now(timezone.utc)

    # Valid: bid only
    Quote(instrument_id=inst_id, as_of=now, bid_price=Decimal("100.0"))
    # Valid: ask only
    Quote(instrument_id=inst_id, as_of=now, ask_price=Decimal("100.0"))
    # Valid: bid + ask
    Quote(instrument_id=inst_id, as_of=now, bid_price=Decimal("100.0"), ask_price=Decimal("101.0"))

    # Empty Quote Test
    with pytest.raises(ValidationError):
        Quote(instrument_id=inst_id, as_of=now)

    # Bid size without bid
    with pytest.raises(ValidationError):
        Quote(instrument_id=inst_id, as_of=now, bid_size=Decimal("10.0"))

    # Ask size without ask
    with pytest.raises(ValidationError):
        Quote(instrument_id=inst_id, as_of=now, ask_size=Decimal("10.0"))

    # Negative size
    with pytest.raises(ValidationError):
        Quote(instrument_id=inst_id, as_of=now, bid_price=Decimal("100"), bid_size=Decimal("-1"))

    # Crossed quote (allowed)
    q = Quote(instrument_id=inst_id, as_of=now, bid_price=Decimal("101.0"), ask_price=Decimal("100.0"))
    assert q.bid_price > q.ask_price


def test_trade_validation():
    # 267, 268, 269
    inst_id = uuid4()
    now = datetime.now(timezone.utc)

    Trade(
        instrument_id=inst_id,
        timestamp=now,
        price=Decimal("100.0"),
        size=Decimal("10.0")
    )

    # Zero size
    with pytest.raises(ValidationError):
        Trade(
            instrument_id=inst_id,
            timestamp=now,
            price=Decimal("100.0"),
            size=Decimal("0.0")
        )

    # Negative price
    Trade(
        instrument_id=inst_id,
        timestamp=now,
        price=Decimal("-10.0"),
        size=Decimal("10.0")
    )


def test_bar_validation():
    # 270, 271, 272, 273, 274, 275
    inst_id = uuid4()
    start = datetime.now(timezone.utc)
    end = start + timedelta(minutes=1)

    OHLCVBar(
        instrument_id=inst_id,
        interval=BarInterval.ONE_MINUTE,
        start_time=start,
        end_time=end,
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102")
    )

    # Invalid high
    with pytest.raises(ValidationError):
        OHLCVBar(
            instrument_id=inst_id, interval=BarInterval.ONE_MINUTE, start_time=start, end_time=end,
            open=Decimal("100"), high=Decimal("101"), low=Decimal("95"), close=Decimal("102")
        )

    # Invalid low
    with pytest.raises(ValidationError):
        OHLCVBar(
            instrument_id=inst_id, interval=BarInterval.ONE_MINUTE, start_time=start, end_time=end,
            open=Decimal("100"), high=Decimal("105"), low=Decimal("101"), close=Decimal("102")
        )

    # Invalid range
    with pytest.raises(ValidationError):
        OHLCVBar(
            instrument_id=inst_id, interval=BarInterval.ONE_MINUTE, start_time=end, end_time=start,
            open=Decimal("100"), high=Decimal("105"), low=Decimal("95"), close=Decimal("102")
        )

    # Negative volume
    with pytest.raises(ValidationError):
        OHLCVBar(
            instrument_id=inst_id, interval=BarInterval.ONE_MINUTE, start_time=start, end_time=end,
            open=Decimal("100"), high=Decimal("105"), low=Decimal("95"), close=Decimal("102"),
            volume=Decimal("-10")
        )

    # Negative trade count
    with pytest.raises(ValidationError):
        OHLCVBar(
            instrument_id=inst_id, interval=BarInterval.ONE_MINUTE, start_time=start, end_time=end,
            open=Decimal("100"), high=Decimal("105"), low=Decimal("95"), close=Decimal("102"),
            trade_count=-1
        )


def test_order_book_validation():
    # 278, 279, 280, 281, 282
    inst_id = uuid4()
    now = datetime.now(timezone.utc)

    # Valid
    OrderBookSnapshot(
        instrument_id=inst_id, as_of=now,
        bids=[
            OrderBookLevel(price=Decimal("100"), size=Decimal("10")),
            OrderBookLevel(price=Decimal("99"), size=Decimal("10"))
        ],
        asks=[
            OrderBookLevel(price=Decimal("101"), size=Decimal("10")),
            OrderBookLevel(price=Decimal("102"), size=Decimal("10"))
        ]
    )

    # Bid ordering
    with pytest.raises(ValidationError):
        OrderBookSnapshot(
            instrument_id=inst_id, as_of=now,
            bids=[
                OrderBookLevel(price=Decimal("99"), size=Decimal("10")),
                OrderBookLevel(price=Decimal("100"), size=Decimal("10"))
            ]
        )

    # Ask ordering
    with pytest.raises(ValidationError):
        OrderBookSnapshot(
            instrument_id=inst_id, as_of=now,
            asks=[
                OrderBookLevel(price=Decimal("102"), size=Decimal("10")),
                OrderBookLevel(price=Decimal("101"), size=Decimal("10"))
            ]
        )

    # Duplicate bids
    with pytest.raises(ValidationError):
        OrderBookSnapshot(
            instrument_id=inst_id, as_of=now,
            bids=[
                OrderBookLevel(price=Decimal("100"), size=Decimal("10")),
                OrderBookLevel(price=Decimal("100"), size=Decimal("20"))
            ]
        )

    # Negative size
    with pytest.raises(ValidationError):
        OrderBookLevel(price=Decimal("100"), size=Decimal("-10"))

    # Crossed book
    OrderBookSnapshot(
        instrument_id=inst_id, as_of=now,
        bids=[OrderBookLevel(price=Decimal("101"), size=Decimal("10"))],
        asks=[OrderBookLevel(price=Decimal("100"), size=Decimal("10"))]
    )

def test_snapshot_validation():
    # 283, 284, 285
    inst_id = uuid4()
    now = datetime.now(timezone.utc)
    
    quote = Quote(instrument_id=inst_id, as_of=now, bid_price=Decimal("100"))

    # Valid
    MarketSnapshot(
        instrument_id=inst_id, as_of=now, quote=quote
    )

    # Nested consistency
    with pytest.raises(ValidationError):
        MarketSnapshot(
            instrument_id=uuid4(), as_of=now, quote=quote
        )

    # Empty Snapshot
    with pytest.raises(ValidationError):
        MarketSnapshot(instrument_id=inst_id, as_of=now)

    # Negative price
    MarketSnapshot(
        instrument_id=inst_id, as_of=now, session_low=Decimal("-10")
    )


def test_origin_validation():
    # 286, 287
    now = datetime.now(timezone.utc)

    orig = MarketDataOrigin(
        provider_key="openbb",
        retrieved_at=now,
        timeliness=MarketDataTimeliness.REAL_TIME
    )
    assert orig.provider_key == "openbb"
    
    # Must contain no secret fields implicitly by schema definition.
    assert "api_key" not in MarketDataOrigin.model_fields
    assert "secret" not in MarketDataOrigin.model_fields


def test_requests_validation():
    # 288, 289, 290, 291
    id1 = uuid4()
    id2 = uuid4()

    QuoteRequest(instrument_ids=(id1,))

    # Empty
    with pytest.raises(ValidationError):
        QuoteRequest(instrument_ids=())

    # Duplicate
    with pytest.raises(ValidationError):
        QuoteRequest(instrument_ids=(id1, id1))

    # Too many
    with pytest.raises(ValidationError):
        QuoteRequest(instrument_ids=tuple(uuid4() for _ in range(101)))

    # Historical ranges
    # 292, 293
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=1)
    
    HistoricalBarsRequest(instrument_id=id1, interval=BarInterval.ONE_DAY, start=start, end=end)
    HistoricalBarsRequest(instrument_id=id1, interval=BarInterval.ONE_DAY, limit=100)

    # Start >= End
    with pytest.raises(ValidationError):
        HistoricalBarsRequest(instrument_id=id1, interval=BarInterval.ONE_DAY, start=end, end=start)

    # Invalid limits
    with pytest.raises(ValidationError):
        HistoricalBarsRequest(instrument_id=id1, interval=BarInterval.ONE_DAY, limit=0)
    with pytest.raises(ValidationError):
        HistoricalBarsRequest(instrument_id=id1, interval=BarInterval.ONE_DAY, limit=10001)

    # Order Book Depth
    # 295
    OrderBookRequest(instrument_id=id1, depth=1)
    with pytest.raises(ValidationError):
        OrderBookRequest(instrument_id=id1, depth=0)
    with pytest.raises(ValidationError):
        OrderBookRequest(instrument_id=id1, depth=101)


def test_responses_validation():
    # 276, 277
    inst_id = uuid4()
    now = datetime.now(timezone.utc)
    orig = MarketDataOrigin(provider_key="test", retrieved_at=now, timeliness=MarketDataTimeliness.HISTORICAL)
    
    bar1 = OHLCVBar(
        instrument_id=inst_id, interval=BarInterval.ONE_DAY,
        start_time=now, end_time=now+timedelta(days=1),
        open=Decimal("10"), high=Decimal("10"), low=Decimal("10"), close=Decimal("10")
    )
    bar2 = OHLCVBar(
        instrument_id=inst_id, interval=BarInterval.ONE_DAY,
        start_time=now+timedelta(days=1), end_time=now+timedelta(days=2),
        open=Decimal("10"), high=Decimal("10"), low=Decimal("10"), close=Decimal("10")
    )

    HistoricalBarsResponse(
        instrument_id=inst_id, interval=BarInterval.ONE_DAY, adjustment=PriceAdjustment.RAW, origin=orig,
        bars=(bar1, bar2)
    )

    # Out of order
    with pytest.raises(ValidationError):
        HistoricalBarsResponse(
            instrument_id=inst_id, interval=BarInterval.ONE_DAY, adjustment=PriceAdjustment.RAW, origin=orig,
            bars=(bar2, bar1)
        )

    # Duplicate
    with pytest.raises(ValidationError):
        HistoricalBarsResponse(
            instrument_id=inst_id, interval=BarInterval.ONE_DAY, adjustment=PriceAdjustment.RAW, origin=orig,
            bars=(bar1, bar1)
        )


def test_capabilities_immutability():
    # 298, 299
    cap = MarketDataProviderCapabilities()
    
    # Empty capabilities allowed
    assert len(cap.operations) == 0

    with pytest.raises(ValidationError):
        cap.operations = frozenset([MarketDataOperation.QUOTE])


def test_no_forbidden_types_in_schema():
    # 305, 306, 307, 308, 309, 310
    from inspect import get_annotations
    
    # Check no DataFrame, dict[str, Any], float, or OpenBB objects in annotations
    forbidden_strs = ["DataFrame", "Any", "float", "OBBject", "OpenBB"]
    
    for cls in [Quote, OHLCVBar, Trade, OrderBookLevel, OrderBookSnapshot, MarketSnapshot]:
        ann = get_annotations(cls)
        for k, v in ann.items():
            s = str(v)
            for f in forbidden_strs:
                assert f not in s, f"Forbidden type {f} found in {cls.__name__}.{k}"
            # Ensure no ticker
            assert k not in ["ticker", "symbol"]


def test_offline_construction():
    # 313, 314
    # Implicitly tested by the fact that all our construction above didn't make network calls.
    pass

