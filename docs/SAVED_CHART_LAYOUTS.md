# ATLAS Saved Chart Layouts V1 Architecture (Stage 74)

## 1. Executive Summary

Stage 74 implements **Saved Chart Layouts V1**, establishing a persistent, professional, and secure workspace storage engine for the ATLAS Charts module (`/charts`). Users can create, save, rename, duplicate, list, load, export, and import multi-chart workspaces containing up to 4 charts, complete with independent instruments, intervals, chart types, TA-Lib indicator parameters, Stage 71 drawings with precision financial coordinates, and Stage 73 synchronization group configurations.

The architecture enforces a foundational principle:
**A saved chart layout is a versioned description of user workspace configuration, NOT a stored copy of market data, live quotes, or browser runtime objects.**

```
+----------------------------------------------------------------------------------------------------+
|                                    ATLAS PERSISTENT WORKSPACE                                      |
|                                                                                                    |
|  [LAYOUT SELECTOR: 4-Grid]   [SAVED: Macro Overview (Rev 3)]   [SAVE]   [SYNC: Group A]   [ACTIVE]   |
|                                                                                                    |
|  +---------------------------------------+---------------------------------------+                 |
|  | PANEL 1 (SPY, 1D, Candlestick)        | PANEL 2 (BTCUSDT, 1h, Candlestick)    |                 |
|  | - Viewport & Linear Scale             | - EMA(20) & RSI(14)                   |                 |
|  | - Trendline & Fibo Anchors            | - Rectangle Box Annotations           |                 |
|  +---------------------------------------+---------------------------------------+                 |
|  | PANEL 3 (EURUSD, 15m, Line)           | PANEL 4 (AAPL, 5m, Bar)               |                 |
|  | - Bollinger Bands Overlay             | - MACD(12,26,9) Subpane               |                 |
|  | - Measurement Tool                    | - Independent Viewport & Scale        |                 |
|  +---------------------------------------+---------------------------------------+                 |
+----------------------------------------------------------------------------------------------------+
                                                  |
                    PURE SERIALIZATION BOUNDARY (ALLOWLIST ONLY)
                                                  |
                                                  v
                      +---------------------------------------+
                      |   SavedChartLayoutDocumentV1 (JSONB)  |
                      |   - layout preset & split ratios      |
                      |   - panel configs (instrument UUIDs)  |
                      |   - indicator definitions/params      |
                      |   - drawings (financial anchors)      |
                      |   - sync groups & property toggles    |
                      +---------------------------------------+
                                                  |
               AUTHENTICATED FASTAPI API (`/api/v1/charts/layouts`)
               OPTIMISTIC CONCURRENCY CONTROL (`ETag` / `If-Match`)
                                                  |
                                                  v
                      +---------------------------------------+
                      |     PostgreSQL: `chart_layouts`       |
                      |     - owner_user_id (RLS / Auth)      |
                      |     - revision (monotonic integer)    |
                      |     - document_schema_version = 1     |
                      |     - unique(owner_user_id, name)     |
                      +---------------------------------------+
```

---

## 2. Saved Layout vs Working Layout

A clean separation of concerns is maintained between the active in-memory workspace and the persistent layout record:

1. **Working Layout (Mutable Client State)**:
   - Resides in client memory (`workspaceStore`, `drawingStore`, `chartSyncStore`).
   - Accommodates rapid user interaction: panning, dragging splitters, armed drawing tools, hover tooltips, and live streaming ticks.
   - Computes deterministic dirty-state by comparing its persistent configuration against the baseline saved snapshot.
2. **Saved Layout (Authoritative Persistent Document)**:
   - Stored in PostgreSQL under the `chart_layouts` table.
   - Contains only validated, versioned JSONB configuration.
   - Associated with an authenticated owner, unique normalized name, and monotonic revision counter.

---

## 3. Database Schema & Migration

### PostgreSQL Table Definition
The table is defined in `apps/api/migrations/versions/stage74_chart_layouts.py` using SQLAlchemy and Alembic (`revision = "stage74_chart_layouts"`):

```sql
CREATE TABLE chart_layouts (
    id UUID PRIMARY KEY,
    owner_user_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(100) NOT NULL,
    description VARCHAR(500) NULL,
    document_schema_version INTEGER NOT NULL DEFAULT 1,
    revision BIGINT NOT NULL DEFAULT 1,
    layout_document JSONB NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_chart_layouts_owner_name UNIQUE (owner_user_id, normalized_name)
);

CREATE INDEX ix_chart_layouts_owner_user_id ON chart_layouts (owner_user_id);
CREATE INDEX ix_chart_layouts_updated_at ON chart_layouts (updated_at);
CREATE UNIQUE INDEX uq_chart_layouts_owner_default ON chart_layouts (owner_user_id) WHERE is_default = TRUE;
```

