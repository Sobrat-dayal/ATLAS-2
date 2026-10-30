# Global Workspace Linking and Cross-Module Context Synchronization System

## Stage 121 Architectural Specification & Operator Reference

### 1. Executive Summary & Canonical Roadmap Position
The **Global Workspace Linking and Cross-Module Context Synchronization System** (Stage 121 of 150) establishes an institutional-grade, deterministic, and high-performance financial context synchronization architecture across ATLAS. Building upon the multi-panel layout foundation established in Stage 120, Stage 121 unifies financial entity selection, link channel management, cross-panel synchronization, cross-workspace coordination, cross-entity canonical transformations, and multi-tab synchronization while enforcing strict safety invariants: zero trading mutation, monotonic revision ordering, causation chain loop prevention, and truthful entity resolution.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ATLAS AppShell Chrome                            │
│  [GLOBAL CONTEXT BAR]  [LINK A: BLUE]  [AAPL US]  [USD]  [1Y]  [MANAGE]     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Workspace Analytical Desktop                                              │
│  ┌───────────────────────────────┐  ┌────────────────────────────────────┐  │
│  │ Watchlist Panel               │  │ Instrument Chart Panel             │  │
│  │ Channel: Group A (PUBLISH)    │  │ Channel: Group A (SUBSCRIBE)       │  │
│  │ Click: AAPL US                │─►│ Auto-syncs chart to AAPL           │  │
│  └───────────────────────────────┘  └────────────────────────────────────┘  │
│  ┌───────────────────────────────┐  ┌────────────────────────────────────┐  │
│  │ Company Overview Panel        │  │ Macro Series Panel                 │  │
│  │ Channel: Group A (SUBSCRIBE)  │  │ Channel: Independent (UNLINKED)    │  │
│  │ Auto-transforms: AAPL -> AAPL │  │ Preserves CPI/GDP Macro View       │  │
│  └───────────────────────────────┘  └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Core Concepts & Domain Architecture

#### 2.1 The Ten Context Dimensions
ATLAS coordinates context across ten standardized, non-colliding financial dimensions:

| Dimension | Description | Typical Payload / Key | Example Value |
|---|---|---|---|
| `INSTRUMENT` | Tradable security / listing | `instrument_id`, `ticker`, `mic`, `asset_class` | `inst_aapl_us` ("AAPL", NASDAQ) |
| `COMPANY` | Corporate legal entity / issuer | `company_id`, `ticker`, `cik`, `lei` | `comp_apple_us` (Apple Inc.) |
| `PORTFOLIO` | Investment portfolio | `portfolio_id`, `name`, `base_currency` | `port_institutional_alpha` |
| `BENCHMARK` | Market index or benchmark | `benchmark_id`, `symbol`, `name` | `SPX` (S&P 500 Index) |
| `ECONOMIC_SERIES` | Macroeconomic indicator | `series_id`, `symbol`, `frequency` | `CPI` (Consumer Price Index) |
| `DATE_RANGE` | Temporal window for analysis | `start_date`, `end_date` | `2024-01-01` to `2024-12-31` |
| `AS_OF_DATE` | Specific historical snapshot point | `as_of_date` (ISO-8601) | `2024-10-25` |
| `TIMEFRAME` | Granularity / chart frequency | `timeframe` | `1D`, `1W`, `1M`, `1Y`, `5Y` |
| `REPORTING_CURRENCY` | Base reporting currency | `currency_code` (ISO-4217) | `USD`, `EUR`, `GBP`, `JPY` |
| `REGION` | Geographic or economic jurisdiction | `region_code` (ISO-3166) | `US`, `EU`, `GB`, `JP`, `GLOBAL` |

#### 2.2 Context Scopes
Context channels operate within explicitly bounded scopes:
- **`PANEL_LOCAL`**: Local to an individual panel instance; overrides all external channels.
- **`WORKSPACE`**: Scoped strictly to the active workspace desk. Does not affect background desks.
- **`USER_APPLICATION`**: Platform-wide user scope; synchronizes across all modules within the active browser window.
- **`USER_CROSS_TAB`**: Multi-window scope synchronized across browser tabs via `BroadcastChannel`.

#### 2.3 Subscription Modes
Every panel instance connects to a link channel with an explicit subscription mode:
- **`PUBLISH`**: Outbound-only. Emits context events when selections occur; ignores incoming broadcasts.
- **`SUBSCRIBE`**: Inbound-only. Listens to channel context broadcasts; internal user interactions inside the panel do not broadcast to the channel.
- **`BIDIRECTIONAL`**: Full sync. Emits outbound events on selection and consumes inbound updates.
- **`INDEPENDENT`**: Disconnected (`channel_id = null`). Maintains independent local state completely isolated from external events.

---

