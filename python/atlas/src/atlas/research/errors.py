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


# ---------------------------------------------------------------------------
# Stage 106 — Research Analysis, Runs, Hypothesis, Findings & Scenario Errors
# ---------------------------------------------------------------------------

class ResearchAnalysisNotFoundError(ResearchDomainError):
    """Raised when a research analysis ID does not exist."""
    pass


class ResearchAnalysisAccessDeniedError(ResearchDomainError):
    """Raised when a user attempts to access an analysis owned by another user."""
    pass


class ResearchAnalysisTypeUnsupportedError(ResearchDomainError):
    """Raised when an requested analysis type is not supported."""
    pass


class ResearchAnalysisConfigurationInvalidError(ResearchDomainError):
    """Raised when an analysis specification fails parameter or schema validation."""
    pass


class ResearchAnalysisRevisionConflictError(ResearchDomainError):
    """Raised when optimistic concurrency detects a stale analysis write."""
    pass


class ResearchAnalysisExecutionFailedError(ResearchDomainError):
    """Raised when analytical execution encounters an unrecoverable failure."""
    pass


class ResearchAnalysisExecutionTimeoutError(ResearchDomainError):
    """Raised when an analytical run exceeds execution runtime limits."""
    pass


class ResearchAnalysisResourceLimitExceededError(ResearchDomainError):
    """Raised when query or data points exceed per-user compute bounds."""
    pass


class ResearchAnalysisMetricUnsupportedError(ResearchDomainError):
    """Raised when an unknown or unsupported financial metric concept is requested."""
    pass


class ResearchAnalysisPeriodIncompatibleError(ResearchDomainError):
    """Raised when financial statement periods cannot be compared meaningfully."""
    pass


class ResearchAnalysisCurrencyMismatchError(ResearchDomainError):
    """Raised when monetary metrics in different currencies are compared without FX conversion."""
    pass


class ResearchAnalysisUnitMismatchError(ResearchDomainError):
    """Raised when incompatible metric dimensional units are combined."""
    pass


class ResearchAnalysisInputUnavailableError(ResearchDomainError):
    """Raised when required canonical input data points are missing or not reported."""
    pass


class ResearchAnalysisLookaheadViolationError(ResearchDomainError):
    """Raised when an analysis requests data published after an explicit as-known-at cutoff."""
    pass


class ResearchAnalysisSampleInsufficientError(ResearchDomainError):
    """Raised when the eligible observation sample is insufficient for statistical validity."""
    pass


class ResearchAnalysisFormulaInvalidError(ResearchDomainError):
    """Raised when a formula definition or expression syntax is invalid."""
    pass


class ResearchAnalysisDivisionByZeroError(ResearchDomainError):
    """Raised when a calculation encounters an unhandled division by zero."""
    pass


class ResearchAnalysisUndefinedGrowthError(ResearchDomainError):
    """Raised when a percentage change or CAGR has an invalid non-positive baseline."""
    pass


class ResearchAnalysisStatisticalTestInvalidError(ResearchDomainError):
    """Raised when statistical test preconditions or assumptions are violated."""
    pass


class ResearchAnalysisRunNotFoundError(ResearchDomainError):
    """Raised when an analysis run ID cannot be found."""
    pass


class ResearchFindingNotFoundError(ResearchDomainError):
    """Raised when a research finding ID cannot be found."""
    pass


class ResearchFindingAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to access or modify a research finding."""
    pass


class ResearchFindingEvidenceMissingError(ResearchDomainError):
    """Raised when a finding lacks required supporting evidence citations."""
    pass


class ResearchFindingRevisionConflictError(ResearchDomainError):
    """Raised when an optimistic concurrency conflict occurs on a research finding."""
    pass


class ResearchHypothesisEvaluationNotFoundError(ResearchDomainError):
    """Raised when a hypothesis evaluation ID cannot be found."""
    pass


class ResearchHypothesisEvaluationInvalidError(ResearchDomainError):
    """Raised when an evaluation configuration or methodology is invalid."""
    pass


class ResearchHypothesisCriteriaUnsupportedError(ResearchDomainError):
    """Raised when testable hypothesis criteria specify unsupported operators or metrics."""
    pass


class ResearchScenarioConfigurationInvalidError(ResearchDomainError):
    """Raised when scenario sensitivity inputs fail range or unit bounds."""
    pass


class ResearchScenarioParameterLimitExceededError(ResearchDomainError):
    """Raised when what-if parameter grid exceeds combinatorial bounds."""
    pass


class ResearchAssumptionNotFoundError(ResearchDomainError):
    """Raised when an assumption ID cannot be found."""
    pass


# ---------------------------------------------------------------------------
# Stage 107 Research Report, Thesis & Export Errors
# ---------------------------------------------------------------------------

class ResearchReportNotFoundError(ResearchDomainError):
    """Raised when a research report ID cannot be found."""
    pass


class ResearchReportAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to access or modify a research report."""
    pass


