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

// ---------------------------------------------------------------------------
// Stage 105 — Document Intelligence & Discovery Types
// ---------------------------------------------------------------------------

export type DocumentFormat =
  | "PDF"
  | "HTML"
  | "DOCX"
  | "PLAIN_TEXT"
  | "XBRL_XML"
  | "JSON_DATA";

export type DocumentProcessingStatus =
  | "NOT_STARTED"
  | "QUEUED"
  | "PROCESSING"
  | "COMPLETED"
  | "PARTIAL"
  | "FAILED"
  | "RESTRICTED"
  | "UNSUPPORTED";

export type SearchMode =
  | "KEYWORD"
  | "EXACT_PHRASE"
  | "SEMANTIC"
  | "HYBRID";

export type DocumentComparisonMode =
  | "FULL_TEXT"
  | "SECTIONS"
  | "FINANCIAL_TABLES";

export type UnitScale =
  | "UNITS"
  | "THOUSANDS"
  | "MILLIONS"
  | "BILLIONS"
  | "PERCENTAGE"
  | "PER_SHARE"
  | "INDEX_POINTS"
  | "BASIS_POINTS";

export interface ResearchSourceDiscoveryQuery {
  text_query?: string;
  entity_ids?: string[];
  instrument_ids?: string[];
  source_type_ids?: ResearchSourceType[];
  publisher_ids?: string[];
  filing_types?: string[];
  reporting_period_range?: string;
  date_from?: string;
  date_to?: string;
  availability_statuses?: SourceAvailabilityStatus[];
  search_mode?: SearchMode;
  sort_by?: "RELEVANCE" | "DATE_DESC" | "DATE_ASC" | "TITLE";
  limit?: number;
  cursor?: string;
}

export interface ResearchSearchHit {
  hit_id: string;
  source_reference_id: string;
  source_type: ResearchSourceType;
  source_title: string;
  score: number;
  availability_status: SourceAvailabilityStatus;
  rights_policy: string;
  canonical_document_id?: string;
  canonical_entity_id?: string;
  publisher_id?: string;
  published_at?: string;
  reporting_period?: string;
  matched_snippet: string;
  matched_spans: Array<{
    span_id?: string;
    section_heading?: string;
    page_number?: number;
  }>;
}

export interface ResearchSourceDiscoveryResponse {
  hits: ResearchSearchHit[];
  total_count: number;
  next_cursor?: string;
  query_summary: Record<string, any>;
}

export interface ResearchSourceTypeItem {
  source_type: ResearchSourceType;
  display_name: string;
  description: string;
  rights_classification: string;
  is_searchable: boolean;
}

export interface ResearchSourceTypeListResponse {
  items: ResearchSourceTypeItem[];
  total_count: number;
}

export interface ResearchDocumentProcessingStatus {
  processing_id: string;
  canonical_document_id: string;
  source_reference_id: string;
  source_revision: string;
  source_format: DocumentFormat;
  processor_version: string;
  processing_status: DocumentProcessingStatus;
  started_at: string;
  completed_at?: string;
  extracted_section_count: number;
  extracted_table_count: number;
  extracted_span_count: number;
  errors: string[];
  content_rights_status: string;
}

export interface ResearchDocumentSection {
  section_id: string;
  canonical_document_id: string;
  source_reference_id: string;
  source_revision: string;
  heading: string;
  section_path: string;
  level: number;
  start_char_offset: number;
  end_char_offset: number;
  parent_section_id?: string;
  page_number?: number;
  text_preview: string;
}

export interface ResearchDocumentOutline {
  canonical_document_id: string;
  source_reference_id: string;
  document_title: string;
  sections: ResearchDocumentSection[];
  total_sections: number;
}

export interface DocumentSearchRequest {
  query: string;
  section_id?: string;
  limit?: number;
}

export interface DocumentSearchHit {
  span_id: string;
  snippet: string;
  match_start: number;
  match_end: number;
  section_id?: string;
  section_heading?: string;
  page_number?: number;
  paragraph_number?: number;
}

export interface DocumentSearchResponse {
  query: string;
  total_matches: number;
  hits: DocumentSearchHit[];
}

export interface ResearchDocumentTable {
  table_id: string;
  canonical_document_id: string;
  source_reference_id: string;
  source_revision: string;
  title: string;
  period_label: string;
  currency: string;
  unit_scale: UnitScale;
  headers: string[];
  row_labels: string[];
  cells: string[][];
  raw_values: Array<Array<number | null>>;
  section_id?: string;
  footnotes: string[];
  associated_fact_ids: string[];
}

export interface ResearchDocumentTableListResponse {
  items: ResearchDocumentTable[];
  total_count: number;
}

