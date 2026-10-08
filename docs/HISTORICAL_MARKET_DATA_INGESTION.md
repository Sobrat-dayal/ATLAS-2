# Historical Market Data Ingestion (Stage 39)

This document describes the design and implementation of the historical market data ingestion process for ATLAS.

## Architecture
ATLAS employs a tri-datastore architecture:
- **PostgreSQL**: Authoritative transactional system for instrument identities, configurations, and metadata.
- **ClickHouse**: Analytical database for high-volume timeseries data (OHLCV bars, trades, order book snapshots).
- **Valkey**: Ephemeral low-latency state. (Not used in Stage 39 historical ingestion).

## Ingestion Flow
1. **Trigger**: Manually or internally triggered via CLI/Service (No generic scheduler).
2. **Range Planning**: `RangePlanner` queries PostgreSQL (`historical_market_data_ingestion_runs`) to determine optimal request intervals, avoiding re-ingestion of identical data.
3. **Provider Fetch**: `HistoricalMarketDataIngestionService` uses `HistoricalBarsMarketDataProvider` via the OpenBB provider abstraction to fetch canonical data (`OHLCVBar`).
4. **ClickHouse Mapping**: `HistoricalMarketBarStorageMapper` generates a deterministic content hash and prepares insertion formats.
5. **Persistence**:
    - Data is written to ClickHouse in `historical_market_bars_versions` (ReplacingMergeTree).
    - Metadata about the ingestion run is committed to PostgreSQL in `historical_market_data_ingestion_runs`.

## ClickHouse Schema
The table `historical_market_bars_versions` is structured as a `ReplacingMergeTree` ordered by `(instrument_entity_id, interval_code, adjustment_code, bar_start, provider_key)`. This allows idempotency and eventual deduplication across multiple ingestions.
Provider-specific models NEVER hit the database. Only canonical Stage 33 Market Data models are stored.

## Tooling
- **Database Migrations (PostgreSQL)**: Managed via Alembic (`apps/api/migrations`).
- **Database Migrations (ClickHouse)**: Managed via custom determinable script `ch-migrate`.
