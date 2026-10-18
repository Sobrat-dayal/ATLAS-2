# ATLAS Chart Drawing Tools V1 (Stage 71)

## 1. Executive Summary

Stage 71 introduces **Chart Drawing Tools V1** to the ATLAS Charts module (`/charts`), transforming the charting workspace into an institutional technical analysis and visual annotation environment inspired by Bloomberg Terminal and TradingView.

The system is architected around **strict financial coordinate anchoring**: drawings are defined by canonical financial coordinates `{ time, price }`, never by transient screen pixels or mutable bar indices. When charts are panned, zoomed, resized, or switched across supported timeframes, drawing geometries dynamically re-project from their immutable financial anchors.

---

## 2. Canonical Roadmap Scope Boundaries

| Capability | Stage 71 Ownership | Next Stage / Scope Owner |
|---|---|---|
| **Interactive Drawing Tools** | **OWNED (Stage 71)** | Extended in future chart stages |
| **Session Drawing State** | **OWNED (Stage 71)** | Session-level in-memory state |
| **Smart OHLC Snapping** | **OWNED (Stage 71)** | Qualified canonical bar snapping |
| **Undo / Redo History** | **OWNED (Stage 71)** | Bounded 100-step transaction history |
| **Multi-Chart Layouts** | **DEFERRED** | Stage 72 |
| **Cross-Chart Sync** | **DEFERRED** | Stage 73 |
| **Saved Chart Layouts** | **DEFERRED** | Stage 74 (Cloud persistence, schema migrations) |
| **Chart Replay** | **DEFERRED** | Stage 75 |
| **Automated Trading / Alerts** | **DEFERRED** | Stages 80, 144, 145 |

**Critical Architectural Constraint:** Stage 71 does NOT introduce persistent database tables (`saved_chart_drawings`) or external synchronization APIs. All drawings reside in bounded session-level memory scoped by `[instrument_entity_id : price_basis]`.

---

## 3. Supported Drawing Tools (The 9 Canonical Tools)

| Tool | Anchors | Category | Behavior & Semantics |
|---|:---:|:---:|---|
| **Trendline** | 2 | Line | Direct line segment between $(T_0, P_0)$ and $(T_1, P_1)$ with draggable endpoints and whole-line translation. |
| **Horizontal Line** | 1 | Line | Infinite horizontal level at price $P_0$ spanning full chart width with right-aligned price badge. |
| **Horizontal Ray** | 1 | Line | Originates at $(T_0, P_0)$ and extends horizontally to the right edge of the chart pane. |
| **Vertical Line** | 1 | Line | Infinite vertical time marker through timestamp $T_0$ with bottom date/time badge. |
| **Rectangle Zone** | 2 | Zone | Opposing corners $(T_0, P_0)$ and $(T_1, P_1)$ highlighting a price/time area with customizable fill opacity. |
| **Price Range** | 2 | Measurement | Shaded vertical band calculating $\Delta P = P_1 - P_0$ and $\Delta P\% = \frac{P_1 - P_0}{P_0} \times 100\%$ with sign. |
| **Time Range** | 2 | Measurement | Shaded horizontal band measuring elapsed calendar duration and qualified loaded bar count. |
| **Price & Time** | 2 | Measurement | Simultaneous bounding box and vector measuring $\Delta P$, $\Delta P\%$, elapsed time, and bar count. |
| **Fibonacci Retracement**| 2 | Fibonacci | Standard retracement levels ($0\%, 23.6\%, 38.2\%, 50\%, 61.8\%, 78.6\%, 100\%$) oriented along anchor direction. |

---

## 4. Financial Coordinate System & Screen Mapping

### 4.1 Coordinate Independence
The system isolates the following coordinate spaces:
1. **Financial Time:** Canonical UTC Unix timestamp in seconds (`number`).
2. **Financial Price:** Validated finite quotation value (`number`).
3. **Screen CSS Pixels:** Position within the chart container (`{ x, y }`).
4. **Device Pixels:** Backing canvas resolution handled natively via SVG vector rendering.

### 4.2 Bidirectional Mapping
- **`financialToScreen(anchor)`**:
  - Utilizes `timeScale.timeToCoordinate(anchor.time)` and `series.priceToCoordinate(anchor.price)`.
  - Fallback projection: When timestamps fall between loaded bars or off-screen, linear interpolation projects screen X based on surrounding canonical bar timestamps.
- **`screenToFinancial(point)`**:
  - Utilizes `timeScale.coordinateToTime(point.x)` and `series.coordinateToPrice(point.y)`.
  - Fallback interpolation: If pointing beyond the rightmost bar, maps time according to chart bar spacing.

---

## 5. Mathematical Semantics

