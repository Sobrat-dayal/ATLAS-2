import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  formatCurrency,
  formatStrike,
  formatPercent,
  formatNumber,
  formatDte,
  formatMoneynessBadge,
  formatQualityFlag,
  formatOsiSymbol,
  parseOsiSymbol,
} from "../formatters";

describe("ATLAS Options Analytics Formatters & Symbology", () => {
  it("formats currency correctly for USD, INR, and negative balances", () => {
    assert.equal(formatCurrency(1500), "$1,500.00");
    assert.equal(formatCurrency(-500), "-$500.00");
    assert.equal(formatCurrency(9000, "INR"), "₹9,000.00");
    assert.equal(formatCurrency(-9000, "INR"), "-₹9,000.00");
    assert.equal(formatCurrency(null), "—");
    assert.equal(formatCurrency(undefined), "—");
  });

  it("formats strike price with appropriate currency prefix", () => {
    assert.equal(formatStrike(100), "$100.00");
    assert.equal(formatStrike(22000, "INR"), "₹22000.00");
  });

  it("formats percent and numbers accurately", () => {
    assert.equal(formatPercent(0.254), "25.4%");
    assert.equal(formatPercent(null), "—");
    assert.equal(formatNumber(45000), "45,000");
    assert.equal(formatNumber(null), "—");
  });

  it("formats days to expiration human-readable label", () => {
    assert.equal(formatDte(0), "0d (Expires Today)");
    assert.equal(formatDte(1), "1d (Tomorrow)");
    assert.equal(formatDte(32), "32d");
    assert.equal(formatDte(null), "—");
  });

  it("formats moneyness badges", () => {
    assert.equal(formatMoneynessBadge("IN_THE_MONEY").label, "ITM");
    assert.equal(formatMoneynessBadge("AT_THE_MONEY").label, "ATM");
    assert.equal(formatMoneynessBadge("OUT_OF_THE_MONEY").label, "OTM");
  });

  it("formats quote quality flags", () => {
    assert.equal(formatQualityFlag("VALID").label, "Valid");
    assert.match(formatQualityFlag("ZERO_BID").label, /Zero Bid/);
    assert.match(formatQualityFlag("CROSSED_MARKET").label, /Crossed Market/);
    assert.match(formatQualityFlag("LOCKED_MARKET").label, /Locked Market/);
    assert.match(formatQualityFlag("STALE_QUOTE").label, /Stale Quote/);
  });

  it("formats 21-character standard OSI symbols", () => {
    const osiCall = formatOsiSymbol("SPY", "2024-06-21", "CALL", 100.0);
    assert.equal(osiCall.length, 21);
    assert.equal(osiCall, "SPY   240621C00100000");

    const osiPut = formatOsiSymbol("AAPL", "2024-07-19", "PUT", 185.5);
    assert.equal(osiPut.length, 21);
    assert.equal(osiPut, "AAPL  240719P00185500");
  });

  it("parses 21-character OSI symbols into root, expiration, type, and strike", () => {
    const parsed = parseOsiSymbol("SPY   240621C00100000");
    assert.ok(parsed);
    assert.equal(parsed.root, "SPY");
    assert.equal(parsed.expirationDate, "2024-06-21");
    assert.equal(parsed.optionType, "CALL");
    assert.equal(parsed.strikePrice, 100.0);

    const parsedPut = parseOsiSymbol("AAPL  240719P00185500");
    assert.ok(parsedPut);
    assert.equal(parsedPut.root, "AAPL");
    assert.equal(parsedPut.expirationDate, "2024-07-19");
    assert.equal(parsedPut.optionType, "PUT");
    assert.equal(parsedPut.strikePrice, 185.5);

    assert.equal(parseOsiSymbol("INVALID_LENGTH"), null);
  });
});