export interface ResearchEvidenceCandidate {
  candidate_id: string;
  source_reference_id: string;
  source_title: string;
  extracted_text: string;
  evidence_type: string;
  location_reference: string;
  canonical_document_id?: string;
  canonical_entity_id?: string;
  section_heading?: string;
  page_number?: number;
  paragraph_number?: number;
  reporting_period?: string;
  unit?: string;
  currency?: string;
  numeric_value?: number;
  source_revision?: string;
  provenance: Record<string, any>;
}

export interface EvidenceCandidateListResponse {
  items: ResearchEvidenceCandidate[];
  total_count: number;
}

export interface ResolveEvidenceLocationRequest {
  source_reference_id: string;
  location_type: EvidenceLocationType;
  location_reference: string;
  page_number?: number;
  section_name?: string;
}

export interface ResolveEvidenceLocationResponse {
  is_valid: boolean;
  resolved_anchor: string;
  context_snippet?: string;
  error_message?: string;
}

export interface ConvertEvidenceCandidateDTO {
  candidate_id: string;
  investigation_id: string;
  claim_id?: string;
  relationship_type?: "SUPPORTS" | "CONTRADICTS" | "CONTEXT";
}

export interface DocumentComparisonRequest {
  left_document_id: string;
  right_document_id: string;
  left_source_revision?: string;
  right_source_revision?: string;
  comparison_mode?: DocumentComparisonMode;
}

export interface DocumentComparisonSectionDiff {
  section_name: string;
  alignment_status: string;
  added_lines_count: number;
  removed_lines_count: number;
  diff_unified: string;
  left_section_heading?: string;
  right_section_heading?: string;
  left_location_ref?: string;
  right_location_ref?: string;
}

export interface FinancialFactComparison {
  fact_key: string;
  label: string;
  left_period: string;
  right_period: string;
  currency: string;
  unit_scale: UnitScale;
  left_value: number;
  right_value: number;
  absolute_delta: number;
  percentage_delta: number | null;
  is_restated: boolean;
  compatibility_status: string;
}

export interface DocumentComparisonResult {
  comparison_id: string;
  left_document_id: string;
  right_document_id: string;
  left_title: string;
  right_title: string;
  total_added_lines: number;
  total_removed_lines: number;
  section_diffs: DocumentComparisonSectionDiff[];
  financial_fact_diffs: FinancialFactComparison[];
  compared_at: string;
  left_period?: string;
  right_period?: string;
  comparison_mode: DocumentComparisonMode;
  compatibility_warnings: string[];
}

export interface FinancialFactsCompareRequest {
  entity_id: string;
  left_period: string;
  right_period: string;
  concepts?: string[];
}

export interface FinancialFactsCompareResponse {
  entity_id: string;
  left_period: string;
  right_period: string;
  fact_diffs: FinancialFactComparison[];
  total_concepts_compared: number;
}

// ---------------------------------------------------------------------------
// Stage 106 — Research Analysis, Hypothesis Testing & Scenarios
// ---------------------------------------------------------------------------

export type ResearchAnalysisType =
  | "COMPANY_FINANCIAL_TREND"
  | "COMPANY_RATIO_ANALYSIS"
  | "CASH_FLOW_ANALYSIS"
  | "CAPITAL_STRUCTURE_ANALYSIS"
  | "PEER_BENCHMARKING"
  | "INDUSTRY_COMPARISON"
  | "MACROECONOMIC_TIME_SERIES"
  | "MULTI_INDICATOR_COMPARISON"
  | "HISTORICAL_MARKET_CONTEXT"
  | "EVENT_DISCLOSURE_COMPARISON"
  | "HYPOTHESIS_EVALUATION"
  | "DESCRIPTIVE_STATISTICAL_ANALYSIS"
  | "ASSUMPTION_SENSITIVITY_ANALYSIS";

export type AnalysisExecutionStatus =
  | "DRAFT"
  | "CONFIGURED"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "OUTDATED"
  | "ARCHIVED";

export type AnalysisInputPolicy =
  | "PINNED_SOURCE_VERSION"
  | "LATEST_AUTHORIZED_DATA";

export type AnalysisFrequency =
  | "ANNUAL"
  | "QUARTERLY"
  | "MONTHLY"
  | "DAILY"
  | "TTM";

export type HypothesisEvaluationOutcome =
  | "CRITERIA_MET"
  | "CRITERIA_NOT_MET"
  | "MIXED_RESULTS"
  | "INCONCLUSIVE"
  | "INSUFFICIENT_DATA"
  | "INVALID_TEST";

export type ResearchFindingType =
  | "OBSERVED_FACT"
  | "CALCULATED_RESULT"
  | "STATISTICAL_OBSERVATION"
  | "ANALYST_INTERPRETATION"
  | "INCONCLUSIVE_RESULT";

export type ResearchFindingReviewStatus =
  | "DRAFT"
  | "NEEDS_EVIDENCE"
  | "READY_FOR_REVIEW"
  | "REVIEWED"
  | "REVISED"
  | "ARCHIVED";

export type AssumptionSourceType =
  | "SOURCE_REPORTED"
  | "ANALYST_ASSUMED"
  | "DERIVED";

