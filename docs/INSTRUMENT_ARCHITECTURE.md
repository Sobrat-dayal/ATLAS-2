# ATLAS Instrument Architecture (Stage 17)

## Overview
The Financial Instruments layer is the first major specialization of the Universal Entity Model (Stage 16). It extends base entities with financial semantics while maintaining `entity_id` as the immutable, universal identifier.

## Core Principles
1. **Instrument is an Entity**: Every financial instrument is an Entity, but not every Entity is a financial instrument.
2. **Polymorphic Identity**: The Universal Entity system provides identity. The instrument layer provides financial domain attributes.
3. **No Market Data Here**: Instruments are strictly structural, reference definitions. No price, volume, or temporal market data exists in these tables. (Stage 33 explicitly defines Market Data canonical models which reference the `entity_id` rather than a ticker/symbol).
4. **Precision**: All financial numeric values use `Decimal` with exact precision. No floating point representations are allowed.
5. **Atomic Creation**: Creating an instrument requires atomic insertion into `entities`, `financial_instruments`, and any specialized tables (e.g., `securities`, `equities`).

## Architecture

### Hierarchy
```text
Entity (Base)
  │
  └── Financial Instrument
          │
          ├── Security
          │     ├── Equity
          │     ├── ETF
          │     ├── Bond
          │     ├── Option
          │     ├── Future
          │     └── Fund
          │
          ├── Currency
          ├── Crypto Asset
          ├── Commodity
          └── Market Index
```

### Schemas
- **`financial_instruments`**: The root marker table indicating an entity participates in the financial domain.
- **`securities`**: The root marker table for tradable securities.
- **Specializations**: Separate tables for `equities`, `etfs`, `bonds`, `options`, `futures`, `funds`, `currencies`, `crypto_assets`, `commodities`, and `market_indexes` storing domain-specific attributes.

All tables share the same Primary Key (`entity_id`), which is a Foreign Key to the parent table in the hierarchy.

### Foreign Key Resolution
- `currencies`: Defines fiat and supranational currencies.
- `base_currency_entity_id`, `denomination_currency_entity_id`, `settlement_currency_entity_id`: Foreign keys mapping back to `currencies`.
- `underlying_entity_id`: Foreign key mapping back to `financial_instruments` (for derivatives).

## Technical Implementation
- **SQLAlchemy ORM**: Implemented in `python/atlas/src/atlas/instruments/models.py`.
- **Pydantic**: Discriminated Union pattern in `schemas.py` to serialize polymorphic instruments properly.
- **Service Layer**: `InstrumentService` acts as an orchestrator, creating base entities and instrument specializations atomically without immediately committing to the database (delegating transaction control to the router/API layer).
- **Enums**: All enumerations (e.g., `OptionRight`, `SettlementType`, `EquityKind`) use standard Python `StrEnum` mapped to string columns in PostgreSQL.
