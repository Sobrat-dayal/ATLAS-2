/**
 * Formatting utilities for ATLAS Cryptocurrency Markets V1 (Stage 60).
 *
 * Implements strict, Decimal-safe display helpers for crypto prices,
 * spreads, percentage returns, volume units, and freshness indicators.
 */

/**
 * Format cryptocurrency market price with authoritative precision.
 */
export function formatCryptoPrice(
  price: string | number | null | undefined,
  precision = 2,
  quoteAsset?: string
): string {
  if (price === null || price === undefined || price === "") {
    return "—";
  }

  const num = typeof price === "number" ? price : parseFloat(price);
  if (isNaN(num)) {
    return "—";
  }

  let formatted: string;
  if (precision >= 0) {
    formatted = num.toLocaleString("en-US", {
      minimumFractionDigits: precision,
      maximumFractionDigits: precision,
    });
  } else if (num < 0.0001) {
    formatted = num.toFixed(8);
  } else if (num < 1) {
    formatted = num.toFixed(4);
  } else {
    formatted = num.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  if (quoteAsset) {
    return `${formatted} ${quoteAsset}`;
  }
  return formatted;
}

/**
 * Format absolute bid/ask spread.
 */
export function formatCryptoSpread(
  spread: string | number | null | undefined,
  precision = 2
): string {
  if (spread === null || spread === undefined || spread === "") {
    return "—";
  }

  const num = typeof spread === "number" ? spread : parseFloat(spread);
  if (isNaN(num)) {
    return "—";
  }

  return num.toFixed(precision);
}

/**
 * Format spread in normalized basis points (bps).
 */
export function formatCryptoSpreadBps(bps: string | number | null | undefined): string {
  if (bps === null || bps === undefined || bps === "") {
    return "—";
  }

  const num = typeof bps === "number" ? bps : parseFloat(bps);
  if (isNaN(num)) {
    return "—";
  }

  return `${num.toFixed(1)} bps`;
}

/**
 * Format signed 24h percentage price change.
 */
export function formatCryptoChange(changePct: string | number | null | undefined): {
  text: string;
  isPositive: boolean;
  isNegative: boolean;
  colorClass: string;
} {
  if (changePct === null || changePct === undefined || changePct === "") {
    return {
      text: "—",
      isPositive: false,
      isNegative: false,
      colorClass: "text-[var(--atlas-text-secondary)]",
    };
  }

  const num = typeof changePct === "number" ? changePct : parseFloat(changePct);
  if (isNaN(num)) {
    return {
      text: "—",
      isPositive: false,
      isNegative: false,
      colorClass: "text-[var(--atlas-text-secondary)]",
    };
  }

  if (num > 0) {
    return {
      text: `+${num.toFixed(2)}%`,
      isPositive: true,
      isNegative: false,
      colorClass: "text-emerald-400",
    };
  }

  if (num < 0) {
    return {
      text: `${num.toFixed(2)}%`,
      isPositive: false,
      isNegative: true,
      colorClass: "text-rose-400",
    };
  }

  return {
    text: "0.00%",
    isPositive: false,
    isNegative: false,
    colorClass: "text-[var(--atlas-text-secondary)]",
  };
}

/**
 * Format reported 24h trading volume preserving explicit base or quote units.
 */
export function formatCryptoVolume(
  volume: string | number | null | undefined,
  unit?: string
): string {
  if (volume === null || volume === undefined || volume === "") {
    return "—";
  }

  const num = typeof volume === "number" ? volume : parseFloat(volume);
  if (isNaN(num)) {
    return "—";
  }

  let formatted: string;
  if (num >= 1_000_000_000) {
    formatted = `${(num / 1_000_000_000).toFixed(2)}B`;
  } else if (num >= 1_000_000) {
    formatted = `${(num / 1_000_000).toFixed(2)}M`;
  } else if (num >= 1_000) {
    formatted = `${(num / 1_000).toFixed(1)}K`;
  } else {
    formatted = num.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }

  if (unit) {
    return `${formatted} ${unit}`;
  }
  return formatted;
}

/**
 * Format rate observation classification badge.
 */
export function formatCryptoRateKind(kind: string | null | undefined): {
  label: string;
  badgeClass: string;
} {
  switch (kind) {
    case "SPOT_TRADE":
      return {
        label: "Spot Trade",
        badgeClass: "bg-emerald-950/40 text-emerald-300 border-emerald-800/40",
      };
    case "BID_ASK_QUOTE":
      return {
        label: "Bid / Ask",
        badgeClass: "bg-cyan-950/40 text-cyan-300 border-cyan-800/40",
      };
    case "INDICATIVE_COMPOSITE":
      return {
        label: "Composite",
        badgeClass: "bg-blue-950/40 text-blue-300 border-blue-800/40",
      };
    case "CROSSED_INVALID":
      return {
        label: "Crossed (Invalid)",
        badgeClass: "bg-rose-950/40 text-rose-300 border-rose-800/40",
      };
    default:
      return {
        label: "Indicative",
        badgeClass: "bg-zinc-800 text-zinc-400 border-zinc-700/50",
      };
  }
}

/**
 * Format observation freshness badge.
 */
export function formatCryptoFreshnessBadge(status: string | null | undefined): {
  label: string;
  badgeClass: string;
} {
  switch (status?.toUpperCase()) {
    case "FRESH":
      return {
        label: "Live",
        badgeClass: "bg-emerald-950/60 text-emerald-400 border-emerald-800/50",
      };
    case "DELAYED":
      return {
        label: "Delayed",
        badgeClass: "bg-sky-950/60 text-sky-400 border-sky-800/50",
      };
    case "STALE":
      return {
        label: "Stale",
        badgeClass: "bg-amber-950/60 text-amber-400 border-amber-800/50",
      };
    default:
      return {
        label: "Unknown",
        badgeClass: "bg-zinc-800 text-zinc-400 border-zinc-700/50",
      };
  }
}

/**
 * Format ISO timestamp into clean financial terminal representation.
 */
export function formatObservedTimestamp(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "—";
    return d.toISOString().replace("T", " ").substring(0, 19) + " UTC";
  } catch {
    return "—";
  }
}
