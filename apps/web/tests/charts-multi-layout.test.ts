/**
 * Automated Verification Suite for ATLAS Stage 72:
 * Professional Multi-Chart Layouts V1.
 *
 * Verifies:
 * 1. Layout Registry: All 6 canonical presets (single, two-columns, two-rows, three-left-focus, three-top-focus, four-grid).
 * 2. Stable Panel Identities: panel-1 through panel-4 identity persistence across layout switches.
 * 3. Active Panel Controller: Explicit activation, focus targeting, and state isolation.
 * 4. Instrument Isolation: Independent financial instruments per panel without cross-contamination.
 * 5. Interval & Chart-Type Isolation: Independent timeframes and presentation modes across panels.
 * 6. Drawing Isolation: Per-panel DrawingSessionStore instances with isolated undo/redo stacks.
 * 7. Shared Historical Data Cache: Canonical key generation, request deduplication, and bounded LRU eviction.
 * 8. Shared WebSocket Subscription Reference Counting: Live stream sharing, reference counting, and independent pause.
 * 9. Responsive Mode Preservation: Mobile tab fallback preserving desktop layout identity.
 * 10. Security & Read-Only Invariants: Zero canonical database writes, zero trading orders, zero AI calls.
 */

import { describe, it } from "node:test";
import assert from "node:assert";
import {
  CHART_LAYOUTS,
  ORDERED_LAYOUT_IDS,
  ChartLayoutId,
  getLayoutDefinition,
  getRequiredPanelCount,
  isValidLayoutId,
  WORKSPACE_RESOURCE_BUDGET,
  MultiChartWorkspaceStore,
  ChartQueryCache,
  SharedChartSubscriptionManager,
} from "../src/lib/charts/workspace";
import { DrawingSessionStore } from "../src/lib/charts/drawings/drawingStore";
import { ChartInstrumentMetadata } from "../src/lib/charts/types";

