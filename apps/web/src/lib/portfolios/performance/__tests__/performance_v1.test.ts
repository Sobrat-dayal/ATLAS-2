import { test } from "node:test";
import assert from "node:assert/strict";

import {
  formatCurrency,
  formatRate,
  getCashFlowClassificationBadge,
  getCompletenessBadge,
} from "../formatting";

test("Stage 111: Part XIII Exact TWR Reference Fixture Math", () => {
  // Period 1: $100 -> $110 (R1 = 10%)
  const r1 = 110 / 100 - 1;
  assert.ok(Math.abs(r1 - 0.1) < 1e-6);

  // Flow: +$50 at start of Period 2 -> starting base $160
  // Period 2: $160 -> $176 (R2 = 10%)
  const r2 = 176 / 160 - 1;
  assert.ok(Math.abs(r2 - 0.1) < 1e-6);

  // Geometric linking: (1 + 0.1) * (1 + 0.1) - 1 = 1.21 - 1 = 21%
  const twr = (1 + r1) * (1 + r2) - 1;
  assert.equal(Math.round(twr * 10000) / 10000, 0.21);

  // Naive rate: ($176 - $100) / $100 = 76% (strictly rejected!)
  const naive = (176 - 100) / 100;
  assert.notEqual(twr, naive);
  assert.equal(naive, 0.76);
});

test("Stage 111: Part XXXIV Multi-Currency Return Fixture Math", () => {
  // Native USD: $100 -> $110 (+10%)
  const rUsd = 110 / 100 - 1;
  assert.ok(Math.abs(rUsd - 0.1) < 1e-6);

  // FX: USD/INR starts at 80.0, ends at 90.0
  const inrStart = 100 * 80; // 8,000 INR
  const inrEnd = 110 * 90; // 9,900 INR

  // Base INR Return: 9900 / 8000 - 1 = 1.2375 - 1 = 23.75%
  const rInr = inrEnd / inrStart - 1;
  assert.ok(Math.abs(rInr - 0.2375) < 1e-6);
  assert.equal(formatRate(rInr), "+23.75%");
});

test("Stage 111: formatRate handles positive, negative, zero, and options", () => {
  assert.equal(formatRate(0.21), "+21.00%");
  assert.equal(formatRate("0.21"), "+21.00%");
  assert.equal(formatRate(-0.054), "-5.40%");
  assert.equal(formatRate(0), "0.00%");
  assert.equal(formatRate(0.12345, { decimals: 4 }), "+12.3450%");
  assert.equal(formatRate(0.1, { showSign: false }), "10.00%");
  assert.equal(formatRate(null), "--");
  assert.equal(formatRate(undefined), "--");
  assert.equal(formatRate("invalid"), "--");
});

test("Stage 111: formatCurrency handles standard and institutional amounts", () => {
  assert.equal(formatCurrency(10000, "USD"), "$10,000.00");
  assert.equal(formatCurrency("10490.50", "USD"), "$10,490.50");
  assert.equal(formatCurrency(0, "USD"), "$0.00");
  assert.equal(formatCurrency(null), "--");
  assert.equal(formatCurrency(undefined), "--");
});

test("Stage 111: getCompletenessBadge returns institutional status labels", () => {
  assert.equal(getCompletenessBadge("COMPLETE").variant, "positive");
  assert.equal(getCompletenessBadge("COMPLETE_WITH_STALE_MARKS").variant, "warning");
  assert.equal(getCompletenessBadge("PARTIAL_MISSING_PRICES").variant, "negative");
  assert.equal(getCompletenessBadge("PARTIAL_MISSING_VALUATION").variant, "negative");
  assert.equal(getCompletenessBadge("EMPTY").variant, "default");
});

test("Stage 111: getCashFlowClassificationBadge discriminates internal vs external", () => {
  const dep = getCashFlowClassificationBadge("EXTERNAL_CONTRIBUTION");
  assert.equal(dep.isExternal, true);
  assert.equal(dep.label, "External Contribution");

  const wdr = getCashFlowClassificationBadge("EXTERNAL_WITHDRAWAL");
  assert.equal(wdr.isExternal, true);

  const buy = getCashFlowClassificationBadge("INTERNAL_SECURITY_TRADE");
  assert.equal(buy.isExternal, false);

  const div = getCashFlowClassificationBadge("INTERNAL_INCOME");
  assert.equal(div.isExternal, false);

  const fee = getCashFlowClassificationBadge("INTERNAL_FEE");
  assert.equal(fee.isExternal, false);

  const xfer = getCashFlowClassificationBadge("INTERNAL_TRANSFER");
  assert.equal(xfer.isExternal, false);
});
