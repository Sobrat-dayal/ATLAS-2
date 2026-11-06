/**
 * ATLAS Stage 144: Paper Trading API client.
 * PAPER SIMULATION ONLY — no real broker, no real money.
 */

import type { PaperAccount, PaperOrder, PaperPosition } from "./types";

const BASE = "/api/v1/trading/paper";

export async function listPaperAccounts(): Promise<PaperAccount[]> {
  const r = await fetch(`${BASE}/accounts`);
  if (!r.ok) throw new Error(`listPaperAccounts: ${r.status}`);
  return r.json();
}

export async function createPaperAccount(payload: {
  name: string;
  currency?: string;
  initial_cash?: number;
}): Promise<PaperAccount> {
  const r = await fetch(`${BASE}/accounts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`createPaperAccount: ${r.status}`);
  return r.json();
}

export async function getPaperAccount(accountId: string): Promise<PaperAccount> {
  const r = await fetch(`${BASE}/accounts/${accountId}`);
  if (!r.ok) throw new Error(`getPaperAccount: ${r.status}`);
  return r.json();
}

export async function activatePaperKillSwitch(accountId: string, reason: string): Promise<void> {
  const r = await fetch(`${BASE}/accounts/${accountId}/kill-switch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!r.ok) throw new Error(`activatePaperKillSwitch: ${r.status}`);
}

export async function submitPaperOrder(accountId: string, payload: {
  symbol: string;
  side: "BUY" | "SELL";
  order_type: string;
  quantity: number;
  limit_price?: number;
  stop_price?: number;
  time_in_force?: string;
  client_order_id?: string;
}): Promise<PaperOrder> {
  const r = await fetch(`${BASE}/accounts/${accountId}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`submitPaperOrder: ${r.status}`);
  return r.json();
}

export async function listPaperOrders(accountId: string): Promise<PaperOrder[]> {
  const r = await fetch(`${BASE}/accounts/${accountId}/orders`);
  if (!r.ok) throw new Error(`listPaperOrders: ${r.status}`);
  return r.json();
}

export async function cancelPaperOrder(accountId: string, orderId: string): Promise<void> {
  const r = await fetch(`${BASE}/accounts/${accountId}/orders/${orderId}/cancel`, {
    method: "POST",
  });
  if (!r.ok) throw new Error(`cancelPaperOrder: ${r.status}`);
}

export async function listPaperPositions(accountId: string): Promise<PaperPosition[]> {
  const r = await fetch(`${BASE}/accounts/${accountId}/positions`);
  if (!r.ok) throw new Error(`listPaperPositions: ${r.status}`);
  return r.json();
}