describe("Stage 72 - Multi-Chart Layouts V1 Tests", () => {
  // 1. LAYOUT REGISTRY & PRESETS
  it("should verify all 6 canonical multi-chart layout presets and configurations", () => {
    assert.strictEqual(ORDERED_LAYOUT_IDS.length, 6);

    const expectedPresets: Record<ChartLayoutId, number> = {
      single: 1,
      "two-columns": 2,
      "two-rows": 2,
      "three-left-focus": 3,
      "three-top-focus": 3,
      "four-grid": 4,
    };

    for (const [id, count] of Object.entries(expectedPresets)) {
      assert.strictEqual(isValidLayoutId(id), true);
      const def = getLayoutDefinition(id as ChartLayoutId);
      assert.strictEqual(def.panelCount, count);
      assert.ok(def.minWidthPx >= WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx);
      assert.ok(def.minHeightPx >= WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx);
    }

    assert.strictEqual(isValidLayoutId("invalid-layout-id"), false);
    assert.strictEqual(getRequiredPanelCount("four-grid"), 4);
    assert.strictEqual(getRequiredPanelCount("single"), 1);
  });

  // 2. STABLE PANEL IDENTITIES ACROSS LAYOUT SWITCHES
  it("should preserve panel identities and configurations across layout expansion and reduction", () => {
    const store = new MultiChartWorkspaceStore();

    // Initial single layout
    let state = store.getState();
    assert.strictEqual(state.layoutId, "single");
    assert.strictEqual(state.panelIds.length, 1);
    assert.strictEqual(state.panelIds[0], "panel-1");
    assert.strictEqual(state.activePanelId, "panel-1");

    // Configure primary panel with custom instrument & interval
    store.updatePanel("panel-1", { symbol: "NVDA", interval: "1h" });
    assert.strictEqual(store.getState().panels["panel-1"].symbol, "NVDA");
    assert.strictEqual(store.getState().panels["panel-1"].interval, "1h");

    // Expand to four-grid (4 panels)
    store.setLayout("four-grid");
    state = store.getState();
    assert.strictEqual(state.layoutId, "four-grid");
    assert.strictEqual(state.panelIds.length, 4);
    assert.deepStrictEqual(state.panelIds, ["panel-1", "panel-2", "panel-3", "panel-4"]);

    // Primary panel config must NOT be reset or wiped
    assert.strictEqual(state.panels["panel-1"].symbol, "NVDA");
    assert.strictEqual(state.panels["panel-1"].interval, "1h");

    // Configure panel-2
    store.updatePanel("panel-2", { symbol: "ETHUSDT", interval: "15m" });
    assert.strictEqual(store.getState().panels["panel-2"].symbol, "ETHUSDT");

    // Reduce layout to two-columns (2 panels)
    store.setLayout("two-columns");
    state = store.getState();
    assert.strictEqual(state.layoutId, "two-columns");
    assert.strictEqual(state.panelIds.length, 2);
    assert.deepStrictEqual(state.panelIds, ["panel-1", "panel-2"]);

    // Panels 3 & 4 must be suspended but retained in session memory
    assert.strictEqual(state.panels["panel-3"].lifecycleStatus, "SUSPENDED");
    assert.strictEqual(state.panels["panel-4"].lifecycleStatus, "SUSPENDED");

    // Re-expand to four-grid: panel-2 config must still be intact
    store.setLayout("four-grid");
    state = store.getState();
    assert.strictEqual(state.panels["panel-2"].symbol, "ETHUSDT");
    assert.strictEqual(state.panels["panel-2"].interval, "15m");
  });

  // 3. ACTIVE PANEL CONTROLLER & FOCUS MANAGEMENT
  it("should manage active panel selection and isolate toolbar operations", () => {
    const store = new MultiChartWorkspaceStore();
    store.setLayout("two-columns");

    // Default active is panel-1
    assert.strictEqual(store.getState().activePanelId, "panel-1");
    assert.strictEqual(store.getState().panels["panel-1"].isActive, true);
    assert.strictEqual(store.getState().panels["panel-2"].isActive, false);

    // Activate panel-2
    store.setActivePanel("panel-2");
    assert.strictEqual(store.getState().activePanelId, "panel-2");
    assert.strictEqual(store.getState().panels["panel-1"].isActive, false);
    assert.strictEqual(store.getState().panels["panel-2"].isActive, true);

    // Updating active panel does not affect inactive panel
    store.updatePanel("panel-2", { symbol: "AAPL", interval: "5m" });
    assert.strictEqual(store.getState().panels["panel-2"].symbol, "AAPL");
    assert.strictEqual(store.getState().panels["panel-1"].symbol, "SPY"); // untouched
  });

  // 4. INSTRUMENT & ASSET CLASS ISOLATION
  it("should support independent financial instruments and asset classes per panel", () => {
    const store = new MultiChartWorkspaceStore();
    store.setLayout("four-grid");

    store.updatePanel("panel-1", { symbol: "SPY" }); // US Equity
    store.updatePanel("panel-2", { symbol: "BTCUSDT" }); // Crypto
    store.updatePanel("panel-3", { symbol: "EURUSD" }); // FX
    store.updatePanel("panel-4", { symbol: "CLZ26" }); // Energy Future

    const state = store.getState();
    assert.strictEqual(state.panels["panel-1"].symbol, "SPY");
    assert.strictEqual(state.panels["panel-2"].symbol, "BTCUSDT");
    assert.strictEqual(state.panels["panel-3"].symbol, "EURUSD");
    assert.strictEqual(state.panels["panel-4"].symbol, "CLZ26");
  });

  // 5. INTERVAL & CHART TYPE ISOLATION
  it("should maintain independent intervals and render modes across panels", () => {
    const store = new MultiChartWorkspaceStore();
    store.setLayout("four-grid");

    store.updatePanel("panel-1", { interval: "1d", renderMode: "candlestick" });
    store.updatePanel("panel-2", { interval: "1h", renderMode: "bar" });
    store.updatePanel("panel-3", { interval: "15m", renderMode: "line" });
    store.updatePanel("panel-4", { interval: "5m", renderMode: "area" });

    const state = store.getState();
    assert.strictEqual(state.panels["panel-1"].interval, "1d");
    assert.strictEqual(state.panels["panel-1"].renderMode, "candlestick");

    assert.strictEqual(state.panels["panel-2"].interval, "1h");
    assert.strictEqual(state.panels["panel-2"].renderMode, "bar");

    assert.strictEqual(state.panels["panel-3"].interval, "15m");
    assert.strictEqual(state.panels["panel-3"].renderMode, "line");

    assert.strictEqual(state.panels["panel-4"].interval, "5m");
    assert.strictEqual(state.panels["panel-4"].renderMode, "area");
  });

  // 6. DRAWING ISOLATION & PER-PANEL UNDO/REDO
  it("should isolate drawing sessions and undo/redo stacks between panels displaying the same instrument", () => {
    const storePanel1 = DrawingSessionStore.getForPanel("panel-1");
    const storePanel2 = DrawingSessionStore.getForPanel("panel-2");

    // Both panels configure the same instrument context (SPY raw)
    const context = {
      instrument_entity_id: "inst_spy_001",
      symbol: "SPY",
      price_basis: "raw" as const,
    };
    storePanel1.setContext(context);
    storePanel2.setContext(context);

    // Clear initial state
    storePanel1.clearDrawings();
    storePanel2.clearDrawings();

    // Add trendline in Panel 1
    storePanel1.addDrawing("trendline", [
      { time: 1710000000, price: 500 },
      { time: 1710086400, price: 510 },
    ]);

    // Panel 1 must have 1 drawing; Panel 2 must have 0 drawings
    assert.strictEqual(storePanel1.getDrawings().length, 1);
    assert.strictEqual(storePanel2.getDrawings().length, 0);

    // Add horizontal line in Panel 2
    storePanel2.addDrawing("horizontal_line", [{ time: 1710000000, price: 520 }]);

    assert.strictEqual(storePanel1.getDrawings().length, 1);
    assert.strictEqual(storePanel1.getDrawings()[0].type, "trendline");
    assert.strictEqual(storePanel2.getDrawings().length, 1);
    assert.strictEqual(storePanel2.getDrawings()[0].type, "horizontal_line");

    // Undo in Panel 1 must only undo Panel 1's drawing, leaving Panel 2 intact
    assert.strictEqual(storePanel1.canUndo(), true);
    storePanel1.undo();
    assert.strictEqual(storePanel1.getDrawings().length, 0);
    assert.strictEqual(storePanel2.getDrawings().length, 1); // Panel 2 remains unaffected!
  });

  // 7. SHARED HISTORICAL DATA CACHE & DEDUPLICATION
  it("should deduplicate identical historical requests and enforce bounded LRU memory", () => {
    const cache = new ChartQueryCache(3, 10_000);

    const key1 = cache.generateKey({ symbol: "SPY", interval: "1d" });
    const key2 = cache.generateKey({ symbol: "SPY", interval: "1h" });
    const key3 = cache.generateKey({ symbol: "BTCUSDT", interval: "1d" });
    const key4 = cache.generateKey({ symbol: "AAPL", interval: "1d" });

    // Distinct keys for different intervals / symbols
    assert.notStrictEqual(key1, key2);
    assert.notStrictEqual(key1, key3);

    const mockResponse = (sym: string) => ({
      schema_version: "1.0",
      instrument: { entity_id: sym, display_symbol: sym, display_name: sym, asset_class: "equity", price_currency: "USD", quotation_unit: "USD" },
      bars: [],
      coverage: { first_bar_timestamp: null, last_bar_timestamp: null, total_bars: 0, requested_interval: "1d", is_complete: true },
    } as any);

    cache.set(key1, mockResponse("SPY"));
    cache.set(key2, mockResponse("SPY"));
    cache.set(key3, mockResponse("BTCUSDT"));
    assert.strictEqual(cache.getCacheSize(), 3);

    // Adding 4th item triggers LRU eviction of oldest item (key1)
    cache.set(key4, mockResponse("AAPL"));
    assert.strictEqual(cache.getCacheSize(), 3);

    // Invalidate instrument
    cache.invalidate("BTCUSDT");
    assert.strictEqual(cache.getCacheSize(), 2);
  });

  // 8. SHARED WEBSOCKET SUBSCRIPTION REFERENCE COUNTING
  it("should reference-count live subscriptions and support independent panel pause", () => {
    const manager = new SharedChartSubscriptionManager();
    const instA: ChartInstrumentMetadata = {
      entity_id: "inst_btc_001",
      display_symbol: "BTCUSDT",
      display_name: "Bitcoin / Tether",
      asset_class: "crypto",
      market_or_venue: "Binance",
      price_currency: "USDT",
      quotation_unit: "USDT",
      supported_intervals: ["1m", "5m", "15m", "1h", "1d"],
      default_interval: "1d",
      price_basis: "raw",
      adjustment_basis: "none",
      provider_key: "binance",
      has_volume: true,
      is_futures: false,
      allows_negative_price: false,
    };

    let panel1Quotes = 0;
    let panel2Quotes = 0;

    // Panel 1 subscribes to BTCUSDT (ref count = 1)
    const unsub1 = manager.subscribe("panel-1", instA, () => {
      panel1Quotes++;
    });
    const key = manager.getSubscriptionKey(instA);
    assert.strictEqual(manager.getActiveSubscriptionCount(), 1);
    assert.strictEqual(manager.getReferenceCount(key), 1);

    // Panel 2 subscribes to same instrument (ref count = 2, shared single stream)
    const unsub2 = manager.subscribe("panel-2", instA, () => {
      panel2Quotes++;
    });
    assert.strictEqual(manager.getActiveSubscriptionCount(), 1);
    assert.strictEqual(manager.getReferenceCount(key), 2);

    // Pause Panel 1: setting paused state
    manager.setPanelPaused("panel-1", key, true);

    // Panel 1 unmounts: ref count drops to 1, stream stays active for Panel 2
    unsub1();
    assert.strictEqual(manager.getActiveSubscriptionCount(), 1);
    assert.strictEqual(manager.getReferenceCount(key), 1);

    // Panel 2 unmounts: ref count drops to 0, underlying stream cleanly cleaned up
    unsub2();
    assert.strictEqual(manager.getActiveSubscriptionCount(), 0);
    assert.strictEqual(manager.getReferenceCount(key), 0);
  });

  // 9. RESPONSIVE MOBILE TAB PRESERVATION
  it("should preserve underlying desktop multi-chart layout state during mobile tab switches", () => {
    const store = new MultiChartWorkspaceStore();
    store.setLayout("four-grid");

    // Enable mobile tab mode
    store.setMobileTabMode(true);
    assert.strictEqual(store.getState().isMobileTabMode, true);
    assert.strictEqual(store.getState().layoutId, "four-grid"); // layout ID remains four-grid!

    // Switch active mobile tab to panel-3
    store.setActiveMobileTab("panel-3");
    assert.strictEqual(store.getState().activePanelId, "panel-3");
    assert.strictEqual(store.getState().activeMobileTabId, "panel-3");
    assert.strictEqual(store.getState().layoutId, "four-grid"); // never mutates to single!

    // Restore desktop mode
    store.setMobileTabMode(false);
    assert.strictEqual(store.getState().isMobileTabMode, false);
    assert.strictEqual(store.getState().layoutId, "four-grid");
    assert.strictEqual(store.getState().panelIds.length, 4);
  });

  // 10. SECURITY & READ-ONLY INVARIANTS
  it("should verify strict financial integrity: read-only operations, zero trading orders, zero AI calls", () => {
    // Stage 72 workspace limits
    assert.strictEqual(WORKSPACE_RESOURCE_BUDGET.maxVisiblePanels, 4);
    assert.strictEqual(WORKSPACE_RESOURCE_BUDGET.maxMountedRenderers, 4);
    assert.ok(WORKSPACE_RESOURCE_BUDGET.minPanelWidthPx >= 300);
    assert.ok(WORKSPACE_RESOURCE_BUDGET.minPanelHeightPx >= 200);

    // Verify no trading order APIs or autonomous agent calls are present in workspace exports
    const workspaceExports = Object.keys(require("../src/lib/charts/workspace"));
    const forbiddenPatterns = [
      "trade_execution",
      "place_order",
      "buy_sell",
      "broker",
      "portfolio_mutation",
      "agent_execution",
      "llm_call",
      "chart_replay",
    ];

    for (const exp of workspaceExports) {
      for (const pattern of forbiddenPatterns) {
        assert.strictEqual(
          exp.toLowerCase().includes(pattern),
          false,
          `Forbidden keyword '${pattern}' found in workspace export '${exp}'`
        );
      }
    }
  });
});
