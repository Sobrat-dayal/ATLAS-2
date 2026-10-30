"""Typed Error Taxonomy for ATLAS Stage 127: AI Research and Retrieval-Augmented Generation.

Implements all canonical error codes and typed exceptions for source governance,
ingestion, chunking, embeddings, hybrid retrieval, citation verification, and security.
"""

from typing import Any, Dict, Optional


class ResearchError(Exception):
    """Base exception for all AI Research and RAG operations."""

    def __init__(
        self,
        message: str,
        code: str = "RESEARCH_INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# --- Source Governance Errors ---


class ResearchSourceNotFoundError(ResearchError):
    def __init__(self, source_id: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            f"Research source '{source_id}' was not found in the registry.",
            code="RESEARCH_SOURCE_NOT_FOUND",
            details={"source_id": source_id, **(details or {})},
            status_code=404,
        )


class ResearchSourceAccessDeniedError(ResearchError):
    def __init__(self, source_id: str, reason: str = "Unauthorized") -> None:
        super().__init__(
            f"Access to research source '{source_id}' was denied: {reason}",
            code="RESEARCH_SOURCE_ACCESS_DENIED",
            details={"source_id": source_id, "reason": reason},
            status_code=403,
        )


class ResearchSourceLicenseRestrictedError(ResearchError):
    def __init__(self, source_id: str, license_tier: str) -> None:
        super().__init__(
            f"Research source '{source_id}' is restricted under license tier '{license_tier}'.",
            code="RESEARCH_SOURCE_LICENSE_RESTRICTED",
            details={"source_id": source_id, "license_tier": license_tier},
            status_code=403,
        )


class ResearchSourceDisclosureDeniedError(ResearchError):
    def __init__(self, source_id: str, policy: str) -> None:
        super().__init__(
            f"Research source '{source_id}' cannot be transmitted to external providers (Policy: {policy}).",
            code="RESEARCH_SOURCE_DISCLOSURE_DENIED",
            details={"source_id": source_id, "policy": policy},
            status_code=403,
        )


# --- Document & Ingestion Errors ---


class ResearchDocumentNotFoundError(ResearchError):
    def __init__(self, document_id: str) -> None:
        super().__init__(
            f"Research document '{document_id}' was not found.",
            code="RESEARCH_DOCUMENT_NOT_FOUND",
            details={"document_id": document_id},
            status_code=404,
        )


class ResearchDocumentAccessDeniedError(ResearchError):
    def __init__(self, document_id: str, user_id: str) -> None:
        super().__init__(
            f"User '{user_id}' does not have read permissions for document '{document_id}'.",
            code="RESEARCH_DOCUMENT_ACCESS_DENIED",
            details={"document_id": document_id, "user_id": user_id},
            status_code=403,
        )


class ResearchDocumentUnsupportedFormatError(ResearchError):
    def __init__(self, mime_type: str, extension: str) -> None:
        super().__init__(
            f"Unsupported document format '{extension}' ({mime_type}). Only PDF, text, and markdown are accepted.",
            code="RESEARCH_DOCUMENT_UNSUPPORTED_FORMAT",
            details={"mime_type": mime_type, "extension": extension},
            status_code=400,
        )


class ResearchDocumentTooLargeError(ResearchError):
    def __init__(self, size_bytes: int, max_bytes: int) -> None:
        super().__init__(
            f"Document size ({size_bytes} bytes) exceeds maximum allowable limit of {max_bytes} bytes.",
            code="RESEARCH_DOCUMENT_TOO_LARGE",
            details={"size_bytes": size_bytes, "max_bytes": max_bytes},
            status_code=413,
        )


class ResearchDocumentParseFailedError(ResearchError):
    def __init__(self, document_id: str, reason: str) -> None:
        super().__init__(
            f"Failed to parse and extract text structure from document '{document_id}': {reason}",
            code="RESEARCH_DOCUMENT_PARSE_FAILED",
            details={"document_id": document_id, "reason": reason},
            status_code=422,
        )


class ResearchIngestionFailedError(ResearchError):
    def __init__(self, job_id: str, reason: str) -> None:
        super().__init__(
            f"Document ingestion job '{job_id}' failed: {reason}",
            code="RESEARCH_INGESTION_FAILED",
            details={"job_id": job_id, "reason": reason},
            status_code=500,
        )


# --- Embedding & Indexing Errors ---


class ResearchEmbeddingUnavailableError(ResearchError):
    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(
            f"Embedding service provider '{provider}' is currently unavailable: {reason}",
            code="RESEARCH_EMBEDDING_UNAVAILABLE",
            details={"provider": provider, "reason": reason},
            status_code=503,
        )


class ResearchEmbeddingModelMismatchError(ResearchError):
    def __init__(self, expected_dim: int, actual_dim: int) -> None:
        super().__init__(
            f"Embedding dimension mismatch: expected {expected_dim}, got {actual_dim}.",
            code="RESEARCH_EMBEDDING_MODEL_MISMATCH",
            details={"expected_dim": expected_dim, "actual_dim": actual_dim},
            status_code=400,
        )


class ResearchVectorIndexUnavailableError(ResearchError):
    def __init__(self, index_name: str, reason: str) -> None:
        super().__init__(
            f"Vector search index '{index_name}' is unavailable: {reason}",
            code="RESEARCH_VECTOR_INDEX_UNAVAILABLE",
            details={"index_name": index_name, "reason": reason},
            status_code=503,
        )


# --- Retrieval & Search Errors ---


class ResearchQueryInvalidError(ResearchError):
    def __init__(self, query: str, reason: str) -> None:
        super().__init__(
            f"Invalid research query '{query}': {reason}",
            code="RESEARCH_QUERY_INVALID",
            details={"query": query, "reason": reason},
            status_code=400,
        )


class ResearchRetrievalEmptyError(ResearchError):
    def __init__(self, query: str) -> None:
        super().__init__(
            f"No relevant indexed documents or evidence found matching research query '{query}'.",
            code="RESEARCH_RETRIEVAL_EMPTY",
            details={"query": query},
            status_code=404,
        )


class ResearchEvidenceInsufficientError(ResearchError):
    def __init__(self, query: str, missing_aspects: Optional[list] = None) -> None:
        super().__init__(
            f"Retrieved evidence is insufficient to answer query '{query}' without unsupported extrapolation.",
            code="RESEARCH_EVIDENCE_INSUFFICIENT",
            details={"query": query, "missing_aspects": missing_aspects or []},
            status_code=422,
        )


# --- Citation Verification Errors ---


class ResearchCitationInvalidError(ResearchError):
    def __init__(self, citation_id: str, reason: str) -> None:
        super().__init__(
            f"Citation '{citation_id}' is invalid: {reason}",
            code="RESEARCH_CITATION_INVALID",
            details={"citation_id": citation_id, "reason": reason},
            status_code=422,
        )


class ResearchCitationSourceMissingError(ResearchError):
    def __init__(self, citation_id: str, expected_evidence_id: str) -> None:
        super().__init__(
            f"Citation '{citation_id}' references non-existent or fabricated evidence ID '{expected_evidence_id}'.",
            code="RESEARCH_CITATION_SOURCE_MISSING",
            details={"citation_id": citation_id, "expected_evidence_id": expected_evidence_id},
            status_code=404,
        )


class ResearchCitationAccessDeniedError(ResearchError):
    def __init__(self, citation_id: str, document_id: str) -> None:
        super().__init__(
            f"Access to underlying document '{document_id}' for citation '{citation_id}' is revoked or denied.",
            code="RESEARCH_CITATION_ACCESS_DENIED",
            details={"citation_id": citation_id, "document_id": document_id},
            status_code=403,
        )


class ResearchCitationUnsupportedClaimError(ResearchError):
    def __init__(self, citation_id: str, claim: str, span: str) -> None:
        super().__init__(
            f"Claim '{claim}' is not supported by cited source span: '{span}'.",
            code="RESEARCH_CITATION_UNSUPPORTED_CLAIM",
            details={"citation_id": citation_id, "claim": claim, "span": span},
            status_code=422,
        )


# --- Context & Governance Errors ---


class ResearchContextTooLargeError(ResearchError):
    def __init__(self, token_count: int, max_tokens: int) -> None:
        super().__init__(
            f"Assembled research context ({token_count} tokens) exceeds budget ({max_tokens} tokens).",
            code="RESEARCH_CONTEXT_TOO_LARGE",
            details={"token_count": token_count, "max_tokens": max_tokens},
            status_code=400,
        )


class ResearchQuotaExceededError(ResearchError):
    def __init__(self, metric: str, limit: int) -> None:
        super().__init__(
            f"Research quota exceeded for {metric} (limit: {limit}).",
            code="RESEARCH_QUOTA_EXCEEDED",
            details={"metric": metric, "limit": limit},
            status_code=429,
        )

