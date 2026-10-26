/**
 * Precision formatting utilities for Financial Screeners V1 (Stage 94).
 */

export function formatCompactCurrency(val: number | null | undefined, currency = "USD"): string {
  if (val === null || val === undefined) return "—";
  const sym = currency === "USD" ? "$" : currency === "INR" ? "₹" : currency === "EUR" ? "€" : currency === "GBP" ? "£" : `${currency} `;
  const abs = Math.abs(val);
  const sign = val < 0 ? "-" : "";

  if (abs >= 1e12) {
    return `${sign}${sym}${(abs / 1e12).toFixed(2)}T`;
  }
  if (abs >= 1e9) {
    return `${sign}${sym}${(abs / 1e9).toFixed(2)}B`;
  }
  if (abs >= 1e6) {
    return `${sign}${sym}${(abs / 1e6).toFixed(2)}M`;
  }
  if (abs >= 1e3) {
    return `${sign}${sym}${(abs / 1e3).toFixed(2)}K`;
  }
  return `${sign}${sym}${abs.toFixed(2)}`;
}

export function formatPrice(val: number | null | undefined, currency = "USD"): string {
  if (val === null || val === undefined) return "—";
  const sym = currency === "USD" ? "$" : currency === "INR" ? "₹" : currency === "EUR" ? "€" : currency === "GBP" ? "£" : `${currency} `;
  return `${sym}${Number(val).toFixed(2)}`;
}

export function formatPercent(val: number | null | undefined, includeSign = false): string {
  if (val === null || val === undefined) return "—";
  const num = Number(val);
  const sign = includeSign && num > 0 ? "+" : "";
  return `${sign}${num.toFixed(2)}%`;
}

export function formatMultiple(val: number | null | undefined): string {
  if (val === null || val === undefined) return "—";
  return `${Number(val).toFixed(2)}x`;
}

export function formatShares(val: number | null | undefined): string {
  if (val === null || val === undefined) return "—";
  const num = Number(val);
  if (num >= 1e6) {
    return `${(num / 1e6).toFixed(1)}M`;
  }
  if (num >= 1e3) {
    return `${(num / 1e3).toFixed(1)}K`;
  }
  return num.toLocaleString();
}