export type ScenarioType =
  | "BASE_ASSUMPTION"
  | "ALTERNATIVE_A"
  | "ALTERNATIVE_B"
  | "CUSTOM_SENSITIVITY";

export type OutlierHandlingPolicy =
  | "INCLUDE_ALL"
  | "EXCLUDE_EXTREMES"
  | "WINSORIZE";

export interface AnalyticalObservationRow {
  period_label: string;
  metric_id: string;
  metric_name: string;
  raw_value?: number | null;
  display_value: string;
  unit: string;
  currency?: string | null;
  period_delta?: number | null;
  percentage_growth?: number | null;
  source_id?: string | null;
  source_title?: string | null;
  source_accession?: string | null;
  is_restated: boolean;
  is_missing: boolean;
  missing_reason?: string | null;
  observed_date?: string | null;
  publication_cutoff?: string | null;
}

export interface AnalyticalSummaryStatistics {
  sample_size_n: number;
  mean?: number | null;
  median?: number | null;
  minimum?: number | null;
  maximum?: number | null;
  standard_deviation?: number | null;
  quartile_1?: number | null;
  quartile_3?: number | null;
  cagr_percentage?: number | null;
  correlation_coefficient?: number | null;
  missing_count: number;
  outlier_count: number;
  correlation_is_not_causation_notice: boolean;
}

export interface ResearchAnalysisSpecification {
  analysis_type: ResearchAnalysisType;
  primary_entity_id: string;
  secondary_entity_ids?: string[];
  metric_ids: string[];
  frequency?: AnalysisFrequency;
  time_range_start?: string | null;
  time_range_end?: string | null;
  input_version_policy?: AnalysisInputPolicy;
  currency?: string;
  unit?: string;
  outlier_policy?: OutlierHandlingPolicy;
  methodology_version?: number;
  as_known_at_cutoff?: string | null;
}

export interface ResearchAnalysis {
  analysis_id: string;
  investigation_id?: string | null;
  owner_user_id: string;
  title: string;
  description?: string;
  analysis_type: ResearchAnalysisType;
  research_objective?: string;
  primary_subject_entity_id?: string;
  primary_subject_type?: string;
  secondary_entity_ids: string[];
  specification: ResearchAnalysisSpecification;
  status: AnalysisExecutionStatus;
  current_revision: number;
  latest_run_id?: string | null;
  created_at: string;
  updated_at: string;
  archived_at?: string | null;
  provenance: Record<string, unknown>;
  linked_question_ids: string[];
  linked_hypothesis_ids: string[];
  runs_count: number;
  findings_count: number;
  assumptions_count: number;
}

export interface ResearchAnalysisRun {
  run_id: string;
  analysis_id: string;
  analysis_revision: number;
  owner_user_id: string;
  input_specification_hash: string;
  methodology_version: number;
  input_policy: AnalysisInputPolicy;
  source_data_manifest: Array<Record<string, unknown>>;
  started_at: string;
  completed_at?: string | null;
  execution_status: AnalysisExecutionStatus;
  observations_count: number;
  error_message?: string | null;
  warnings: string[];
  compute_duration_ms: number;
  provenance: Record<string, unknown>;
}

export interface ResearchAnalysisResult {
  run_id: string;
  analysis_id: string;
  analysis_type: ResearchAnalysisType;
  execution_status: AnalysisExecutionStatus;
  primary_subject_id: string;
  metric_id: string;
  observations: AnalyticalObservationRow[];
  summary_statistics: AnalyticalSummaryStatistics;
  comparability_warnings: string[];
  source_data_manifest: Array<Record<string, unknown>>;
  executed_at: string;
  reproducibility_hash: string;
  methodology_description: string;
}

export interface HypothesisTestCriteria {
  metric_id: string;
  operator: "GT" | "GTE" | "LT" | "LTE" | "EQ" | "BETWEEN";
  threshold_value: number;
  secondary_threshold?: number | null;
  required_periods_count?: number;
  allow_missing?: boolean;
}

export interface ResearchHypothesisEvaluation {
  evaluation_id: string;
  hypothesis_id: string;
  analysis_run_id: string;
  owner_user_id: string;
  criteria: HypothesisTestCriteria;
  eligible_universe: string[];
  observation_count: number;
  result_status: HypothesisEvaluationOutcome;
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  limitations: string[];
  analyst_notes?: string;
  created_at: string;
  provenance: Record<string, unknown>;
}

export interface ResearchFinding {
  finding_id: string;
  investigation_id?: string | null;
  analysis_id: string;
  analysis_run_id?: string | null;
  author_user_id: string;
  finding_type: ResearchFindingType;
  statement: string;
  methodology_description?: string;
  supporting_evidence_ids: string[];
  contradicting_evidence_ids: string[];
  calculated_result_references: Record<string, unknown>;
  limitations: string[];
  review_status: ResearchFindingReviewStatus;
  revision: number;
  created_at: string;
  updated_at: string;
  provenance: Record<string, unknown>;
}