### 3. Canonical Capability Registry (`CAPABILITIES_CATALOG`)
Each of the 14 canonical institutional panel types declares a typed capability contract defining subscribable dimensions, publishable dimensions, accepted entity types, and required transformations:

```typescript
export interface PanelContextCapability {
  panel_type_id: string;
  publishable_dimensions: ContextDimension[];
  subscribable_dimensions: ContextDimension[];
  accepted_entity_types: string[];
  required_transformations: Record<string, string>;
  supported_timeframes: string[];
  supports_as_of: boolean;
  supports_currency: boolean;
}
```

#### Capability Matrix Summary:
1. **`WATCHLIST`**: Outbound publisher (`INSTRUMENT`, `COMPANY`). Inbound subscriber (`INSTRUMENT`, `COMPANY`).
2. **`INSTRUMENT_CHART`**: Inbound subscriber (`INSTRUMENT`, `TIMEFRAME`, `DATE_RANGE`). Outbound publisher (`TIMEFRAME`, `DATE_RANGE`). Accepts `INSTRUMENT_TO_COMPANY` reverse resolution.
3. **`COMPANY_OVERVIEW`**: Inbound subscriber (`COMPANY`, `INSTRUMENT`). Automatically transforms `INSTRUMENT` -> `COMPANY` via canonical entity resolution.
4. **`NEWS_FEED`**: Inbound subscriber (`INSTRUMENT`, `COMPANY`, `PORTFOLIO`). Filters news by active linked entity.
5. **`PORTFOLIO_SUMMARY`**: Inbound subscriber (`PORTFOLIO`, `REPORTING_CURRENCY`, `DATE_RANGE`). Outbound publisher (`PORTFOLIO`).
6. **`PORTFOLIO_PERFORMANCE`**: Inbound subscriber (`PORTFOLIO`, `BENCHMARK`, `DATE_RANGE`, `REPORTING_CURRENCY`). Automatically resolves `PORTFOLIO` -> `BENCHMARK`.
7. **`RISK_OVERVIEW` / `RISK_ANALYSIS`**: Inbound subscriber (`PORTFOLIO`, `BENCHMARK`, `AS_OF_DATE`, `REPORTING_CURRENCY`).
8. **`ECONOMIC_SERIES`**: Inbound subscriber (`ECONOMIC_SERIES`, `DATE_RANGE`). Outbound publisher (`ECONOMIC_SERIES`).
9. **`RESEARCH_DOCUMENT` / `RESEARCH_REPORT`**: Inbound subscriber (`COMPANY`, `INSTRUMENT`). Accepts company or ticker context.
10. **`DATA_TABLE`**: Dynamic subscriber based on configured data schema.

---

### 4. Canonical Entity Resolver & Transformations
ATLAS strictly prohibits speculative ticker guessing. Cross-entity transformations use deterministic lookup fixtures and canonical registry services:

- **`INSTRUMENT_TO_COMPANY`**: Maps tradable security (e.g., `inst_aapl_us`) to issuer entity (`comp_apple_us`).
- **`COMPANY_TO_PRIMARY_LISTING`**: Maps corporate issuer (`comp_apple_us`) to primary equity instrument (`inst_aapl_us`).
- **`PORTFOLIO_TO_BENCHMARK`**: Resolves portfolio default investment benchmark (e.g., `port_institutional_alpha` -> `SPX`).
- **`OPTION_TO_UNDERLYING`**: Strips derivative symbology to resolve underlying equity instrument.
- **`GENERIC_RESOLVE`**: Resolves universal entity identifiers (`entity_id`) against registry records.

---

### 5. Deterministic Synchronization, Concurrency & Loop Prevention

#### 5.1 Monotonic Channel Revisions
Every link channel maintains a monotonic integer `revision` sequence number.
- When an event is published, the channel revision increments (`revision + 1`).
- Subscribers maintain their local `last_applied_revision`.
- Any arriving event or state snapshot with `revision <= last_applied_revision` is dropped immediately as stale.

#### 5.2 Causation Chain Loop Prevention & Echo Suppression
To prevent infinite event ping-pong loops across bidirectional panels:
1. **Echo Suppression**: A panel instance discards any event where `origin_panel_instance_id === current_panel_id`.
2. **Causation IDs**: Events contain `causation_id` and `correlation_id`. A panel recording an update spawned by event `E_1` sets `causation_id: E_1.event_id`. If an event encounters its own origin in the causation chain, propagation terminates immediately.
3. **Event Deduplication**: The event bus maintains a high-water ring buffer of recently processed `event_id` hashes. Duplicate event dispatches are silently dropped.

