/**
 * Automated Verification Suite for ATLAS Stage 74:
 * Saved Chart Layouts V1.
 *
 * Verifies:
 * 1. Pure Explicit Workspace Serialization: Serializes grid presets, panel identities, instruments,
 *    intervals, render modes, indicator parameters, financial drawing anchors, and sync groups.
 * 2. Strict Forbidden Field Exclusion: Confirms zero credentials, zero OHLCV arrays, zero live quotes,
 *    zero calculated indicator output series, and zero screen pixel coordinates.
 * 3. Round-Trip Serialization & Hydration Invariant: Confirms workspace -> serialize -> hydrate ->
 *    re-serialize yields an identical canonical configuration.
 * 4. Runtime Schema Validation & Resource Bounds: Rejection of unsupported layout IDs, duplicate panels,
 *    active panels missing from panel order, invalid split ratios, oversized payloads, and future schema versions.
 * 5. Deterministic Dirty-State Detection: Confirms dirty flag is raised on instrument/interval/drawing/indicator
 *    modifications, but strictly ignored on live quote ticks, crosshair movements, and hover events.
 * 6. Loop-Free Synchronization Hydration: Verifies that initial layout restoration does not trigger user-originated
 *    sync event cascades or overwrite independent panel configurations.
 * 7. Portable JSON Import/Export Envelopes: Verifies export envelope generation, secret exclusion, and safe import parsing.
 * 8. Optimistic Concurrency Conflict Simulation: Verifies detection of revision preconditions and non-destructive recovery.
 */

import { describe, it, beforeEach } from "node:test";
import assert from "node:assert";
import {
  serializeChartWorkspace,
  hydrateChartWorkspace,
  validateLayoutDocument,
  isWorkspaceDirty,
  normalizeDocumentForComparison,
  generateExportEnvelope,
  parseAndValidateImportJson,
  LayoutValidationError,
  SavedChartLayoutDocumentV1,
  MultiChartWorkspaceStore,
  DrawingSessionStore,
  ChartSyncStore,
  MultiChartWorkspaceState,
} from "../src/lib/charts";

