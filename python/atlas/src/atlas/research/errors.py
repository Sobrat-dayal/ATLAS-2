"""Typed Error Hierarchy for Institutional Financial Research Platform (Stage 104)."""


class ResearchDomainError(Exception):
    """Base exception for all research domain errors."""
    pass


# ---------------------------------------------------------------------------
# Legacy Stage 36 Errors (Preserved for backwards compatibility)
# ---------------------------------------------------------------------------

class ResearchDocumentNotFoundError(ResearchDomainError):
    pass


class ResearchDocumentDataInconsistentError(ResearchDomainError):
    pass


class InvalidResearchDocumentKindError(ResearchDomainError):
    pass


class InvalidDocumentLanguageError(ResearchDomainError):
    pass


class AbstractTooLargeError(ResearchDomainError):
    pass


# ---------------------------------------------------------------------------
# Stage 104 Research Investigation Errors
# ---------------------------------------------------------------------------

class ResearchInvestigationNotFoundError(ResearchDomainError):
    """Raised when an investigation ID does not exist."""
    pass


class ResearchInvestigationAccessDeniedError(ResearchDomainError):
    """Raised when a user attempts to access an investigation owned by another principal."""
    pass


class ResearchInvestigationRevisionConflictError(ResearchDomainError):
    """Raised when optimistic concurrency detects a stale revision write."""
    pass


class ResearchInvestigationInvalidStateError(ResearchDomainError):
    """Raised when an invalid state transition is requested."""
    pass


# ---------------------------------------------------------------------------
# Stage 104 Research Question & Hypothesis Errors
# ---------------------------------------------------------------------------

class ResearchQuestionNotFoundError(ResearchDomainError):
    """Raised when a research question ID does not exist."""
    pass


class ResearchHypothesisNotFoundError(ResearchDomainError):
    """Raised when a hypothesis ID does not exist."""
    pass


# ---------------------------------------------------------------------------
# Stage 104 Research Note & Claim Errors
# ---------------------------------------------------------------------------

class ResearchNoteNotFoundError(ResearchDomainError):
    """Raised when a research note ID does not exist."""
    pass


class ResearchNoteAccessDeniedError(ResearchDomainError):
    """Raised when a user attempts to access a note owned by another principal."""
    pass


class ResearchNoteRevisionConflictError(ResearchDomainError):
    """Raised when optimistic concurrency detects a concurrent note edit conflict."""
    pass


class ResearchNoteContentInvalidError(ResearchDomainError):
    """Raised when note content fails length or safety validation."""
    pass


class ResearchClaimNotFoundError(ResearchDomainError):
    """Raised when a claim ID does not exist."""
    pass


# ---------------------------------------------------------------------------
# Stage 104 Research Source & Evidence Errors
# ---------------------------------------------------------------------------

class ResearchSourceNotFoundError(ResearchDomainError):
    """Raised when a source reference ID does not exist."""
    pass


class ResearchSourceRestrictedError(ResearchDomainError):
    """Raised when source licensing or user entitlement restricts access."""
    pass


class ResearchSourceUnavailableError(ResearchDomainError):
    """Raised when a cited source document is unavailable."""
    pass


class ResearchSourceWithdrawnError(ResearchDomainError):
    """Raised when an upstream source has been withdrawn, corrected, or retracted."""
    pass


class ResearchSourceDuplicateError(ResearchDomainError):
    """Raised when an exact duplicate source link already exists."""
    pass


class ResearchSourceUrlUnsafeError(ResearchDomainError):
    """Raised when a user-supplied external URL fails SSRF or scheme validation."""
    pass


class ResearchSourceTypeUnsupportedError(ResearchDomainError):
    """Raised when an unknown or unsupported source type is supplied."""
    pass


class ResearchEvidenceNotFoundError(ResearchDomainError):
    """Raised when an evidence ID does not exist."""
    pass


class ResearchEvidenceSourceMissingError(ResearchDomainError):
    """Raised when evidence references a nonexistent source document."""
    pass


class ResearchEvidenceLocationInvalidError(ResearchDomainError):
    """Raised when a citation location (page/section) is invalid or fabricated."""
    pass


class ResearchEvidenceContentRestrictedError(ResearchDomainError):
    """Raised when evidence text exceeds permissible quotation bounds."""
    pass


class ResearchCitationInvalidError(ResearchDomainError):
    """Raised when citation syntax or parameters are invalid."""
    pass


class ResearchCitationBrokenError(ResearchDomainError):
    """Raised when a citation references a withdrawn or missing target."""
    pass


class ResearchEntityNotFoundError(ResearchDomainError):
    """Raised when a requested canonical entity cannot be resolved."""
    pass


class ResearchSearchQueryInvalidError(ResearchDomainError):
    """Raised when a search query is malformed or invalid."""
    pass


# ---------------------------------------------------------------------------
# Stage 105 Document Intelligence & Comparison Errors
# ---------------------------------------------------------------------------

class ResearchDiscoveryQueryInvalidError(ResearchDomainError):
    """Raised when a discovery query or filter set is invalid or exceeds bounds."""
    pass


class ResearchDocumentContentUnavailableError(ResearchDomainError):
    """Raised when document content is unavailable or restricted by licensing."""
    pass


class ResearchDocumentProcessingPendingError(ResearchDomainError):
    """Raised when document parsing or indexing is still in progress."""
    pass


class ResearchDocumentProcessingFailedError(ResearchDomainError):
    """Raised when document parsing encountered unrecoverable errors."""
    pass


class ResearchDocumentFormatUnsupportedError(ResearchDomainError):
    """Raised when an uploaded or referenced document format is not supported."""
    pass


class ResearchDocumentSectionNotFoundError(ResearchDomainError):
    """Raised when a requested document section does not exist."""
    pass


class ResearchDocumentSpanInvalidError(ResearchDomainError):
    """Raised when a character span offset or length is invalid or fabricated."""
    pass


class ResearchDocumentTableNotFoundError(ResearchDomainError):
    """Raised when a requested extracted financial table does not exist."""
    pass


class ResearchEvidenceCandidateNotFoundError(ResearchDomainError):
    """Raised when an evidence candidate does not exist or has already been converted."""
    pass


class ResearchComparisonIncompatibleError(ResearchDomainError):
    """Raised when two documents or metrics are incompatible for comparison."""
    pass


class ResearchComparisonResourceLimitError(ResearchDomainError):
    """Raised when a comparison request exceeds processing size or line limits."""
    pass


class ResearchSemanticSearchUnavailableError(ResearchDomainError):
    """Raised when semantic retrieval is requested but unavailable or unlicensed."""
    pass