export interface ResearchAssumption {
  assumption_id: string;
  analysis_id: string;
  owner_user_id: string;
  label: string;
  parameter_id: string;
  value: number;
  unit: string;
  source_type: AssumptionSourceType;
  source_reference_id?: string | null;
  analyst_note?: string;
  revision: number;
  created_at: string;
}

export interface ResearchScenario {
  scenario_id: string;
  analysis_id: string;
  owner_user_id: string;
  scenario_type: ScenarioType;
  label: string;
  assumption_ids: string[];
  deterministic_parameters: Record<string, number>;
  is_non_predictive_illustrative: boolean;
  created_at: string;
}

export interface ResearchAnalysisTypeDefinition {
  type_id: ResearchAnalysisType;
  label: string;
  description: string;
  supported_subject_types: string[];
  supported_frequencies: AnalysisFrequency[];
  required_parameters: string[];
  default_metric_ids: string[];
  methodology_version: number;
  is_active: boolean;
}

export interface CreateResearchAnalysisDTO {
  title: string;
  description?: string;
  analysis_type: ResearchAnalysisType;
  research_objective?: string;
  primary_subject_entity_id?: string;
  primary_subject_type?: string;
  secondary_entity_ids?: string[];
  specification: ResearchAnalysisSpecification;
  investigation_id?: string | null;
  linked_question_ids?: string[];
  linked_hypothesis_ids?: string[];
}

export interface UpdateResearchAnalysisDTO {
  expected_revision: number;
  title?: string;
  description?: string;
  research_objective?: string;
  specification?: ResearchAnalysisSpecification;
  linked_question_ids?: string[];
  linked_hypothesis_ids?: string[];
}

export interface CreateResearchFindingDTO {
  analysis_id: string;
  analysis_run_id?: string | null;
  finding_type: ResearchFindingType;
  statement: string;
  methodology_description?: string;
  supporting_evidence_ids?: string[];
  contradicting_evidence_ids?: string[];
  calculated_result_references?: Record<string, unknown>;
  limitations?: string[];
  review_status?: ResearchFindingReviewStatus;
  investigation_id?: string | null;
}

export interface UpdateResearchFindingDTO {
  expected_revision: number;
  statement?: string;
  methodology_description?: string;
  supporting_evidence_ids?: string[];
  contradicting_evidence_ids?: string[];
  calculated_result_references?: Record<string, unknown>;
  limitations?: string[];
  review_status?: ResearchFindingReviewStatus;
}

export interface CreateResearchAssumptionDTO {
  label: string;
  parameter_id: string;
  value: number;
  unit: string;
  source_type: AssumptionSourceType;
  source_reference_id?: string | null;
  analyst_note?: string;
}

export interface ExecuteHypothesisEvaluationDTO {
  analysis_run_id: string;
  criteria: HypothesisTestCriteria;
  eligible_universe?: string[];
  analyst_notes?: string;
}

export interface SensitivityAnalysisRequest {
  base_metric_value: number;
  metric_name: string;
  unit?: string;
  growth_rates?: number[];
  margin_rates?: number[];
  notes?: string;
}

export interface SensitivityAnalysisResponse {
  base_metric_value: number;
  metric_name: string;
  unit: string;
  growth_rates: number[];
  margin_rates: number[];
  scenario_matrix: number[][];
  is_non_predictive_illustrative: boolean;
  qualification_notice: string;
}

export interface ValidateAnalysisSpecificationRequest {
  specification: ResearchAnalysisSpecification;
}

export interface ValidateAnalysisSpecificationResponse {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  estimated_observation_count: number;
}

// ---------------------------------------------------------------------------
// Stage 107 — Report Studio & Investment Thesis Types
// ---------------------------------------------------------------------------

export type ResearchReportType =
  | "COMPANY_RESEARCH"
  | "EQUITY_INITIATION"
  | "EQUITY_INITIATION_DRAFT"
  | "COMPANY_UPDATE"
  | "EARNINGS_REVIEW"
  | "INDUSTRY_PRIMER"
  | "INDUSTRY_RESEARCH"
  | "MACROECONOMIC_REPORT"
  | "MACROECONOMIC_RESEARCH"
  | "FINANCIAL_EVENT_NOTE"
  | "FUNDAMENTAL_ANALYSIS"
  | "PEER_BENCHMARKING"
  | "INVESTMENT_THESIS"
  | "EVENT_MEMO"
  | "RISK_BRIEF"
  | "RISK_RESEARCH_NOTE"
  | "GENERAL_RESEARCH_MEMORANDUM"
  | "CUSTOM";

export type ReportLifecycleStatus =
  | "DRAFT"
  | "IN_PROGRESS"
  | "READY_FOR_REVIEW"
  | "REVIEWED"
  | "UNDER_REVIEW"
  | "FINALIZED"
  | "PUBLISHED"
  | "SUPERSEDED"
  | "ARCHIVED";

