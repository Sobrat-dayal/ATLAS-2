/**
 * ATLAS Portfolios V1 — Exposure & Allocation TypeScript Types (Stage 112).
 */

export type ExposureBasis = 'DIRECT' | 'LOOK_THROUGH' | 'GROSS' | 'NET' | 'NET_ASSET_VALUE' | 'LONG_ONLY' | 'SHORT_ONLY';

export type ExposureDimension =
  | 'ASSET_CLASS'
  | 'SECTOR'
  | 'INDUSTRY'
  | 'COUNTRY'
  | 'REGION'
  | 'CURRENCY'
  | 'SECURITY'
  | 'ISSUER';

export type AssetClass =
  | 'EQUITY'
  | 'FUND'
  | 'FIXED_INCOME'
  | 'CASH'
  | 'CASH_EQUIVALENT'
  | 'COMMODITY'
  | 'DIGITAL_ASSET'
  | 'DERIVATIVE'
  | 'OTHER'
  | 'UNKNOWN';

export type GeographyPolicy =
  | 'ISSUER_DOMICILE'
  | 'HEADQUARTERS'
  | 'LISTING_VENUE'
  | 'REVENUE_GEOGRAPHY';

export type LookThroughStatus =
  | 'FULL_LOOK_THROUGH'
  | 'PARTIAL_LOOK_THROUGH'
  | 'UNSUPPORTED'
  | 'DATA_UNAVAILABLE'
  | 'DEPTH_EXCEEDED';

export type ExposureDataCompleteness =
  | 'COMPLETE'
  | 'COMPLETE_WITH_WARNINGS'
  | 'PARTIAL_CLASSIFICATION'
  | 'PARTIAL_VALUATION'
  | 'PARTIAL_FX'
  | 'EMPTY';

export interface ExposureCategoryResponse {
  category_id: string;
  category_label: string;
  base_value: string;
  weight: string;
  percentage: string;
  position_count: number;
  direct_value: string;
  look_through_value: string;
  is_residual: boolean;
  is_unclassified: boolean;
  parent_category_id?: string | null;
  subcategories: ExposureCategoryResponse[];
}

export interface ExposureDimensionResponse {
  dimension: ExposureDimension;
  total_base_value: string;
  total_weight: string;
  reconciled: boolean;
  reconciliation_discrepancy: string;
  categories: ExposureCategoryResponse[];
}

export interface SecurityWeightResponse {
  instrument_id: string;
  symbol: string;
  name: string;
  asset_class: string;
  base_value: string;
  weight: string;
  percentage: string;
  direct_weight: string;
  look_through_weight: string;
  effective_shares: string;
  rank: number;
}

export interface IssuerWeightResponse {
  issuer_id: string;
  issuer_name: string;
  country_code: string;
  base_value: string;
  weight: string;
  percentage: string;
  constituent_instruments: string[];
  rank: number;
}

export interface ConcentrationSummaryResponse {
  top1_weight: string;
  top3_weight: string;
  top5_weight: string;
  top10_weight: string;
  top20_weight: string;
  herfindahl_index: string;
  herfindahl_index_normalized: string;
  effective_number_of_holdings: string;
  total_positions: number;
  direct_holdings_count: number;
  look_through_holdings_count: number;
}

export interface FundConstituentResponse {
  parent_fund_id: string;
  constituent_instrument_id: string;
  constituent_symbol: string;
  constituent_name: string;
  constituent_asset_class: string;
  constituent_sector: string;
  constituent_country: string;
  constituent_currency: string;
  constituent_weight_in_fund: string;
  effective_base_value: string;
  effective_portfolio_weight: string;
  is_residual: boolean;
}

export interface FundLookThroughResponse {
  fund_instrument_id: string;
  fund_symbol: string;
  fund_name: string;
  fund_base_value: string;
  fund_weight_in_portfolio: string;
  as_of_date: string;
  status: LookThroughStatus;
  coverage_ratio: string;
  residual_weight: string;
  residual_base_value: string;
  constituents: FundConstituentResponse[];
}

export interface CrossFundOverlapResponse {
  constituent_symbol: string;
  constituent_name: string;
  total_effective_weight: string;
  total_effective_value: string;
  funds_involved: string[];
  weights_by_fund: Record<string, string>;
}

export interface HistoricalAllocationPointResponse {
  as_of_date: string;
  dimension: ExposureDimension;
  category_id: string;
  category_label: string;
  weight: string;
  base_value: string;
  base_currency: string;
}

export interface AllocationChangeResponse {
  dimension: ExposureDimension;
  category_id: string;
  category_label: string;
  start_date: string;
  end_date: string;
  start_weight: string;
  end_weight: string;
  weight_change_pct: string;
  weight_change_bps: number;
  start_value: string;
  end_value: string;
  value_change: string;
}

export interface ExposureDataQualityResponse {
  completeness: ExposureDataCompleteness;
  total_positions: number;
  classified_positions: number;
  unclassified_positions: number;
  classification_coverage_ratio: string;
  valuation_coverage_ratio: string;
  fx_coverage_ratio: string;
  warnings: string[];
  errors: string[];
  reconciled: boolean;
  reconciliation_discrepancy: string;
}

export interface PortfolioExposureRunResponse {
  run_id: string;
  portfolio_id: string;
  account_ids: string[];
  as_of_date: string;
  calculated_at: string;
  base_currency: string;
  exposure_basis: ExposureBasis;
  geography_policy: GeographyPolicy;
  look_through_applied: boolean;
  total_nav: string;
  gross_exposure: string;
  cash_value: string;
  cash_weight: string;
  input_hash: string;
  calculation_version: string;
  reconciled: boolean;
  data_quality: ExposureDataQualityResponse;
  asset_classes: ExposureDimensionResponse;
  sectors: ExposureDimensionResponse;
  industries: ExposureDimensionResponse;
  countries: ExposureDimensionResponse;
  currencies: ExposureDimensionResponse;
  concentration: ConcentrationSummaryResponse;
  security_weights: SecurityWeightResponse[];
  issuer_weights: IssuerWeightResponse[];
  funds: FundLookThroughResponse[];
  cross_fund_overlap: CrossFundOverlapResponse[];
}

export interface CalculateExposureRequest {
  as_of_date?: string | null;
  account_ids?: string[] | null;
  exposure_basis?: ExposureBasis;
  geography_policy?: GeographyPolicy;
  enable_look_through?: boolean;
  max_look_through_depth?: number;
  force_recalculate?: boolean;
}
