/**
 * TypeScript Types & DTO Interfaces for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61).
 */

export type BondType =
  | "sovereign"
  | "corporate"
  | "municipal"
  | "agency"
  | "supranational"
  | "treasury_bill";

export type IssuerCategory =
  | "sovereign"
  | "corporate"
  | "municipal"
  | "agency"
  | "supranational";

export type CouponType =
  | "fixed"
  | "floating"
  | "zero_coupon"
  | "step_up"
  | "inflation_linked"
  | "other";

export type CouponFrequency =
  | "annual"
  | "semiannual"
  | "quarterly"
  | "monthly"
  | "zero";

export type PriceBasis = "clean" | "dirty" | "unknown";

export type PriceQuoteUnit =
  | "percentage_of_par"
  | "price_per_100_face"
  | "absolute_amount";

export type PriceKind =
  | "trade_price"
  | "indicative_quote"
  | "evaluated_price"
  | "reference_price"
  | "unknown";

export type YieldType =
  | "ytm"
  | "ytc"
  | "ytw"
  | "current_yield"
  | "discount_yield"
  | "unknown";

export type DayCountConvention =
  | "ACT/ACT ICMA"
  | "30/360"
  | "ACT/360"
  | "ACT/365"
  | "UNKNOWN";

export type Seniority =
  | "senior_secured"
  | "senior_unsecured"
  | "subordinated"
  | "junior"
  | "unknown";

export type MaturityBucket =
  | "under_1_year"
  | "1_to_3_years"
  | "3_to_5_years"
  | "5_to_10_years"
  | "over_10_years"
  | "perpetual";

export interface BondIssuerSummary {
  issuer_entity_id: string;
  name: string;
  issuer_category: IssuerCategory;
  country_code: string;
  jurisdiction: string;
}

export interface BondContractTermsView {
  issue_date: string;
  dated_date?: string | null;
  maturity_date?: string | null;
  is_perpetual: boolean;
  time_to_maturity_years?: string | number | null;
  maturity_bucket: MaturityBucket;
  coupon_type: CouponType;
  coupon_rate?: string | number | null;
  coupon_frequency: CouponFrequency;
  day_count_convention: DayCountConvention;
  face_value: string | number;
  face_value_convention: string;
  seniority: Seniority;
  is_callable: boolean;
  is_putable: boolean;
  reference_index?: string | null;
  floating_margin_bps?: string | number | null;
}

export interface BondPriceObservationView {
  clean_price?: string | number | null;
  dirty_price?: string | number | null;
  accrued_interest?: string | number | null;
  price_basis: PriceBasis;
  quote_unit: PriceQuoteUnit;
  price_kind: PriceKind;
  currency: string;
  bid?: string | number | null;
  ask?: string | number | null;
  spread?: string | number | null;
  price_change_24h?: string | number | null;
  price_change_24h_percent?: string | number | null;
  source_timestamp: string;
  received_at: string;
  valuation_date?: string | null;
  freshness_status: string;
  delay_status: string;
  provider: string;
}

export interface BondYieldObservationView {
  yield_value?: string | number | null;
  yield_type: YieldType;
  yield_unit: string;
  yield_change_bps_24h?: string | number | null;
  as_of: string;
  source: string;
  methodology?: string | null;
}

export interface BondDirectoryItem {
  instrument_entity_id: string;
  symbol: string;
  name: string;
  isin?: string | null;
  cusip?: string | null;
  issuer: BondIssuerSummary;
  bond_type: BondType;
  currency: string;
  terms: BondContractTermsView;
  price: BondPriceObservationView;
  yield_obs: BondYieldObservationView;
  freshness_status: string;
  provider: string;
  data_status: string;
}

export interface BondCoverageSummary {
  total_bonds: number;
  total_issuers: number;
  sovereign_bonds: number;
  corporate_bonds: number;
  other_bonds: number;
  bonds_with_prices: number;
  bonds_with_yields: number;
  bonds_with_accrued_interest: number;
  currencies: string[];
}

export interface BondFilterOptionsResponse {
  issuer_categories: string[];
  bond_types: string[];
  currencies: string[];
  coupon_types: string[];
  maturity_buckets: string[];
  issuers: Array<{
    issuer_entity_id: string;
    name: string;
    category: string;
    country: string;
  }>;
  coverage: BondCoverageSummary;
}

export interface BondDirectoryResponse {
  schema_version: string;
  scope: string;
  items: BondDirectoryItem[];
  total: number;
  limit: number;
  next_cursor?: string | null;
  has_more: boolean;
  coverage: BondCoverageSummary;
}

export interface BondOverviewResponse {
  schema_version: string;
  instrument_entity_id: string;
  symbol: string;
  name: string;
  isin?: string | null;
  cusip?: string | null;
  issuer: BondIssuerSummary;
  bond_type: BondType;
  currency: string;
  terms: BondContractTermsView;
  price: BondPriceObservationView;
  yield_obs: BondYieldObservationView;
  provenance: Record<string, string>;
  availability: Record<string, boolean>;
  non_executable_disclaimer: string;
}

export interface BondDirectoryFilters {
  query?: string;
  issuer_type?: string;
  issuer_entity_id?: string;
  bond_type?: string;
  currency?: string;
  coupon_type?: string;
  maturity_bucket?: string;
  limit?: number;
  cursor?: string;
}
