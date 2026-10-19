/**
 * Financial terminal data formatting utilities for Watchlists V1.
 * Pure, side-effect free, deterministic presentation helpers.
 */

export function formatPrice(
  price: string | null | undefined,
  assetClass?: string,
  currency?: string | null
): string {
  if (currency) {
    // Preserved for quotation currency resolution
  }
  if (price === null || price === undefined || price.trim() === "") {
    return "—";
  }

  const num = parseFloat(price);
  if (isNaN(num)) {
    return price;
  }

  const cls = (assetClass || "").toLowerCase();
  let formatted: string;

  if (cls === "crypto") {
    if (Math.abs(num) < 0.0001) {
      formatted = num.toFixed(8);
    } else if (Math.abs(num) < 1) {
      formatted = num.toFixed(4);
    } else {
      formatted = num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
  } else if (cls === "currency" || cls === "fx") {
    formatted = num.toFixed(4);
  } else if (cls === "bond") {
    formatted = num.toFixed(3);
  } else {
    formatted = num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  return formatted;
}

export function formatChange(
  absoluteChange: string | null | undefined,
  percentageChange: string | null | undefined
): {
  text: string;
  direction: "up" | "down" | "flat" | "unknown";
} {
  if (
    (absoluteChange === null || absoluteChange === undefined || absoluteChange.trim() === "") &&
    (percentageChange === null || percentageChange === undefined || percentageChange.trim() === "")
  ) {
    return { text: "—", direction: "unknown" };
  }

  const absStr = absoluteChange?.trim() || "";
  const pctStr = percentageChange?.trim() || "";

  let direction: "up" | "down" | "flat" | "unknown" = "unknown";

  if (absStr.startsWith("+") || pctStr.startsWith("+")) {
    direction = "up";
  } else if (absStr.startsWith("-") || pctStr.startsWith("-")) {
    direction = "down";
  } else if (absStr === "0" || absStr === "0.00" || pctStr === "0.00%") {
    direction = "flat";
  }

  let text = "";
  if (absStr && pctStr) {
    text = `${absStr} (${pctStr})`;
  } else if (pctStr) {
    text = pctStr;
  } else if (absStr) {
    text = absStr;
  } else {
    text = "—";
  }

  return { text, direction };
}

export function formatObservationTime(timestamp: string | null | undefined): string {
  if (!timestamp) {
    return "—";
  }
  try {
    const d = new Date(timestamp);
    if (isNaN(d.getTime())) {
      return "—";
    }
    const hours = String(d.getUTCHours()).padStart(2, "0");
    const minutes = String(d.getUTCMinutes()).padStart(2, "0");
    const seconds = String(d.getUTCSeconds()).padStart(2, "0");
    return `${hours}:${minutes}:${seconds} UTC`;
  } catch {
    return "—";
  }
}

export function getAssetClassBadge(assetClass: string): { label: string; variant: string } {
  const norm = (assetClass || "").toLowerCase();
  switch (norm) {
    case "equity":
      return { label: "EQUITY", variant: "equity" };
    case "etf":
      return { label: "ETF", variant: "etf" };
    case "crypto":
      return { label: "CRYPTO", variant: "crypto" };
    case "currency":
    case "fx":
      return { label: "FX", variant: "fx" };
    case "bond":
      return { label: "BOND", variant: "bond" };
    case "fund":
      return { label: "FUND", variant: "fund" };
    case "future":
      return { label: "FUTURES", variant: "future" };
    case "commodity":
      return { label: "COMMODITY", variant: "commodity" };
    case "index":
      return { label: "INDEX", variant: "index" };
    default:
      return { label: norm.toUpperCase() || "ASSET", variant: "default" };
  }
}

export function getMarketRouteForAssetClass(assetClass: string): string {
  const norm = (assetClass || "").toLowerCase();
  switch (norm) {
    case "equity":
      return "/markets/equities";
    case "etf":
    case "fund":
      return "/markets/funds";
    case "crypto":
      return "/markets/crypto";
    case "currency":
    case "fx":
      return "/markets/fx";
    case "bond":
      return "/markets/bonds";
    case "future":
      return "/markets/futures";
    default:
      return "/markets";
  }
}
