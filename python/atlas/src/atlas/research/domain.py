"""Domain Models for Institutional Financial Research Platform (Stage 104)."""

import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from atlas.research.enums import (
    AnalysisExecutionStatus,
    AnalysisFrequency,
    AnalysisInputPolicy,
    AssumptionSourceType,
    CirculationStatus,
    ClaimEvidenceRelationship,
    CommentAnchorType,
    CommentThreadStatus,
    DependencyType,
    DocumentComparisonMode,
    DocumentFormat,
    DocumentProcessingStatus,
    EvidenceLocationType,
    ExportFormat,
    ExportStatus,
    HypothesisEvaluationOutcome,
    ImpactCategory,
    InvestigationLifecycleStatus,
    KnowledgeEntryType,
    KnowledgeSourceAvailability,
    KnowledgeStatus,
    OutlierHandlingPolicy,
    ReportBlockType,
    ReportLifecycleStatus,
    ReportSectionType,
    ReportSnapshotPolicy,
    ResearchActivityAction,
    ResearchAnalysisType,
    ResearchAuditEventType,
    ResearchClaimCategory,
    ResearchEvidenceStatus,
    ResearchFindingReviewStatus,
    ResearchFindingType,
    ResearchHypothesisStatus,
    ResearchNoteStatus,
    ResearchNoteType,
    ResearchPrincipalType,
    ResearchQuestionStatus,
    ResearchReportType,
    ResearchResourceType,
    ResearchRole,
    ResearchSourceType,
    ResearchType,
    RevalidationOutcome,
    RevalidationStatus,
    ReviewDecisionType,
    ReviewScope,
    ReviewStatus,
    ScenarioType,
    SourceAvailabilityStatus,
    SourceChangeType,
    ThesisArgumentType,
    ThesisLifecycleStatus,
    UnitScale,
    UpdateItemPriority,
    UpdateItemStatus,
    UpdateItemType,
)


@dataclass
class ResearchInvestigation:
    """Canonical research investigation container."""
    investigation_id: str
    owner_user_id: str
    title: str
    description: Optional[str]
    primary_subject_entity_id: Optional[str]
    primary_subject_type: Optional[str]  # COMPANY, INSTRUMENT, INDUSTRY, MACROECONOMIC, GEOGRAPHY
    secondary_entity_ids: List[str]
    research_type: ResearchType
    research_objective: Optional[str]
    status: InvestigationLifecycleStatus
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    archived_at: Optional[datetime.datetime] = None
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchQuestion:
    """Analyst-authored research inquiry."""
    question_id: str
    investigation_id: str
    question_text: str
    status: ResearchQuestionStatus
    related_entity_ids: List[str]
    related_evidence_ids: List[str]
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class ResearchHypothesis:
    """Analyst hypothesis (an idea to investigate, strictly distinct from proven facts)."""
    hypothesis_id: str
    investigation_id: str
    statement: str
    status: ResearchHypothesisStatus
    related_claim_ids: List[str]
    related_evidence_ids: List[str]
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class ResearchNoteRevision:
    """Point-in-time snapshot of note content preserving edit history."""
    revision_id: str
    note_id: str
    revision_number: int
    title: str
    body_document: str
    author_user_id: str
    created_at: datetime.datetime


