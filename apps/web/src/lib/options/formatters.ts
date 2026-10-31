/**
 * Formatting utilities for ATLAS Options Analytics (Stage 141).
 */

import { MoneynessState, QuoteQualityFlag } from "./types";

export function formatCurrency(
  value?: number | null,
  currency: string = "USD",
  decimals: number = 2
): string {
  if (value === undefined || value === null || isNaN(value)) {
    return "—";
  }
  const prefix = currency === "INR" ? "₹" : currency === "EUR" ? "€" : "$";
  const absVal = Math.abs(value);
  const formatted = absVal.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return value < 0 ? `-${prefix}${formatted}` : `${prefix}${formatted}`;
}

export function formatStrike(strike: number, currency: string = "USD"): string {
  const prefix = currency === "INR" ? "₹" : currency === "EUR" ? "€" : "$";
  return `${prefix}${strike.toFixed(2)}`;
}

export function formatPercent(val?: number | null, decimals: number = 1): string {
  if (val === undefined || val === null || isNaN(val)) {
    return "—";
  }
  return `${(val * 100).toFixed(decimals)}%`;
}

export function formatNumber(val?: number | null): string {
  if (val === undefined || val === null || isNaN(val)) {
    return "—";
  }
  return val.toLocaleString();
}

export function formatDte(dte?: number | null): string {
  if (dte === undefined || dte === null) return "—";
  if (dte === 0) return "0d (Expires Today)";
  if (dte === 1) return "1d (Tomorrow)";
  return `${dte}d`;
}

export function formatMoneynessBadge(moneyness: MoneynessState): { label: string; className: string } {
  switch (moneyness) {
    case "IN_THE_MONEY":
      return { label: "ITM", className: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30" };
    case "AT_THE_MONEY":
      return { label: "ATM", className: "bg-amber-500/15 text-amber-400 border border-amber-500/30" };
    case "OUT_OF_THE_MONEY":
    default:
      return { label: "OTM", className: "bg-zinc-800 text-zinc-400 border border-zinc-700/50" };
  }
}

export function formatQualityFlag(flag: QuoteQualityFlag): { label: string; className: string } {
  switch (flag) {
    case "VALID":
      return { label: "Valid", className: "text-emerald-400" };
    case "ZERO_BID":
      return { label: "Zero Bid (No Liquidity)", className: "text-amber-400 bg-amber-500/10 px-1 rounded" };
    case "CROSSED_MARKET":
      return { label: "Crossed Market (Bid > Ask)", className: "text-rose-400 bg-rose-500/10 px-1 rounded" };
    case "LOCKED_MARKET":
      return { label: "Locked Market (Bid == Ask)", className: "text-yellow-400 bg-yellow-500/10 px-1 rounded" };
    case "STALE_QUOTE":
      return { label: "Stale Quote", className: "text-orange-400 bg-orange-500/10 px-1 rounded" };
    case "MISSING_ASK":
      return { label: "Missing Ask", className: "text-rose-400 bg-rose-500/10 px-1 rounded" };
    case "WIDE_SPREAD":
      return { label: "Wide Bid-Ask Spread", className: "text-amber-300 bg-amber-500/10 px-1 rounded" };
    default:
      return { label: flag, className: "text-zinc-400" };
  }
}

export function formatOsiSymbol(
  root: string,
  expirationDate: string,
  optionType: "CALL" | "PUT",
  strikePrice: number
): string {
  const paddedRoot = root.toUpperCase().padEnd(6, " ");
  const [year, month, day] = expirationDate.split("-");
  const yy = year.slice(2);
  const typeChar = optionType === "CALL" ? "C" : "P";
  const strikeInt = Math.round(strikePrice * 1000);
  const strikePadded = strikeInt.toString().padStart(8, "0");
  return `${paddedRoot}${yy}${month}${day}${typeChar}${strikePadded}`;
}

export function parseOsiSymbol(osi: string): {
  root: string;
  expirationDate: string;
  optionType: "CALL" | "PUT";
  strikePrice: number;
} | null {
  if (!osi || osi.length !== 21) return null;
  const root = osi.slice(0, 6).trim();
  const yy = osi.slice(6, 8);
  const mm = osi.slice(8, 10);
  const dd = osi.slice(10, 12);
  const typeChar = osi.slice(12, 13);
  const strikeRaw = parseInt(osi.slice(13, 21), 10);

  if (isNaN(strikeRaw)) return null;
  const strikePrice = strikeRaw / 1000.0;
  const optionType: "CALL" | "PUT" = typeChar === "C" ? "CALL" : "PUT";
  const expirationDate = `20${yy}-${mm}-${dd}`;

  return { root, expirationDate, optionType, strikePrice };
}

