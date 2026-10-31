/**
 * Formatting and Unit Helpers for Financial Exposure (Stage 137).
 */

export function formatCurrencyAmount(
  amount: string | number | null | undefined,
  currency = "USD"
): string {
  if (amount === null || amount === undefined) {
    return "UNAVAILABLE";
  }
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return "UNAVAILABLE";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency || "USD",
    maximumFractionDigits: 2
  }).format(num);
}

export function formatPercentage(
  pct: string | number | null | undefined,
  includeSymbol = true
): string {
  if (pct === null || pct === undefined) {
    return "UNAVAILABLE";
  }
  const num = typeof pct === "string" ? parseFloat(pct) : pct;
  if (isNaN(num)) return "UNAVAILABLE";

  const formatted = num.toFixed(2);
  return includeSymbol ? `${formatted}%` : formatted;
}

export function formatRatio(
  ratio: string | number | null | undefined
): string {
  if (ratio === null || ratio === undefined) return "N/A";
  const num = typeof ratio === "string" ? parseFloat(ratio) : ratio;
  if (isNaN(num)) return "N/A";
  return (num * 100).toFixed(1) + "%";
}

export function formatExposureAmount(
  amount: string | number | null | undefined,
  unit: string,
  currency = "USD"
): string {
  if (amount === null || amount === undefined) return "UNAVAILABLE";

  const u = (unit || "").toUpperCase();
  if (u === "PERCENT") {
    return formatPercentage(amount);
  } else if (u === "COUNT") {
    return `${amount} facilities`;
  } else if (u === "KM" || u === "DISTANCE_KM") {
    return `${amount} km`;
  } else if (u === "QUALITATIVE") {
    return "Documented Qualitative";
  } else {
    return formatCurrencyAmount(amount, currency);
  }
}

