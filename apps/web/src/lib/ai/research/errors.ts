/**
 * Typed Error formatting for Stage 127 AI Research.
 */

export const RESEARCH_ERROR_MESSAGES: Record<string, string> = {
  RESEARCH_SOURCE_NOT_FOUND: "The requested research source was not found in the catalog.",
  RESEARCH_SOURCE_ACCESS_DENIED: "You do not have permission to access this research source.",
  RESEARCH_SOURCE_LICENSE_RESTRICTED: "Access to this source is restricted by institutional licensing.",
  RESEARCH_SOURCE_DISCLOSURE_DENIED: "This document cannot be disclosed to external model providers.",
  RESEARCH_DOCUMENT_NOT_FOUND: "The requested document was not found.",
  RESEARCH_DOCUMENT_ACCESS_DENIED: "Access to this document is denied or has been revoked.",
  RESEARCH_DOCUMENT_UNSUPPORTED_FORMAT: "Unsupported document format. Please upload PDF, TXT, or MD.",
  RESEARCH_DOCUMENT_TOO_LARGE: "The document exceeds the maximum allowable size (50MB).",
  RESEARCH_RETRIEVAL_EMPTY: "No indexed passages matched your query.",
  RESEARCH_EVIDENCE_INSUFFICIENT: "Sufficient evidence was not found to answer this query without hallucination.",
  RESEARCH_CITATION_INVALID: "The citation reference could not be verified against authorized evidence.",
  RESEARCH_CITATION_SOURCE_MISSING: "The citation references a non-existent source.",
  RESEARCH_CITATION_ACCESS_DENIED: "Access to the underlying document for this citation is restricted.",
};

export function formatResearchError(code?: string, fallbackMessage?: string): string {
  if (code && RESEARCH_ERROR_MESSAGES[code]) {
    return RESEARCH_ERROR_MESSAGES[code];
  }
  return fallbackMessage || "An error occurred during AI research retrieval.";
}

