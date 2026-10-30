/**
 * Error formatting and code mapping for ATLAS AI Financial Actions (Stage 128).
 */

export const ACTION_ERROR_MAP: Record<string, string> = {
  AI_ACTION_UNSUPPORTED: "The requested financial operation is not supported by the AI Action Engine.",
  AI_ACTION_INVALID_INTENT: "Could not translate your request into a valid financial action.",
  AI_ACTION_AMBIGUOUS_TARGET: "Multiple target resources found. Please specify which resource to modify.",
  AI_ACTION_TARGET_NOT_FOUND: "The requested financial resource was not found.",
  AI_ACTION_ACCESS_DENIED: "You do not have permission to execute this action.",
  AI_ACTION_PROVIDER_DISCLOSURE_DENIED: "Disclosure policy prevents sending sensitive financial data to the AI model.",
  AI_ACTION_SCHEMA_INVALID: "Proposed parameters failed schema validation.",
  AI_ACTION_PARAMETER_UNSUPPORTED: "One or more action parameters are not supported.",
  AI_ACTION_VALIDATION_FAILED: "Action validation failed financial safety checks.",
  AI_ACTION_PREVIEW_UNAVAILABLE: "Preview is temporarily unavailable for this operation.",
  AI_ACTION_PREVIEW_EXPIRED: "Action preview has expired. A fresh preview is required.",
  AI_ACTION_APPROVAL_REQUIRED: "This action requires explicit user confirmation before execution.",
  AI_ACTION_APPROVAL_DENIED: "Action was denied.",
  AI_ACTION_APPROVAL_EXPIRED: "Approval has expired. Please review and confirm again.",
  AI_ACTION_APPROVAL_MISMATCH: "Security alert: Action arguments or target do not match the approved preview.",
  AI_ACTION_REPLAY_DETECTED: "Approval has already been consumed. Replay rejected.",
  AI_ACTION_RESOURCE_CONFLICT: "Resource was modified concurrently. Please generate a fresh preview.",
  AI_ACTION_QUOTA_EXCEEDED: "Action computation quota exceeded for this tenant.",
  AI_ACTION_RATE_LIMITED: "Too many requests. Please wait a moment before trying again.",
  AI_ACTION_EXECUTION_FAILED: "Execution failed during processing on the backend service.",
  AI_ACTION_PARTIAL_COMPLETION: "The multi-step plan partially succeeded. Inspect step receipts for details.",
  AI_ACTION_CANCELLED: "Action was cancelled.",
  AI_ACTION_TIMEOUT: "Action execution timed out.",
  AI_ACTION_UNDO_UNAVAILABLE: "Undo is not supported for this action (e.g. immutable risk runs).",
  AI_ACTION_UNDO_CONFLICT: "Undo failed due to a state conflict.",
  AI_ACTION_SOURCE_UNAVAILABLE: "Required financial data source is temporarily unavailable.",
  AI_ACTION_DATA_QUALITY_INSUFFICIENT: "Data coverage or quality is insufficient for calculation.",
  AI_ACTION_FINANCIAL_CONSTRAINT_FAILED: "Financial constraint violated (e.g. weights do not sum to 100%).",
  AI_ACTION_LEDGER_MUTATION_PROHIBITED: "Direct ledger and cash mutations are strictly prohibited in Stage 128.",
  AI_ACTION_BROKER_EXECUTION_PROHIBITED: "Live broker order execution is prohibited. Only hypothetical scenarios are supported.",
};

export function formatActionError(code?: string, fallback?: string): string {
  if (code && ACTION_ERROR_MAP[code]) {
    return ACTION_ERROR_MAP[code];
  }
  return fallback || "An error occurred while processing the financial action.";
}

