/**
 * Formatting and Validation Helpers for Financial Research Platform (Stage 104).
 */

import {
  InvestigationLifecycleStatus,
  ResearchClaimCategory,
  ResearchEvidenceStatus,
  ResearchHypothesisStatus,
  ResearchNoteType,
  ResearchSourceType,
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
