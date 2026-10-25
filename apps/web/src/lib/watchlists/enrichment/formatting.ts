/**
 * Financial Formatting Utilities for Watchlist Enrichment (Stage 79).
 *
 * Implements strict, high-density financial number presentation:
 * - Millions / Billions scale abbreviations for revenue, market cap, assets.
 * - Precision control: P/E ratios to 1-2 decimal places (30.0x).
 * - Safe null/not-applicable/insufficient-history fallback labels.
 * - Zero divide-by-zero or NaN display.
 */

import { WatchlistRowCellValue } from "../columns/types";

export function formatCompactFinancialNumber(val: number, currency: string = "USD"): string {
  if (isNaN(val) || !isFinite(val)) return "—";

  const absVal = Math.abs(val);
  const sign = val < 0 ? "-" : "";

  let formatted = "";
  if (absVal >= 1e12) {
    formatted = `${(absVal / 1e12).toFixed(2)}T`;
  } else if (absVal >= 1e9) {
    formatted = `${(absVal / 1e9).toFixed(2)}B`;
  } else if (absVal >= 1e6) {
    formatted = `${(absVal / 1e6).toFixed(2)}M`;
  } else if (absVal >= 1e3) {
    formatted = `${(absVal / 1e3).toFixed(2)}K`;
  } else {
    formatted = absVal.toFixed(2);
  }

  const prefix = currency === "USD" ? "$" : `${currency} `;
  return `${sign}${prefix}${formatted}`;
}

export function formatEnrichmentDisplay(
  columnId: string,
  cell?: WatchlistRowCellValue | null
): { text: string; subtext?: string; isDimmed: boolean; colorClass?: string } {
  if (!cell) {
    return { text: "—", isDimmed: true };
  }

  // Handle distinct financial quality and availability statuses
  switch (cell.status) {
    case "NOT_APPLICABLE":
      return {
        text: "N/M",
        subtext: cell.reason ? cell.reason.slice(0, 30) : "Not Applicable",
        isDimmed: true,
      };

    case "INSUFFICIENT_HISTORY":
      return {
        text: "Incomplete",
        subtext: "< 35 bars",
        isDimmed: true,
      };

    case "NOT_ENTITLED":
      return {
        text: "Restricted",
        subtext: "Entitlement Required",
        isDimmed: true,
        colorClass: "text-amber-500/80",
      };

    case "UNAVAILABLE":
    case "ERROR":
      return {
        text: "—",
        subtext: cell.reason ? cell.reason.slice(0, 24) : undefined,
        isDimmed: true,
      };

    case "AVAILABLE":
    case "STALE":
      break;

    default:
      return { text: "—", isDimmed: true };
  }

  const raw = cell.value;
  if (raw === null || raw === undefined) {
    return { text: "—", isDimmed: true };
  }

  // Category-based and column-based exact formatting
  if (columnId.startsWith("fundamentals.")) {
    if (columnId === "fundamentals.eps") {
      const num = typeof raw === "number" ? raw : parseFloat(String(raw));
      if (isNaN(num)) return { text: "—", isDimmed: true };
      const sign = num > 0 ? "$" : num < 0 ? "-$" : "$";
      return {
        text: `${sign}${Math.abs(num).toFixed(2)}`,
        subtext: cell.fiscal_period || undefined,
        isDimmed: false,
      };
    }

    const num = typeof raw === "number" ? raw : parseFloat(String(raw));
    if (isNaN(num)) return { text: "—", isDimmed: true };
    return {
      text: formatCompactFinancialNumber(num, cell.currency || "USD"),
      subtext: cell.fiscal_period || undefined,
      isDimmed: false,
    };
  }

  if (columnId.startsWith("valuation.")) {
    if (columnId === "valuation.market_cap") {
      const num = typeof raw === "number" ? raw : parseFloat(String(raw));
      return {
        text: formatCompactFinancialNumber(num, cell.currency || "USD"),
        isDimmed: false,
      };
    }

    if (columnId === "valuation.dividend_yield") {
      const num = typeof raw === "number" ? raw : parseFloat(String(raw));
      return {
        text: `${num.toFixed(2)}%`,
        isDimmed: false,
        colorClass: "text-emerald-400",
      };
    }

    // P/E, P/B, P/S multiples
    const num = typeof raw === "number" ? raw : parseFloat(String(raw));
    return {
      text: `${num.toFixed(1)}x`,
      isDimmed: false,
    };
  }

  if (columnId.startsWith("technical.")) {
    const num = typeof raw === "number" ? raw : parseFloat(String(raw));
    if (isNaN(num)) return { text: "—", isDimmed: true };

    if (columnId === "technical.rsi_14_1d") {
      let rsiColor = "text-zinc-200";
      if (num >= 70) rsiColor = "text-rose-400 font-semibold";
      else if (num <= 30) rsiColor = "text-emerald-400 font-semibold";

      return {
        text: num.toFixed(2),
        subtext: num >= 70 ? "Overbought" : num <= 30 ? "Oversold" : undefined,
        isDimmed: false,
        colorClass: rsiColor,
      };
    }

    if (columnId === "technical.obv_1d") {
      return {
        text: formatCompactFinancialNumber(num, "").replace("$", ""),
        isDimmed: false,
      };
    }

    if (columnId.includes("macd")) {
      const sign = num > 0 ? "+" : "";
      return {
        text: `${sign}${num.toFixed(2)}`,
        isDimmed: false,
        colorClass: num > 0 ? "text-emerald-400" : num < 0 ? "text-rose-400" : undefined,
      };
    }

    return {
      text: num.toFixed(2),
      isDimmed: false,
    };
  }

  if (columnId.startsWith("events.")) {
    if (columnId === "events.next_earnings_status") {
      const st = String(raw).toUpperCase();
      const isConfirmed = st === "CONFIRMED";
      return {
        text: isConfirmed ? "Confirmed" : "Estimated",
        isDimmed: false,
        colorClass: isConfirmed ? "text-emerald-400 font-medium" : "text-amber-400 font-normal",
      };
    }

    return {
      text: String(raw),
      subtext: cell.event_status ? `(${cell.event_status})` : undefined,
      isDimmed: false,
    };
  }

  if (columnId.startsWith("earnings.")) {
    const num = typeof raw === "number" ? raw : parseFloat(String(raw));
    if (isNaN(num)) return { text: "—", isDimmed: true };

    if (columnId === "earnings.eps_surprise_pct") {
      const sign = num > 0 ? "+" : "";
      return {
        text: `${sign}${num.toFixed(2)}%`,
        isDimmed: false,
        colorClass: num > 0 ? "text-emerald-400 font-semibold" : num < 0 ? "text-rose-400 font-semibold" : undefined,
      };
    }

    return {
      text: `$${num.toFixed(2)}`,
      subtext: cell.fiscal_period || undefined,
      isDimmed: false,
    };
  }

  if (columnId.startsWith("news.")) {
    if (columnId === "news.latest_publication_time") {
      try {
        const d = new Date(String(raw));
        return {
          text: d.toLocaleDateString([], { month: "short", day: "numeric" }),
          subtext: d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          isDimmed: false,
        };
      } catch {
        return { text: String(raw), isDimmed: false };
      }
    }

    return {
      text: String(raw),
      subtext: cell.publisher || undefined,
      isDimmed: false,
    };
  }

  return {
    text: String(raw),
    isDimmed: false,
  };
}
