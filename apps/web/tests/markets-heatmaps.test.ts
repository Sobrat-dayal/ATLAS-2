import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  describeCoverageStatus,
  describeExclusionReason,
  formatMarketCap,
  formatPrice,
  formatSignedPercent,
  formatTimestamp,
} from "../src/lib/markets/heatmaps/formatting";
import { getHeatmapTileColor } from "../src/lib/markets/heatmaps/colors";
import {
  computeHierarchicalTreemap,
  computeSquarifiedLayout,
} from "../src/lib/markets/heatmaps/treemap";
import * as heatmapsComponents from "../src/components/markets/heatmaps";
import { HeatmapGroupNode, HeatmapLeafNode } from "../src/lib/markets/heatmaps/types";

describe("Stage 64 - Market Heatmaps V1 Tests", () => {
  it("should confirm Market Heatmaps components export cleanly", () => {
    assert.ok(heatmapsComponents.MarketHeatmapsPage, "MarketHeatmapsPage must be exported");
    assert.ok(heatmapsComponents.HeatmapsHeader, "HeatmapsHeader must be exported");
    assert.ok(heatmapsComponents.HeatmapUniverseSelector, "HeatmapUniverseSelector must be exported");
    assert.ok(heatmapsComponents.HeatmapPeriodSelector, "HeatmapPeriodSelector must be exported");
    assert.ok(heatmapsComponents.HeatmapModeSelector, "HeatmapModeSelector must be exported");
    assert.ok(heatmapsComponents.HeatmapCoverageSummary, "HeatmapCoverageSummary must be exported");
    assert.ok(heatmapsComponents.HeatmapLegend, "HeatmapLegend must be exported");
    assert.ok(heatmapsComponents.HeatmapTreemap, "HeatmapTreemap must be exported");
    assert.ok(heatmapsComponents.HeatmapTile, "HeatmapTile must be exported");
    assert.ok(heatmapsComponents.HeatmapInspector, "HeatmapInspector must be exported");
    assert.ok(heatmapsComponents.HeatmapAccessibleTable, "HeatmapAccessibleTable must be exported");
    assert.ok(heatmapsComponents.HeatmapEmptyState, "HeatmapEmptyState must be exported");
    assert.ok(heatmapsComponents.HeatmapErrorState, "HeatmapErrorState must be exported");
    assert.ok(heatmapsComponents.HeatmapLoadingState, "HeatmapLoadingState must be exported");
  });

  it("should correctly map financial returns to diverging performance colors", () => {
    // Positive return -> green / emerald tones
    const pos = getHeatmapTileColor(2.35);
    assert.strictEqual(pos.isMissing, false);
    assert.ok(pos.backgroundColor.includes("4, 120, 87") || pos.backgroundColor.includes("5, 150, 105"));

    // Extreme positive return -> saturated emerald boundary
    const extremePos = getHeatmapTileColor(8.5);
    assert.strictEqual(extremePos.isMissing, false);
    assert.ok(extremePos.backgroundColor.includes("16, 185, 129"));

    // Negative return -> red / crimson tones
    const neg = getHeatmapTileColor(-1.8);
    assert.strictEqual(neg.isMissing, false);
    assert.ok(neg.backgroundColor.includes("153, 27, 27") || neg.backgroundColor.includes("127, 29, 29"));

    // Extreme negative return -> saturated red boundary
    const extremeNeg = getHeatmapTileColor(-9.2);
    assert.strictEqual(extremeNeg.isMissing, false);
    assert.ok(extremeNeg.backgroundColor.includes("220, 38, 38"));

    // Exactly zero return -> neutral zinc
    const zero = getHeatmapTileColor(0.0);
    assert.strictEqual(zero.isMissing, false);
    assert.ok(zero.backgroundColor.includes("39, 39, 42"));

    // Missing returns (null, undefined, invalid) -> distinct isMissing: true
    const missingNull = getHeatmapTileColor(null);
    assert.strictEqual(missingNull.isMissing, true);

    const missingUndefined = getHeatmapTileColor(undefined);
    assert.strictEqual(missingUndefined.isMissing, true);

    const missingNaN = getHeatmapTileColor("invalid");
    assert.strictEqual(missingNaN.isMissing, true);
  });

  it("should format signed percentage returns with explicit '+' sign", () => {
    assert.strictEqual(formatSignedPercent(3.45), "+3.45%");
    assert.strictEqual(formatSignedPercent("1.2"), "+1.20%");
    assert.strictEqual(formatSignedPercent(-2.75), "-2.75%");
    assert.strictEqual(formatSignedPercent(0), "0.00%");
    assert.strictEqual(formatSignedPercent(null), "N/A");
    assert.strictEqual(formatSignedPercent(undefined), "N/A");
  });

  it("should format financial market capitalization with T, B, and M suffixes", () => {
    assert.strictEqual(formatMarketCap(3540000000000, "USD"), "$3.54T");
    assert.strictEqual(formatMarketCap("710000000000", "USD"), "$710.0B");
    assert.strictEqual(formatMarketCap(86000000, "USDT"), "$86.0M");
    assert.strictEqual(formatMarketCap(null), "N/A");
    assert.strictEqual(formatMarketCap(-100), "N/A");
  });

  it("should format traded prices with explicit currency symbols", () => {
    assert.strictEqual(formatPrice(232.5, "USD"), "$232.50");
    assert.strictEqual(formatPrice("67850.00", "USDT"), "$67,850.00");
    assert.strictEqual(formatPrice(0.542, "USDT"), "$0.5420");
    assert.strictEqual(formatPrice(null), "—");

    // Timestamp formatting
    assert.strictEqual(formatTimestamp(null), "—");
    assert.strictEqual(formatTimestamp("invalid"), "—");
    assert.ok(formatTimestamp("2026-10-17T21:40:00Z").includes("UTC"));
  });

  it("should format coverage status and exclusion reasons truthfully", () => {
    const complete = describeCoverageStatus("COMPLETE_FOR_DEFINED_UNIVERSE");
    assert.strictEqual(complete.label, "Complete");
    assert.ok(complete.badgeClass.includes("emerald"));

    const partial = describeCoverageStatus("PARTIAL_COVERAGE");
    assert.strictEqual(partial.label, "Partial");
    assert.ok(partial.badgeClass.includes("amber"));

    assert.strictEqual(
      describeExclusionReason("NO_CURRENT_QUOTE"),
      "Current market quote is missing from authoritative provider"
    );
    assert.strictEqual(
      describeExclusionReason("MISSING_WEIGHT"),
      "Verified market capitalization is unavailable for this instrument"
    );
    assert.strictEqual(
      describeExclusionReason("INVALID_DENOMINATOR"),
      "Reference price is zero or negative (cannot compute percentage change)"
    );
  });

  it("should compute squarified treemap layout with strictly proportional tile areas", () => {
    // 3 items with weights: A = 50, B = 30, C = 20 -> Area proportions 50%, 30%, 20%
    const items = [
      { id: "A", weight: 50, data: { symbol: "A" } as HeatmapLeafNode },
      { id: "B", weight: 30, data: { symbol: "B" } as HeatmapLeafNode },
      { id: "C", weight: 20, data: { symbol: "C" } as HeatmapLeafNode },
    ];

    const width = 1000;
    const height = 500;
    const totalArea = width * height; // 500,000

    const rects = computeSquarifiedLayout(items, 0, 0, width, height, 0);
    assert.strictEqual(rects.length, 3);

    const rectA = rects.find((r) => r.id === "A")!;
    const rectB = rects.find((r) => r.id === "B")!;
    const rectC = rects.find((r) => r.id === "C")!;

    assert.ok(rectA, "Rect A must exist");
    assert.ok(rectB, "Rect B must exist");
    assert.ok(rectC, "Rect C must exist");

    const areaA = rectA.width * rectA.height;
    const areaB = rectB.width * rectB.height;
    const areaC = rectC.width * rectC.height;

    // Check proportional area within 1% layout tolerance
    assert.ok(Math.abs(areaA / totalArea - 0.5) < 0.01, `Area A fraction was ${areaA / totalArea}`);
    assert.ok(Math.abs(areaB / totalArea - 0.3) < 0.01, `Area B fraction was ${areaB / totalArea}`);
    assert.ok(Math.abs(areaC / totalArea - 0.2) < 0.01, `Area C fraction was ${areaC / totalArea}`);

    // All rectangles must stay within bounds
    for (const r of rects) {
      assert.ok(r.x >= 0, "x >= 0");
      assert.ok(r.y >= 0, "y >= 0");
      assert.ok(r.x + r.width <= width + 0.01, "x + width <= total width");
      assert.ok(r.y + r.height <= height + 0.01, "y + height <= total height");
    }
  });

  it("should compute hierarchical sector treemaps with nested child rectangles", () => {
    const dummyLeaf = (sym: string, w: number): HeatmapLeafNode => ({
      node_id: `leaf:${sym}`,
      node_kind: "instrument",
      instrument_entity_id: "12345678-1234-5678-1234-567812345678",
      market_series_identity: `series:${sym}`,
      symbol: sym,
      display_name: `Company ${sym}`,
      asset_class: "equity",
      exchange_or_venue: "XNAS",
      currency: "USD",
      freshness_status: "live",
      delay_status: "realtime",
      provider: "openbb",
      is_qualified: true,
      weight_value: w,
      normalized_weight: w / 100,
    });

    const groups: HeatmapGroupNode[] = [
      {
        group_id: "sector:tech",
        group_kind: "sector",
        label: "Technology",
        taxonomy: "GICS",
        constituent_count: 2,
        qualified_count: 2,
        total_weight: 70,
        normalized_weight: 0.7,
        aggregate_return: 3.5,
        aggregate_method: "cap_weighted_return",
        children: [dummyLeaf("AAPL", 40), dummyLeaf("MSFT", 30)],
      },
      {
        group_id: "sector:health",
        group_kind: "sector",
        label: "Healthcare",
        taxonomy: "GICS",
        constituent_count: 1,
        qualified_count: 1,
        total_weight: 30,
        normalized_weight: 0.3,
        aggregate_return: -1.2,
        aggregate_method: "cap_weighted_return",
        children: [dummyLeaf("UNH", 30)],
      },
    ];

    const hierarchical = computeHierarchicalTreemap(groups, 800, 600);
    assert.strictEqual(hierarchical.length, 2);

    const techGroup = hierarchical.find((g) => g.group.label === "Technology")!;
    assert.ok(techGroup, "Technology group must exist");
    assert.strictEqual(techGroup.children.length, 2);

    const healthGroup = hierarchical.find((g) => g.group.label === "Healthcare")!;
    assert.ok(healthGroup, "Healthcare group must exist");
    assert.strictEqual(healthGroup.children.length, 1);
  });

  it("should verify that the /markets/heatmaps Next.js page exists and is properly configured", () => {
    const pagePath = path.join(
      process.cwd(),
      "src/app/(atlas)/markets/heatmaps/page.tsx"
    );
    assert.ok(fs.existsSync(pagePath), "page.tsx must exist at src/app/(atlas)/markets/heatmaps/page.tsx");
    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("MarketHeatmapsPage"), "page.tsx must import and render MarketHeatmapsPage");
    assert.ok(content.includes("Market Heatmaps | ATLAS"), "page.tsx must export metadata title");
  });
});
