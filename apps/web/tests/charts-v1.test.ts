import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatBarDate,
  formatBarDateTime,
  formatPercentChange,
  formatPrice,
  formatVolume,
  getAssetClassBadgeLabel,
  getAssetClassColor,
} from "../src/lib/charts/formatting";
import * as chartComponents from "../src/components/charts";
import * as chartHooks from "../src/hooks/charts";

describe("Stage 66 - Charts V1 Tests", () => {
  it("should confirm all foundational Charts V1 components are exported", () => {
    assert.ok(chartComponents.ChartsPage, "ChartsPage must be exported");
    assert.ok(chartComponents.ChartInstrumentHeader, "ChartInstrumentHeader must be exported");
    assert.ok(chartComponents.ChartToolbar, "ChartToolbar must be exported");
    assert.ok(chartComponents.HistoricalChart, "HistoricalChart must be exported");
    assert.ok(chartComponents.ChartCrosshairDetails, "ChartCrosshairDetails must be exported");
    assert.ok(chartComponents.ChartDataStatus, "ChartDataStatus must be exported");
    assert.ok(chartComponents.HistoricalDataTable, "HistoricalDataTable must be exported");
    assert.ok(chartComponents.ChartEmptyState, "ChartEmptyState must be exported");
    assert.ok(chartComponents.ChartErrorState, "ChartErrorState must be exported");
    assert.ok(chartComponents.ChartLoadingSkeleton, "ChartLoadingSkeleton must be exported");
  });

  it("should confirm the charts route page exists and mounts ChartsPage", () => {
    const pagePath = path.resolve(__dirname, "../src/app/(atlas)/charts/page.tsx");
    assert.ok(fs.existsSync(pagePath), "Route page must exist at /charts/page.tsx");

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("ChartsPage"), "Page must render ChartsPage");
    assert.ok(content.includes("generateMetadata"), "Page must define institutional metadata");
  });

  it("should confirm useChartHistory hook is exported", () => {
    assert.ok(chartHooks.useChartHistory, "useChartHistory must be exported from hooks/charts");
  });

  it("should format prices correctly with quotation-aware precision", () => {
    assert.strictEqual(formatPrice(1234.56, 2), "1,234.56");
    assert.strictEqual(formatPrice(1.08542, 4), "1.0854");
    assert.strictEqual(formatPrice(null), "—");
    assert.strictEqual(formatPrice(undefined), "—");
    assert.strictEqual(formatPrice("75.25", 2), "75.25");
  });

  it("should format trading volumes correctly with unit suffixes", () => {
    assert.strictEqual(formatVolume(55_200_000), "55.20M");
    assert.strictEqual(formatVolume(1_250_000_000), "1.25B");
    assert.strictEqual(formatVolume(25_400), "25.40K");
    assert.strictEqual(formatVolume(500), "500");
    assert.strictEqual(formatVolume(null), "—");
    assert.strictEqual(formatVolume(undefined), "—");
  });

  it("should format percentage changes with signed prefix and precision", () => {
    assert.strictEqual(formatPercentChange(2.45), "+2.45%");
    assert.strictEqual(formatPercentChange(-1.32), "-1.32%");
    assert.strictEqual(formatPercentChange(0), "0.00%");
    assert.strictEqual(formatPercentChange(null), "—");
  });

  it("should format UTC bar dates correctly", () => {
    const dateFormatted = formatBarDate("2026-10-16T00:00:00Z");
    assert.ok(dateFormatted.includes("2026") && dateFormatted.includes("16"));
    assert.strictEqual(formatBarDate(""), "—");
  });

  it("should assign distinct color badges and labels to financial asset classes", () => {
    assert.strictEqual(getAssetClassBadgeLabel("equities"), "EQUITY");
    assert.strictEqual(getAssetClassBadgeLabel("etfs"), "ETF");
    assert.strictEqual(getAssetClassBadgeLabel("fx"), "FX SPOT");
    assert.strictEqual(getAssetClassBadgeLabel("crypto"), "CRYPTO");
    assert.strictEqual(getAssetClassBadgeLabel("bonds"), "SOVEREIGN BOND");
    assert.strictEqual(getAssetClassBadgeLabel("futures"), "FUTURES");

    assert.ok(getAssetClassColor("equities").includes("emerald"));
    assert.ok(getAssetClassColor("etfs").includes("cyan"));
    assert.ok(getAssetClassColor("fx").includes("amber"));
    assert.ok(getAssetClassColor("crypto").includes("violet"));
    assert.ok(getAssetClassColor("bonds").includes("blue"));
    assert.ok(getAssetClassColor("futures").includes("rose"));
  });

  it("should confirm lightweight-charts is installed as a valid production dependency", () => {
    const pkgPath = path.resolve(__dirname, "../package.json");
    assert.ok(fs.existsSync(pkgPath), "package.json must exist in apps/web");

    const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf-8"));
    assert.ok(
      pkg.dependencies && pkg.dependencies["lightweight-charts"],
      "lightweight-charts must be listed in dependencies"
    );
  });
});
