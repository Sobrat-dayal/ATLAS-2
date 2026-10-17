import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatActivityVolume,
  formatCoverageStatus,
  formatExclusionReason,
  formatPrice,
  formatRank,
  formatSignedAbsoluteChange,
  formatSignedPercent,
  formatTimestamp,
} from "../src/lib/markets/movers/formatting";
import * as moversComponents from "../src/components/markets/movers";
import * as marketsComponents from "../src/components/markets";

describe("Stage 63 - Market Movers V1 Tests", () => {
  it("should confirm Market Movers components export cleanly", () => {
    assert.ok(moversComponents.MarketMoversPage, "MarketMoversPage must be exported");
    assert.ok(moversComponents.MarketMoversHeader, "MarketMoversHeader must be exported");
    assert.ok(moversComponents.MoverUniverseSelector, "MoverUniverseSelector must be exported");
    assert.ok(moversComponents.MoverWindowSelector, "MoverWindowSelector must be exported");
    assert.ok(moversComponents.MoverCategoryTabs, "MoverCategoryTabs must be exported");
    assert.ok(moversComponents.MoverFilters, "MoverFilters must be exported");
    assert.ok(moversComponents.MoverCoverageSummary, "MoverCoverageSummary must be exported");
    assert.ok(moversComponents.MarketMoversTable, "MarketMoversTable must be exported");
    assert.ok(moversComponents.MarketMoverRow, "MarketMoverRow must be exported");
    assert.ok(moversComponents.MarketMoverInspector, "MarketMoverInspector must be exported");
    assert.ok(moversComponents.MoverEmptyState, "MoverEmptyState must be exported");
    assert.ok(moversComponents.MoverErrorState, "MoverErrorState must be exported");
    assert.ok(marketsComponents.MarketsNavigationTabs, "MarketsNavigationTabs must be exported");
  });

  it("should format signed percentage returns with positive plus sign and tabular precision", () => {
    assert.strictEqual(formatSignedPercent(8.42), "+8.42%");
    assert.strictEqual(formatSignedPercent("3.1"), "+3.10%");
    assert.strictEqual(formatSignedPercent(-5.6), "-5.60%");
    assert.strictEqual(formatSignedPercent(0), "0.00%");
    assert.strictEqual(formatSignedPercent(null), "—");
    assert.strictEqual(formatSignedPercent(undefined), "—");
    assert.strictEqual(formatSignedPercent(""), "—");
  });

  it("should format signed absolute price changes with explicit currency and sign", () => {
    assert.strictEqual(formatSignedAbsoluteChange("4.25", "USD"), "+$4.25");
    assert.strictEqual(formatSignedAbsoluteChange("-2.50", "USD"), "-$2.50");
    assert.strictEqual(formatSignedAbsoluteChange("0.00", "USD"), "$0.00");
    assert.strictEqual(formatSignedAbsoluteChange(null), "—");
  });

  it("should format traded prices with correct decimals and currency symbols", () => {
    assert.strictEqual(formatPrice("232.50", "USD"), "$232.50");
    assert.strictEqual(formatPrice("67850.00", "USDT"), "$67,850.00");
    assert.strictEqual(formatPrice("0.5420", "USDT"), "$0.5420");
    assert.strictEqual(formatPrice("412.50", "US cents"), "412.50 US cents");
    assert.strictEqual(formatPrice(null), "—");
  });

  it("should format activity volume preserving explicit units", () => {
    assert.strictEqual(formatActivityVolume("48210500", "shares"), "48.21M shares");
    assert.strictEqual(formatActivityVolume("1850000000", "USDT"), "1.85B USDT");
    assert.strictEqual(formatActivityVolume("285400", "contracts"), "285.4K contracts");
    assert.strictEqual(formatActivityVolume("500", "shares"), "500 shares");
    assert.strictEqual(formatActivityVolume(null), "—");
  });

  it("should format ordinal ranks correctly", () => {
    assert.strictEqual(formatRank(1), "#1");
    assert.strictEqual(formatRank(25), "#25");
    assert.strictEqual(formatRank(100), "#100");
  });

  it("should accurately classify and describe coverage statuses", () => {
    const complete = formatCoverageStatus("COMPLETE_FOR_DEFINED_UNIVERSE");
    assert.strictEqual(complete.label, "Complete for Defined Universe");
    assert.ok(complete.badgeClass.includes("emerald"));

    const partial = formatCoverageStatus("PARTIAL_COVERAGE");
    assert.strictEqual(partial.label, "Partial Coverage");
    assert.ok(partial.badgeClass.includes("amber"));

    const degraded = formatCoverageStatus("DEGRADED");
    assert.strictEqual(degraded.label, "Degraded Coverage");
    assert.ok(degraded.badgeClass.includes("rose"));

    const unavail = formatCoverageStatus("UNAVAILABLE");
    assert.strictEqual(unavail.label, "Unavailable");
  });

  it("should provide truthful, human-readable descriptions of typed exclusion reasons", () => {
    assert.strictEqual(
      formatExclusionReason("INVALID_DENOMINATOR"),
      "Non-positive reference price (percent return undefined)"
    );
    assert.strictEqual(
      formatExclusionReason("NO_CURRENT_QUOTE"),
      "Missing latest traded quote"
    );
    assert.strictEqual(
      formatExclusionReason("NO_REFERENCE"),
      "Missing reference observation (previous close/settle)"
    );
    assert.strictEqual(
      formatExclusionReason("MISSING_VOLUME"),
      "No trading volume reported"
    );
    assert.strictEqual(
      formatExclusionReason("INSTRUMENT_INACTIVE"),
      "Instrument not actively trading"
    );
    assert.strictEqual(
      formatExclusionReason("OTHER"),
      "Zero price change or unqualified"
    );
  });

  it("should format timestamps cleanly", () => {
    const formatted = formatTimestamp("2026-10-17T14:30:00Z");
    assert.ok(typeof formatted === "string");
    assert.ok(formatted.length >= 5);
    assert.strictEqual(formatTimestamp(null), "—");
  });

  it("should verify the Next.js /markets/movers page exists and is properly configured", () => {
    const pagePath = path.resolve(
      __dirname,
      "../src/app/(atlas)/markets/movers/page.tsx"
    );
    assert.ok(fs.existsSync(pagePath), "page.tsx must exist at (atlas)/markets/movers/page.tsx");

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("MarketMoversPage"), "page.tsx must render MarketMoversPage");
    assert.ok(content.includes("generateMetadata"), "page.tsx must export generateMetadata");
    assert.ok(content.includes("Market Movers | ATLAS"), "title must be Market Movers | ATLAS");
  });
});