@dataclass
class ResearchNote:
    """Analyst-authored structured research observation or thesis document."""
    note_id: str
    investigation_id: str
    owner_user_id: str
    title: str
    body_document: str
    note_type: ResearchNoteType
    status: ResearchNoteStatus
    related_entity_ids: List[str]
    linked_source_ids: List[str]
    linked_evidence_ids: List[str]
    citation_ids: List[str]
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class ResearchClaim:
    """Granular claim with fact-vs-interpretation qualification and evidence status."""
    claim_id: str
    investigation_id: str
    statement: str
    claim_category: ResearchClaimCategory
    evidence_status: ResearchEvidenceStatus
    supporting_evidence_ids: List[str]
    contradicting_evidence_ids: List[str]
    related_entity_ids: List[str]
    author_user_id: str
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class ResearchSourceReference:
    """Canonical pointer to an official filing, news article, dataset, or financial statement fact."""
    source_reference_id: str
    canonical_document_id: Optional[str]
    canonical_entity_id: Optional[str]
    source_type: ResearchSourceType
    provider_id: str
    publisher_id: Optional[str]
    source_title: str
    source_url: Optional[str]
    published_at: Optional[datetime.datetime]
    source_updated_at: Optional[datetime.datetime]
    first_observed_at: datetime.datetime
    registered_at: datetime.datetime
    reporting_period: Optional[str]
    source_revision: Optional[str]
    rights_policy: str
    availability_status: SourceAvailabilityStatus
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchEvidence:
    """Canonical research evidence record linking a claim to a verified source location."""
    evidence_id: str
    investigation_id: str
    source_reference_id: str
    canonical_source_entity_id: Optional[str]
    evidence_type: str
    source_location_type: EvidenceLocationType
    source_location_reference: str
    page_number: Optional[int]
    section_name: Optional[str]
    source_revision: Optional[str]
    observation_time: datetime.datetime
    allowed_excerpt: Optional[str]
    linked_claim_ids: List[str]
    created_by: str
    created_at: datetime.datetime
    availability_status: SourceAvailabilityStatus
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchClaimEvidence:
    """Explicit mapping between a claim and supporting or contradicting evidence."""
    relationship_id: str
    claim_id: str
    evidence_id: str
    relationship_type: ClaimEvidenceRelationship
    linked_by: str
    created_at: datetime.datetime


@dataclass
class ResearchCitation:
    """Formatted, navigation-ready citation identifier."""
    citation_id: str
    investigation_id: str
    evidence_id: str
    source_reference_id: str
    citation_label: str
    location_reference: str
    source_revision: Optional[str]
    created_at: datetime.datetime
    is_broken: bool = False
    status_reason: Optional[str] = None


@dataclass
class ResearchActivity:
    """Append-only audit record of research operations."""
    activity_id: str
    investigation_id: str
    action_type: ResearchActivityAction
    actor_user_id: str
    object_type: str
    object_id: str
    details: Dict[str, Any]
    occurred_at: datetime.datetime


# ---------------------------------------------------------------------------
# Stage 105 Document Processing, Structure, Tables, & Search Models
# ---------------------------------------------------------------------------

@dataclass
class ResearchDocumentProcessingRecord:
    """Audit record and execution status of document parsing and text extraction."""
    processing_id: str
    canonical_document_id: str
    source_reference_id: str
    source_revision: str
    source_format: DocumentFormat
    processor_version: str
    processing_status: DocumentProcessingStatus
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    extracted_section_count: int = 0
    extracted_table_count: int = 0
    extracted_span_count: int = 0
    errors: List[str] = field(default_factory=list)
    content_rights_status: str = "PERMITTED"


@dataclass
class ResearchDocumentSection:
    """Hierarchical structural item or section within a research document."""
    section_id: str
    canonical_document_id: str
    source_reference_id: str
    source_revision: str
    heading: str
    section_path: str
    level: int
    start_char_offset: int
    end_char_offset: int
    parent_section_id: Optional[str] = None
    page_number: Optional[int] = None
    text_preview: str = ""


@dataclass
class ResearchDocumentSpan:
    """Exact source text segment indexed with character offsets and pagination."""
    span_id: str
    canonical_document_id: str
    source_reference_id: str
    source_revision: str
    start_char_offset: int
    end_char_offset: int
    text: str
    section_id: Optional[str] = None
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None


@dataclass
class ResearchDocumentTable:
    """Structured financial or operational table extracted from research sources."""
    table_id: str
    canonical_document_id: str
    source_reference_id: str
    source_revision: str
    title: str
    period_label: str
    currency: str
    unit_scale: UnitScale
    headers: List[str]
    row_labels: List[str]
    cells: List[List[str]]
    raw_values: List[List[Optional[float]]]
    section_id: Optional[str] = None
    footnotes: List[str] = field(default_factory=list)
    associated_fact_ids: List[str] = field(default_factory=list)


