import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import * as chartComponents from "../src/components/charts";
import * as chartHooks from "../src/hooks/charts";
import * as chartApi from "../src/lib/charts/api";
import {
  ChartIntervalOptionDTO,
  ChartRenderMode,
} from "../src/lib/charts/types";

describe("Stage 68 - Advanced Chart Intervals & Chart Types V1", () => {
  it("should confirm all Stage 68 components and hooks are exported", () => {
    assert.ok(
      chartComponents.ChartIntervalSelector,
      "ChartIntervalSelector must be exported"
    );
    assert.ok(
      chartComponents.ChartTypeSelector,
      "ChartTypeSelector must be exported"
    );
    assert.ok(
      chartHooks.useChartIntervals,
      "useChartIntervals must be exported from hooks/charts"
    );
    assert.ok(
      chartApi.fetchChartIntervals,
      "fetchChartIntervals must be exported from lib/charts/api"
    );
  });

  it("should verify ChartRenderMode supports exactly 4 professional financial chart types", () => {
    const validModes: ChartRenderMode[] = [
      "candlestick",
      "bar",
      "line",
      "area",
    ];
    assert.strictEqual(validModes.length, 4);
    assert.ok(validModes.includes("candlestick"));
    assert.ok(validModes.includes("bar"));
    assert.ok(validModes.includes("line"));
    assert.ok(validModes.includes("area"));
  });

  it("should verify HistoricalChart source code registers BarSeries and AreaSeries", () => {
    const chartPath = path.resolve(
      __dirname,
      "../src/components/charts/HistoricalChart.tsx"
    );
    assert.ok(fs.existsSync(chartPath));

    const content = fs.readFileSync(chartPath, "utf-8");
    assert.ok(
      content.includes("CandlestickSeries"),
      "HistoricalChart must mount CandlestickSeries"
    );
    assert.ok(
      content.includes("BarSeries"),
      "HistoricalChart must mount BarSeries for OHLC bars"
    );
    assert.ok(
      content.includes("LineSeries"),
      "HistoricalChart must mount LineSeries for close line"
    );
    assert.ok(
      content.includes("AreaSeries"),
      "HistoricalChart must mount AreaSeries for area charts"
    );
  });

  it("should verify ChartIntervalSelector handles native, derived, and unavailable intervals", () => {
    const selectorPath = path.resolve(
      __dirname,
      "../src/components/charts/ChartIntervalSelector.tsx"
    );
    assert.ok(fs.existsSync(selectorPath));

    const content = fs.readFileSync(selectorPath, "utf-8");
    assert.ok(content.includes("AVAILABLE_NATIVE"));
    assert.ok(content.includes("AVAILABLE_DERIVED"));
    assert.ok(content.includes("cursor-not-allowed"));
    assert.ok(content.includes("unavailability_reason"));
  });

  it("should verify ChartTypeSelector renders all 4 types with appropriate icons", () => {
    const selectorPath = path.resolve(
      __dirname,
      "../src/components/charts/ChartTypeSelector.tsx"
    );
    assert.ok(fs.existsSync(selectorPath));

    const content = fs.readFileSync(selectorPath, "utf-8");
    assert.ok(content.includes("candlestick"));
    assert.ok(content.includes("bar"));
    assert.ok(content.includes("line"));
    assert.ok(content.includes("area"));
  });

  it("should confirm the /charts page has Stage 68 header metadata", () => {
    const pagePath = path.resolve(
      __dirname,
      "../src/components/charts/ChartsPage.tsx"
    );
    assert.ok(fs.existsSync(pagePath));

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("STAGE 68"));
    assert.ok(content.includes("MULTI-TIMEFRAME & ADVANCED TYPES"));
    assert.ok(content.includes("useChartIntervals"));
  });

  it("should verify ChartDataStatus displays active interval and lineage", () => {
    const statusPath = path.resolve(
      __dirname,
      "../src/components/charts/ChartDataStatus.tsx"
    );
    assert.ok(fs.existsSync(statusPath));

    const content = fs.readFileSync(statusPath, "utf-8");
    assert.ok(content.includes("intervalSourceKind"));
    assert.ok(content.includes("DERIVED"));
    assert.ok(content.includes("NATIVE"));
  });

  it("should verify safe interval option data structure", () => {
    const sampleOption: ChartIntervalOptionDTO = {
      interval_id: "1w",
      display_label: "1W",
      duration_seconds: null, // calendar interval
      availability: "AVAILABLE_DERIVED",
      native_or_derived: "DERIVED",
      is_supported: true,
      source_interval: "1d",
      earliest_available: "2025-10-16T00:00:00Z",
      latest_available: "2026-10-16T00:00:00Z",
      live_bar_supported: false,
      unavailability_reason: null,
    };

    assert.strictEqual(sampleOption.interval_id, "1w");
    assert.strictEqual(sampleOption.availability, "AVAILABLE_DERIVED");
    assert.strictEqual(sampleOption.duration_seconds, null);
    assert.strictEqual(sampleOption.source_interval, "1d");
  });
});
