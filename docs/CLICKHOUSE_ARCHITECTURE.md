# ClickHouse Infrastructure Architecture

## Core Principle
ClickHouse is ATLAS's analytical and high-volume datastore. 
PostgreSQL remains the authoritative transactional source of truth.
ClickHouse **does not** replace PostgreSQL. 

Stage 37 deployed the ClickHouse infrastructure only. It currently stores no ATLAS business dataset.

## Target Architecture

```text
                       PostgreSQL / Supabase
                              │
                              │
                 transactional / identity data
                              │
                              ▼
                        ATLAS Backend
                              │
              ┌───────────────┴────────────────┐
              │                                │
              ▼                                ▼
         PostgreSQL                         ClickHouse
              │                                │
              │                                │
     users / entities /                  high-volume /
     permissions /                      analytical /
     configuration /                    time-series data
     provenance metadata                     │
                                               │
                        ┌──────────────────────┼──────────────────────┐
                        │                      │                      │
                        ▼                      ▼                      ▼
                  Market History         Events / Signals       Analytics
```

## Stage 37 Boundary

At Stage 37, **ClickHouse contains no domain tables**. The following do not exist in ClickHouse yet:
- Quotes, Trades, Bars, OHLCV, Order Books, Market Snapshots
- Economic Observations
- News Articles, Research Document Results
- Replicated tables of users, entities, identifiers, or provider credentials.

Stage 37 does not deploy ClickHouse Keeper, sharding, replication, or distributed tables.

## Deployment Configuration

*   **Image**: `clickhouse/clickhouse-server:24.3.2.74`
*   **Version Pinning**: 24.3.2.74 (latest is forbidden).
*   **Service Name**: `clickhouse`
*   **Database**: `atlas`
*   **Application User**: `atlas_app` (The default user is restricted to container loopback only).
*   **Storage**: Persistent named volume `clickhouse_data` mounted at `/var/lib/clickhouse`.
*   **Timezone**: `UTC` (explicitly set via `TZ=UTC`).
*   **Ports**: HTTP port 8123 bound to `127.0.0.1` locally. The native port 9000 is not exposed.
*   **Healthcheck**: Lightweight `wget` to `/ping` endpoint.
*   **Privileges**: Drops ALL capabilities, adds only necessary ones (`SYS_NICE`, `NET_ADMIN`, `IPC_LOCK`). 

## Credential Handling

ClickHouse credentials belong only to the backend.
*   The password is externalized via `ATLAS_CLICKHOUSE_PASSWORD`.
*   Passwords are never committed to the repository.
*   Passwords are redacted from representations and logs.
*   Frontend applications must never receive ClickHouse credentials.

## Security and Networking

*   **Browser Access Boundary**: Browsers must **never** connect directly to ClickHouse. The path is always `Browser -> ATLAS API -> ClickHouse`.
*   **Production Networking**: In production, ClickHouse should reside on a private network, internal container network, or VPC, and must not be exposed to the public internet.
*   **TLS Support**: Backend configuration `ClickHouseSettings` natively supports HTTPS/TLS via `secure=True` and `verify_tls=True`.
*   **SQL Execution**: There is no generic arbitrary SQL endpoint, no terminal mode, and no direct user capability. Stage 37 ensures no user-controlled SQL string concatenation or shell execution occurs.

## Client Lifecycle

*   **Library**: `clickhouse-connect` version 1.9.0.
*   **Lifecycle**: The client is constructed lazily. If ClickHouse is disabled via configuration, the backend never attempts a network connection, allowing API unit tests and core startup to proceed unimpeded before Stage 39.
*   **Health Service**: Infrastructure health is tested via a lightweight `SELECT 1` ping. This is distinct from Provider Health. ClickHouse is not registered as a Provider.

## Schema Migration Foundation

Future schema changes will be placed in `python/atlas/src/atlas/infrastructure/clickhouse/migrations/` (to be defined fully in Stage 39). PostgreSQL Alembic remains separate and is not used for ClickHouse.

## Future Stages
*   **Stage 39**: Historical Market Data Ingestion.
*   **Stage 40**: Market Data Update Workers.
*   **Stage 41**: Live Quote Ingestion.
*   **Stage 42**: Event pipeline.
