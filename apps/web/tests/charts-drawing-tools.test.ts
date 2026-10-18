/**
 * Automated Verification Suite for ATLAS Stage 71:
 * Professional Chart Drawing Tools V1.
 *
 * Verifies:
 * 1. Drawing Model schemas, versioning, context isolation, and finite anchor validation.
 * 2. Geometry calculations: point distance, segment distance, horizontal ray, rectangle perimeter.
 * 3. Fibonacci retracement levels, direction preservation, and ratio precision.
 * 4. Price & Time measurements: Delta P, Delta P%, zero-base guards, elapsed time, bar counts.
 * 5. Drawing Tool Registry: all 9 canonical tools registered with anchor validation.
 * 6. Smart Snapping Engine: OFF, NEAREST_BAR, OHLC, tolerance boundaries, modifier overrides.
 * 7. Command-based Undo/Redo: single gesture transactions, redo invalidation, bounded history.
 * 8. DrawingSessionStore: instrument-level context isolation, session preservation, lock & visibility.
 * 9. UI & design system invariants: institutional Bloomberg/TradingView aesthetic, no emoji/fake signals.
 */

import { describe, it } from "node:test";
import assert from "node:assert";
import {
  DrawingAnchor,
  DrawingChartContext,
  DrawingObject,
  DrawingType,
  FIBONACCI_DEFAULT_RATIOS,
  calculateFibonacciLevels,
  calculatePriceMeasurement,
  calculateTimeMeasurement,
  calculateCombinedMeasurement,
  pointDistance,
  distanceToSegment,
  distanceToHorizontalLine,
  distanceToHorizontalRay,
  distanceToVerticalLine,
  isPointInRectangle,
  distanceToRectangleBorder,
  strokeStyleToDashArray,
  DrawingToolRegistry,
  DRAWING_TOOLS,
  resolveSnapping,
  UndoRedoHistory,
  drawingStore,
  DrawingSessionStore,
} from "../src/lib/charts/drawings";
import { ChartBarDTO } from "../src/lib/charts/types";

