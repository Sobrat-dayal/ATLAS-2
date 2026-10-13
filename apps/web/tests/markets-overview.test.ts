import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatMarketPrice,
  formatAbsoluteChange,
  formatPercentageChange,
  getChangeDirectionStyles,
  getFreshnessBadge,
  getDelayBadge,
  formatMarketTimestamp,
} from "../src/lib/markets/formatting";
import { MarketsOverviewItem } from "../src/lib/markets/types";
import * as marketsComponents from "../src/components/markets";

describe("Stage 56 - Markets Overview V1 Tests", () => {
  it("should confirm Markets components export cleanly from index.ts", () => {
    assert.ok(marketsComponents.MarketsOverviewPage, "MarketsOverviewPage must be exported");
    assert.ok(marketsComponents.MarketsHeader, "MarketsHeader must be exported");
    assert.ok(marketsComponents.MarketsCoverageSummary, "MarketsCoverageSummary must be exported");
    assert.ok(marketsComponents.MarketsGroupSelector, "MarketsGroupSelector must be exported");
    assert.ok(marketsComponents.FeaturedMarketInstruments, "FeaturedMarketInstruments must be exported");
    assert.ok(marketsComponents.MarketsInstrumentTable, "MarketsInstrumentTable must be exported");
    assert.ok(marketsComponents.MarketsEmptyState, "MarketsEmptyState must be exported");
  });

  it("should format index points without currency symbols", () => {
    const item: MarketsOverviewItem = {
      instrument_entity_id: "a1a2a3a4-b1b2-c1c2-d1d2-e1e2e3e4e5e6",
      display_name: "S&P 500",
      display_symbol: "^GSPC",
      instrument_category: "market_index",
      market_group: "benchmarks",
      value_kind: "points",
      quote_currency: "USD",
      quote_unit: "pts",
      last_price: "5864.67",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
      featured: true,
      display_order: 1,
    };

    const formatted = formatMarketPrice(item);
    assert.strictEqual(formatted.formattedValue, "5,864.67");
    assert.strictEqual(formatted.unitLabel, "pts");
    assert.ok(!formatted.formattedValue.includes("$"), "Index points must not include dollar sign");
  });

  it("should format foreign exchange rates with 4 decimal places", () => {
    const item: MarketsOverviewItem = {
      instrument_entity_id: "a1a2a3a4-b1b2-c1c2-d1d2-e1e2e3e4e5e6",
      display_name: "EUR / USD",
      display_symbol: "EUR/USD",
      instrument_category: "currency",
      market_group: "fx",
      value_kind: "rate",
      quote_currency: "USD",
      quote_unit: "USD per EUR",
      last_price: "1.0845",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
      featured: true,
      display_order: 30,
    };

    const formatted = formatMarketPrice(item);
    assert.strictEqual(formatted.formattedValue, "1.0845");
    assert.strictEqual(formatted.unitLabel, "USD per EUR");
  });

  it("should format bond yields with 3 decimal places and percentage", () => {
    const item: MarketsOverviewItem = {
      instrument_entity_id: "a1a2a3a4-b1b2-c1c2-d1d2-e1e2e3e4e5e6",
      display_name: "US 10-Year Yield",
      display_symbol: "^TNX",
      instrument_category: "bond",
      market_group: "bonds",
      value_kind: "yield",
      quote_currency: "USD",
      quote_unit: "% yield",
      last_price: "4.205",
      change_direction: "down",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
      featured: false,
      display_order: 60,
    };

    const formatted = formatMarketPrice(item);
    assert.strictEqual(formatted.formattedValue, "4.205%");
    assert.strictEqual(formatted.unitLabel, "% yield");
  });

  it("should format missing prices as '—' and never fabricated zero", () => {
    const item: MarketsOverviewItem = {
      instrument_entity_id: "a1a2a3a4-b1b2-c1c2-d1d2-e1e2e3e4e5e6",
      display_name: "Unobserved Security",
      display_symbol: "UNOBS",
      instrument_category: "equity",
      market_group: "equities",
      value_kind: "price",
      quote_currency: "USD",
      quote_unit: "USD",
      last_price: null,
      change_direction: "unknown",
      freshness_status: "unavailable",
      delivery_delay_status: "unknown",
      data_status: "no_quote",
      featured: false,
      display_order: 99,
    };

    const formatted = formatMarketPrice(item);
    assert.strictEqual(formatted.formattedValue, "—");
    assert.notStrictEqual(formatted.formattedValue, "0.00");
    assert.notStrictEqual(formatted.formattedValue, "$0.00");
  });

  it("should format signed absolute changes and percentage changes accurately", () => {
    const positiveItem: MarketsOverviewItem = {
      instrument_entity_id: "uuid-1",
      display_name: "Positive",
      instrument_category: "equity",
      market_group: "equities",
      value_kind: "price",
      quote_currency: "USD",
      last_price: "150.00",
      absolute_change: "2.50",
      percentage_change: "1.69",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
      featured: false,
      display_order: 1,
    };
    assert.strictEqual(formatAbsoluteChange(positiveItem), "+2.50");
    assert.strictEqual(formatPercentageChange(positiveItem), "+1.69%");

    const negativeItem: MarketsOverviewItem = {
      ...positiveItem,
      absolute_change: "-3.15",
      percentage_change: "-2.10",
      change_direction: "down",
    };
    assert.strictEqual(formatAbsoluteChange(negativeItem), "-3.15");
    assert.strictEqual(formatPercentageChange(negativeItem), "-2.10%");

    const missingItem: MarketsOverviewItem = {
      ...positiveItem,
      absolute_change: null,
      percentage_change: null,
      change_direction: "unknown",
    };
    assert.strictEqual(formatAbsoluteChange(missingItem), null);
    assert.strictEqual(formatPercentageChange(missingItem), null);
  });

  it("should provide correct freshness and delay badge information", () => {
    assert.strictEqual(getFreshnessBadge("fresh").label, "Current");
    assert.strictEqual(getFreshnessBadge("aging").label, "Aging");
    assert.strictEqual(getFreshnessBadge("stale").label, "Stale");
    assert.strictEqual(getFreshnessBadge("unavailable").label, "No Feed");

    const delayedBadge = getDelayBadge("delayed", 900);
    assert.strictEqual(delayedBadge.show, true);
    assert.strictEqual(delayedBadge.label, "15m Delayed");

    const realtimeBadge = getDelayBadge("realtime");
    assert.strictEqual(realtimeBadge.show, false);
  });

  it("should verify direction styles provide high contrast semantic colors", () => {
    assert.strictEqual(getChangeDirectionStyles("up").textColor, "text-emerald-400");
    assert.strictEqual(getChangeDirectionStyles("down").textColor, "text-rose-400");
    assert.strictEqual(getChangeDirectionStyles("flat").textColor, "text-zinc-400");
    assert.strictEqual(getChangeDirectionStyles("unknown").textColor, "text-zinc-500");
  });

  it("should verify no fabricated prices or purple gradients in production source", () => {
    const marketsDir = path.resolve(__dirname, "../src/components/markets");
    const files = fs.readdirSync(marketsDir);

    for (const file of files) {
      if (!file.endsWith(".tsx") && !file.endsWith(".ts")) continue;
      const content = fs.readFileSync(path.join(marketsDir, file), "utf-8");

      assert.ok(
        !content.includes("from-purple"),
        `Forbidden purple gradient in ${file}`
      );
      assert.ok(
        !content.includes("to-indigo"),
        `Forbidden purple/indigo gradient in ${file}`
      );
      assert.ok(
        !content.includes("dangerouslySetInnerHTML"),
        `Forbidden dangerous HTML in ${file}`
      );
    }
  });

  it("should format timestamps safely", () => {
    assert.strictEqual(formatMarketTimestamp(null), "—");
    assert.strictEqual(formatMarketTimestamp(undefined), "—");
    assert.strictEqual(formatMarketTimestamp("invalid-date"), "—");
    const valid = formatMarketTimestamp("2026-10-13T12:30:45Z");
    assert.ok(valid.includes(":"), "Should format valid timestamp string");
  });
});
