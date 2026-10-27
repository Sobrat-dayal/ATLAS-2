/**
 * Formatting and Validation Helpers for Financial Research Platform (Stage 104).
 */

import {
  InvestigationLifecycleStatus,
  ResearchClaimCategory,
} from "./types";

/**
 * Validates whether an external URL is safe and mitigates SSRF / dangerous schemes.
 */
export function isSafeExternalResearchUrl(url?: string | null): boolean {
  if (!url || typeof url !== "string") return false;
  const clean = url.trim().toLowerCase();

  // Allow http / https only
  if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
    return false;
  }

  // Block loopback and metadata endpoints
  if (
    clean.includes("localhost") ||
    clean.includes("127.0.0.1") ||
    clean.includes("0.0.0.0") ||
    clean.includes("169.254.169.254") ||
    clean.includes(".internal")
  ) {
    return false;
  }

  return true;
}

/**
 * Format ISO datetime string to clean standard UTC format.
 */
export function formatResearchDate(isoDateString?: string | null): string {
  if (!isoDateString) return "—";
  try {
    const d = new Date(isoDateString);
    if (isNaN(d.getTime())) return "—";
    return d.toISOString().split("T")[0];
  } catch {
    return "—";
  }
}

/**
 * Returns human-readable label and badge variant for investigation lifecycle status.
 */
export function getInvestigationStatusDisplay(status: InvestigationLifecycleStatus): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (status) {
    case "ACTIVE":
      return { label: "Active", variant: "positive" };
    case "COMPLETED":
      return { label: "Completed", variant: "default" };
    case "ON_HOLD":
      return { label: "On Hold", variant: "warning" };
    case "ARCHIVED":
      return { label: "Archived", variant: "outline" };
    case "DRAFT":
    default:
      return { label: "Draft", variant: "outline" };
  }
}

/**
 * Returns human-readable label and badge variant for claim categories.
 */
export function getClaimCategoryDisplay(category: ResearchClaimCategory): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (category) {
    case "SOURCE_REPORTED_FACT":
      return { label: "Source Fact", variant: "positive" };
    case "ANALYST_INTERPRETATION":
      return { label: "Analyst Interpretation", variant: "primary" };
    case "ESTIMATE":
      return { label: "Estimate", variant: "warning" };
    case "ASSUMPTION":
      return { label: "Assumption", variant: "outline" };
    case "HYPOTHESIS":
      return { label: "Hypothesis", variant: "outline" };
    case "OPEN_QUESTION":
      return { label: "Open Question", variant: "outline" };
  }
}

/**
 * Format citation labels concisely.
 */
export function formatCitationBadge(label: string, isBroken: boolean = false): string {
  if (isBroken) {
    return `[Broken Citation: ${label}]`;
  }
  return label;
}

// ---------------------------------------------------------------------------
// Stage 105 — Financial Delta & Document Intelligence Formatting
// ---------------------------------------------------------------------------

export function formatFinancialDelta(delta: number, currency: string = "USD"): string {
  const sign = delta > 0 ? "+" : delta < 0 ? "-" : "";
  const absVal = Math.abs(delta);
  const formatted = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(absVal);
  return `${sign}${currency === "USD" ? "$" : currency + " "}${formatted}`;
}

export function formatPercentageDelta(pct: number | null | undefined): string {
  if (pct === null || pct === undefined || isNaN(pct)) {
    return "N/A (Zero Base)";
  }
  const sign = pct > 0 ? "+" : pct < 0 ? "" : "";
  return `${sign}${pct.toFixed(2)}%`;
}

export function getDocumentProcessingStatusDisplay(status: string): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (status) {
    case "COMPLETED":
      return { label: "Indexed & Processed", variant: "positive" };
    case "PROCESSING":
      return { label: "Processing...", variant: "primary" };
    case "QUEUED":
      return { label: "Queued", variant: "warning" };
    case "PARTIAL":
      return { label: "Partially Processed", variant: "warning" };
    case "FAILED":
      return { label: "Processing Failed", variant: "negative" };
    case "RESTRICTED":
      return { label: "Restricted Rights", variant: "outline" };
    case "UNSUPPORTED":
      return { label: "Unsupported Format", variant: "outline" };
    case "NOT_STARTED":
    default:
      return { label: "Not Started", variant: "outline" };
  }
}

// ---------------------------------------------------------------------------
// Stage 106 — Research Analysis & Hypothesis Evaluation Formatting
// ---------------------------------------------------------------------------

import {
  AnalysisExecutionStatus,
  HypothesisEvaluationOutcome,
  ResearchAnalysisType,
  ResearchFindingReviewStatus,
  ResearchFindingType,
} from "./types";

