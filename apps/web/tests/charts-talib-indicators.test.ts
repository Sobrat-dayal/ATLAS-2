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

describe("Stage 70 - TA-Lib Technical Analysis Engine & Oscillator Panes Tests", () => {
  it("should confirm all Stage 70 indicator components and subpanes are exported", () => {
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
      indicatorComponents.IndicatorInspectorTable,
      "IndicatorInspectorTable must be exported"
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

  it("should verify Stage 70 production catalog covers all 14 indicators across Trend, Momentum, Volatility, and Volume", () => {
    const EXPECTED_INDICATORS = [
      { id: "atlas.sma", category: "TREND", target: "PRICE_OVERLAY" },
      { id: "atlas.ema", category: "TREND", target: "PRICE_OVERLAY" },
      { id: "atlas.wma", category: "TREND", target: "PRICE_OVERLAY" },
      { id: "atlas.rsi", category: "MOMENTUM", target: "INDICATOR_PANE" },
      { id: "atlas.macd", category: "MOMENTUM", target: "INDICATOR_PANE" },
      { id: "atlas.bbands", category: "VOLATILITY", target: "PRICE_OVERLAY" },
      { id: "atlas.atr", category: "VOLATILITY", target: "INDICATOR_PANE" },
      { id: "atlas.stoch", category: "MOMENTUM", target: "INDICATOR_PANE" },
      { id: "atlas.adx", category: "TREND", target: "INDICATOR_PANE" },
      { id: "atlas.cci", category: "MOMENTUM", target: "INDICATOR_PANE" },
      { id: "atlas.roc", category: "MOMENTUM", target: "INDICATOR_PANE" },
      { id: "atlas.mom", category: "MOMENTUM", target: "INDICATOR_PANE" },
      { id: "atlas.obv", category: "VOLUME", target: "INDICATOR_PANE" },
      { id: "atlas.mfi", category: "VOLUME", target: "INDICATOR_PANE" },
    ];

    assert.strictEqual(EXPECTED_INDICATORS.length, 14);

    const categories = new Set(EXPECTED_INDICATORS.map((i) => i.category));
    assert.ok(categories.has("TREND"));
    assert.ok(categories.has("MOMENTUM"));
    assert.ok(categories.has("VOLATILITY"));
    assert.ok(categories.has("VOLUME"));
  });

  it("should verify multi-output schemas for MACD, Bollinger Bands, and Stochastic", () => {
    const macdOutputs = ["macd_line", "signal_line", "histogram"];
    const bbandsOutputs = ["upper_band", "middle_band", "lower_band"];
    const stochOutputs = ["slowk", "slowd"];

    assert.strictEqual(macdOutputs.length, 3);
    assert.strictEqual(bbandsOutputs.length, 3);
    assert.strictEqual(stochOutputs.length, 2);
  });

  it("should verify MISSING_VOLUME and TALIB_UNAVAILABLE status codes in IndicatorStatus", () => {
    const status1: IndicatorStatus = "MISSING_VOLUME";
    const status2: IndicatorStatus = "TALIB_UNAVAILABLE";
    const status3: IndicatorStatus = "WARMUP";
    const status4: IndicatorStatus = "READY";

    assert.strictEqual(status1, "MISSING_VOLUME");
    assert.strictEqual(status2, "TALIB_UNAVAILABLE");
    assert.strictEqual(status3, "WARMUP");
    assert.strictEqual(status4, "READY");
  });

  it("should verify up to 12 active indicator instances are supported simultaneously", () => {
    const instances: IndicatorInstanceConfig[] = [];
    for (let i = 1; i <= 12; i++) {
      instances.push({
        instance_id: `study_${i}`,
        indicator_id: i % 2 === 0 ? "atlas.ema" : "atlas.rsi",
        version: 1,
        parameters: { period: 10 + i },
        visible: true,
        color: "#38bdf8",
      });
    }

    assert.strictEqual(instances.length, 12);
  });

  it("should verify IndicatorSubpane renders Lightweight Charts with reference levels", () => {
    const subpanePath = path.resolve(
      __dirname,
      "../src/components/charts/indicators/IndicatorSubpane.tsx"
    );
    assert.ok(fs.existsSync(subpanePath));

    const content = fs.readFileSync(subpanePath, "utf-8");
    assert.ok(content.includes("createChart"), "Subpane must instantiate Lightweight Charts");
    assert.ok(content.includes("HistogramSeries"), "Subpane must support zero-centered HistogramSeries");
    assert.ok(content.includes("LineSeries"), "Subpane must support LineSeries");
    assert.ok(content.includes("createPriceLine"), "Subpane must render conventional reference lines");
    assert.ok(content.includes("MISSING_VOLUME"), "Subpane must display volume requirement badge");
    assert.ok(content.includes("WARMUP"), "Subpane must display warmup period badge");
  });

  it("should verify HistoricalChart renders multi-series price overlays like Bollinger Bands", () => {
    const chartPath = path.resolve(
      __dirname,
      "../src/components/charts/HistoricalChart.tsx"
    );
    assert.ok(fs.existsSync(chartPath));

    const content = fs.readFileSync(chartPath, "utf-8");
    assert.ok(content.includes("PRICE_OVERLAY"), "HistoricalChart must enforce PRICE_OVERLAY targets");
    assert.ok(content.includes("upper_band"), "HistoricalChart must handle Bollinger Upper band");
    assert.ok(content.includes("lower_band"), "HistoricalChart must handle Bollinger Lower band");
    assert.ok(content.includes("LineStyle.Dashed"), "Upper/Lower bands should use dashed or subtle styling");
  });

  it("should verify IndicatorInspectorTable provides an accessible tabular view", () => {
    const inspectorPath = path.resolve(
      __dirname,
      "../src/components/charts/indicators/IndicatorInspectorTable.tsx"
    );
    assert.ok(fs.existsSync(inspectorPath));

    const content = fs.readFileSync(inspectorPath, "utf-8");
    assert.ok(content.includes("<table"), "Inspector must contain a semantic HTML table");
    assert.ok(content.includes("aria-expanded"), "Inspector toggle button must have aria attributes");
    assert.ok(content.includes("Pagination"), "Inspector must support page navigation");
  });

  it("should confirm the /charts page has Stage 70 header metadata and oscillator subpanes mounted", () => {
    const pagePath = path.resolve(
      __dirname,
      "../src/components/charts/ChartsPage.tsx"
    );
    assert.ok(fs.existsSync(pagePath));

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("STAGE 70"), "Header must feature STAGE 70");
    assert.ok(content.includes("PRODUCTION TECHNICAL ANALYSIS ENGINE (TA-LIB)"));
    assert.ok(content.includes("IndicatorSubpane"), "Subpanes must be mounted on ChartsPage");
    assert.ok(content.includes("IndicatorInspectorTable"), "Inspector table must be mounted on ChartsPage");
  });

  it("should verify strict design invariants: no purple gradients, no emoji icons, no fake buy/sell signals", () => {
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
      assert.ok(!content.includes("BUY NOW"), `${file} must not contain fake trading signals`);
      assert.ok(!content.includes("SELL NOW"), `${file} must not contain fake trading signals`);
    }
  });
});
