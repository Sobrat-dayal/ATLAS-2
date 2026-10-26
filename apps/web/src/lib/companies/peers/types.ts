/**
 * TypeScript definitions for ATLAS Company Peers and Comparable Company Analysis (Stage 87).
 * Strictly mirrors the backend DTOs and models.
 */

export type PeerRelationshipType =
  | "COMPARABLE_CANDIDATE"
  | "USER_SELECTED_PEER"
  | "SOURCE_DEFINED_PEER"
  | "VERIFIED_COMPETITOR";

export type IndustryTaxonomy = "GICS" | "ICB" | "NAICS" | "SIC";

export type ComparisonMetricCategory =
  | "SCALE"
  | "GROWTH"
  | "PROFITABILITY"
  | "LIQUIDITY"
  | "SOLVENCY"
  | "EFFICIENCY"
  | "VALUATION"
  | "CASH_FLOW";

export type PeriodAlignmentMode =
  | "LATEST_AVAILABLE"
  | "LATEST_COMMON_FISCAL_YEAR"
  | "SELECTED_FISCAL_PERIOD"
  | "QUALIFIED_TTM";

export type MetricObservationStatus =
  | "AVAILABLE"
  | "MISSING"
  | "NOT_MEANINGFUL"
  | "INCOMPATIBLE"
  | "STALE"
  | "NOT_APPLICABLE"
  | "NOT_ENTITLED"
  | "SOURCE_ERROR";

export type OutlierPolicy = "ALL_VALID_VALUES" | "EXCLUDE_SELECTED_OUTLIERS";

export type SubjectInclusionPolicy = "PEERS_ONLY_EXCLUDE_SUBJECT" | "ALL_COMPANIES_INCLUDE_SUBJECT";

export interface IndustryClassificationDTO {
  taxonomy: IndustryTaxonomy;
  sector: string;
  industry_group?: string | null;
  industry?: string | null;
  sub_industry?: string | null;
  code?: string | null;
  taxonomy_version: string;
}

export interface CompanyPeerCandidateDTO {
  candidate_company_id: string;
  ticker: string;
  display_name: string;
  relationship_type: PeerRelationshipType;
  classification: IndustryClassificationDTO;
  headquarters_country: string;
  market_cap?: number | null;
  formatted_market_cap?: string | null;
  revenue?: number | null;
  formatted_revenue?: string | null;
  relevance_score: number;
  selection_reasons: string[];
  is_competitor: boolean;
}

export interface UserPeerGroupDTO {
  id: string;
  owner_user_id: string;
  subject_company_id: string;
  name: string;
  description?: string | null;
  peer_company_ids: string[];
  created_at: string;
  updated_at: string;
  revision: number;
}

export interface ComparableObservationDTO {
  company_id: string;
  company_name: string;
  ticker: string;
  metric_id: string;
  metric_name: string;
  category: ComparisonMetricCategory;
  exact_value?: number | null;
  formatted_value: string;
  unit: string;
  currency?: string | null;
  period_id: string;
  period_end: string;
  status: MetricObservationStatus;
  is_subject: boolean;
  source_filing_ref?: string | null;
  explanation?: string | null;
}

export interface PeerBenchmarkStatisticsDTO {
  metric_id: string;
  metric_name: string;
  category: ComparisonMetricCategory;
  unit: string;
  mean?: number | null;
  median?: number | null;
  min_value?: number | null;
  max_value?: number | null;
  sample_count: number;
  total_count: number;
  coverage_ratio: number;
  subject_value?: number | null;
  subject_diff_vs_median_pct?: number | null;
  subject_diff_vs_median_pp?: number | null;
  subject_percentile?: number | null;
  outliers_detected: string[];
}

export interface HistoricalDataPointDTO {
  period_id: string;
  period_end: string;
  fiscal_year: number;
  fiscal_quarter?: string | null;
  value?: number | null;
  formatted_value: string;
}

export interface HistoricalPeerTrendSeriesDTO {
  metric_id: string;
  metric_name: string;
  company_id: string;
  company_name: string;
  ticker: string;
  is_subject: boolean;
  points: HistoricalDataPointDTO[];
}

export interface PeerCompanySummaryDTO {
  company_id: string;
  ticker: string;
  display_name: string;
  relationship_type: PeerRelationshipType;
  sector: string;
  industry: string;
  country: string;
  is_subject: boolean;
}

export interface PeerMetricDefinitionDTO {
  metric_id: string;
  name: string;
  category: ComparisonMetricCategory;
  unit: string;
  formula_display: string;
  description: string;
}

export interface PeersOverviewResponseDTO {
  subject_company_id: string;
  subject_company_name: string;
  classification: IndustryClassificationDTO;
  default_peer_group?: UserPeerGroupDTO | null;
  total_candidates: number;
  available_metrics_count: number;
  key_highlights: Record<string, string>;
}

export interface CandidatesResponseDTO {
  subject_company_id: string;
  total_candidates: number;
  items: CompanyPeerCandidateDTO[];
}

export interface MetricCatalogResponseDTO {
  total_metrics: number;
  items: PeerMetricDefinitionDTO[];
}

export interface PeerComparisonRequestDTO {
  peer_group_id?: string | null;
  peer_company_ids?: string[] | null;
  metric_ids?: string[] | null;
  period_alignment_mode?: PeriodAlignmentMode;
  fiscal_period?: string | null;
  outlier_policy?: OutlierPolicy;
  subject_inclusion_policy?: SubjectInclusionPolicy;
}

export interface PeerComparisonResponseDTO {
  subject_company_id: string;
  companies: PeerCompanySummaryDTO[];
  observations: Record<string, Record<string, ComparableObservationDTO>>;
  statistics: Record<string, PeerBenchmarkStatisticsDTO>;
}

export interface HistoricalComparisonRequestDTO {
  peer_company_ids?: string[] | null;
  metric_ids?: string[] | null;
  max_periods?: number;
}

export interface HistoricalComparisonResponseDTO {
  subject_company_id: string;
  series: HistoricalPeerTrendSeriesDTO[];
}

export interface CreatePeerGroupRequestDTO {
  name: string;
  description?: string | null;
  peer_company_ids: string[];
}

export interface UpdatePeerGroupRequestDTO {
  name?: string | null;
  description?: string | null;
  peer_company_ids?: string[] | null;
  expected_revision?: number | null;
}

export interface PeerMethodologyResponseDTO {
  methodology_version: string;
  taxonomy_hierarchy: string[];
  supported_period_alignment_modes: string[];
  statistical_formulas: Record<string, string>;
  outlier_methodology: string;
  non_meaningful_policies: Record<string, string>;
  entitlement_rules: string[];
  disclaimers: string[];
}
