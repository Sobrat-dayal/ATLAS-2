/**
 * Formatting utilities for financial action diffs and parameters (Stage 128).
 */

import { ActionLifecycleState, AiActionClassification, ApprovalPolicy } from "./types";

export function formatClassificationBadge(classification: AiActionClassification): {
  label: string;
  colorClass: string;
} {
  switch (classification) {
    case "READ_ONLY":
      return { label: "Read Only", colorClass: "bg-blue-500/10 text-blue-400 border-blue-500/20" };
    case "SESSION_UI_CHANGE":
      return { label: "Session UI", colorClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" };
    case "PERSISTENT_CONFIGURATION_CHANGE":
      return { label: "Persistent Config", colorClass: "bg-amber-500/10 text-amber-400 border-amber-500/20" };
    case "SAVED_ANALYTICAL_DRAFT":
      return { label: "Hypothetical Draft", colorClass: "bg-purple-500/10 text-purple-400 border-purple-500/20" };
    case "COMPUTATION_JOB":
      return { label: "Compute Worker", colorClass: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20" };
    case "FINANCIAL_LEDGER_MUTATION":
    case "BROKER_SIDE_EFFECT":
      return { label: "Prohibited", colorClass: "bg-rose-500/10 text-rose-400 border-rose-500/20" };
    default:
      return { label: classification, colorClass: "bg-neutral-500/10 text-neutral-400 border-neutral-500/20" };
  }
}

export function formatActionStatusBadge(status: ActionLifecycleState): {
  label: string;
  colorClass: string;
} {
  switch (status) {
    case "REQUESTED":
    case "VALIDATING":
      return { label: "Validating", colorClass: "bg-amber-500/10 text-amber-400 border-amber-500/20" };
    case "PREVIEW_READY":
      return { label: "Preview Ready", colorClass: "bg-blue-500/10 text-blue-400 border-blue-500/20" };
    case "APPROVAL_REQUIRED":
      return { label: "Awaiting Approval", colorClass: "bg-amber-500/10 text-amber-400 border-amber-500/20" };
    case "APPROVED":
      return { label: "Approved", colorClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" };
    case "EXECUTING":
    case "QUEUED":
      return { label: "Executing", colorClass: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20" };
    case "COMPLETED":
      return { label: "Completed", colorClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" };
    case "PARTIALLY_COMPLETED":
      return { label: "Partially Succeeded", colorClass: "bg-amber-500/10 text-amber-400 border-amber-500/20" };
    case "FAILED":
      return { label: "Failed", colorClass: "bg-rose-500/10 text-rose-400 border-rose-500/20" };
    case "DENIED":
      return { label: "Denied", colorClass: "bg-neutral-500/10 text-neutral-400 border-neutral-500/20" };
    case "CANCELLED":
      return { label: "Cancelled", colorClass: "bg-neutral-500/10 text-neutral-400 border-neutral-500/20" };
    case "CONFLICTED":
      return { label: "Conflict", colorClass: "bg-rose-500/10 text-rose-400 border-rose-500/20" };
    default:
      return { label: status, colorClass: "bg-neutral-500/10 text-neutral-400 border-neutral-500/20" };
  }
}

