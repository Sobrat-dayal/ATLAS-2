"""Pydantic Schemas and DTOs for Institutional Financial Research Platform (Stage 104)."""

import datetime
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.research.enums import (
    EvidenceLocationType,
    InvestigationLifecycleStatus,
    ResearchActivityAction,
    ResearchClaimCategory,
    ResearchEvidenceStatus,
    ResearchHypothesisStatus,
    ResearchNoteStatus,
    ResearchNoteType,
    ResearchQuestionStatus,
    ResearchSourceType,
    ResearchType,
    SourceAvailabilityStatus,
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
    recent_investigations: List[ResearchInvestigationDTO]
    recent_activities: List[ResearchActivityDTO]
