/**
 * Formatting and presentation utilities for ATLAS Charts V1 (Stage 66).
 *
 * Provides institutional formatting for price values, quotation units,
 * trading volume, percentage changes, dates, and asset class badges.
 */

export function formatPrice(
  value: number | string | null | undefined,
  precision: number = 2
): string {
  if (value === null || value === undefined) return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";

  return num.toLocaleString("en-US", {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision,
  });
}

export function formatVolume(volume: number | string | null | undefined): string {
  if (volume === null || volume === undefined) return "—";
  const num = typeof volume === "string" ? parseFloat(volume) : volume;
  if (isNaN(num)) return "—";

  if (Math.abs(num) >= 1_000_000_000) {
    return `${(num / 1_000_000_000).toFixed(2)}B`;
  }
  if (Math.abs(num) >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(num) >= 1_000) {
    return `${(num / 1_000).toFixed(2)}K`;
  }
  return num.toLocaleString("en-US");
}

export function formatPercentChange(changePercent: number | string | null | undefined): string {
  if (changePercent === null || changePercent === undefined) return "—";
  const num = typeof changePercent === "string" ? parseFloat(changePercent) : changePercent;
  if (isNaN(num)) return "—";

  const prefix = num > 0 ? "+" : "";
  return `${prefix}${num.toFixed(2)}%`;
}

export function formatBarDate(isoDate: string): string {
  if (!isoDate) return "—";
  try {
    const d = new Date(isoDate);
    if (isNaN(d.getTime())) return isoDate;
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      timeZone: "UTC",
    });
  } catch {
    return isoDate;
  }
}

export function formatBarDateTime(isoDate: string): string {
  if (!isoDate) return "—";
  try {
    const d = new Date(isoDate);
    if (isNaN(d.getTime())) return isoDate;
    return d.toISOString().replace(".000Z", "Z").replace("T", " ");
  } catch {
    return isoDate;
  }
}

export function getAssetClassColor(assetClass: string): string {
  switch (assetClass.toLowerCase()) {
    case "equities":
      return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    case "etfs":
      return "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";
    case "fx":
      return "text-amber-400 bg-amber-500/10 border-amber-500/20";
    case "crypto":
      return "text-violet-400 bg-violet-500/10 border-violet-500/20";
    case "bonds":
      return "text-blue-400 bg-blue-500/10 border-blue-500/20";
    case "futures":
      return "text-rose-400 bg-rose-500/10 border-rose-500/20";
    default:
      return "text-zinc-400 bg-zinc-500/10 border-zinc-500/20";
  }
}

export function getAssetClassBadgeLabel(assetClass: string): string {
  switch (assetClass.toLowerCase()) {
    case "equities":
      return "EQUITY";
    case "etfs":
      return "ETF";
    case "fx":
      return "FX SPOT";
    case "crypto":
      return "CRYPTO";
    case "bonds":
      return "SOVEREIGN BOND";
    case "futures":
      return "FUTURES";
    default:
      return assetClass.toUpperCase();
  }
}