### 5.1 Fibonacci Retracement Levels
For start price $P_0$ and end price $P_1$:
$$L(r) = P_0 + r \times (P_1 - P_0)$$
Ratios supported:
- `0.0% (0.000)`
- `23.6% (0.236)`
- `38.2% (0.382)`
- `50.0% (0.500)`
- `61.8% (0.618)` (Golden ratio)
- `78.6% (0.786)`
- `100.0% (1.000)`

Direction is strictly preserved:
- Drawn Low to High: $0\%$ at low, $100\%$ at high.
- Drawn High to Low: $0\%$ at high, $100\%$ at low.
- Negative futures prices are supported without mathematical breakdown.

### 5.2 Price Measurement
$$\Delta P = P_2 - P_1$$
$$\Delta P\% = \begin{cases} \frac{P_2 - P_1}{P_1} \times 100\% & \text{if } P_1 > 0 \\ \text{"N/A (base 0)"} & \text{if } P_1 = 0 \\ \text{"N/A (negative base)"} & \text{if } P_1 < 0 \end{cases}$$

### 5.3 Time Measurement
- **Elapsed Duration:** $|T_2 - T_1|$ converted into institutional calendar units (`Xd Yh`, `Xh Ym`, or `Xm`).
- **Bar Count:** Count of qualified loaded bars with $T_{\min} \le \text{bar.time\_unix} \le T_{\max}$. Non-trading weekend/holiday gaps do not generate synthetic bars.

---

## 6. Smart Snapping Engine

Snapping assists precise alignment to genuine market observations without inventing data:
- **`OFF`**: Raw pointer coordinates.
- **`NEAREST_BAR`**: Snaps time to the nearest qualified bar within screen-space pixel tolerance (default 15px).
- **`OHLC`**: Snaps time to the nearest bar, and price to the nearest Open, High, Low, or Close observation of that bar.
- **Modifier Override**: Holding `Shift` or `Alt` temporarily bypasses snapping for sub-pixel precision.
- **Visual Feedback**: Displays a subtle emerald target marker and snap label (`SNAP: HIGH`, `SNAP: CLOSE`, etc.).

---

## 7. Interaction Controller & UX State Machine

```
   [IDLE]  <---------------------------- (Esc / Deselect)
     |
     | Tool Armed
     v
[TOOL_ARMED]
     |
     | 1-Anchor Tool Click -> [COMMITTED] -> [IDLE]
     | 2-Anchor Tool Click
     v
[PLACING_NEXT_ANCHOR] (Transient Preview on mousemove)
     |
     | Second Click -> [COMMITTED] -> [IDLE]
```

### Dragging & Selection
- **Hovering:** Highlights drawing body or anchor handle.
- **Handle Dragging:** Drags individual anchor while keeping opposing anchors stationary.
- **Body Dragging:** Translates all drawing anchors by $(\Delta T, \Delta P)$.
- **Non-Intrusive Pass-Through:** When `activeTool === null` and no drawing is clicked, pointer events pass through to Lightweight Charts, preserving chart mouse/touch pan & pinch zoom.

---

## 8. Command-Based Undo / Redo

- **Single Gesture Atomicity:** Dragging a drawing emits continuous pointer-move events, but records exactly **one** undoable `DrawingCommand` upon pointer-up / commit.
- **Redo Branch Invalidation:** Executing any new action after Undo immediately clears the future redo stack.
- **Bounded Capacity:** 100 commands per instrument context.
- **Supported Operations:** `CREATE`, `DELETE`, `MOVE`, `EDIT_ANCHOR`, `CHANGE_STYLE`, `LOCK`, `VISIBILITY`, `CLEAR`.
- **Keyboard Shortcuts:**
  - `Ctrl + Z` / `Cmd + Z`: Undo.
  - `Ctrl + Shift + Z` / `Cmd + Shift + Z` / `Ctrl + Y`: Redo.
  - `Delete` / `Backspace`: Delete selected drawing (ignored when typing in form inputs).
  - `Escape`: Cancel creation or deselect active drawing.

---

## 9. Accessibility & Numerical Coordinate Editing

- **Drawing Manager:** A slide-out drawer accessible via toolbar (`Layers` icon) displaying all active drawings with type, anchor prices, lock, visibility, and delete controls.
- **Drawing Coordinate Editor:** An accessible dialog allowing direct numerical input of price and ISO timestamp / date for every anchor point, enforcing finite-number validation.
- **Visible Focus & Contrast:** Meets institutional high-contrast criteria against dark chart backgrounds without relying exclusively on color.

---

## 10. Design Invariants & Security

- **Strict Aesthetic:** Institutional dark theme adhering to Tailwind zinc palettes (`zinc-950`, `zinc-900`, `zinc-800`), cyan accents, and Geist Mono typography. No purple gradients, no emoji icons, no glowing cartoon borders.
- **Financial Integrity:** User drawings are pure visual annotations. They do NOT mutate canonical OHLCV, Quotes, Indicators, or execute broker trades.
- **Zero LLM Overhead:** Drawing interactions execute with zero LLM API calls.
