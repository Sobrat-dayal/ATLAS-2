# ATLAS Multi-Chart Layouts V1 Architecture (Stage 72)

## 1. Executive Summary

Stage 72 transforms the ATLAS Charts module (`/charts`) from a single-chart workspace into an institutional-grade, multi-chart financial workstation. Users can configure and examine up to four simultaneous, independently functioning financial chart panels with custom instruments, intervals, chart types, TA-Lib indicators, and precision drawing layers.

The multi-chart architecture strictly adheres to the core ATLAS engineering principle:
**Each chart panel owns its own presentation and interaction state, while shared market-data infrastructure remains centralized and reference-counted.**

```
+-----------------------------------------------------------------------------+
|                         ATLAS MULTI-CHART WORKSPACE                         |
|                                                                             |
|  [LAYOUT SELECTOR: 4-Grid]           [ACTIVE PANEL: P2 - BTCUSDT]           |
|                                                                             |
|  +------------------------------------+----------------------------------+  |
|  | PANEL 1 (SPY, 1D, Candles)         | PANEL 2 (BTCUSDT, 1h, Candles)   |  |
|  | - Independent Viewport & Crosshair | - Active Outline & Header Focus  |  |
|  | - EMA(20) Overlay                  | - RSI(14) Subpane                |  |
|  | - Trendline & Fibo Drawings        | - Support/Resistance Levels      |  |
|  +------------------------------------+----------------------------------+  |
|  |           ================ HORIZONTAL SPLITTER ================       |  |
|  +------------------------------------+----------------------------------+  |
|  | PANEL 3 (EURUSD, 15m, Line)        | PANEL 4 (AAPL, 5m, OHLC Bars)    |  |
|  | - Independent Viewport & Crosshair | - Independent Viewport           |  |
|  | - Bollinger Bands Overlay          | - MACD(12,26,9) Subpane          |  |
|  | - Measurement Tool                 | - Rectangle Box Annotations      |  |
|  +------------------------------------+----------------------------------+  |
+-----------------------------------------------------------------------------+
                                       |
                   SHARED INFRASTRUCTURE LAYER
                                       |
    +----------------------------------+----------------------------------+
    |                                  |                                  |
    v                                  v                                  v
[ChartQueryCache]          [SharedSubscriptionManager]         [DrawingStore.getForPanel]
- Deduplicates OHLCV       - Reference-counted WebSocket       - Per-panel drawing isolation
- In-flight request merge  - Single stream per series          - Independent Undo/Redo
- Bounded LRU memory       - Independent panel pause           - Anchored to time/price
```

---

## 2. Layout Presets and Registry

The multi-chart layout engine defines six canonical presets registered in `CHART_LAYOUTS`:

| Layout ID | Panels | Grid Structure | Intended Analytical Use Case |
|---|:---:|---|---|
| `single` | 1 | Full workspace single viewport | Deep dive single-instrument focus & drawing analysis |
| `two-columns` | 2 | Side-by-side horizontal split | Pair trading, correlation, and cross-asset comparison |
| `two-rows` | 2 | Vertically stacked vertical split | Dual-timeframe analysis (e.g. 1D trend vs 15m entry) |
| `three-left-focus` | 3 | Large left (60%), 2 stacked right (40%) | Benchmark on left, sector/peer components on right |
| `three-top-focus` | 3 | Large top (60%), 2 columns below (40%) | Broad macro index on top, tactical setups below |
| `four-grid` | 4 | 2x2 balanced grid (2 rows × 2 columns) | Institutional multi-asset / cross-currency workstation |

### Layout Definition Contract
```typescript
export interface LayoutDefinition {
  id: ChartLayoutId;
  label: string;
  description: string;
  panelCount: number;
  icon: string;
  minWidthPx: number;
  minHeightPx: number;
}
```

---

## 3. Panel Identity & State Independence

### 3.1 Stable Panel Identity
Each mounted panel possesses a stable, deterministic identity (`panel-1`, `panel-2`, `panel-3`, `panel-4`). Panel IDs are decoupled from financial instrument UUIDs or tickers. When a user switches from `single` to `four-grid` and back to `single`, the primary panel configuration and session drawings are completely preserved.

### 3.2 State Isolation Matrix
Every chart panel maintains strict encapsulation:

| Dimension | Scope | Isolation Mechanism |
|---|---|---|
| **Instrument & Series** | Per Panel | Independent `symbol` and `selectedInstrument` |
| **Interval / Timeframe** | Per Panel | Independent `interval` state (`1m`, `5m`, `15m`, `1h`, `1D`, `1W`) |
| **Chart Type** | Per Panel | Independent `renderMode` (`candlestick`, `bar`, `line`, `area`) |
| **Viewport & Zoom** | Per Panel | Independent `IChartApi` time-scale and price-scale instances |
| **Crosshair Hover** | Per Panel | Local crosshair coordinate emissions |
| **Technical Indicators** | Per Panel | Scoped `useIndicators` instance, unique instance IDs, local subpanes |
| **Drawings & Undo/Redo** | Per Panel | `DrawingSessionStore.getForPanel(panelId)`, independent undo stack |
| **Live Display & Pause**| Per Panel | Independent pause flag in subscription listener |
| **Error Handling** | Per Panel | `ChartPanelErrorBoundary` isolating errors from sibling panels |

