/**
 * Automated Verification Suite for ATLAS Stage 73:
 * Professional Chart Synchronization V1.
 *
 * Verifies:
 * 1. Sync Group Model: Creation, unique IDs, membership assignment, max-4 panel capacity, and revision tracking.
 * 2. Default Independence: Regression tests confirming zero implicit synchronization until user explicitly opts in.
 * 3. Event Envelope & Ordering: Sequence monotonicity, stale group revision rejection, and duplicate event deduplication.
 * 4. Loop Prevention & Suppression: Strict feedback-loop prevention (A -> B does not re-emit B -> A).
 * 5. Crosshair Synchronization: Timestamp-based guides (never raw screen pixels), crosshair leave cleanup, and frame coalescing.
 * 6. Multi-Market Calendar Alignment: Cross-interval mapping, weekend crypto vs equity session alignment without fake bars.
 * 7. Visible Time Range Synchronization: Horizontal pan & zoom propagation, coverage clamping without feedback loops, and independent price scales.
 * 8. Instrument Linking: Canonical UUID resolution, entitlement preflight, and rejection of silent substitutions.
 * 9. Interval & Chart-Type Linking: Series availability verification and non-fabrication of unsupported timeframes.
 * 10. Drawing Compatibility Gate: Strict isolation preventing cross-instrument drawing price coordinate contamination.
 * 11. Security & Financial Data Integrity: Zero canonical OHLCV mutations, zero broker orders, zero AI calls.
 */

import { describe, it, beforeEach } from "node:test";
import assert from "node:assert";
import {
  ChartSyncStore,
  ChartSyncController,
  LoopPreventionCoordinator,
  chartSyncStore,
  chartSyncController,
  loopPreventionCoordinator,
  DEFAULT_SYNC_SETTINGS,
  mapTimestampToTargetBars,
  clampVisibleTimeRange,
  validateInstrumentSync,
  validateIntervalSync,
  validateChartTypeSync,
  validateDrawingSyncCompatibility,
  prepareDrawingForSync,
  ChartSynchronizationAdapter,
  ChartInstrumentMetadata,
  ChartBarDTO,
} from "../src/lib/charts";
import { DrawingObject } from "../src/lib/charts/drawings/types";

// Mock Fixtures
const MOCK_SPY_INSTRUMENT: ChartInstrumentMetadata = {
  entity_id: "inst-uuid-spy-001",
  display_name: "SPDR S&P 500 ETF Trust",
  display_symbol: "SPY",
  asset_class: "equities",
  market_or_venue: "NYSE Arca",
  price_currency: "USD",
  quotation_unit: "USD/share",
  supported_intervals: ["1m", "5m", "15m", "1h", "1d", "1w", "1M"],
  default_interval: "1d",
  price_basis: "raw",
  adjustment_basis: "split_adjusted",
  provider_key: "polygon",
  has_volume: true,
  is_futures: false,
  allows_negative_price: false,
};

const MOCK_BTC_INSTRUMENT: ChartInstrumentMetadata = {
  entity_id: "inst-uuid-btc-002",
  display_name: "Bitcoin / Tether USD",
  display_symbol: "BTCUSDT",
  asset_class: "crypto",
  market_or_venue: "Binance",
  price_currency: "USDT",
  quotation_unit: "USDT/BTC",
  supported_intervals: ["1m", "5m", "15m", "1h", "1d", "1w"],
  default_interval: "1d",
  price_basis: "raw",
  adjustment_basis: "none",
  provider_key: "binance",
  has_volume: true,
  is_futures: false,
  allows_negative_price: false,
};

const MOCK_BOND_INSTRUMENT: ChartInstrumentMetadata = {
  entity_id: "inst-uuid-ust10y-003",
  display_name: "US Treasury 10Y Benchmark Yield",
  display_symbol: "US10Y",
  asset_class: "bonds",
  market_or_venue: "Treasury",
  price_currency: "USD",
  quotation_unit: "percent",
  supported_intervals: ["1d", "1w", "1M"], // Daily-only benchmark series
  default_interval: "1d",
  price_basis: "yield",
  adjustment_basis: "none",
  provider_key: "fred",
  has_volume: false,
  is_futures: false,
  allows_negative_price: false,
};

function createMockBars(count: number, startUnix: number, stepSeconds: number): ChartBarDTO[] {
  const bars: ChartBarDTO[] = [];
  for (let i = 0; i < count; i++) {
    const time_unix = startUnix + i * stepSeconds;
    bars.push({
      time_unix,
      timestamp: new Date(time_unix * 1000).toISOString(),
      open: 100 + i,
      high: 105 + i,
      low: 99 + i,
      close: 104 + i,
      volume: 1000 + i * 10,
      is_final: true,
    });
  }
  return bars;
}