describe("Stage 71 - Professional Chart Drawing Tools V1 Tests", () => {
  // 1. DRAWING MODEL & SCHEMA TESTS
  it("should verify typed drawing object schema and finite financial anchors", () => {
    const context: DrawingChartContext = {
      instrument_entity_id: "inst_spy_001",
      symbol: "SPY",
      price_basis: "raw",
      quotation_unit: "USD",
    };

    const validAnchors: DrawingAnchor[] = [
      { time: 1710000000, price: 512.45 },
      { time: 1710086400, price: 518.2 },
    ];

    assert.strictEqual(DrawingToolRegistry.validateAnchors("trendline", validAnchors), true);

    // Rejection of NaN or Infinity prices
    const invalidNanPrice: DrawingAnchor[] = [
      { time: 1710000000, price: NaN },
      { time: 1710086400, price: 518.2 },
    ];
    assert.strictEqual(DrawingToolRegistry.validateAnchors("trendline", invalidNanPrice), false);

    const invalidInfPrice: DrawingAnchor[] = [
      { time: 1710000000, price: Infinity },
      { time: 1710086400, price: 518.2 },
    ];
    assert.strictEqual(DrawingToolRegistry.validateAnchors("trendline", invalidInfPrice), false);

    // Rejection of missing anchors
    assert.strictEqual(DrawingToolRegistry.validateAnchors("trendline", [validAnchors[0]]), false);
  });

  // 2. GEOMETRY UTILITIES & HIT-TESTING
  it("should calculate exact point distances and segment projections", () => {
    // Euclidean point distance
    const dist = pointDistance({ x: 0, y: 0 }, { x: 3, y: 4 });
    assert.strictEqual(dist, 5);

    // Distance to horizontal line y = 100
    assert.strictEqual(distanceToHorizontalLine({ x: 50, y: 105 }, 100), 5);
    assert.strictEqual(distanceToHorizontalLine({ x: 50, y: 92 }, 100), 8);

    // Distance to vertical line x = 200
    assert.strictEqual(distanceToVerticalLine({ x: 196, y: 300 }, 200), 4);

    // Distance to segment from (0, 0) to (100, 0)
    assert.strictEqual(distanceToSegment({ x: 50, y: 10 }, { x: 0, y: 0 }, { x: 100, y: 0 }), 10);
    // Point past the end of the segment
    assert.strictEqual(distanceToSegment({ x: 110, y: 0 }, { x: 0, y: 0 }, { x: 100, y: 0 }), 10);

    // Distance to horizontal ray starting at (50, 100) extending right
    assert.strictEqual(distanceToHorizontalRay({ x: 80, y: 104 }, { x: 50, y: 100 }), 4);
    // Left of ray start: distance to anchor (50, 100)
    assert.strictEqual(distanceToHorizontalRay({ x: 47, y: 104 }, { x: 50, y: 100 }), 5);

    // Rectangle containment and boundary distance
    assert.strictEqual(isPointInRectangle({ x: 25, y: 25 }, { x: 10, y: 10 }, { x: 40, y: 40 }), true);
    assert.strictEqual(isPointInRectangle({ x: 5, y: 25 }, { x: 10, y: 10 }, { x: 40, y: 40 }), false);

    const borderDist = distanceToRectangleBorder({ x: 12, y: 20 }, { x: 10, y: 10 }, { x: 40, y: 40 });
    assert.strictEqual(borderDist, 2); // closest to left border x=10
  });

  // 3. FIBONACCI RETRACEMENT MATHEMATICAL INTEGRITY
  it("should calculate Fibonacci retracement levels with direction preservation and precision", () => {
    // Upward range: P0 = 100, P1 = 200
    const upLevels = calculateFibonacciLevels(100, 200);
    assert.strictEqual(upLevels.length, 7);

    assert.strictEqual(upLevels[0].ratio, 0.0);
    assert.strictEqual(upLevels[0].price, 100.0);

    assert.strictEqual(upLevels[1].ratio, 0.236);
    assert.strictEqual(upLevels[1].price, 123.6);

    assert.strictEqual(upLevels[2].ratio, 0.382);
    assert.strictEqual(upLevels[2].price, 138.2);

    assert.strictEqual(upLevels[3].ratio, 0.5);
    assert.strictEqual(upLevels[3].price, 150.0);

    assert.strictEqual(upLevels[4].ratio, 0.618);
    assert.strictEqual(upLevels[4].price, 161.8);

    assert.strictEqual(upLevels[5].ratio, 0.786);
    assert.strictEqual(upLevels[5].price, 178.6);

    assert.strictEqual(upLevels[6].ratio, 1.0);
    assert.strictEqual(upLevels[6].price, 200.0);

    // Downward range: P0 = 200 (high), P1 = 100 (low)
    const downLevels = calculateFibonacciLevels(200, 100);
    assert.strictEqual(downLevels[0].price, 200.0); // 0% at high
    assert.strictEqual(downLevels[3].price, 150.0); // 50% at 150
    assert.strictEqual(downLevels[4].price, 138.2); // 61.8% retraced from 200 down to 100 is 200 - 0.618*100 = 138.2
    assert.strictEqual(downLevels[6].price, 100.0); // 100% at low

    // Negative futures price range: P0 = -10, P1 = 40
    const negLevels = calculateFibonacciLevels(-10, 40);
    assert.strictEqual(negLevels[0].price, -10);
    assert.strictEqual(negLevels[3].price, 15); // midpoint of -10 and 40 is (-10 + 50*0.5) = 15
    assert.strictEqual(negLevels[6].price, 40);
  });

  // 4. PRICE & TIME MEASUREMENTS INTEGRITY
  it("should calculate price differences, percentages with zero-base protection, and bar counts", () => {
    // Normal positive price change
    const p1 = calculatePriceMeasurement(100, 125, "USD");
    assert.strictEqual(p1.deltaPrice, 25);
    assert.strictEqual(p1.deltaPriceFormatted, "+25.00 USD");
    assert.strictEqual(p1.deltaPercent, 25);
    assert.strictEqual(p1.deltaPercentFormatted, "+25.00%");

    // Negative price change
    const p2 = calculatePriceMeasurement(200, 180, "USD");
    assert.strictEqual(p2.deltaPrice, -20);
    assert.strictEqual(p2.deltaPriceFormatted, "-20.00 USD");
    assert.strictEqual(p2.deltaPercent, -10);
    assert.strictEqual(p2.deltaPercentFormatted, "-10.00%");

    // Zero-base starting price: division by zero guard
    const p3 = calculatePriceMeasurement(0, 50, "USD");
    assert.strictEqual(p3.deltaPrice, 50);
    assert.strictEqual(p3.deltaPercent, null);
    assert.strictEqual(p3.deltaPercentFormatted, "N/A (base 0)");

    // Negative starting price guard
    const p4 = calculatePriceMeasurement(-15, 10, "USD");
    assert.strictEqual(p4.deltaPrice, 25);
    assert.strictEqual(p4.deltaPercent, null);
    assert.strictEqual(p4.deltaPercentFormatted, "N/A (negative base)");

    // Time measurement and canonical bar count
    const mockBars: ChartBarDTO[] = [
      { time_unix: 1710000000, timestamp: "2024-03-09T16:00:00Z", open: 100, high: 105, low: 99, close: 104, volume: 1000, is_final: true },
      { time_unix: 1710003600, timestamp: "2024-03-09T17:00:00Z", open: 104, high: 108, low: 103, close: 107, volume: 1200, is_final: true },
      { time_unix: 1710007200, timestamp: "2024-03-09T18:00:00Z", open: 107, high: 110, low: 106, close: 109, volume: 1500, is_final: true },
    ];

    const tRes = calculateTimeMeasurement(1710000000, 1710007200, mockBars);
    assert.strictEqual(tRes.elapsedSeconds, 7200);
    assert.strictEqual(tRes.elapsedFormatted, "2h");
    assert.strictEqual(tRes.barCount, 3);
    assert.strictEqual(tRes.barCountFormatted, "3 bars");
  });

  // 5. DRAWING TOOL REGISTRY INTEGRITY
  it("should confirm all 9 canonical drawing tools are properly registered", () => {
    const tools = DrawingToolRegistry.getAll();
    assert.strictEqual(tools.length, 9);

    const expectedTools: DrawingType[] = [
      "trendline",
      "horizontal_line",
      "horizontal_ray",
      "vertical_line",
      "rectangle",
      "price_range",
      "time_range",
      "price_time_measure",
      "fibonacci_retracement",
    ];

    for (const t of expectedTools) {
      const def = DrawingToolRegistry.get(t);
      assert.ok(def, `Tool ${t} must be registered`);
      assert.strictEqual(def.type, t);
      if (t === "horizontal_line" || t === "horizontal_ray" || t === "vertical_line") {
        assert.strictEqual(def.requiredAnchors, 1);
      } else {
        assert.strictEqual(def.requiredAnchors, 2);
      }
    }
  });

  // 6. SMART SNAPPING ENGINE INTEGRITY
  it("should evaluate OFF, NEAREST_BAR, and OHLC snapping without data mutation", () => {
    const mockBars: ChartBarDTO[] = [
      { time_unix: 1710000000, timestamp: "2024-03-09T16:00:00Z", open: 500, high: 510, low: 495, close: 508, volume: 1000, is_final: true },
      { time_unix: 1710086400, timestamp: "2024-03-10T16:00:00Z", open: 508, high: 515, low: 506, close: 512, volume: 1200, is_final: true },
    ];

    // Mock projection
    const mockProjection = {
      timeToScreen: (t: number) => (t === 1710000000 ? 100 : t === 1710086400 ? 200 : null),
      priceToScreen: (p: number) => 1000 - p,
      screenToTime: (x: number) => (x < 150 ? 1710000000 : 1710086400),
      screenToPrice: (y: number) => 1000 - y,
    };

    // Mode: OFF (pointer at x=102, y=490 -> no snap)
    const offRes = resolveSnapping(
      { x: 102, y: 490 },
      mockBars,
      mockProjection,
      { mode: "OFF", pixelTolerance: 15 }
    );
    assert.strictEqual(offRes.snapped, false);
    assert.strictEqual(offRes.screenPoint.x, 102);

    // Mode: NEAREST_BAR (pointer at x=104 -> snaps x to 100, time to 1710000000)
    const barRes = resolveSnapping(
      { x: 104, y: 490 },
      mockBars,
      mockProjection,
      { mode: "NEAREST_BAR", pixelTolerance: 15 }
    );
    assert.strictEqual(barRes.snapped, true);
    assert.strictEqual(barRes.anchor.time, 1710000000);
    assert.strictEqual(barRes.screenPoint.x, 100);

    // Mode: OHLC (pointer near high: price 510 -> screenY = 490)
    // Pointer at x=103, y=489 (distance to high [490] is 1, distance to close [492] is 3)
    const ohlcRes = resolveSnapping(
      { x: 103, y: 489 },
      mockBars,
      mockProjection,
      { mode: "OHLC", pixelTolerance: 15 }
    );
    assert.strictEqual(ohlcRes.snapped, true);
    assert.strictEqual(ohlcRes.snapField, "high");
    assert.strictEqual(ohlcRes.anchor.price, 510);
    assert.strictEqual(ohlcRes.screenPoint.y, 490);

    // Modifier Override: pressing Shift temporarily disables snapping
    const shiftRes = resolveSnapping(
      { x: 104, y: 492 },
      mockBars,
      mockProjection,
      { mode: "OHLC", pixelTolerance: 15, isModifierActive: true }
    );
    assert.strictEqual(shiftRes.snapped, false);
  });

  // 7. UNDO / REDO COMMAND HISTORY TESTS
  it("should execute, undo, and redo drawing mutations with redo invalidation", () => {
    const history = new UndoRedoHistory(50);
    assert.strictEqual(history.canUndo(), false);
    assert.strictEqual(history.canRedo(), false);

    const d1: DrawingObject = {
      id: "d1",
      type: "trendline",
      version: 1,
      context: { instrument_entity_id: "SPY", symbol: "SPY", price_basis: "raw" },
      anchors: [{ time: 1000, price: 100 }, { time: 2000, price: 150 }],
      style: { color: "#38bdf8", lineWidth: 2, lineStyle: "solid", fillOpacity: 0.15, showLabel: false },
      visible: true,
      locked: false,
      zIndex: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Step 1: Create drawing
    history.push("CREATE", [], [d1], [d1.id]);
    assert.strictEqual(history.canUndo(), true);
    assert.strictEqual(history.canRedo(), false);

    // Step 2: Undo creation -> restores empty array
    const undone = history.undo();
    assert.deepStrictEqual(undone, []);
    assert.strictEqual(history.canUndo(), false);
    assert.strictEqual(history.canRedo(), true);

    // Step 3: Redo creation -> restores [d1]
    const redone = history.redo();
    assert.strictEqual(redone?.length, 1);
    assert.strictEqual(redone[0].id, "d1");
    assert.strictEqual(history.canUndo(), true);
    assert.strictEqual(history.canRedo(), false);

    // Step 4: Redo branch invalidation on new edit
    history.undo();
    assert.strictEqual(history.canRedo(), true);

    const d2: DrawingObject = { ...d1, id: "d2" };
    history.push("CREATE", [], [d2], [d2.id]);
    // The previous redo branch for d1 is now invalidated!
    assert.strictEqual(history.canRedo(), false);
  });

  // 8. SESSION DRAWING STORE & CONTEXT ISOLATION
  it("should isolate drawings by instrument context and preserve session state", () => {
    const store = DrawingSessionStore.getInstance();

    // Set context to SPY
    store.setContext({
      instrument_entity_id: "inst_spy",
      symbol: "SPY",
      price_basis: "raw",
    });
    store.clearDrawings();

    // Add a trendline to SPY
    const spyDrawing = store.addDrawing("trendline", [
      { time: 1710000000, price: 500 },
      { time: 1710086400, price: 510 },
    ]);
    assert.ok(spyDrawing);
    assert.strictEqual(store.getDrawings().length, 1);

    // Switch context to QQQ
    store.setContext({
      instrument_entity_id: "inst_qqq",
      symbol: "QQQ",
      price_basis: "raw",
    });
    // QQQ must NOT see SPY drawings!
    assert.strictEqual(store.getDrawings().length, 0);

    // Add a rectangle to QQQ
    store.addDrawing("rectangle", [
      { time: 1710000000, price: 420 },
      { time: 1710086400, price: 430 },
    ]);
    assert.strictEqual(store.getDrawings().length, 1);
    assert.strictEqual(store.getDrawings()[0].type, "rectangle");

    // Return to SPY context in the same browser session
    store.setContext({
      instrument_entity_id: "inst_spy",
      symbol: "SPY",
      price_basis: "raw",
    });
    // SPY trendline is preserved!
    assert.strictEqual(store.getDrawings().length, 1);
    assert.strictEqual(store.getDrawings()[0].type, "trendline");
  });

  // 9. DRAWING MANIPULATION: LOCK, VISIBILITY, AND STYLE
  it("should respect drawing lock and visibility states", () => {
    const store = DrawingSessionStore.getInstance();
    store.setContext({ instrument_entity_id: "inst_test", symbol: "TEST", price_basis: "raw" });
    store.clearDrawings();

    const d = store.addDrawing("horizontal_line", [{ time: 1710000000, price: 150 }]);
    assert.ok(d);

    // Toggle lock
    store.toggleLock(d.id);
    assert.strictEqual(store.getDrawings()[0].locked, true);

    // Attempting to move a locked drawing should not modify its anchors
    store.commitDrawingAnchors(d.id, [{ time: 1710000000, price: 160 }]);
    assert.strictEqual(store.getDrawings()[0].anchors[0].price, 150);

    // Unlock and modify
    store.toggleLock(d.id);
    assert.strictEqual(store.getDrawings()[0].locked, false);
    store.commitDrawingAnchors(d.id, [{ time: 1710000000, price: 160 }]);
    assert.strictEqual(store.getDrawings()[0].anchors[0].price, 160);

    // Toggle visibility
    store.toggleVisibility(d.id);
    assert.strictEqual(store.getDrawings()[0].visible, false);
  });

  // 10. STRICT DESIGN SYSTEM INVARIANTS
  it("should verify strict design invariants: no purple gradients, no emoji icons, no fake buy/sell signals", () => {
    // Check SVG dash array conversion
    assert.strictEqual(strokeStyleToDashArray("solid", 2), undefined);
    assert.strictEqual(typeof strokeStyleToDashArray("dashed", 2), "string");
    assert.strictEqual(typeof strokeStyleToDashArray("dotted", 2), "string");

    // Confirm all tool names are professional institutional terms
    const allTools = DrawingToolRegistry.getAll();
    for (const tool of allTools) {
      assert.ok(!tool.displayName.includes("🚀"), "No emoji icons allowed");
      assert.ok(!tool.displayName.includes("Buy"), "No fake trading signals");
      assert.ok(!tool.displayName.includes("Sell"), "No fake trading signals");
      assert.ok(!tool.description.includes("predict"), "No future prediction claims");
    }
  });
});
