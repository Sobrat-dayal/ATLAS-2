# ATLAS — Stage 76: Watchlists V1 Architecture

## 1. Executive Summary

Stage 76 establishes the canonical, persistent, multi-asset Watchlists foundation for the ATLAS Operating System. The Watchlists module transforms `/watchlists` from a navigation placeholder into an institutional-grade, PostgreSQL-backed workspace enabling users to create multiple custom watchlists, organize financial instruments via drag-and-drop or keyboard-accessible reordering, view authorized market quote snapshots with provenance and freshness metadata, and cross-navigate directly into Charts, Markets, and verified issuing Companies.

**Core Architectural Invariant:** A watchlist is a user-owned collection of references to canonical financial instruments and their explicitly selected market series. It is not an independent market-data provider, historical database, trading portfolio, or streaming subscription engine.

---

## 2. Domain & System Architecture

```
ATLAS Authenticated AppShell
             │
             ▼
         Watchlists (/watchlists)
             │
   ┌─────────┴─────────┐
   ▼                   ▼
Watchlist Selector  Watchlist Table
(Create, Rename,    (Ordered Instrument Rows,
 Delete, Switch)     Drag & Keyboard Reorder)
   │                   │
   └─────────┬─────────┘
             ▼
      Watchlist API Layer (/api/v1/watchlists)
             │
   ┌─────────┴─────────┐
   ▼                   ▼
Authentication     Authorization (User Ownership Scope)
   │                   │
   └─────────┬─────────┘
             ▼
      Watchlist Service
             │
   ┌─────────┴───────────────────────┐
   ▼                                 ▼
Watchlist Repository       Instrument & Quote Resolver
(PostgreSQL Transactions)  (Batch Canonical Lookup)
   │                                 │
   ▼                                 ▼
watchlists / watchlist_items   financial_instruments / entities
                               latest_quotes (Cached Snapshots)
```

### 2.1 Multi-Asset Instrument Coverage
The Watchlists domain supports all canonical financial instrument classifications in the ATLAS entity catalog:
- **Equities:** Common shares, preferred shares, depositary receipts (ADRs/GDRs), distinguished by listing venue and share class.
- **ETFs & Funds:** Exchange-traded funds and mutual funds with distinct NAV valuation series vs. exchange market-traded prices.
- **Foreign Exchange (FX):** Base/Quote pair orientation with indicative mid rates (e.g. EUR/USD).
- **Cryptocurrencies:** Base/Quote denomination (e.g. BTC/USD vs. BTC/USDT) preserving spot venue identity.
- **Bonds & Fixed Income:** Sovereign and corporate debt securities preserving coupon, maturity, clean price, dirty price, and yield measures.
- **Futures & Commodities:** Contract expirations and quotation units (e.g. USD/bbl) preserving exact contract identity.

---

## 3. Database Schema & Persistence

Watchlists and their membership are stored persistently in PostgreSQL through versioned Alembic migrations (`apps/api/migrations/versions/stage76_watchlists.py`).

### 3.1 `watchlists` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Globally unique, immutable watchlist identifier |
| `owner_user_id` | `UUID` | `NOT NULL, REFERENCES users(id) ON DELETE CASCADE` | Authenticated owner principal ID |
| `name` | `VARCHAR(100)` | `NOT NULL` | User-defined display name |
| `normalized_name` | `VARCHAR(100)` | `NOT NULL` | NFKC-normalized, trimmed, lowercase name |
| `description` | `VARCHAR(500)` | `NULL` | Optional descriptive context |
| `revision` | `BIGINT` | `NOT NULL DEFAULT 1` | Monotonic revision counter for optimistic concurrency |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL DEFAULT now()` | Audit creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL DEFAULT now()` | Audit modification timestamp |

**Indexes & Constraints:**
- `uq_watchlists_owner_normalized_name`: `UNIQUE (owner_user_id, normalized_name)` prevents duplicate watchlist names per user.
- `ix_watchlists_owner_updated`: `INDEX (owner_user_id, updated_at DESC)` optimizes owner-scoped listing queries.

