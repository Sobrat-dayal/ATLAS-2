/**
 * Formatting and display utilities for ATLAS Market Heatmaps V1 (Stage 64).
 */

import { HeatmapCoverageStatus, HeatmapExclusionReason } from "./types";

/**
 * Formats a signed percentage return with explicit '+' sign for positive values.
 */
export function formatSignedPercent(
  val: number | string | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || val === "") return "N/A";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "N/A";

  const formatted = Math.abs(num).toFixed(decimals);
  if (num > 0.00001) {
    return `+${formatted}%`;
  } else if (num < -0.00001) {
    return `-${formatted}%`;
  } else {
    return `0.00%`;
  }
}

/**
 * Formats a traded price with currency symbol.
 */
export function formatPrice(
  val: number | string | null | undefined,
  currency: string = "USD"
): string {
  if (val === null || val === undefined || val === "") return "—";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) return "—";

  const prefix = currency === "USD" ? "$" : currency === "USDT" ? "$" : `${currency} `;
  if (num >= 1000) {
    return `${prefix}${num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  } else if (num >= 1) {
    return `${prefix}${num.toFixed(2)}`;
  } else {
    return `${prefix}${num.toFixed(4)}`;
  }
}

/**
 * Formats a financial market capitalization value with T/B/M suffixes.
 */
export function formatMarketCap(
  val: number | string | null | undefined,
  unit: string = "USD"
): string {
  if (val === null || val === undefined || val === "") return "N/A";
  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num) || num <= 0) return "N/A";

  const prefix = unit === "USD" || unit === "USDT" ? "$" : `${unit} `;

  if (num >= 1e12) {
    return `${prefix}${(num / 1e12).toFixed(2)}T`;
  } else if (num >= 1e9) {
    return `${prefix}${(num / 1e9).toFixed(1)}B`;
  } else if (num >= 1e6) {
    return `${prefix}${(num / 1e6).toFixed(1)}M`;
  } else {
    return `${prefix}${num.toLocaleString("en-US")}`;
  }
}

/**
 * Formats ISO timestamps cleanly.
 */
export function formatTimestamp(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "—";
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
      timeZone: "UTC",
    }) + " UTC";
  } catch {
    return "—";
  }
}

/**
 * Translates an exclusion reason enum to a human-readable description.
 */
export function describeExclusionReason(reason: HeatmapExclusionReason | string | null | undefined): string {
  switch (reason) {
    case "NO_CURRENT_QUOTE":
      return "Current market quote is missing from authoritative provider";
    case "NO_REFERENCE":
      return "Prior session reference price or settlement is missing";
    case "MISSING_WEIGHT":
      return "Verified market capitalization is unavailable for this instrument";
    case "INVALID_WEIGHT":
      return "Reported market capitalization is non-positive or invalid";
    case "STALE_OBSERVATION":
      return "Observation freshness exceeds allowed tolerance";
    case "INCOMPATIBLE_WINDOW":
      return "Security does not trade within the selected comparison window";
    case "INVALID_DENOMINATOR":
      return "Reference price is zero or negative (cannot compute percentage change)";
    case "INACTIVE_SECURITY":
      return "Security is halted, suspended, or inactive";
    case "NOT_ENTITLED":
      return "User account lacks entitlement to view this market series";
    case "DATA_SOURCE_UNAVAILABLE":
      return "Underlying venue data stream is temporarily unavailable";
    default:
      return "Observation does not meet institutional qualification standards";
  }
}

/**
 * Returns label and badge styling for HeatmapCoverageStatus.
 */
export function describeCoverageStatus(status: HeatmapCoverageStatus | string): {
  label: string;
  badgeClass: string;
  description: string;
} {
  switch (status) {
    case "COMPLETE_FOR_DEFINED_UNIVERSE":
      return {
        label: "Complete",
        badgeClass: "bg-emerald-950/80 text-emerald-400 border-emerald-700/50",
        description: "100% of defined universe candidates are qualified and visualized",
      };
    case "PARTIAL_COVERAGE":
      return {
        label: "Partial",
        badgeClass: "bg-amber-950/80 text-amber-400 border-amber-700/50",
        description: "Some candidates were excluded due to missing quotes, references, or weights",
      };
    case "DEGRADED":
      return {
        label: "Degraded",
        badgeClass: "bg-orange-950/80 text-orange-400 border-orange-700/50",
        description: "Data provider is reporting latency or incomplete snapshots",
      };
    case "UNAVAILABLE":
    default:
      return {
        label: "Unavailable",
        badgeClass: "bg-red-950/80 text-red-400 border-red-700/50",
        description: "No qualified observations found for this universe and configuration",
      };
  }
}