class ResearchReportTypeUnsupportedError(ResearchDomainError):
    """Raised when an unsupported report type is specified."""
    pass


class ResearchReportTemplateUnavailableError(ResearchDomainError):
    """Raised when a requested report template cannot be found or is inactive."""
    pass


class ResearchReportStructureInvalidError(ResearchDomainError):
    """Raised when report outline or section hierarchy is invalid."""
    pass


class ResearchReportRevisionConflictError(ResearchDomainError):
    """Raised when optimistic concurrency detects a stale report revision write."""
    pass


class ResearchReportStatusInvalidError(ResearchDomainError):
    """Raised when an invalid report status transition is attempted."""
    pass


class ResearchReportFinalizedImmutableError(ResearchDomainError):
    """Raised when attempting to mutate an already finalized report version."""
    pass


class ResearchReportSectionNotFoundError(ResearchDomainError):
    """Raised when a section ID cannot be found in the report."""
    pass


class ResearchReportBlockInvalidError(ResearchDomainError):
    """Raised when a content block has an invalid schema or corrupted structure."""
    pass


class ResearchReportEditorSchemaUnsupportedError(ResearchDomainError):
    """Raised when editor payload schema version is unrecognized."""
    pass


class ResearchReportContentTooLargeError(ResearchDomainError):
    """Raised when report document size exceeds system memory bounds."""
    pass


class ResearchReportCitationInvalidError(ResearchDomainError):
    """Raised when an in-text citation does not resolve to valid evidence."""
    pass


class ResearchReportCitationBrokenError(ResearchDomainError):
    """Raised when a cited source has been withdrawn or corrupted."""
    pass


class ResearchReportSourceWithdrawnError(ResearchDomainError):
    """Raised when attempting to finalize a report citing withdrawn primary sources."""
    pass


class ResearchReportSourceRestrictedError(ResearchDomainError):
    """Raised when an embedded source has redistribution restrictions preventing export."""
    pass


class ResearchReportAnalysisRunNotFoundError(ResearchDomainError):
    """Raised when an embedded analysis run ID cannot be found."""
    pass


class ResearchReportPointInTimeConflictError(ResearchDomainError):
    """Raised when cited observations violate the historical research cutoff date."""
    pass


class ResearchReportExportFormatUnsupportedError(ResearchDomainError):
    """Raised when an unsupported document export format is requested."""
    pass


class ResearchReportExportRestrictedContentError(ResearchDomainError):
    """Raised when content licensing prohibits export or redistribution."""
    pass


class ResearchReportExportTooLargeError(ResearchDomainError):
    """Raised when export document exceeds maximum renderable page or size bounds."""
    pass


class ResearchReportExportFailedError(ResearchDomainError):
    """Raised when background PDF or DOCX generation encounters an unrecoverable error."""
    pass


class ResearchReportExportExpiredError(ResearchDomainError):
    """Raised when attempting to download an expired export artifact."""
    pass


class ResearchReportExportNotFoundError(ResearchDomainError):
    """Raised when an export job ID cannot be found."""
    pass


class ResearchReportExportAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to download an export."""
    pass


class ResearchInvestmentThesisNotFoundError(ResearchDomainError):
    """Raised when an investment thesis ID cannot be found."""
    pass


class ResearchInvestmentThesisAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to access or modify a thesis."""
    pass


class ResearchInvestmentThesisRevisionConflictError(ResearchDomainError):
    """Raised when an optimistic concurrency conflict occurs on a thesis."""
    pass


class ResearchThesisArgumentNotFoundError(ResearchDomainError):
    """Raised when a thesis argument ID cannot be found."""
    pass


# ---------------------------------------------------------------------------
# Stage 108 Collaboration, Review, Comments & Circulation Errors
# ---------------------------------------------------------------------------

class ResearchAccessGrantNotFoundError(ResearchDomainError):
    """Raised when an access grant ID cannot be found."""
    pass


class ResearchAccessGrantForbiddenError(ResearchDomainError):
    """Raised when an unauthorized user attempts to manage access grants."""
    pass


class ResearchAccessRoleInvalidError(ResearchDomainError):
    """Raised when an invalid research role assignment is attempted."""
    pass


