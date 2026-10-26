/**
 * Canonical TypeScript Domain Types for ATLAS Economics V1 (Stage 89).
 */

export type IndicatorCategory =
  | "NATIONAL_ACCOUNTS"
  | "INFLATION"
  | "LABOR_MARKET"
  | "INTEREST_RATES"
  | "MONETARY"
  | "INDUSTRIAL_ACTIVITY"
  | "CONSUMPTION"
  | "FISCAL"
  | "EXTERNAL_SECTOR"
  | "HOUSING"
  | "BUSINESS_SURVEYS"
  | "OTHER";

export type StatisticalUnit =
  | "PERCENT"
  | "PERCENTAGE_POINTS"
  | "BASIS_POINTS"
  | "INDEX_POINTS"
  | "LOCAL_CURRENCY"
  | "USD"
  | "LOCAL_CURRENCY_BILLIONS"
  | "CURRENCY_USD_BILLIONS"
  | "PERSONS"
  | "THOUSANDS_OF_PERSONS"
  | "MILLIONS_OF_PERSONS"
  | "RATIO"
  | "OTHER_SOURCE_DEFINED";

export type ReportingFrequency =
  | "DAILY"
  | "WEEKLY"
  | "MONTHLY"
  | "QUARTERLY"
  | "ANNUAL"
  | "IRREGULAR";

export type SeasonalAdjustmentKind =
  | "SEASONALLY_ADJUSTED"
  | "NOT_SEASONALLY_ADJUSTED"
  | "CALENDAR_ADJUSTED"
  | "OTHER_ADJUSTED";

export type PriceBasisKind =
  | "CURRENT_PRICES"
  | "CONSTANT_PRICES"
  | "CHAIN_VOLUME"
  | "NOT_APPLICABLE";

export type ObservationStatus =
  | "OBSERVED"
  | "PRELIMINARY"
  | "REVISED"
  | "FINAL"
  | "ESTIMATED"
  | "FORECAST"
  | "MISSING";

export type TransformationType =
  | "SOURCE_REPORTED"
  | "LEVEL"
  | "ABSOLUTE_CHANGE"
  | "PERCENT_CHANGE"
  | "YEAR_OVER_YEAR"
  | "MONTH_OVER_MONTH"
  | "QUARTER_OVER_QUARTER"
  | "ANNUALIZED_QUARTERLY_GROWTH"
  | "PERCENTAGE_POINT_CHANGE"
  | "BASIS_POINT_CHANGE";

export type GeographicScopeKind =
  | "COUNTRY"
  | "ECONOMIC_AREA"
  | "REGION"
  | "GLOBAL_AGGREGATE";

export type DateRangePreset = "1Y" | "3Y" | "5Y" | "10Y" | "MAX";

export interface EconomicGeographyDTO {
  geography_id: string;
  iso_code: string;
  name: string;
  scope_kind: GeographicScopeKind;
  currency_code: string;
  central_bank_name: string;
  statistical_agency: string;
}

export interface EconomicIndicatorDTO {
  indicator_id: string;
  canonical_code: string;
  display_name: string;
  description: string;
  category: IndicatorCategory;
  default_unit: StatisticalUnit;
  expected_frequency: ReportingFrequency;
  seasonal_adjustment_policy: SeasonalAdjustmentKind;
  price_basis: PriceBasisKind;
  methodology_version: string;
  supported_units: StatisticalUnit[];
  supported_frequencies: ReportingFrequency[];
}

export interface EconomicSeriesDTO {
  series_id: string;
  canonical_indicator_id: string;
  geography_id: string;
  source_provider_id: string;
  source_series_code: string;
  series_name: string;
  source_definition: string;
  unit: StatisticalUnit;
  frequency: ReportingFrequency;
  seasonal_adjustment: SeasonalAdjustmentKind;
  price_basis: PriceBasisKind;
  index_base?: string | null;
  earliest_period?: string | null;
  latest_period?: string | null;
  observation_count: number;
  source_url?: string | null;
  revision_capability: boolean;
  licensing_policy: string;
}

export interface EconomicObservationDTO {
  observation_id: string;
  series_id: string;
  reference_period: string;
  period_start?: string | null;
  period_end?: string | null;
  value: number;
  unit: StatisticalUnit;
  frequency: ReportingFrequency;
  seasonal_adjustment: SeasonalAdjustmentKind;
  price_basis: PriceBasisKind;
  status: ObservationStatus;
  published_at?: string | null;
  available_at?: string | null;
  source_revision?: string | null;
  vintage_id?: string | null;
  is_transformed: boolean;
  transformation_applied?: TransformationType | null;
}

export interface EconomicVintageDTO {
  vintage_id: string;
  series_id: string;
  reference_period: string;
  vintage_sequence: number;
  estimate_label: string;
  value: number;
  published_at: string;
  source_revision: string;
  status: ObservationStatus;
}

export interface TransformationDefinitionDTO {
  transformation_type: TransformationType;
  display_name: string;
  description: string;
  output_unit_rule: string;
}

export interface MajorEconomyMacroSummaryDTO {
  geography: EconomicGeographyDTO;
  gdp_growth_qoq?: EconomicObservationDTO | null;
  gdp_growth_series_id?: string | null;
  cpi_inflation_yoy?: EconomicObservationDTO | null;
  cpi_series_id?: string | null;
  unemployment_rate?: EconomicObservationDTO | null;
  unemployment_series_id?: string | null;
  policy_rate?: EconomicObservationDTO | null;
  policy_rate_series_id?: string | null;
  data_freshness_status: string;
  reporting_sources: string[];
}

export interface GlobalMacroOverviewResponseDTO {
  as_of_date: string;
  global_aggregates_note: string;
  covered_economies_count: number;
  major_economies: MajorEconomyMacroSummaryDTO[];
  headline_indicators_count: number;
  active_providers: string[];
}

export interface EconomicSeriesObservationsResponseDTO {
  series: EconomicSeriesDTO;
  geography: EconomicGeographyDTO;
  indicator: EconomicIndicatorDTO;
  transformation_applied: TransformationType;
  effective_unit: StatisticalUnit;
  observations_count: number;
  observations: EconomicObservationDTO[];
}

export interface EconomicCoverageResponseDTO {
  total_indicators: number;
  total_series: number;
  total_observations: number;
  supported_geographies: EconomicGeographyDTO[];
  categories: IndicatorCategory[];
  providers: string[];
  revision_support: boolean;
  point_in_time_support: boolean;
}
