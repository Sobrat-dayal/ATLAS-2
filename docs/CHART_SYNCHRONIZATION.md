# Professional Chart Synchronization V1 — ATLAS Stage 73

## 1. Overview and Architecture

ATLAS Stage 73 implements **Professional Chart Synchronization V1**, transforming the multi-chart workspace at `/charts` into an institutional financial analysis environment comparable to TradingView and Bloomberg Terminal.

Stage 73 builds directly on the Stage 72 multi-chart layout foundation (which introduced independent chart panels with stable identities `panel-1` through `panel-4`, independent viewports, shared query caching, and reference-counted WebSocket subscriptions).

```
ATLAS AUTHENTICATED APPSHELL (/charts)
                 |
                 v
       Stage 72 MultiChartWorkspace
                 |
                 v
       Stage 73 Chart Synchronization Controller
                 |
       +---------+----------+
       |                    |
       v                    v
 Sync Group Registry   Sync Property Settings
       |                    |
       +---------+----------+
                 |
                 v
          Sync Event Router
                 |
       +---------+----------+
       |                    |
       v                    v
 Source Validation     Loop Prevention Coordinator
       |                    |
       +---------+----------+
                 |
                 v
     Compatibility & Entitlement Verification
                 |
       +---------+----------+
       |                    |
       v                    v
  Temporal Mapping     Series/Interval Availability
       |                    |
       +---------+----------+
                 |
                 v
       Target Chart Panel Adapters (P1 - P4)
                 |
       +---------+----------+
       |                    |
       v                    v
  Linked Crosshairs    Linked Time Ranges
       |                    |
       +---------+----------+
                 |
       +---------+----------+
       |                    |
       v                    v
  Linked Instruments   Linked Intervals
       |                    |
       +---------+----------+
                 |
       +---------+----------+
       |                    |
       v                    v
  Linked Chart Types   Compatible Drawing Sync
```

---

## 2. Core Architectural Principles

1. **Explicit Opt-In Only**: Independent chart state is the default. Zero implicit or automatic synchronization occurs unless the user assigns panels to a group and activates specific properties.
2. **Strict Loop Prevention**: Programmatic updates applied to destination panels are flagged as `SYNC_APPLIED` under a token-based suppression window. Programmatic callbacks (e.g. `subscribeVisibleTimeRangeChange`) are suppressed from re-transmitting to the group, preventing infinite `A -> B -> A` cycles.
3. **Canonical Timestamp Alignment**: Synchronization is strictly time-based using UTC Unix seconds. Screen X pixels and ordinal candle indices are NEVER propagated across panels.
4. **Multi-Market Calendar Integrity**: Different market sessions (crypto 24/7 continuous vs equity Monday-Friday) are respected without fabricating missing candles or synthetic OHLC data.
5. **No Entitlement Bypass**: Linked instrument updates undergo preflight authorization and entitlement checks. Unauthorized targets reject the update with an explicit error and preserve their existing series.
6. **No Fake Data / Resampling**: Unsupported intervals (e.g. 1m on daily-only Treasury bonds) are rejected without generating artificial resampling.
7. **Strict Drawing Compatibility Gate**: Drawings only synchronize if panels share identical canonical instrument UUIDs and quotation currencies. Cross-instrument drawing synchronization is strictly rejected.
8. **Session-Level State**: All synchronization groups and settings are maintained in session memory. Persistent saved chart layouts are deferred to Stage 74.

---

## 3. Domain Model and Event Contracts

### 3.1 Synchronization Groups (`ChartSyncGroup`)
```typescript
interface ChartSyncGroup {
  id: string;              // e.g. "group-a", "group-b"
  name: string;            // e.g. "Group A"
  memberPanelIds: string[];// ["panel-1", "panel-2"] (bounded to max 4 panels)
  settings: ChartSyncSettings;
  enabled: boolean;
  revision: number;        // Monotonic counter incremented on any configuration change
  color: string;           // Cyan, Emerald, Amber, Purple
}
```

### 3.2 Fine-Grained Per-Property Settings (`ChartSyncSettings`)
```typescript
interface ChartSyncSettings {
  crosshair: boolean;        // Default: false
  visibleTimeRange: boolean; // Default: false
  instrument: boolean;       // Default: false
  interval: boolean;         // Default: false
  chartType: boolean;        // Default: false
  drawings: boolean;         // Default: false
}
```