export function formatCAGR(cagr: number | null | undefined): string {
  if (cagr === null || cagr === undefined || isNaN(cagr)) {
    return "N/A (Invalid Endpoints)";
  }
  const sign = cagr > 0 ? "+" : "";
  return `${sign}${cagr.toFixed(2)}% CAGR`;
}

export function formatStatisticsValue(val: number | null | undefined, unit: string = ""): string {
  if (val === null || val === undefined || isNaN(val)) {
    return "—";
  }
  const formatted = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(val);
  return unit ? `${formatted} ${unit}` : formatted;
}

export function getHypothesisOutcomeDisplay(outcome: HypothesisEvaluationOutcome): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (outcome) {
    case "CRITERIA_MET":
      return { label: "Criteria Met (Consistent)", variant: "positive" };
    case "CRITERIA_NOT_MET":
      return { label: "Criteria Not Met", variant: "negative" };
    case "MIXED_RESULTS":
      return { label: "Mixed Results", variant: "warning" };
    case "INCONCLUSIVE":
      return { label: "Inconclusive", variant: "outline" };
    case "INSUFFICIENT_DATA":
      return { label: "Insufficient Observations", variant: "outline" };
    case "INVALID_TEST":
      return { label: "Invalid Test Definition", variant: "negative" };
  }
}

export function getAnalysisStatusDisplay(status: AnalysisExecutionStatus): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (status) {
    case "COMPLETED":
      return { label: "Completed", variant: "positive" };
    case "RUNNING":
      return { label: "Computing...", variant: "primary" };
    case "CONFIGURED":
      return { label: "Ready to Run", variant: "default" };
    case "FAILED":
      return { label: "Execution Failed", variant: "negative" };
    case "OUTDATED":
      return { label: "Source Outdated", variant: "warning" };
    case "ARCHIVED":
      return { label: "Archived", variant: "outline" };
    case "DRAFT":
    default:
      return { label: "Draft", variant: "outline" };
  }
}

export function getFindingTypeDisplay(type: ResearchFindingType): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (type) {
    case "OBSERVED_FACT":
      return { label: "Reported Fact", variant: "positive" };
    case "CALCULATED_RESULT":
      return { label: "Calculated Derivation", variant: "primary" };
    case "STATISTICAL_OBSERVATION":
      return { label: "Statistical Result", variant: "default" };
    case "ANALYST_INTERPRETATION":
      return { label: "Analyst Interpretation", variant: "warning" };
    case "INCONCLUSIVE_RESULT":
      return { label: "Inconclusive", variant: "outline" };
  }
}

export function getFindingReviewStatusDisplay(status: ResearchFindingReviewStatus): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (status) {
    case "REVIEWED":
      return { label: "Reviewed & Verified", variant: "positive" };
    case "READY_FOR_REVIEW":
      return { label: "Ready for Review", variant: "primary" };
    case "NEEDS_EVIDENCE":
      return { label: "Needs Citations", variant: "warning" };
    case "REVISED":
      return { label: "Revised", variant: "default" };
    case "ARCHIVED":
      return { label: "Archived", variant: "outline" };
    case "DRAFT":
    default:
      return { label: "Draft", variant: "outline" };
  }
}

export function getAnalysisTypeLabel(type: ResearchAnalysisType): string {
  switch (type) {
    case "COMPANY_FINANCIAL_TREND":
      return "Company Financial Trend";
    case "COMPANY_RATIO_ANALYSIS":
      return "Company Financial Ratios";
    case "CASH_FLOW_ANALYSIS":
      return "Cash Flow Dynamics";
    case "CAPITAL_STRUCTURE_ANALYSIS":
      return "Capital Structure & Leverage";
    case "PEER_BENCHMARKING":
      return "Cross-Sectional Peer Benchmarking";
    case "INDUSTRY_COMPARISON":
      return "Industry Cohort Comparison";
    case "MACROECONOMIC_TIME_SERIES":
      return "Macroeconomic Time Series";
    case "MULTI_INDICATOR_COMPARISON":
      return "Multi-Indicator Macro Context";
    case "HISTORICAL_MARKET_CONTEXT":
      return "Historical Market Context";
    case "EVENT_DISCLOSURE_COMPARISON":
      return "Event Disclosure Chronology";
    case "HYPOTHESIS_EVALUATION":
      return "Deterministic Hypothesis Test";
    case "DESCRIPTIVE_STATISTICAL_ANALYSIS":
      return "Descriptive Statistical Analysis";
    case "ASSUMPTION_SENSITIVITY_ANALYSIS":
      return "Scenario Sensitivity Matrix";
  }
}

