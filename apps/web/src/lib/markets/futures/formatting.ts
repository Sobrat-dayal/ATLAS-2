/**
 * Financial formatting utilities for ATLAS Futures & Commodities Markets V1 (Stage 62).
 */

import { CommodityCategory, SettlementType } from "./types";

const MONTH_NAMES = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

/**
 * Format a futures contract price preserving units and supporting negative values.
 * e.g. "$69.45", "-$37.63", "426.50 ¢", "5,872.25 pts", "$2,685.40".
 */
export function formatFuturesPrice(
  price: string | number | null | undefined,
  quoteUnit?: string,
  currency: string = "USD"
): string {
  if (price === null || price === undefined || price === "") {
    return "—";
  }

  const num = typeof price === "string" ? parseFloat(price) : price;
  if (isNaN(num)) return "—";

  const isNegative = num < 0;
  const absNum = Math.abs(num);

  const unitLower = (quoteUnit || "").toLowerCase();

  // US Cents per bushel or pound (e.g. CBOT Corn, Soybeans, Wheat, Live Cattle)
  if (unitLower.includes("cents")) {
    const formatted = absNum.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 3,
    });
    return isNegative ? `-${formatted} ¢` : `${formatted} ¢`;
  }

  // Index points (e.g. E-mini S&P 500)
  if (unitLower.includes("index points") || unitLower.includes("index")) {
    const formatted = absNum.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    return isNegative ? `-${formatted} pts` : `${formatted} pts`;
  }

  // Natural Gas (USD per MMBtu has 3 decimals)
  if (unitLower.includes("mmbtu")) {
    const formatted = absNum.toLocaleString("en-US", {
      minimumFractionDigits: 3,
      maximumFractionDigits: 3,
    });
    return isNegative ? `-$${formatted}` : `$${formatted}`;
  }

  // Copper (USD per pound has 4 decimals)
  if (unitLower.includes("pound")) {
    const formatted = absNum.toLocaleString("en-US", {
      minimumFractionDigits: 4,
      maximumFractionDigits: 4,
    });
    return isNegative ? `-$${formatted}` : `$${formatted}`;
  }

  // Standard USD commodity quotation (Crude, Gold, Silver)
  const digits = absNum >= 1000 ? 2 : absNum >= 10 ? 2 : 3;
  const formatted = absNum.toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });

  const prefix = currency === "USD" ? "$" : `${currency} `;
  return isNegative ? `-${prefix}${formatted}` : `${prefix}${formatted}`;
}

/**
 * Format qualified same-contract price movement.
 * Suppresses percentage change if reference price was <= 0 to avoid misleading metrics.
 */
export function formatPriceChange(
  changeAbs: string | number | null | undefined,
  changePct: string | number | null | undefined,
  quoteUnit?: string
): string {
  if (changeAbs === null || changeAbs === undefined || changeAbs === "") {
    return "—";
  }

  const absNum =
    typeof changeAbs === "string" ? parseFloat(changeAbs) : changeAbs;
  if (isNaN(absNum)) return "—";

  const isPositive = absNum > 0;
  const sign = isPositive ? "+" : absNum < 0 ? "-" : "";
  const mag = Math.abs(absNum);

  const unitLower = (quoteUnit || "").toLowerCase();
  let formattedMag: string;

  if (unitLower.includes("cents")) {
    formattedMag = `${mag.toFixed(2)} ¢`;
  } else if (unitLower.includes("index points")) {
    formattedMag = `${mag.toFixed(2)} pts`;
  } else if (unitLower.includes("mmbtu")) {
    formattedMag = `$${mag.toFixed(3)}`;
  } else if (unitLower.includes("pound")) {
    formattedMag = `$${mag.toFixed(4)}`;
  } else {
    formattedMag = `$${mag.toFixed(2)}`;
  }

  const formattedAbs = `${sign}${formattedMag}`;

  // If percentage change is suppressed (e.g. reference <= 0), show only absolute change
  if (changePct === null || changePct === undefined || changePct === "") {
    return formattedAbs;
  }

  const pctNum =
    typeof changePct === "string" ? parseFloat(changePct) : changePct;
  if (isNaN(pctNum)) {
    return formattedAbs;
  }

  const pctSign = pctNum > 0 ? "+" : "";
  const formattedPct = `(${pctSign}${pctNum.toFixed(2)}%)`;

  return `${formattedAbs} ${formattedPct}`;
}

/**
 * Color classes for positive/negative price movements.
 */
export function formatPriceChangeClass(
  change: string | number | null | undefined
): string {
  if (change === null || change === undefined) {
    return "text-[var(--atlas-text-secondary)]";
  }
  const num = typeof change === "string" ? parseFloat(change) : change;
  if (isNaN(num) || num === 0) {
    return "text-[var(--atlas-text-secondary)]";
  }
  return num > 0 ? "text-emerald-400" : "text-rose-400";
}

/**
 * Format price change in ticks increments.
 */
