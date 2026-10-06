# ATLAS Database Architecture

This document describes the PostgreSQL database architecture used by ATLAS.

## Schema Versioning
Migrations are managed using Alembic.
Migration scripts are located in `apps/api/migrations/versions`.

## Core Identity: Universal Entities
The foundational data layer in ATLAS is the Universal Entity Layer (Stage 16).
Every real-world concept (securities, companies, countries) receives an immutable `entity_id` UUID.

### `entity_types`
The canonical code-controlled registry of entity types.
- `key`: Primary Key (e.g., `security`, `company`, `equity`).
- `parent_key`: Implements the type hierarchy (e.g. `equity` -> `security`).

### `entities`
The root table for all universally identified objects.
- `entity_id`: UUID, Primary Key. Immutable.
- `entity_type`: FK to `entity_types.key`.
- `canonical_name`: The ATLAS canonical name (Not globally unique).

### Specialization Pattern (Future)
Future tables containing specific attributes will relate back 1-to-1 via `entity_id`.
```sql
CREATE TABLE companies (
    entity_id UUID PRIMARY KEY REFERENCES entities(entity_id),
    ...
);
```

### Identity Invariants
- External Identifiers (Tickers, ISIN, etc.) are **NEVER** primary keys.
- Entities do not change their ID.
- Generic metadata JSON blobs are not permitted in the `entities` table.

## Global Application Context
Global Application Context (Stage 26) is transient browser-session state. No PostgreSQL tables are used for context persistence.


## Market Data (Stage 33)
Stage 33 adds no Market Data persistence tables to PostgreSQL (e.g., no quotes, 	rades, candles, order_books tables). High-volume historical and live Market Data storage is deferred to future stages utilizing ClickHouse (Stage 37).

## OpenBB Integration
See [OPENBB_INTEGRATION.md](OPENBB_INTEGRATION.md) for details on the Stage 29 OpenBB Framework Provider integration.
