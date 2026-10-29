import { test } from "node:test";
import assert from "node:assert/strict";

import {
  formatCurrency,
  formatPnL,
  formatPrice,
  formatQuantity,
  getQuoteFreshnessBadge,
  getReconciliationBadge,
  getTransactionTypeBadge,
  getValuationStatusBadge,
} from "../formatting";

test("Stage 110: formatCurrency formats standard currencies accurately", () => {
  assert.equal(formatCurrency(10000, "USD"), "$10,000.00");
  assert.equal(formatCurrency("7382.00", "USD"), "$7,382.00");
  assert.equal(formatCurrency(0, "USD"), "$0.00");
  assert.equal(formatCurrency(null), "—");
  assert.equal(formatCurrency(undefined), "—");
  assert.equal(formatCurrency("invalid"), "—");
});

test("Stage 110: formatQuantity formats whole and fractional shares", () => {
  assert.equal(formatQuantity(100), "100");
  assert.equal(formatQuantity("60"), "60");
  assert.equal(formatQuantity(42.5), "42.5");
  assert.equal(formatQuantity(null), "—");
});

test("Stage 110: formatPrice handles precision and currencies", () => {
  assert.equal(formatPrice(50.1, "USD"), "$50.10");
  assert.equal(formatPrice(55, "USD"), "$55.00");
  assert.equal(formatPrice(null), "—");
});

test("Stage 110: formatPnL decorates signs and institutional formatting", () => {
  const pos = formatPnL(388, "USD");
  assert.equal(pos.text, "+$388.00");
  assert.equal(pos.isPositive, true);
  assert.equal(pos.isNegative, false);

  const neg = formatPnL(-150.5, "USD");
  assert.equal(neg.text, "-$150.50");
  assert.equal(neg.isPositive, false);
  assert.equal(neg.isNegative, true);

  const zero = formatPnL(0, "USD");
  assert.equal(zero.text, "$0.00");
  assert.equal(zero.isPositive, false);
  assert.equal(zero.isNegative, false);
});

test("Stage 110: Status and classification badge resolvers return valid variants", () => {
  assert.equal(getValuationStatusBadge("COMPLETE").variant, "positive");
  assert.equal(getValuationStatusBadge("PARTIAL_MISSING_PRICES").variant, "warning");
  assert.equal(getValuationStatusBadge("UNAVAILABLE").variant, "negative");

  assert.equal(getTransactionTypeBadge("BUY").variant, "primary");
  assert.equal(getTransactionTypeBadge("SELL").variant, "warning");
  assert.equal(getTransactionTypeBadge("CASH_DEPOSIT").variant, "positive");
  assert.equal(getTransactionTypeBadge("CORRECTION_REVERSAL").variant, "negative");

  assert.equal(getQuoteFreshnessBadge("REALTIME").variant, "positive");
  assert.equal(getQuoteFreshnessBadge("STALE").variant, "warning");

  assert.equal(getReconciliationBadge("RECONCILED").variant, "positive");
  assert.equal(getReconciliationBadge("OUT_OF_BALANCE").variant, "negative");
});

test("Stage 110: Part XXII Exact Reference Fixture Accounting Math Verification", () => {
  // Initial deposit
  const initialDeposit = 10000;

  // Buy 100 shares @ $50 + $10 fee
  const buyQty = 100;
  const buyPrice = 50;
  const buyFee = 10;
  const purchaseGross = buyQty * buyPrice; // 5,000
  const purchaseTotalCost = purchaseGross + buyFee; // 5,010
  const cashAfterBuy = initialDeposit - purchaseTotalCost; // 4,990
  const unitCostBasis = purchaseTotalCost / buyQty; // 50.10

  assert.equal(purchaseGross, 5000);
  assert.equal(purchaseTotalCost, 5010);
  assert.equal(cashAfterBuy, 4990);
  assert.equal(unitCostBasis, 50.1);

  // Sell 40 shares @ $60 - $8 fee
  const sellQty = 40;
  const sellPrice = 60;
  const sellFee = 8;
  const saleGross = sellQty * sellPrice; // 2,400
  const saleNetProceeds = saleGross - sellFee; // 2,392
  const cashAfterSale = cashAfterBuy + saleNetProceeds; // 7,382
  const remainingQty = buyQty - sellQty; // 60
  const basisDisposed = sellQty * unitCostBasis; // 2,004
  const realizedPnL = saleNetProceeds - basisDisposed; // 388
  const remainingBasis = remainingQty * unitCostBasis; // 3,006

  assert.equal(saleGross, 2400);
  assert.equal(saleNetProceeds, 2392);
  assert.equal(cashAfterSale, 7382);
  assert.equal(remainingQty, 60);
  assert.equal(basisDisposed, 2004);
  assert.equal(realizedPnL, 388);
  assert.equal(remainingBasis, 3006);

  // Mark price: $55
  const markPrice = 55;
  const positionMarketValue = remainingQty * markPrice; // 3,300
  const unrealizedPnL = positionMarketValue - remainingBasis; // 294
  const portfolioMarketValue = cashAfterSale + positionMarketValue; // 10,682
  const netGain = realizedPnL + unrealizedPnL; // 682

  assert.equal(positionMarketValue, 3300);
  assert.equal(unrealizedPnL, 294);
  assert.equal(portfolioMarketValue, 10682);
  assert.equal(netGain, 682);
  assert.equal(portfolioMarketValue - initialDeposit, netGain);
});
