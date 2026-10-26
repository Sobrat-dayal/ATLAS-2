"""Domain Models for Institutional Financial Research Platform (Stage 104)."""

import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from atlas.research.enums import (
    ClaimEvidenceRelationship,
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
