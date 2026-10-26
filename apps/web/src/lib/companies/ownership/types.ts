/**
 * TypeScript Type Definitions for Company Ownership Intelligence (Stage 85).
 * 
 * Defines qualified models for institutional holders, insider positions,
 * beneficial owners (Schedule 13D/13G), shareholding pattern categories,
 * historical ownership snapshots, and quarterly position changes.
 */

export type HolderCategory =
  | "INSTITUTIONAL_MANAGER"
  | "INVESTMENT_FUND"
  | "CORPORATION"
  | "INSIDER_PERSON"
  | "GOVERNMENT_ENTITY"
  | "SOVEREIGN_WEALTH_FUND"
  | "PROMOTER"
  | "NOMINEE_CUSTODIAN"
  | "RETAIL_PUBLIC"
  | "OTHER_DISCLOSED_HOLDER";

export type OwnershipForm =
  | "DIRECT"
  | "INDIRECT"
  | "BENEFICIAL"
  | "REGISTERED_NOMINEE"
  | "MANAGED_DISCRETIONARY"
  | "VOTING_TRUST"
  | "OTHER";

export type PositionType =
  | "ORDINARY_SHARES"
  | "PREFERRED_SHARES"
  | "DEPOSITARY_RECEIPTS"
  | "CLASS_A_COMMON"
  | "CLASS_B_COMMON"
  | "DERIVATIVE_CALL"
  | "DERIVATIVE_PUT"
  | "WARRANT"
  | "RESTRICTED_STOCK_UNIT"
  | "STOCK_OPTION";

export type DisclosureType =
  | "FORM_13F"
  | "SCHEDULE_13D"
  | "SCHEDULE_13G"
  | "FORM_3"
  | "FORM_4"
  | "FORM_5"
  | "SEBI_SHAREHOLDING_PATTERN"
  | "ANNUAL_PROXY_DEF14A"
  | "ANNUAL_REPORT"
  | "OTHER_REGULATORY";

export type PositionChangeStatus =
  | "NEW_HOLDING"
  | "INCREASED"
  | "DECREASED"
  | "UNCHANGED"
  | "EXITED";

export interface HolderSummaryDTO {
  holder_entity_id: string;
  name: string;
  category: HolderCategory;
  reporting_party?: string | null;
  country?: string | null;
  is_insider: boolean;
  is_institution: boolean;
  is_promoter: boolean;
}

export interface SecuritySummaryDTO {
  security_id: string;
  ticker?: string | null;
  share_class?: string | null;
  security_name: string;
  shares_outstanding: number;
  formatted_shares_outstanding: string;
  as_of_date: string;
}

export interface OwnershipPositionDTO {
  position_id: string;
  company_id: string;
  security_id: string;
  security_name: string;
  share_class?: string | null;
  holder: HolderSummaryDTO;
  shares_held: number;
  formatted_shares: string;
  source_reported_percentage?: number | null;
  calculated_percentage?: number | null;
  formatted_percentage?: string | null;
  reporting_date: string;
  filing_date: string;
  filing_delay_days: number;
  disclosure_type: DisclosureType;
  jurisdiction: string;
  source_document_id?: string | null;
  source_provider: string;
  ownership_form: OwnershipForm;
  position_type: PositionType;
  voting_power_shares?: number | null;
  shared_voting_power_shares?: number | null;
  dispositive_power_shares?: number | null;
  shared_dispositive_power_shares?: number | null;
  indicative_market_value?: number | null;
  formatted_market_value?: string | null;
  insider_role?: string | null;
  is_officer: boolean;
  is_director: boolean;
}

export interface OwnershipConcentrationDTO {
  company_id: string;
  reporting_period: string;
  top_1_holder_name?: string | null;
  top_1_shares?: number | null;
  top_1_pct?: number | null;
  top_5_shares?: number | null;
  top_5_pct?: number | null;
  top_10_shares?: number | null;
  top_10_pct?: number | null;
  total_disclosed_shares?: number | null;
  total_disclosed_pct?: number | null;
  total_shares_outstanding: number;
}

