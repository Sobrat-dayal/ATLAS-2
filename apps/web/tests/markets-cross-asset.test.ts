import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatIndexedValue,
  formatIsoTime,
  formatNativeChange,
  formatNumber,
  formatPercentChange,
  getAssetClassColor,
  getModeLabel,
  getWindowLabel,
} from "../src/lib/markets/cross-asset/formatting";
import * as crossAssetComponents from "../src/components/markets/cross-asset";

describe("Stage 65 - Cross-Asset Markets V1 Tests", () => {
  it("should confirm Cross-Asset Markets components export cleanly", () => {
    assert.ok(crossAssetComponents.CrossAssetMarketsPage, "CrossAssetMarketsPage must be exported");
    assert.ok(crossAssetComponents.CrossAssetHeader, "CrossAssetHeader must be exported");
    assert.ok(crossAssetComponents.CrossAssetUniverseSelector, "CrossAssetUniverseSelector must be exported");
    assert.ok(crossAssetComponents.CrossAssetModeSelector, "CrossAssetModeSelector must be exported");
    assert.ok(crossAssetComponents.CrossAssetWindowSelector, "CrossAssetWindowSelector must be exported");
    assert.ok(crossAssetComponents.CrossAssetCoverageSummary, "CrossAssetCoverageSummary must be exported");
    assert.ok(crossAssetComponents.AssetClassOverviewGrid, "AssetClassOverviewGrid must be exported");
    assert.ok(crossAssetComponents.CrossAssetComparisonTable, "CrossAssetComparisonTable must be exported");
    assert.ok(crossAssetComponents.CrossAssetInspector, "CrossAssetInspector must be exported");
    assert.ok(crossAssetComponents.AlignmentMethodologyPanel, "AlignmentMethodologyPanel must be exported");
    assert.ok(crossAssetComponents.CrossAssetEmptyState, "CrossAssetEmptyState must be exported");
    assert.ok(crossAssetComponents.CrossAssetErrorState, "CrossAssetErrorState must be exported");
    assert.ok(crossAssetComponents.CrossAssetLoadingSkeleton, "CrossAssetLoadingSkeleton must be exported");
  });

  it("should confirm the cross-asset route page exists in app router", () => {
    const pagePath = path.resolve(__dirname, "../src/app/(atlas)/markets/cross-asset/page.tsx");
    assert.ok(fs.existsSync(pagePath), "Route page must exist at /markets/cross-asset/page.tsx");

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("CrossAssetMarketsPage"), "Route page must render CrossAssetMarketsPage");
    assert.ok(content.includes("generateMetadata"), "Route page must define institutional metadata");
  });

  it("should confirm MarketsNavigationTabs enables the cross-asset tab", () => {
    const tabsPath = path.resolve(__dirname, "../src/components/markets/MarketsNavigationTabs.tsx");
    assert.ok(fs.existsSync(tabsPath), "MarketsNavigationTabs must exist");

    const content = fs.readFileSync(tabsPath, "utf-8");
    assert.ok(
      content.includes('id: "cross-asset"') &&
        content.includes('href: "/markets/cross-asset"') &&
        content.includes("isImplemented: true"),
      "Cross-Asset tab must be active and implemented in navigation"
    );
  });

  it("should correctly format numbers and percent changes", () => {
    assert.strictEqual(formatNumber(1234.56), "1,234.56");
    assert.strictEqual(formatNumber(null), "—");
    assert.strictEqual(formatNumber("4.225", 3), "4.225");

    assert.strictEqual(formatPercentChange(2.45), "+2.45%");
    assert.strictEqual(formatPercentChange(-1.82), "-1.82%");
    assert.strictEqual(formatPercentChange(0), "0.00%");
    assert.strictEqual(formatPercentChange(null), "—");
  });

  it("should preserve native market conventions and never treat bond yields as equity returns", () => {
    // Bond yield in basis points: e.g. change of 7.5 bps
    const bondChange = formatNativeChange("7.5", null, "BOND_YIELD_BPS_CHANGE", "bps");
    assert.strictEqual(bondChange, "+7.5 bps", "Bond yield changes must format explicitly as basis points (bps)");

    // Equity price change in %
    const equityChange = formatNativeChange("3.35", "1.4471", "EQUITY_PRICE_CHANGE", "%");
    assert.strictEqual(equityChange, "+1.45%", "Equity change must format as percentage price return");

    // Futures price change in contractual units (e.g. USD/barrel)
    const futuresChange = formatNativeChange("1.15", "1.637", "FUTURES_SETTLEMENT_CHANGE", "USD/barrel");
    assert.strictEqual(futuresChange, "+1.64%", "Futures change with percent available must format percentage");

    // Futures price change without percentage
    const futuresPoints = formatNativeChange("1.15", null, "FUTURES_SETTLEMENT_CHANGE", "USD/barrel");
    assert.strictEqual(futuresPoints, "+1.15 USD/barrel", "Futures change without percent must format in native quote units");
  });

  it("should correctly format indexed values to base 100", () => {
    assert.strictEqual(formatIndexedValue("101.4471"), "101.45");
    assert.strictEqual(formatIndexedValue(98.2), "98.20");
    assert.strictEqual(formatIndexedValue(null), "—");
  });

  it("should correctly format UTC timestamps", () => {
    const formatted = formatIsoTime("2026-10-17T18:00:00Z");
    assert.ok(formatted.includes("18:00:00 UTC"));
    assert.strictEqual(formatIsoTime(null), "—");
  });

  it("should return distinct semantic colors for each financial asset class", () => {
    const eq = getAssetClassColor("equities");
    const etf = getAssetClassColor("etfs");
    const fx = getAssetClassColor("fx");
    const crypto = getAssetClassColor("crypto");
    const bonds = getAssetClassColor("bonds");
    const futures = getAssetClassColor("futures");

    assert.ok(eq.text.includes("blue"), "Equities badge should use blue tones");
    assert.ok(etf.text.includes("indigo"), "ETFs badge should use indigo tones");
    assert.ok(fx.text.includes("teal"), "FX badge should use teal tones");
    assert.ok(crypto.text.includes("amber"), "Crypto badge should use amber tones");
    assert.ok(bonds.text.includes("purple"), "Bonds badge should use purple tones");
    assert.ok(futures.text.includes("emerald"), "Futures badge should use emerald tones");
  });

  it("should return human-readable labels for modes and windows", () => {
    assert.strictEqual(getModeLabel("native_overview"), "Native Market Overview");
    assert.strictEqual(getModeLabel("aligned_performance"), "Aligned Price Performance");
    assert.strictEqual(getWindowLabel("last_24h"), "Previous 24 Hours");
    assert.strictEqual(getWindowLabel("last_7d"), "Previous 7 Days");
    assert.strictEqual(getWindowLabel("last_30d"), "Previous 30 Days");
  });
});
