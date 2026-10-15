import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatFxRate,
  formatFxSpread,
  formatFxSpreadBps,
  formatFxSpreadPips,
  formatFxChange,
  formatRateKind,
  formatFxFreshnessBadge,
  formatMoneyAmount,
  formatObservedTimestamp,
} from "../src/lib/markets/fx/formatting";
import * as fxComponents from "../src/components/markets/fx";
import * as marketsComponents from "../src/components/markets";

describe("Stage 59 - FX Markets V1 Tests", () => {
  it("should confirm FX components export cleanly", () => {
    assert.ok(fxComponents.FxPage, "FxPage must be exported");
    assert.ok(fxComponents.FxHeader, "FxHeader must be exported");
    assert.ok(
      fxComponents.FxCoverageSummary,
      "FxCoverageSummary must be exported"
    );
    assert.ok(fxComponents.FxPairFilters, "FxPairFilters must be exported");
    assert.ok(
      fxComponents.FxPairDirectoryTable,
      "FxPairDirectoryTable must be exported"
    );
    assert.ok(
      fxComponents.FxPairDirectoryRow,
      "FxPairDirectoryRow must be exported"
    );
    assert.ok(fxComponents.FxPairInspector, "FxPairInspector must be exported");
    assert.ok(
      fxComponents.FxCurrencyConverter,
      "FxCurrencyConverter must be exported"
    );
    assert.ok(fxComponents.FxEmptyState, "FxEmptyState must be exported");
    assert.ok(
      marketsComponents.MarketsNavigationTabs,
      "MarketsNavigationTabs must be exported from components/markets"
    );
  });

  it("should format exchange rates with correct quotation precision", () => {
    // 4 decimals for standard pairs
    assert.strictEqual(formatFxRate("1.0850", 4), "1.0850");
    assert.strictEqual(formatFxRate("1.2645", 4), "1.2645");

    // 2 decimals for JPY / INR pairs
    assert.strictEqual(formatFxRate("153.25", 2), "153.25");
    assert.strictEqual(formatFxRate("84.42", 2), "84.42");

    // Missing / null rates must return a truthful dash
    assert.strictEqual(formatFxRate(null), "—");
    assert.strictEqual(formatFxRate(undefined), "—");
    assert.strictEqual(formatFxRate(""), "—");
    assert.strictEqual(formatFxRate("invalid"), "—");
  });

  it("should format absolute spread and basis points accurately", () => {
    // Absolute spread
    assert.strictEqual(formatFxSpread("0.0002", 4), "0.0002");
    assert.strictEqual(formatFxSpread("0.03", 2), "0.03");
    assert.strictEqual(formatFxSpread(null), "—");

    // Basis points (bps)
    assert.strictEqual(formatFxSpreadBps("1.84"), "1.8 bps");
    assert.strictEqual(formatFxSpreadBps("10.5"), "10.5 bps");
    assert.strictEqual(formatFxSpreadBps(null), "—");

    // Pips
    assert.strictEqual(formatFxSpreadPips("2.0"), "2.0 pips");
    assert.strictEqual(formatFxSpreadPips("0.5"), "0.5 pips");
    assert.strictEqual(formatFxSpreadPips(null), "—");
  });

  it("should format signed percentage returns with appropriate color classes", () => {
    const pos = formatFxChange("0.45");
    assert.strictEqual(pos.text, "+0.45%");
    assert.strictEqual(pos.isPositive, true);
    assert.strictEqual(pos.colorClass, "text-emerald-400");

    const neg = formatFxChange("-0.32");
    assert.strictEqual(neg.text, "-0.32%");
    assert.strictEqual(neg.isNegative, true);
    assert.strictEqual(neg.colorClass, "text-rose-400");

    const zero = formatFxChange("0.00");
    assert.strictEqual(zero.text, "0.00%");
    assert.strictEqual(zero.colorClass, "text-[var(--atlas-text-secondary)]");

    const missing = formatFxChange(null);
    assert.strictEqual(missing.text, "—");
  });

  it("should format rate kinds distinctly without conflation", () => {
    assert.strictEqual(formatRateKind("SPOT_BID_ASK"), "Spot Bid/Ask");
    assert.strictEqual(formatRateKind("INDICATIVE_MID"), "Indicative Mid");
    assert.strictEqual(formatRateKind("REFERENCE_RATE"), "Reference Rate");
    assert.strictEqual(formatRateKind("LAST_TRADE"), "Last Observed Trade");
    assert.strictEqual(formatRateKind("CROSSED_INVALID"), "Crossed (Invalid)");
    assert.strictEqual(formatRateKind("ARITHMETIC_IDENTITY"), "Identity (1:1)");
    assert.strictEqual(formatRateKind("UNKNOWN"), "Unknown");
  });

  it("should format freshness status badges", () => {
    const live = formatFxFreshnessBadge("FRESH");
    assert.strictEqual(live.label, "Live / Fresh");
    assert.ok(live.badgeClass.includes("text-emerald-400"));

    const stale = formatFxFreshnessBadge("STALE");
    assert.strictEqual(stale.label, "Stale");
    assert.ok(stale.badgeClass.includes("text-amber-400"));

    const crossed = formatFxFreshnessBadge("INCONSISTENT");
    assert.strictEqual(crossed.label, "Crossed");
    assert.ok(crossed.badgeClass.includes("text-rose-400"));
  });

  it("should format money amounts using destination currency minor units", () => {
    // USD (2 minor units)
    assert.strictEqual(formatMoneyAmount("108.489", 2), "108.49");
    assert.strictEqual(formatMoneyAmount("108.489", 2, "$"), "$108.49");

    // JPY (0 minor units)
    assert.strictEqual(formatMoneyAmount("15328.45", 0), "15,328");
    assert.strictEqual(formatMoneyAmount("15328.45", 0, "¥"), "¥15,328");

    // Missing amounts
    assert.strictEqual(formatMoneyAmount(null), "—");
    assert.strictEqual(formatMoneyAmount(""), "—");
  });

  it("should format observation timestamps safely", () => {
    const formatted = formatObservedTimestamp("2026-10-15T12:30:00Z");
    assert.ok(formatted !== "—", "Valid timestamp must be formatted");
    assert.strictEqual(formatObservedTimestamp(null), "—");
    assert.strictEqual(formatObservedTimestamp("invalid"), "—");
  });

  it("should ensure the dedicated /markets/fx route page exists and renders FxPage", () => {
    const pagePath = path.join(
      __dirname,
      "../src/app/(atlas)/markets/fx/page.tsx"
    );
    assert.ok(fs.existsSync(pagePath), "markets/fx/page.tsx route file must exist");
    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("FxPage"), "Page must render FxPage component");
    assert.ok(
      content.includes("FX Markets | ATLAS"),
      "Page metadata must be Foreign Exchange"
    );
  });

  it("should verify MarketsNavigationTabs links to /markets/fx and marks it implemented", () => {
    const tabsPath = path.join(
      __dirname,
      "../src/components/markets/MarketsNavigationTabs.tsx"
    );
    const content = fs.readFileSync(tabsPath, "utf-8");
    assert.ok(
      content.includes('id: "fx"'),
      "MarketsNavigationTabs must contain fx tab"
    );
    assert.ok(
      content.includes('href: "/markets/fx"'),
      "MarketsNavigationTabs must link fx tab to /markets/fx"
    );
    assert.ok(
      content.includes('isImplemented: true'),
      "MarketsNavigationTabs must mark fx tab as implemented"
    );
  });

  it("should verify strict financial design rules: no purple gradients and no buy/sell trading actions", () => {
    const componentsDir = path.join(__dirname, "../src/components/markets/fx");
    const files = fs.readdirSync(componentsDir);

    for (const file of files) {
      if (!file.endsWith(".tsx")) continue;
      const content = fs.readFileSync(path.join(componentsDir, file), "utf-8");

      assert.ok(
        !content.includes("from-purple-") && !content.includes("to-purple-"),
        `File ${file} must not contain forbidden purple gradients`
      );
      assert.ok(
        !content.includes("Buy Currency") &&
          !content.includes("Sell Currency") &&
          !content.includes("Execute FX") &&
          !content.includes("Set Stop Loss"),
        `File ${file} must not contain broker/trading execution controls`
      );
    }
  });

  it("should verify non-executable disclaimer is present in inspector and converter", () => {
    const inspectorPath = path.join(
      __dirname,
      "../src/components/markets/fx/FxPairInspector.tsx"
    );
    const inspectorContent = fs.readFileSync(inspectorPath, "utf-8");
    assert.ok(
      inspectorContent.includes("indicative over-the-counter market observations"),
      "Inspector must disclose indicative OTC market reality"
    );

    const converterPath = path.join(
      __dirname,
      "../src/components/markets/fx/FxCurrencyConverter.tsx"
    );
    const converterContent = fs.readFileSync(converterPath, "utf-8");
    assert.ok(
      converterContent.includes("Non-Executable") ||
        converterContent.includes("Read-Only"),
      "Converter must explicitly disclose read-only / non-executable status"
    );
  });
});