### Key Relational Columns
- `id`: Canonical UUID generated at creation.
- `owner_user_id`: Enforces strict tenant ownership derived from JWT authentication.
- `name` & `normalized_name`: Unicode NFKC normalized, stripped of HTML/script injection, and canonicalized to lowercase for case-insensitive unique naming per user.
- `document_schema_version`: Identifies the JSON structure version (currently `1`).
- `revision`: Monotonic counter incremented on every document update for optimistic concurrency.
- `layout_document`: Validated, size-bounded (< 512 KiB) JSONB configuration.
- `is_default`: Flag ensuring at most one default layout per user via a PostgreSQL partial unique index.

---

## 4. Canonical Document Schema (V1)

The canonical document format is strictly typed in both backend Pydantic (`python/atlas/src/atlas/charts/layouts/schemas.py`) and frontend TypeScript (`apps/web/src/lib/charts/layouts/types.ts`):

```typescript
export interface SavedChartLayoutDocumentV1 {
  schema_version: 1;
  layout: {
    layout_id: "single" | "two-columns" | "two-rows" | "three-left-focus" | "three-top-focus" | "four-grid";
    panel_order: string[];
    split_ratios: Record<string, number>;
  };
  panels: SavedChartPanelV1[];
  active_panel_id: string;
  synchronization_groups: SavedSyncGroupV1[];
}

export interface SavedChartPanelV1 {
  panel_id: string;
  instrument_entity_id: string;
  canonical_market_series_identity: {
    venue?: string;
    listing?: string;
    currency_pair?: string;
    contract_expiration?: string;
    price_basis?: string;
    adjustment_basis?: string;
    quote_unit?: string;
    provider?: string;
  };
  interval: "1m" | "5m" | "15m" | "1h" | "1d" | "1w" | "1M";
  chart_type: "candlestick" | "bar" | "line" | "area";
  price_scale_settings: {
    mode?: "linear" | "log";
    invert?: boolean;
    scale_visible?: boolean;
  };
  viewport?: {
    visible_start?: number;
    visible_end?: number;
    following_latest?: boolean;
  };
  indicator_instances: SavedIndicatorInstanceV1[];
  drawings: SavedDrawingObjectV1[];
  live_display_preference?: {
    show_volume?: boolean;
    show_subpanes?: boolean;
  };
}

export interface SavedIndicatorInstanceV1 {
  instance_id: string;
  indicator_id: string;
  indicator_version: number;
  parameters: Record<string, any>;
  source_field?: string;
  rendering_target?: "overlay" | "subpane";
  visible: boolean;
  presentation_style?: Record<string, any>;
}

export interface SavedDrawingObjectV1 {
  drawing_id: string;
  drawing_type: string;
  drawing_schema_version: number;
  chart_context: {
    instrument_id: string;
    price_basis?: string;
    adjustment_basis?: string;
    quote_unit?: string;
  };
  financial_anchors: Array<{
    timestamp: number;
    price: number | string;
  }>;
  style: Record<string, any>;
  visible: boolean;
  locked: boolean;
  z_index: number;
}

export interface SavedSyncGroupV1 {
  group_id: string;
  name: string;
  member_panel_ids: string[];
  enabled: boolean;
  settings: {
    crosshair: boolean;
    visible_time_range: boolean;
    instrument: boolean;
    interval: boolean;
    chart_type: boolean;
    drawings: boolean;
  };
}
```

---

## 5. Strict Serialization Allowlist & Forbidden Fields

Stage 74 implements explicit transformation boundaries (`serializeChartWorkspace` and `hydrateChartWorkspace`). Whole-store serialization (`JSON.stringify(store)`) is strictly prohibited.

### Persisted Fields (Allowlist)
- Layout preset identifier & splitter ratios.
- Panel identities, order, and active panel focus.
- Canonical instrument entity UUIDs & series context (venue, basis, units).
- Validated canonical intervals and chart types.
- Viewport time boundaries (UTC timestamps, `following_latest`).
- Technical indicator definitions, versions, parameter dictionaries, and subpane targets.
- Drawing types, financial coordinate anchors (`timestamp`, `price`), styling, lock states, and z-indexes.
- Synchronization group memberships and property toggles.