class ResearchAccessRevokedError(ResearchDomainError):
    """Raised when attempting an operation under a revoked grant."""
    pass


class ResearchParticipantIneligibleError(ResearchDomainError):
    """Raised when a proposed collaborator or reviewer is not eligible."""
    pass


class ResearchParticipantCrossTenantError(ResearchDomainError):
    """Raised when an operation crosses unauthorized tenant boundaries."""
    pass


class ResearchReviewNotFoundError(ResearchDomainError):
    """Raised when a review request ID cannot be found."""
    pass


class ResearchReviewAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to access or act on a review."""
    pass


class ResearchReviewInvalidTransitionError(ResearchDomainError):
    """Raised when an invalid review state machine transition is attempted."""
    pass


class ResearchReviewSelfApprovalForbiddenError(ResearchDomainError):
    """Raised when an author attempts to approve their own report under separation of duties."""
    pass


class ResearchReviewAlreadyDecidedError(ResearchDomainError):
    """Raised when attempting to decide an already completed or superseded review."""
    pass


class ResearchReviewRevisionMismatchError(ResearchDomainError):
    """Raised when an approval decision targets a stale or modified report revision."""
    pass


class ResearchReviewDuplicateActiveRequestError(ResearchDomainError):
    """Raised when an active review request already exists for the target revision."""
    pass


class ResearchCommentThreadNotFoundError(ResearchDomainError):
    """Raised when a comment thread ID cannot be found."""
    pass


class ResearchCommentNotFoundError(ResearchDomainError):
    """Raised when a specific comment ID cannot be found."""
    pass


class ResearchCommentAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to comment or edit a comment."""
    pass


class ResearchCommentAnchorInvalidError(ResearchDomainError):
    """Raised when a comment anchor references a nonexistent block or section."""
    pass


class ResearchCirculationNotFoundError(ResearchDomainError):
    """Raised when an internal circulation record cannot be found."""
    pass


class ResearchCirculationAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to circulate a report."""
    pass


class ResearchCirculationRevokedError(ResearchDomainError):
    """Raised when attempting to access a report via a revoked circulation grant."""
    pass


class ResearchQualityGateFailedError(ResearchDomainError):
    """Raised when a report fails required blocking quality gates prior to finalization."""
    pass


# ---------------------------------------------------------------------------
# Stage 109 Knowledge, Dependency Lineage, Monitoring & Lifecycle Errors
# ---------------------------------------------------------------------------

class ResearchKnowledgeEntryNotFoundError(ResearchDomainError):
    """Raised when a research knowledge entry ID cannot be found."""
    pass


class ResearchKnowledgeAccessDeniedError(ResearchDomainError):
    """Raised when access to a research knowledge entry is unauthorized."""
    pass


class ResearchKnowledgeTypeUnsupportedError(ResearchDomainError):
    """Raised when attempting to index or query an unsupported knowledge entry type."""
    pass


class ResearchDependencyNotFoundError(ResearchDomainError):
    """Raised when a dependency edge cannot be located."""
    pass


class ResearchDependencyCycleDetectedError(ResearchDomainError):
    """Raised when a cycle is detected during dependency lineage traversal."""
    pass


class ResearchDependencyTraversalLimitError(ResearchDomainError):
    """Raised when lineage traversal exceeds maximum depth or node budget."""
    pass


class ResearchSourceChangeNotFoundError(ResearchDomainError):
    """Raised when a source-change event cannot be found."""
    pass


class ResearchSourceChangeDuplicateError(ResearchDomainError):
    """Raised when attempting to ingest a duplicate source-change event."""
    pass


class ResearchImpactNotFoundError(ResearchDomainError):
    """Raised when an impact assessment record cannot be found."""
    pass


class ResearchRevalidationNotFoundError(ResearchDomainError):
    """Raised when a revalidation result record cannot be found."""
    pass


class ResearchRevalidationAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to trigger revalidation."""
    pass


class ResearchRevalidationTargetUnavailableError(ResearchDomainError):
    """Raised when the target resource for revalidation does not exist."""
    pass


class ResearchUpdateItemNotFoundError(ResearchDomainError):
    """Raised when a research update queue item cannot be found."""
    pass


class ResearchUpdateItemAccessDeniedError(ResearchDomainError):
    """Raised when an unauthorized user attempts to mutate an update queue item."""
    pass


class ResearchUpdateInvalidStateTransitionError(ResearchDomainError):
    """Raised when an update item transition violates the state machine."""
    pass


class ResearchUpdateAlreadyResolvedError(ResearchDomainError):
    """Raised when attempting to re-resolve an already resolved update item without reopening."""
    pass


