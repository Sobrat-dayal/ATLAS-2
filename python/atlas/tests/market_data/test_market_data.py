import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from atlas.market_data import (
    BarInterval,
    HistoricalBarsRequest,
    HistoricalBarsResponse,
    MarketDataOrigin,
    MarketDataTimeliness,
    MarketSnapshot,
    OHLCVBar,
    OrderBookLevel,
    OrderBookRequest,
    OrderBookSnapshot,
    PriceAdjustment,
    Quote,
    QuoteRequest,
    Trade,
    TradesResponse,
)


# Helper for UTC now
def now_utc():
    return datetime.now(timezone.utc)


def test_quote_valid():
    inst_id = uuid.uuid4()
    q = Quote(
        instrument_id=inst_id,
        as_of=now_utc(),
        bid_price=Decimal("150.00"),
        bid_size=Decimal("100"),
        ask_price=Decimal("150.10"),
        ask_size=Decimal("200"),
    )
    assert q.bid_price == Decimal("150.00")


def test_quote_bid_only():
    inst_id = uuid.uuid4()
    q = Quote(
        instrument_id=inst_id, as_of=now_utc(), bid_price=Decimal("150.00"), bid_size=Decimal("100")
    )
    assert q.ask_price is None


def test_quote_ask_only():
    inst_id = uuid.uuid4()
    q = Quote(
        instrument_id=inst_id, as_of=now_utc(), ask_price=Decimal("150.00"), ask_size=Decimal("100")
    )
    assert q.bid_price is None


def test_quote_empty_reject():
    inst_id = uuid.uuid4()
    with pytest.raises(ValidationError, match="must have at least one of bid_price or ask_price"):
        Quote(instrument_id=inst_id, as_of=now_utc())


def test_quote_size_without_price():
    inst_id = uuid.uuid4()
    with pytest.raises(ValidationError, match="bid_size must also have bid_price"):
        Quote(
            instrument_id=inst_id, as_of=now_utc(), ask_price=Decimal("10"), bid_size=Decimal("10")
        )

    with pytest.raises(ValidationError, match="ask_size must also have ask_price"):
        Quote(
            instrument_id=inst_id, as_of=now_utc(), bid_price=Decimal("10"), ask_size=Decimal("10")
        )


def test_quote_negative_size():
    inst_id = uuid.uuid4()
    with pytest.raises(ValidationError, match="non-negative"):
        Quote(
            instrument_id=inst_id, as_of=now_utc(), bid_price=Decimal("10"), bid_size=Decimal("-5")
        )


def test_crossed_quote():
    inst_id = uuid.uuid4()
    q = Quote(
        instrument_id=inst_id,
        as_of=now_utc(),
        bid_price=Decimal("105.00"),
        bid_size=Decimal("10"),
        ask_price=Decimal("104.00"),
        ask_size=Decimal("10"),
    )
    assert q.bid_price > q.ask_price


def test_trade_valid():
    t = Trade(
        instrument_id=uuid.uuid4(),
        timestamp=now_utc(),
        price=Decimal("150.00"),
        size=Decimal("100"),
    )
    assert t.price == Decimal("150.00")


def test_trade_negative_price():
    t = Trade(
        instrument_id=uuid.uuid4(),
        timestamp=now_utc(),
        price=Decimal("-37.50"),
        size=Decimal("100"),
    )
    assert t.price == Decimal("-37.50")


def test_trade_zero_size_reject():
    with pytest.raises(ValidationError, match="strictly positive"):
        Trade(
            instrument_id=uuid.uuid4(),
            timestamp=now_utc(),
            price=Decimal("150.00"),
            size=Decimal("0"),
        )


def test_trade_negative_size_reject():
    with pytest.raises(ValidationError, match="strictly positive"):
        Trade(
            instrument_id=uuid.uuid4(),
            timestamp=now_utc(),
            price=Decimal("150.00"),
            size=Decimal("-10"),
        )


