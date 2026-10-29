/**
 * ATLAS Portfolios V1 — Formatting Helpers and Badge Resolvers.
 */

import {
  QuoteFreshness,
  ReconciliationStatus,
  TransactionType,
  ValuationCompletenessStatus,
} from "./types";

export type BadgeVariant =
  | "default"
  | "primary"
  | "positive"
  | "negative"
  | "warning"
  | "outline";

export function formatCurrency(
  amount: number | string | null | undefined,
  currency: string = "USD"
): string {
  if (amount === null || amount === undefined || amount === "") {
    return "—";
  }
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return "—";

  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency.toUpperCase(),
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  } catch {
    return `${currency} ${num.toFixed(2)}`;
  }
}

export function formatQuantity(qty: number | string | null | undefined): string {
  if (qty === null || qty === undefined || qty === "") return "—";
  const num = typeof qty === "string" ? parseFloat(qty) : qty;
  if (isNaN(num)) return "—";
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 4,
  }).format(num);
}

export function formatPrice(
  price: number | string | null | undefined,
  currency: string = "USD"
): string {
  if (price === null || price === undefined || price === "") return "—";
  const num = typeof price === "string" ? parseFloat(price) : price;
  if (isNaN(num)) return "—";
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency.toUpperCase(),
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(num);
  } catch {
    return `${currency} ${num.toFixed(2)}`;
  }
}

export function formatPnL(
  amount: number | string | null | undefined,
  currency: string = "USD"
): { text: string; isPositive: boolean; isNegative: boolean } {
  if (amount === null || amount === undefined || amount === "") {
    return { text: "—", isPositive: false, isNegative: false };
  }
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return { text: "—", isPositive: false, isNegative: false };

  const formatted = formatCurrency(Math.abs(num), currency);
  if (num > 0) {
    return { text: `+${formatted}`, isPositive: true, isNegative: false };
  } else if (num < 0) {
    return { text: `-${formatted}`, isPositive: false, isNegative: true };
  }
  return { text: formatted, isPositive: false, isNegative: false };
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return (
      d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
      }) + " UTC"
    );
  } catch {
    return dateStr;
  }
}

export function getValuationStatusBadge(
  status: ValuationCompletenessStatus
): { label: string; variant: BadgeVariant } {
  switch (status) {
    case "COMPLETE":
      return { label: "Verified Complete", variant: "positive" };
    case "PARTIAL_MISSING_PRICES":
      return { label: "Missing Prices", variant: "warning" };
    case "PARTIAL_MISSING_FX":
      return { label: "Missing FX Rate", variant: "warning" };
    case "PARTIAL_STALE_DATA":
      return { label: "Stale Prices", variant: "warning" };
    case "UNAVAILABLE":
    case "FAILED":
      return { label: "Valuation Unavailable", variant: "negative" };
    default:
      return { label: status, variant: "default" };
  }
}

export function getTransactionTypeBadge(
  type: TransactionType
): { label: string; variant: BadgeVariant } {
  switch (type) {
    case "BUY":
      return { label: "BUY", variant: "primary" };
    case "SELL":
      return { label: "SELL", variant: "warning" };
    case "CASH_DEPOSIT":
      return { label: "DEPOSIT", variant: "positive" };
    case "CASH_WITHDRAWAL":
      return { label: "WITHDRAW", variant: "negative" };
    case "CASH_DIVIDEND":
      return { label: "DIVIDEND", variant: "positive" };
    case "CASH_INTEREST":
      return { label: "INTEREST", variant: "positive" };
    case "ACCOUNT_FEE":
      return { label: "FEE", variant: "outline" };
    case "WITHHOLDING_TAX":
      return { label: "TAX", variant: "outline" };
    case "STOCK_SPLIT_ADJUSTMENT":
      return { label: "STOCK SPLIT", variant: "primary" };
    case "CORRECTION_REVERSAL":
      return { label: "REVERSAL", variant: "negative" };
    default:
      return { label: type, variant: "default" };
  }
}

export function getQuoteFreshnessBadge(
  freshness: QuoteFreshness
): { label: string; variant: BadgeVariant } {
  switch (freshness) {
    case "REALTIME":
      return { label: "Realtime", variant: "positive" };
    case "DELAYED":
      return { label: "Delayed 15m", variant: "warning" };
    case "END_OF_DAY":
      return { label: "EOD Close", variant: "default" };
    case "HISTORICAL":
      return { label: "Historical", variant: "default" };
    case "STALE":
      return { label: "Stale Mark", variant: "warning" };
    case "UNAVAILABLE":
      return { label: "Unpriced", variant: "negative" };
    default:
      return { label: freshness, variant: "default" };
  }
}

export function getReconciliationBadge(
  status: ReconciliationStatus
): { label: string; variant: BadgeVariant } {
  switch (status) {
    case "RECONCILED":
      return { label: "Reconciled", variant: "positive" };
    case "RECONCILIATION_WARNING":
      return { label: "Warning", variant: "warning" };
    case "OUT_OF_BALANCE":
    case "INCOMPLETE_INPUTS":
      return { label: "Out of Balance", variant: "negative" };
    default:
      return { label: status, variant: "warning" };
  }
}
