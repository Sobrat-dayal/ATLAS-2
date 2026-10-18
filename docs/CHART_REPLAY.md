# ATLAS Historical Chart Replay V1 Architecture (Stage 75)

## 1. Executive Summary

Stage 75 delivers **Historical Chart Replay V1**, introducing institutional historical chart replay inside the canonical ATLAS Charts module (`/charts`). Users can select an instrument, timeframe, and historical starting point, and step or play forward candle-by-candle through historical market development with strict temporal integrity.

The core architectural invariant of Stage 75 is:
**The replayed chart must contain only qualified historical observations that have become visible at the current replay position. If the replay cursor is positioned at bar $N$, bars $N+1$ and later must never appear in the chart, price autoscaling, candlestick rendering, indicator calculations, legends, tooltips, or crosshair inspection.**

```
+----------------------------------------------------------------------------------------------------+
|                                    ATLAS REPLAY WORKSPACE                                          |
|                                                                                                    |
|  [LAYOUT: 2-Columns]   [REPLAY ACTIVE: P1 SPY 1D]   [EXIT REPLAY]   [SYNC: Isolated]   [ACTIVE: P1]    |
|                                                                                                    |
|  +---------------------------------------------------+------------------------------------------+  |
|  | PANEL 1: REPLAY MODE (SPY, 1D, Cursor: 2024-03-15)| PANEL 2: NORMAL LIVE MODE (BTCUSDT, 1h) |  |
|  | [RESTART] [STEP <] [PLAY/PAUSE] [STEP >] [1.0x]   | - Normal live quotes streaming           |  |
|  | - Strictly cursor-bounded bars [0..cursor_index]  | - Global WebSocket connected             |  |
|  | - Live quote overlay strictly suppressed          | - Standard autoscale & full history      |  |
|  | - TA-Lib indicators computed on revealed bars only | - Normal sync group participation        |  |
|  | - Autoscale ignores unrevealed future bars        | - Normal drawing tools active            |  |
|  +---------------------------------------------------+------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
                                                   |
                         CENTRAL REPLAY BOUNDARY GATE (NO LOOK-AHEAD)
                                                   |
                                                   v
                       +---------------------------------------+
                       |       ReplaySessionDTO (Ephemeral)    |
                       |       - session_id (UUID4)            |
                       |       - target_panel_id (Stage 72 ID) |
                       |       - cursor_index / start_index    |
                       |       - cursor_bar (ChartBarDTO)      |
                       |       - revealed_bars_count           |
                       |       - playback_speed (bars/sec)     |
                       |       - source_revision_fingerprint   |
                       +---------------------------------------+
                                                   |
                 AUTHENTICATED FASTAPI API (`/api/v1/charts/replay`)
                                                   |
                                                   v
                       +---------------------------------------+
                       |    Historical Chart Replay Service    |
                       |    - In-memory session manager        |
                       |    - 60-min inactivity TTL / quota    |
                       |    - Canonical historical reads       |
                       |    - Zero synthetic bar generation    |
                       +---------------------------------------+
```

---

## 2. Replay vs Normal Mode

The system enforces an explicit dichotomy between two operating modes:

1. **NORMAL Mode (Stages 66–74)**:
   - Full historical data pagination and caching via `chartQueryCache`.
   - Real-time quote streaming via `sharedSubscriptionManager` and global WebSocket.
   - Stage 73 synchronization group propagation.
   - Stage 74 layout persistence and dirty-state tracking.

2. **REPLAY Mode (Stage 75)**:
   - Bounded historical series revealed strictly up to the replay cursor ($[0 \dots \text{cursor\_index}]$).
   - Real-time live quotes suppressed on the replayed panel (set to `null`) to prevent price drift and scale distortion.
   - Synchronization isolation: linked instruments and intervals cannot mutate the replayed series; crosshair events with timestamps beyond the cursor are rejected.
   - Ephemeral session state: replay cursor and playback status are never serialized into Stage 74 persistent layouts and never mark layouts dirty.

