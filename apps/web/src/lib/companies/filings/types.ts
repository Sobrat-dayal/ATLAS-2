/**
 * TypeScript Type Definitions for Regulatory Company Filings Intelligence (Stage 86).
 */

export type Regulator =
  | "SEC_EDGAR"
  | "SEBI"
  | "NSE"
  | "BSE"
  | "MCA"
  | "COMPANIES_HOUSE"
  | "OTHER_REGULATOR";

export type FilingCategory =
  | "ANNUAL_REPORTS"
  | "QUARTERLY_REPORTS"
  | "CURRENT_REPORTS"
  | "OWNERSHIP_INSIDER"
  | "PROXY_STATEMENTS"
  | "REGISTRATION_STATEMENTS"
  | "OTHER_REGULATORY";

export type DocumentMediaType =
  | "HTML"
  | "XML_XBRL"
  | "PDF"
  | "PLAIN_TEXT"
  | "JSON";

export type AmendmentStatus = "ORIGINAL" | "AMENDMENT" | "SUPERSEDED";

export type XBRLContextPeriodType = "INSTANT" | "DURATION";

export type XBRLUnitType = "USD" | "SHARES" | "USD_PER_SHARE" | "PERCENT" | "PURE";

export interface FilingDocumentDTO {
  document_id: string;
  filename: string;
  document_type: string;
  description: string;
  media_type: DocumentMediaType;
  byte_size: number;
  content_hash: string;
  source_url: string;
  is_primary: boolean;
}

export interface FilingSectionDTO {
  item_id: string;
  title: string;
  anchor: string;
  char_offset: number;
  char_length: number;
  summary_excerpt?: string | null;
}

export interface XBRLFactDTO {
  fact_id: string;
  concept_name: string;
  label: string;
  period_type: XBRLContextPeriodType;
  period_end: string;
  period_start?: string | null;
  unit: XBRLUnitType;
  exact_value: number;
  formatted_value: string;
  decimals?: number | null;
  dimensions: Record<string, string>;
}

export interface XBRLFactsResponseDTO {
  filing_id: string;
  accession_number: string;
  total_count: number;
  items: XBRLFactDTO[];
}

export interface FilingSummaryDTO {
  filing_id: string;
  company_id: string;
  filer_cik: string;
  filer_name: string;
  regulator: Regulator;
  accession_number: string;
  form_type: string;
  category: FilingCategory;
  reporting_period: string;
  filing_date: string;
  acceptance_timestamp?: string | null;
  publication_timestamp?: string | null;
  is_amendment: boolean;
  amendment_status: AmendmentStatus;
  amends_accession_number?: string | null;
  primary_document_name: string;
  title: string;
  document_count: number;
  fact_count: number;
}

export interface FilingCatalogResponseDTO {
  company_id: string;
  total_count: number;
  limit: number;
  offset: number;
  items: FilingSummaryDTO[];
}

export interface FilingDetailDTO {
  filing_id: string;
  company_id: string;
  filer_cik: string;
  filer_name: string;
  regulator: Regulator;
  accession_number: string;
  form_type: string;
  category: FilingCategory;
  reporting_period: string;
  filing_date: string;
  acceptance_timestamp?: string | null;
  publication_timestamp?: string | null;
  is_amendment: boolean;
  amendment_status: AmendmentStatus;
  amends_accession_number?: string | null;
  primary_document_name: string;
  primary_document_url: string;
  title: string;
  documents: FilingDocumentDTO[];
  sections: FilingSectionDTO[];
  fact_count: number;
  full_text_indexed: boolean;
}

export interface FilingContentDTO {
  filing_id: string;
  document_id: string;
  accession_number: string;
  filename: string;
  media_type: DocumentMediaType;
  content_html?: string | null;
  content_text?: string | null;
}

export interface FilingSearchHitDTO {
  filing_id: string;
  document_id: string;
  accession_number: string;
  form_type: string;
  reporting_period: string;
  filing_date: string;
  section_name?: string | null;
  matched_snippet: string;
  char_offset: number;
  score: number;
}

export interface FilingSearchResponseDTO {
  company_id: string;
  query: string;
  total_hits: number;
  hits: FilingSearchHitDTO[];
}

export interface SectionDiffDTO {
  section_name: string;
  added_lines_count: number;
  removed_lines_count: number;
  diff_text: string;
}

export interface XBRLFactDiffDTO {
  concept_name: string;
  label: string;
  period_label: string;
  unit: string;
  prior_value: number;
  current_value: number;
  absolute_difference: number;
  percentage_difference?: number | null;
  is_restatement: boolean;
}

export interface FilingComparisonResponseDTO {
  left_filing_id: string;
  right_filing_id: string;
  left_accession: string;
  right_accession: string;
  comparison_type: string;
  left_filing_date: string;
  right_filing_date: string;
  text_diff_sections: SectionDiffDTO[];
  xbrl_fact_diffs: XBRLFactDiffDTO[];
  total_text_changes: number;
  total_fact_adjustments: number;
}

export interface FilingCoverageDTO {
  company_id: string;
  company_name: string;
  regulator: Regulator;
  filer_cik: string;
  total_filings: number;
  forms_available: string[];
  latest_filing_date?: string | null;
  oldest_filing_date?: string | null;
  source_policy: string;
  user_agent_configured: string;
}

export interface FilingSourceReferenceDTO {
  filing_id: string;
  regulator: Regulator;
  accession_number: string;
  filer_cik: string;
  official_url: string;
  primary_document_url: string;
  content_hash: string;
  retrieved_timestamp: string;
  source_attribution: string;
  license_tier: string;
}

export interface FilingsOverviewSummaryDTO {
  company_id: string;
  coverage: FilingCoverageDTO;
  latest_annual?: FilingSummaryDTO | null;
  latest_quarterly?: FilingSummaryDTO | null;
  latest_current_report?: FilingSummaryDTO | null;
}
