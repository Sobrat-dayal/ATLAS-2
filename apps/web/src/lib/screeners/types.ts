/**
 * TypeScript types and DTO contracts for Financial Screeners V1 (Stage 94).
 */

export type UniverseKind =
  | "common_equity"
  | "all_equity"
  | "global_mega_cap"
  | "us_large_cap"
  | "tech_sector"
  | "dividend_stocks"
  | "delisted_equity";

export type SecurityType =
  | "common_stock"
  | "preferred_stock"
  | "depositary_receipt"
  | "etf"
  | "fund";

export type ListingStatus = "active" | "suspended" | "delisted" | "inactive";

export type FilterCategory =
  | "universe"
  | "listing"
  | "geography"
  | "industry"
  | "market_data"
  | "fundamentals"
  | "valuation"
  | "profitability"
  | "growth"
  | "cash_flow"
  | "balance_sheet"
  | "capital_efficiency"
  | "technical_trend"
  | "technical_momentum"
  | "technical_volatility"
  | "technical_volume";

export type FilterOperator =
  | "eq"
  | "ne"
  | "gt"
  | "gte"
  | "lt"
  | "lte"
  | "between"
  | "in";

export type ValueType =
  | "numeric"
  | "integer"
  | "enum"
  | "boolean"
  | "currency"
  | "percentage";

export type UnitKind =
  | "monetary"
  | "percent"
  | "multiple"
  | "shares"
  | "currency_per_share"
  | "dimensionless";

export type EditorType =
  | "decimal_input"
  | "monetary_input"
  | "percent_input"
  | "multiple_input"
  | "number_range"
  | "enum_select"
  | "enum_multi_select"
  | "boolean_select"
  | "date_input";

export type SortDirection = "asc" | "desc";
export type SortNullOrder = "nulls_last" | "nulls_first";

export type RankingMode = "single_factor" | "multi_factor_composite";
export type RankingDirection = "higher_value_first" | "lower_value_first";
export type RankingMethod = "dense_rank" | "competition_rank";
export type RankingTransformation = "raw_rank" | "percentile" | "z_score";

export type ExportFormat = "csv" | "xlsx" | "json";
export type ExportScope = "current_page" | "all_matching_results";
export type ExportJobStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "cancel_requested"
  | "cancelled"
  | "expired";

export type SavedScreenerStatus = "active" | "archived" | "deleted";

export interface RankingFactorWeight {
  factor_id: string;
  direction: RankingDirection;
  transformation: RankingTransformation;
  weight: number;
}

export interface ScreenerRankingSpec {
  mode: RankingMode;
  cohort_policy: string;
  factors: RankingFactorWeight[];
  method: RankingMethod;
  missing_value_policy?: string;
  minimum_coverage?: number;
  methodology_version?: string;
}

export interface ScreenerUniverseDefinition {
  universe_id: string;
  name: string;
  description: string;
  asset_class: string;
  eligible_security_types: SecurityType[];
  eligible_listing_statuses: ListingStatus[];
  geographic_scope?: string[] | null;
  exchange_scope?: string[] | null;
  is_default: boolean;
}

export interface ScreenerFilterDefinition {
  filter_id: string;
  display_name: string;
  description: string;
  category: FilterCategory;
  value_type: ValueType;
  unit_kind: UnitKind;
  allowed_operators: FilterOperator[];
  eligible_security_types?: SecurityType[];
  eligible_industries?: string[];
  default_operator: FilterOperator;
  is_range_supported: boolean;
  min_value?: number | null;
  max_value?: number | null;
  editor_type?: EditorType;
  currency_options?: string[];
  magnitude_options?: string[];
  aliases?: string[];
  methodology_reference?: string;
  decimal_precision?: number;
  entitlement_state?: string;
  source_coverage_summary?: string;
  indicator_type?: string | null;
  default_parameters?: Record<string, string | number | boolean> | null;
  allowed_parameters?: Record<string, Array<string | number | boolean>> | null;
  minimum_lookback?: number | null;
  output_components?: string[] | null;
  calculation_version?: string;
}

export interface ScreenerColumnDefinition {
  column_id: string;
  display_label: string;
  category: FilterCategory;
  data_type: ValueType;
  unit_kind: UnitKind;
  sortable: boolean;
  default_visible: boolean;
  description: string;
  alignment: "left" | "right";
}

export interface FilterCriterion {
  condition_id?: string;
  filter_id: string;
  operator: FilterOperator;
  value: string | number | boolean;
  secondary_value?: string | number | null;
  currency?: string | null;
  unit?: string | null;
  parameters?: Record<string, string | number | boolean> | null;
  period_policy?: string | null;
}


export interface SortCriterion {
  field_id: string;
  direction: SortDirection;
  null_order?: SortNullOrder;
}

