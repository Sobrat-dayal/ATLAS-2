/**
 * Financial Formatting Utilities for Stage 57 Equities Markets V1
 *
 * Provides:
 * - High-precision currency formatting
 * - Safe Decimal string representation without floating-point errors
 * - Signed price change formatting
 * - Subtype and venue label resolution
 * - Freshness and data status badge styles
 */

import {
  MarketSummaryChangeDirection,
  MarketSummaryDataStatus,
  MarketSummaryDeliveryDelay,
} from "@/lib/home/market-summary-types";

const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "$",
  INR: "₹",
  GBP: "£",
  JPY: "¥",
  EUR: "€",
  CAD: "CA$",
  AUD: "A$",
  CHF: "CHF ",
  HKD: "HK$",
  SGD: "S$",
};

/**
 * Format a price value with currency symbol and appropriate decimal places.
 * If price is missing or null, returns a truthful placeholder "—".
 */
export function formatEquityPrice(
  price: string | number | null | undefined,
  currency?: string | null
): string {
  if (price === null || price === undefined || price === "") {
    return "—";
  }

  const num = typeof price === "number" ? price : parseFloat(price);
  if (isNaN(num)) return "—";

  const curr = (currency || "USD").toUpperCase();
  const symbol = CURRENCY_SYMBOLS[curr] || `${curr} `;

  // Determine decimal places (e.g. JPY has 0 decimals typically, others 2)
  const decimals = curr === "JPY" ? 0 : 2;

  const formattedNum = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);

  return `${symbol}${formattedNum}`;
}

/**
 * Format an absolute price change with signed prefix.
 */
export function formatAbsoluteChange(
  change: string | number | null | undefined,
  currency?: string | null
): string {
  if (change === null || change === undefined || change === "") {
    return "—";
  }

  const num = typeof change === "number" ? change : parseFloat(change);
  if (isNaN(num)) return "—";

  const curr = (currency || "USD").toUpperCase();
  const symbol = CURRENCY_SYMBOLS[curr] || `${curr} `;
  const decimals = curr === "JPY" ? 0 : 2;

  const absNum = Math.abs(num);
  const formatted = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(absNum);

  if (num > 0) return `+${symbol}${formatted}`;
  if (num < 0) return `-${symbol}${formatted}`;
  return `${symbol}${formatted}`;
}

/**
 * Format a percentage change with sign and percent symbol.
 */
export function formatPercentageChange(
  pct: string | number | null | undefined
): string {
  if (pct === null || pct === undefined || pct === "") {
    return "—";
  }

  const num = typeof pct === "number" ? pct : parseFloat(pct);
  if (isNaN(num)) return "—";

  const absNum = Math.abs(num);
  const formatted = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(absNum);

  if (num > 0) return `+${formatted}%`;
  if (num < 0) return `-${formatted}%`;
  return `0.00%`;
}

/**
 * Maps equity subtype code to clean human-readable title.
 */
export function formatEquitySubtype(subtype?: string | null): string {
  if (!subtype) return "Common";
  switch (subtype.toLowerCase()) {
    case "common_equity":
    case "common":
      return "Common Stock";
    case "preferred_equity":
    case "preferred":
      return "Preferred Stock";
    case "depositary_receipt":
    case "adr":
    case "gdr":
      return "ADR / GDR";
    case "unit":
      return "Unit";
    case "warrant":
      return "Warrant";
    default:
      return subtype.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }
}

/**
 * Get CSS badge styling for market data freshness.
 */
export function getFreshnessBadge(freshnessStatus?: string | null): {
  label: string;
  className: string;
} {
  const status = (freshnessStatus || "unknown").toLowerCase();
  switch (status) {
    case "fresh":
      return {
        label: "Fresh",
        className: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      };
    case "stale":
      return {
        label: "Stale",
        className: "bg-amber-500/10 text-amber-400 border-amber-500/20",
      };
    case "delayed":
      return {
        label: "Delayed",
        className: "bg-sky-500/10 text-sky-400 border-sky-500/20",
      };
    case "unavailable":
    case "unknown":
    default:
      return {
        label: "Unavailable",
        className: "bg-zinc-800 text-zinc-400 border-zinc-700",
      };
  }
}

/**
 * Return directional color classes for numeric change.
 */
export function getDirectionColorClass(
  direction?: MarketSummaryChangeDirection | string | null
): string {
  const dir = (direction || "unknown").toLowerCase();
  switch (dir) {
    case "up":
      return "text-emerald-400";
    case "down":
      return "text-rose-400";
    case "flat":
    case "unchanged":
      return "text-zinc-400";
    case "unknown":
    default:
      return "text-zinc-500";
  }
}

/**
 * Format observation ISO timestamp into localized human-readable time string.
 */
export function formatObservationTime(timestamp?: string | null): string {
  if (!timestamp) return "—";
  try {
    const d = new Date(timestamp);
    if (isNaN(d.getTime())) return "—";
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return "—";
  }
}