### 3.3 Event Envelope (`ChartSyncEvent`)
```typescript
interface ChartSyncEvent<T> {
  eventId: string;
  groupId: string;
  groupRevision: number;
  sourcePanelId: string;
  sourceGeneration: number;
  property: ChartSyncProperty;
  sequence: number;          // Monotonic sequence per panel & property
  origin: "USER" | "SYNC_APPLIED";
  timestampMs: number;
  payload: T;
}
```

---

## 4. Synchronization Behaviors

### 4.1 Linked Crosshairs
- Propagates canonical UTC timestamps on cursor hover across member charts.
- Throttled using `requestAnimationFrame` coalescing to avoid excessive React rerenders during rapid pointer motion.
- Renders `<LinkedCrosshairOverlay />` with a high-precision vertical dashed guide line and timestamp tag badge at the bottom time axis.
- Cleans up immediately on `mouseleave` or when source crosshair exits.
- Displays no fabricated OHLC tooltips if the destination chart has no bar at that timestamp.

### 4.2 Linked Visible Time Ranges (Pan & Zoom)
- Captures `{ from, to }` UTC seconds from `timeScale().subscribeVisibleTimeRangeChange`.
- Clamps to destination available coverage `[max(destMin, from), min(destMax, to)]` without bouncing the clamped range back to the source chart.
- Vertical price scales remain strictly independent (autoscaled to each asset's price bounds).

### 4.3 Linked Instruments
- Propagates canonical entity UUID and validated series identity.
- Enforces preflight entitlement verification: target panels check access permissions before adopting the series.
- Recalculates indicators on destination panel using the new series' qualified historical bars.
- Preserves drawing context isolation (does not copy drawings across instruments).
- Reuses Stage 43 reference counting via `sharedSubscriptionManager`.

### 4.4 Linked Intervals & Chart Types
- Propagates canonical interval IDs (`1m`, `5m`, `15m`, `1h`, `1d`, `1w`, `1M`).
- Preserves case distinction between minute (`1m`) and month (`1M`).
- Verifies series availability: if unsupported, preserves existing interval and logs explicit status.
- Propagates supported chart types (`candlestick`, `bar`, `line`, `area`).
- Candlestick and Bar require full OHLC; line-only series reject candlestick requests cleanly.

### 4.5 Compatible Drawing Synchronization
- Opt-in toggle requiring strict compatibility gate verification.
- Validates identical canonical instrument UUID and quotation currency.
- Performs deep cloning of drawing anchors so each panel maintains an independent mutable instance in its `DrawingSessionStore`.

---

## 5. User Interface & Controls

1. **Toolbar Button (`ChartSyncButton`)**:
   - Placed in the workspace top bar alongside the layout selector:
     `[Sync: Group A (2 linked)]` or `[Sync: Independent]`.
   - Color-coded group badge (Cyan, Emerald, Amber).
   - Opens `ChartSyncMenu`.
2. **Synchronization Manager Popover (`ChartSyncMenu`)**:
   - Group selector tabs with add/delete/rename capabilities.
   - Master group enable/pause toggle.
   - Panel membership checkboxes (`P1`, `P2`, `P3`, `P4`).
   - Per-property toggle switches with clear descriptions.
   - Quick action: **"Align Group to Active Panel"**.
   - Quick action: **"Restore All Panels to Independent Mode"**.
   - Institutional synchronization policy disclosure banner.
3. **Per-Panel Header Badge**:
   - Header displays `[P1] [LINK A]` or `[P2] [IND]`.

---

## 6. Verification and Quality Gates

1. **Unit & Integration Suite (`tests/charts-synchronization.test.ts`)**:
   - 10 comprehensive tests covering group models, default independence, event ordering, loop prevention, crosshairs, time ranges, instruments, intervals, drawings, and security invariants.
   - Execution time: ~25ms (10 pass, 0 fail).
2. **Full Charts Regression Suite (Stages 66–73)**:
   - 80 automated tests passing (80 pass, 0 fail).
3. **TypeScript Typecheck**:
   - Clean compilation (`npx tsc --noEmit` exited with code 0).
4. **Next.js Production Build**:
   - All 38 routes compiling successfully.

---

## 7. Deferred to Stage 74

- Persistent saved chart layouts (PostgreSQL database backing).
- Cloud-saved synchronization group configurations.
- Cross-device chart layout restoration.
- Saved drawing collections and templates.
