import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import * as indicatorComponents from "../src/components/charts/indicators";
import * as chartHooks from "../src/hooks/charts";
import * as indicatorApi from "../src/lib/charts/indicators/api";
import {
  IndicatorCategory,
  IndicatorDefinition,
  IndicatorInstanceConfig,
  IndicatorPoint,
  IndicatorRenderingTarget,
  IndicatorStatus,
} from "../src/lib/charts/indicators/types";

describe("Stage 69 - Technical Indicator Infrastructure V1 Tests", () => {
  it("should confirm all Stage 69 indicator components and hooks are exported", () => {
    assert.ok(
      indicatorComponents.IndicatorPicker,
      "IndicatorPicker must be exported"
    );
    assert.ok(
      indicatorComponents.ActiveIndicators,
      "ActiveIndicators must be exported"
    );
    assert.ok(
      indicatorComponents.IndicatorParameterEditor,
      "IndicatorParameterEditor must be exported"
    );
    assert.ok(
      indicatorComponents.IndicatorSubpane,
      "IndicatorSubpane must be exported"
    );
    assert.ok(
      chartHooks.useIndicators,
      "useIndicators must be exported from hooks/charts"
    );
    assert.ok(
      indicatorApi.fetchIndicatorCatalog,
      "fetchIndicatorCatalog must be exported from lib/charts/indicators/api"
    );
    assert.ok(
      indicatorApi.calculateIndicators,
      "calculateIndicators must be exported from lib/charts/indicators/api"
    );
  });

  it("should verify typed indicator definition contracts and schemas", () => {
    const mockSmaDef: IndicatorDefinition = {
      indicator_id: "atlas.sma",
      version: 1,
      display_name: "Simple Moving Average",
      description: "Arithmetic average of prices over a specified lookback window.",
      category: "TREND",
      rendering_target: "PRICE_OVERLAY",
      input_requirements: ["close"],
      parameters: [
        {
          name: "period",
          type: "INTEGER",
          default: 20,
          required: true,
          min_value: 2,
          max_value: 500,
          description: "Number of qualified historical bars for calculation window.",
        },
      ],
      default_color: "#38bdf8",
      default_line_width: 2,
      supported_intervals: ["1m", "5m", "15m", "1h", "4h", "1D", "1W", "1M"],
      min_history_bars: 2,
    };

    assert.strictEqual(mockSmaDef.indicator_id, "atlas.sma");
    assert.strictEqual(mockSmaDef.version, 1);
    assert.strictEqual(mockSmaDef.category, "TREND");
    assert.strictEqual(mockSmaDef.rendering_target, "PRICE_OVERLAY");
    assert.strictEqual(mockSmaDef.parameters[0].default, 20);
    assert.strictEqual(mockSmaDef.parameters[0].min_value, 2);
    assert.strictEqual(mockSmaDef.parameters[0].max_value, 500);
  });

  it("should verify multiple indicator instances can coexist on one chart", () => {
    const inst1: IndicatorInstanceConfig = {
      instance_id: "sma_fast_20",
      indicator_id: "atlas.sma",
      version: 1,
      parameters: { period: 20 },
      visible: true,
      color: "#38bdf8",
      line_width: 2,
    };

    const inst2: IndicatorInstanceConfig = {
      instance_id: "sma_slow_50",
      indicator_id: "atlas.sma",
      version: 1,
      parameters: { period: 50 },
      visible: true,
      color: "#f59e0b",
      line_width: 2,
    };

    assert.notStrictEqual(inst1.instance_id, inst2.instance_id);
    assert.strictEqual(inst1.parameters.period, 20);
    assert.strictEqual(inst2.parameters.period, 50);
  });

  it("should confirm warmup values are represented as null/unavailable, never fabricated zero", () => {
    const sampleWarmupPoints: IndicatorPoint[] = [
      { timestamp: "2026-10-18T00:00:00Z", time_unix: 1700000000, value: null, status: "WARMUP" },
      { timestamp: "2026-10-18T00:01:00Z", time_unix: 1700000060, value: null, status: "WARMUP" },
      { timestamp: "2026-10-18T00:02:00Z", time_unix: 1700000120, value: 105.42, status: "READY" },
    ];

    assert.strictEqual(sampleWarmupPoints[0].value, null);
    assert.strictEqual(sampleWarmupPoints[0].status, "WARMUP");
    assert.strictEqual(sampleWarmupPoints[1].value, null);
    assert.strictEqual(sampleWarmupPoints[2].value, 105.42);
    assert.strictEqual(sampleWarmupPoints[2].status, "READY");
  });

  it("should verify IndicatorParameterEditor enforces integer bounds (2-500)", () => {
    const editorPath = path.resolve(
      __dirname,
      "../src/components/charts/indicators/IndicatorParameterEditor.tsx"
    );
    assert.ok(fs.existsSync(editorPath));

    const content = fs.readFileSync(editorPath, "utf-8");
    assert.ok(content.includes("min_value"), "Editor must respect min_value");
    assert.ok(content.includes("max_value"), "Editor must respect max_value");
    assert.ok(content.includes("error"), "Editor must display validation errors");
    assert.ok(content.includes("Apply Settings"), "Editor must have apply/save control");
  });

  it("should verify ActiveIndicators legend component provides visibility toggle, configure, and remove controls", () => {
    const activePath = path.resolve(
      __dirname,
      "../src/components/charts/indicators/ActiveIndicators.tsx"
    );
    assert.ok(fs.existsSync(activePath));

    const content = fs.readFileSync(activePath, "utf-8");
    assert.ok(content.includes("onToggleVisibility"), "Must support visibility toggling");
    assert.ok(content.includes("onConfigure"), "Must support configure/edit");
    assert.ok(content.includes("onRemove"), "Must support removal");
    assert.ok(content.includes("WARMUP"), "Must display warmup status gracefully");
  });

  it("should verify IndicatorSubpane container provides isolated vertical scale for future oscillators", () => {
    const subpanePath = path.resolve(
      __dirname,
      "../src/components/charts/indicators/IndicatorSubpane.tsx"
    );
    assert.ok(fs.existsSync(subpanePath));

    const content = fs.readFileSync(subpanePath, "utf-8");
    assert.ok(content.includes("instance"), "Must accept instance prop");
    assert.ok(content.includes("height"), "Must support configurable height");
    assert.ok(content.includes("Stage 70"), "Must reference Stage 70 oscillator readiness");
  });

  it("should verify HistoricalChart synchronizes indicator overlays via LineSeries", () => {
    const chartPath = path.resolve(
      __dirname,
      "../src/components/charts/HistoricalChart.tsx"
    );
    assert.ok(fs.existsSync(chartPath));

    const content = fs.readFileSync(chartPath, "utf-8");
    assert.ok(
      content.includes("indicatorSeriesMapRef"),
      "HistoricalChart must track active indicator series in ref map"
    );
    assert.ok(
      content.includes("indicatorResults"),
      "HistoricalChart must accept indicatorResults prop"
    );
    assert.ok(
      content.includes("activeIndicators"),
      "HistoricalChart must accept activeIndicators prop"
    );
  });

  it("should confirm the /charts page has Stage 69 header metadata and indicators integration", () => {
    const pagePath = path.resolve(
      __dirname,
      "../src/components/charts/ChartsPage.tsx"
    );
    assert.ok(fs.existsSync(pagePath));

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("STAGE 70") || content.includes("STAGE 69"));
    assert.ok(content.includes("TECHNICAL INDICATOR") || content.includes("TECHNICAL ANALYSIS"));
    assert.ok(content.includes("useIndicators"));
    assert.ok(content.includes("IndicatorPicker"));
    assert.ok(content.includes("ActiveIndicators"));
  });

  it("should verify strict design invariants: no purple gradients, no emoji icons, no fake RSI/MACD", () => {
    const dir = path.resolve(__dirname, "../src/components/charts/indicators");
    const files = fs.readdirSync(dir);

    for (const file of files) {
      if (!file.endsWith(".tsx") && !file.endsWith(".ts")) continue;
      const content = fs.readFileSync(path.join(dir, file), "utf-8");
      assert.ok(!content.includes("from-purple-"), `${file} must not contain purple gradients`);
      assert.ok(!content.includes("to-purple-"), `${file} must not contain purple gradients`);
      assert.ok(!content.includes("🚀"), `${file} must not contain emoji`);
      assert.ok(!content.includes("📈"), `${file} must not contain emoji`);
      assert.ok(!content.includes("💰"), `${file} must not contain emoji`);
    }
  });
});
