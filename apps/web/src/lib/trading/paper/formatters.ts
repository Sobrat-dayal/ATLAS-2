/**
 * ATLAS Stage 144: Paper Trading formatters and utilities.
 */

import type { PaperAccount, PaperOrder, PaperOrderStatus, PaperOrderType, PaperPosition } from "./types";

export function formatCurrency(value: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatPnl(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${formatCurrency(value)}`;
}

export function formatPnlPct(value: number, basis: number): string {
  if (basis === 0) return "0.00%";
  const pct = (value / basis) * 100;
  const sign = pct >= 0 ? "+" : "";
  return `${sign}${pct.toFixed(2)}%`;
}

export function formatOrderStatus(status: PaperOrderStatus): string {
  return status.charAt(0) + status.slice(1).toLowerCase();
}

export function formatOrderType(type: PaperOrderType): string {
  return type.replace(/_/g, " ");
}

export function calcFillPct(order: PaperOrder): number {
  if (order.quantity === 0) return 0;
  return (order.filled_qty / order.quantity) * 100;
}

export function calcPositionValue(position: PaperPosition): number {
  return position.quantity * position.current_price;
}

export function calcAccountPnlPct(account: PaperAccount): number {
  if (account.initial_cash === 0) return 0;
  const totalPnl = account.unrealized_pnl + account.realized_pnl;
  return (totalPnl / account.initial_cash) * 100;
}

export function formatTimestamp(ts: string): string {
  if (!ts) return "—";
  try {
    return new Date(ts).toLocaleString("en-US", {
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return ts;
  }
}

export function isKillSwitchActive(account: PaperAccount): boolean {
  return account.kill_switch_active;
}

export function paperAccountBadge(account: PaperAccount): string {
  if (account.kill_switch_active) return "KILL SWITCH";
  if (!account.active) return "INACTIVE";
  return "PAPER";
}

export function statusColor(status: PaperOrderStatus): string {
  switch (status) {
    case "FILLED": return "text-green-400";
    case "PARTIAL": return "text-yellow-400";
    case "OPEN": return "text-blue-400";
    case "PENDING": return "text-gray-400";
    case "CANCELLED": return "text-gray-500";
    case "REJECTED": return "text-red-400";
    case "EXPIRED": return "text-orange-400";
    default: return "text-gray-400";
  }
}

export function pnlColor(value: number): string {
  if (value > 0) return "text-green-400";
  if (value < 0) return "text-red-400";
  return "text-gray-400";
}