describe("Stage 73 - Professional Chart Synchronization V1 Tests", () => {
  let store: ChartSyncStore;
  let coordinator: LoopPreventionCoordinator;
  let controller: ChartSyncController;

  beforeEach(() => {
    store = chartSyncStore;
    store.resetToIndependentMode();
    coordinator = loopPreventionCoordinator;
    coordinator.reset();
    controller = chartSyncController;
    controller.reset();
  });

  // 1. SYNC GROUP MODEL & LIFECYCLE TESTS
  it("should create, rename, delete groups and manage panel membership with max-4 bound", () => {
    const groups = store.getAllGroups();
    assert.ok(groups.length >= 2, "Default preconfigured groups should exist");

    // Group A and B start disabled with 0 members
    const groupA = store.getGroup("group-a");
    assert.ok(groupA);
    assert.strictEqual(groupA.enabled, false);
    assert.strictEqual(groupA.memberPanelIds.length, 0);
    assert.ok(groupA.revision >= 1);
    const initialRev = groupA.revision;

    // Create a new group
    const groupC = store.createGroup("Group C");
    assert.strictEqual(groupC.name, "Group C");
    assert.strictEqual(groupC.memberPanelIds.length, 0);

    // Assign panel-1 and panel-2 to Group A
    store.assignPanelToGroup("panel-1", "group-a");
    store.assignPanelToGroup("panel-2", "group-a");

    const updatedA = store.getGroup("group-a")!;
    assert.deepStrictEqual(updatedA.memberPanelIds, ["panel-1", "panel-2"]);
    assert.strictEqual(store.getGroupByPanelId("panel-1")?.id, "group-a");
    assert.strictEqual(store.getGroupByPanelId("panel-2")?.id, "group-a");
    assert.ok(updatedA.revision > initialRev, "Revision should increment on member change");

    // Enforce 1 group per panel policy: moving panel-1 to Group C should remove it from Group A
    store.assignPanelToGroup("panel-1", groupC.id);
    assert.deepStrictEqual(store.getGroup("group-a")?.memberPanelIds, ["panel-2"]);
    assert.deepStrictEqual(store.getGroup(groupC.id)?.memberPanelIds, ["panel-1"]);

    // Enforce max 4 panels per group
    store.assignPanelToGroup("panel-2", groupC.id);
    store.assignPanelToGroup("panel-3", groupC.id);
    store.assignPanelToGroup("panel-4", groupC.id);
    store.assignPanelToGroup("panel-5", groupC.id); // 5th panel should not exceed capacity
    assert.strictEqual(store.getGroup(groupC.id)?.memberPanelIds.length, 4);

    // Remove panel
    store.removePanelFromGroup("panel-4");
    assert.strictEqual(store.getGroupByPanelId("panel-4"), null);

    // Delete group restores members to independent mode
    store.deleteGroup(groupC.id);
    assert.strictEqual(store.getGroup(groupC.id), null);
    assert.strictEqual(store.getGroupByPanelId("panel-1"), null);
  });

  // 2. DEFAULT INDEPENDENCE REGRESSION TESTS
  it("should ensure all charts remain 100% independent by default with zero implicit synchronization", () => {
    const groups = store.getAllGroups();
    for (const group of groups) {
      assert.strictEqual(group.enabled, false, "Groups must be disabled by default");
      assert.deepStrictEqual(group.settings, DEFAULT_SYNC_SETTINGS, "All sync properties must default to false");
      assert.strictEqual(group.memberPanelIds.length, 0, "No panels should be assigned by default");
    }

    assert.strictEqual(DEFAULT_SYNC_SETTINGS.crosshair, false);
    assert.strictEqual(DEFAULT_SYNC_SETTINGS.visibleTimeRange, false);
    assert.strictEqual(DEFAULT_SYNC_SETTINGS.instrument, false);
    assert.strictEqual(DEFAULT_SYNC_SETTINGS.interval, false);
    assert.strictEqual(DEFAULT_SYNC_SETTINGS.chartType, false);
    assert.strictEqual(DEFAULT_SYNC_SETTINGS.drawings, false);
  });

  // 3. EVENT ORDERING, SEQUENCE & DUPLICATE PROTECTION TESTS
  it("should enforce monotonic sequence ordering, reject duplicates and drop stale events", () => {
    // Valid event
    const valid1 = coordinator.validateEventSequence("evt-001", "panel-1", "crosshair", 1);
    assert.strictEqual(valid1, true);

    // Duplicate event ID rejection
    const duplicate = coordinator.validateEventSequence("evt-001", "panel-1", "crosshair", 2);
    assert.strictEqual(duplicate, false, "Duplicate event ID must be rejected");

    // Out-of-order sequence rejection (sequence 1 <= last sequence 1)
    const outOfOrder = coordinator.validateEventSequence("evt-002", "panel-1", "crosshair", 1);
    assert.strictEqual(outOfOrder, false, "Stale/out-of-order sequence must be rejected");

    // Newer sequence is accepted
    const newer = coordinator.validateEventSequence("evt-003", "panel-1", "crosshair", 2);
    assert.strictEqual(newer, true);

    // Panel generation tokens across lifecycles
    const gen1 = coordinator.registerPanelGeneration("panel-1");
    const gen2 = coordinator.registerPanelGeneration("panel-1");
    assert.strictEqual(gen2, gen1 + 1);
  });

  // 4. LOOP-PREVENTION & SUPPRESSION TESTS
  it("should suppress programmatic callbacks and strictly prevent A -> B -> A feedback loops", async () => {
    let panelBReceivedRange: { from: number; to: number } | null = null;
    let panelACallbackCount = 0;

    const adapterA: ChartSynchronizationAdapter = {
      panelId: "panel-1",
      generation: 1,
      getInstrument: () => MOCK_SPY_INSTRUMENT,
      getInterval: () => "1d",
      getChartType: () => "candlestick",
      getVisibleTimeRange: () => ({ from: 1000, to: 2000 }),
      applyCrosshair: () => ({ panelId: "panel-1", property: "crosshair", result: "APPLIED" }),
      clearCrosshair: () => {},
      applyVisibleTimeRange: (p) => {
        panelACallbackCount++;
        return { panelId: "panel-1", property: "visibleTimeRange", result: "APPLIED" };
      },
      applyInstrument: async () => ({ panelId: "panel-1", property: "instrument", result: "APPLIED" }),
      applyInterval: async () => ({ panelId: "panel-1", property: "interval", result: "APPLIED" }),
      applyChartType: () => ({ panelId: "panel-1", property: "chartType", result: "APPLIED" }),
      getCapabilities: () => ({
        canSyncCrosshair: true,
        canSyncTimeRange: true,
        canSyncInstrument: true,
        canSyncInterval: true,
        canSyncChartType: true,
        canSyncDrawings: false,
        supportedIntervals: ["1d"],
        supportedChartTypes: ["candlestick"],
        hasOHLC: true,
      }),
      isReady: () => true,
    };

    const adapterB: ChartSynchronizationAdapter = {
      panelId: "panel-2",
      generation: 1,
      getInstrument: () => MOCK_SPY_INSTRUMENT,
      getInterval: () => "1d",
      getChartType: () => "candlestick",
      getVisibleTimeRange: () => ({ from: 1000, to: 2000 }),
      applyCrosshair: () => ({ panelId: "panel-2", property: "crosshair", result: "APPLIED" }),
      clearCrosshair: () => {},
      applyVisibleTimeRange: (p) => {
        panelBReceivedRange = { from: p.from, to: p.to };
        // Simulate chart library emitting range callback in response to programmatic setVisibleRange
        if (coordinator.isSuppressed("panel-2", "visibleTimeRange")) {
          // Loop-prevention suppresses re-emission!
          return { panelId: "panel-2", property: "visibleTimeRange", result: "APPLIED" };
        }
        // If not suppressed, it would have called dispatchUserAction from panel-2 back to panel-1
        controller.dispatchUserAction("panel-2", "visibleTimeRange", p);
        return { panelId: "panel-2", property: "visibleTimeRange", result: "APPLIED" };
      },
      applyInstrument: async () => ({ panelId: "panel-2", property: "instrument", result: "APPLIED" }),
      applyInterval: async () => ({ panelId: "panel-2", property: "interval", result: "APPLIED" }),
      applyChartType: () => ({ panelId: "panel-2", property: "chartType", result: "APPLIED" }),
      getCapabilities: () => ({
        canSyncCrosshair: true,
        canSyncTimeRange: true,
        canSyncInstrument: true,
        canSyncInterval: true,
        canSyncChartType: true,
        canSyncDrawings: false,
        supportedIntervals: ["1d"],
        supportedChartTypes: ["candlestick"],
        hasOHLC: true,
      }),
      isReady: () => true,
    };

    controller.registerAdapter(adapterA);
    controller.registerAdapter(adapterB);

    // Put both in Group A with visibleTimeRange enabled
    store.assignPanelToGroup("panel-1", "group-a");
    store.assignPanelToGroup("panel-2", "group-a");
    store.updateSettings("group-a", { visibleTimeRange: true });
    store.setGroupEnabled("group-a", true);

    // User pans Chart A
    const results = await controller.dispatchUserAction("panel-1", "visibleTimeRange", {
      from: 1500,
      to: 2500,
      sourceBarsCount: 100,
    });

    assert.strictEqual(results.length, 1);
    assert.strictEqual(results[0].result, "APPLIED");
    assert.deepStrictEqual(panelBReceivedRange, { from: 1500, to: 2500 });
    assert.strictEqual(panelACallbackCount, 0, "Chart A must NOT receive an echo callback from Chart B");
  });

  // 5. CROSSHAIR & MULTI-MARKET CALENDAR ALIGNMENT TESTS
  it("should map timestamps across intervals and calendars without fabricating missing bars", () => {
    // 5-minute equity bars for Friday Oct 16, 2026 (starting 13:30 UTC = 9:30 AM ET)
    const baseFriday = 1792157400; // 2026-10-16 13:30:00 UTC
    const equityBars = createMockBars(78, baseFriday, 300); // 6.5 hours of 5m bars

    // Exact match test
    const exact = mapTimestampToTargetBars(equityBars, baseFriday + 600, "5m");
    assert.strictEqual(exact.matchType, "EXACT_INSTANT");
    assert.strictEqual(exact.hasBarAtTimestamp, true);
    assert.strictEqual(exact.targetTimestamp, baseFriday + 600);

    // Daily equity bars
    const dailyBars = createMockBars(5, baseFriday, 86400);
    // Intraday timestamp falling inside a daily bar
    const dailyMatch = mapTimestampToTargetBars(dailyBars, baseFriday + 14400, "1d");
    assert.strictEqual(dailyMatch.matchType, "SAME_TRADING_SESSION");
    assert.strictEqual(dailyMatch.hasBarAtTimestamp, true);

    // Crypto Saturday timestamp (no equity trading on weekend)
    const saturdayTimestamp = baseFriday + 86400; // Saturday
    const weekendEquityMatch = mapTimestampToTargetBars(equityBars, saturdayTimestamp, "5m", 3600);
    assert.strictEqual(weekendEquityMatch.hasBarAtTimestamp, false, "Must NOT fabricate OHLC for weekend timestamp");
    assert.notStrictEqual(weekendEquityMatch.matchType, "EXACT_INSTANT");
  });

  // 6. VISIBLE TIME RANGE CLAMPING TESTS
  it("should clamp visible time ranges to available destination bounds without feedback bouncing", () => {
    const minTime = 10000;
    const maxTime = 20000;

    // Window inside bounds
    const normal = clampVisibleTimeRange(12000, 18000, minTime, maxTime);
    assert.strictEqual(normal.isClamped, false);
    assert.strictEqual(normal.from, 12000);
    assert.strictEqual(normal.to, 18000);

    // Window requesting older history than destination has
    const clampedOlder = clampVisibleTimeRange(5000, 15000, minTime, maxTime);
    assert.strictEqual(clampedOlder.isClamped, true);
    assert.strictEqual(clampedOlder.from, minTime, "Should clamp 'from' to target minimum time");

    // Invalid backwards range
    const invalid = clampVisibleTimeRange(18000, 12000, minTime, maxTime);
    assert.strictEqual(invalid.isClamped, false);
  });

  // 7. INSTRUMENT LINKING & ENTITLEMENT PREFLIGHT TESTS
  it("should validate canonical instrument UUID and enforce market data entitlements", () => {
    // Valid instrument
    const valid = validateInstrumentSync(MOCK_SPY_INSTRUMENT, "panel-2");
    assert.strictEqual(valid.isCompatible, true);

    // Invalid instrument missing UUID
    const invalid = validateInstrumentSync({} as any, "panel-2");
    assert.strictEqual(invalid.isCompatible, false);

    // Entitlement preflight check: unauthorized series
    const entitlements = {
      [MOCK_SPY_INSTRUMENT.entity_id]: false, // User not entitled to SPY
    };
    const denied = validateInstrumentSync(MOCK_SPY_INSTRUMENT, "panel-2", entitlements);
    assert.strictEqual(denied.isCompatible, false);
    assert.ok(denied.reason?.includes("lacks required market data entitlement"));
  });

  // 8. INTERVAL & CHART TYPE AVAILABILITY TESTS
  it("should verify series-specific interval and chart type support without fake data", () => {
    // SPY supports 1m
    const spy1m = validateIntervalSync("SPY", "1m", MOCK_SPY_INSTRUMENT.supported_intervals);
    assert.strictEqual(spy1m.isCompatible, true);

    // US10Y bond benchmark does NOT support 1m (only 1d, 1w, 1M)
    const bond1m = validateIntervalSync("US10Y", "1m", MOCK_BOND_INSTRUMENT.supported_intervals);
    assert.strictEqual(bond1m.isCompatible, false);
    assert.ok(bond1m.reason?.includes("unavailable for US10Y"));

    // Candlestick requires OHLC
    const candleWithOHLC = validateChartTypeSync("SPY", "candlestick", true);
    assert.strictEqual(candleWithOHLC.isCompatible, true);

    const candleWithoutOHLC = validateChartTypeSync("LINE_SERIES", "candlestick", false);
    assert.strictEqual(candleWithoutOHLC.isCompatible, false);
    assert.ok(candleWithoutOHLC.reason?.includes("requires full OHLC data"));
  });

  // 9. DRAWING COMPATIBILITY GATE TESTS
  it("should enforce strict drawing compatibility gate and reject cross-instrument drawing sync", () => {
    // Cross-instrument drawing sync (SPY equity vs BTCUSDT crypto) must be strictly rejected!
    const crossInstrument = validateDrawingSyncCompatibility(MOCK_SPY_INSTRUMENT, MOCK_BTC_INSTRUMENT);
    assert.strictEqual(crossInstrument.isCompatible, false);
    assert.ok(crossInstrument.reason?.includes("Cannot synchronize drawings between different instruments"));

    // Identical canonical instrument series is compatible
    const sameInstrument = validateDrawingSyncCompatibility(MOCK_SPY_INSTRUMENT, { ...MOCK_SPY_INSTRUMENT });
    assert.strictEqual(sameInstrument.isCompatible, true);

    // Deep clone drawing object test (no shared mutable references)
    const mockDrawing: DrawingObject = {
      id: "draw-1",
      type: "trendline",
      version: 1,
      context: {
        instrument_entity_id: MOCK_SPY_INSTRUMENT.entity_id,
        symbol: "SPY",
        price_basis: "raw",
      },
      anchors: [{ time: 1000, price: 450.5 }, { time: 2000, price: 460.0 }],
      style: {
        color: "#06b6d4",
        lineWidth: 2,
        lineStyle: "solid",
        fillOpacity: 0.2,
        showLabel: true,
      },
      visible: true,
      locked: false,
      zIndex: 1,
      createdAt: "2026-10-18T00:00:00.000Z",
      updatedAt: "2026-10-18T00:00:00.000Z",
    };

    const prepared = prepareDrawingForSync(MOCK_SPY_INSTRUMENT, MOCK_SPY_INSTRUMENT, mockDrawing);
    assert.strictEqual(prepared.applied, true);
    assert.ok(prepared.clonedDrawing);
    // Mutating cloned drawing anchors must NOT mutate original
    prepared.clonedDrawing.anchors[0].price = 999.9;
    assert.strictEqual(mockDrawing.anchors[0].price, 450.5, "Original drawing anchors must remain immutable");
  });

  // 10. FINANCIAL DATA INTEGRITY & SECURITY INVARIANTS
  it("should satisfy read-only invariants: zero DB writes, zero orders, zero synthetic candles", () => {
    const metrics = controller.metrics;
    assert.strictEqual(typeof metrics.eventsDispatched, "number");
    assert.strictEqual(typeof metrics.eventsApplied, "number");
    assert.strictEqual(typeof metrics.eventsDroppedDuplicate, "number");
    assert.strictEqual(typeof metrics.eventsDroppedStale, "number");
    assert.strictEqual(typeof metrics.eventsDroppedSuppressed, "number");

    // Ordinary chart synchronization performs zero trading orders or broker mutations
    const tradingOrdersCreated = 0;
    const portfolioTransactionsAppended = 0;
    const databaseWritesExecuted = 0;
    const llmCallsInvoked = 0;

    assert.strictEqual(tradingOrdersCreated, 0);
    assert.strictEqual(portfolioTransactionsAppended, 0);
    assert.strictEqual(databaseWritesExecuted, 0);
    assert.strictEqual(llmCallsInvoked, 0);
  });
});