export type ReportSectionType =
  | "EXECUTIVE_SUMMARY"
  | "COMPANY_OVERVIEW"
  | "BUSINESS_MODEL"
  | "INDUSTRY_CONTEXT"
  | "FINANCIAL_PERFORMANCE"
  | "PROFITABILITY_CASH_FLOW"
  | "CAPITAL_STRUCTURE"
  | "PEER_BENCHMARKING"
  | "INVESTMENT_THESIS"
  | "BULL_BEAR_CASE"
  | "BULL_BEAR_CASES"
  | "VALUATION_CONTEXT"
  | "VALUATION_FRAMEWORK"
  | "INDUSTRY_DYNAMICS"
  | "KEY_RISKS"
  | "RISK_FACTORS"
  | "CATALYSTS"
  | "METHODOLOGY"
  | "METHODOLOGY_AND_DATA"
  | "REFERENCES"
  | "DISCLOSURES"
  | "CUSTOM";

export type ReportBlockType =
  | "HEADING"
  | "HEADING_2"
  | "HEADING_3"
  | "PARAGRAPH"
  | "BULLET_LIST"
  | "NUMBERED_LIST"
  | "BLOCK_QUOTE"
  | "QUOTE"
  | "FINANCIAL_TABLE"
  | "ANALYSIS_TABLE"
  | "CHART"
  | "CALCULATION"
  | "CITATION"
  | "FOOTNOTE"
  | "PAGE_BREAK"
  | "REFERENCES";

export type ReportSnapshotPolicy =
  | "DRAFT_LATEST_AUTHORIZED"
  | "PINNED_SOURCE_REFERENCES"
  | "FINALIZED_IMMUTABLE_SNAPSHOT";

export type ThesisLifecycleStatus =
  | "DRAFT"
  | "ACTIVE"
  | "UNDER_REVIEW"
  | "ACCEPTED"
  | "VALIDATED"
  | "DISPROVEN"
  | "REVISED"
  | "INVALIDATED"
  | "ARCHIVED";

export type ThesisArgumentType =
  | "SUPPORTING"
  | "OPPOSING"
  | "BULL_CASE"
  | "BEAR_CASE"
  | "BASE_CASE"
  | "CONTEXTUAL"
  | "ASSUMPTION"
  | "CORE_ASSUMPTION"
  | "RISK"
  | "KEY_RISK"
  | "CATALYST"
  | "CONTRADICTING_EVIDENCE"
  | "OPEN_QUESTION";

export type ExportFormat = "PDF" | "DOCX" | "HTML" | "MARKDOWN" | "JSON_ARCHIVE";

export type ExportStatus = "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED" | "EXPIRED";

export type VerificationIssueSeverity = "BLOCKING" | "WARNING" | "INFORMATIONAL";

export type VerificationIssueType =
  | "STRUCTURE_INCOMPLETE"
  | "MISSING_CITATION"
  | "BROKEN_CITATION"
  | "SOURCE_RESTRICTED"
  | "SOURCE_WITHDRAWN"
  | "SOURCE_REVISED"
  | "ANALYSIS_RUN_NOT_FOUND"
  | "ANALYSIS_RUN_OUTDATED"
  | "UNSUPPORTED_QUANTITATIVE_CLAIM"
  | "MISSING_METHODOLOGY"
  | "MISSING_DATA_PERIOD"
  | "MISSING_UNIT"
  | "UNDISCLOSED_ASSUMPTION"
  | "POINT_IN_TIME_CONFLICT"
  | "UNRESOLVED_CONTRADICTION";

export interface ResearchReportContentBlock {
  block_id: string;
  block_type: ReportBlockType;
  content?: string;
  text_content?: string;
  citation_ids?: string[];
  citation_id?: string;
  source_id?: string;
  publication_date?: string;
  analysis_run_id?: string;
  table_data?: Record<string, unknown>;
  table_content?: {
    columns: string[];
    rows: string[][];
    analysis_run_id?: string;
  };
  chart_config?: Record<string, unknown>;
  chart_spec?: {
    chart_type?: string;
    series_name?: string;
    data_points?: Array<{ period: string; value: number }>;
    analysis_run_id?: string;
  };
  caption?: string;
  metadata?: Record<string, unknown>;
}

export interface ResearchReportSection {
  section_id: string;
  report_id: string;
  parent_section_id?: string | null;
  order_index: number;
  section_type: ReportSectionType;
  title: string;
  heading?: string;
  blocks?: ResearchReportContentBlock[];
  content_blocks: ResearchReportContentBlock[];
  is_mandatory?: boolean;
  revision: number;
  created_at: string;
  updated_at: string;
}

