# Market Data Architecture

## High-Level Architecture
ATLAS owns the canonical Market Data schema. Providers adapt themselves to ATLAS, not the other way around.

```text
Provider-specific response
        │
        ▼
Provider Adapter
        │
        ▼
ATLAS Canonical Market Data
        │
        ▼
Domain Services
```

## Canonical Instrument Identity
Canonical identity is the instrument UUID, reused from the Stage 16-22 Entity Architecture.
**Ticker is not canonical identity.** Tickers/symbols are identifiers managed by the identifier resolution system.

## Financial Numeric Policy
All prices, sizes, volumes, VWAP, etc., use `Decimal`.
Float is explicitly rejected for financial numeric values because binary floating point is not exact.

| Value Type | Python Type |
|---|---|
| price | `CanonicalDecimal` |
| size | `NonNegativeCanonicalDecimal` (or `PositiveCanonicalDecimal`) |
| volume | `NonNegativeCanonicalDecimal` |
| VWAP | `CanonicalDecimal` |
| order count | `int` |
| trade count | `int` |

Float input is rejected unless an explicitly documented safe conversion exists in the Provider Adapter.
For JSON serialization, `Decimal` objects are serialized as strings preserving exact precision (e.g., `{"bid_price": "185.2000"}`).

## Timestamp Policy
All canonical market data timestamps are timezone-aware and normalized to UTC.
Naive datetimes are rejected by Pydantic validation.
Timestamps are serialized as ISO8601 with a `Z` suffix.
If a timestamp source needs semantics, it uses `MarketDataTimestampSource` (e.g., `exchange`, `provider`, `retrieval`, `derived`).

## Market Data Timeliness

| Value | Meaning |
|---|---|
| `real_time` | Source indicates data is live/real-time. |
| `delayed` | Source explicitly delays data. |
| `end_of_day` | Official end-of-day dataset. |
| `historical` | Historical retrieval dataset. |
| `unknown` | ATLAS cannot reliably determine timeliness. |

## Market Data Origin
Lightweight runtime lineage metadata for Market Data responses.

| Field | Type | Purpose |
|---|---|---|
| `provider_key` | `str` | ATLAS Provider that fulfilled request |
| `upstream_source` | `str` | Human/machine-readable source (e.g., FRED, Polygon) |
| `retrieved_at` | `CanonicalDatetime` | UTC time when ATLAS received data |
| `timeliness` | `MarketDataTimeliness` | Timeliness indication |
| `delay_seconds` | `int` | Explicit delay in seconds (if delayed) |
| `source_timestamp` | `CanonicalDatetime` | Original data timestamp (if known) |

**Origin vs Provenance**: `MarketDataOrigin` is runtime lineage metadata. It is NOT the persistent source/evidence lineage handled by Stage 24 `Provenance`. Future Stage 39 ingestion may convert `MarketDataOrigin` into persisted Provenance.

## Market Session

| Session | Meaning |
|---|---|
| `pre_market` | Before regular hours. |
| `regular` | Regular trading hours. |
| `post_market` | After regular hours. |
| `overnight` | Overnight session. |
| `continuous` | 24-hour continuous (e.g., crypto, FX). |
| `unknown` | Cannot be determined. |

## Trade Side

| Side | Meaning |
|---|---|
| `buy` | Buyer was the aggressor side. |
| `sell` | Seller was the aggressor side. |
| `unknown` | Aggressor side unknown. |

## Price Adjustment

| Value | Meaning |
|---|---|
| `raw` | No corporate-action adjustment. |
| `split_adjusted` | Prices adjusted for splits. |
| `total_return` | Adjusted for splits and dividends. |

## Bar Interval

| Canonical Value | Meaning |
|---|---|
| `1s`, `5s`, `15s`, `30s` | Seconds |
| `1m`, `5m`, `15m`, `30m` | Minutes |
| `1h`, `2h`, `4h` | Hours |
| `1d`, `1w`, `1mo` | Days, Weeks, Months |

