import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  formatCryptoPrice,
  formatCryptoSpread,
  formatCryptoSpreadBps,
  formatCryptoChange,
  formatCryptoVolume,
  formatCryptoRateKind,
  formatCryptoFreshnessBadge,
  formatObservedTimestamp,
} from "../src/lib/markets/crypto/formatting";
import * as cryptoComponents from "../src/components/markets/crypto";
import * as marketsComponents from "../src/components/markets";

describe("Stage 60 - Cryptocurrency Markets V1 Tests", () => {
  it("should confirm Crypto components export cleanly", () => {
    assert.ok(cryptoComponents.CryptoMarketsPage, "CryptoMarketsPage must be exported");
    assert.ok(cryptoComponents.CryptoHeader, "CryptoHeader must be exported");
    assert.ok(
      cryptoComponents.CryptoCoverageSummary,
      "CryptoCoverageSummary must be exported"
    );
    assert.ok(
      cryptoComponents.CryptoMarketFilters,
      "CryptoMarketFilters must be exported"
    );
    assert.ok(
      cryptoComponents.CryptoSpotMarketTable,
      "CryptoSpotMarketTable must be exported"
    );
    assert.ok(
      cryptoComponents.CryptoSpotMarketRow,
      "CryptoSpotMarketRow must be exported"
    );
    assert.ok(
      cryptoComponents.CryptoMarketInspector,
      "CryptoMarketInspector must be exported"
    );
    assert.ok(
      cryptoComponents.CryptoEmptyState,
      "CryptoEmptyState must be exported"
    );
    assert.ok(
      marketsComponents.MarketsNavigationTabs,
      "MarketsNavigationTabs must be exported from components/markets"
    );
  });

  it("should format crypto prices with high precision and small-value handling", () => {
    // Standard major coin prices
    assert.strictEqual(formatCryptoPrice("67450.00", 2), "67,450.00");
    assert.strictEqual(formatCryptoPrice("3522.50", 2, "USDT"), "3,522.50 USDT");

    // Small coin / token prices
    assert.strictEqual(formatCryptoPrice("0.14250", 5), "0.14250");
    assert.strictEqual(formatCryptoPrice("0.052210", 6, "BTC"), "0.052210 BTC");

    // Missing / null rates must return a truthful dash
    assert.strictEqual(formatCryptoPrice(null), "—");
    assert.strictEqual(formatCryptoPrice(undefined), "—");
    assert.strictEqual(formatCryptoPrice(""), "—");
    assert.strictEqual(formatCryptoPrice("invalid"), "—");
  });

  it("should format absolute spread and basis points accurately", () => {
    // Absolute spread
    assert.strictEqual(formatCryptoSpread("4.00", 2), "4.00");
    assert.strictEqual(formatCryptoSpread("0.00004", 5), "0.00004");
    assert.strictEqual(formatCryptoSpread(null), "—");

    // Basis points (bps)
    assert.strictEqual(formatCryptoSpreadBps("0.59"), "0.6 bps");
    assert.strictEqual(formatCryptoSpreadBps("12.4"), "12.4 bps");
    assert.strictEqual(formatCryptoSpreadBps(null), "—");
  });

  it("should format signed percentage returns with appropriate color classes", () => {
    const pos = formatCryptoChange("2.45");
    assert.strictEqual(pos.text, "+2.45%");
    assert.strictEqual(pos.isPositive, true);
    assert.strictEqual(pos.colorClass, "text-emerald-400");

    const neg = formatCryptoChange("-0.65");
    assert.strictEqual(neg.text, "-0.65%");
    assert.strictEqual(neg.isNegative, true);
    assert.strictEqual(neg.colorClass, "text-rose-400");

    const zero = formatCryptoChange("0.00");
    assert.strictEqual(zero.text, "0.00%");
    assert.strictEqual(zero.colorClass, "text-[var(--atlas-text-secondary)]");

    const missing = formatCryptoChange(null);
    assert.strictEqual(missing.text, "—");
  });

  it("should format volume preserving base and quote units", () => {
    // Base volume
    assert.strictEqual(formatCryptoVolume("11200.5", "BTC"), "11.2K BTC");
    assert.strictEqual(formatCryptoVolume("780000", "SOL"), "780.0K SOL");

    // Quote volume
    assert.strictEqual(formatCryptoVolume("755473725", "USD"), "755.47M USD");
    assert.strictEqual(formatCryptoVolume("1916006000", "USDT"), "1.92B USDT");

    // Missing
    assert.strictEqual(formatCryptoVolume(null), "—");
  });

  it("should format rate kinds and freshness badges distinctly", () => {
    assert.strictEqual(formatCryptoRateKind("SPOT_TRADE").label, "Spot Trade");
    assert.strictEqual(formatCryptoRateKind("BID_ASK_QUOTE").label, "Bid / Ask");
    assert.strictEqual(
      formatCryptoRateKind("CROSSED_INVALID").label,
      "Crossed (Invalid)"
    );

    assert.strictEqual(formatCryptoFreshnessBadge("FRESH").label, "Live");
    assert.strictEqual(formatCryptoFreshnessBadge("DELAYED").label, "Delayed");
    assert.strictEqual(formatCryptoFreshnessBadge("STALE").label, "Stale");
  });

  it("should format observation timestamps safely", () => {
    assert.strictEqual(
      formatObservedTimestamp("2026-10-15T12:00:00Z"),
      "2026-10-15 12:00:00 UTC"
    );
    assert.strictEqual(formatObservedTimestamp(null), "—");
    assert.strictEqual(formatObservedTimestamp(""), "—");
  });

  it("should ensure the dedicated /markets/crypto route page exists and renders CryptoMarketsPage", () => {
    const routePage = path.join(
      __dirname,
      "../src/app/(atlas)/markets/crypto/page.tsx"
    );
    assert.ok(fs.existsSync(routePage), "/markets/crypto/page.tsx must exist");
    const content = fs.readFileSync(routePage, "utf-8");
    assert.ok(
      content.includes("CryptoMarketsPage"),
      "Route page must render CryptoMarketsPage"
    );
  });

  it("should verify MarketsNavigationTabs links to /markets/crypto and marks it implemented", () => {
    const tabsFile = path.join(
      __dirname,
      "../src/components/markets/MarketsNavigationTabs.tsx"
    );
    const content = fs.readFileSync(tabsFile, "utf-8");
    assert.ok(
      content.includes("/markets/crypto"),
      "Tabs must link to /markets/crypto"
    );
    assert.ok(
      content.includes("Cryptocurrency"),
      "Tabs must contain Cryptocurrency item"
    );
  });

  it("should verify strict financial design rules: no purple gradients and no buy/sell trading actions", () => {
    const componentsDir = path.join(
      __dirname,
      "../src/components/markets/crypto"
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
        !content.includes("Buy Crypto") &&
          !content.includes("Sell Crypto") &&
          !content.includes("Connect Wallet") &&
          !content.includes("Execute Trade") &&
          !content.includes("Deposit Funds"),
        `File ${file} must not contain broker/trading execution controls`
      );
    }
  });

  it("should verify non-executable disclaimer is present in inspector", () => {
    const inspectorPath = path.join(
      __dirname,
      "../src/components/markets/crypto/CryptoMarketInspector.tsx"
    );
    const inspectorContent = fs.readFileSync(inspectorPath, "utf-8");
    assert.ok(
      inspectorContent.includes("disclaimer") ||
        inspectorContent.includes("Indicative spot market observation"),
      "Inspector must disclose indicative spot market reality"
    );
  });
});
