"""Pydantic Schemas and DTOs for Institutional Financial Research Platform (Stage 104)."""

import datetime
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.research.enums import (
    AnalysisExecutionStatus,
    AnalysisFrequency,
    AnalysisInputPolicy,
    AssumptionSourceType,
    CirculationStatus,
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
    SearchMode,
    SourceAvailabilityStatus,
    SourceChangeType,
    ThesisArgumentType,
    ThesisLifecycleStatus,
    UnitScale,
    UpdateItemPriority,
    UpdateItemStatus,
    UpdateItemType,
)
from atlas.research.types import ResearchDocumentKind

# ---------------------------------------------------------------------------
# Legacy Stage 36 Schemas (Preserved for backwards compatibility)
# ---------------------------------------------------------------------------

class ResearchDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    document_kind: Optional[ResearchDocumentKind] = None
    publication_date: Optional[datetime.date] = None
    language_code: Optional[str] = None
    abstract_text: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


# ---------------------------------------------------------------------------
# Stage 104 Research Investigation DTOs
# ---------------------------------------------------------------------------

class CreateResearchInvestigationDTO(BaseModel):
    title: str = Field(..., min_length=3, max_length=500, description="Investigation title")
    research_type: ResearchType = Field(default=ResearchType.COMPANY_RESEARCH)
    primary_subject_entity_id: Optional[str] = Field(None, description="Primary canonical entity (ticker or entity ID)")
    primary_subject_type: Optional[str] = Field(None, description="COMPANY, INSTRUMENT, INDUSTRY, MACROECONOMIC, GEOGRAPHY")
    secondary_entity_ids: List[str] = Field(default_factory=list)
    research_objective: Optional[str] = Field(None, max_length=5000, description="Core thesis or objective")
    description: Optional[str] = Field(None, max_length=50000, description="Detailed scope description")


class UpdateResearchInvestigationDTO(BaseModel):
    expected_revision: int = Field(..., description="Revision number for optimistic concurrency conflict detection")
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    research_type: Optional[ResearchType] = None
    primary_subject_entity_id: Optional[str] = None
    primary_subject_type: Optional[str] = None
    secondary_entity_ids: Optional[List[str]] = None
    research_objective: Optional[str] = None
    description: Optional[str] = None
    status: Optional[InvestigationLifecycleStatus] = None


class ResearchInvestigationDTO(BaseModel):
    investigation_id: str
    owner_user_id: str
    title: str
    description: Optional[str] = None
    primary_subject_entity_id: Optional[str] = None
    primary_subject_type: Optional[str] = None
    secondary_entity_ids: List[str] = Field(default_factory=list)
    research_type: ResearchType
    research_objective: Optional[str] = None
    status: InvestigationLifecycleStatus
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    archived_at: Optional[datetime.datetime] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    notes_count: int = 0
    sources_count: int = 0
    questions_count: int = 0
    hypotheses_count: int = 0
    claims_count: int = 0
    evidence_count: int = 0


class ResearchInvestigationListResponseDTO(BaseModel):
    items: List[ResearchInvestigationDTO]
    total_count: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Stage 104 Research Question DTOs
# ---------------------------------------------------------------------------

class CreateResearchQuestionDTO(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=2000)
    related_entity_ids: List[str] = Field(default_factory=list)


class UpdateResearchQuestionDTO(BaseModel):
    question_text: Optional[str] = Field(None, min_length=5, max_length=2000)
    status: Optional[ResearchQuestionStatus] = None
    related_entity_ids: Optional[List[str]] = None
    related_evidence_ids: Optional[List[str]] = None


