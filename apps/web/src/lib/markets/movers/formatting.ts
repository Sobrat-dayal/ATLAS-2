/**
 * Numerical, financial, and temporal formatting utilities for Market Movers V1.
 */

import { CoverageStatus, ExclusionReason } from "./types";

/**
 * Format signed percentage with positive plus sign and tabular precision.
 */
export function formatSignedPercent(val?: string | number | null): string {
  if (val === null || val === undefined || val === "") return "—";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "—";

  const prefix = num > 0 ? "+" : "";
  return `${prefix}${num.toFixed(2)}%`;
}

/**
 * Format signed absolute price change with explicit sign.
 */
export function formatSignedAbsoluteChange(
  val?: string | number | null,
  currency: string = "USD"
): string {
  if (val === null || val === undefined || val === "") return "—";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "—";

  const absFormatted = formatPrice(Math.abs(num), currency);
  if (num > 0) {
    return `+${absFormatted}`;
  } else if (num < 0) {
    return `-${absFormatted}`;
  }
  return absFormatted;
}

/**
 * Format monetary or commodity price.
 */
export function formatPrice(
  val?: string | number | null,
  currency: string = "USD"
): string {
  if (val === null || val === undefined || val === "") return "—";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "—";

  if (currency === "USDT" || currency === "USD") {
    if (num >= 1000) {
      return `$${num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (num < 1 && num > 0) {
      return `$${num.toFixed(4)}`;
    }
    return `$${num.toFixed(2)}`;
  }

  return `${num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`;
}

/**
 * Format trading activity volume with explicit units.
 */
export function formatActivityVolume(
  val?: string | number | null,
  unit?: string | null
): string {
  if (val === null || val === undefined || val === "") return "—";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "—";

  let formattedNum = "";
  if (num >= 1_000_000_000) {
    formattedNum = `${(num / 1_000_000_000).toFixed(2)}B`;
  } else if (num >= 1_000_000) {
    formattedNum = `${(num / 1_000_000).toFixed(2)}M`;
  } else if (num >= 1_000) {
    formattedNum = `${(num / 1_000).toFixed(1)}K`;
  } else {
    formattedNum = num.toLocaleString("en-US");
  }

  return unit ? `${formattedNum} ${unit}` : formattedNum;
}

/**
 * Format ordinal rank.
 */
export function formatRank(rank: number): string {
  return `#${rank}`;
}

/**
 * Human-readable label for coverage status.
 */
export function formatCoverageStatus(status: CoverageStatus): {
  label: string;
  badgeClass: string;
} {
  switch (status) {
    case "COMPLETE_FOR_DEFINED_UNIVERSE":
      return {
        label: "Complete for Defined Universe",
        badgeClass: "bg-emerald-950/60 text-emerald-400 border-emerald-800/40",
      };
    case "PARTIAL_COVERAGE":
      return {
        label: "Partial Coverage",
        badgeClass: "bg-amber-950/60 text-amber-400 border-amber-800/40",
      };
    case "DEGRADED":
      return {
        label: "Degraded Coverage",
        badgeClass: "bg-rose-950/60 text-rose-400 border-rose-800/40",
      };
    case "UNAVAILABLE":
    default:
      return {
        label: "Unavailable",
        badgeClass: "bg-zinc-800 text-zinc-400 border-zinc-700/50",
      };
  }
}

/**
 * Human-readable description of typed exclusion reason.
 */
export function formatExclusionReason(reason: ExclusionReason | string): string {
  switch (reason) {
    case "NO_CURRENT_QUOTE":
      return "Missing latest traded quote";
    case "NO_REFERENCE":
      return "Missing reference observation (previous close/settle)";
    case "INVALID_DENOMINATOR":
      return "Non-positive reference price (percent return undefined)";
    case "MISSING_VOLUME":
      return "No trading volume reported";
    case "INSTRUMENT_INACTIVE":
      return "Instrument not actively trading";
    case "STALE_CURRENT":
      return "Current quote is stale";
    case "UNKNOWN_FRESHNESS":
      return "Quote freshness cannot be verified";
    case "INCOMPATIBLE_SERIES":
      return "Series methodology mismatch";
    case "INCOMPATIBLE_UNIT":
      return "Quotation unit incompatibility";
    case "INCOMPATIBLE_WINDOW":
      return "Comparison time window mismatch";
    case "NOT_ENTITLED":
      return "Not entitled to market feed";
    case "DATA_SOURCE_UNAVAILABLE":
      return "Provider feed unavailable";
    case "OTHER":
    default:
      return "Zero price change or unqualified";
  }
}

/**
 * Format UTC ISO timestamp to compact display.
 */
export function formatTimestamp(isoStr?: string | null): string {
  if (!isoStr) return "—";
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return isoStr;
  }
}