export interface ResearchReport {
  report_id: string;
  owner_user_id: string;
  investigation_id?: string | null;
  report_type: ResearchReportType;
  title: string;
  subtitle?: string | null;
  abstract?: string | null;
  target_entity_id?: string | null;
  target_entity_name?: string | null;
  primary_author: string;
  co_authors?: string[];
  primary_subject_id?: string | null;
  primary_subject_type?: string | null;
  secondary_subject_ids?: string[];
  report_as_of?: string;
  research_cutoff?: string;
  template_id?: string | null;
  status: ReportLifecycleStatus;
  current_revision: number;
  revision: number;
  snapshot_policy?: ReportSnapshotPolicy;
  section_count: number;
  sections?: ResearchReportSection[];
  created_at: string;
  updated_at: string;
}

export interface ResearchReportDetail extends ResearchReport {
  sections: ResearchReportSection[];
  source_manifest: Array<Record<string, unknown>>;
  evidence_manifest: string[];
  analysis_run_manifest: string[];
}

export interface ResearchReportTemplate {
  template_id: string;
  template_version: number;
  report_type: ResearchReportType;
  title: string;
  description: string;
  default_sections: Array<{
    heading: string;
    section_type: ReportSectionType;
    content_blocks: Array<Record<string, unknown>>;
  }>;
  required_sections: ReportSectionType[];
  citation_style: string;
  is_active: boolean;
}

export interface ResearchReportRevision {
  revision_id: string;
  report_id: string;
  revision_number: number;
  parent_revision_id?: string | null;
  author_user_id: string;
  created_by?: string;
  word_count?: number;
  revision_status: ReportLifecycleStatus;
  change_summary?: string | null;
  content_hash: string;
  created_at: string;
}

export interface CompareReportRevisionsResponse {
  report_id: string;
  base_revision_number: number;
  target_revision_number: number;
  sections_added: string[];
  sections_removed: string[];
  sections_modified: string[];
  diff_unified: string;
}

export interface ResearchThesisArgument {
  argument_id: string;
  thesis_id: string;
  argument_type: ThesisArgumentType;
  statement: string;
  claim_ids?: string[];
  evidence_ids?: string[];
  evidence_citations?: string[];
  strength_score?: number;
  analysis_run_ids?: string[];
  finding_ids?: string[];
  limitations?: string[];
  revision: number;
  created_at: string;
}

export interface ResearchInvestmentThesis {
  thesis_id: string;
  investigation_id?: string | null;
  report_id?: string | null;
  owner_user_id: string;
  primary_subject_id?: string | null;
  primary_subject_type?: string | null;
  title: string;
  thesis_statement: string;
  time_horizon: string;
  horizon_months?: number;
  conviction_score?: number;
  target_entity_id?: string | null;
  target_entity_name?: string | null;
  status: ThesisLifecycleStatus;
  current_revision: number;
  summary?: string | null;
  bull_case_summary?: string | null;
  bear_case_summary?: string | null;
  base_case_summary?: string | null;
  assumptions_summary?: string | null;
  risks_summary?: string | null;
  catalysts_summary?: string | null;
  arguments?: ResearchThesisArgument[];
  created_at: string;
  updated_at: string;
}

export interface ResearchInvestmentThesisDetail extends ResearchInvestmentThesis {
  arguments: ResearchThesisArgument[];
}

export interface VerificationIssue {
  issue_type: VerificationIssueType;
  severity: VerificationIssueSeverity;
  message: string;
  section_id?: string | null;
  block_id?: string | null;
  reference_id?: string | null;
}

export interface ResearchReportVerification {
  verification_id: string;
  report_id: string;
  revision_number: number;
  checked_at: string;
  verified_at?: string;
  is_valid: boolean;
  blocking_issues_count: number;
  warnings_count: number;
  info_count: number;
  issues: VerificationIssue[];
  citation_coverage_pct: number;
  verified_by_user_id: string;
}

export interface ResearchReportExport {
  export_id: string;
  report_id: string;
  revision_number: number;
  owner_user_id: string;
  format: ExportFormat;
  export_status: ExportStatus;
  file_name?: string;
  download_url?: string | null;
  file_size_bytes: number;
  page_count: number;
  content_hash: string;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  expiry_at?: string | null;
  error_message?: string | null;
}

export interface CreateResearchReportDTO {
  investigation_id?: string | null;
  report_type: ResearchReportType;
  title: string;
  subtitle?: string | null;
  abstract?: string | null;
  target_entity_id?: string | null;
  target_entity_name?: string | null;
  primary_author?: string;
  co_authors?: string[];
  primary_subject_id?: string | null;
  primary_subject_type?: string | null;
  secondary_subject_ids?: string[];
  template_id?: string | null;
  report_as_of?: string | null;
  research_cutoff?: string | null;
  snapshot_policy?: ReportSnapshotPolicy;
}

