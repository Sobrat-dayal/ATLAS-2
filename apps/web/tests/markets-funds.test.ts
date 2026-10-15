import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatFundPrice,
  formatFundNAV,
  formatExpenseRatio,
  formatAUM,
  formatFundChange,
  formatValuationDate,
} from "../src/lib/markets/funds/formatting";
import * as fundsComponents from "../src/components/markets/funds";
import * as marketsComponents from "../src/components/markets";

describe("Stage 58 - ETFs & Funds Markets V1 Tests", () => {
  it("should confirm Funds components export cleanly", () => {
    assert.ok(fundsComponents.FundsPage, "FundsPage must be exported");
    assert.ok(fundsComponents.FundsHeader, "FundsHeader must be exported");
    assert.ok(
      fundsComponents.FundCoverageSummary,
      "FundCoverageSummary must be exported"
    );
    assert.ok(
      fundsComponents.FundTypeSelector,
      "FundTypeSelector must be exported"
    );
    assert.ok(
      fundsComponents.FundDirectoryFilters,
      "FundDirectoryFilters must be exported"
    );
    assert.ok(
      fundsComponents.FundDirectoryTable,
      "FundDirectoryTable must be exported"
    );
    assert.ok(
      fundsComponents.FundDirectoryRow,
      "FundDirectoryRow must be exported"
    );
    assert.ok(fundsComponents.FundInspector, "FundInspector must be exported");
    assert.ok(fundsComponents.FundEmptyState, "FundEmptyState must be exported");
    assert.ok(
      marketsComponents.MarketsNavigationTabs,
      "MarketsNavigationTabs must be exported from components/markets"
    );
  });

  it("should format exchange market prices with 2 decimal places and currency", () => {
    const formatted = formatFundPrice("588.2", "USD");
    assert.strictEqual(formatted, "588.20 USD");

    const noCcy = formatFundPrice("125.75");
    assert.strictEqual(noCcy, "125.75");

    assert.strictEqual(formatFundPrice(null), "—");
    assert.strictEqual(formatFundPrice(undefined), "—");
    assert.strictEqual(formatFundPrice(""), "—");
    assert.strictEqual(formatFundPrice("invalid"), "—");
  });

  it("should format official NAV preserving 4 decimal places without conflating with market price", () => {
    const formatted = formatFundNAV("585.4", "USD");
    assert.strictEqual(formatted, "585.40 USD");

    const detailedNAV = formatFundNAV("585.4025", "USD");
    assert.strictEqual(detailedNAV, "585.4025 USD");

    assert.strictEqual(formatFundNAV(null), "—");
    assert.strictEqual(formatFundNAV(undefined), "—");
    assert.strictEqual(formatFundNAV(""), "—");
  });

  it("should format expense ratio accurately and never display missing fee as 0.00%", () => {
    // 0.09% expense ratio
    assert.strictEqual(formatExpenseRatio("0.09", "percentage"), "0.09%");
    assert.strictEqual(formatExpenseRatio("0.03", "percentage"), "0.03%");

    // Fraction scale: 0.0009 -> 0.09%
    assert.strictEqual(formatExpenseRatio("0.0009", "fraction"), "0.09%");

    // Missing expense ratio MUST return "—", never "0.00%"
    assert.strictEqual(formatExpenseRatio(null), "—");
    assert.strictEqual(formatExpenseRatio(undefined), "—");
    assert.strictEqual(formatExpenseRatio(""), "—");
    assert.strictEqual(formatExpenseRatio("invalid"), "—");
  });

  it("should format AUM with compact abbreviations and explicit currency", () => {
    // Billions
    assert.strictEqual(formatAUM("540200000000", "USD"), "540.20B USD");
    assert.strictEqual(formatAUM("31500000000", "USD"), "31.50B USD");

    // Millions
    assert.strictEqual(formatAUM("1850000000", "USD"), "1.85B USD");
    assert.strictEqual(formatAUM("850000000", "USD"), "850.00M USD");

    // Missing AUM
    assert.strictEqual(formatAUM(null), "—");
    assert.strictEqual(formatAUM("0"), "—");
    assert.strictEqual(formatAUM(undefined), "—");
  });

  it("should format fund market price changes with appropriate sign and color class", () => {
    const positive = formatFundChange("0.45");
    assert.strictEqual(positive.text, "+0.45%");
    assert.strictEqual(positive.isPositive, true);
    assert.ok(positive.colorClass.includes("emerald"));

    const negative = formatFundChange("-1.12");
    assert.strictEqual(negative.text, "-1.12%");
    assert.strictEqual(negative.isNegative, true);
    assert.ok(negative.colorClass.includes("rose"));

    const flat = formatFundChange("0.00");
    assert.strictEqual(flat.text, "0.00%");
    assert.strictEqual(flat.isPositive, false);
    assert.strictEqual(flat.isNegative, false);

    const missing = formatFundChange(null);
    assert.strictEqual(missing.text, "—");
    assert.strictEqual(missing.isPositive, false);
    assert.strictEqual(missing.isNegative, false);
  });

  it("should format valuation dates safely and truthfully", () => {
    const formatted = formatValuationDate("2026-03-30");
    assert.ok(formatted.includes("2026"));
    assert.strictEqual(formatValuationDate(null), "Unavailable");
    assert.strictEqual(formatValuationDate(""), "Unavailable");
  });

  it("should ensure the dedicated /markets/funds route page exists and renders FundsPage", () => {
    const pagePath = path.join(
      __dirname,
      "../src/app/(atlas)/markets/funds/page.tsx"
    );
    assert.ok(fs.existsSync(pagePath), "app/(atlas)/markets/funds/page.tsx must exist");
    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("FundsPage"), "Route must render FundsPage");
    assert.ok(content.includes("ETFs & Funds"), "Metadata title must reference ETFs & Funds");
  });

  it("should verify MarketsNavigationTabs links to /markets/funds and marks it implemented", () => {
    const tabsFile = path.join(
      __dirname,
      "../src/components/markets/MarketsNavigationTabs.tsx"
    );
    assert.ok(fs.existsSync(tabsFile), "MarketsNavigationTabs.tsx must exist");
    const content = fs.readFileSync(tabsFile, "utf-8");

    assert.ok(content.includes("/markets/funds"), "Tabs must link to /markets/funds");
    assert.ok(
      content.includes('id: "etfs"') && content.includes("isImplemented: true"),
      "ETFs & Funds tab must have isImplemented: true"
    );
  });

  it("should verify strict financial design rules: no purple gradients and no buy/sell trading actions", () => {
    const fundsDir = path.join(__dirname, "../src/components/markets/funds");
    const files = fs.readdirSync(fundsDir);

    for (const file of files) {
      if (!file.endsWith(".tsx")) continue;
      const content = fs.readFileSync(path.join(fundsDir, file), "utf-8");

      assert.ok(
        !content.includes("from-purple") &&
          !content.includes("via-purple") &&
          !content.includes("to-purple"),
        `File ${file} must not contain purple gradients`
      );

      assert.ok(
        !content.includes("Buy Fund") &&
          !content.includes("Sell Fund") &&
          !content.includes("Place Order") &&
          !content.includes("Trade Now") &&
          !content.includes("Buy ETF"),
        `File ${file} must not contain execution trading buttons`
      );

      assert.ok(
        !content.includes("Top Pick") &&
          !content.includes("Strong Buy") &&
          !content.includes("Guaranteed Return"),
        `File ${file} must not contain fake investment advice or AI rankings`
      );
    }
  });
});
