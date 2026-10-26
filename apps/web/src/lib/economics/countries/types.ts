/**
 * TypeScript Type Definitions for Country Economics Intelligence (Stage 90).
 */

export type CountryCategoryTab =
  | "overview"
  | "gdp"
  | "inflation"
  | "labor"
  | "industry"
  | "monetary"
  | "fiscal"
  | "external"
  | "demographics"
  | "historical";

export type GeographicScopeKind =
  | "COUNTRY"
  | "ECONOMIC_AREA"
  | "REGION"
  | "STATISTICAL_AGGREGATE";

export type PriceBasisKind =
  | "CURRENT_PRICES"
  | "CONSTANT_PRICES"
  | "CHAIN_LINKED_VOLUME"
  | "NOT_APPLICABLE";

export type SeasonalAdjustmentKind =
  | "SEASONALLY_ADJUSTED"
  | "NOT_ADJUSTED"
  | "CALENDAR_ADJUSTED"
  | "SEASONALLY_AND_CALENDAR_ADJUSTED";

export type StatisticalUnit =
  | "PERCENT"
  | "PERCENT_PER_ANNUM"
  | "PERCENT_CHANGE_YOY"
  | "PERCENT_CHANGE_MOM"
  | "PERCENT_CHANGE_QOQ"
  | "PERCENT_CHANGE_QOQ_ANNUALIZED"
  | "INDEX_POINTS"
  | "BASIS_POINTS"
  | "CURRENCY_USD_BILLIONS"
  | "CURRENCY_EUR_BILLIONS"
  | "CURRENCY_GBP_BILLIONS"
  | "CURRENCY_JPY_TRILLIONS"
  | "CURRENCY_CNY_BILLIONS"
  | "CURRENCY_INR_CRORES"
  | "LOCAL_CURRENCY_BILLIONS"
  | "THOUSANDS_OF_PERSONS"
  | "MILLIONS_OF_PERSONS";

export type GDPApproachKind = "EXPENDITURE" | "PRODUCTION" | "INCOME";

export type GovernmentAccountingScope =
  | "GENERAL_GOVERNMENT"
  | "CENTRAL_GOVERNMENT"
  | "PUBLIC_SECTOR"
  | "LOCAL_GOVERNMENT";

export type FiscalAccountingBasis = "ACCRUAL" | "CASH" | "MODIFIED_CASH";

export type TradeValuationKind = "FOB" | "CIF" | "NOT_APPLICABLE";

export interface CountryEconomicProfileDTO {
  geography_id: string;
  name: string;
  iso_code: string;
  scope_kind: GeographicScopeKind;
  currency_code: string;
  central_bank_name: string;
  statistical_agency: string;
  fiscal_year_structure: string;
  national_accounts_standard: string;
  available_categories: string[];
  supported_series_count: number;
  earliest_observation_period: string;
  latest_observation_period: string;
  notes?: string | null;
}

export interface GDPComponentItemDTO {
  component_id: string;
  name: string;
  code: string;
  value: number;
  unit: StatisticalUnit;
  share_of_gdp_pct: number;
  contribution_to_growth_pct_points?: number | null;
}

export interface CountryGDPDecompositionDTO {
  geography_id: string;
  reference_period: string;
  price_basis: PriceBasisKind;
  currency: string;
  nominal_gdp_billions: number;
  real_gdp_billions: number;
  gdp_deflator_index?: number | null;
  real_growth_qoq_ann?: number | null;
  real_growth_yoy?: number | null;
  gdp_per_capita_usd?: number | null;
  per_capita_population_period?: string | null;
  approach: GDPApproachKind;
  components: GDPComponentItemDTO[];
  total_calculated: number;
  is_strictly_additive: boolean;
  non_additive_reason?: string | null;
}

export interface CountrySectorValueAddedItemDTO {
  sector_id: string;
  name: string;
  code: string;
  value_added_billions: number;
  share_of_gva_pct: number;
  growth_yoy?: number | null;
}

export interface CountryProductionDecompositionDTO {
  geography_id: string;
  reference_period: string;
  total_gva_billions: number;
  currency: string;
  sectors: CountrySectorValueAddedItemDTO[];
  notes?: string | null;
}

export interface CountryInflationSummaryDTO {
  geography_id: string;
  reference_period: string;
  cpi_index_level: number;
  cpi_index_base: string;
  headline_yoy: number;
  headline_mom: number;
  core_yoy?: number | null;
  core_mom?: number | null;
  food_inflation_yoy?: number | null;
  energy_inflation_yoy?: number | null;
  ppi_yoy?: number | null;
  gdp_deflator_yoy?: number | null;
  seasonal_adjustment: SeasonalAdjustmentKind;
  notes?: string | null;
}