def test_bar_valid():
    t1 = now_utc()
    t2 = t1 + timedelta(minutes=1)
    b = OHLCVBar(
        instrument_id=uuid.uuid4(),
        interval=BarInterval.ONE_MINUTE,
        start_time=t1,
        end_time=t2,
        open=Decimal("100"),
        high=Decimal("105"),
        low=Decimal("95"),
        close=Decimal("102"),
    )
    assert b.high == Decimal("105")


def test_bar_invalid_high():
    t1 = now_utc()
    t2 = t1 + timedelta(minutes=1)
    with pytest.raises(ValidationError, match="high must be >="):
        OHLCVBar(
            instrument_id=uuid.uuid4(),
            interval=BarInterval.ONE_MINUTE,
            start_time=t1,
            end_time=t2,
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("95"),
            close=Decimal("102"),
        )


def test_bar_invalid_low():
    t1 = now_utc()
    t2 = t1 + timedelta(minutes=1)
    with pytest.raises(ValidationError, match="low must be <="):
        OHLCVBar(
            instrument_id=uuid.uuid4(),
            interval=BarInterval.ONE_MINUTE,
            start_time=t1,
            end_time=t2,
            open=Decimal("100"),
            high=Decimal("105"),
            low=Decimal("101"),
            close=Decimal("102"),
        )


def test_bar_invalid_time():
    t1 = now_utc()
    t2 = t1 - timedelta(minutes=1)
    with pytest.raises(ValidationError, match="start_time must be strictly before"):
        OHLCVBar(
            instrument_id=uuid.uuid4(),
            interval=BarInterval.ONE_MINUTE,
            start_time=t1,
            end_time=t2,
            open=Decimal("10"),
            high=Decimal("10"),
            low=Decimal("10"),
            close=Decimal("10"),
        )


def test_bar_negative_volume():
    t1 = now_utc()
    t2 = t1 + timedelta(minutes=1)
    with pytest.raises(ValidationError, match="non-negative"):
        OHLCVBar(
            instrument_id=uuid.uuid4(),
            interval=BarInterval.ONE_MINUTE,
            start_time=t1,
            end_time=t2,
            open=Decimal("10"),
            high=Decimal("10"),
            low=Decimal("10"),
            close=Decimal("10"),
            volume=Decimal("-100"),
        )


def test_bar_negative_trade_count():
    t1 = now_utc()
    t2 = t1 + timedelta(minutes=1)
    with pytest.raises(ValidationError):
        OHLCVBar(
            instrument_id=uuid.uuid4(),
            interval=BarInterval.ONE_MINUTE,
            start_time=t1,
            end_time=t2,
            open=Decimal("10"),
            high=Decimal("10"),
            low=Decimal("10"),
            close=Decimal("10"),
            trade_count=-5,
        )


def test_order_book_valid():
    bids = (
        OrderBookLevel(price=Decimal("100"), size=Decimal("10")),
        OrderBookLevel(price=Decimal("99"), size=Decimal("20")),
    )
    asks = (
        OrderBookLevel(price=Decimal("101"), size=Decimal("10")),
        OrderBookLevel(price=Decimal("102"), size=Decimal("20")),
    )
    ob = OrderBookSnapshot(instrument_id=uuid.uuid4(), as_of=now_utc(), bids=bids, asks=asks)
    assert ob.bids[0].price == Decimal("100")


def test_order_book_bid_ordering():
    bids = (
        OrderBookLevel(price=Decimal("99"), size=Decimal("10")),
        OrderBookLevel(price=Decimal("100"), size=Decimal("20")),
    )
    with pytest.raises(ValidationError, match="strictly descending"):
        OrderBookSnapshot(instrument_id=uuid.uuid4(), as_of=now_utc(), bids=bids)


def test_order_book_ask_ordering():
    asks = (
        OrderBookLevel(price=Decimal("102"), size=Decimal("10")),
        OrderBookLevel(price=Decimal("101"), size=Decimal("20")),
    )
    with pytest.raises(ValidationError, match="strictly ascending"):
        OrderBookSnapshot(instrument_id=uuid.uuid4(), as_of=now_utc(), asks=asks)


