# Live Quote Ingestion

## Overview

The Live Quote Ingestion subsystem provides continuous, low-latency updates for market data quotes (bid/ask). It is designed to be highly concurrent, resilient to worker restarts, and strictly follows the rule of decoupling high-frequency state updates from the persistent transactional database (PostgreSQL).

## Architecture

```text
+----------------+      +-------------------+      +------------------+
|                |      |                   |      |                  |
|  PostgreSQL    |<---->| LiveQuoteWorker   |<---->| Provider(s)      |
|  (Targets)     |      |                   |      |                  |
+----------------+      +---------+---------+      +------------------+
                                  |
                                  v
                        +-------------------+
                        |                   |
                        |   Redis / Valkey  |
                        |   (State Store)   |
                        +-------------------+
```

### Components

1. **PostgreSQL Target Store (`market_data_live_quote_targets`)**
   - **Authoritative** source for which instruments are actively subscribed to for live quotes.
   - Contains lease management columns (`lease_owner`, `lease_expires_at`, `last_heartbeat_at`) allowing concurrent workers to safely distribute targets.
   - **Crucially:** Does *not* store price data or actual quotes.

2. **LiveQuoteWorker**
   - The worker process that runs independently from the main API.
   - Uses `FOR UPDATE SKIP LOCKED` to claim targets from PostgreSQL.
   - Maintains periodic heartbeats to extend leases.
   - Delegates to `LiveQuoteSourceManager` to group targets by provider and establish streams.

3. **LiveQuoteSourceManager**
   - Manages connections to Providers (via the `LiveQuoteStreamProvider` capability protocol).
   - Dynamically reconciles streams based on the current leases held by the worker.
   - Subscribes to streams and delegates incoming quotes to the state store.

4. **Redis / Valkey State Store (`LiveQuoteStateStore`)**
   - **Non-authoritative**, ephemeral store holding the absolute latest quote state per instrument.
   - Employs a **Lua Script** to perform an atomic Compare-And-Swap (CAS).
   - Only overwrites the cached quote if the incoming quote has a strictly strictly greater timestamp (`new.as_of > cached.source_timestamp`).
   - If Redis crashes, no historical data is lost; the cache simply rebuilds as new quotes stream in.

5. **LiveQuoteService**
   - Provides a read-only interface for the main API and other internal components to fetch the latest quotes.
   - Reads directly from Redis/Valkey.

## Key Rules Followed

1. **PostgreSQL is authoritative for configuration, not state**: Quotes never touch PostgreSQL.
2. **Redis/Valkey is non-authoritative for latest quote state**: If Redis goes down, we just lose the most recent quotes until new ones arrive.
3. **Atomic Writes**: A Lua script ensures that concurrent quotes do not overwrite a newer quote with an older one.
4. **Instrument UUID is canonical**: Quotes are mapped by the canonical `instrument_entity_id`.

## Configuration

Configuration is managed via `LiveQuoteWorkerSettings` (prefixed with `ATLAS_LIVE_QUOTE_`), which dictates:
- Worker concurrency (`max_concurrent_targets`)
- Lease duration (`lease_duration_seconds`)
- Reconnect backoffs.
- Target grouping limits (`targets_per_stream_chunk`).

## Execution

The worker is designed to be run as a standalone process:

```bash
uv run atlas-live-quotes
```

## Stage 52 Home Market Summary Consumption

Stage 52 reuses `LiveQuoteService` as its primary latest-quote read interface:
- **Read-Only**: `HomeMarketSummaryService` queries `get_latest_quotes(configured_ids)` without side-effects.
- **No Target Creation on Load**: Opening Home **never** inserts rows into `market_data_live_quote_targets`.
- **No Streaming Side-Effects**: Home **never** initiates live provider streams directly. Upstream workers remain the sole managers of provider ingestion.

