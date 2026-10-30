/**
 * ATLAS Stage 127: AI Research and Retrieval-Augmented Generation Types.
 * Frontend contracts and data transfer objects matching backend schemas.
 */

export type ResearchSourceType =
  | "CORPORATE_FILING"
  | "EARNINGS_TRANSCRIPT"
  | "RESEARCH_REPORT"
  | "ECONOMIC_PUBLICATION"
  | "NEWS_ARTICLE"
  | "USER_DOCUMENT";

export type LicensingClass =
  | "PUBLIC_DOMAIN"
  | "PROPRIETARY_LICENSED"
  | "INTERNAL_CONFIDENTIAL"
  | "USER_PRIVATE";

export type ProviderDisclosurePolicy =
  | "ALLOWED"
  | "REDACTED_ONLY"
  | "PROHIBITED";

export type RetrievalStrategy =
  | "LEXICAL"
  | "SEMANTIC"
  | "HYBRID_FUSION"
  | "HYBRID_RERANK";

export type ResearchRunStatus =
  | "IDLE"
  | "PLANNING"
  | "RETRIEVING"
  | "RERANKING"
  | "ASSEMBLING_EVIDENCE"
  | "GENERATING"
  | "VALIDATING_CITATIONS"
  | "COMPLETED"
  | "INSUFFICIENT_EVIDENCE"
  | "FAILED"
  | "CANCELLED";

export type CitationValidationStatus =
  | "VERIFIED"
  | "REJECTED"
  | "ACCESS_DENIED"
  | "EXPIRED"
  | "UNSUPPORTED_CLAIM";

export interface ResearchSourceDTO {
  source_id: string;
  name: string;
  category: ResearchSourceType;
  licensing_class: LicensingClass;
  provider_disclosure: ProviderDisclosurePolicy;
  publisher: string;
  reliability_tier: string;
  created_at: string;
}

export interface ResearchDocumentDTO {
  document_id: string;
  source_id: string;
  title: string;
  document_type: string;
  publication_date: string;
  company_id?: string | null;
  symbol?: string | null;
  filing_date?: string | null;
  access_tier: string;
  created_at: string;
}

export interface ResearchPassageDTO {
  chunk_id: string;
  document_id: string;
  revision_id: string;
  title: string;
  symbol?: string | null;
  section_title: string;
  page_number: number;
  publication_date: string;
  snippet: string;
  exact_span: string;
  relevance_score: number;
  licensing_class: LicensingClass;
  content_hash: string;
}

export interface ResearchCitationDTO {
  citation_id: string;
  evidence_id: string;
  document_id: string;
  symbol?: string | null;
  title: string;
  page_number: number;
  section_title: string;
  publication_date: string;
  claim_text: string;
  quote_span: string;
  status: CitationValidationStatus;
  validation_reason?: string | null;
}

export interface ResearchSourceManifestDTO {
  manifest_id: string;
  run_id: string;
  sources_used: Array<Record<string, any>>;
  total_sources_evaluated: number;
  excluded_sources_count: number;
  coverage_summary: string;
  has_conflicting_sources: boolean;
  conflict_notes?: string | null;
}

export interface ResearchAnswerResponse {
  run_id: string;
  query: string;
  status: ResearchRunStatus;
  strategy: RetrievalStrategy;
  answer_text: string;
  citations: ResearchCitationDTO[];
  evidence_manifest?: ResearchSourceManifestDTO | null;
  limitations: string[];
  source_count: number;
  execution_time_ms: number;
  historical_as_of?: string | null;
  generated_at: string;
}

export interface ComparisonDifferenceDTO {
  aspect: string;
  doc_a_value: string;
  doc_b_value: string;
  difference_text: string;
  citation_a?: Record<string, any> | null;
  citation_b?: Record<string, any> | null;
}

export interface DocumentComparisonResponse {
  comparison_id: string;
  document_a_title: string;
  document_b_title: string;
  document_a_date: string;
  document_b_date: string;
  differences: ComparisonDifferenceDTO[];
  summary_text: string;
  citations: Array<Record<string, any>>;
  execution_time_ms: number;
}

export interface ResearchSearchRequest {
  query: string;
  symbols?: string[];
  document_types?: string[];
  source_ids?: string[];
  historical_as_of?: string;
  date_start?: string;
  date_end?: string;
  retrieval_strategy?: RetrievalStrategy;
  limit?: number;
}

export interface ResearchQueryRequest {
  query: string;
  symbols?: string[];
  document_types?: string[];
  historical_as_of?: string;
  date_start?: string;
  date_end?: string;
  retrieval_strategy?: RetrievalStrategy;
  max_evidence_units?: number;
  token_budget?: number;
  conversation_id?: string;
}

export interface DocumentComparisonRequest {
  document_id_a: string;
  document_id_b: string;
  aspects?: string[];
  historical_as_of?: string;
}

export interface IngestDocumentRequest {
  source_id: string;
  title: string;
  document_type: string;
  publication_date: string;
  content_text: string;
  symbol?: string;
  company_id?: string;
  filing_date?: string;
  access_tier?: string;
}

export interface IngestDocumentResponse {
  job_id: string;
  document_id: string;
  revision_id: string;
  chunks_created: number;
  indexing_status: string;
  content_hash: string;
}

