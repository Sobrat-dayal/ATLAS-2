/**
 * ATLAS Stage 58 - ETFs & Funds Markets V1
 * Formatting & Presentation Utilities
 *
 * Strict financial-data integrity rules:
 * - Market Last price and Official NAV must never be conflated.
 * - Missing values are rendered as "—" or explicit descriptive unavailable states, never "0.00%".
 * - Currencies and valuation dates must be clearly labeled.
 */

export function formatFundPrice(
  priceStr?: string | null,
  currency?: string | null
): string {
  if (!priceStr) return "—";
  const num = parseFloat(priceStr);
  if (isNaN(num)) return "—";

  const formatted = num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return currency ? `${formatted} ${currency}` : formatted;
}

export function formatFundNAV(
  navStr?: string | null,
  currency?: string | null
): string {
  if (!navStr) return "—";
  const num = parseFloat(navStr);
  if (isNaN(num)) return "—";

  const formatted = num.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  });

  return currency ? `${formatted} ${currency}` : formatted;
}

export function formatExpenseRatio(
  feeStr?: string | null,
  scale = "percentage"
): string {
  if (!feeStr) return "—";
  const num = parseFloat(feeStr);
  if (isNaN(num)) return "—";

  // If already a percentage (e.g. 0.09 means 0.09%)
  if (scale === "percentage") {
    return `${num.toFixed(2)}%`;
  }
  // If decimal fraction (e.g. 0.0009 means 0.09%)
  return `${(num * 100).toFixed(2)}%`;
}

export function formatAUM(
  amountStr?: string | null,
  currency?: string | null
): string {
  if (!amountStr) return "—";
  const num = parseFloat(amountStr);
  if (isNaN(num) || num <= 0) return "—";

  let formatted = "";
  if (num >= 1_000_000_000_000) {
    formatted = `${(num / 1_000_000_000_000).toFixed(2)}T`;
  } else if (num >= 1_000_000_000) {
    formatted = `${(num / 1_000_000_000).toFixed(2)}B`;
  } else if (num >= 1_000_000) {
    formatted = `${(num / 1_000_000).toFixed(2)}M`;
  } else if (num >= 1_000) {
    formatted = `${(num / 1_000).toFixed(2)}K`;
  } else {
    formatted = num.toLocaleString("en-US", { maximumFractionDigits: 0 });
  }

  return currency ? `${formatted} ${currency}` : formatted;
}

export function formatFundChange(
  changePct?: string | null
): { text: string; colorClass: string; isPositive: boolean; isNegative: boolean } {
  if (!changePct) {
    return {
      text: "—",
      colorClass: "text-[var(--atlas-text-secondary)]",
      isPositive: false,
      isNegative: false,
    };
  }

  const num = parseFloat(changePct);
  if (isNaN(num)) {
    return {
      text: "—",
      colorClass: "text-[var(--atlas-text-secondary)]",
      isPositive: false,
      isNegative: false,
    };
  }

  const isPositive = num > 0;
  const isNegative = num < 0;
  const sign = isPositive ? "+" : "";
  const text = `${sign}${num.toFixed(2)}%`;

  const colorClass = isPositive
    ? "text-emerald-400 font-mono"
    : isNegative
    ? "text-rose-400 font-mono"
    : "text-[var(--atlas-text-secondary)] font-mono";

  return { text, colorClass, isPositive, isNegative };
}

export function formatValuationDate(dateStr?: string | null): string {
  if (!dateStr) return "Unavailable";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}