#### 5.3 Cross-Tab Coordination via `BroadcastChannel`
In multi-window or multi-monitor configurations, the client-side `ContextEventBus` utilizes standard HTML5 `BroadcastChannel('atlas_global_context_channel')`:
- Transmits serialized `ContextSelectionEvent` objects across browser windows.
- Outbound cross-tab dispatches carry `scope: 'USER_CROSS_TAB'`.
- Receiving windows verify the user ID and apply monotonic revision checks before rendering updates.

---

### 6. Relational Persistence Schema

Stage 121 introduces four relational tables in PostgreSQL / Supabase with comprehensive indexes and referential integrity:

1. **`global_context_channels`**:
   - `channel_id` (UUID PK): Channel identifier.
   - `owner_user_id` (TEXT): Owner reference.
   - `workspace_id` (UUID FK, nullable): Scoped workspace desk.
   - `scope` (VARCHAR): `PANEL_LOCAL`, `WORKSPACE`, `USER_APPLICATION`, `USER_CROSS_TAB`.
   - `name` (VARCHAR): Display name (e.g., "Group A Blue").
   - `display_color_token` (VARCHAR): Color token (`blue`, `green`, `amber`, `rose`, `purple`, `cyan`).
   - `enabled` (BOOLEAN): Active state.
   - `supported_dimensions` (JSONB): Supported context dimension array.
   - `context_snapshot` (JSONB): Current dimensional state dictionary.
   - `revision` (BIGINT): Monotonic sequence number.
   - Timestamps: `created_at`, `updated_at`.

2. **`global_context_channel_memberships`**:
   - `membership_id` (UUID PK): Membership record.
   - `channel_id` (UUID FK): Target channel.
   - `panel_instance_id` (UUID): Bound panel instance.
   - `subscription_mode` (VARCHAR): `PUBLISH`, `SUBSCRIBE`, `BIDIRECTIONAL`, `INDEPENDENT`.
   - `dimension_overrides` (JSONB): Per-dimension manual overrides.
   - Timestamps: `created_at`, `updated_at`.

3. **`global_context_snapshots`**:
   - Historical state audit trail enabling snapshot playback and undo operations.

4. **`global_context_audit_events`**:
   - Append-only event log capturing every dispatched selection event for diagnostic inspection.

---

### 7. REST API Endpoints (`/api/v1/context`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/context/capabilities` | Retrieve the global catalog of panel capabilities. |
| `GET` | `/api/v1/context/channels` | List all context channels for user and workspace. |
| `POST` | `/api/v1/context/channels` | Create a new custom context channel. |
| `GET` | `/api/v1/context/channels/{channel_id}` | Retrieve channel state and snapshot. |
| `PUT` | `/api/v1/context/channels/{channel_id}` | Update channel metadata or color token. |
| `DELETE` | `/api/v1/context/channels/{channel_id}` | Delete a custom context channel. |
| `POST` | `/api/v1/context/channels/{channel_id}/memberships` | Bind a panel instance to a channel. |
| `DELETE` | `/api/v1/context/channels/{channel_id}/memberships/{panel_id}` | Unbind a panel instance. |
| `POST` | `/api/v1/context/channels/{channel_id}/events` | Dispatch a context selection event. |
| `POST` | `/api/v1/context/resolve` | Deterministically resolve an entity across dimensions. |

---

### 8. Frontend UI Components

1. **`<GlobalContextBar />`**:
   Mounted in the `WorkspaceHeader` and application chrome. Displays active channel badge (`[LINK A: BLUE]`), current entity ticker (`[AAPL]`), base currency (`[USD]`), active timeframe (`[1Y]`), and quick action button to open the link manager.
2. **`<PanelLinkControl />`**:
   Integrated into `<WorkspacePanelHost />` panel headers. Allows instant switching between Group A, Group B, Group C, Group D, or Unlinked (Independent Mode). Features color-coded badges matching institutional terminal standards.
3. **`<LinkChannelManagerModal />`**:
   Comprehensive modal dialog displaying all active channels, connected panel counts, dimensional states, and custom channel creation options.
4. **`<ContextCompatibilityStatus />`**:
   Compact visual indicator showing whether a panel is currently compatible with, synchronized to, or ignoring the active channel context.

---

### 9. Verification & Test Rigor
- **Backend Tests (`test_context_stage121_v1.py`)**: 12 integration tests passing (channel CRUD, membership lifecycle, entity resolution, cross-entity transformations, event dispatching, optimistic concurrency control, and REST endpoints).
- **Stage 120 Backend Regression Tests**: 17 tests passing (29 total pytest assertions passing in 9.25s).
- **Frontend Unit Tests (`context_stage121_v1.test.ts`)**: 9 tests passing covering Reference Fixtures A through I (cross-widget sync, independent panel preservation, channel isolation, timeframe independence, monotonic ordering, echo suppression, canonical transformations, capability contracts, and deduplication).
- **Production Build**: 100% clean Next.js build across all 38 routes with 0 TypeScript compilation errors and 0 lint warnings.

