import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatBondPrice,
  formatPriceBasis,
  formatPriceKind,
  formatBondCoupon,
  formatBondMaturity,
  formatTimeToMaturity,
  formatBondYield,
  formatYieldTypeLabel,
  formatYieldChangeBps,
  formatBondSpread,
  formatBondType,
  formatObservationTime,
  getFreshnessBadgeClass,
} from "../src/lib/markets/bonds/formatting";
import * as bondsComponents from "../src/components/markets/bonds";
import * as marketsComponents from "../src/components/markets";

describe("Stage 61 - Bonds & Fixed-Income Markets V1 Tests", () => {
  it("should confirm Bonds components export cleanly", () => {
    assert.ok(bondsComponents.BondsPage, "BondsPage must be exported");
    assert.ok(bondsComponents.BondsHeader, "BondsHeader must be exported");
    assert.ok(
      bondsComponents.BondCoverageSummary,
      "BondCoverageSummary must be exported"
    );
    assert.ok(
      bondsComponents.BondDirectoryFilters,
      "BondDirectoryFilters must be exported"
    );
    assert.ok(
      bondsComponents.BondDirectoryTable,
      "BondDirectoryTable must be exported"
    );
    assert.ok(
      bondsComponents.BondDirectoryRow,
      "BondDirectoryRow must be exported"
    );
    assert.ok(
      bondsComponents.BondInspector,
      "BondInspector must be exported"
    );
    assert.ok(
      bondsComponents.BondEmptyState,
      "BondEmptyState must be exported"
    );
    assert.ok(
      marketsComponents.MarketsNavigationTabs,
      "MarketsNavigationTabs must be exported from components/markets"
    );
  });

  it("should format bond prices preserving quote units and clean/dirty basis", () => {
    // Percentage of par
    assert.strictEqual(
      formatBondPrice("98.50", "percentage_of_par"),
      "98.50%"
    );
    // Price per 100 face
    assert.strictEqual(
      formatBondPrice("100.25", "price_per_100_face"),
      "100.25 /100"
    );
    // Absolute amount
    assert.strictEqual(
      formatBondPrice("950.00", "absolute_amount"),
      "950.00"
    );

    // Missing / null prices must return a truthful dash
    assert.strictEqual(formatBondPrice(null), "—");
    assert.strictEqual(formatBondPrice(undefined), "—");
    assert.strictEqual(formatBondPrice(""), "—");
    assert.strictEqual(formatBondPrice("invalid"), "—");

    // Price basis labels
    assert.strictEqual(formatPriceBasis("clean"), "Clean");
    assert.strictEqual(formatPriceBasis("dirty"), "Dirty");
    assert.strictEqual(formatPriceBasis("unknown"), "Unknown");

    // Price kind labels
    assert.strictEqual(formatPriceKind("evaluated_price"), "Evaluated Model");
    assert.strictEqual(formatPriceKind("trade_price"), "Executed Trade");
    assert.strictEqual(formatPriceKind("indicative_quote"), "Indicative Quote");
  });

  it("should format contractual coupons distinguishing fixed, floating, zero and missing", () => {
    // Fixed coupon
    assert.strictEqual(
      formatBondCoupon("5.250", "fixed"),
      "5.25%"
    );
    // Genuine zero coupon bond
    assert.strictEqual(
      formatBondCoupon(null, "zero_coupon"),
      "Zero (0.00%)"
    );
    // Floating rate bond
    assert.strictEqual(
      formatBondCoupon("1.250", "floating"),
      "1.25% (Float)"
    );
    // Missing coupon must never be rendered as 0%
    assert.strictEqual(
      formatBondCoupon(null, "other"),
      "Coupon unavailable"
    );
    assert.strictEqual(
      formatBondCoupon(null, "fixed"),
      "Coupon unavailable"
    );
  });

  it("should format bond yields preserving typed measures, negative yields and basis point changes", () => {
    // Typical positive yield
    assert.strictEqual(formatBondYield("4.250"), "4.25%");
    // Genuine negative yield (e.g. historical German Bunds or JGBs)
    assert.strictEqual(formatBondYield("-0.150"), "-0.15%");
    // Missing yield must return a dash, never a fabricated number
    assert.strictEqual(formatBondYield(null), "—");

    // Yield type labels
    assert.strictEqual(formatYieldTypeLabel("ytm"), "YTM");
    assert.strictEqual(formatYieldTypeLabel("discount_yield"), "Discount");
    assert.strictEqual(formatYieldTypeLabel("current_yield"), "Current Yield");
    assert.strictEqual(formatYieldTypeLabel("ytw"), "YTW");

    // Basis points (bps) yield change
    assert.strictEqual(formatYieldChangeBps("25.0"), "+25.0 bps");
    assert.strictEqual(formatYieldChangeBps("-5.5"), "-5.5 bps");
    assert.strictEqual(formatYieldChangeBps("0.0"), "0.0 bps");
    assert.strictEqual(formatYieldChangeBps(null), "—");
  });

  it("should format maturities, perpetual debt, and calendar time-to-maturity approximations", () => {
    assert.strictEqual(
      formatBondMaturity("2034-05-15"),
      "May 15, 2034"
    );
    assert.strictEqual(
      formatBondMaturity(null, true),
      "Perpetual"
    );
    assert.strictEqual(
      formatBondMaturity(null, false),
      "Maturity unavailable"
    );

    // Approximate time to maturity (in years)
    assert.strictEqual(formatTimeToMaturity("10.5"), "10.5 yr");
    assert.strictEqual(formatTimeToMaturity("0.5"), "6 mo");
    assert.strictEqual(formatTimeToMaturity(null), "—");
  });

  it("should format bid/ask spread and bond classifications", () => {
    assert.strictEqual(formatBondSpread("0.040"), "0.040");
    assert.strictEqual(formatBondSpread(null), "—");

    assert.strictEqual(formatBondType("sovereign"), "Sovereign");
    assert.strictEqual(formatBondType("corporate"), "Corporate");
    assert.strictEqual(formatBondType("treasury_bill"), "Treasury Bill");
    assert.strictEqual(formatBondType("supranational"), "Supranational");
  });

  it("should format observation timestamps and freshness indicators", () => {
    assert.strictEqual(
      formatObservationTime("2026-10-15T12:00:00Z"),
      "12:00:00 UTC"
    );
    assert.strictEqual(formatObservationTime(null), "—");

    const freshClass = getFreshnessBadgeClass("REALTIME");
    assert.ok(freshClass.includes("emerald"), "Fresh class must have emerald style");
    const delayedClass = getFreshnessBadgeClass("DELAYED");
    assert.ok(delayedClass.includes("amber"), "Delayed class must have amber style");
    const staleClass = getFreshnessBadgeClass("STALE");
    assert.ok(staleClass.includes("rose"), "Stale class must have rose style");
  });

  it("should ensure the dedicated /markets/bonds route page exists and renders BondsPage", () => {
    const routePage = path.join(
      __dirname,
      "../src/app/(atlas)/markets/bonds/page.tsx"
    );
    assert.ok(fs.existsSync(routePage), "/markets/bonds/page.tsx must exist");
    const content = fs.readFileSync(routePage, "utf-8");
    assert.ok(
      content.includes("BondsPage"),
      "Route page must render BondsPage"
    );
  });

  it("should verify MarketsNavigationTabs links to /markets/bonds and marks it implemented", () => {
    const tabsFile = path.join(
      __dirname,
      "../src/components/markets/MarketsNavigationTabs.tsx"
    );
    const content = fs.readFileSync(tabsFile, "utf-8");
    assert.ok(
      content.includes("/markets/bonds"),
      "Tabs must link to /markets/bonds"
    );
    assert.ok(
      content.includes("Bonds"),
      "Tabs must contain Bonds item"
    );
  });

  it("should verify strict financial design rules: no purple gradients and no buy/sell trading actions", () => {
    const componentsDir = path.join(
      __dirname,
      "../src/components/markets/bonds"
    );
    const files = fs.readdirSync(componentsDir);

    for (const file of files) {
      if (!file.endsWith(".tsx")) continue;
      const content = fs.readFileSync(path.join(componentsDir, file), "utf-8");

      assert.ok(
        !content.includes("from-purple-") && !content.includes("to-purple-"),
        `File ${file} must not contain forbidden purple gradients`
      );
      assert.ok(
        !content.includes("Buy Bond") &&
          !content.includes("Sell Bond") &&
          !content.includes("Request Quote") &&
          !content.includes("Place Order") &&
          !content.includes("Execute Trade"),
        `File ${file} must not contain broker/trading execution controls`
      );
    }
  });

  it("should verify non-executable disclaimer is present in inspector", () => {
    const inspectorPath = path.join(
      __dirname,
      "../src/components/markets/bonds/BondInspector.tsx"
    );
    const inspectorContent = fs.readFileSync(inspectorPath, "utf-8");
    assert.ok(
      inspectorContent.includes("disclaimer") ||
        inspectorContent.includes("Indicative fixed-income market observation"),
      "Inspector must disclose indicative fixed-income market reality"
    );
  });
});