@dataclass
class ResearchSearchHit:
    """Search hit returned by multi-facet research source discovery."""
    hit_id: str
    source_reference_id: str
    source_type: ResearchSourceType
    source_title: str
    score: float
    availability_status: SourceAvailabilityStatus
    rights_policy: str
    canonical_document_id: Optional[str] = None
    canonical_entity_id: Optional[str] = None
    publisher_id: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    reporting_period: Optional[str] = None
    matched_snippet: str = ""
    matched_spans: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DocumentSearchHit:
    """Match result for an in-document query."""
    span_id: str
    snippet: str
    match_start: int
    match_end: int
    section_id: Optional[str] = None
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None


@dataclass
class ResearchEvidenceCandidate:
    """Discovered candidate evidence passage eligible for analyst conversion into evidence."""
    candidate_id: str
    source_reference_id: str
    source_title: str
    extracted_text: str
    evidence_type: str
    location_reference: str
    canonical_document_id: Optional[str] = None
    canonical_entity_id: Optional[str] = None
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None
    reporting_period: Optional[str] = None
    unit: Optional[str] = None
    currency: Optional[str] = None
    numeric_value: Optional[float] = None
    source_revision: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentComparisonSectionDiff:
    """Aligned textual diff between two document sections."""
    section_name: str
    alignment_status: str  # "MATCHED", "ADDED_IN_RIGHT", "REMOVED_IN_RIGHT"
    added_lines_count: int
    removed_lines_count: int
    diff_unified: str
    left_section_heading: Optional[str] = None
    right_section_heading: Optional[str] = None
    left_location_ref: Optional[str] = None
    right_location_ref: Optional[str] = None


@dataclass
class FinancialFactComparison:
    """Side-by-side comparison of structured financial metrics across periods."""
    fact_key: str
    label: str
    left_period: str
    right_period: str
    currency: str
    unit_scale: UnitScale
    left_value: float
    right_value: float
    absolute_delta: float
    percentage_delta: Optional[float]
    is_restated: bool = False
    compatibility_status: str = "COMPATIBLE"


@dataclass
class DocumentComparisonResult:
    """Full comparative analysis between two research documents or filing periods."""
    comparison_id: str
    left_document_id: str
    right_document_id: str
    left_title: str
    right_title: str
    total_added_lines: int
    total_removed_lines: int
    section_diffs: List[DocumentComparisonSectionDiff]
    financial_fact_diffs: List[FinancialFactComparison]
    compared_at: datetime.datetime
    left_period: Optional[str] = None
    right_period: Optional[str] = None
    comparison_mode: DocumentComparisonMode = DocumentComparisonMode.FULL_TEXT
    compatibility_warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Stage 106 — Research Analysis, Execution Runs, Findings & Hypothesis Domain
# ---------------------------------------------------------------------------

@dataclass
class AnalyticalObservationRow:
    """A single source-grounded or calculated observation in an analytical time series or cross-section."""
    period_or_subject: str
    primary_value: Optional[float]
    unit: str
    formatted_value: str
    period_change_absolute: Optional[float] = None
    period_change_percentage: Optional[float] = None
    source_reference_id: Optional[str] = None
    source_accession: Optional[str] = None
    source_vintage: Optional[str] = None
    is_restated: bool = False
    is_missing: bool = False
    availability_status: str = "AVAILABLE"
    derived_formula_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class AnalyticalSummaryStatistics:
    """Descriptive statistics computed over genuine eligible observations."""
    sample_size_n: int
    excluded_count: int
    mean: Optional[float] = None
    median: Optional[float] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    standard_deviation: Optional[float] = None
    q1_percentile: Optional[float] = None
    q3_percentile: Optional[float] = None
    cagr_percentage: Optional[float] = None
    pearson_correlation: Optional[float] = None
    methodology_notes: List[str] = field(default_factory=list)


@dataclass
class ResearchAnalysisSpecification:
    """Typed analysis specification defining inputs, metrics, time periods, and methodology."""
    analysis_type: ResearchAnalysisType
    primary_entity_id: str
    secondary_entity_ids: List[str] = field(default_factory=list)
    metric_ids: List[str] = field(default_factory=list)
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None
    frequency: AnalysisFrequency = AnalysisFrequency.ANNUAL
    input_version_policy: AnalysisInputPolicy = AnalysisInputPolicy.PINNED_SOURCE_VERSION
    outlier_policy: OutlierHandlingPolicy = OutlierHandlingPolicy.INCLUDE_ALL
    currency: Optional[str] = None
    as_known_at_cutoff: Optional[datetime.datetime] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    methodology_version: int = 1