export interface UniverseSelection {
  universe_id: string;
  security_types?: string[] | null;
  listing_statuses?: string[] | null;
  exchange_mics?: string[] | null;
  issuer_country_codes?: string[] | null;
  listing_country_codes?: string[] | null;
  sectors?: string[] | null;
  industries?: string[] | null;
}

export interface ScreenerRunRequest {
  universe: UniverseSelection;
  filters: FilterCriterion[];
  sort: SortCriterion[];
  multi_sort?: SortCriterion[] | null;
  ranking?: ScreenerRankingSpec | null;
  columns?: string[] | null;
  page?: number;
  page_size?: number;
  cursor?: string | null;
  period_policy?: string;
  currency_policy?: string;
}

export interface ScreenerMetricCell {
  metric_id: string;
  raw_value?: number | string | null;
  display_value: string;
  unit?: string | null;
  currency?: string | null;
  status: "available" | "missing" | "not_meaningful" | "restricted" | string;
  observation_period?: string | null;
  freshness?: string | null;
  as_of?: string | null;
  provider?: string | null;
}

export interface ScreenerResultRow {
  instrument_entity_id: string;
  listing_id: string;
  issuer_company_entity_id: string;
  canonical_security_name: string;
  ticker: string;
  exchange_mic: string;
  exchange_name: string;
  listing_country_code: string;
  issuer_country_code: string;
  security_type: string;
  share_class_name?: string | null;
  listing_status: string;
  currency: string;
  sector?: string | null;
  industry?: string | null;
  metrics: Record<string, ScreenerMetricCell>;
  rank?: number | null;
  composite_score?: number | null;
  percentile?: number | null;
  z_score?: number | null;
}

export interface ScreenerRunResponse {
  query_id: string;
  universe_id: string;
  evaluated_as_of: string;
  total_matching_count: number;
  count_exactness: string;
  page: number;
  page_size: number;
  total_pages: number;
  has_next_page: boolean;
  has_previous_page: boolean;
  next_cursor?: string | null;
  rows: ScreenerResultRow[];
  applied_filters_count: number;
  source_coverage: Record<string, number>;
  execution_duration_ms: number;
  warnings: string[];
  ranking_evaluation_id?: string | null;
  ranking_summary?: {
    mode: string;
    method: string;
    cohort_policy?: string;
    eligible_count: number;
    excluded_count: number;
    methodology_version: string;
  } | null;
}

export interface SavedScreener {
  saved_screen_id: string;
  owner_user_id: string;
  name: string;
  description?: string | null;
  query_schema_version: string;
  universe: UniverseSelection;
  filters: FilterCriterion[];
  columns: string[];
  sort: SortCriterion[];
  ranking?: ScreenerRankingSpec | null;
  period_policy: string;
  currency_policy: string;
  revision: number;
  status: SavedScreenerStatus;
  created_at: string;
  updated_at: string;
  last_executed_at?: string | null;
}

export interface SavedScreenerCreateRequest {
  name: string;
  description?: string | null;
  universe: UniverseSelection;
  filters: FilterCriterion[];
  columns?: string[];
  sort: SortCriterion[];
  ranking?: ScreenerRankingSpec | null;
  period_policy?: string;
  currency_policy?: string;
  idempotency_key?: string | null;
}

export interface SavedScreenerUpdateRequest {
  name?: string;
  description?: string | null;
  universe?: UniverseSelection;
  filters?: FilterCriterion[];
  columns?: string[];
  sort?: SortCriterion[];
  ranking?: ScreenerRankingSpec | null;
  period_policy?: string;
  currency_policy?: string;
  expected_revision: number;
}

export interface SavedScreenerListResponse {
  total: number;
  page: number;
  page_size: number;
  items: SavedScreener[];
}

export interface ScreenerExportRequest {
  query: ScreenerRunRequest;
  saved_screen_id?: string | null;
  format: ExportFormat;
  scope: ExportScope;
  selected_columns?: string[] | null;
  include_metadata?: boolean;
  idempotency_key?: string | null;
}

export interface ScreenerExportJob {
  export_job_id: string;
  owner_user_id: string;
  status: ExportJobStatus;
  format: ExportFormat;
  scope: ExportScope;
  row_count: number;
  file_size_bytes?: number | null;
  download_url?: string | null;
  error_message?: string | null;
  created_at: string;
  completed_at?: string | null;
  expires_at?: string | null;
}

export interface ScreenerExportListResponse {
  total: number;
  items: ScreenerExportJob[];
}

export interface ConditionValidationIssue {
  condition_id?: string | null;
  filter_id?: string | null;
  field_path?: string | null;
  code: string;
  severity: "error" | "warning";
  message: string;
}

export interface ValidationResponse {
  valid: boolean;
  accepted_filters: FilterCriterion[];
  rejected_filters: Array<{
    filter_id: string;
    condition_id?: string;
    reason: string;
    code: string;
  }>;
  issues?: ConditionValidationIssue[];
  warnings: string[];
  contradictions_detected?: boolean;
  eligible_universe_size: number;
}