---

## 3. Future-Data Boundary Gating (No Look-Ahead)

Stage 75 strictly prohibits visual masking workarounds (e.g., rendering all future candles and drawing an opaque rectangle over them). The boundary gate physically slices the historical array:

$$\text{revealed\_bars} = \text{qualified\_bars}[0 \dots \text{cursor\_index}]$$

This physical data boundary guarantees:
- **Candlestick Rendering**: Bars $N+1$ and later are not in the series passed to the chart library.
- **Autoscale Isolation**: Highs and lows of future bars cannot influence $Y$-axis scaling or bounding boxes.
- **Crosshair Inspection**: Tooltips and hover bars can only query bars $\le \text{cursor\_index}$.
- **Indicator Gating**: TA-Lib inputs and outputs terminate exactly at the cursor bar.
- **Manual Drawing Protection**: Drawings anchored beyond the cursor cannot reveal future market observations.

---

## 4. Replay-Aware Technical Indicators (TA-Lib)

All indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV) reuse the established Stage 69 Indicator Registry and Stage 70 production calculators:

- **Warmup History**: Bounded earlier historical bars before the start index are used strictly for algorithmic warmup (e.g., recursive smoothing for EMA/RSI).
- **No Future Inputs**: Indicator calculation requests receive `barsCount = effectiveBars.length`.
- **Step Forward ($+1$)**: Indicator series is recomputed or appended to include the newly revealed bar.
- **Step Backward ($-1$)**: The latest indicator output is truncated; previous outputs are deterministically restored.
- **Cache Isolation**: Indicator cache keys include `replay_session_id` and `cursor_revision`, ensuring normal-mode results with future data are never shared with replay consumers.

---

## 5. Playback Controller & Scheduler

The frontend `ReplayStore` and `useChartReplay` hook manage playback deterministically:

- **Play**: Initiates client-side timer firing at intervals:
  $$\Delta t = \max\left(100\text{ ms}, \text{round}\left(\frac{1000}{\text{playbackSpeed}}\right)\right)$$
- **Pause**: Halts the timer immediately, preserving visible history.
- **Step Forward**: Advances `cursor_index` by 1 bar; if `cursor_index == total_bars - 1`, transitions to `END_OF_DATA` and stops the timer.
- **Step Backward**: Decrements `cursor_index` by 1 bar, popping the latest bar from `revealedBars`.
- **Restart**: Seeks back to `start_index` deterministically.
- **Seek**: Moves cursor to a specific historical timestamp or bar index within authorized coverage.
- **Monotonic Speed**: Selectable speeds: `0.5x`, `1.0x`, `2.0x`, `5.0x`, `10.0x` bars per second.
- **In-Flight Step Suppression**: `isStepping` guard prevents timer drift from spawning concurrent step requests.

---

## 6. Historical Data Semantics & Methodological Transparency

Stage 75 maintains strict institutional transparency regarding historical data:

1. **Current Revised Dataset vs. Point-in-Time Availability**:
   - Standard historical OHLCV records represent today's best available revised, split-adjusted dataset.
   - Retrospectively adjusted corporate actions (splits, dividends) may contain post-event adjustments.
   - The UI and API explicitly state:
     > *"Historical playback uses the currently available adjusted/revised dataset and does not guarantee point-in-time information availability."*
2. **Finalized Bars Only**:
   - Replay reveals completed, finalized historical bars.
   - It does not fabricate intraday random walks or artificial ticks from daily OHLC records.
3. **No Synthetic Data**:
   - Trading holidays, weekend closures, and exchange halts are preserved as legitimate gaps.
   - Missing volume remains unavailable (`null`), never fabricated as zero.

---

## 7. Multi-Chart & Stage 73 Synchronization Compatibility