@dataclass
class ResearchAnalysis:
    """Canonical institutional research analysis container."""
    analysis_id: str
    investigation_id: Optional[str]
    owner_user_id: str
    title: str
    description: Optional[str]
    analysis_type: ResearchAnalysisType
    research_objective: Optional[str]
    primary_subject_entity_id: str
    primary_subject_type: str  # COMPANY, FINANCIAL_INSTRUMENT, INDUSTRY, ECONOMIC_ENTITY, FINANCIAL_EVENT
    secondary_entity_ids: List[str]
    specification: ResearchAnalysisSpecification
    status: AnalysisExecutionStatus
    current_revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    archived_at: Optional[datetime.datetime] = None
    linked_question_ids: List[str] = field(default_factory=list)
    linked_hypothesis_ids: List[str] = field(default_factory=list)
    latest_run_id: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchAnalysisRun:
    """Point-in-time immutable record of an executed research analysis."""
    run_id: str
    analysis_id: str
    analysis_revision: int
    owner_user_id: str
    input_specification_hash: str
    methodology_version: int
    source_data_manifest: List[Dict[str, Any]]  # List of exact facts, filings, dates, vintages
    source_revision_watermarks: Dict[str, str]
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    execution_status: AnalysisExecutionStatus
    observations_count: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    compute_metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchAnalysisResult:
    """Complete analytical results payload with observations, charts, and summary statistics."""
    analysis_id: str
    run_id: str
    analysis_type: ResearchAnalysisType
    execution_status: AnalysisExecutionStatus
    methodology_version: int
    primary_subject_id: str
    metric_id: str
    unit: str
    observations: List[AnalyticalObservationRow]
    summary_statistics: AnalyticalSummaryStatistics
    chart_series: List[Dict[str, Any]]
    missingness_report: Dict[str, Any]
    comparability_warnings: List[str]
    source_data_manifest: List[Dict[str, Any]]
    executed_at: datetime.datetime
    as_known_at_cutoff: Optional[str] = None
    non_causal_qualification: str = "Observed historical correlation or trends do not establish deterministic economic causality or investment outcomes."


@dataclass
class HypothesisTestCriteria:
    """Explicit deterministic evaluation criteria for testing a hypothesis."""
    metric_id: str
    operator: str  # GTE, LTE, GT, LT, EQ, CONSISTENT_EXPANSION
    threshold_value: Optional[float] = None
    comparison_target: Optional[str] = None  # PEER_MEDIAN, PREVIOUS_PERIOD, HISTORICAL_MEAN
    required_periods_count: Optional[int] = None
    allow_missing: bool = False


@dataclass
class ResearchHypothesisEvaluation:
    """Evidence-based hypothesis evaluation record without fabricated conclusions."""
    evaluation_id: str
    hypothesis_id: str
    analysis_run_id: str
    author_user_id: str
    criteria: HypothesisTestCriteria
    eligible_universe: List[str]
    observation_count: int
    result_status: HypothesisEvaluationOutcome
    supporting_evidence_ids: List[str]
    contradicting_evidence_ids: List[str]
    evaluation_summary: str
    methodology_limitations: List[str]
    analyst_review_state: str  # PENDING_REVIEW, ACCEPTED_BY_ANALYST, REJECTED_BY_ANALYST
    created_at: datetime.datetime


@dataclass
class ResearchFinding:
    """Canonical research finding linking an analytical run to evidence and interpretations."""
    finding_id: str
    investigation_id: Optional[str]
    analysis_id: str
    analysis_run_id: str
    author_user_id: str
    finding_type: ResearchFindingType
    statement: str
    methodology_description: str
    supporting_evidence_ids: List[str]
    contradicting_evidence_ids: List[str]
    calculated_result_references: Dict[str, Any]
    limitations: List[str]
    review_status: ResearchFindingReviewStatus
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_source_outdated: bool = False
    source_outdated_reason: Optional[str] = None


