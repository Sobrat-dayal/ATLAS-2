/**
 * Financial Formatting Utilities for Watchlist Alerts (Stage 80).
 */

import {
  AlertEvaluationStatus,
  AlertRuleType,
  AlertState,
  QuoteMeasure,
  RecurrencePolicy,
} from "./types";

export function formatConditionLabel(ruleType: AlertRuleType): string {
  switch (ruleType) {
    case "PRICE_ABOVE":
      return "Price Is Above";
    case "PRICE_BELOW":
      return "Price Is Below";
    case "CROSSING_ABOVE":
      return "Price Crosses Above";
    case "CROSSING_BELOW":
      return "Price Crosses Below";
    case "PERCENTAGE_CHANGE_ABOVE":
      return "% Change Crosses Above";
    case "PERCENTAGE_CHANGE_BELOW":
      return "% Change Crosses Below";
    default:
      return ruleType;
  }
}

export function formatQuoteMeasure(measure: QuoteMeasure): string {
  switch (measure) {
    case "LAST":
      return "Last Price";
    case "BID":
      return "Bid Price";
    case "ASK":
      return "Ask Price";
    case "MID":
      return "Midpoint";
    case "OPEN":
      return "Session Open";
    case "HIGH":
      return "Session High";
    case "LOW":
      return "Session Low";
    case "CLOSE":
      return "Previous Close";
    case "NAV":
      return "Net Asset Value";
    case "YIELD":
      return "Yield";
    default:
      return measure;
  }
}

export function formatEvaluationStatus(status: AlertEvaluationStatus): {
  label: string;
  variant: "armed" | "triggered" | "cooldown" | "warning" | "neutral";
} {
  switch (status) {
    case "ARMED":
      return { label: "Armed", variant: "armed" };
    case "WAITING_FOR_BASELINE":
      return { label: "Baselining", variant: "neutral" };
    case "TRIGGERED":
      return { label: "Triggered", variant: "triggered" };
    case "COOLDOWN":
      return { label: "Cooldown", variant: "cooldown" };
    case "COMPLETED":
      return { label: "Completed", variant: "neutral" };
    case "DATA_UNAVAILABLE":
      return { label: "Data Unavailable", variant: "warning" };
    case "DEGRADED":
      return { label: "Degraded Feed", variant: "warning" };
    case "ENTITLEMENT_DENIED":
      return { label: "Unauthorized Feed", variant: "warning" };
    case "EXPIRED":
      return { label: "Expired", variant: "neutral" };
    default:
      return { label: status, variant: "neutral" };
  }
}

export function formatAlertState(state: AlertState): {
  label: string;
  badgeClass: string;
} {
  switch (state) {
    case "ENABLED":
      return { label: "Active", badgeClass: "text-emerald-400 bg-emerald-950/60 border-emerald-800" };
    case "PAUSED":
      return { label: "Paused", badgeClass: "text-amber-400 bg-amber-950/60 border-amber-800" };
    case "DISABLED":
      return { label: "Disabled", badgeClass: "text-zinc-400 bg-zinc-900 border-zinc-700" };
    case "EXPIRED":
      return { label: "Expired", badgeClass: "text-rose-400 bg-rose-950/60 border-rose-800" };
    case "DELETED":
      return { label: "Deleted", badgeClass: "text-zinc-500 bg-zinc-950 border-zinc-800" };
    default:
      return { label: state, badgeClass: "text-zinc-400 bg-zinc-900 border-zinc-700" };
  }
}

export function formatRecurrenceLabel(
  recurrence: RecurrencePolicy,
  cooldownSeconds?: number,
): string {
  if (recurrence === "ONE_SHOT") {
    return "One-Shot (Auto-Disables)";
  }
  if (!cooldownSeconds || cooldownSeconds === 0) {
    return "Recurring (No Cooldown)";
  }
  if (cooldownSeconds === 60) return "Recurring (1m Cooldown)";
  if (cooldownSeconds === 300) return "Recurring (5m Cooldown)";
  if (cooldownSeconds === 900) return "Recurring (15m Cooldown)";
  if (cooldownSeconds === 3600) return "Recurring (1h Cooldown)";
  if (cooldownSeconds === 86400) return "Recurring (1d Cooldown)";
  return `Recurring (${cooldownSeconds}s Cooldown)`;
}

export function formatThresholdDisplay(
  threshold: number,
  unit: string,
  ruleType: AlertRuleType,
): string {
  if (
    ruleType === "PERCENTAGE_CHANGE_ABOVE" ||
    ruleType === "PERCENTAGE_CHANGE_BELOW"
  ) {
    const sign = threshold > 0 ? "+" : "";
    return `${sign}${threshold.toFixed(2)}%`;
  }
  return `${threshold.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 6 })} ${unit}`;
}
