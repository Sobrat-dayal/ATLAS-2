/**
 * Formatting and Validation Helpers for Financial Research Platform (Stage 104).
 */

import {
  InvestigationLifecycleStatus,
  ResearchClaimCategory,
  AnalysisExecutionStatus,
  ResearchFindingType,
  ResearchFindingReviewStatus,
  ResearchAnalysisType,
  // Stage 107 Types
  ResearchReportType,
  ReportLifecycleStatus,
  ThesisLifecycleStatus,
  ThesisArgumentType,
  ExportFormat,
  VerificationIssueSeverity,
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
  HypothesisEvaluationOutcome,
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

export function getReportStatusDisplay(status: ReportLifecycleStatus): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (status) {
    case "FINALIZED":
      return { label: "Finalized", variant: "positive" };
    case "PUBLISHED":
      return { label: "Published", variant: "positive" };
    case "UNDER_REVIEW":
      return { label: "Under Review", variant: "warning" };
    case "ARCHIVED":
      return { label: "Archived", variant: "outline" };
    case "SUPERSEDED":
      return { label: "Superseded", variant: "negative" };
    case "DRAFT":
    default:
      return { label: "Draft", variant: "outline" };
  }
}

export function getReportTypeDisplay(type: ResearchReportType): string {
  switch (type) {
    case "COMPANY_RESEARCH":
      return "Company Research Report";
    case "EQUITY_INITIATION":
      return "Equity Initiation Coverage";
    case "EARNINGS_REVIEW":
      return "Earnings Review Note";
    case "MACROECONOMIC_REPORT":
      return "Macroeconomic Outlook";
    case "INDUSTRY_PRIMER":
      return "Industry Primer";
    case "INVESTMENT_THESIS":
      return "Investment Thesis Memo";
    case "EVENT_MEMO":
      return "Event Reaction Memo";
    case "RISK_BRIEF":
      return "Risk Assessment Brief";
    case "CUSTOM":
    default:
      return "Custom Research Report";
  }
}

export function getThesisStatusDisplay(status: ThesisLifecycleStatus): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (status) {
    case "ACTIVE":
      return { label: "Active Thesis", variant: "positive" };
    case "VALIDATED":
      return { label: "Validated", variant: "primary" };
    case "DISPROVEN":
      return { label: "Disproven", variant: "negative" };
    case "UNDER_REVIEW":
      return { label: "Under Review", variant: "warning" };
    case "ARCHIVED":
      return { label: "Archived", variant: "outline" };
    case "DRAFT":
    default:
      return { label: "Draft", variant: "outline" };
  }
}

export function getThesisArgumentTypeDisplay(type: ThesisArgumentType): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (type) {
    case "BULL_CASE":
      return { label: "Bull Case", variant: "positive" };
    case "BEAR_CASE":
      return { label: "Bear Case", variant: "negative" };
    case "BASE_CASE":
      return { label: "Base Case", variant: "primary" };
    case "CATALYST":
      return { label: "Catalyst", variant: "warning" };
    case "KEY_RISK":
      return { label: "Key Risk", variant: "negative" };
    case "CORE_ASSUMPTION":
      return { label: "Core Assumption", variant: "default" };
    case "CONTRADICTING_EVIDENCE":
      return { label: "Contradiction", variant: "outline" };
    default:
      return { label: type, variant: "default" };
  }
}

export function getExportFormatDisplay(format: ExportFormat): string {
  switch (format) {
    case "PDF":
      return "Institutional PDF";
    case "DOCX":
      return "Office Word (DOCX)";
    case "HTML":
      return "Self-Contained HTML";
    case "MARKDOWN":
      return "Research Markdown";
    case "JSON_ARCHIVE":
      return "Point-in-Time JSON Archive";
    default:
      return format;
  }
}

export function getVerificationSeverityDisplay(severity: VerificationIssueSeverity): {
  label: string;
  variant: "default" | "primary" | "positive" | "negative" | "warning" | "outline";
} {
  switch (severity) {
    case "BLOCKING":
      return { label: "Blocking Violation", variant: "negative" };
    case "WARNING":
      return { label: "Warning", variant: "warning" };
    case "INFORMATIONAL":
    default:
      return { label: "Info", variant: "outline" };
  }
}