@dataclass
class ResearchAnalysisAssumption:
    """Analyst-defined parameter assumption for sensitivity testing."""
    assumption_id: str
    analysis_id: str
    label: str
    parameter_id: str
    value: float
    unit: str
    source_type: AssumptionSourceType
    source_reference_id: Optional[str]
    analyst_note: Optional[str]
    created_at: datetime.datetime


@dataclass
class ResearchScenario:
    """Deterministic what-if scenario parameter set for sensitivity analysis."""
    scenario_id: str
    analysis_id: str
    name: str
    scenario_type: ScenarioType
    parameter_values: Dict[str, float]
    calculated_outputs: Dict[str, float]
    created_at: datetime.datetime
    is_non_predictive_illustrative: bool = True


@dataclass
class ResearchAnalysisTypeDefinition:
    """Taxonomic metadata definition for supported analysis types."""
    type_id: ResearchAnalysisType
    label: str
    description: str
    supported_subject_types: List[str]
    supported_frequencies: List[AnalysisFrequency]
    supported_metric_categories: List[str]
    is_active: bool = True
    methodology_version: int = 1


# ---------------------------------------------------------------------------
# Stage 107 Research Reports & Investment Theses Domain Models
# ---------------------------------------------------------------------------

@dataclass
class ResearchReport:
    """Canonical institutional financial research report container."""
    report_id: str
    owner_user_id: str
    investigation_id: Optional[str]
    report_type: ResearchReportType
    title: str
    subtitle: Optional[str]
    abstract: Optional[str]
    primary_subject_id: Optional[str]
    primary_subject_type: Optional[str]
    secondary_subject_ids: List[str]
    report_as_of: datetime.date
    research_cutoff: datetime.datetime
    template_id: Optional[str]
    status: ReportLifecycleStatus
    current_revision: int
    snapshot_policy: ReportSnapshotPolicy
    source_manifest: List[Dict[str, Any]]
    evidence_manifest: List[str]
    analysis_run_manifest: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    archived_at: Optional[datetime.datetime] = None
    citation_references: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchReportContentBlock:
    """Individual typed content unit within a report section."""
    block_id: str
    section_id: str
    order_index: int
    block_type: ReportBlockType
    content_text: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    citation_ids: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    analysis_run_id: Optional[str] = None
    caption: Optional[str] = None


@dataclass
class ResearchReportSection:
    """Structured hierarchical section within an institutional research report."""
    section_id: str
    report_id: str
    parent_section_id: Optional[str]
    order_index: int
    section_type: ReportSectionType
    heading: str
    content_blocks: List[Dict[str, Any]]
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class ResearchReportTemplate:
    """Pre-configured institutional research template definition."""
    template_id: str
    template_version: int
    report_type: ResearchReportType
    title: str
    description: str
    default_sections: List[Dict[str, Any]]
    required_sections: List[ReportSectionType]
    citation_style: str = "INSTITUTIONAL_NUMERIC"
    is_active: bool = True


@dataclass
class ResearchReportRevision:
    """Immutable snapshot of a saved or finalized report version."""
    revision_id: str
    report_id: str
    revision_number: int
    parent_revision_id: Optional[str]
    author_user_id: str
    document_snapshot: Dict[str, Any]
    source_manifest: List[Dict[str, Any]]
    analysis_manifest: List[str]
    revision_status: ReportLifecycleStatus
    change_summary: Optional[str]
    content_hash: str
    created_at: datetime.datetime


@dataclass
class ResearchInvestmentThesis:
    """Structured analyst investment thesis linking bull/bear cases and evidence."""
    thesis_id: str
    investigation_id: Optional[str]
    report_id: Optional[str]
    owner_user_id: str
    primary_subject_id: Optional[str]
    primary_subject_type: Optional[str]
    thesis_statement: str
    time_horizon: str
    status: ThesisLifecycleStatus
    current_revision: int
    bull_case_summary: Optional[str] = None
    bear_case_summary: Optional[str] = None
    base_case_summary: Optional[str] = None
    assumptions_summary: Optional[str] = None
    risks_summary: Optional[str] = None
    catalysts_summary: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ResearchThesisArgument:
    """Structured argument node in a two-sided investment thesis."""
    argument_id: str
    thesis_id: str
    argument_type: ThesisArgumentType
    statement: str
    claim_ids: List[str]
    evidence_ids: List[str]
    analysis_run_ids: List[str]
    finding_ids: List[str]
    limitations: List[str]
    revision: int
    created_at: datetime.datetime