export interface PatternCategoryDTO {
  category_name: string;
  shares_held: number;
  formatted_shares: string;
  percentage_of_total: number;
  formatted_percentage: string;
  pledged_percentage?: number | null;
  shareholder_count?: number | null;
}

export interface ShareholdingPatternDTO {
  company_id: string;
  reporting_period: string;
  reporting_date: string;
  categories: PatternCategoryDTO[];
}

export interface CompanyOwnershipOverviewDTO {
  company_id: string;
  company_name: string;
  selected_security: SecuritySummaryDTO;
  available_securities: SecuritySummaryDTO[];
  reporting_period: string;
  reporting_date: string;
  filing_date: string;
  source_coverage: string;
  concentration: OwnershipConcentrationDTO;
  top_holders: OwnershipPositionDTO[];
  institutional_summary: {
    total_shares?: number;
    formatted_shares?: string;
    percentage?: number;
    holder_count?: number;
    [key: string]: any;
  };
  insider_summary: {
    total_shares?: number;
    formatted_shares?: string;
    percentage?: number;
    holder_count?: number;
    [key: string]: any;
  };
  beneficial_summary: Record<string, any>;
  patterns?: ShareholdingPatternDTO | null;
}

export interface InstitutionalHoldingDTO {
  position: OwnershipPositionDTO;
  shares_change_prior_quarter?: number | null;
  formatted_shares_change?: string | null;
  status: PositionChangeStatus;
  percentage_points_change?: number | null;
}

export interface InstitutionalHoldingsResponseDTO {
  company_id: string;
  reporting_period: string;
  total_count: number;
  items: InstitutionalHoldingDTO[];
}

export interface InsiderHoldingDTO {
  position: OwnershipPositionDTO;
  shares_change_prior_filing?: number | null;
  formatted_shares_change?: string | null;
  status: PositionChangeStatus;
  transaction_code?: string | null;
  is_officer: boolean;
  is_director: boolean;
}

export interface InsiderHoldingsResponseDTO {
  company_id: string;
  reporting_period: string;
  total_count: number;
  items: InsiderHoldingDTO[];
}

export interface BeneficialOwnerDTO {
  position: OwnershipPositionDTO;
  is_group_filing: boolean;
  group_name?: string | null;
  sole_voting_power?: number | null;
  shared_voting_power?: number | null;
  sole_dispositive_power?: number | null;
  shared_dispositive_power?: number | null;
}

export interface BeneficialOwnersResponseDTO {
  company_id: string;
  reporting_period: string;
  total_count: number;
  items: BeneficialOwnerDTO[];
}

export interface OwnershipChangeDTO {
  holder: HolderSummaryDTO;
  security_id: string;
  current_shares: number;
  prior_shares: number;
  shares_change: number;
  formatted_shares_change: string;
  position_pct_change?: number | null;
  formatted_pct_change?: string | null;
  percentage_points_change?: number | null;
  formatted_pp_change?: string | null;
  status: PositionChangeStatus;
  is_corporate_action_adjusted: boolean;
}

export interface OwnershipChangesResponseDTO {
  company_id: string;
  current_period: string;
  prior_period: string;
  total_count: number;
  items: OwnershipChangeDTO[];
}

export interface HistoricalOwnershipSnapshotDTO {
  reporting_period: string;
  reporting_date: string;
  filing_date: string;
  shares_outstanding: number;
  formatted_shares_outstanding: string;
  total_disclosed_shares: number;
  formatted_disclosed_shares: string;
  total_disclosed_percentage: number;
  top_5_percentage: number;
  institutional_shares: number;
  insider_shares: number;
  holder_count: number;
}

export interface OwnershipHistoryResponseDTO {
  company_id: string;
  security_id: string;
  snapshots: HistoricalOwnershipSnapshotDTO[];
}

export interface OwnershipSecuritiesResponseDTO {
  company_id: string;
  securities: SecuritySummaryDTO[];
}

export interface OwnershipHoldersResponseDTO {
  company_id: string;
  reporting_period: string;
  total_count: number;
  items: OwnershipPositionDTO[];
}
