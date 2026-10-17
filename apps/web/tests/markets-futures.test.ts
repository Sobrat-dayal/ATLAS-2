import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatContractMonth,
  formatContractSize,
  formatFuturesPrice,
  formatOpenInterest,
  formatPriceChange,
  formatSettlementType,
  formatTickSpecs,
  formatTicksChange,
  formatVolume,
} from "../src/lib/markets/futures/formatting";
import * as futuresComponents from "../src/components/markets/futures";
import * as marketsComponents from "../src/components/markets";

describe("Stage 62 - Futures & Commodities Markets V1 Tests", () => {
  it("should confirm Futures components export cleanly", () => {
    assert.ok(futuresComponents.FuturesMarketsPage, "FuturesMarketsPage must be exported");
    assert.ok(futuresComponents.FuturesHeader, "FuturesHeader must be exported");
    assert.ok(futuresComponents.FuturesCoverageSummary, "FuturesCoverageSummary must be exported");
    assert.ok(futuresComponents.FuturesMarketTabs, "FuturesMarketTabs must be exported");
    assert.ok(futuresComponents.FuturesContractFilters, "FuturesContractFilters must be exported");
    assert.ok(futuresComponents.FuturesContractTable, "FuturesContractTable must be exported");
    assert.ok(futuresComponents.FuturesContractRow, "FuturesContractRow must be exported");
    assert.ok(futuresComponents.FuturesContractInspector, "FuturesContractInspector must be exported");
    assert.ok(futuresComponents.CommodityDirectoryTable, "CommodityDirectoryTable must be exported");
    assert.ok(futuresComponents.SpotBenchmarkDirectoryTable, "SpotBenchmarkDirectoryTable must be exported");
    assert.ok(futuresComponents.FuturesEmptyState, "FuturesEmptyState must be exported");
    assert.ok(marketsComponents.MarketsNavigationTabs, "MarketsNavigationTabs must be exported from components/markets");
  });

  it("should format futures prices preserving quote units and negative prices", () => {
    // Standard USD crude oil quotation
    assert.strictEqual(formatFuturesPrice("69.45", "USD per barrel", "USD"), "$69.45");

    // Legitimate negative futures price (historical WTI oil)
    assert.strictEqual(formatFuturesPrice("-37.63", "USD per barrel", "USD"), "-$37.63");

    // US Cents per bushel (CBOT Corn)
    assert.strictEqual(formatFuturesPrice("426.50", "US cents per bushel", "USD"), "426.50 ¢");

    // Index points (E-mini S&P 500)
    assert.strictEqual(formatFuturesPrice("5872.25", "Index points", "USD"), "5,872.25 pts");

    // Natural Gas (USD per MMBtu with 3 decimals)
    assert.strictEqual(formatFuturesPrice("3.142", "USD per MMBtu", "USD"), "$3.142");

    // Copper (USD per pound with 4 decimals)
    assert.strictEqual(formatFuturesPrice("4.3820", "USD per pound", "USD"), "$4.3820");

    // Gold (high precision USD per troy oz)
    assert.strictEqual(formatFuturesPrice("2685.40", "USD per troy oz", "USD"), "$2,685.40");

    // Null/undefined handling
    assert.strictEqual(formatFuturesPrice(null), "—");
    assert.strictEqual(formatFuturesPrice(undefined), "—");
  });

  it("should format qualified price changes and suppress percentage change on nonpositive reference", () => {
    // Normal positive reference: displays both absolute change and percentage change
    const normalChange = formatPriceChange("-0.70", "-0.997", "USD per barrel");
    assert.ok(normalChange.includes("-$0.70"), "Must include absolute change");
    assert.ok(normalChange.includes("(-1.00%)"), "Must include rounded percentage change");

    // Critical Requirement: when percentage change is suppressed (null) due to nonpositive reference
    const negativeRefChange = formatPriceChange("+15.00", null, "USD per barrel");
    assert.strictEqual(negativeRefChange, "+$15.00", "Must show absolute change without bogus percentage");

    // Cents per bushel change
    const grainChange = formatPriceChange("4.25", "1.01", "US cents per bushel");
    assert.ok(grainChange.includes("+4.25 ¢"));

    // Null change
    assert.strictEqual(formatPriceChange(null, null), "—");
  });

  it("should format ticks change correctly", () => {
    assert.strictEqual(formatTicksChange("70.0"), "+70.0 ticks");
    assert.strictEqual(formatTicksChange("-12.5"), "-12.5 ticks");
    assert.strictEqual(formatTicksChange(null), "—");
  });

  it("should format contract month code and year into human readable string", () => {
    assert.strictEqual(formatContractMonth("2026-12"), "Dec 2026");
    assert.strictEqual(formatContractMonth("2027-01"), "Jan 2027");
    assert.strictEqual(formatContractMonth("2027-03"), "Mar 2027");
    assert.strictEqual(formatContractMonth(""), "—");
  });

  it("should format contract size and tick specifications", () => {
    assert.strictEqual(formatContractSize("1000", "barrels"), "1,000 barrels");
    assert.strictEqual(formatContractSize("5000", "bushels"), "5,000 bushels");

    assert.strictEqual(formatTickSpecs("0.01", "10.00", "USD"), "0.01 (USD $10.00)");
    assert.strictEqual(formatTickSpecs("0.25", "12.50", "USD"), "0.25 (USD $12.50)");
  });

  it("should format settlement types distinguishing physical vs cash", () => {
    const phys = formatSettlementType("physical");
    assert.strictEqual(phys.label, "Physical Delivery");
    assert.ok(phys.badgeClass.includes("amber"));

    const cash = formatSettlementType("cash");
    assert.strictEqual(cash.label, "Cash Settled");
    assert.ok(cash.badgeClass.includes("blue"));
  });

  it("should format volume and open interest counts", () => {
    assert.strictEqual(formatVolume(284500), "284,500");
    assert.strictEqual(formatVolume(null), "—");

    assert.strictEqual(formatOpenInterest(412300, "2026-10-14"), "412,300 (as of 2026-10-14)");
    assert.strictEqual(formatOpenInterest(null), "—");
  });

  it("should ensure the dedicated /markets/futures route page exists and renders FuturesMarketsPage", () => {
    const pagePath = path.resolve(__dirname, "../src/app/(atlas)/markets/futures/page.tsx");
    assert.ok(fs.existsSync(pagePath), "app/(atlas)/markets/futures/page.tsx must exist");
    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("FuturesMarketsPage"), "Page must render FuturesMarketsPage component");
    assert.ok(content.includes("Futures & Commodities Markets | ATLAS"), "Page metadata title must be correct");
  });

  it("should verify MarketsNavigationTabs links to /markets/futures and marks it implemented", () => {
    const navPath = path.resolve(__dirname, "../src/components/markets/MarketsNavigationTabs.tsx");
    const content = fs.readFileSync(navPath, "utf-8");
    assert.ok(
      content.includes(`{ id: "futures", label: "Futures & Commodities", href: "/markets/futures", isImplemented: true }`),
      "MarketsNavigationTabs must link to /markets/futures with isImplemented: true"
    );
  });

  it("should verify strict financial design rules: no purple gradients and no buy/sell trading actions", () => {
    const inspectorPath = path.resolve(__dirname, "../src/components/markets/futures/FuturesContractInspector.tsx");
    const inspectorContent = fs.readFileSync(inspectorPath, "utf-8");

    assert.strictEqual(inspectorContent.includes("from-purple"), false, "No purple gradients allowed");
    assert.strictEqual(inspectorContent.includes("bg-purple"), false, "No purple colors allowed");

    // Check that there are no executable trading buttons (Buy, Sell, Place Order)
    assert.strictEqual(inspectorContent.includes("<button>Buy</button>"), false);
    assert.strictEqual(inspectorContent.includes("<button>Sell</button>"), false);
    assert.strictEqual(inspectorContent.includes("Place Order"), false);

    // Verify institutional non-executable disclaimer
    assert.ok(
      inspectorContent.includes("Derivatives Terminal Notice"),
      "Inspector must include read-only derivatives disclaimer"
    );
  });
});
