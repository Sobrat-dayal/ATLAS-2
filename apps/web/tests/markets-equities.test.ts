import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatEquityPrice,
  formatAbsoluteChange,
  formatPercentageChange,
  formatEquitySubtype,
  getFreshnessBadge,
  getDirectionColorClass,
  formatObservationTime,
} from "../src/lib/markets/equities/formatting";
import * as equitiesComponents from "../src/components/markets/equities";
import * as marketsComponents from "../src/components/markets";

describe("Stage 57 - Equities Markets V1 Tests", () => {
  it("should confirm Equities components export cleanly", () => {
    assert.ok(equitiesComponents.EquitiesPage, "EquitiesPage must be exported");
    assert.ok(equitiesComponents.EquitiesHeader, "EquitiesHeader must be exported");
    assert.ok(
      equitiesComponents.EquityCoverageSummary,
      "EquityCoverageSummary must be exported"
    );
    assert.ok(
      equitiesComponents.EquityDirectoryFilters,
      "EquityDirectoryFilters must be exported"
    );
    assert.ok(
      equitiesComponents.EquityDirectoryTable,
      "EquityDirectoryTable must be exported"
    );
    assert.ok(
      equitiesComponents.EquityDirectoryRow,
      "EquityDirectoryRow must be exported"
    );
    assert.ok(equitiesComponents.EquityInspector, "EquityInspector must be exported");
    assert.ok(equitiesComponents.EquityEmptyState, "EquityEmptyState must be exported");
    assert.ok(
      marketsComponents.MarketsNavigationTabs,
      "MarketsNavigationTabs must be exported from components/markets"
    );
  });

  it("should format USD equity prices with 2 decimals", () => {
    const formatted = formatEquityPrice("224.5", "USD");
    assert.strictEqual(formatted, "$224.50");
  });

  it("should format INR equity prices with Indian Rupee symbol", () => {
    const formatted = formatEquityPrice("1450.75", "INR");
    assert.strictEqual(formatted, "₹1,450.75");
  });

  it("should format GBP equity prices with Pound symbol", () => {
    const formatted = formatEquityPrice("82.4", "GBP");
    assert.strictEqual(formatted, "£82.40");
  });

  it("should format JPY equity prices with 0 decimals", () => {
    const formatted = formatEquityPrice("2850", "JPY");
    assert.strictEqual(formatted, "¥2,850");
  });

  it("should format missing or null prices as a truthful dash", () => {
    assert.strictEqual(formatEquityPrice(null), "—");
    assert.strictEqual(formatEquityPrice(undefined), "—");
    assert.strictEqual(formatEquityPrice(""), "—");
    assert.strictEqual(formatEquityPrice("NaN"), "—");
  });

  it("should format signed absolute changes with correct currency symbols", () => {
    assert.strictEqual(formatAbsoluteChange("4.5", "USD"), "+$4.50");
    assert.strictEqual(formatAbsoluteChange("-1.25", "USD"), "-$1.25");
    assert.strictEqual(formatAbsoluteChange("0", "USD"), "$0.00");
    assert.strictEqual(formatAbsoluteChange("-35.5", "INR"), "-₹35.50");
    assert.strictEqual(formatAbsoluteChange(null), "—");
  });

  it("should format signed percentage changes safely", () => {
    assert.strictEqual(formatPercentageChange("2.456"), "+2.46%");
    assert.strictEqual(formatPercentageChange("-1.123"), "-1.12%");
    assert.strictEqual(formatPercentageChange("0"), "0.00%");
    assert.strictEqual(formatPercentageChange(null), "—");
    assert.strictEqual(formatPercentageChange("invalid"), "—");
  });

  it("should resolve human-readable equity subtypes", () => {
    assert.strictEqual(formatEquitySubtype("common_equity"), "Common Stock");
    assert.strictEqual(formatEquitySubtype("preferred_equity"), "Preferred Stock");
    assert.strictEqual(formatEquitySubtype("depositary_receipt"), "ADR / GDR");
    assert.strictEqual(formatEquitySubtype("unit"), "Unit");
    assert.strictEqual(formatEquitySubtype("warrant"), "Warrant");
    assert.strictEqual(formatEquitySubtype(null), "Common");
  });

  it("should return correct freshness badge classes", () => {
    const fresh = getFreshnessBadge("fresh");
    assert.strictEqual(fresh.label, "Fresh");
    assert.ok(fresh.className.includes("emerald"));

    const stale = getFreshnessBadge("stale");
    assert.strictEqual(stale.label, "Stale");
    assert.ok(stale.className.includes("amber"));

    const delayed = getFreshnessBadge("delayed");
    assert.strictEqual(delayed.label, "Delayed");
    assert.ok(delayed.className.includes("sky"));

    const unavailable = getFreshnessBadge("unavailable");
    assert.strictEqual(unavailable.label, "Unavailable");
  });

  it("should return directional color classes without throwing", () => {
    assert.ok(getDirectionColorClass("up").includes("emerald"));
    assert.ok(getDirectionColorClass("down").includes("rose"));
    assert.ok(getDirectionColorClass("flat").includes("zinc"));
    assert.ok(getDirectionColorClass("unknown").includes("zinc"));
    assert.ok(getDirectionColorClass(null).includes("zinc"));
  });

  it("should format observation timestamps or return dash on invalid", () => {
    const validIso = "2026-10-15T09:30:00Z";
    const formatted = formatObservationTime(validIso);
    assert.ok(formatted !== "—");
    assert.strictEqual(formatObservationTime(null), "—");
    assert.strictEqual(formatObservationTime("not-a-date"), "—");
  });

  it("should ensure the dedicated equities route page exists", () => {
    const pagePath = path.join(
      __dirname,
      "../src/app/(atlas)/markets/equities/page.tsx"
    );
    assert.ok(fs.existsSync(pagePath), "app/(atlas)/markets/equities/page.tsx must exist");
    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("EquitiesPage"), "Page must render EquitiesPage");
  });

  it("should verify strict design rules: no purple gradients and no buy/sell buttons", () => {
    const equitiesDir = path.join(__dirname, "../src/components/markets/equities");
    const files = fs.readdirSync(equitiesDir);

    for (const file of files) {
      if (!file.endsWith(".tsx")) continue;
      const content = fs.readFileSync(path.join(equitiesDir, file), "utf-8");

      assert.ok(
        !content.includes("from-purple") &&
          !content.includes("via-purple") &&
          !content.includes("to-purple"),
        `File ${file} must not contain purple gradients`
      );

      assert.ok(
        !content.includes("Buy Stock") &&
          !content.includes("Sell Stock") &&
          !content.includes("Place Order") &&
          !content.includes("Trade Now"),
        `File ${file} must not contain trading execution buttons`
      );
    }
  });

  it("should verify MarketsNavigationTabs contains canonical subviews and links", () => {
    const tabsFile = path.join(
      __dirname,
      "../src/components/markets/MarketsNavigationTabs.tsx"
    );
    assert.ok(fs.existsSync(tabsFile), "MarketsNavigationTabs.tsx must exist");
    const content = fs.readFileSync(tabsFile, "utf-8");

    assert.ok(content.includes("/markets"), "Tabs must link to /markets");
    assert.ok(content.includes("/markets/equities"), "Tabs must link to /markets/equities");
    assert.ok(
      content.includes("/markets/funds") || content.includes("Stage 58"),
      "ETFs & Funds must be linked to /markets/funds or marked Stage 58"
    );
    assert.ok(content.includes("Stage 59"), "FX must be marked Stage 59");
    assert.ok(content.includes("Stage 60"), "Crypto must be marked Stage 60");
  });
});