## Canonical Models

### Quote Model
| Field | Type | Required | Meaning |
|---|---|---|---|
| `instrument_id` | `UUID` | Yes | Canonical instrument ID |
| `as_of` | `CanonicalDatetime` | Yes | UTC timestamp of quote |
| `timestamp_source` | `MarketDataTimestampSource` | No | Source of timestamp |
| `venue_id` | `UUID` | No | Exchange/venue canonical ID |
| `session` | `MarketSession` | No | Trading session |
| `bid_price` | `CanonicalDecimal` | No | Highest buyer price |
| `bid_size` | `NonNegativeCanonicalDecimal` | No | Quantity available at bid |
| `ask_price` | `CanonicalDecimal` | No | Lowest seller price |
| `ask_size` | `NonNegativeCanonicalDecimal` | No | Quantity available at ask |

**Rules**:
- Must have at least bid or ask.
- If a size is present, its corresponding price must be present.
- Crossed quotes (`bid_price >= ask_price`) are explicitly allowed as they reflect real fragmented market behavior.
- Last trade is NOT inside Quote to maintain clean semantics.

### Trade Model
| Field | Type | Required | Meaning |
|---|---|---|---|
| `instrument_id` | `UUID` | Yes | Canonical instrument ID |
| `timestamp` | `CanonicalDatetime` | Yes | UTC timestamp |
| `timestamp_source` | `MarketDataTimestampSource` | No | Timestamp origin |
| `venue_id` | `UUID` | No | Exchange/venue canonical ID |
| `session` | `MarketSession` | No | Trading session |
| `price` | `CanonicalDecimal` | Yes | Executed price (can be negative) |
| `size` | `PositiveCanonicalDecimal` | Yes | Executed quantity (> 0) |
| `trade_id` | `str` | No | Provider trade ID (<= 128) |
| `sequence` | `int` | No | Monotonically increasing sequence |
| `side` | `TradeSide` | No | Aggressor side |

### OHLCV Bar Model
| Field | Type | Required | Meaning |
|---|---|---|---|
| `instrument_id` | `UUID` | Yes | Canonical instrument ID |
| `interval` | `BarInterval` | Yes | Time interval |
| `start_time` | `CanonicalDatetime` | Yes | UTC start time |
| `end_time` | `CanonicalDatetime` | Yes | UTC end time |
| `venue_id` | `UUID` | No | Exchange/venue canonical ID |
| `session` | `MarketSession` | No | Trading session |
| `open` | `CanonicalDecimal` | Yes | Open price (can be negative) |
| `high` | `CanonicalDecimal` | Yes | Highest price |
| `low` | `CanonicalDecimal` | Yes | Lowest price |
| `close` | `CanonicalDecimal` | Yes | Closing price |
| `volume` | `NonNegativeCanonicalDecimal`| No | Traded volume |
| `vwap` | `CanonicalDecimal` | No | Volume-weighted average price |
| `trade_count` | `int` | No | Number of trades |
| `is_final` | `bool` | Yes | Source guarantee of finality |

**Rules**:
- `start_time < end_time`
- Envelope bounds: `high >= open/low/close` and `low <= open/high/close`.

### Order Book Models

**OrderBookLevel**:
- `price: CanonicalDecimal`
- `size: NonNegativeCanonicalDecimal`
- `order_count: int` (optional)

**OrderBookSnapshot**:
- `instrument_id: UUID`
- `as_of: CanonicalDatetime`
- `timestamp_source: MarketDataTimestampSource`
- `venue_id: UUID`
- `bids: tuple[OrderBookLevel, ...]`
- `asks: tuple[OrderBookLevel, ...]`

**Rules**:
- Bids must be sorted strictly descending by price.
- Asks must be sorted strictly ascending by price.
- Duplicate prices per side are rejected.
- Crossed books are representable.