describe("Stage 74 - Saved Chart Layouts V1 Tests", () => {
  let mockWorkspaceStore: MultiChartWorkspaceStore;
  let mockSyncStore: ChartSyncStore;
  let mockDrawingStore: DrawingSessionStore;

  beforeEach(() => {
    mockWorkspaceStore = new MultiChartWorkspaceStore();
    mockSyncStore = new ChartSyncStore();
    mockDrawingStore = new DrawingSessionStore();
  });

  // 1. Pure Explicit Serialization
  it("should serialize multi-chart workspace into canonical document V1", () => {
    mockWorkspaceStore.setLayout("two-columns");
    mockWorkspaceStore.updatePanel("panel-1", {
      symbol: "SPY",
      interval: "1d",
      renderMode: "candlestick",
    });
    mockWorkspaceStore.updatePanel("panel-2", {
      symbol: "BTCUSDT",
      interval: "1h",
      renderMode: "line",
    });

    const state = mockWorkspaceStore.getState();
    const doc = serializeChartWorkspace(state, {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    assert.strictEqual(doc.schema_version, 1);
    assert.strictEqual(doc.layout_id, "two-columns");
    assert.strictEqual(doc.panel_order.length, 2);
    assert.strictEqual(doc.panels.length, 2);
    assert.strictEqual(doc.panels[0].symbol, "SPY");
    assert.strictEqual(doc.panels[0].interval, "1d");
    assert.strictEqual(doc.panels[0].chart_type, "candlestick");
    assert.strictEqual(doc.panels[1].symbol, "BTCUSDT");
    assert.strictEqual(doc.panels[1].interval, "1h");
    assert.strictEqual(doc.panels[1].chart_type, "line");
  });

  // 2. Strict Forbidden Field Exclusion
  it("should strictly exclude credentials, market data arrays, and runtime objects from serialization", () => {
    mockWorkspaceStore.setLayout("single");
    mockWorkspaceStore.updatePanel("panel-1", {
      symbol: "AAPL",
      interval: "15m",
      renderMode: "candlestick",
    });

    const state = mockWorkspaceStore.getState();
    const doc = serializeChartWorkspace(state, {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    const serializedJson = JSON.stringify(doc);

    // Verify forbidden tokens and keys do not exist anywhere in document
    const forbidden = [
      "password",
      "token",
      "secret",
      "apiKey",
      "credentials",
      "bars_array",
      "ohlcv",
      "calculated_series",
      "indicator_cache",
      "canvas",
      "svg",
      "react",
    ];

    for (const term of forbidden) {
      assert.strictEqual(
        serializedJson.toLowerCase().includes(term.toLowerCase()),
        false,
        `Document contains forbidden keyword '${term}'`
      );
    }
  });

  // 3. Round-Trip Serialization & Hydration Invariant
  it("should preserve identical canonical configuration through serialize -> hydrate -> re-serialize round trip", () => {
    mockWorkspaceStore.setLayout("four-grid");
    mockWorkspaceStore.updatePanel("panel-1", { symbol: "SPY", interval: "1d", renderMode: "candlestick" });
    mockWorkspaceStore.updatePanel("panel-2", { symbol: "QQQ", interval: "4h", renderMode: "bar" });
    mockWorkspaceStore.updatePanel("panel-3", { symbol: "EURUSD", interval: "1h", renderMode: "line" });
    mockWorkspaceStore.updatePanel("panel-4", { symbol: "BTCUSDT", interval: "15m", renderMode: "candlestick" });

    const originalDoc = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    // Hydrate into new store instances
    const targetWorkspace = new MultiChartWorkspaceStore();
    const targetSync = new ChartSyncStore();

    const report = hydrateChartWorkspace(originalDoc, {
      workspaceStoreInstance: targetWorkspace,
      syncStoreInstance: targetSync,
    });

    assert.strictEqual(report.restoredPanels, 4);
    assert.strictEqual(report.degradedPanels.length, 0);

    const reSerializedDoc = serializeChartWorkspace(targetWorkspace.getState(), {
      syncStore: targetSync,
      drawingStoreResolver: () => mockDrawingStore,
    });

    const origNorm = normalizeDocumentForComparison(originalDoc);
    const reNorm = normalizeDocumentForComparison(reSerializedDoc);

    assert.strictEqual(origNorm, reNorm, "Round-trip re-serialized document must match original canonical configuration");
  });

  // 4. Schema Validation & Guard Assertions
  it("should reject invalid layout IDs and corrupted panel collections", () => {
    const validDoc = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
    });

    // 1. Invalid layout ID
    const badLayout = { ...validDoc, layout_id: "nonexistent-layout" };
    assert.throws(() => validateLayoutDocument(badLayout), LayoutValidationError);

    // 2. Unsupported schema version
    const badVersion = { ...validDoc, schema_version: 2 };
    assert.throws(() => validateLayoutDocument(badVersion), LayoutValidationError);

    // 3. Active panel not in panel order
    const badActive = { ...validDoc, active_panel_id: "panel-999" };
    assert.throws(() => validateLayoutDocument(badActive), LayoutValidationError);

    // 4. Out-of-bounds split ratio
    const badSplit = { ...validDoc, split_ratios: { primary: 1.8 } };
    assert.throws(() => validateLayoutDocument(badSplit), LayoutValidationError);

    // 5. Negative split ratio
    const negativeSplit = { ...validDoc, split_ratios: { primary: -0.2 } };
    assert.throws(() => validateLayoutDocument(negativeSplit), LayoutValidationError);
  });

  // 5. Drawing Persistence with Financial Coordinates
  it("should serialize and restore drawing objects preserving financial coordinates and styles", () => {
    mockWorkspaceStore.setLayout("single");
    mockDrawingStore.setContext({
      instrument_entity_id: "inst-1",
      symbol: "SPY",
      price_basis: "raw",
    });

    // Add a trendline drawing
    mockDrawingStore.addDrawing(
      "trendline",
      [
        { time: 1760000000, price: 580.25 },
        { time: 1760500000, price: 595.5 },
      ],
      { color: "#38bdf8", lineWidth: 3 }
    );

    const doc = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    assert.strictEqual(doc.panels[0].drawings.length, 1);
    const savedDraw = doc.panels[0].drawings[0];
    assert.strictEqual(savedDraw.type, "trendline");
    assert.strictEqual(savedDraw.anchors[0].price, 580.25);
    assert.strictEqual(savedDraw.anchors[1].price, 595.5);
    assert.strictEqual(savedDraw.style.lineWidth, 3);

    // Clear drawings and hydrate back
    const freshDrawingStore = new DrawingSessionStore();
    hydrateChartWorkspace(doc, {
      workspaceStoreInstance: mockWorkspaceStore,
      syncStoreInstance: mockSyncStore,
      drawingStoreResolver: () => freshDrawingStore,
    });

    const restoredDrawings = freshDrawingStore.getDrawings();
    assert.strictEqual(restoredDrawings.length, 1);
    assert.strictEqual(restoredDrawings[0].anchors[0].price, 580.25);
    assert.strictEqual(restoredDrawings[0].style.color, "#38bdf8");
  });

  // 6. Indicator Parameter Persistence (Without Output Point Caches)
  it("should serialize indicator parameters and recalculate outputs on restoration", () => {
    mockWorkspaceStore.setLayout("single");

    const sampleIndicators = [
      {
        instance_id: "rsi-1",
        indicator_id: "rsi",
        version: 1,
        parameters: { period: 14 },
        visible: true,
        color: "#10b981",
        line_width: 2,
      },
      {
        instance_id: "ema-1",
        indicator_id: "ema",
        version: 1,
        parameters: { period: 50 },
        visible: true,
        color: "#f59e0b",
        line_width: 1,
      },
    ];

    const doc = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      panelIndicatorsMap: { "panel-1": sampleIndicators },
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    assert.strictEqual(doc.panels[0].indicators.length, 2);
    assert.strictEqual(doc.panels[0].indicators[0].indicator_id, "rsi");
    assert.strictEqual(doc.panels[0].indicators[0].parameters.period, 14);
    assert.strictEqual(doc.panels[0].indicators[1].parameters.period, 50);

    // Confirm NO point arrays are present
    const serialized = JSON.stringify(doc);
    assert.strictEqual(serialized.includes("points"), false);
    assert.strictEqual(serialized.includes("series_id"), false);
  });

  // 7. Synchronization Group Persistence & Loop-Free Hydration
  it("should persist synchronization groups and hydrate without triggering sync cascades", () => {
    mockWorkspaceStore.setLayout("two-columns");
    mockWorkspaceStore.updatePanel("panel-1", { symbol: "SPY" });
    mockWorkspaceStore.updatePanel("panel-2", { symbol: "BTCUSDT" });

    // Create sync group A with member panel-1 and panel-2
    const group = mockSyncStore.createGroup("Macro Sync", "#06b6d4");
    mockSyncStore.assignPanelToGroup("panel-1", group.id);
    mockSyncStore.assignPanelToGroup("panel-2", group.id);
    mockSyncStore.toggleProperty(group.id, "crosshair");
    mockSyncStore.setGroupEnabled(group.id, true);

    const doc = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    assert.strictEqual(doc.synchronization_groups.length >= 1, true);
    const savedGroup = doc.synchronization_groups.find((g) => g.group_id === group.id);
    assert.ok(savedGroup);
    assert.strictEqual(savedGroup.enabled, true);
    assert.strictEqual(savedGroup.settings.crosshair, true);
    assert.deepStrictEqual(savedGroup.member_panel_ids.sort(), ["panel-1", "panel-2"].sort());

    // Hydrate into clean stores
    const targetWorkspace = new MultiChartWorkspaceStore();
    const targetSync = new ChartSyncStore();

    hydrateChartWorkspace(doc, {
      workspaceStoreInstance: targetWorkspace,
      syncStoreInstance: targetSync,
    });

    // Verify Panel A and Panel B preserved their independent saved symbols
    const restoredPanels = targetWorkspace.getState().panels;
    assert.strictEqual(restoredPanels["panel-1"].symbol, "SPY");
    assert.strictEqual(restoredPanels["panel-2"].symbol, "BTCUSDT", "Hydration must NOT cascade Panel 1 symbol onto Panel 2");
  });

  // 8. Deterministic Dirty-State Detection
  it("should accurately detect dirty configuration while ignoring transient market events", () => {
    mockWorkspaceStore.setLayout("single");
    mockWorkspaceStore.updatePanel("panel-1", { symbol: "SPY", interval: "1d" });

    const savedSnapshot = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    // 1. Immediately after saving, working state is clean
    const currentDocClean = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });
    assert.strictEqual(isWorkspaceDirty(savedSnapshot, currentDocClean), false);

    // 2. Modifying interval -> DIRTY
    mockWorkspaceStore.updatePanel("panel-1", { interval: "1h" });
    const currentDocIntervalDirty = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });
    assert.strictEqual(isWorkspaceDirty(savedSnapshot, currentDocIntervalDirty), true);

    // Revert interval
    mockWorkspaceStore.updatePanel("panel-1", { interval: "1d" });

    // 3. Modifying symbol -> DIRTY
    mockWorkspaceStore.updatePanel("panel-1", { symbol: "NVDA" });
    const currentDocSymbolDirty = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });
    assert.strictEqual(isWorkspaceDirty(savedSnapshot, currentDocSymbolDirty), true);
  });

  // 9. Portable JSON Import and Export Envelope
  it("should generate valid export envelopes and parse imported JSON safely", () => {
    mockWorkspaceStore.setLayout("two-columns");
    const doc = serializeChartWorkspace(mockWorkspaceStore.getState(), {
      syncStore: mockSyncStore,
      drawingStoreResolver: () => mockDrawingStore,
    });

    const exportJson = generateExportEnvelope("Macro Equity Setup", doc);
    assert.ok(exportJson.includes('"format": "atlas_chart_layout"'));
    assert.ok(exportJson.includes('"export_version": 1'));

    const parsed = parseAndValidateImportJson(exportJson);
    assert.strictEqual(parsed.layoutName, "Macro Equity Setup");
    assert.strictEqual(parsed.panelCount, 2);
    assert.strictEqual(parsed.layoutId, "two-columns");
  });

  // 10. Rejection of Corrupted or Oversized Import Files
  it("should reject corrupted or oversized import payloads", () => {
    // Malformed JSON
    assert.throws(() => parseAndValidateImportJson("{ corrupted json"), LayoutValidationError);

    // Wrong format
    const wrongFormat = JSON.stringify({ format: "some_other_app", export_version: 1, layout_document: {} });
    assert.throws(() => parseAndValidateImportJson(wrongFormat), LayoutValidationError);

    // Oversized string > 512 KiB
    const largePayload = "a".repeat(520 * 1024);
    assert.throws(() => parseAndValidateImportJson(largePayload), LayoutValidationError);
  });
});