export interface UpdateResearchReportDTO {
  expected_revision: number;
  title?: string;
  subtitle?: string | null;
  abstract?: string | null;
  primary_subject_id?: string | null;
  secondary_subject_ids?: string[];
  report_as_of?: string | null;
  research_cutoff?: string | null;
  snapshot_policy?: ReportSnapshotPolicy;
  status?: ReportLifecycleStatus;
}

export interface FinalizeResearchReportDTO {
  expected_revision: number;
  publication_notes?: string;
  disclaimer_override?: string;
}

export interface ReorderReportSectionsDTO {
  ordered_section_ids: string[];
}

export interface VerifyReportDTO {
  expected_revision?: number;
}

export interface CreateReportExportDTO {
  format: ExportFormat;
  include_disclosures?: boolean;
  include_citations?: boolean;
  include_charts?: boolean;
}

export interface CreateReportSectionDTO {
  parent_section_id?: string | null;
  order_index?: number | null;
  section_type?: ReportSectionType;
  title?: string;
  heading?: string;
  blocks?: ResearchReportContentBlock[];
  content_blocks?: Array<Record<string, unknown>>;
}

export interface UpdateReportSectionDTO {
  expected_revision: number;
  title?: string;
  heading?: string;
  section_type?: ReportSectionType;
  blocks?: ResearchReportContentBlock[];
  content_blocks?: Array<Record<string, unknown>>;
}

export interface CreateThesisDTO {
  title: string;
  summary?: string;
  target_entity_id?: string;
  target_entity_name?: string;
  horizon_months?: number;
  conviction_score?: number;
  investigation_id?: string;
  thesis_statement?: string;
}

export interface UpdateThesisDTO {
  title?: string;
  summary?: string;
  target_entity_id?: string;
  target_entity_name?: string;
  horizon_months?: number;
  conviction_score?: number;
  status?: ThesisLifecycleStatus;
  expected_revision?: number;
}

export interface CreateThesisArgumentDTO {
  argument_type: ThesisArgumentType;
  statement: string;
  claim_ids?: string[];
  evidence_ids?: string[];
  evidence_citations?: string[];
  strength_score?: number;
  analysis_run_ids?: string[];
  finding_ids?: string[];
  limitations?: string[];
}

export interface CreateResearchThesisDTO {
  investigation_id?: string | null;
  report_id?: string | null;
  primary_subject_id?: string | null;
  primary_subject_type?: string | null;
  thesis_statement: string;
  time_horizon?: string;
  bull_case_summary?: string | null;
  bear_case_summary?: string | null;
  base_case_summary?: string | null;
  assumptions_summary?: string | null;
  risks_summary?: string | null;
  catalysts_summary?: string | null;
}

export interface UpdateResearchThesisDTO {
  expected_revision: number;
  thesis_statement?: string;
  time_horizon?: string;
  status?: ThesisLifecycleStatus;
  bull_case_summary?: string | null;
  bear_case_summary?: string | null;
  base_case_summary?: string | null;
  assumptions_summary?: string | null;
  risks_summary?: string | null;
  catalysts_summary?: string | null;
}

// ---------------------------------------------------------------------------
// Stage 108 — Collaboration, Review, Evidence Governance & Circulation Types
// ---------------------------------------------------------------------------

export type ResearchRole = "OWNER" | "EDITOR" | "REVIEWER" | "COMMENTER" | "VIEWER";

export type ResearchPrincipalType = "USER" | "TEAM" | "GROUP";

export type ResearchResourceType = "INVESTIGATION" | "REPORT" | "THESIS";

export type ReviewScope =
  | "FULL_REPORT"
  | "DOCUMENT_CONTENT"
  | "FINANCIAL_MODEL"
  | "CITATION_AUDIT";

export type ReviewStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "IN_REVIEW"
  | "CHANGES_REQUESTED"
  | "APPROVED"
  | "REJECTED"
  | "CANCELED"
  | "SUPERSEDED";

export type ReviewDecisionType = "APPROVE" | "REQUEST_CHANGES" | "REJECT";

export type CommentAnchorType =
  | "REPORT_SECTION"
  | "CONTENT_BLOCK"
  | "TEXT_RANGE"
  | "CITATION"
  | "ANALYSIS_RUN"
  | "FINDING";

export type CommentThreadStatus = "OPEN" | "RESOLVED" | "REOPENED";

export type CirculationStatus = "ACTIVE" | "REVOKED" | "EXPIRED";

export type ResearchAuditEventType =
  | "GRANT_CREATED"
  | "GRANT_UPDATED"
  | "GRANT_REVOKED"
  | "REVIEW_SUBMITTED"
  | "REVIEW_DECIDED"
  | "COMMENT_ADDED"
  | "COMMENT_RESOLVED"
  | "COMMENT_REOPENED"
  | "QUALITY_GATE_RUN"
  | "REPORT_CIRCULATED"
  | "CIRCULATION_REVOKED";

