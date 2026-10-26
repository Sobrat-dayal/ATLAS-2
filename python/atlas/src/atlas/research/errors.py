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