@dataclass
class ResearchReportVerification:
    """Audit outcome of automated evidence, citation, and temporal verification."""
    verification_id: str
    report_id: str
    revision_number: int
    checked_at: datetime.datetime
    is_valid: bool
    blocking_issues_count: int
    warnings_count: int
    info_count: int
    issues: List[Dict[str, Any]]
    citation_coverage_pct: float
    verified_by_user_id: str


@dataclass
class ResearchReportExport:
    """Record of a rendered PDF or DOCX research publication artifact."""
    export_id: str
    report_id: str
    revision_number: int
    owner_user_id: str
    format: ExportFormat
    export_status: ExportStatus
    download_url: Optional[str]
    file_size_bytes: int
    page_count: int
    content_hash: str
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    expiry_at: Optional[datetime.datetime] = None
    error_message: Optional[str] = None


# ---------------------------------------------------------------------------
# Stage 108 Collaboration, Review, Comments & Circulation Domain Entities
# ---------------------------------------------------------------------------

@dataclass
class ResearchAccessGrant:
    """Explicit access permission granted to a user or organization role."""
    grant_id: str
    resource_type: ResearchResourceType
    resource_id: str
    principal_type: ResearchPrincipalType
    principal_id: str
    role: ResearchRole
    granted_by: str
    organization_id: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    expires_at: Optional[datetime.datetime] = None
    revoked_at: Optional[datetime.datetime] = None


@dataclass
class ResearchReviewRequest:
    """Formal review request targeting an exact revision of a report or investigation."""
    review_request_id: str
    target_type: str
    target_id: str
    target_revision_number: int
    target_content_hash: str
    requested_by: str
    assigned_reviewer_id: str
    review_scope: ReviewScope
    review_round: int
    status: ReviewStatus
    organization_id: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    instructions: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    completed_at: Optional[datetime.datetime] = None


@dataclass
class ResearchReviewAssignment:
    """Individual reviewer assignment under a review request."""
    assignment_id: str
    review_request_id: str
    reviewer_user_id: str
    role: str
    status: str
    assigned_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    completed_at: Optional[datetime.datetime] = None


@dataclass
class ResearchReviewDecision:
    """Recorded human review decision explicitly bound to a content revision."""
    decision_id: str
    review_request_id: str
    reviewer_user_id: str
    target_revision_number: int
    target_content_hash: str
    decision: ReviewDecisionType
    decision_comment: Optional[str] = None
    decided_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ResearchCommentThread:
    """Discussion thread anchored to an exact section, block, or evidence item."""
    thread_id: str
    resource_type: str
    resource_id: str
    target_revision_number: int
    anchor_type: CommentAnchorType
    anchor_reference: str
    created_by: str
    anchor_text: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    resolution_status: CommentThreadStatus = CommentThreadStatus.OPEN
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime.datetime] = None
    comments_count: int = 1
    is_stale: bool = False


@dataclass
class ResearchComment:
    """Individual message within an anchored review comment thread."""
    comment_id: str
    thread_id: str
    author_user_id: str
    body: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    edit_revision: int = 1


@dataclass
class QualityGateResult:
    """Quality gate and verification readiness evaluation."""
    gate_run_id: str
    report_id: str
    revision_number: int
    executed_at: datetime.datetime
    eligible_for_review: bool
    eligible_for_finalization: bool
    blocking_issues_count: int
    warnings_count: int
    issues: List[Dict[str, Any]]
    checklist: List[Dict[str, Any]]


@dataclass
class ResearchInternalCirculation:
    """Controlled internal circulation of an approved or finalized research report."""
    circulation_id: str
    report_id: str
    revision_number: int
    initiated_by: str
    recipient_user_ids: List[str]
    organization_id: Optional[str] = None
    status: CirculationStatus = CirculationStatus.ACTIVE
    notes: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    revoked_at: Optional[datetime.datetime] = None


