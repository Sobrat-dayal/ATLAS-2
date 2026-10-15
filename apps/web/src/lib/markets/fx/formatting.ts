/**
 * Financial formatting helpers for ATLAS FX Markets V1 (Stage 59).
 */

/**
 * Formats a spot exchange rate preserving required quotation precision.
 * Returns truthful dash if null, undefined, or invalid.
 */
export function formatFxRate(
  rate: string | number | null | undefined,
  precision = 4
): string {
  if (rate === null || rate === undefined || rate === "") return "—";
  const num = typeof rate === "number" ? rate : Number(rate);
  if (isNaN(num)) return "—";

  return num.toLocaleString(undefined, {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  });
}

/**
 * Formats an absolute bid/ask spread.
 */
export function formatFxSpread(
  spreadAbs: string | number | null | undefined,
  precision = 4
): string {
  if (spreadAbs === null || spreadAbs === undefined || spreadAbs === "") return "—";
  const num = typeof spreadAbs === "number" ? spreadAbs : Number(spreadAbs);
  if (isNaN(num)) return "—";

  return num.toLocaleString(undefined, {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  });
}

/**
 * Formats spread in basis points (bps).
 */
export function formatFxSpreadBps(
  spreadBps: string | number | null | undefined
): string {
  if (spreadBps === null || spreadBps === undefined || spreadBps === "") return "—";
  const num = typeof spreadBps === "number" ? spreadBps : Number(spreadBps);
  if (isNaN(num)) return "—";

  return `${num.toLocaleString(undefined, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })} bps`;
}

/**
 * Formats spread in market pips.
 */
export function formatFxSpreadPips(
  spreadPips: string | number | null | undefined
): string {
  if (spreadPips === null || spreadPips === undefined || spreadPips === "") return "—";
  const num = typeof spreadPips === "number" ? spreadPips : Number(spreadPips);
  if (isNaN(num)) return "—";

  return `${num.toLocaleString(undefined, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })} pips`;
}

/**
 * Formats signed 24h percentage return.
 */
export function formatFxChange(
  pct: string | number | null | undefined
): {
  text: string;
  isPositive: boolean;
  isNegative: boolean;
  colorClass: string;
} {
  if (pct === null || pct === undefined || pct === "") {
    return {
      text: "—",
      isPositive: false,
      isNegative: false,
      colorClass: "text-[var(--atlas-text-tertiary)]",
    };
  }

  const num = typeof pct === "number" ? pct : Number(pct);
  if (isNaN(num)) {
    return {
      text: "—",
      isPositive: false,
      isNegative: false,
      colorClass: "text-[var(--atlas-text-tertiary)]",
    };
  }

  const isPositive = num > 0;
  const isNegative = num < 0;
  const prefix = isPositive ? "+" : "";

  let colorClass = "text-[var(--atlas-text-secondary)]";
  if (isPositive) colorClass = "text-emerald-400";
  if (isNegative) colorClass = "text-rose-400";

  return {
    text: `${prefix}${num.toFixed(2)}%`,
    isPositive,
    isNegative,
    colorClass,
  };
}

/**
 * Returns human-readable label for FX Rate Kind.
 */
export function formatRateKind(rateKind: string): string {
  switch (rateKind) {
    case "SPOT_BID_ASK":
      return "Spot Bid/Ask";
    case "INDICATIVE_MID":
      return "Indicative Mid";
    case "REFERENCE_RATE":
      return "Reference Rate";
    case "LAST_TRADE":
      return "Last Observed Trade";
    case "CROSSED_INVALID":
      return "Crossed (Invalid)";
    case "ARITHMETIC_IDENTITY":
      return "Identity (1:1)";
    case "UNKNOWN":
      return "Unknown";
    default:
      return rateKind || "Unknown";
  }
}

/**
 * Returns UI badge styling for quote freshness.
 */
export function formatFxFreshnessBadge(status: string): {
  label: string;
  badgeClass: string;
} {
  switch (status?.toUpperCase()) {
    case "FRESH":
    case "REALTIME":
      return {
        label: "Live / Fresh",
        badgeClass: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
      };
    case "STALE":
      return {
        label: "Stale",
        badgeClass: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
      };
    case "DELAYED":
      return {
        label: "Delayed",
        badgeClass: "bg-blue-500/10 text-blue-400 border border-blue-500/20",
      };
    case "INCONSISTENT":
      return {
        label: "Crossed",
        badgeClass: "bg-rose-500/10 text-rose-400 border border-rose-500/20",
      };
    default:
      return {
        label: status || "Unknown",
        badgeClass: "bg-zinc-800 text-zinc-400 border border-zinc-700",
      };
  }
}

/**
 * Formats a converted money amount to destination currency minor units.
 */
export function formatMoneyAmount(
  amount: string | number | null | undefined,
  minorUnits = 2,
  symbol = ""
): string {
  if (amount === null || amount === undefined || amount === "") return "—";
  const num = typeof amount === "number" ? amount : Number(amount);
  if (isNaN(num)) return "—";

  const formattedNum = num.toLocaleString(undefined, {
    minimumFractionDigits: minorUnits,
    maximumFractionDigits: minorUnits,
  });

  return symbol ? `${symbol}${formattedNum}` : formattedNum;
}

/**
 * Formats observation timestamps cleanly for institutional financial displays.
 */
export function formatObservedTimestamp(isoStr: string | null | undefined): string {
  if (!isoStr) return "—";
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return "—";
    return d.toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return "—";
  }
}