def test_order_book_duplicate_level():
    bids = (
        OrderBookLevel(price=Decimal("100"), size=Decimal("10")),
        OrderBookLevel(price=Decimal("100"), size=Decimal("20")),
    )
    with pytest.raises(ValidationError, match="Duplicate price"):
        OrderBookSnapshot(instrument_id=uuid.uuid4(), as_of=now_utc(), bids=bids)


def test_crossed_book():
    bids = (OrderBookLevel(price=Decimal("102"), size=Decimal("10")),)
    asks = (OrderBookLevel(price=Decimal("101"), size=Decimal("10")),)
    ob = OrderBookSnapshot(instrument_id=uuid.uuid4(), as_of=now_utc(), bids=bids, asks=asks)
    assert ob.bids[0].price > ob.asks[0].price


def test_snapshot_empty():
    with pytest.raises(ValidationError, match="must contain at least one piece"):
        MarketSnapshot(instrument_id=uuid.uuid4(), as_of=now_utc())


def test_snapshot_identity_consistency():
    inst_id = uuid.uuid4()
    other_id = uuid.uuid4()

    q = Quote(
        instrument_id=other_id, as_of=now_utc(), bid_price=Decimal("10"), bid_size=Decimal("10")
    )
    with pytest.raises(ValidationError, match="Quote instrument_id must match"):
        MarketSnapshot(instrument_id=inst_id, as_of=now_utc(), quote=q)


def test_quote_request_batch_bounds():
    with pytest.raises(ValidationError):
        QuoteRequest(instrument_ids=())

    ids = tuple(uuid.uuid4() for _ in range(101))
    with pytest.raises(ValidationError):
        QuoteRequest(instrument_ids=ids)


def test_quote_request_duplicates():
    id1 = uuid.uuid4()
    with pytest.raises(ValidationError, match="Duplicate"):
        QuoteRequest(instrument_ids=(id1, id1))


def test_historical_request_bounds():
    with pytest.raises(ValidationError, match="must specify at least start/end"):
        HistoricalBarsRequest(instrument_id=uuid.uuid4(), interval=BarInterval.ONE_MINUTE)

    t1 = now_utc()
    t2 = t1 - timedelta(minutes=1)
    with pytest.raises(ValidationError, match="strictly before"):
        HistoricalBarsRequest(
            instrument_id=uuid.uuid4(), interval=BarInterval.ONE_MINUTE, start=t1, end=t2
        )


def test_historical_request_limit():
    with pytest.raises(ValidationError):
        HistoricalBarsRequest(instrument_id=uuid.uuid4(), interval=BarInterval.ONE_MINUTE, limit=0)


def test_order_book_request_depth():
    with pytest.raises(ValidationError):
        OrderBookRequest(instrument_id=uuid.uuid4(), depth=0)

    with pytest.raises(ValidationError):
        OrderBookRequest(instrument_id=uuid.uuid4(), depth=101)


def test_bar_response_ordering():
    origin = MarketDataOrigin(
        provider_key="test", retrieved_at=now_utc(), timeliness=MarketDataTimeliness.REAL_TIME
    )
    t1 = now_utc()
    t2 = t1 + timedelta(minutes=1)

    b1 = OHLCVBar(
        instrument_id=uuid.uuid4(),
        interval=BarInterval.ONE_MINUTE,
        start_time=t1,
        end_time=t2,
        open=Decimal("1"),
        high=Decimal("1"),
        low=Decimal("1"),
        close=Decimal("1"),
    )
    b2 = OHLCVBar(
        instrument_id=uuid.uuid4(),
        interval=BarInterval.ONE_MINUTE,
        start_time=t2,
        end_time=t2 + timedelta(minutes=1),
        open=Decimal("1"),
        high=Decimal("1"),
        low=Decimal("1"),
        close=Decimal("1"),
    )

    with pytest.raises(ValidationError, match="ordered chronologically"):
        HistoricalBarsResponse(
            instrument_id=uuid.uuid4(),
            interval=BarInterval.ONE_MINUTE,
            adjustment=PriceAdjustment.RAW,
            origin=origin,
            bars=(b2, b1),
        )

    with pytest.raises(ValidationError, match="Duplicate bar"):
        HistoricalBarsResponse(
            instrument_id=uuid.uuid4(),
            interval=BarInterval.ONE_MINUTE,
            adjustment=PriceAdjustment.RAW,
            origin=origin,
            bars=(b1, b1),
        )


