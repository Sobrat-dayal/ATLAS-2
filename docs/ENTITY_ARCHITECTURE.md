# ATLAS Universal Entity Architecture

## Purpose
ATLAS works with many real-world objects: companies, securities, countries, facilities, economic series, and research documents. These objects are not implemented as isolated systems. Instead, they share a **Universal Entity Layer**.

The central principle of ATLAS Identity is:
**Every real-world ATLAS object receives one stable internal `entity_id`.**

This `entity_id` is the foundation for later capabilities like search, tagging, graph relationships, portfolios, and AI reasoning.

Entities can also be referenced by the global application **Selected Entity Context**. This frontend context uses the `entity_id` as the singular identity pointer across the application.

## Architecture

```text
                    ATLAS Universal Entity Layer

                              Entity
                                │
                                │ entity_id
                                │
            ┌───────────────────┼────────────────────┐
            │                   │                    │
            ▼                   ▼                    ▼
        Company              Security             Country
            │                   │                    │
            ▼                   ▼                    ▼
       Stage 18              Stage 17             Stage 19

            ┌───────────────────┼────────────────────┐
            │                   │                    │
            ▼                   ▼                    ▼
        Facility         Economic Series      Research Document
         Stage 19            Stage 20              Stage 20
```

## Entity ID Rules
1. **UUID**: `entity_id` is a UUID generated on creation.
2. **Immutability**: Once created, an `entity_id` never changes, even if a company rebrands or a security changes its ticker.
3. **No External PKs**: External identifiers (ISIN, FIGI, Tickers, Provider IDs) are NEVER used as primary keys.
4. **Canonical Names are NOT Unique**: Multiple entities can legitimately share the same name (e.g., people with the same name, or a company and security sharing a name).

## Company vs Security Distinction
A legal company and its tradable security are **explicitly separate entities** in ATLAS.

Example:
```text
Company:
NVIDIA Corporation
entity_id = A

Equity:
NVDA
entity_id = B

A != B
```
Future relationship graph updates (Stage 23) will link them via an `issued` relationship (`A --issued--> B`).

## Entity Type Registry
The `entity_types` canonical registry enforces structural taxonomy. Each entity has exactly one primary `entity_type`.

### Type Hierarchy
```text
security
├── equity
├── etf
├── bond
├── option
├── future
└── fund

facility
├── port
└── airport
```

### Initial Canonical Types
- **Financial**: `security`, `equity`, `etf`, `bond`, `option`, `future`, `fund`, `crypto`, `currency`, `commodity`, `index`
- **Organizations/People**: `company`, `person`
- **Geography/Infrastructure**: `country`, `facility`, `port`, `airport`, `exchange`
- **Economics**: `economic_series`
- **Events/Documents**: `news_event`, `research_document`

## Database Schema (PostgreSQL)

### `entity_types`
- `key` (PK, String 128)
- `name` (String 256)
- `description` (Text, optional)
- `parent_key` (FK to `entity_types.key`)
- `is_system` (Boolean, default True)

### `entities`
- `entity_id` (PK, UUID)
- `entity_type` (FK to `entity_types.key`, Indexed)
- `canonical_name` (String 512, Not Null)
- `display_name` (String 512, Not Null)
- `description` (Text, optional)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)

## Specialization Pattern
Specialized fields (e.g., coordinates for geography, maturity for bonds, sector for companies) **do not belong in the base `entities` table**.

Future tables will use `entity_id` as their Primary Key / Foreign Key to enforce 1-to-1 extension:
```text
entities
    ↓ entity_id
companies (Stage 18)
    ↓ entity_id
securities (Stage 17)
```

## Service and Repository
The `EntityService` handles validation, identity immutability, and display-name defaulting.
The `EntityRepository` handles explicit persistence.
Transactions remain open during basic entity creation to allow atomic future specialization (e.g., `Entity` + `Company` in one `async with session.begin()` block).

## What DOES NOT Belong in Base Entities
- `ticker`, `symbol`, `ISIN`, `CUSIP`, `FIGI`, `CIK`, `LEI` (Stage 21 Identifiers)
- Aliases or alternate names (Stage 22 Aliases)
- Relationships (Stage 23 Graph)
- Provider references, source urls, or provenance data (Stage 24 Provenance)
- Geography data like Lat/Long (Stage 19)
- Security specific financial attributes like strikes, coupons, yields (Stage 17)
- Generic JSONB `metadata` property. Stable attributes must be properly mapped in specialization tables.

## Future Identifiers & Aliases
Identifiers and aliases will be attached via separate tables (Stage 21 & 22) referencing the `entity_id`, rather than overloading the base entity schema.

## Future Search
Global Search will be handled by a specialized indexing system in Stage 45. `canonical_name` is strictly for domain identity, not for fuzzy full-text searching in Postgres.
