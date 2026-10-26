/**
 * TypeScript type definitions for Institutional Macroeconomic Comparisons & Benchmarking (Stage 93).
 */

export type ComparisonMetricKind =
  | "gdp_nominal_usd"
  | "gdp_real_growth_yoy"
  | "gdp_per_capita_usd"
  | "gdp_ppp_intl_dollars"
  | "gdp_ppp_per_capita_intl"
  | "cpi_headline_yoy"
  | "cpi_core_yoy"
  | "unemployment_rate"
  | "labor_participation_rate"
  | "central_bank_policy_rate"
  | "government_debt_to_gdp"
  | "fiscal_balance_to_gdp"
  | "trade_balance_to_gdp"
  | "current_account_to_gdp"
  | "foreign_exchange_reserves_usd"
  | "population_millions";

export type CompatibilityStatus =
  | "directly_comparable"
  | "comparable_with_qualification"
  | "transformable"
  | "incompatible"
  | "insufficient_metadata";

export type GeographicCohortKind =
  | "G7"
  | "G20"
  | "BRICS"
  | "OECD"
  | "EU_EURO_AREA"
  | "CUSTOM_SELECTION";

export type PeriodAlignmentPolicy =
  | "exact_period"
  | "latest_common_period"
  | "latest_per_country";

export type RankingDirection = "ascending" | "descending";

export type TieBreakerPolicy = "standard_competition" | "dense_rank";

export type WeightingPolicy =
  | "equal_weight"
  | "population_weighted"
  | "gdp_weighted";

export type CorrelationMethod = "pearson" | "spearman";

export type VintagePolicy = "latest_revised" | "as_known_at";

export interface ComparableIndicatorDTO {
  metric_kind: ComparisonMetricKind;
  name: string;
  category: string;
  default_unit: string;
  description: string;
  higher_is_better: boolean | null;
  methodology_notes: string;
}

export interface GeographicCohortDTO {
  cohort_id: string;
  name: string;
  cohort_kind: GeographicCohortKind;
  member_geography_ids: string[];
  description: string;
}

export interface CountryMetricObservationDTO {
  geography_id: string;
  country_name: string;
  iso_code: string;
  metric_kind: ComparisonMetricKind;
  reference_period: string;
  raw_value: number;
  formatted_value: string;
  unit: string;
  source_agency: string;
  source_series_id: string;
  vintage_date?: string | null;
  is_preliminary: boolean;
  methodology_qualifications: string[];
}

export interface ComparisonEligibilityRecordDTO {
  geography_id: string;
  metric_kind: ComparisonMetricKind;
  status: CompatibilityStatus;
  is_eligible: boolean;
  reasons: string[];
  caveats: string[];
}

export interface MatrixCellDTO {
  geography_id: string;
  country_name: string;
  iso_code: string;
  metric_kind: ComparisonMetricKind;
  raw_value?: number | null;
  formatted_value: string;
  unit: string;
  reference_period: string;
  status: CompatibilityStatus;
  source_agency: string;
  source_series_id?: string;
  caveats: string[];
}

export interface ComparisonMatrixRequestDTO {
  geography_ids?: string[];
  metric_kinds?: ComparisonMetricKind[];
  period_policy?: PeriodAlignmentPolicy;
  target_period?: string | null;
  vintage_policy?: VintagePolicy;
}

export interface ComparisonMatrixResponseDTO {
  geography_ids: string[];
  metric_kinds: ComparisonMetricKind[];
  period_policy: PeriodAlignmentPolicy;
  cells: MatrixCellDTO[];
  eligibility: ComparisonEligibilityRecordDTO[];
  total_countries: number;
  generated_at: string;
}

export interface CountryRankingRowDTO {
  rank: number;
  geography_id: string;
  country_name: string;
  iso_code: string;
  metric_kind: ComparisonMetricKind;
  raw_value: number;
  formatted_value: string;
  unit: string;
  reference_period: string;
  is_tied: boolean;
}

export interface EconomicRankingsRequestDTO {
  metric_kind: ComparisonMetricKind;
  geography_ids?: string[] | null;
  cohort_id?: string | null;
  direction?: RankingDirection;
  tie_policy?: TieBreakerPolicy;
  period?: string | null;
}

export interface EconomicRankingsResponseDTO {
  metric_kind: ComparisonMetricKind;
  direction: RankingDirection;
  reference_period: string;
  total_eligible: number;
  total_excluded: number;
  rankings: CountryRankingRowDTO[];
  notes: string[];
}

export interface DistributionSummaryDTO {
  metric_kind: ComparisonMetricKind;
  reference_period: string;
  sample_size: number;
  total_eligible_geographies: number;
  mean: number;
  median: number;
  minimum: number;
  maximum: number;
  q1: number;
  q3: number;
  standard_deviation: number;
  weighting_policy: WeightingPolicy;
  unit: string;
  excluded_geography_ids: string[];
}

export interface DistributionStatisticsRequestDTO {
  metric_kind: ComparisonMetricKind;
  geography_ids?: string[] | null;
  cohort_id?: string | null;
  weighting_policy?: WeightingPolicy;
  period?: string | null;
}

export interface HistoricalTrendPointDTO {
  geography_id: string;
  country_name: string;
  reference_period: string;
  raw_value: number;
  indexed_value?: number | null;
}

export interface HistoricalTrendsRequestDTO {
  metric_kind: ComparisonMetricKind;
  geography_ids: string[];
  start_period?: string | null;
  end_period?: string | null;
  base_period?: string | null;
}

export interface HistoricalTrendsResponseDTO {
  metric_kind: ComparisonMetricKind;
  geography_ids: string[];
  base_period?: string | null;
  points: HistoricalTrendPointDTO[];
  common_periods: string[];
}

export interface DivergencePointDTO {
  reference_period: string;
  country_a_value: number;
  country_b_value: number;
  differential_value: number;
  unit: string;
  ratio?: number | null;
}

export interface DivergenceAnalysisRequestDTO {
  metric_kind: ComparisonMetricKind;
  geography_a_id: string;
  geography_b_id: string;
  start_period?: string | null;
  end_period?: string | null;
}

export interface DivergenceAnalysisResponseDTO {
  metric_kind: ComparisonMetricKind;
  geography_a_id: string;
  country_a_name: string;
  geography_b_id: string;
  country_b_name: string;
  points: DivergencePointDTO[];
  latest_differential: number;
  unit: string;
}

export interface CorrelationResultDTO {
  metric_a: ComparisonMetricKind;
  geography_a_id: string;
  country_a_name: string;
  metric_b: ComparisonMetricKind;
  geography_b_id: string;
  country_b_name: string;
  method: CorrelationMethod;
  sample_size: number;
  coefficient: number;
  is_valid: boolean;
  warnings: string[];
}

export interface CorrelationAnalysisRequestDTO {
  series_pairs: Array<{
    geo_a: string;
    metric_a: string;
    geo_b: string;
    metric_b: string;
  }>;
  method?: CorrelationMethod;
}

export interface CorrelationAnalysisResponseDTO {
  results: CorrelationResultDTO[];
}

export interface MacroCoverageSummaryDTO {
  supported_geographies: string[];
  supported_metrics: string[];
  cohorts: string[];
  total_observations_count: number;
  harmonized_sources: string[];
  methodology_qualifications: string[];
}