---

## 4. Active Panel Controller & Global Context

### 4.1 Active Panel Mechanics
Exactly one visible panel is designated as the active panel (`activePanelId`).
- **Activation Triggers**: Clicking the panel header, focusing the chart canvas, or selecting it via keyboard.
- **Visual Feedback**: Subtle cyan border highlight (`border-cyan-500/80`), cyan ring (`ring-1 ring-cyan-500/40`), and top bar badge `Active: P2 (BTCUSDT)`.
- **Global Search Targeting**: Selecting a symbol in the global search bar updates only the active panel. Inactive panels retain their existing instruments.
- **No Circular Feedback Loops**: Updating the active panel synchronizes with global `SelectedEntity` with explicit directionality, preventing cascaded re-selection loops across sibling panels.

---

## 5. Shared Market Data Infrastructure

### 5.1 Centralized Historical Query Cache (`ChartQueryCache`)
To prevent redundant HTTP calls and provider load when multiple panels display the same series or interval:
- **Canonical Cache Key**: `${instrument_id || symbol}:${interval}:${start}:${end}:${before}:${limit}`
- **In-Flight Request Merging**: If two panels request `SPY 1D` simultaneously upon layout mount, a single network Promise is shared.
- **Deep-Cloned Immutability**: Returned datasets are immutable copies to prevent cross-panel bar mutations.
- **LRU Memory Eviction**: Enforces `WORKSPACE_RESOURCE_BUDGET.queryCacheCapacity` (default 50 entries).

### 5.2 Reference-Counted Live Subscriptions (`SharedChartSubscriptionManager`)
Stage 72 connects all panels to the central Stage 43 WebSocket gateway without opening redundant transport connections:
- **Reference Counting**: Keyed by canonical series identity.
  - Panel 1 subscribes to `BTCUSDT` -> `refCount = 1`, single controller starts.
  - Panel 2 subscribes to `BTCUSDT` -> `refCount = 2`, reuses active stream.
  - Panel 1 pauses -> only Panel 1 ceases drawing new ticks; Panel 2 continues live.
  - Panel 1 unmounts -> `refCount = 1`, stream stays active for Panel 2.
  - Panel 2 unmounts -> `refCount = 0`, stream is cleanly disposed.

---

## 6. Panel Resizing and Responsive Presentation

### 6.1 Resizable Splitters
- Implemented with `AtlasSplit`, `AtlasPanel`, and `AtlasResizeHandle` (`react-resizable-panels`).
- Supports mouse drag, touch drag, and keyboard navigation (`ArrowLeft`, `ArrowRight`, `ArrowUp`, `ArrowDown`).
- Minimum constraints enforced: min panel width ~320px, min panel height ~220px to prevent collapsed zero-pixel rendering.
- `ResizeObserver` propagates dimensional updates to Lightweight Charts canvas without destroying or remounting chart instances.

### 6.2 Responsive Mobile Tab Fallback
On screens narrower than 768px:
- Automatically renders `ChartPanelTabs` (`[P1 SPY] [P2 BTCUSDT] [P3 EURUSD] [P4 AAPL]`).
- Displays one usable, full-resolution chart panel at a time.
- **Critical Policy**: Mobile presentation does NOT mutate `layoutId` to `single`. When the viewport widens back to desktop, the user's selected multi-chart grid is instantly restored.

---

## 7. Resource Budgets and Lifecycle

Stage 72 enforces strict resource limits:

```typescript
export const WORKSPACE_RESOURCE_BUDGET: ResourceBudgetConfig = {
  maxVisiblePanels: 4,
  maxMountedRenderers: 4,
  minPanelWidthPx: 320,
  minPanelHeightPx: 220,
  maxDrawingsPerPanel: 250,
  maxIndicatorsPerPanel: 12,
  maxLiveSubscriptions: 10,
  queryCacheCapacity: 50,
};
```

When layouts are reduced (e.g. `four-grid` -> `two-columns`), unused panels transition to `SUSPENDED` lifecycle status, releasing active live listeners and animation frames while preserving session configurations for subsequent expansion.

---

## 8. Roadmap Boundaries & Next Stage

- **Stage 72 (Current)**: Independent Multi-Chart Layouts V1.
- **Stage 73 (Next)**: Chart Synchronization (optional opt-in linked crosshairs, shared cursor timestamps, linked time ranges, and synchronized pan/zoom).
- **Stage 74**: Saved Chart Layouts & Cloud Persistence (PostgreSQL layout schemas).
- **Stage 75**: Chart Replay Engine.