class ResearchQuestionDTO(BaseModel):
    question_id: str
    investigation_id: str
    question_text: str
    status: ResearchQuestionStatus
    related_entity_ids: List[str]
    related_evidence_ids: List[str]
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ResearchQuestionListResponseDTO(BaseModel):
    items: List[ResearchQuestionDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 104 Research Hypothesis DTOs
# ---------------------------------------------------------------------------

class CreateResearchHypothesisDTO(BaseModel):
    statement: str = Field(..., min_length=5, max_length=5000, description="Hypothesis statement under investigation")
    related_claim_ids: List[str] = Field(default_factory=list)
    related_evidence_ids: List[str] = Field(default_factory=list)


class UpdateResearchHypothesisDTO(BaseModel):
    statement: Optional[str] = Field(None, min_length=5, max_length=5000)
    status: Optional[ResearchHypothesisStatus] = None
    related_claim_ids: Optional[List[str]] = None
    related_evidence_ids: Optional[List[str]] = None


class ResearchHypothesisDTO(BaseModel):
    hypothesis_id: str
    investigation_id: str
    statement: str
    status: ResearchHypothesisStatus
    related_claim_ids: List[str]
    related_evidence_ids: List[str]
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ResearchHypothesisListResponseDTO(BaseModel):
    items: List[ResearchHypothesisDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 104 Research Note DTOs
# ---------------------------------------------------------------------------

class CreateResearchNoteDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body_document: str = Field(default="", max_length=500000)
    note_type: ResearchNoteType = Field(default=ResearchNoteType.GENERAL_NOTE)
    related_entity_ids: List[str] = Field(default_factory=list)
    linked_source_ids: List[str] = Field(default_factory=list)
    linked_evidence_ids: List[str] = Field(default_factory=list)


class UpdateResearchNoteDTO(BaseModel):
    expected_revision: int = Field(..., description="Expected revision number for optimistic concurrency")
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    body_document: Optional[str] = Field(None, max_length=500000)
    note_type: Optional[ResearchNoteType] = None
    status: Optional[ResearchNoteStatus] = None
    related_entity_ids: Optional[List[str]] = None
    linked_source_ids: Optional[List[str]] = None
    linked_evidence_ids: Optional[List[str]] = None
    citation_ids: Optional[List[str]] = None


class ResearchNoteRevisionDTO(BaseModel):
    revision_id: str
    note_id: str
    revision_number: int
    title: str
    body_document: str
    author_user_id: str
    created_at: datetime.datetime


class ResearchNoteDTO(BaseModel):
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


class ResearchNoteListResponseDTO(BaseModel):
    items: List[ResearchNoteDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 104 Research Claim DTOs
# ---------------------------------------------------------------------------

class CreateResearchClaimDTO(BaseModel):
    statement: str = Field(..., min_length=3, max_length=5000)
    claim_category: ResearchClaimCategory = Field(default=ResearchClaimCategory.ANALYST_INTERPRETATION)
    evidence_status: ResearchEvidenceStatus = Field(default=ResearchEvidenceStatus.NOT_REVIEWED)
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    related_entity_ids: List[str] = Field(default_factory=list)


class UpdateResearchClaimDTO(BaseModel):
    statement: Optional[str] = Field(None, min_length=3, max_length=5000)
    claim_category: Optional[ResearchClaimCategory] = None
    evidence_status: Optional[ResearchEvidenceStatus] = None
    supporting_evidence_ids: Optional[List[str]] = None
    contradicting_evidence_ids: Optional[List[str]] = None
    related_entity_ids: Optional[List[str]] = None


class ResearchClaimDTO(BaseModel):
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


class ResearchClaimListResponseDTO(BaseModel):
    items: List[ResearchClaimDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 104 Research Source DTOs
# ---------------------------------------------------------------------------

class LinkResearchSourceDTO(BaseModel):
    source_reference_id: Optional[str] = None
    # Or register candidate external/canonical source:
    canonical_document_id: Optional[str] = None
    canonical_entity_id: Optional[str] = None
    source_type: Optional[ResearchSourceType] = None
    provider_id: Optional[str] = None
    publisher_id: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    reporting_period: Optional[str] = None
    source_revision: Optional[str] = None
    rights_policy: Optional[str] = None


class ResearchSourceReferenceDTO(BaseModel):
    source_reference_id: str
    canonical_document_id: Optional[str] = None
    canonical_entity_id: Optional[str] = None
    source_type: ResearchSourceType
    provider_id: str
    publisher_id: Optional[str] = None
    source_title: str
    source_url: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    source_updated_at: Optional[datetime.datetime] = None
    first_observed_at: datetime.datetime
    registered_at: datetime.datetime
    reporting_period: Optional[str] = None
    source_revision: Optional[str] = None
    rights_policy: str
    availability_status: SourceAvailabilityStatus
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ResearchSourceListResponseDTO(BaseModel):
    items: List[ResearchSourceReferenceDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 104 Research Evidence & Citation DTOs
# ---------------------------------------------------------------------------

class AttachResearchEvidenceDTO(BaseModel):
    source_reference_id: str = Field(..., description="Target source reference ID")
    evidence_type: str = Field(default="QUALITATIVE_QUOTE")
    source_location_type: EvidenceLocationType = Field(default=EvidenceLocationType.SECTION)
    source_location_reference: str = Field(..., min_length=2, max_length=500, description="e.g. Item 1A Risk Factors")
    page_number: Optional[int] = Field(None, ge=1)
    section_name: Optional[str] = Field(None, max_length=200)
    allowed_excerpt: Optional[str] = Field(None, max_length=5000, description="Permitted source excerpt")
    linked_claim_ids: List[str] = Field(default_factory=list)


class UpdateResearchEvidenceDTO(BaseModel):
    source_location_reference: Optional[str] = Field(None, min_length=2, max_length=500)
    page_number: Optional[int] = None
    section_name: Optional[str] = None
    allowed_excerpt: Optional[str] = None
    linked_claim_ids: Optional[List[str]] = None


class ResearchEvidenceDTO(BaseModel):
    evidence_id: str
    investigation_id: str
    source_reference_id: str
    canonical_source_entity_id: Optional[str] = None
    evidence_type: str
    source_location_type: EvidenceLocationType
    source_location_reference: str
    page_number: Optional[int] = None
    section_name: Optional[str] = None
    source_revision: Optional[str] = None
    observation_time: datetime.datetime
    allowed_excerpt: Optional[str] = None
    linked_claim_ids: List[str]
    created_by: str
    created_at: datetime.datetime
    availability_status: SourceAvailabilityStatus
    provenance: Dict[str, Any] = Field(default_factory=dict)
    # Enriched source details
    source_title: Optional[str] = None
    publisher_id: Optional[str] = None
    source_url: Optional[str] = None


class ResearchEvidenceListResponseDTO(BaseModel):
    items: List[ResearchEvidenceDTO]
    total_count: int


class ResearchCitationDTO(BaseModel):
    citation_id: str
    investigation_id: str
    evidence_id: str
    source_reference_id: str
    citation_label: str
    location_reference: str
    source_revision: Optional[str] = None
    created_at: datetime.datetime
    is_broken: bool = False
    status_reason: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    publisher_id: Optional[str] = None


class ResearchCitationListResponseDTO(BaseModel):
    items: List[ResearchCitationDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 104 Research Activity & Overview DTOs
# ---------------------------------------------------------------------------

class ResearchActivityDTO(BaseModel):
    activity_id: str
    investigation_id: str
    action_type: ResearchActivityAction
    actor_user_id: str
    object_type: str
    object_id: str
    details: Dict[str, Any]
    occurred_at: datetime.datetime


class ResearchActivityTimelineResponseDTO(BaseModel):
    items: List[ResearchActivityDTO]
    total_count: int


class ResearchOverviewSummaryDTO(BaseModel):
    active_investigations_count: int
    draft_investigations_count: int
    completed_investigations_count: int
    archived_investigations_count: int
    total_notes_count: int
    total_sources_count: int
    total_evidence_count: int
    total_analyses_count: int = 0
    total_findings_count: int = 0
    total_evaluations_count: int = 0
    recent_investigations: List[ResearchInvestigationDTO]
    recent_activities: List[ResearchActivityDTO]


# ---------------------------------------------------------------------------
# Stage 105 Research Source Discovery & Search DTOs
# ---------------------------------------------------------------------------

class ResearchSourceDiscoveryQueryDTO(BaseModel):
    """Multi-facet query specification for finding research sources."""
    text_query: Optional[str] = None
    entity_ids: List[str] = Field(default_factory=list)
    instrument_ids: List[str] = Field(default_factory=list)
    source_type_ids: List[ResearchSourceType] = Field(default_factory=list)
    publisher_ids: List[str] = Field(default_factory=list)
    filing_types: List[str] = Field(default_factory=list)
    reporting_period_range: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    availability_statuses: List[SourceAvailabilityStatus] = Field(default_factory=list)
    search_mode: SearchMode = SearchMode.KEYWORD
    sort_by: str = "RELEVANCE"  # "RELEVANCE", "DATE_DESC", "DATE_ASC", "TITLE"
    limit: int = Field(default=25, ge=1, le=100)
    cursor: Optional[str] = None


class ResearchSearchHitDTO(BaseModel):
    """Ranked search hit from source discovery with matched excerpts."""
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
    matched_spans: List[Dict[str, Any]] = Field(default_factory=list)


class ResearchSourceDiscoveryResponseDTO(BaseModel):
    """Paginated source discovery search results with query audit summary."""
    hits: List[ResearchSearchHitDTO]
    total_count: int
    next_cursor: Optional[str] = None
    query_summary: Dict[str, Any] = Field(default_factory=dict)


class ResearchSourceTypeItemDTO(BaseModel):
    """Taxonomic description and rights classification of a source category."""
    source_type: ResearchSourceType
    display_name: str
    description: str
    rights_classification: str
    is_searchable: bool = True


class ResearchSourceTypeListResponseDTO(BaseModel):
    """List of supported canonical research source categories."""
    items: List[ResearchSourceTypeItemDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 105 Document Processing, Outline & Section DTOs
# ---------------------------------------------------------------------------

class ResearchDocumentProcessingStatusDTO(BaseModel):
    """Status and performance audit of document structure extraction."""
    processing_id: str
    canonical_document_id: str
    source_reference_id: str
    source_revision: str
    source_format: DocumentFormat
    processor_version: str
    processing_status: DocumentProcessingStatus
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    extracted_section_count: int
    extracted_table_count: int
    extracted_span_count: int
    errors: List[str] = Field(default_factory=list)
    content_rights_status: str = "PERMITTED"


class ResearchDocumentSectionDTO(BaseModel):
    """Hierarchical section node in a research document."""
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


class ResearchDocumentOutlineDTO(BaseModel):
    """Structured outline navigation tree of a document."""
    canonical_document_id: str
    source_reference_id: str
    document_title: str
    sections: List[ResearchDocumentSectionDTO]
    total_sections: int


class DocumentSearchRequestDTO(BaseModel):
    """Search request within a single research document."""
    query: str = Field(min_length=1, max_length=200)
    section_id: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=50)


class DocumentSearchHitDTO(BaseModel):
    """In-document keyword or phrase match with location anchor."""
    span_id: str
    snippet: str
    match_start: int
    match_end: int
    section_id: Optional[str] = None
    section_heading: Optional[str] = None
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None


class DocumentSearchResponseDTO(BaseModel):
    """Matches within a specific research document."""
    query: str
    total_matches: int
    hits: List[DocumentSearchHitDTO]


# ---------------------------------------------------------------------------
# Stage 105 Financial Table Extraction DTOs
# ---------------------------------------------------------------------------

class ResearchDocumentTableDTO(BaseModel):
    """Structured financial or operational data table extracted from source."""
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
    footnotes: List[str] = Field(default_factory=list)
    associated_fact_ids: List[str] = Field(default_factory=list)


class ResearchDocumentTableListResponseDTO(BaseModel):
    """List of extracted tables for a research document."""
    items: List[ResearchDocumentTableDTO]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 105 Evidence Candidates & Location Validation DTOs
# ---------------------------------------------------------------------------

class ResearchEvidenceCandidateDTO(BaseModel):
    """Candidate evidence snippet extracted from search or document inspection."""
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
    provenance: Dict[str, Any] = Field(default_factory=dict)


class EvidenceCandidateListResponseDTO(BaseModel):
    """List of evidence candidates discovered across research sources."""
    items: List[ResearchEvidenceCandidateDTO]
    total_count: int


class ResolveEvidenceLocationRequestDTO(BaseModel):
    """Request to validate an evidence location anchor against original source text."""
    source_reference_id: str
    location_type: EvidenceLocationType
    location_reference: str
    page_number: Optional[int] = None
    section_name: Optional[str] = None


class ResolveEvidenceLocationResponseDTO(BaseModel):
    """Validation outcome for a citation or evidence location anchor."""
    is_valid: bool
    resolved_anchor: str
    context_snippet: Optional[str] = None
    error_message: Optional[str] = None


class ConvertEvidenceCandidateDTO(BaseModel):
    """Request to convert a discovered candidate into a persistent ResearchEvidence record."""
    candidate_id: str
    investigation_id: str
    claim_id: Optional[str] = None
    relationship_type: Optional[str] = None  # "SUPPORTS", "CONTRADICTS", "CONTEXT"


# ---------------------------------------------------------------------------
# Stage 105 Two-Document & Financial Fact Comparison DTOs
# ---------------------------------------------------------------------------

class DocumentComparisonRequestDTO(BaseModel):
    """Request to compare two research documents or filing periods side-by-side."""
    left_document_id: str
    right_document_id: str
    left_source_revision: Optional[str] = None
    right_source_revision: Optional[str] = None
    comparison_mode: DocumentComparisonMode = DocumentComparisonMode.FULL_TEXT


class DocumentComparisonSectionDiffDTO(BaseModel):
    """Line-by-line diff for an aligned section across two documents."""
    section_name: str
    alignment_status: str
    added_lines_count: int
    removed_lines_count: int
    diff_unified: str
    left_section_heading: Optional[str] = None
    right_section_heading: Optional[str] = None
    left_location_ref: Optional[str] = None
    right_location_ref: Optional[str] = None


class FinancialFactComparisonDTO(BaseModel):
    """Side-by-side metric comparison between two periods or filings."""
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


class DocumentComparisonResultDTO(BaseModel):
    """Comprehensive comparison output including section diffs and financial variance."""
    comparison_id: str
    left_document_id: str
    right_document_id: str
    left_title: str
    right_title: str
    total_added_lines: int
    total_removed_lines: int
    section_diffs: List[DocumentComparisonSectionDiffDTO]
    financial_fact_diffs: List[FinancialFactComparisonDTO]
    compared_at: datetime.datetime
    left_period: Optional[str] = None
    right_period: Optional[str] = None
    comparison_mode: DocumentComparisonMode = DocumentComparisonMode.FULL_TEXT
    compatibility_warnings: List[str] = Field(default_factory=list)


class FinancialFactsCompareRequestDTO(BaseModel):
    """Request to compare financial statement facts for a company across two periods."""
    entity_id: str
    left_period: str
    right_period: str
    concepts: List[str] = Field(default_factory=list)


class FinancialFactsCompareResponseDTO(BaseModel):
    """Variance analysis across canonical financial statement facts."""
    entity_id: str
    left_period: str
    right_period: str
    fact_diffs: List[FinancialFactComparisonDTO]
    total_concepts_compared: int


# ---------------------------------------------------------------------------
# Stage 106 — Research Analysis, Runs, Findings & Hypothesis DTOs
# ---------------------------------------------------------------------------

class ResearchAnalysisSpecificationDTO(BaseModel):
    """Typed specification for executing a research analysis."""
    analysis_type: ResearchAnalysisType = Field(..., description="Canonical analysis type")
    primary_entity_id: str = Field(..., description="Primary subject ticker or entity ID (e.g. 'AAPL', 'CPI')")
    secondary_entity_ids: List[str] = Field(default_factory=list, description="Peers or benchmark entities")
    metric_ids: List[str] = Field(default_factory=list, description="Canonical metric concepts or ratios")
    time_range_start: Optional[str] = Field(None, description="Start date or period (e.g. '2020' or '2020-01-01')")
    time_range_end: Optional[str] = Field(None, description="End date or period (e.g. '2024' or '2024-12-31')")
    frequency: AnalysisFrequency = Field(default=AnalysisFrequency.ANNUAL)
    input_version_policy: AnalysisInputPolicy = Field(default=AnalysisInputPolicy.PINNED_SOURCE_VERSION)
    outlier_policy: OutlierHandlingPolicy = Field(default=OutlierHandlingPolicy.INCLUDE_ALL)
    currency: Optional[str] = Field(None, description="Preserved reporting currency (e.g. 'USD')")
    as_known_at_cutoff: Optional[datetime.datetime] = Field(None, description="Historical point-in-time publication cutoff")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom parameters or threshold criteria")
    methodology_version: int = Field(default=1, ge=1)


class CreateResearchAnalysisDTO(BaseModel):
    """Request DTO to create a new research analysis."""
    title: str = Field(..., min_length=3, max_length=500, description="Title of the research analysis")
    description: Optional[str] = Field(None, max_length=50000)
    analysis_type: ResearchAnalysisType = Field(..., description="Canonical analysis type")
    research_objective: Optional[str] = Field(None, max_length=5000)
    investigation_id: Optional[str] = Field(None, description="Optional parent investigation ID")
    primary_subject_entity_id: str = Field(..., description="Primary company ticker or entity ID")
    primary_subject_type: str = Field(default="COMPANY", description="COMPANY, FINANCIAL_INSTRUMENT, INDUSTRY, ECONOMIC_ENTITY, FINANCIAL_EVENT")
    secondary_entity_ids: List[str] = Field(default_factory=list)
    specification: ResearchAnalysisSpecificationDTO
    linked_question_ids: List[str] = Field(default_factory=list)
    linked_hypothesis_ids: List[str] = Field(default_factory=list)


class UpdateResearchAnalysisDTO(BaseModel):
    """Request DTO to update an existing analysis with optimistic concurrency."""
    expected_revision: int = Field(..., description="Expected revision number to guard against stale edits")
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    description: Optional[str] = None
    research_objective: Optional[str] = None
    specification: Optional[ResearchAnalysisSpecificationDTO] = None
    linked_question_ids: Optional[List[str]] = None
    linked_hypothesis_ids: Optional[List[str]] = None
    status: Optional[AnalysisExecutionStatus] = None


class ResearchAnalysisDTO(BaseModel):
    """Response DTO representing a research analysis entity."""
    analysis_id: str
    investigation_id: Optional[str] = None
    owner_user_id: str
    title: str
    description: Optional[str] = None
    analysis_type: ResearchAnalysisType
    research_objective: Optional[str] = None
    primary_subject_entity_id: str
    primary_subject_type: str
    secondary_entity_ids: List[str] = Field(default_factory=list)
    specification: ResearchAnalysisSpecificationDTO
    status: AnalysisExecutionStatus
    current_revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    archived_at: Optional[datetime.datetime] = None
    linked_question_ids: List[str] = Field(default_factory=list)
    linked_hypothesis_ids: List[str] = Field(default_factory=list)
    latest_run_id: Optional[str] = None
    runs_count: int = 0
    findings_count: int = 0
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ResearchAnalysisListResponseDTO(BaseModel):
    """Paginated or filtered list of research analyses."""
    analyses: List[ResearchAnalysisDTO]
    total_count: int


class AnalyticalObservationRowDTO(BaseModel):
    """Single observation data point in a time series or comparative table."""
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


class AnalyticalSummaryStatisticsDTO(BaseModel):
    """Cross-sectional or time-series summary statistics."""
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
    methodology_notes: List[str] = Field(default_factory=list)


class ResearchAnalysisRunDTO(BaseModel):
    """Metadata for an individual analytical execution run."""
    run_id: str
    analysis_id: str
    analysis_revision: int
    owner_user_id: str
    input_specification_hash: str
    methodology_version: int
    source_data_manifest: List[Dict[str, Any]]
    source_revision_watermarks: Dict[str, str] = Field(default_factory=dict)
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    execution_status: AnalysisExecutionStatus
    observations_count: int
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    compute_metadata: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ResearchAnalysisRunListResponseDTO(BaseModel):
    """List of executed runs for an analysis."""
    analysis_id: str
    runs: List[ResearchAnalysisRunDTO]
    total_count: int


class ResearchAnalysisResultDTO(BaseModel):
    """Complete results of an executed analysis."""
    analysis_id: str
    run_id: str
    analysis_type: ResearchAnalysisType
    execution_status: AnalysisExecutionStatus
    methodology_version: int
    primary_subject_id: str
    metric_id: str
    unit: str
    observations: List[AnalyticalObservationRowDTO]
    summary_statistics: AnalyticalSummaryStatisticsDTO
    chart_series: List[Dict[str, Any]]
    missingness_report: Dict[str, Any] = Field(default_factory=dict)
    comparability_warnings: List[str] = Field(default_factory=list)
    source_data_manifest: List[Dict[str, Any]] = Field(default_factory=list)
    executed_at: datetime.datetime
    as_known_at_cutoff: Optional[str] = None
    non_causal_qualification: str = (
        "Observed historical correlation or trends do not establish deterministic economic causality or investment outcomes."
    )


class AnalysisProvenanceResponseDTO(BaseModel):
    """Detailed audit lineage of data sources, formulas, and calculations."""
    analysis_id: str
    run_id: str
    input_specification_hash: str
    methodology_version: int
    executed_at: datetime.datetime
    source_manifest: List[Dict[str, Any]]
    source_watermarks: Dict[str, str]
    formula_definitions: Dict[str, str]
    temporal_policy: str
    provenance_chain: List[Dict[str, Any]]


class HypothesisTestCriteriaDTO(BaseModel):
    """Specification of criteria for deterministic hypothesis testing."""
    metric_id: str = Field(..., description="Canonical metric ID tested (e.g. 'profitability.operating_margin')")
    operator: str = Field(..., description="GTE, LTE, GT, LT, EQ, CONSISTENT_EXPANSION")
    threshold_value: Optional[float] = Field(None, description="Numeric threshold for comparison")
    comparison_target: Optional[str] = Field(None, description="PEER_MEDIAN, PREVIOUS_PERIOD, HISTORICAL_MEAN")
    required_periods_count: Optional[int] = Field(None, description="Required consecutive or total periods")
    allow_missing: bool = Field(default=False)


class EvaluateResearchHypothesisDTO(BaseModel):
    """Request DTO to evaluate an analyst hypothesis against an executed analysis run."""
    analysis_run_id: str = Field(..., description="Target analysis run to evaluate against")
    criteria: HypothesisTestCriteriaDTO
    eligible_universe: List[str] = Field(default_factory=list)


class ResearchHypothesisEvaluationDTO(BaseModel):
    """Evaluation result for a research hypothesis."""
    evaluation_id: str
    hypothesis_id: str
    analysis_run_id: str
    author_user_id: str
    criteria: HypothesisTestCriteriaDTO
    eligible_universe: List[str]
    observation_count: int
    result_status: HypothesisEvaluationOutcome
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    evaluation_summary: str
    methodology_limitations: List[str] = Field(default_factory=list)
    analyst_review_state: str = "PENDING_REVIEW"
    created_at: datetime.datetime


class ResearchHypothesisEvaluationListResponseDTO(BaseModel):
    """History of hypothesis evaluations."""
    hypothesis_id: str
    evaluations: List[ResearchHypothesisEvaluationDTO]
    total_count: int


class CreateResearchFindingDTO(BaseModel):
    """Request DTO to record a new research finding."""
    analysis_id: str
    analysis_run_id: str
    investigation_id: Optional[str] = None
    finding_type: ResearchFindingType = Field(default=ResearchFindingType.CALCULATED_RESULT)
    statement: str = Field(..., min_length=5, max_length=5000, description="Clear finding statement")
    methodology_description: str = Field(..., max_length=5000, description="Calculation or derivation methodology")
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    calculated_result_references: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)


class UpdateResearchFindingDTO(BaseModel):
    """Request DTO to update a research finding."""
    expected_revision: int = Field(..., description="Optimistic concurrency revision check")
    statement: Optional[str] = Field(None, min_length=5, max_length=5000)
    finding_type: Optional[ResearchFindingType] = None
    methodology_description: Optional[str] = None
    supporting_evidence_ids: Optional[List[str]] = None
    contradicting_evidence_ids: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    review_status: Optional[ResearchFindingReviewStatus] = None


class ResearchFindingDTO(BaseModel):
    """Canonical research finding response."""
    finding_id: str
    investigation_id: Optional[str] = None
    analysis_id: str
    analysis_run_id: str
    author_user_id: str
    finding_type: ResearchFindingType
    statement: str
    methodology_description: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    calculated_result_references: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    review_status: ResearchFindingReviewStatus
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_source_outdated: bool = False
    source_outdated_reason: Optional[str] = None


class ResearchFindingListResponseDTO(BaseModel):
    """List of research findings for an analysis or investigation."""
    findings: List[ResearchFindingDTO]
    total_count: int


class CreateResearchAssumptionDTO(BaseModel):
    """Request to record an explicit analyst assumption."""
    label: str = Field(..., min_length=2, max_length=200)
    parameter_id: str = Field(..., description="Parameter key (e.g. 'revenue_growth_rate')")
    value: float = Field(...)
    unit: str = Field(default="%")
    source_type: AssumptionSourceType = Field(default=AssumptionSourceType.ANALYST_ASSUMED)
    source_reference_id: Optional[str] = None
    analyst_note: Optional[str] = None


class ResearchAssumptionDTO(BaseModel):
    """Response DTO for an analyst assumption."""
    assumption_id: str
    analysis_id: str
    label: str
    parameter_id: str
    value: float
    unit: str
    source_type: AssumptionSourceType
    source_reference_id: Optional[str] = None
    analyst_note: Optional[str] = None
    created_at: datetime.datetime


class ResearchAssumptionListResponseDTO(BaseModel):
    """List of assumptions recorded for an analysis."""
    analysis_id: str
    assumptions: List[ResearchAssumptionDTO]
    total_count: int


class ExecuteSensitivityScenarioDTO(BaseModel):
    """Request for running bounded deterministic what-if sensitivity scenario matrix."""
    base_metric_value: float = Field(..., description="Baseline historical value (e.g. 391035.0)")
    metric_name: str = Field(default="Revenue")
    unit: str = Field(default="$M")
    growth_rates: List[float] = Field(
        default_factory=lambda: [-0.05, 0.0, 0.05, 0.10, 0.15],
        description="Finite percentage growth assumptions (e.g. -5% to +15%)"
    )
    margin_rates: Optional[List[float]] = Field(
        default_factory=lambda: [0.28, 0.30, 0.32, 0.34],
        description="Optional operating margin assumptions"
    )


class ResearchSensitivityResultDTO(BaseModel):
    """Sensitivity table output clearly qualified as illustrative non-predictive calculation."""
    base_metric_value: float
    growth_rates: List[float]
    margin_rates: Optional[List[float]] = None
    scenario_matrix: List[List[float]]  # Row: growth rate, Col: margin rate (or 1D if single param)
    headers: List[str]
    row_labels: List[str]
    unit: str
    is_non_predictive_illustrative: bool = True
    qualification_notice: str = (
        "Sensitivity analysis provides deterministic illustrative arithmetic for specified assumptions; "
        "it does not constitute a probabilistic market forecast, trading recommendation, or guaranteed valuation."
    )


class ResearchAnalysisTypeDTO(BaseModel):
    """Metadata for an analysis type in the registry."""
    type_id: ResearchAnalysisType
    label: str
    description: str
    supported_subject_types: List[str]
    supported_frequencies: List[AnalysisFrequency]
    supported_metric_categories: List[str]
    is_active: bool = True
    methodology_version: int = 1


class ResearchAnalysisTypeListResponseDTO(BaseModel):
    """Catalog of supported analysis types."""
    analysis_types: List[ResearchAnalysisTypeDTO]
    total_count: int


class ValidateAnalysisSpecificationRequestDTO(BaseModel):
    """Request to validate an analysis configuration before execution."""
    specification: ResearchAnalysisSpecificationDTO


class ValidateAnalysisSpecificationResponseDTO(BaseModel):
    """Validation response indicating configuration soundness and data availability."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    available_data_periods: List[str] = Field(default_factory=list)
    estimated_observation_count: int = 0


# ---------------------------------------------------------------------------
# Stage 107 Research Reports & Investment Theses DTOs
# ---------------------------------------------------------------------------

class ResearchReportContentBlockDTO(BaseModel):
    """Content block within a report section."""
    block_id: str
    section_id: str
    order_index: int
    block_type: ReportBlockType
    content_text: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    citation_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    analysis_run_id: Optional[str] = None
    caption: Optional[str] = None


class ResearchReportSectionDTO(BaseModel):
    """Structured hierarchical section DTO."""
    section_id: str
    report_id: str
    parent_section_id: Optional[str] = None
    order_index: int
    section_type: ReportSectionType
    heading: str
    content_blocks: List[Dict[str, Any]] = Field(default_factory=list)
    revision: int = 1
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CreateResearchReportRequest(BaseModel):
    """Request payload to create a new institutional research report."""
    investigation_id: Optional[str] = None
    report_type: ResearchReportType
    title: str = Field(..., min_length=3, max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    abstract: Optional[str] = Field(default=None, max_length=2000)
    primary_subject_id: Optional[str] = None
    primary_subject_type: Optional[str] = None
    secondary_subject_ids: List[str] = Field(default_factory=list)
    template_id: Optional[str] = None
    report_as_of: Optional[datetime.date] = None
    research_cutoff: Optional[datetime.datetime] = None
    snapshot_policy: ReportSnapshotPolicy = ReportSnapshotPolicy.DRAFT_LATEST_AUTHORIZED


class UpdateResearchReportRequest(BaseModel):
    """Request payload to update report metadata and parameters."""
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    subtitle: Optional[str] = None
    abstract: Optional[str] = None
    primary_subject_id: Optional[str] = None
    secondary_subject_ids: Optional[List[str]] = None
    report_as_of: Optional[datetime.date] = None
    research_cutoff: Optional[datetime.datetime] = None
    snapshot_policy: Optional[ReportSnapshotPolicy] = None
    status: Optional[ReportLifecycleStatus] = None
    expected_revision: int = Field(..., description="Optimistic concurrency guard")


class FinalizeReportRequest(BaseModel):
    """Request to freeze and finalize a report into an immutable snapshot."""
    expected_revision: int
    change_summary: Optional[str] = None


class ResearchReportResponse(BaseModel):
    """Summary representation of a research report."""
    report_id: str
    owner_user_id: str
    investigation_id: Optional[str] = None
    report_type: ResearchReportType
    title: str
    subtitle: Optional[str] = None
    abstract: Optional[str] = None
    primary_subject_id: Optional[str] = None
    primary_subject_type: Optional[str] = None
    secondary_subject_ids: List[str] = Field(default_factory=list)
    report_as_of: datetime.date
    research_cutoff: datetime.datetime
    template_id: Optional[str] = None
    status: ReportLifecycleStatus
    current_revision: int
    snapshot_policy: ReportSnapshotPolicy
    section_count: int = 0
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ResearchReportDetailResponse(ResearchReportResponse):
    """Complete representation of a research report including sections."""
    sections: List[ResearchReportSectionDTO] = Field(default_factory=list)
    source_manifest: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_manifest: List[str] = Field(default_factory=list)
    analysis_run_manifest: List[str] = Field(default_factory=list)


class ResearchReportListResponse(BaseModel):
    """Paginated collection of research reports."""
    reports: List[ResearchReportResponse]
    total_count: int


class CreateReportSectionRequest(BaseModel):
    """Request payload to add a section to a report."""
    parent_section_id: Optional[str] = None
    order_index: Optional[int] = None
    section_type: ReportSectionType = ReportSectionType.CUSTOM
    heading: str = Field(..., min_length=1, max_length=200)
    content_blocks: List[Dict[str, Any]] = Field(default_factory=list)


class UpdateReportSectionRequest(BaseModel):
    """Request payload to update an existing section and its content blocks."""
    heading: Optional[str] = Field(default=None, min_length=1, max_length=200)
    section_type: Optional[ReportSectionType] = None
    content_blocks: Optional[List[Dict[str, Any]]] = None
    expected_revision: int = Field(default=1)


class ReorderReportSectionsRequest(BaseModel):
    """Request to safely update the ordering of sections in a report."""
    section_ids: List[str]


class ResearchReportTemplateDTO(BaseModel):
    """Institutional template schema for report authoring."""
    template_id: str
    template_version: int
    report_type: ResearchReportType
    title: str
    description: str
    default_sections: List[Dict[str, Any]]
    required_sections: List[ReportSectionType]
    citation_style: str
    is_active: bool


class ResearchReportTemplateListResponseDTO(BaseModel):
    """Collection of available report templates."""
    templates: List[ResearchReportTemplateDTO]
    total_count: int


class ResearchReportRevisionDTO(BaseModel):
    """Revision history entry of a saved report."""
    revision_id: str
    report_id: str
    revision_number: int
    parent_revision_id: Optional[str] = None
    author_user_id: str
    revision_status: ReportLifecycleStatus
    change_summary: Optional[str] = None
    content_hash: str
    created_at: datetime.datetime


class ResearchReportRevisionListResponseDTO(BaseModel):
    """Collection of revision history entries."""
    revisions: List[ResearchReportRevisionDTO]
    total_count: int


class CompareReportRevisionsRequestDTO(BaseModel):
    """Request to diff two revisions of a report."""
    base_revision_number: int
    target_revision_number: int


class CompareReportRevisionsResponseDTO(BaseModel):
    """Structural and text diff between two report revisions."""
    report_id: str
    base_revision_number: int
    target_revision_number: int
    sections_added: List[str]
    sections_removed: List[str]
    sections_modified: List[str]
    diff_unified: str


class CreateResearchThesisRequest(BaseModel):
    """Request to create an analyst investment thesis."""
    investigation_id: Optional[str] = None
    report_id: Optional[str] = None
    primary_subject_id: Optional[str] = None
    primary_subject_type: Optional[str] = None
    thesis_statement: str = Field(..., min_length=10, max_length=1000)
    time_horizon: str = Field(default="12_MONTHS")
    bull_case_summary: Optional[str] = None
    bear_case_summary: Optional[str] = None
    base_case_summary: Optional[str] = None
    assumptions_summary: Optional[str] = None
    risks_summary: Optional[str] = None
    catalysts_summary: Optional[str] = None


class UpdateResearchThesisRequest(BaseModel):
    """Request to update an analyst investment thesis."""
    thesis_statement: Optional[str] = Field(default=None, min_length=10, max_length=1000)
    time_horizon: Optional[str] = None
    status: Optional[ThesisLifecycleStatus] = None
    bull_case_summary: Optional[str] = None
    bear_case_summary: Optional[str] = None
    base_case_summary: Optional[str] = None
    assumptions_summary: Optional[str] = None
    risks_summary: Optional[str] = None
    catalysts_summary: Optional[str] = None
    expected_revision: int


class ResearchThesisArgumentDTO(BaseModel):
    """Argument component of an investment thesis."""
    argument_id: str
    thesis_id: str
    argument_type: ThesisArgumentType
    statement: str
    claim_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    analysis_run_ids: List[str] = Field(default_factory=list)
    finding_ids: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    revision: int
    created_at: datetime.datetime


class CreateThesisArgumentRequest(BaseModel):
    """Request to add a supporting/opposing argument or scenario to a thesis."""
    argument_type: ThesisArgumentType
    statement: str = Field(..., min_length=5, max_length=1000)
    claim_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    analysis_run_ids: List[str] = Field(default_factory=list)
    finding_ids: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class UpdateThesisArgumentRequest(BaseModel):
    """Request to modify an existing thesis argument."""
    statement: Optional[str] = None
    argument_type: Optional[ThesisArgumentType] = None
    claim_ids: Optional[List[str]] = None
    evidence_ids: Optional[List[str]] = None
    analysis_run_ids: Optional[List[str]] = None
    finding_ids: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    expected_revision: int = 1


class ResearchThesisResponse(BaseModel):
    """Summary of an investment thesis."""
    thesis_id: str
    investigation_id: Optional[str] = None
    report_id: Optional[str] = None
    owner_user_id: str
    primary_subject_id: Optional[str] = None
    primary_subject_type: Optional[str] = None
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
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ResearchThesisDetailResponse(ResearchThesisResponse):
    """Detailed thesis representation including structured argument list."""
    arguments: List[ResearchThesisArgumentDTO] = Field(default_factory=list)


class VerifyReportRequest(BaseModel):
    """Request to trigger verification checks on a report."""
    expected_revision: Optional[int] = None


class ResearchReportVerificationResponse(BaseModel):
    """Result of automated report verification."""
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


class CreateReportExportRequest(BaseModel):
    """Request to queue a PDF or DOCX report publication export."""
    format: ExportFormat = ExportFormat.PDF
    expected_revision: Optional[int] = None
    include_toc: bool = True
    include_references: bool = True
    author_name: str = "ATLAS Analyst"


class ResearchReportExportResponse(BaseModel):
    """Metadata and status of a research report export artifact."""
    export_id: str
    report_id: str
    revision_number: int
    owner_user_id: str
    format: ExportFormat
    export_status: ExportStatus
    download_url: Optional[str] = None
    file_size_bytes: int
    page_count: int
    content_hash: str
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    expiry_at: Optional[datetime.datetime] = None
    error_message: Optional[str] = None


class ResearchReportExportListResponse(BaseModel):
    """Collection of export jobs for a report."""
    exports: List[ResearchReportExportResponse]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 108 Collaboration, Review, Comments & Circulation Schemas
# ---------------------------------------------------------------------------

class CreateAccessGrantRequest(BaseModel):
    """Request payload to grant research access to a principal."""
    principal_type: ResearchPrincipalType = ResearchPrincipalType.USER
    principal_id: str
    role: ResearchRole
    expires_at: Optional[datetime.datetime] = None


class UpdateAccessGrantRequest(BaseModel):
    """Request payload to change an existing research role grant."""
    role: ResearchRole


class ResearchAccessGrantResponse(BaseModel):
    """Access grant record returned to authorized clients."""
    grant_id: str
    resource_type: ResearchResourceType
    resource_id: str
    principal_type: ResearchPrincipalType
    principal_id: str
    role: ResearchRole
    granted_by: str
    organization_id: Optional[str] = None
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime] = None
    revoked_at: Optional[datetime.datetime] = None


class ResearchAccessGrantListResponse(BaseModel):
    """Collection of access grants for a resource."""
    grants: List[ResearchAccessGrantResponse]
    total_count: int


class CreateReviewRequest(BaseModel):
    """Request to initiate a formal review round on a research object."""
    target_type: str = "REPORT"
    target_id: str
    target_revision_number: Optional[int] = None
    assigned_reviewer_id: str
    review_scope: ReviewScope = ReviewScope.FULL_REPORT
    due_date: Optional[datetime.datetime] = None
    instructions: Optional[str] = None


class UpdateReviewRequest(BaseModel):
    """Request to modify non-decision review metadata."""
    assigned_reviewer_id: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    instructions: Optional[str] = None


class CreateReviewDecisionRequest(BaseModel):
    """Formal decision submission from an assigned reviewer."""
    decision: ReviewDecisionType
    decision_comment: Optional[str] = None
    expected_revision_number: Optional[int] = None


class ResearchReviewDecisionResponse(BaseModel):
    """Recorded review decision audit representation."""
    decision_id: str
    review_request_id: str
    reviewer_user_id: str
    target_revision_number: int
    target_content_hash: str
    decision: ReviewDecisionType
    decision_comment: Optional[str] = None
    decided_at: datetime.datetime


class ResearchReviewRequestResponse(BaseModel):
    """Detailed review request record."""
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
    created_at: datetime.datetime
    updated_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    latest_decision: Optional[ResearchReviewDecisionResponse] = None


class ResearchReviewListResponse(BaseModel):
    """Queue of review requests."""
    reviews: List[ResearchReviewRequestResponse]
    total_count: int


class ResearchApprovalStatusResponse(BaseModel):
    """Point-in-time approval certification status for a report revision."""
    report_id: str
    revision_number: int
    is_approved: bool
    status_message: str
    approval_id: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    target_content_hash: Optional[str] = None


class CreateCommentThreadRequest(BaseModel):
    """Request to anchor a new review discussion thread."""
    target_revision_number: Optional[int] = None
    anchor_type: CommentAnchorType = CommentAnchorType.REPORT_SECTION
    anchor_reference: str
    anchor_text: Optional[str] = None
    initial_comment: str


class CreateCommentReplyRequest(BaseModel):
    """Request to post a reply within an existing comment thread."""
    body: str


class UpdateCommentRequest(BaseModel):
    """Request to edit an authored comment body."""
    body: str


class ResearchCommentResponse(BaseModel):
    """Individual comment representation."""
    comment_id: str
    thread_id: str
    author_user_id: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    edit_revision: int


class ResearchCommentThreadResponse(BaseModel):
    """Full thread representation with comments."""
    thread_id: str
    resource_type: str
    resource_id: str
    target_revision_number: int
    anchor_type: CommentAnchorType
    anchor_reference: str
    anchor_text: Optional[str] = None
    created_by: str
    created_at: datetime.datetime
    resolution_status: CommentThreadStatus
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime.datetime] = None
    comments: List[ResearchCommentResponse]
    is_stale: bool = False


class ResearchCommentThreadListResponse(BaseModel):
    """Collection of anchored comment threads."""
    threads: List[ResearchCommentThreadResponse]
    total_count: int


class RunQualityGateRequest(BaseModel):
    """Request to evaluate a report revision against governance quality gates."""
    revision_number: Optional[int] = None


class QualityGateResultResponse(BaseModel):
    """Audit response from a quality gate evaluation run."""
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


class CreateCirculationRequest(BaseModel):
    """Request to internally circulate an approved or finalized report."""
    revision_number: Optional[int] = None
    recipient_user_ids: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class ResearchInternalCirculationResponse(BaseModel):
    """Record of an active or revoked internal report circulation."""
    circulation_id: str
    report_id: str
    revision_number: int
    initiated_by: str
    recipient_user_ids: List[str]
    organization_id: Optional[str] = None
    status: CirculationStatus
    notes: Optional[str] = None
    created_at: datetime.datetime
    revoked_at: Optional[datetime.datetime] = None


class ResearchInternalCirculationListResponse(BaseModel):
    """Collection of internal circulations."""
    circulations: List[ResearchInternalCirculationResponse]
    total_count: int


class ResearchReviewAuditEventResponse(BaseModel):
    """Audit trail record of collaboration and review operations."""
    audit_event_id: str
    actor_user_id: str
    resource_type: str
    resource_id: str
    action: str
    occurred_at: datetime.datetime
    organization_id: Optional[str] = None
    target_revision_number: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ResearchReviewAuditEventListResponse(BaseModel):
    """Collection of review audit events."""
    events: List[ResearchReviewAuditEventResponse]
    total_count: int


# ---------------------------------------------------------------------------
# Stage 109 Knowledge, Dependency Lineage, Monitoring & Lifecycle Schemas
# ---------------------------------------------------------------------------

class ResearchKnowledgeEntryResponse(BaseModel):
    """Record representing an indexed research knowledge entry."""
    knowledge_entry_id: str
    entry_type: KnowledgeEntryType
    referenced_resource_type: str
    referenced_resource_id: str
    owner_user_id: str
    title: str
    description: Optional[str] = None
    investigation_id: Optional[str] = None
    subject_entity_ids: List[str] = Field(default_factory=list)
    source_status: KnowledgeSourceAvailability
    knowledge_status: KnowledgeStatus
    metadata_revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ResearchKnowledgeSearchQuery(BaseModel):
    """Query criteria for searching across authorized research knowledge entries."""
    query: Optional[str] = None
    entry_types: Optional[List[KnowledgeEntryType]] = None
    investigation_id: Optional[str] = None
    entity_id: Optional[str] = None
    source_status: Optional[KnowledgeSourceAvailability] = None
    knowledge_status: Optional[KnowledgeStatus] = None
    limit: int = 50
    offset: int = 0


class ResearchKnowledgeSearchResponse(BaseModel):
    """Paginated collection of research knowledge entries."""
    entries: List[ResearchKnowledgeEntryResponse]
    total_count: int


class ResearchDependencyEdgeResponse(BaseModel):
    """Link between upstream dependency and downstream dependent research artifact."""
    edge_id: str
    upstream_resource_type: str
    upstream_resource_id: str
    upstream_revision_id: Optional[str] = None
    downstream_resource_type: str
    downstream_resource_id: str
    downstream_revision_id: Optional[str] = None
    dependency_type: DependencyType
    source_reference: Optional[str] = None
    created_at: datetime.datetime


class ResearchDependencyLineageResponse(BaseModel):
    """Full lineage graph for a target research artifact."""
    root_resource_type: str
    root_resource_id: str
    edges: List[ResearchDependencyEdgeResponse]
    nodes: List[Dict[str, Any]] = Field(default_factory=list)


class CreateSourceChangeEventRequest(BaseModel):
    """Request to record a canonical data source revision or amendment event."""
    source_type: str
    canonical_source_id: str
    old_revision_id: Optional[str] = None
    new_revision_id: str
    change_type: SourceChangeType
    changed_fields: List[str] = Field(default_factory=list)
    source_published_at: Optional[datetime.datetime] = None
    provider_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ResearchSourceChangeEventResponse(BaseModel):
    """Record of a detected canonical source revision or status alteration."""
    change_event_id: str
    source_type: str
    canonical_source_id: str
    old_revision_id: Optional[str] = None
    new_revision_id: str
    change_type: SourceChangeType
    changed_fields: List[str]
    detected_at: datetime.datetime
    source_published_at: Optional[datetime.datetime] = None
    provider_id: Optional[str] = None
    details: Dict[str, Any]


class ResearchSourceChangeEventListResponse(BaseModel):
    """Collection of detected source change events."""
    events: List[ResearchSourceChangeEventResponse]
    total_count: int


class ResearchImpactAssessmentResponse(BaseModel):
    """Impact diagnosis on research artifacts originating from a source change."""
    impact_id: str
    change_event_id: str
    target_resource_type: str
    target_resource_id: str
    target_revision_id: Optional[str] = None
    impact_category: ImpactCategory
    dependency_path: List[str]
    direct_dependency: bool
    review_recommended: bool
    summary: str
    detected_at: datetime.datetime


class ResearchImpactListResponse(BaseModel):
    """Collection of impact assessments."""
    impacts: List[ResearchImpactAssessmentResponse]
    total_count: int


class CreateRevalidationRequest(BaseModel):
    """Request to revalidate citations, data inputs, and approval state."""
    target_type: str
    target_id: str
    target_revision_number: Optional[int] = None
    initiating_change_event_id: Optional[str] = None


class ResearchRevalidationIssueResponse(BaseModel):
    """Specific broken reference or warning discovered during revalidation."""
    issue_id: str
    severity: str
    issue_type: str
    message: str
    target_reference: Optional[str] = None


class ResearchRevalidationResultResponse(BaseModel):
    """Detailed outcome from a research revalidation execution."""
    revalidation_id: str
    target_type: str
    target_id: str
    target_revision_number: Optional[int] = None
    status: RevalidationStatus
    outcome: RevalidationOutcome
    issues: List[ResearchRevalidationIssueResponse]
    executed_at: datetime.datetime
    validated_by: str


class CreateUpdateItemRequest(BaseModel):
    """Request to create an actionable research update queue item."""
    investigation_id: Optional[str] = None
    target_resource_type: str
    target_resource_id: str
    source_change_event_id: Optional[str] = None
    impact_assessment_id: Optional[str] = None
    update_type: UpdateItemType
    priority: UpdateItemPriority = UpdateItemPriority.MEDIUM
    title: str
    description: Optional[str] = None


class ResolveUpdateItemRequest(BaseModel):
    """Request to resolve a research update queue item."""
    resolution_note: str


class ResearchUpdateItemResponse(BaseModel):
    """Record of an actionable item in the research update queue."""
    update_item_id: str
    owner_user_id: str
    investigation_id: Optional[str] = None
    target_resource_type: str
    target_resource_id: str
    source_change_event_id: Optional[str] = None
    impact_assessment_id: Optional[str] = None
    update_type: UpdateItemType
    priority: UpdateItemPriority
    status: UpdateItemStatus
    title: str
    description: Optional[str] = None
    resolution_note: Optional[str] = None
    assigned_user_id: Optional[str] = None
    created_at: datetime.datetime
    acknowledged_at: Optional[datetime.datetime] = None
    resolved_at: Optional[datetime.datetime] = None


class ResearchUpdateItemListResponse(BaseModel):
    """Collection of research update queue items."""
    updates: List[ResearchUpdateItemResponse]
    total_count: int


class ResearchOverviewSummaryResponse(BaseModel):
    """Consolidated summary metrics for the unified institutional research overview."""
    active_investigations_count: int
    total_notes_count: int
    total_analyses_count: int
    total_reports_count: int
    total_theses_count: int
    pending_reviews_count: int
    open_updates_count: int
    critical_updates_count: int
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)