### Excluded Runtime State (Strictly Forbidden)
- **Market Data**: No historical OHLCV arrays, tick feeds, quote snapshots, or last-price overlays.
- **Calculated Series**: No TA-Lib SMA/EMA/RSI/MACD output arrays or cached indicator points.
- **Screen Coordinates**: No pixel coordinates (`canvas_x`, `canvas_y`, `screen_px`) stored as authoritative drawing anchors.
- **Credentials & Tokens**: No user passwords, bearer tokens, API keys, or provider secret headers.
- **Ephemeral State**: No WebSocket connections, pointer coordinates, hover tooltips, drag previews, undo/redo stacks, or pending event queues.
- **DOM / Framework Objects**: No React refs, canvas contexts, ResizeObserver instances, or DOM nodes.

Backend validators recursively scan every incoming layout document for forbidden terms (`password`, `token`, `secret`, `api_key`, `bars_array`, `ohlcv_data`, `calculated_series`, `indicator_cache`) and reject violations immediately with `422 Unprocessable Entity`.

---

## 6. Optimistic Concurrency Control

To prevent silent lost updates across multiple browser tabs, workstations, or mobile devices, Stage 74 mandates monotonic revision checks:

1. **Monotonic Revision**: Every layout starts at `revision = 1`. Each successful document update increments revision by 1.
2. **HTTP ETags**: Responses include `ETag: W/"<revision>"`.
3. **If-Match Verification**: The frontend supplies `If-Match: "<revision>"` on `PUT /api/v1/charts/layouts/{id}`.
4. **Atomic SQL Compare-and-Swap**:
   ```sql
   UPDATE chart_layouts
   SET layout_document = :doc,
       revision = revision + 1,
       updated_at = NOW()
   WHERE id = :layout_id
     AND owner_user_id = :user_id
     AND revision = :expected_revision;
   ```
5. **Conflict Resolution (`412 Precondition Failed`)**:
   If another session has saved a newer revision, the server rejects the write. The client displays the `<LayoutConflictDialog />`, giving the user three clear paths:
   - **Save As New**: Persists the local changes as an independent layout.
   - **Reload Latest**: Discards local edits and fetches the latest revision from the server.
   - **Cancel**: Keeps the local working copy active in memory without overwriting the server document.

---

## 7. Restoration Pipeline & Hydration Safety

Restoration is a controlled, 10-step transactional operation:

1. **Fetch & Verify**: Retrieve layout document by UUID under authenticated user credentials.
2. **Schema Migration**: Route through `migrate_layout_document`. Currently validates Schema V1; safely rejects unsupported future versions (> 1).
3. **Preflight Structural Validation**: Validate layout preset, panel identities, bounds, and resource quotas (< 4 panels, < 12 indicators/panel, < 250 drawings/panel).
4. **Entitlement & Series Check**: Revalidate that the user retains authorization for saved instrument UUIDs and requested providers.
5. **Loop-Free Sync Suppression**: Set hydration origin flag (`isHydrating = true`) to prevent restored panel properties from firing synchronization echo events into neighboring panels.
6. **Workspace Structure Hydration**: Mount panels in the specified order with validated split ratios.
7. **Indicator Reattachment**: Install indicator configurations into panels; trigger TA-Lib recomputation against fresh, qualified historical data.
8. **Drawing Reconstruction**: Restore drawings using financial coordinate anchors (`timestamp`, `price`). Recompute Fibonacci retracement percentages dynamically.
9. **Sync Group Reconnection**: Register restored synchronization groups into `chartSyncStore` without triggering cascading updates.
10. **Data Reconciliation**: Reload authentic historical data via `useChartHistory` and reconcile live quote streaming through reference-counted WebSocket subscriptions.

---

## 8. Import / Export Architecture

Layouts can be securely exported to and imported from portable JSON files:

### Envelope Specification
```json
{
  "format": "atlas_chart_layout",
  "export_version": 1,
  "exported_at": "2026-10-18T10:40:00.000Z",
  "layout_name": "Macro Cross-Asset Overview",
  "document_schema_version": 1,
  "layout_document": { ... }
}
```

### Security & Sanitization Constraints
- **Zero Secrets**: Strip all user identifiers, provider credentials, and runtime tokens before export.
- **Strict File-Size Limit**: Enforces a strict 512 KiB payload ceiling.
- **Preview & Reassignment**: On import, the user previews the layout metadata (panels, indicators, drawings, sync groups). The imported layout is assigned a fresh UUID and owned exclusively by the currently authenticated user.
- **No Script Execution**: Import processes strictly structured JSON data; no JavaScript expressions, eval calls, or external URL fetches are performed.

---

## 9. Frontend User Interface

