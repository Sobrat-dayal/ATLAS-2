# Market Data Architecture

## Overview
ATLAS owns the canonical Market Data schema. Market Data encompasses financial metrics, observations, and points-in-time pricing derived from external data sources (Providers). This architecture enforces a strict boundary between Provider-specific objects and the canonical representation required by internal ATLAS domain services.

The flow is strictly unidirectional for normalization:
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

## Identity
- **Canonical identity**: All canonical Market Data models reference an instrument or entity UUID, leveraging the Stage 17 entity/instrument architecture.
- **Ticker**: A ticker/symbol is treated as an identifier or alias, NOT the canonical identity. Provider adapters must resolve symbols to UUIDs prior to or during integration.

## Numeric Policy
- **prices, sizes, volumes, VWAP**: Use financially precise `Decimal` representations. 
- **No binary floats**: Floating point errors are unacceptable in canonical financial data. Binary float inputs are rejected unless explicitly and safely converted (e.g., via adapter normalization).
- **Serialization**: `Decimal` fields serialize as strings (e.g., `"185.2000"`) in JSON responses to avoid browser/client precision loss. 

## Timestamps
- All canonical Market Data timestamps are **timezone-aware** and **UTC-normalized**. Naive datetime objects are rejected.

## Origin & Provenance
- `MarketDataOrigin` is lightweight runtime source metadata attached to canonical responses. It captures `provider_key`, `retrieved_at`, and `timeliness`.
- `Provenance` (Stage 24) remains the authoritative persistent lineage system. Future ingestion (Stage 39) will convert `MarketDataOrigin` into persistent `Provenance` records.

## Enums
- **MarketSession**: Defines market sessions (e.g., `pre_market`, `regular`, `post_market`, `continuous`, `unknown`).
- **BarInterval**: Standardized interval representations (e.g., `1m`, `5m`, `1d`, `1w`). 
- **PriceAdjustment**: Specifies price adjustment modes (`raw`, `split_adjusted`, `total_return`).

## Core Models

### Quote
Represents the bid and ask state of an instrument.
- Must contain at least a bid or an ask.
- Sizes require corresponding prices.
- Crossed quotes are structurally allowed to preserve real-world observations.
- Last executed price is NOT duplicated inside a Quote.

### Trade
Represents a financial transaction.
- Requires `instrument_id`, `price` (Decimal), and `size` (Decimal > 0).
- Negative prices are allowed depending on market structure, but negative sizes are rejected.

### OHLCVBar
Represents a time-bound interval of trading activity.
- Requires explicit `start_time` and `end_time` bounds.
- Validates the internal high/low consistency (`high >= open, low <= open`, etc.).
- Missing data is never fabricated as `0`. 

### Order Book Models
- **OrderBookLevel**: Decimal price and size.
- **OrderBookSnapshot**: Point-in-time order book structure. Bids are sorted descending (highest price first), and asks are sorted ascending (lowest price first). Duplicate price levels are rejected.

### Market Snapshot
A point-in-time aggregate summary of Market Data fields, often containing nested `Quote` and `Trade` models.
- Rejects completely empty snapshots.
- Nested Quotes/Trades must match the Snapshot's `instrument_id`.
- Derived change/change-percent metrics are not stored inside the canonical snapshot.

## Request & Response Contracts
Canonical requests (e.g., `QuoteRequest`, `HistoricalBarsRequest`) do NOT include execution context like Provider routing fallbacks, credentials, or user context.
- **Batch Safety**: Requests accept bounded batches to avoid overwhelming downstream services.
- **History Limits**: Historical requests enforce time boundaries and maximum record limits.
- **Typed Responses**: All canonical responses return strongly-typed objects containing a `MarketDataOrigin`. Unstructured `dict[str, Any]` is forbidden.

## Operations and Capabilities
- Market Data support is fine-grained. Declaring `ProviderDomain.MARKET_DATA` does NOT automatically imply support for all Market Data operations.
- Operations are defined by `MarketDataOperation` (e.g., `quote`, `historical_bars`, `trades`, `order_book`, `snapshot`).
- Capabilities are declared statically via `MarketDataProviderCapabilities`.

## Provider Protocols
Adapters must implement strongly-typed Protocols corresponding to their capabilities (e.g., `QuoteMarketDataProvider`, `HistoricalBarsMarketDataProvider`). 
There is NO generic `execute(operation, payload)` dictionary-based execution entrypoint.

## Excluded Scope
Stage 33 focuses exclusively on the internal domain models and contracts.
- **No REST API endpoints** or application capability gateway registrations exist for Market Data yet.
- **No Persistence**: Market Data is NOT stored in PostgreSQL. Future stages will utilize ClickHouse for high-volume storage.
- **No OpenBB Execution**: While OpenBB supports the Market Data domain conceptually, no actual external network calls are performed in Stage 33.
