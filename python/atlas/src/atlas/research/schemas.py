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
    DocumentComparisonMode,
    DocumentFormat,
    DocumentProcessingStatus,
    EvidenceLocationType,
    HypothesisEvaluationOutcome,
    InvestigationLifecycleStatus,
    OutlierHandlingPolicy,
    ResearchActivityAction,
    ResearchAnalysisType,
    ResearchClaimCategory,
    ResearchEvidenceStatus,
    ResearchFindingReviewStatus,
    ResearchFindingType,
    ResearchHypothesisStatus,
    ResearchNoteStatus,
    ResearchNoteType,
    ResearchQuestionStatus,
    ResearchSourceType,
    ResearchType,
    SearchMode,
    SourceAvailabilityStatus,
    UnitScale,
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
