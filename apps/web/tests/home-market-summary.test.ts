import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  formatAbsoluteChange,
  formatMarketPrice,
  formatPercentageChange,
  getChangeDirectionStyles,
  getDelayBadge,
  getFreshnessBadge,
} from "../src/lib/home/market-summary-format";
import {
  HomeMarketSummaryItem,
} from "../src/lib/home/market-summary-types";
import { getWidgetDefinition } from "../src/lib/home/widget-registry";

describe("Stage 52 - Home Market Summary Formatting & Logic Tests", () => {
  it("should format index points without currency symbols", () => {
    const item: HomeMarketSummaryItem = {
      instrument_entity_id: "02ddbbd5-1c31-50e5-950c-e274ee794026",
      display_name: "S&P 500",
      display_symbol: "^GSPC",
      instrument_category: "market_index",
      value_kind: "points",
      quote_currency: "USD",
      quote_unit: "pts",
      last_price: "5050.50",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
    };

    const { formattedValue, unitLabel } = formatMarketPrice(item);
    assert.equal(formattedValue, "5,050.50");
    assert.equal(unitLabel, "pts");
    // Crucial: Must NOT contain "$" for an index points value
    assert.ok(!formattedValue.includes("$"));
  });

  it("should format equity ETF prices with correct currency", () => {
    const item: HomeMarketSummaryItem = {
      instrument_entity_id: "1be9be59-e962-5205-9543-c0d18b375b4b",
      display_name: "SPDR S&P 500 ETF",
      display_symbol: "SPY",
      instrument_category: "etf",
      value_kind: "price",
      quote_currency: "USD",
      quote_unit: "USD",
      last_price: "500.25",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
    };

    const { formattedValue, unitLabel } = formatMarketPrice(item);
    assert.equal(formattedValue, "$500.25");
    assert.equal(unitLabel, "USD");
  });

  it("should format foreign exchange rates with 4 decimal places", () => {
    const item: HomeMarketSummaryItem = {
      instrument_entity_id: "372e93b1-a67b-5c4a-9db7-28d8b9e67a68",
      display_name: "EUR / USD",
      display_symbol: "EUR/USD",
      instrument_category: "currency",
      value_kind: "rate",
      quote_currency: "USD",
      quote_unit: "USD per EUR",
      last_price: "1.0845",
      change_direction: "down",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
    };

    const { formattedValue, unitLabel } = formatMarketPrice(item);
    assert.equal(formattedValue, "1.0845");
    assert.equal(unitLabel, "USD per EUR");
  });

  it("should format commodity contracts with unit of measure", () => {
    const item: HomeMarketSummaryItem = {
      instrument_entity_id: "f459c55d-efbf-5573-9ea8-a3be8eb84fa8",
      display_name: "Brent Crude",
      display_symbol: "BZ=F",
      instrument_category: "commodity",
      value_kind: "price",
      quote_currency: "USD",
      quote_unit: "USD/bbl",
      last_price: "78.40",
      change_direction: "flat",
      freshness_status: "aging",
      delivery_delay_status: "delayed",
      data_status: "available",
    };

    const { formattedValue, unitLabel } = formatMarketPrice(item);
    assert.equal(formattedValue, "$78.40");
    assert.equal(unitLabel, "USD/bbl");
  });

  it("should format missing prices as Unavailable and never zero", () => {
    const item: HomeMarketSummaryItem = {
      instrument_entity_id: "82eaee06-d0e5-5e60-84c6-f755ee14e0bc",
      display_name: "Bitcoin",
      display_symbol: "BTC/USD",
      instrument_category: "crypto_asset",
      value_kind: "price",
      quote_currency: "USD",
      quote_unit: "USD",
      last_price: null,
      change_direction: "unknown",
      freshness_status: "unavailable",
      delivery_delay_status: "unknown",
      data_status: "no_quote",
    };

    const { formattedValue } = formatMarketPrice(item);
    assert.equal(formattedValue, "Unavailable");
    // Crucial: Must NEVER format missing quote as "0.00" or "$0.00"
    assert.ok(!formattedValue.includes("0"));
  });

  it("should format signed absolute changes accurately", () => {
    const posItem: HomeMarketSummaryItem = {
      instrument_entity_id: "1",
      display_name: "Pos",
      instrument_category: "equity",
      value_kind: "price",
      absolute_change: "12.40",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
    };
    assert.equal(formatAbsoluteChange(posItem), "+12.40");

    const negItem: HomeMarketSummaryItem = {
      ...posItem,
      absolute_change: "-8.25",
      change_direction: "down",
    };
    assert.equal(formatAbsoluteChange(negItem), "-8.25");

    const zeroItem: HomeMarketSummaryItem = {
      ...posItem,
      absolute_change: "0.00",
      change_direction: "flat",
    };
    assert.equal(formatAbsoluteChange(zeroItem), "0.00");

    const nullItem: HomeMarketSummaryItem = {
      ...posItem,
      absolute_change: null,
      change_direction: "unknown",
    };
    assert.equal(formatAbsoluteChange(nullItem), null);
  });

  it("should format signed percentage changes accurately", () => {
    const posItem: HomeMarketSummaryItem = {
      instrument_entity_id: "1",
      display_name: "Pos",
      instrument_category: "equity",
      value_kind: "price",
      percentage_change: "1.24",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
    };
    assert.equal(formatPercentageChange(posItem), "+1.24%");

    const negItem: HomeMarketSummaryItem = {
      ...posItem,
      percentage_change: "-0.83",
      change_direction: "down",
    };
    assert.equal(formatPercentageChange(negItem), "-0.83%");

    const zeroItem: HomeMarketSummaryItem = {
      ...posItem,
      percentage_change: "0.00",
      change_direction: "flat",
    };
    assert.equal(formatPercentageChange(zeroItem), "0.00%");

    const nullItem: HomeMarketSummaryItem = {
      ...posItem,
      percentage_change: null,
      change_direction: "unknown",
    };
    assert.equal(formatPercentageChange(nullItem), null);
  });

  it("should provide correct styling for movement directions", () => {
    assert.ok(getChangeDirectionStyles("up").textColor.includes("emerald"));
    assert.ok(getChangeDirectionStyles("down").textColor.includes("rose"));
    assert.ok(getChangeDirectionStyles("flat").textColor.includes("zinc"));
    assert.ok(getChangeDirectionStyles("unknown").textColor.includes("zinc"));
  });

  it("should provide correct freshness badges matching Stage 44 semantics", () => {
    assert.equal(getFreshnessBadge("fresh").label, "Current");
    assert.equal(getFreshnessBadge("aging").label, "Aging");
    assert.equal(getFreshnessBadge("stale").label, "Stale");
    assert.equal(getFreshnessBadge("unavailable").label, "No Feed");
  });

  it("should provide delay badge information", () => {
    assert.deepEqual(getDelayBadge("delayed", 900), { label: "15m Delayed", show: true });
    assert.deepEqual(getDelayBadge("realtime", 0), { label: "", show: false });
    assert.deepEqual(getDelayBadge("unknown", null), { label: "", show: false });
  });

  it("should confirm widget registry marks home-market-summary as implemented", () => {
    const widget = getWidgetDefinition("home-market-summary");
    assert.ok(widget);
    assert.equal(widget?.status, "implemented");
    assert.equal(widget?.defaultState, "available");
    assert.equal(widget?.targetStage, 52);
  });

  it("should format multi-currency prices with correct symbols and currency labels", () => {
    // 1. EUR
    const eurItem: HomeMarketSummaryItem = {
      instrument_entity_id: "eur-id",
      display_name: "Euro Security",
      instrument_category: "equity",
      value_kind: "price",
      quote_currency: "EUR",
      last_price: "45.50",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
    };
    assert.equal(formatMarketPrice(eurItem).formattedValue, "€45.50");
    assert.equal(formatMarketPrice(eurItem).unitLabel, "EUR");

    // 2. GBP
    const gbpItem: HomeMarketSummaryItem = {
      ...eurItem,
      quote_currency: "GBP",
      last_price: "120.00",
    };
    assert.equal(formatMarketPrice(gbpItem).formattedValue, "£120.00");

    // 3. JPY
    const jpyItem: HomeMarketSummaryItem = {
      ...eurItem,
      quote_currency: "JPY",
      last_price: "3500.00",
    };
    assert.equal(formatMarketPrice(jpyItem).formattedValue, "¥3,500.00");

    // 4. INR
    const inrItem: HomeMarketSummaryItem = {
      ...eurItem,
      quote_currency: "INR",
      last_price: "2450.75",
    };
    assert.equal(formatMarketPrice(inrItem).formattedValue, "₹2,450.75");

    // 5. CHF
    const chfItem: HomeMarketSummaryItem = {
      ...eurItem,
      quote_currency: "CHF",
      last_price: "110.20",
    };
    assert.equal(formatMarketPrice(chfItem).formattedValue, "CHF 110.20");
  });

  it("should apply tiered precision formatting for cryptocurrency prices", () => {
    // High-value crypto (>= 100): 2 decimals
    const btcItem: HomeMarketSummaryItem = {
      instrument_entity_id: "btc-id",
      display_name: "Bitcoin",
      instrument_category: "crypto_asset",
      value_kind: "price",
      quote_currency: "USD",
      last_price: "67500.25",
      change_direction: "up",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      data_status: "available",
    };
    assert.equal(formatMarketPrice(btcItem).formattedValue, "$67,500.25");

    // Mid-value crypto (1 to 100): 4 decimals
    const midCrypto: HomeMarketSummaryItem = {
      ...btcItem,
      last_price: "15.2530",
    };
    assert.equal(formatMarketPrice(midCrypto).formattedValue, "$15.2530");

    // Micro-value crypto (< 1): 6 decimals
    const microCrypto: HomeMarketSummaryItem = {
      ...btcItem,
      last_price: "0.045123",
    };
    assert.equal(formatMarketPrice(microCrypto).formattedValue, "$0.045123");
  });

  it("should verify snapshot race condition ordering logic", () => {
    let lastAcceptedTime = 0;
    const acceptSnapshot = (timestampIso: string) => {
      const timeMs = new Date(timestampIso).getTime();
      if (timeMs >= lastAcceptedTime) {
        lastAcceptedTime = timeMs;
        return true;
      }
      return false;
    };

    // First snapshot at t=100 is accepted
    assert.equal(acceptSnapshot("2026-10-12T10:00:00Z"), true);
    assert.equal(lastAcceptedTime, new Date("2026-10-12T10:00:00Z").getTime());

    // Live update / refetch snapshot at t=200 is accepted
    assert.equal(acceptSnapshot("2026-10-12T10:05:00Z"), true);

    // Stale/delayed response arriving from t=150 is rejected (cannot overwrite newer state)
    assert.equal(acceptSnapshot("2026-10-12T10:02:00Z"), false);

    // Same or newer timestamp at t=205 is accepted
    assert.equal(acceptSnapshot("2026-10-12T10:06:00Z"), true);
  });
});