1. **Single-Panel Replay Target**:
   - V1 binds replay to a single Stage 72 panel (`panel_id`).
   - Other panels in 2-column, 2-row, or 4-grid layouts remain in normal live mode.
2. **Synchronization Isolation**:
   - Incompatible sync actions (`instrument`, `interval`) directed to the replayed panel return `result: "UNCHANGED"` with reason `"Replay panel isolated"`.
   - Incoming crosshair moves with timestamp $> \text{cursor\_time}$ return `result: "UNCHANGED"` with reason `"Replay future isolation"`.
3. **Panel Teardown**:
   - If the user removes the replayed panel from the workspace, the replay session is cleanly terminated via `exitReplay()`.

---

## 8. Stage 74 Saved Layout Compatibility

Stage 74 persistent layout documents (`SavedChartLayoutDocumentV1`) are protected against pollution:

- **Ephemeral Replay State**: `session_id`, `cursor_index`, `revealed_bars`, `playback_speed`, and timer handles are strictly excluded from serialization allowlists.
- **Dirty-State Invariance**: Stepping or playing historical replay does not alter `isWorkspaceDirty()` or prompt the user to save unsaved layout changes.
- **Layout Switch Safety**: Loading a saved layout safely exits active replay before hydrating the new workspace.

---

## 9. API Specification

All replay APIs are mounted under `/api/v1/charts/replay`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/charts/replay/capabilities` | Returns historical bar coverage, date limits, and interval support. |
| `POST` | `/api/v1/charts/replay/sessions` | Creates an authenticated ephemeral replay session with start window. |
| `GET` | `/api/v1/charts/replay/sessions/{id}` | Reads current replay session cursor, status, and metadata. |
| `POST` | `/api/v1/charts/replay/sessions/{id}/step` | Steps cursor forward or backward by `count` bars. |
| `POST` | `/api/v1/charts/replay/sessions/{id}/seek` | Seeks cursor to target index or ISO timestamp. |
| `DELETE` | `/api/v1/charts/replay/sessions/{id}` | Closes session and releases ephemeral resources. |
| `POST` | `/api/v1/charts/replay/sessions/{id}/indicators` | Recalculates indicators strictly over revealed history. |

### Quotas & TTL

- **Session TTL**: 60 minutes of inactivity.
- **User Quota**: Maximum 5 concurrent active replay sessions per authenticated user.
- **Memory Bounds**: Ephemeral in-memory session manager with automatic garbage collection of expired sessions.

---

## 10. Security & Read-Only Invariants

Historical Chart Replay operates under strict read-only constraints:
- **Canonical OHLCV Writes**: 0
- **Database Migrations / Schema Changes**: 0
- **Ingestion Jobs Triggered**: 0
- **Trading Orders Placed**: 0
- **Broker Sandbox Calls**: 0
- **Autonomous Agent Invocations**: 0
- **LLM Calls**: 0
- **Market Data Entitlements**: Checked before session initialization.
- **Session Ownership**: Enforced on every mutation endpoint; users cannot step or close sessions owned by another user.

---

## 11. Verification Matrix

| Category | Suite | Tests | Result |
|---|---|---|---|
| Backend Replay API | `apps/api/tests/test_chart_replay.py` | 10 | 10 / 10 PASSED |
| Backend Regression (Stages 66-74) | `apps/api/tests/test_charts_*.py` | 97 | 97 / 97 PASSED |
| Frontend Replay Suite | `apps/web/tests/charts-replay.test.ts` | 10 | 10 / 10 PASSED |
| Frontend Regression (Stages 66-74) | `apps/web/tests/charts-*.test.ts` | 90 | 90 / 90 PASSED |
| TypeScript Compiler | `apps/web: tsc --noEmit` | - | PASSED (0 errors) |
| Next.js Production Build | `apps/web: npm run build` | 38 routes | PASSED (3.3s build) |
| Python Lint & Format | `apps/api: ruff check` | - | PASSED (0 errors) |