export type ConditionStatus = "valid" | "incomplete" | "invalid";

export interface VisualFilterCondition {
  conditionId: string;
  filterId: string;
  operator: FilterOperator;
  value: string;
  secondaryValue?: string | null;
  currency?: string | null;
  magnitude?: "UNITS" | "THOUSANDS" | "MILLIONS" | "BILLIONS" | "TRILLIONS";
  parameters?: Record<string, string | number | boolean> | null;
  periodPolicy?: string | null;
  status: ConditionStatus;
  validationMessage?: string | null;
  fieldErrors?: Record<string, string>;
  isDirty?: boolean;
}

export interface QueryPreviewSummary {
  universeId: string;
  universeName: string;
  conditionsCount: number;
  plainEnglishPredicates: string[];
  periodPolicy: string;
  currencyPolicy: string;
  isValid: boolean;
  contradictionsDetected: boolean;
  warnings: string[];
}


export interface ExchangeOption {
  mic: string;
  name: string;
  country_code: string;
  count: number;
}

export interface CountryOption {
  code: string;
  name: string;
  count: number;
}

export interface SectorOption {
  name: string;
  count: number;
  industries: string[];
}

export interface ScreenerCoverageResponse {
  total_instruments: number;
  active_listings: number;
  exchanges_count: number;
  countries_count: number;
  sectors_count: number;
  instruments_with_quotes: number;
  instruments_with_market_cap: number;
  instruments_with_fundamentals: number;
  instruments_with_ratios: number;
  providers_represented: string[];
  data_freshness_breakdown: Record<string, number>;
}

// =============================================================================
// Stage 98: Natural-Language Screener Translation Contracts
// =============================================================================

export type NLTranslationStatus =
  | "valid"
  | "needs_clarification"
  | "unsupported"
  | "restricted"
  | "unavailable"
  | "invalid"
  | "error";

export type NLAmbiguityCategory =
  | "metric_ambiguity"
  | "operator_ambiguity"
  | "currency_ambiguity"
  | "unit_ambiguity"
  | "period_ambiguity"
  | "geography_ambiguity"
  | "industry_ambiguity"
  | "indicator_ambiguity"
  | "ranking_ambiguity"
  | "logical_ambiguity"
  | "universe_ambiguity";

export type NLRequirementStatus =
  | "resolved"
  | "ambiguous"
  | "unsupported"
  | "restricted"
  | "dropped";

export interface NLRequirementResolution {
  requirement_id: string;
  source_text: string;
  interpreted_concept?: string | null;
  resolved_filter_id?: string | null;
  status: NLRequirementStatus;
  explanation: string;
  alternatives?: string[] | null;
}

export interface NLAmbiguityOption {
  id: string;
  label: string;
  filter_id?: string;
  operator?: string;
  value?: any;
  description?: string;
}

export interface NLAmbiguityQuestion {
  ambiguity_id: string;
  category: NLAmbiguityCategory;
  question: string;
  source_phrase: string;
  options: NLAmbiguityOption[];
}

export interface NLQueryModificationDiff {
  added_conditions: FilterCriterion[];
  updated_conditions: FilterCriterion[];
  removed_conditions: string[];
}

export interface NLTranslationProposal {
  proposal_id: string;
  status: NLTranslationStatus;
  original_text: string;
  universe: UniverseSelection;
  filters: FilterCriterion[];
  sort: SortCriterion[];
  result_limit?: number | null;
  requirements: NLRequirementResolution[];
  ambiguities: NLAmbiguityQuestion[];
  unsupported: string[];
  assumptions: string[];
  modification_diff?: NLQueryModificationDiff | null;
  ready_for_review: boolean;
  translator_version: string;
  registry_revision: string;
  coverage_count: string;
}

export interface NLTranslateRequest {
  text: string;
  universe_context?: string;
  current_filters?: FilterCriterion[];
  currency_policy?: string;
  period_policy?: string;
  locale?: string;
  mode?: "create_new_query" | "modify_current_draft" | "explain_current_query";
  request_id?: string;
}

export interface NLClarifyRequest {
  proposal_id: string;
  original_text: string;
  ambiguity_id: string;
  selected_option_id: string;
  additional_text?: string;
  current_universe?: UniverseSelection;
  current_filters?: FilterCriterion[];
}

export interface NLCapabilitiesResponse {
  supported_metrics: Array<{
    filter_id: string;
    display_name: string;
    category: string;
    unit_kind: string;
    aliases: string[];
  }>;
  supported_operators: string[];
  supported_currencies: string[];
  supported_units: string[];
  supported_indicators: Array<{
    indicator_id: string;
    display_name: string;
    category: string;
  }>;
  supported_magnitudes: string[];
  example_queries: Array<{
    title: string;
    query: string;
  }>;
}