def test_trade_response_ordering():
    origin = MarketDataOrigin(
        provider_key="test", retrieved_at=now_utc(), timeliness=MarketDataTimeliness.REAL_TIME
    )
    t1 = now_utc()
    t2 = t1 + timedelta(minutes=1)

    tr1 = Trade(
        instrument_id=uuid.uuid4(), timestamp=t1, price=Decimal("1"), size=Decimal("1"), sequence=1
    )
    tr2 = Trade(
        instrument_id=uuid.uuid4(), timestamp=t1, price=Decimal("1"), size=Decimal("1"), sequence=2
    )
    tr3 = Trade(
        instrument_id=uuid.uuid4(), timestamp=t2, price=Decimal("1"), size=Decimal("1"), sequence=3
    )

    with pytest.raises(ValidationError, match="ordered chronologically"):
        TradesResponse(instrument_id=uuid.uuid4(), origin=origin, trades=(tr3, tr1))

    with pytest.raises(ValidationError, match="ordered by sequence"):
        TradesResponse(instrument_id=uuid.uuid4(), origin=origin, trades=(tr2, tr1))


def test_decimal_roundtrip():
    q = Quote(
        instrument_id=uuid.uuid4(),
        as_of=now_utc(),
        bid_price=Decimal("123456789012345.123456789"),
        bid_size=Decimal("0.00000001"),
    )
    json_data = q.model_dump_json()
    assert '"123456789012345.123456789"' in json_data
    assert '"0.00000001"' in json_data

    q2 = Quote.model_validate_json(json_data)
    assert q2.bid_price == Decimal("123456789012345.123456789")
    assert q2.bid_size == Decimal("0.00000001")


def test_float_rejection():
    with pytest.raises(ValidationError, match="Binary floats are rejected"):
        Quote(
            instrument_id=uuid.uuid4(),
            as_of=now_utc(),
            bid_price=150.2,  # Float
            bid_size=Decimal("100"),
        )


def test_nan_infinity_rejection():
    with pytest.raises(ValidationError, match="finite"):
        Quote(
            instrument_id=uuid.uuid4(),
            as_of=now_utc(),
            bid_price=Decimal("Infinity"),
            bid_size=Decimal("100"),
        )


def test_naive_datetime_rejection():
    with pytest.raises(ValidationError, match="timezone-aware"):
        Quote(
            instrument_id=uuid.uuid4(),
            as_of=datetime.now(),  # Naive
            bid_price=Decimal("100"),
            bid_size=Decimal("100"),
        )


def test_origin_no_credentials():
    origin = MarketDataOrigin(
        provider_key="test",
        upstream_source="test_source",
        retrieved_at=now_utc(),
        timeliness=MarketDataTimeliness.REAL_TIME,
    )
    # Ensure there are no credential fields in the model
    assert "api_key" not in origin.model_dump()
    assert "secret" not in origin.model_dump()


def test_fractional_volume_roundtrip():
    b = OHLCVBar(
        instrument_id=uuid.uuid4(),
        interval=BarInterval.ONE_MINUTE,
        start_time=now_utc(),
        end_time=now_utc() + timedelta(minutes=1),
        open=Decimal("100"),
        high=Decimal("100"),
        low=Decimal("100"),
        close=Decimal("100"),
        volume=Decimal("0.00012345"),
    )
    json_data = b.model_dump_json()
    assert '"0.00012345"' in json_data
    b2 = OHLCVBar.model_validate_json(json_data)
    assert b2.volume == Decimal("0.00012345")
