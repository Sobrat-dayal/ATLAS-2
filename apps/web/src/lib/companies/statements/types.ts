/**
 * Canonical Types and Enums for Company Financial Statements (Stage 82).
 */

export type StatementType = "income_statement" | "balance_sheet" | "cash_flow_statement";

export type StatementPeriodType = "annual" | "quarterly" | "ttm" | "semiannual" | "nine_month";

export type ConsolidationScope = "consolidated" | "standalone";

export type AccountingFramework = "us_gaap" | "ifrs" | "ind_as" | "other" | "unknown";

export type ScaleType = "auto" | "billions" | "millions" | "thousands" | "original";

export type ComparisonMode =
  | "none"
  | "yoy_absolute"
  | "yoy_percent"
  | "qoq_absolute"
  | "qoq_percent"
  | "common_size";

export type RevisionPolicy = "latest" | "original";

export type DerivationKind =
  | "reported"
  | "normalized"
  | "derived_quarter"
  | "derived_ttm"
  | "subtotal";

export type DiagnosticStatus =
  | "consistent"
  | "within_rounding_tolerance"
  | "not_comparable"
  | "incomplete"
  | "requires_review";

export interface StatementPeriodDTO {
  period_id: string;
  label: string;
  period_type: StatementPeriodType;
  fiscal_year?: number;
  fiscal_quarter?: string;
  period_start?: string;
  period_end: string;
  filing_date?: string;
  reported_at?: string;
  is_restated: boolean;
  revision_id?: string;
  source_document_id?: string;
  source_filing_name?: string;
  is_derived: boolean;
  derivation_lineage: string[];
}

export interface FinancialStatementCellDTO {
  concept_id: string;
  original_concept?: string;
  original_label?: string;
  exact_value?: string | number | null;
  formatted_value: string;
  raw_number?: number | null;
  unit: string;
  unit_category: "currency" | "shares" | "currency_per_share" | "percent";
  scale: string;
  derivation_kind: DerivationKind;
  is_restated: boolean;
  source_revision?: string;
  source_document_id?: string;
  notes?: string;

  comparison_value?: string | number | null;
  comparison_formatted?: string | null;
  is_not_meaningful: boolean;
}

export interface FinancialStatementRowDTO {
  concept_id: string;
  label: string;
  hierarchy_level: number;
  parent_id?: string;
  display_order: number;
  is_group: boolean;
  is_total: boolean;
  normal_sign: "signed" | "positive" | "negative";
  unit_category: string;
  description?: string;
  cells: Record<string, FinancialStatementCellDTO>;
}

export interface StatementDiagnosticsDTO {
  status: DiagnosticStatus;
  balance_difference?: string | number | null;
  is_balanced: boolean;
  tolerance_applied?: string | number | null;
  notes: string[];
}

export interface FinancialStatementResponse {
  company_entity_id: string;
  reporting_entity_id: string;
  company_name: string;
  statement_type: StatementType;
  accounting_framework: AccountingFramework;
  consolidation_scope: ConsolidationScope;
  reporting_currency: string;
  scale: ScaleType;
  comparison_mode: ComparisonMode;
  revision_policy: RevisionPolicy;
  periods: StatementPeriodDTO[];
  rows: FinancialStatementRowDTO[];
  diagnostics: StatementDiagnosticsDTO;
  source_provenance: string;
  as_of: string;
}

export interface PeriodSummaryItem {
  period_id: string;
  label: string;
  period_type: StatementPeriodType;
  fiscal_year?: number;
  fiscal_quarter?: string;
  period_end: string;
  filing_date?: string;
  is_restated: boolean;
}

export interface StatementCatalogResponse {
  company_entity_id: string;
  reporting_entity_id: string;
  available_statements: StatementType[];
  available_fiscal_years: number[];
  available_periods: PeriodSummaryItem[];
  supported_scopes: ConsolidationScope[];
  reporting_currencies: string[];
  accounting_frameworks: AccountingFramework[];
  is_ttm_supported: boolean;
  latest_filing_date?: string;
}

export interface StatementSourceMetadataDTO {
  statement_type: StatementType;
  period_id: string;
  filing_name?: string;
  source_document_id?: string;
  source_revision?: string;
  is_restated: boolean;
  is_derived: boolean;
  derivation_lineage: string[];
  accounting_standard: string;
  reporting_currency: string;
}

export interface StatementSourcesResponse {
  company_id: string;
  statement_type: StatementType;
  sources: StatementSourceMetadataDTO[];
}