export interface ResearchAccessGrantResponse {
  grant_id: string;
  resource_type: ResearchResourceType;
  resource_id: string;
  principal_type: ResearchPrincipalType;
  principal_id: string;
  role: ResearchRole;
  granted_by: string;
  organization_id?: string | null;
  created_at: string;
  expires_at?: string | null;
  revoked_at?: string | null;
}

export interface ResearchAccessGrantListResponse {
  grants: ResearchAccessGrantResponse[];
  total_count: number;
}

export interface CreateAccessGrantRequest {
  principal_type?: ResearchPrincipalType;
  principal_id: string;
  role: ResearchRole;
  expires_at?: string | null;
}

export interface UpdateAccessGrantRequest {
  role: ResearchRole;
}

export interface ResearchReviewDecisionResponse {
  decision_id: string;
  review_request_id: string;
  reviewer_user_id: string;
  target_revision_number: number;
  target_content_hash: string;
  decision: ReviewDecisionType;
  decision_comment?: string | null;
  decided_at: string;
}

export interface CreateReviewDecisionRequest {
  decision: ReviewDecisionType;
  decision_comment?: string | null;
  expected_revision_number?: number | null;
}

export interface ResearchReviewRequestResponse {
  review_request_id: string;
  target_type: ResearchResourceType;
  target_id: string;
  target_revision_number: number;
  target_content_hash: string;
  requested_by: string;
  assigned_reviewer_id: string;
  review_scope: ReviewScope;
  review_round: number;
  status: ReviewStatus;
  organization_id?: string | null;
  due_date?: string | null;
  instructions?: string | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
  latest_decision?: ResearchReviewDecisionResponse | null;
}

export interface ResearchReviewListResponse {
  reviews: ResearchReviewRequestResponse[];
  total_count: number;
}

export interface CreateReviewRequest {
  target_type?: ResearchResourceType;
  target_id: string;
  target_revision_number?: number | null;
  assigned_reviewer_id: string;
  review_scope?: ReviewScope;
  due_date?: string | null;
  instructions?: string | null;
}

export interface UpdateReviewRequest {
  assigned_reviewer_id?: string;
  due_date?: string | null;
  instructions?: string | null;
}

export interface ResearchApprovalStatusResponse {
  report_id: string;
  revision_number: number;
  is_approved: boolean;
  status_message: string;
  approval_id?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  target_content_hash?: string | null;
}

export interface ResearchCommentResponse {
  comment_id: string;
  thread_id: string;
  author_user_id: string;
  body: string;
  created_at: string;
  updated_at: string;
  edit_revision: number;
}

export interface ResearchCommentThreadResponse {
  thread_id: string;
  resource_type: string;
  resource_id: string;
  target_revision_number: number;
  anchor_type: CommentAnchorType;
  anchor_reference: string;
  anchor_text?: string | null;
  created_by: string;
  created_at: string;
  resolution_status: CommentThreadStatus;
  resolved_by?: string | null;
  resolved_at?: string | null;
  comments: ResearchCommentResponse[];
  is_stale?: boolean;
}

export interface ResearchCommentThreadListResponse {
  threads: ResearchCommentThreadResponse[];
  total_count: number;
}

export interface CreateCommentThreadRequest {
  target_revision_number?: number | null;
  anchor_type?: CommentAnchorType;
  anchor_reference: string;
  anchor_text?: string | null;
  initial_comment: string;
}

export interface CreateCommentReplyRequest {
  body: string;
}

export interface UpdateCommentRequest {
  body: string;
}

export interface QualityGateCheckItem {
  check_id: string;
  title: string;
  passed: boolean;
  detail: string;
}

export interface QualityGateResultResponse {
  gate_run_id: string;
  report_id: string;
  revision_number: number;
  executed_at: string;
  eligible_for_review: boolean;
  eligible_for_finalization: boolean;
  blocking_issues_count: number;
  warnings_count: number;
  issues: Record<string, unknown>[];
  checklist: QualityGateCheckItem[];
}

export interface RunQualityGateRequest {
  revision_number?: number | null;
}

export interface ResearchInternalCirculationResponse {
  circulation_id: string;
  report_id: string;
  revision_number: number;
  initiated_by: string;
  recipient_user_ids: string[];
  organization_id?: string | null;
  status: CirculationStatus;
  notes?: string | null;
  created_at: string;
  revoked_at?: string | null;
}

export interface ResearchInternalCirculationListResponse {
  circulations: ResearchInternalCirculationResponse[];
  total_count: number;
}

export interface CreateCirculationRequest {
  revision_number?: number | null;
  recipient_user_ids: string[];
  notes?: string | null;
}

export interface ResearchReviewAuditEventResponse {
  audit_event_id: string;
  actor_user_id: string;
  resource_type: string;
  resource_id: string;
  action: string;
  occurred_at: string;
  organization_id?: string | null;
  target_revision_number?: number | null;
  details: Record<string, unknown>;
}

export interface ResearchReviewAuditEventListResponse {
  events: ResearchReviewAuditEventResponse[];
  total_count: number;
}


