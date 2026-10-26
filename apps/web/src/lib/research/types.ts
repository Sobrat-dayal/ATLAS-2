/**
 * Canonical Types for Institutional Financial Research Platform (Stage 104).
 */

export type ResearchType =
  | "COMPANY_RESEARCH"
  | "SECURITY_RESEARCH"
  | "INDUSTRY_RESEARCH"
  | "MACROECONOMIC_RESEARCH"
  | "MARKET_RESEARCH"
  | "FINANCIAL_EVENT_RESEARCH"
  | "GENERAL_FINANCIAL_RESEARCH";

export type InvestigationLifecycleStatus =
  | "DRAFT"
  | "ACTIVE"
  | "ON_HOLD"
  | "COMPLETED"
  | "ARCHIVED";

export type ResearchQuestionStatus =
  | "OPEN"
  | "UNDER_REVIEW"
  | "ADDRESSED"
  | "DROPPED";

export type ResearchHypothesisStatus =
  | "PROPOSED"
  | "UNDER_TEST"
  | "SUPPORTED_BY_AVAILABLE_EVIDENCE"
  | "CONTRADICTED_BY_AVAILABLE_EVIDENCE"
  | "INCONCLUSIVE"
  | "RETIRED";

export type ResearchNoteType =
  | "OBSERVATION"
  | "QUESTION"
  | "HYPOTHESIS"
  | "ASSUMPTION"
  | "ANALYSIS"
  | "CONCLUSION"
  | "GENERAL_NOTE";

export type ResearchNoteStatus =
  | "DRAFT"
  | "IN_PROGRESS"
  | "REVIEWED"
  | "ARCHIVED";

export type ResearchClaimCategory =
  | "SOURCE_REPORTED_FACT"
  | "ANALYST_INTERPRETATION"
  | "ASSUMPTION"
  | "HYPOTHESIS"
  | "ESTIMATE"
  | "OPEN_QUESTION";

export type ResearchEvidenceStatus =
  | "SUPPORTED_BY_CITED_SOURCE"
  | "PARTIALLY_SUPPORTED"
  | "CONTRADICTED"
  | "INSUFFICIENT_EVIDENCE"
  | "NOT_REVIEWED"
  | "SOURCE_UNAVAILABLE"
  | "SOURCE_WITHDRAWN";

export type ResearchSourceType =
  | "REGULATORY_FILING"
  | "CORPORATE_DISCLOSURE"
  | "ANNUAL_REPORT"
  | "QUARTERLY_REPORT"
  | "EARNINGS_RELEASE"
  | "FINANCIAL_STATEMENT"
  | "MARKET_DATASET"
  | "ECONOMIC_DATASET"
  | "ECONOMIC_RELEASE"
  | "NEWS_ARTICLE"
  | "NEWS_STORY"
  | "FINANCIAL_EVENT"
  | "OFFICIAL_STATISTICAL_PUBLICATION"
  | "LICENSED_RESEARCH_REPORT"
  | "ACADEMIC_PUBLICATION"
  | "USER_AUTHORED_DOCUMENT"
  | "AUTHORIZED_EXTERNAL_REFERENCE"
  | "UNKNOWN";

export type EvidenceLocationType =
  | "PAGE"
  | "SECTION"
  | "PARAGRAPH"
  | "TABLE"
  | "ROW"
  | "DATA_POINT"
  | "ARTICLE_REVISION";

export type SourceAvailabilityStatus =
  | "AVAILABLE"
  | "RESTRICTED"
  | "WITHDRAWN"
  | "UNAVAILABLE";

export type ResearchActivityAction =
  | "INVESTIGATION_CREATED"
  | "INVESTIGATION_UPDATED"
  | "STATUS_CHANGED"
  | "INVESTIGATION_ARCHIVED"
  | "INVESTIGATION_DELETED"
  | "QUESTION_ADDED"
  | "QUESTION_UPDATED"
  | "QUESTION_DELETED"
  | "HYPOTHESIS_ADDED"
  | "HYPOTHESIS_UPDATED"
  | "HYPOTHESIS_DELETED"
  | "NOTE_CREATED"
  | "NOTE_UPDATED"
  | "NOTE_DELETED"
  | "CLAIM_CREATED"
  | "CLAIM_UPDATED"
  | "CLAIM_DELETED"
  | "SOURCE_LINKED"
  | "SOURCE_UNLINKED"
  | "EVIDENCE_ATTACHED"
  | "EVIDENCE_REMOVED";

export interface ResearchInvestigation {
  investigation_id: string;
  owner_user_id: string;
  title: string;
  description?: string;
  primary_subject_entity_id?: string;
  primary_subject_type?: string;
  secondary_entity_ids: string[];
  research_type: ResearchType;
  research_objective?: string;
  status: InvestigationLifecycleStatus;
  revision: number;
  created_at: string;
  updated_at: string;
  archived_at?: string;
  provenance: Record<string, any>;
  notes_count: number;
  sources_count: number;
  questions_count: number;
  hypotheses_count: number;
  claims_count: number;
  evidence_count: number;
}

export interface CreateResearchInvestigationDTO {
  title: string;
  research_type?: ResearchType;
  primary_subject_entity_id?: string;
  primary_subject_type?: string;
  secondary_entity_ids?: string[];
  research_objective?: string;
  description?: string;
}

export interface UpdateResearchInvestigationDTO {
  expected_revision: number;
  title?: string;
  research_type?: ResearchType;
  primary_subject_entity_id?: string;
  primary_subject_type?: string;
  secondary_entity_ids?: string[];
  research_objective?: string;
  description?: string;
  status?: InvestigationLifecycleStatus;
}

