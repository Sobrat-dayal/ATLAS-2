import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  formatCurrency,
  formatPnl,
  formatPnlPct,
  formatOrderStatus,
  formatOrderType,
  calcFillPct,
  calcPositionValue,
  calcAccountPnlPct,
  formatTimestamp,
  isKillSwitchActive,
  paperAccountBadge,
  statusColor,
  pnlColor,
} from "../formatters.js";
import type { PaperAccount, PaperOrder, PaperPosition } from "../types.js";

const baseAccount: PaperAccount = {
  account_id: "acct-1",
  tenant_id: "tenant-1",
  owner_id: "user-1",
  name: "Test Paper Account",
  currency: "USD",
  initial_cash: 10000,
  cash: 9500,
  buying_power: 9500,
  margin_used: 0,
  portfolio_value: 10200,
  unrealized_pnl: 200,
  realized_pnl: 0,
  daily_realized_pnl: 0,
  kill_switch_active: false,
  active: true,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

const baseOrder: PaperOrder = {
  order_id: "ord-1",
  client_order_id: "client-ord-1",
  account_id: "acct-1",
  symbol: "AAPL",
  asset_class: "EQUITY",
  side: "BUY",
  order_type: "MARKET",
  quantity: 100,
  time_in_force: "DAY",
  status: "FILLED",
  filled_qty: 100,
  avg_fill_price: 150,
  total_fee: 1.0,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  fills: [],
};

const basePosition: PaperPosition = {
  position_id: "pos-1",
  account_id: "acct-1",
  symbol: "AAPL",
  asset_class: "EQUITY",
  quantity: 100,
  avg_cost: 150,
  current_price: 155,
  market_value: 15500,
  unrealized_pnl: 500,
  realized_pnl: 0,
  cost_basis: 15000,
  updated_at: "2024-01-01T00:00:00Z",
};

describe("paper trading formatters", () => {
  it("formatCurrency formats USD correctly", () => {
    assert.equal(formatCurrency(1234.56), "$1,234.56");
  });

  it("formatPnl shows + sign for positive", () => {
    assert.ok(formatPnl(100).startsWith("+"));
  });

  it("formatPnl shows negative for negative", () => {
    assert.ok(formatPnl(-50).includes("-"));
  });

  it("formatPnlPct calculates percentage correctly", () => {
    const result = formatPnlPct(200, 10000);
    assert.ok(result.includes("2.00"));
  });

  it("formatPnlPct handles zero basis", () => {
    assert.equal(formatPnlPct(100, 0), "0.00%");
  });

  it("formatOrderStatus capitalizes status", () => {
    assert.equal(formatOrderStatus("FILLED"), "Filled");
  });

  it("formatOrderType replaces underscores", () => {
    assert.equal(formatOrderType("STOP_LIMIT"), "STOP LIMIT");
  });

  it("calcFillPct returns 100 for fully filled order", () => {
    assert.equal(calcFillPct(baseOrder), 100);
  });

  it("calcFillPct handles zero quantity", () => {
    const o = { ...baseOrder, quantity: 0 };
    assert.equal(calcFillPct(o), 0);
  });

  it("calcPositionValue returns quantity * price", () => {
    assert.equal(calcPositionValue(basePosition), 15500);
  });

  it("calcAccountPnlPct calculates correctly", () => {
    const pct = calcAccountPnlPct(baseAccount);
    assert.ok(typeof pct === "number");
    assert.equal(pct, 2);
  });

  it("formatTimestamp formats ISO string", () => {
    const result = formatTimestamp("2024-01-15T10:30:00Z");
    assert.ok(result.includes("Jan") || result.includes("30"));
  });

  it("isKillSwitchActive returns false for active account", () => {
    assert.equal(isKillSwitchActive(baseAccount), false);
  });

  it("isKillSwitchActive returns true when kill switch set", () => {
    assert.equal(isKillSwitchActive({ ...baseAccount, kill_switch_active: true }), true);
  });

  it("paperAccountBadge returns PAPER for normal active account", () => {
    assert.equal(paperAccountBadge(baseAccount), "PAPER");
  });

  it("paperAccountBadge returns KILL SWITCH when activated", () => {
    assert.equal(paperAccountBadge({ ...baseAccount, kill_switch_active: true }), "KILL SWITCH");
  });

  it("statusColor returns green for FILLED", () => {
    assert.ok(statusColor("FILLED").includes("green"));
  });

  it("pnlColor returns green for positive", () => {
    assert.ok(pnlColor(100).includes("green"));
  });

  it("pnlColor returns red for negative", () => {
    assert.ok(pnlColor(-50).includes("red"));
  });
});