export function formatTicksChange(
  ticks: string | number | null | undefined
): string {
  if (ticks === null || ticks === undefined || ticks === "") {
    return "—";
  }
  const num = typeof ticks === "string" ? parseFloat(ticks) : ticks;
  if (isNaN(num)) return "—";
  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(1)} ticks`;
}

/**
 * Convert ISO YYYY-MM to readable month label, e.g. "2026-12" -> "Dec 2026".
 */
export function formatContractMonth(monthStr: string): string {
  if (!monthStr || !monthStr.includes("-")) return monthStr || "—";
  const [year, month] = monthStr.split("-");
  const monthIdx = parseInt(month, 10) - 1;
  if (monthIdx >= 0 && monthIdx < 12) {
    return `${MONTH_NAMES[monthIdx]} ${year}`;
  }
  return monthStr;
}

/**
 * Format a date string (YYYY-MM-DD) into a standard financial date display.
 */
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return "—";
  try {
    const parts = dateStr.split("-");
    if (parts.length === 3) {
      const year = parts[0];
      const monthIdx = parseInt(parts[1], 10) - 1;
      const day = parseInt(parts[2], 10);
      if (monthIdx >= 0 && monthIdx < 12) {
        return `${MONTH_NAMES[monthIdx]} ${day}, ${year}`;
      }
    }
    return dateStr;
  } catch {
    return dateStr;
  }
}

/**
 * Format contract size with its underlying physical units.
 */
export function formatContractSize(
  size: string | number,
  sizeUnit: string
): string {
  const num = typeof size === "string" ? parseFloat(size) : size;
  if (isNaN(num)) return `${size} ${sizeUnit}`;
  return `${num.toLocaleString("en-US")} ${sizeUnit}`;
}

/**
 * Format minimum tick size and verified monetary tick value.
 */
export function formatTickSpecs(
  tickSize: string | number,
  tickValue?: string | number | null,
  currency: string = "USD"
): string {
  const sizeNum = typeof tickSize === "string" ? parseFloat(tickSize) : tickSize;
  const sizeStr = isNaN(sizeNum) ? `${tickSize}` : sizeNum.toString();

  if (tickValue !== null && tickValue !== undefined) {
    const valNum =
      typeof tickValue === "string" ? parseFloat(tickValue) : tickValue;
    if (!isNaN(valNum)) {
      return `${sizeStr} (${currency} $${valNum.toFixed(2)})`;
    }
  }

  return `${sizeStr}`;
}

/**
 * Format settlement method (cash vs physical delivery).
 */
export function formatSettlementType(type: SettlementType): {
  label: string;
  badgeClass: string;
} {
  switch (type) {
    case "physical":
      return {
        label: "Physical Delivery",
        badgeClass: "bg-amber-950/40 text-amber-300 border-amber-800/40",
      };
    case "cash":
      return {
        label: "Cash Settled",
        badgeClass: "bg-blue-950/40 text-blue-300 border-blue-800/40",
      };
    default:
      return {
        label: "Other / Unknown",
        badgeClass: "bg-zinc-800 text-zinc-400 border-zinc-700",
      };
  }
}

/**
 * Format contract volume count.
 */
export function formatVolume(volume?: number | null): string {
  if (volume === null || volume === undefined) {
    return "—";
  }
  return volume.toLocaleString("en-US");
}

/**
 * Format open interest contract count.
 */
export function formatOpenInterest(
  oi?: number | null,
  asOfDate?: string | null
): string {
  if (oi === null || oi === undefined) {
    return "—";
  }
  const formatted = oi.toLocaleString("en-US");
  if (asOfDate) {
    return `${formatted} (as of ${asOfDate})`;
  }
  return formatted;
}

/**
 * Format commodity category label.
 */
export function formatCommodityCategory(category: CommodityCategory): string {
  switch (category) {
    case "energy":
      return "Energy";
    case "precious_metals":
      return "Precious Metals";
    case "industrial_metals":
      return "Industrial Metals";
    case "agriculture":
      return "Agriculture";
    case "soft_commodities":
      return "Soft Commodities";
    case "livestock":
      return "Livestock";
    case "financial_index":
      return "Financial / Index";
    default:
      return category;
  }
}

/**
 * Format observation timestamp for financial provenance.
 */
export function formatObservationTime(isoString?: string | null): string {
  if (!isoString) return "—";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toISOString().replace("T", " ").substring(0, 19) + " UTC";
  } catch {
    return isoString;
  }
}

/**
 * Get CSS badge classes for data freshness.
 */
export function getFreshnessBadgeClass(status?: string): string {
  switch ((status || "").toUpperCase()) {
    case "REALTIME":
      return "bg-emerald-950/40 text-emerald-400 border-emerald-800/40";
    case "DELAYED":
      return "bg-amber-950/40 text-amber-400 border-amber-800/40";
    case "STALE":
      return "bg-rose-950/40 text-rose-400 border-rose-800/40";
    default:
      return "bg-zinc-900 text-zinc-400 border-zinc-800";
  }
}