The layout manager is integrated directly into the `/charts` workspace toolbar:

```
[Arrangement: 4-Grid v]  [Saved: Macro Overview (Unsaved changes) v]  [Save]  [Sync: Group A (2 linked) v]
```

### Components (`apps/web/src/components/charts/layouts/`)
- `SavedLayoutsMenu`: Compact dropdown menu displaying the current layout, unsaved status badge, recent layouts list, and quick actions:
  - **Save** (`Ctrl+S` / `Cmd+S`): Direct optimistic save of current layout.
  - **Save As...**: Prompts for a new layout name with uniqueness checks.
  - **Manage Layouts...**: Opens full management dialog.
  - **Export JSON**: Downloads the current workspace envelope.
  - **Import JSON**: Uploads and validates an external layout envelope.
- `SaveLayoutDialog` & `SaveAsLayoutDialog`: Compact dialogs with character count (max 100) and trim normalization.
- `SavedLayoutsManagerDialog`: Institutional table listing all user layouts with panel counts, arrangement badges, default stars, rename/duplicate/delete actions, and quick loading.
- `LayoutConflictDialog`: Prompts user on revision mismatch with non-destructive resolution options.
- `LayoutImportDialog`: Validates file size, schema integrity, and displays a pre-import structural inspection.
- `LayoutRestoreStatus`: Displays non-intrusive status toast if any instruments or indicators require attention.

---

## 10. Automated Test Coverage & Quality Gates

### Backend Test Suite (`apps/api/tests/test_chart_layouts.py`)
27 tests covering 100% of core persistence, security, and concurrency mechanics:
- `test_create_layout_success`: Validates V1 layout creation with auto-incrementing revision.
- `test_create_layout_duplicate_name_rejected`: Enforces case-insensitive per-user unique name constraint.
- `test_create_layout_quota_exceeded`: Rejects creation when user reaches 50 saved layouts.
- `test_optimistic_concurrency_update`: Verifies atomic compare-and-swap and `ETag` revision matching.
- `test_optimistic_concurrency_conflict_rejected`: Rejects stale revision updates with `412 Precondition Failed`.
- `test_forbidden_keywords_rejected`: Scans for tokens, passwords, and market data arrays.
- `test_ownership_isolation`: Asserts User A cannot read, update, or delete User B's layouts.
- `test_duplicate_layout`: Clones layout under a new name with fresh UUID and revision 1.
- `test_default_layout_uniqueness`: Verifies at most one layout can be flagged default per user.
- `test_export_envelope`: Confirms exported envelopes contain format markers and omit sensitive metadata.

### Frontend Test Suite (`apps/web/tests/charts-saved-layouts.test.ts`)
10 tests verifying serialization, hydration, dirty-state, and UI workflows:
- `serialization extracts persistent state without market data or DOM refs`.
- `serialization preserves Stage 71 drawings and Stage 73 sync groups`.
- `serialization excludes forbidden runtime properties`.
- `hydration restores multi-chart panels, drawings, and sync groups`.
- `hydration does not trigger cross-panel synchronization loops`.
- `dirty-state comparator detects structural changes while ignoring ticks and hover`.
- `schema validator accepts valid V1 documents and rejects malformed payloads`.
- `import/export envelope correctly encodes and decodes workspaces`.
- `optimistic concurrency helper catches revision mismatch`.
- `quota limits are strictly validated on the client`.

---

## 11. Roadmap Boundaries

| Stage | Responsibility | Boundary Rule |
|---|---|---|
| Stage 66 | Historical Charts | Authoritative rendering & time-scale coordinates |
| Stage 67 | Live Streaming | Real-time WebSocket quote subscription reconciliation |
| Stage 68 | Intervals & Types | Resampling and presentation modes |
| Stage 69 | Indicator Registry | Mathematical definitions & warmup lookback rules |
| Stage 70 | TA-Lib | Numerical calculation engine |
| Stage 71 | Drawing Tools | Financial coordinates, anchor precision, drawing models |
| Stage 72 | Multi-Chart Layouts | Grid presets, panel order, splitters, shared caching |
| Stage 73 | Chart Synchronization | Group controllers, loop prevention, crosshair guides |
| **Stage 74** | **Saved Chart Layouts** | **Persistence, PostgreSQL JSONB, revisions, CRUD, import/export** |
| Stage 75 | Chart Replay | Historical playback, scrub bar, simulation (DEFERRED) |

**Stage 74 does NOT implement chart replay, candle playback, historical simulations, alerts, watchlists, screeners, paper trading, or automated execution.**