### Market Snapshot Model
| Field | Type | Required | Meaning |
|---|---|---|---|
| `instrument_id` | `UUID` | Yes | Canonical instrument ID |
| `as_of` | `CanonicalDatetime` | Yes | UTC timestamp |
| `venue_id` | `UUID` | No | Exchange/venue canonical ID |
| `session` | `MarketSession` | No | Trading session |
| `quote` | `Quote` | No | Current/latest quote |
| `last_trade` | `Trade` | No | Last executed trade |
| `session_open` | `CanonicalDecimal` | No | Session open price |
| `session_high` | `CanonicalDecimal` | No | Session high price |
| `session_low` | `CanonicalDecimal` | No | Session low price |
| `previous_close`| `CanonicalDecimal` | No | Previous session close |
| `session_volume`| `NonNegativeCanonicalDecimal`| No | Session volume |
| `vwap` | `CanonicalDecimal` | No | Volume-weighted average price |

**Rules**:
- Must not be entirely empty.
- Nested Quotes/Trades must match the Snapshot `instrument_id`.
- Change/percent-change fields are deliberately excluded as derived data.

## Market Data Operations

| Operation | Purpose |
|---|---|
| `quote` | Retrieve live or recent canonical quotes. |
| `historical_bars` | Retrieve historical OHLCV data. |
| `trades` | Retrieve historical executed trades. |
| `order_book` | Retrieve market depth snapshot. |
| `snapshot` | Retrieve a point-in-time point market summary. |

**Provider Capabilities**:
A Provider claiming `ProviderDomain.MARKET_DATA` domain does not imply it supports all specific `MarketDataOperation` values. Its `MarketDataProviderCapabilities` object dictates explicit supported canonical operations.

## Request/Response Contracts

**QuoteRequest**: `instrument_ids: tuple[UUID, ...]` (1-100 max, no duplicates).
**QuoteResponse**: Contains `origin`, `quotes: tuple[Quote]`, and `unavailable_instrument_ids`.

**HistoricalBarsRequest**: `instrument_id`, `interval`, `start`, `end`, `adjustment`, `limit` (max 10k). Bound requirements apply.
**HistoricalBarsResponse**: Contains `origin`, `bars: tuple[OHLCVBar]` ordered chronologically.

**TradesRequest**: `instrument_id`, `start`, `end`, `limit` (max 10k). Bound requirements apply.
**TradesResponse**: Contains `origin`, `trades: tuple[Trade]` ordered chronologically.

**OrderBookRequest**: `instrument_id`, `depth` (1-100 max).
**OrderBookResponse**: Contains `origin`, `book: OrderBookSnapshot`.

**MarketSnapshotRequest**: `instrument_ids: tuple[UUID, ...]` (1-100 max).
**MarketSnapshotResponse**: Contains `origin`, `snapshots`, `unavailable_instrument_ids`.

*All responses contain a required `MarketDataOrigin` metadata field.*

## Provider Protocols
Stage 33 implements specific Provider Protocols instead of a single massive interface:
- `QuoteMarketDataProvider`
- `HistoricalBarsMarketDataProvider`
- `TradesMarketDataProvider`
- `OrderBookMarketDataProvider`
- `SnapshotMarketDataProvider`

## OpenBB Status
OpenBB is registered for the Market Data domain, but no Stage 33 canonical Market Data operation is executed yet.
OpenBB `MarketDataProviderCapabilities.operations` is explicitly empty.

## Boundary Principles
- **No Generic Executor**: `execute(operation: str, payload: dict)` is forbidden.
- **No Pandas/Polars**: `DataFrame` is NOT used as a canonical API contract.
- **Provider Leakage**: Provider credentials, routing states, and keys do NOT leak into canonical requests.
- **No Fake API**: Stage 33 creates NO PostgreSQL tables, NO Market Data REST API endpoints, NO database queries during model validation, and performs NO Market Data network requests.