### 3.2 `watchlist_items` Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | `PRIMARY KEY` | Globally unique membership item identifier |
| `watchlist_id` | `UUID` | `NOT NULL, REFERENCES watchlists(id) ON DELETE CASCADE` | Parent watchlist ID |
| `instrument_entity_id` | `UUID` | `NOT NULL, REFERENCES financial_instruments(entity_id) ON DELETE RESTRICT` | Canonical financial instrument |
| `market_series_id` | `VARCHAR(128)` | `NOT NULL DEFAULT ''` | Specific market series / listing reference |
| `position` | `INTEGER` | `NOT NULL` | 0-indexed dense ordering rank |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL DEFAULT now()` | Audit membership timestamp |

**Indexes & Constraints:**
- `uq_watchlist_items_membership`: `UNIQUE (watchlist_id, instrument_entity_id, market_series_id)` prevents duplicate instrument memberships within a single watchlist.
- `ix_watchlist_items_order`: `INDEX (watchlist_id, position ASC)` guarantees high-performance ordered reads.
- `ix_watchlist_items_instrument`: `INDEX (instrument_entity_id)` supports reverse-lookup references.

---

## 4. Quotas & Capacity Limits

To safeguard infrastructure from denial-of-service, excessive database fanout, and unbounded memory consumption, strict server-side resource quotas are enforced:
- **Maximum Watchlists per User:** 50
- **Maximum Items per Watchlist:** 250
- **Maximum Watchlist Name Length:** 100 characters (min 1 character after trimming)
- **Maximum Description Length:** 500 characters
- **Default Item Page Size:** 50 (max 100)
- **Reorder Payload Limit:** Exactly matches the current item count of the watchlist

---

## 5. Security & Authorization

### 5.1 Authentication
All endpoints require a verified Bearer token or Supabase session resolving to an authenticated `AuthPrincipal`. Anonymous requests are rejected with `401 Unauthorized`.

### 5.2 Ownership Enforcement
- `owner_user_id` is always derived securely from the authenticated principal; client-supplied owner IDs are rejected.
- All database queries for watchlists and watchlist items filter strictly by `owner_user_id == principal.user_id`.
- If a user attempts to read, rename, delete, add to, remove from, or reorder another user's watchlist, the server returns `404 Not Found` (preventing UUID enumeration leakage) or `403 Forbidden`.
- Item modifications verify that `item.watchlist_id == watchlist.id` and that the parent watchlist belongs to the calling user.

---

## 6. Concurrency Control & Reordering

### 6.1 Monotonic Revisions
Every watchlist maintains an integer `revision` starting at 1. Any mutating operation (renaming, adding an item, removing an item, reordering items) atomically increments `revision` by 1 within a database transaction.

### 6.2 Optimistic Concurrency Protocol
When reordering entries:
- Clients submit `ordered_item_ids: List[UUID]` and `expected_revision: int` (or HTTP `If-Match: "<revision>"`).
- The service verifies:
  1. `watchlist.revision == expected_revision`. If mismatched, raises `409 Conflict` (or `412 Precondition Failed`).
  2. Length of `ordered_item_ids` matches current item count.
  3. No duplicate IDs and no foreign item IDs.
  4. All items belong to the target watchlist.
- If valid, positions are atomically updated to dense ranks `0, 1, 2, ... N-1`, and `revision` is incremented.
- If the backend rejects the reorder due to a revision conflict, the frontend automatically rolls back its optimistic drag-and-drop state to the authoritative server order and alerts the user.

### 6.3 Dense Position Reindexing
When an item is deleted from a watchlist:
- Remaining items are atomically reindexed in the database (`UPDATE position = position - 1 WHERE position > deleted_position`).
- No gaps or duplicate positions ever exist in committed state.

---

## 7. Market Quote Snapshot Semantics

Stage 76 adheres strictly to institutional financial data integrity principles:
1. **Zero Provider Fanout:** Opening a watchlist does not trigger upstream API calls per table row. Observations are resolved in a single batch read from existing cached quote services.
2. **Zero Fabricated Data:** If a market quote is unavailable or unentitled, the UI displays `Unavailable` and neutral dashes (`—`). The system never substitutes `0.00` or synthetic prices.
3. **Quotation Currency & Units:** Measures preserve canonical quotation units (e.g. `USD`, `INR`, `USD/bbl`, `% of par`, `Yield %`).
4. **Qualified Price Changes:** Equity-style percentage change is calculated only against verified prior session closes with matching adjustments and currencies. NAV changes refer strictly to official valuation dates. FX and Crypto rolling 24h metrics are clearly qualified.
5. **Freshness & Delay Classification:**
   - `FRESH`: Realtime observation within freshness threshold.
   - `DELAYED`: Observation subjected to exchange-mandated delay (typically 15 minutes).
   - `STALE`: Outdated observation beyond acceptable session bounds.
   - `UNAVAILABLE`: No valid cached observation found.
6. **No Fake Streaming:** Stage 76 does not implement WebSocket tick-by-tick streaming (reserved for Stage 78).

---

## 8. Cross-Module Navigation

Each watchlist item provides verified, context-aware cross-navigation:
- **Open in Charts:** Navigates to `/charts` preserving canonical `instrument_entity_id` and market series identity in the global selected entity context.
- **Open in Markets:** Routes to the appropriate asset class hub:
  - Equity -> `/markets/equities`
  - ETF / Mutual Fund -> `/markets/funds`
  - Crypto -> `/markets/crypto`
  - FX / Currency -> `/markets/fx`
  - Bond -> `/markets/bonds`
  - Futures -> `/markets/futures`
- **Open in Companies:** Navigates to `/companies?entity=<issuer_id>` **only** when a verified issuer relationship (`issued_by`) exists in the relationship graph (`entity_relationships`). If no verified company relationship exists, the action is omitted or disabled.

---

## 9. REST API Reference

All endpoints are mounted under `/api/v1/watchlists`:

| Method | Path | Request Body | Status | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/watchlists` | Query: `limit`, `offset` | `200 OK` | List user-owned watchlists with item counts |
| `POST` | `/api/v1/watchlists` | `WatchlistCreateRequest` | `201 Created` | Create a new user watchlist |
| `GET` | `/api/v1/watchlists/{id}` | Query: `limit`, `offset` | `200 OK` | Read watchlist details, items, and quote snapshots |
| `PATCH` | `/api/v1/watchlists/{id}` | `WatchlistUpdateRequest` | `200 OK` | Rename watchlist or update description |
| `DELETE` | `/api/v1/watchlists/{id}` | None | `204 No Content` | Delete watchlist and cascade membership |
| `POST` | `/api/v1/watchlists/{id}/items` | `AddWatchlistItemRequest` | `201 Created` | Add canonical financial instrument to watchlist |
| `DELETE` | `/api/v1/watchlists/{id}/items/{item_id}` | None | `204 No Content` | Remove membership item and reindex positions |
| `PUT` | `/api/v1/watchlists/{id}/items/order` | `ReorderWatchlistItemsRequest` | `200 OK` | Atomically reorder items with revision check |

---

## 10. Roadmap Scope Boundaries

| Stage | Feature Area | Status in Stage 78 |
|---|---|---|
| **Stage 76** | Watchlists V1: Persistent Multi-Asset Watchlists, CRUD, Drag-and-Drop, Snapshots | **COMPLETE** |
| **Stage 77** | Advanced Configurable Watchlist Columns (Custom columns, presets, formulas) | **COMPLETE** |
| **Stage 78** | Live Watchlist Updates (Streaming WebSockets, per-row tick flashing, reconciliation) | **COMPLETE** |
| **Stage 79** | Fundamental, Technical, Event and News Watchlist Enrichment | **DEFERRED** |
| **Stage 80** | Watchlist Alerts (Price thresholds, volume spikes, push alerts) | **DEFERRED** |
