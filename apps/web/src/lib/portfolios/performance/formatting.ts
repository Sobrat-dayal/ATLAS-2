/**
 * ATLAS Portfolios V1 — Performance Formatting Utilities (Stage 111).
 */

import { CashFlowClassification, DataCompletenessStatus } from "./types";

export function formatRate(
  rate: number | string | null | undefined,
  options: {
    showSign?: boolean;
    decimals?: number;
    fallback?: string;
  } = {}
): string {
  const { showSign = true, decimals = 2, fallback = "--" } = options;

  if (rate === null || rate === undefined || rate === "") {
    return fallback;
  }

  const num = typeof rate === "string" ? parseFloat(rate) : rate;
  if (isNaN(num)) {
    return fallback;
  }

  const pct = num * 100;
  const formatted = pct.toFixed(decimals);

  if (showSign && pct > 0) {
    return `+${formatted}%`;
  }
  return `${formatted}%`;
}

export function formatCurrency(
  val: number | string | null | undefined,
  currency = "USD",
  options: { decimals?: number; fallback?: string } = {}
): string {
  const { decimals = 2, fallback = "--" } = options;

  if (val === null || val === undefined || val === "") {
    return fallback;
  }

  const num = typeof val === "string" ? parseFloat(val) : val;
  if (isNaN(num)) {
    return fallback;
  }

  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  } catch {
    return `${currency} ${num.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })}`;
  }
}

export function getCompletenessBadge(status: DataCompletenessStatus): {
  label: string;
  variant: "default" | "warning" | "primary" | "positive" | "negative" | "outline";
  description: string;
} {
  switch (status) {
    case "COMPLETE":
      return {
        label: "Verified Complete",
        variant: "positive",
        description: "All historical marks, exchange rates, and cash flows verified.",
      };
    case "COMPLETE_WITH_STALE_MARKS":
      return {
        label: "Verified (Stale Marks)",
        variant: "warning",
        description: "Calculation verified with some previous-close or stale prices.",
      };
    case "PARTIAL_MISSING_PRICES":
      return {
        label: "Partial (Missing Prices)",
        variant: "negative",
        description: "Some positions lacked verified marks; unpriced assets held at 0 gain.",
      };
    case "PARTIAL_MISSING_VALUATION":
      return {
        label: "Partial (Missing Valuation)",
        variant: "negative",
        description: "Valuation point could not be resolved at subperiod boundary.",
      };
    case "EMPTY":
      return {
        label: "Empty Ledger",
        variant: "default",
        description: "No eligible trades or cash flows in this period.",
      };
    default:
      return {
        label: status,
        variant: "default",
        description: "",
      };
  }
}

export function getCashFlowClassificationBadge(classification: CashFlowClassification): {
  label: string;
  isExternal: boolean;
  colorClass: string;
} {
  switch (classification) {
    case "EXTERNAL_CONTRIBUTION":
      return {
        label: "External Contribution",
        isExternal: true,
        colorClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      };
    case "EXTERNAL_WITHDRAWAL":
      return {
        label: "External Withdrawal",
        isExternal: true,
        colorClass: "bg-blue-500/10 text-blue-400 border-blue-500/20",
      };
    case "INTERNAL_SECURITY_TRADE":
      return {
        label: "Security Trade (Internal)",
        isExternal: false,
        colorClass: "bg-slate-500/10 text-slate-400 border-slate-500/20",
      };
    case "INTERNAL_INCOME":
      return {
        label: "Dividend / Income (Internal)",
        isExternal: false,
        colorClass: "bg-purple-500/10 text-purple-400 border-purple-500/20",
      };
    case "INTERNAL_FEE":
      return {
        label: "Portfolio Fee (Internal)",
        isExternal: false,
        colorClass: "bg-amber-500/10 text-amber-400 border-amber-500/20",
      };
    case "INTERNAL_TRANSFER":
      return {
        label: "Inter-Account Transfer",
        isExternal: false,
        colorClass: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
      };
    case "CORPORATE_ACTION_NONCASH":
      return {
        label: "Corporate Action",
        isExternal: false,
        colorClass: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
      };
    default:
      return {
        label: classification,
        isExternal: false,
        colorClass: "bg-slate-500/10 text-slate-400 border-slate-500/20",
      };
  }
}
