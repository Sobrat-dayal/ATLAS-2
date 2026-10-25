/**
 * TypeScript Type Definitions for Company Financial Ratios (Stage 83).
 */

export type RatioCategory =
  | "profitability"
  | "liquidity"
  | "solvency"
  | "efficiency"
  | "cash_flow"
  | "valuation";

export type RatioStatus =
  | "AVAILABLE"
  | "UNAVAILABLE"
  | "NOT_APPLICABLE"
  | "NOT_MEANINGFUL"
  | "INSUFFICIENT_DATA"
  | "INCOMPATIBLE_INPUTS"
  | "NOT_ENTITLED";

export type RatioPeriodType = "ANNUAL" | "QUARTERLY" | "TTM";

export type UnitKind =
  | "PERCENT"
  | "MULTIPLE"
  | "DAYS"
  | "MONETARY"
  | "CURRENCY_PER_SHARE"
  | "DIMENSIONLESS";

export type DenominatorPolicy =
  | "STRICT_POSITIVE"
  | "NON_ZERO"
  | "AVERAGE_BALANCE"
  | "PERIOD_END";

export type NegativePolicy = "VALID_NEGATIVE" | "NOT_MEANINGFUL";

export interface RatioDefinitionDTO {
  id: string;
  name: string;
  description: string;
  category: RatioCategory;
  methodology_version: number;
  methodology_id: string;
  formula_display: string;
  numerator_definition: string;
  denominator_definition: string;
  required_inputs: string[];
  supported_periods: RatioPeriodType[];
  unit_kind: UnitKind;
  output_format: string;
  denominator_policy: DenominatorPolicy;
  negative_policy: NegativePolicy;
  requires_market_data: boolean;
  requires_balance_sheet_average: boolean;
  supported_industries: string[];
}

export interface RatioCatalogResponse {
  ratios: RatioDefinitionDTO[];
  total_count: number;
  categories: string[];
}

export interface RatioInputFactDTO {
  fact_key: string;
  concept_name: string;
  value?: number | string | null;
  formatted_value?: string | null;
  statement_type: string;
  period_id: string;
  is_average: boolean;
  source_revision: string;
}

export interface RatioValueDTO {
  ratio_id: string;
  name: string;
  category: RatioCategory;
  status: RatioStatus;
  exact_value?: number | string | null;
  formatted_value: string;
  unit_kind: UnitKind;
  formula_display: string;
  period_id: string;
  period_type: RatioPeriodType;
  numerator_value?: number | string | null;
  denominator_value?: number | string | null;
  explanation?: string | null;
  methodology_version: number;
  input_lineage: RatioInputFactDTO[];
  calculated_at?: string;
}

export interface CompanyRatiosResponse {
  company_id: string;
  company_name: string;
  period_id: string;
  period_type: RatioPeriodType;
  fiscal_year: number;
  reporting_currency: string;
  ratios: RatioValueDTO[];
  category_counts: Record<string, number>;
  available_count: number;
  total_count: number;
}

export interface RatioHistoryPointDTO {
  period_id: string;
  fiscal_year: number;
  period_type: RatioPeriodType;
  period_end?: string | null;
  status: RatioStatus;
  exact_value?: number | string | null;
  formatted_value: string;
  is_restated?: boolean;
}

export interface RatioHistoryResponse {
  company_id: string;
  company_name: string;
  ratio_id: string;
  ratio_name: string;
  category: RatioCategory;
  unit_kind: UnitKind;
  series: RatioHistoryPointDTO[];
}

export interface RatioMethodologyResponse {
  definition: RatioDefinitionDTO;
  calculation_notes: string;
  supported_periods: RatioPeriodType[];
}

export interface RatioLineageResponse {
  company_id: string;
  ratio_id: string;
  period_id: string;
  ratio_value?: RatioValueDTO | null;
  source_documents: Array<{
    statement_type: string;
    period_id: string;
    provenance_provider: string;
    filing_status: string;
  }>;
}