export interface CountryLaborSummaryDTO {
  geography_id: string;
  reference_period: string;
  unemployment_rate?: number | null;
  employment_level_thousands?: number | null;
  labor_force_participation_rate?: number | null;
  employment_to_population_ratio?: number | null;
  youth_unemployment_rate?: number | null;
  nominal_wage_growth_yoy?: number | null;
  real_wage_growth_yoy?: number | null;
  survey_methodology: string;
  age_scope: string;
  notes?: string | null;
}

export interface CountryIndustrySummaryDTO {
  geography_id: string;
  reference_period: string;
  industrial_production_index?: number | null;
  industrial_production_yoy?: number | null;
  manufacturing_output_yoy?: number | null;
  retail_sales_nominal_yoy?: number | null;
  retail_sales_real_yoy?: number | null;
  capacity_utilization_pct?: number | null;
  housing_starts_annualized_thousands?: number | null;
  building_permits_annualized_thousands?: number | null;
  consumer_confidence_index?: number | null;
  business_confidence_index?: number | null;
  notes?: string | null;
}

export interface CountryMonetarySummaryDTO {
  geography_id: string;
  reference_period: string;
  policy_rate?: number | null;
  policy_rate_target_range?: string | null;
  m1_growth_yoy?: number | null;
  m2_growth_yoy?: number | null;
  domestic_credit_to_private_sector_pct_gdp?: number | null;
  bank_lending_growth_yoy?: number | null;
  monetary_area_name: string;
  central_bank_name: string;
  notes?: string | null;
}

export interface CountryFiscalSummaryDTO {
  geography_id: string;
  reference_period: string;
  fiscal_year: string;
  accounting_scope: GovernmentAccountingScope;
  accounting_basis: FiscalAccountingBasis;
  total_revenue_billions?: number | null;
  tax_revenue_billions?: number | null;
  total_expenditure_billions?: number | null;
  interest_expenditure_billions?: number | null;
  fiscal_balance_billions?: number | null;
  fiscal_balance_pct_gdp?: number | null;
  primary_balance_billions?: number | null;
  primary_balance_pct_gdp?: number | null;
  gross_debt_billions?: number | null;
  gross_debt_pct_gdp?: number | null;
  net_debt_pct_gdp?: number | null;
  notes?: string | null;
}

export interface CountryExternalSummaryDTO {
  geography_id: string;
  reference_period: string;
  goods_exports_billions?: number | null;
  goods_imports_billions?: number | null;
  merchandise_trade_balance_billions?: number | null;
  services_exports_billions?: number | null;
  services_imports_billions?: number | null;
  services_trade_balance_billions?: number | null;
  total_trade_balance_billions?: number | null;
  current_account_balance_billions?: number | null;
  current_account_pct_gdp?: number | null;
  fdi_net_inflow_billions?: number | null;
  portfolio_investment_net_billions?: number | null;
  gross_external_debt_billions?: number | null;
  foreign_exchange_reserves_billions?: number | null;
  fx_reserves_currency: string;
  notes?: string | null;
}

export interface CountryDemographicsSummaryDTO {
  geography_id: string;
  reference_period: string;
  total_population_millions?: number | null;
  population_growth_rate_yoy?: number | null;
  working_age_population_pct?: number | null;
  youth_population_pct?: number | null;
  elderly_population_pct?: number | null;
  age_dependency_ratio?: number | null;
  urbanization_rate_pct?: number | null;
  notes?: string | null;
}

export interface CountryEconomicsOverviewDTO {
  profile: CountryEconomicProfileDTO;
  headline_real_gdp_growth_qoq?: number | null;
  headline_real_gdp_growth_yoy?: number | null;
  headline_gdp_period?: string | null;
  nominal_gdp_usd_billions?: number | null;
  gdp_per_capita_usd?: number | null;
  headline_cpi_inflation_yoy?: number | null;
  headline_cpi_period?: string | null;
  core_cpi_inflation_yoy?: number | null;
  unemployment_rate?: number | null;
  unemployment_period?: string | null;
  policy_interest_rate?: number | null;
  policy_rate_period?: string | null;
  general_gov_debt_pct_gdp?: number | null;
  fiscal_balance_pct_gdp?: number | null;
  current_account_pct_gdp?: number | null;
  total_population_millions?: number | null;
  fx_reserves_billions?: number | null;
  data_freshness_status: string;
}

export interface CountryCoverageResponseDTO {
  country_id: string;
  profile: CountryEconomicProfileDTO;
  has_gdp_decomposition: boolean;
  has_production_gva: boolean;
  has_inflation_components: boolean;
  has_labor_survey: boolean;
  has_industry_indicators: boolean;
  has_monetary_aggregates: boolean;
  has_fiscal_accounts: boolean;
  has_external_bop: boolean;
  has_demographics: boolean;
}