@dataclass
class ResearchReviewAuditEvent:
    """Immutable audit trail record for research governance and review operations."""
    audit_event_id: str
    actor_user_id: str
    resource_type: str
    resource_id: str
    action: str
    occurred_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    organization_id: Optional[str] = None
    target_revision_number: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Stage 109 Knowledge, Dependency Lineage, Monitoring & Lifecycle Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ResearchKnowledgeEntry:
    """Indexed reference entry representing a canonical research artifact."""
    knowledge_entry_id: str
    entry_type: KnowledgeEntryType
    referenced_resource_type: str
    referenced_resource_id: str
    owner_user_id: str
    title: str
    description: Optional[str] = None
    investigation_id: Optional[str] = None
    subject_entity_ids: List[str] = field(default_factory=list)
    source_status: KnowledgeSourceAvailability = KnowledgeSourceAvailability.AVAILABLE
    knowledge_status: KnowledgeStatus = KnowledgeStatus.ACTIVE
    metadata_revision: int = 1
    organization_id: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ResearchKnowledgeCollection:
    """User or investigation-scoped collection grouping research knowledge entries."""
    collection_id: str
    owner_user_id: str
    title: str
    description: Optional[str] = None
    investigation_id: Optional[str] = None
    entry_ids: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ResearchDependencyEdge:
    """Explicit dependency link between upstream source/analysis and downstream research artifact."""
    edge_id: str
    upstream_resource_type: str
    upstream_resource_id: str
    downstream_resource_type: str
    downstream_resource_id: str
    upstream_revision_id: Optional[str] = None
    downstream_revision_id: Optional[str] = None
    dependency_type: DependencyType = DependencyType.SOURCE_TO_EVIDENCE
    source_reference: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ResearchSourceChangeEvent:
    """Canonical event describing detected revision, amendment, or status change in a data source."""
    change_event_id: str
    source_type: str
    canonical_source_id: str
    old_revision_id: Optional[str] = None
    new_revision_id: str = ""
    change_type: SourceChangeType = SourceChangeType.DOCUMENT_REVISED
    changed_fields: List[str] = field(default_factory=list)
    detected_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    source_published_at: Optional[datetime.datetime] = None
    provider_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchImpactAssessment:
    """Evaluated mechanical and potential interpretation impact of a source change on research."""
    impact_id: str
    change_event_id: str
    target_resource_type: str
    target_resource_id: str
    target_revision_id: Optional[str] = None
    impact_category: ImpactCategory = ImpactCategory.DIRECT_SOURCE_REFERENCE_CHANGED
    dependency_path: List[str] = field(default_factory=list)
    direct_dependency: bool = True
    review_recommended: bool = False
    summary: str = ""
    detected_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class ResearchRevalidationIssue:
    """Specific finding or broken reference detected during automated revalidation."""
    issue_id: str
    severity: str
    issue_type: str
    message: str
    target_reference: Optional[str] = None


@dataclass
class ResearchRevalidationResult:
    """Result of an evidence and reference integrity revalidation execution."""
    revalidation_id: str
    target_type: str
    target_id: str
    target_revision_number: Optional[int] = None
    status: RevalidationStatus = RevalidationStatus.COMPLETED
    outcome: RevalidationOutcome = RevalidationOutcome.VALID_REFERENCES
    issues: List[ResearchRevalidationIssue] = field(default_factory=list)
    executed_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    validated_by: str = "SYSTEM"


@dataclass
class ResearchUpdateItem:
    """Actionable maintenance task in the institutional research update queue."""
    update_item_id: str
    owner_user_id: str
    investigation_id: Optional[str] = None
    target_resource_type: str = ""
    target_resource_id: str = ""
    source_change_event_id: Optional[str] = None
    impact_assessment_id: Optional[str] = None
    update_type: UpdateItemType = UpdateItemType.SOURCE_CHANGE_REVIEW
    priority: UpdateItemPriority = UpdateItemPriority.MEDIUM
    status: UpdateItemStatus = UpdateItemStatus.OPEN
    title: str = ""
    description: Optional[str] = None
    resolution_note: Optional[str] = None
    assigned_user_id: Optional[str] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    acknowledged_at: Optional[datetime.datetime] = None
    resolved_at: Optional[datetime.datetime] = None