describe("Stage 52 - No Fake Data Static Code Verification", () => {
  it("should verify HomeMarketSummary and card components do not contain hardcoded stock prices", () => {
    const cardPath = path.resolve(__dirname, "../src/components/home/MarketSummaryInstrumentCard.tsx");
    const summaryPath = path.resolve(__dirname, "../src/components/home/HomeMarketSummary.tsx");

    const cardContent = fs.readFileSync(cardPath, "utf-8");
    const summaryContent = fs.readFileSync(summaryPath, "utf-8");

    // Must not contain hardcoded stock prices or fake percentages
    const forbiddenPatterns = [
      /\$5,\d{3}\.\d{2}/, // e.g. $5,000.00
      /\+2\.34%/,
      /-1\.15%/,
      /"AAPL"/,
      /"MSFT"/,
      /"5000\.00"/,
    ];

    for (const pattern of forbiddenPatterns) {
      assert.ok(
        !pattern.test(cardContent),
        `MarketSummaryInstrumentCard.tsx contains forbidden pattern: ${pattern}`
      );
      assert.ok(
        !pattern.test(summaryContent),
        `HomeMarketSummary.tsx contains forbidden pattern: ${pattern}`
      );
    }
  });

  it("should verify no third-party iframe price widgets or direct provider calls in web", () => {
    const summaryPath = path.resolve(__dirname, "../src/components/home/HomeMarketSummary.tsx");
    const apiPath = path.resolve(__dirname, "../src/lib/home/market-summary-api.ts");

    const summaryContent = fs.readFileSync(summaryPath, "utf-8");
    const apiContent = fs.readFileSync(apiPath, "utf-8");

    assert.ok(!summaryContent.includes("<iframe"), "Cannot contain iframe widgets");
    assert.ok(!summaryContent.includes("tradingview"), "Cannot contain external TradingView widgets");
    assert.ok(!apiContent.includes("finnhub"), "Cannot call third-party providers from browser");
    assert.ok(!apiContent.includes("polygon.io"), "Cannot call third-party providers from browser");
  });
});