export interface ResearchQuestion {
  question_id: string;
  investigation_id: string;
  question_text: string;
  status: ResearchQuestionStatus;
  related_entity_ids: string[];
  related_evidence_ids: string[];
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface CreateResearchQuestionDTO {
  question_text: string;
  related_entity_ids?: string[];
}

export interface UpdateResearchQuestionDTO {
  question_text?: string;
  status?: ResearchQuestionStatus;
  related_entity_ids?: string[];
  related_evidence_ids?: string[];
}

export interface ResearchHypothesis {
  hypothesis_id: string;
  investigation_id: string;
  statement: string;
  status: ResearchHypothesisStatus;
  related_claim_ids: string[];
  related_evidence_ids: string[];
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface CreateResearchHypothesisDTO {
  statement: string;
  related_claim_ids?: string[];
  related_evidence_ids?: string[];
}

export interface UpdateResearchHypothesisDTO {
  statement?: string;
  status?: ResearchHypothesisStatus;
  related_claim_ids?: string[];
  related_evidence_ids?: string[];
}

export interface ResearchNoteRevision {
  revision_id: string;
  note_id: string;
  revision_number: number;
  title: string;
  body_document: string;
  author_user_id: string;
  created_at: string;
}

export interface ResearchNote {
  note_id: string;
  investigation_id: string;
  owner_user_id: string;
  title: string;
  body_document: string;
  note_type: ResearchNoteType;
  status: ResearchNoteStatus;
  related_entity_ids: string[];
  linked_source_ids: string[];
  linked_evidence_ids: string[];
  citation_ids: string[];
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface CreateResearchNoteDTO {
  title: string;
  body_document?: string;
  note_type?: ResearchNoteType;
  related_entity_ids?: string[];
  linked_source_ids?: string[];
  linked_evidence_ids?: string[];
}

export interface UpdateResearchNoteDTO {
  expected_revision: number;
  title?: string;
  body_document?: string;
  note_type?: ResearchNoteType;
  status?: ResearchNoteStatus;
  related_entity_ids?: string[];
  linked_source_ids?: string[];
  linked_evidence_ids?: string[];
  citation_ids?: string[];
}

export interface ResearchClaim {
  claim_id: string;
  investigation_id: string;
  statement: string;
  claim_category: ResearchClaimCategory;
  evidence_status: ResearchEvidenceStatus;
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  related_entity_ids: string[];
  author_user_id: string;
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface CreateResearchClaimDTO {
  statement: string;
  claim_category?: ResearchClaimCategory;
  evidence_status?: ResearchEvidenceStatus;
  supporting_evidence_ids?: string[];
  contradicting_evidence_ids?: string[];
  related_entity_ids?: string[];
}

export interface UpdateResearchClaimDTO {
  statement?: string;
  claim_category?: ResearchClaimCategory;
  evidence_status?: ResearchEvidenceStatus;
  supporting_evidence_ids?: string[];
  contradicting_evidence_ids?: string[];
  related_entity_ids?: string[];
}

export interface ResearchSourceReference {
  source_reference_id: string;
  canonical_document_id?: string;
  canonical_entity_id?: string;
  source_type: ResearchSourceType;
  provider_id: string;
  publisher_id?: string;
  source_title: string;
  source_url?: string;
  published_at?: string;
  source_updated_at?: string;
  first_observed_at: string;
  registered_at: string;
  reporting_period?: string;
  source_revision?: string;
  rights_policy: string;
  availability_status: SourceAvailabilityStatus;
  provenance: Record<string, any>;
}

export interface LinkResearchSourceDTO {
  source_reference_id?: string;
  canonical_document_id?: string;
  canonical_entity_id?: string;
  source_type?: ResearchSourceType;
  provider_id?: string;
  publisher_id?: string;
  source_title?: string;
  source_url?: string;
  published_at?: string;
  reporting_period?: string;
  source_revision?: string;
  rights_policy?: string;
}

export interface ResearchEvidence {
  evidence_id: string;
  investigation_id: string;
  source_reference_id: string;
  canonical_source_entity_id?: string;
  evidence_type: string;
  source_location_type: EvidenceLocationType;
  source_location_reference: string;
  page_number?: number;
  section_name?: string;
  source_revision?: string;
  observation_time: string;
  allowed_excerpt?: string;
  linked_claim_ids: string[];
  created_by: string;
  created_at: string;
  availability_status: SourceAvailabilityStatus;
  provenance: Record<string, any>;
  source_title?: string;
  publisher_id?: string;
  source_url?: string;
}

export interface AttachResearchEvidenceDTO {
  source_reference_id: string;
  evidence_type?: string;
  source_location_type?: EvidenceLocationType;
  source_location_reference: string;
  page_number?: number;
  section_name?: string;
  allowed_excerpt?: string;
  linked_claim_ids?: string[];
}

export interface ResearchCitation {
  citation_id: string;
  investigation_id: string;
  evidence_id: string;
  source_reference_id: string;
  citation_label: string;
  location_reference: string;
  source_revision?: string;
  created_at: string;
  is_broken: boolean;
  status_reason?: string;
  source_title?: string;
  source_url?: string;
  publisher_id?: string;
}

export interface ResearchActivity {
  activity_id: string;
  investigation_id: string;
  action_type: ResearchActivityAction;
  actor_user_id: string;
  object_type: string;
  object_id: string;
  details: Record<string, any>;
  occurred_at: string;
}

export interface ResearchOverviewSummary {
  active_investigations_count: number;
  draft_investigations_count: number;
  completed_investigations_count: number;
  archived_investigations_count: number;
  total_notes_count: number;
  total_sources_count: number;
  total_evidence_count: number;
  recent_investigations: ResearchInvestigation[];
  recent_activities: ResearchActivity[];
}
