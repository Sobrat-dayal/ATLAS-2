/**
 * Types for ATLAS Financial and Economic Exposure Engine (Stage 137).
 */

export type ExposureDomain =
  | "COMPANY"
  | "PORTFOLIO"
  | "GEOGRAPHIC"
  | "SECTOR"
  | "COMMODITY"
  | "CORPORATE_GROUP"
  | "SUPPLY_CHAIN"
  | "INFRASTRUCTURE"
  | "DERIVATIVES"
  | "MACRO_ECONOMIC";

export type ExposureType =
  | "EQUITY_POSITION_EXPOSURE"
  | "DEBT_POSITION_EXPOSURE"
  | "PORTFOLIO_WEIGHT_EXPOSURE"
  | "DERIVATIVE_NOTIONAL_EXPOSURE"
  | "DERIVATIVE_DELTA_EQUIVALENT_EXPOSURE"
  | "DERIVATIVE_SENSITIVITY_EXPOSURE"
  | "REVENUE_GEOGRAPHIC_EXPOSURE"
  | "REVENUE_SEGMENT_EXPOSURE"
  | "REVENUE_CUSTOMER_EXPOSURE"
  | "ASSET_GEOGRAPHIC_EXPOSURE"
  | "CAPEX_GEOGRAPHIC_EXPOSURE"
  | "SECTOR_ALLOCATION_EXPOSURE"
  | "INDUSTRY_ALLOCATION_EXPOSURE"
  | "COMMODITY_PRICE_EXPOSURE"
  | "COMMODITY_OPERATIONAL_EXPOSURE"
  | "FOREIGN_EXCHANGE_EXPOSURE"
  | "INTEREST_RATE_EXPOSURE"
  | "SUPPLY_CHAIN_DEPENDENCY"
  | "INFRASTRUCTURE_ASSET_ASSOCIATION"
  | "FACILITY_GEOGRAPHIC_PRESENCE"
  | "CORPORATE_GROUP_EXPOSURE"
  | "ECONOMIC_INDICATOR_SENSITIVITY"
  | "SCENARIO_EXPOSURE";

export type ExposureEvidenceClass =
  | "REPORTED"
  | "DETERMINISTICALLY_CALCULATED"
  | "MODEL_ESTIMATED"
  | "USER_DEFINED_SCENARIO"
  | "SOURCE_REPORTED_QUALITATIVE"
  | "UNAVAILABLE";

export type ExposureRelationshipStrength =
  | "DIRECT_MEASURED"
  | "DIRECT_REPORTED"
  | "DERIVED_FROM_VERIFIED_DATA"
  | "INDIRECT_DOCUMENTED"
  | "QUALITATIVE_REPORTED"
  | "ASSUMPTION_DEPENDENT"
  | "UNRESOLVED";

export type CoverageStatus =
  | "COMPLETE"
  | "PARTIAL"
  | "UNALLOCATED_RESIDUAL"
  | "UNCOVERED"
  | "UNKNOWN";

export type UncertaintyClass =
  | "SOURCE_INCOMPLETE"
  | "TEMPORAL_MISMATCH"
  | "ENTITY_IDENTITY_AMBIGUITY"
  | "GEOGRAPHIC_PRECISION_LIMITATION"
  | "QUANTITATIVE_ESTIMATION"
  | "SCENARIO_ASSUMPTION"
  | "DATA_STALENESS"
  | "INCONSISTENT_REPORTING"
  | "VERIFIED_DETERMINISTIC";

export type ConsolidationBasis =
  | "CONSOLIDATED"
  | "SUBSIDIARY_STANDALONE"
  | "EQUITY_METHOD"
  | "PROPORTIONAL"
  | "NOT_CONSOLIDATED";

export type AnalysisRunStatus =
  | "QUEUED"
  | "VALIDATING"
  | "RESOLVING"
  | "CALCULATING"
  | "VERIFYING"
  | "COMPLETED"
  | "PARTIAL"
  | "FAILED"
  | "CANCELLED";

export interface CanonicalGraphNodeRef {
  node_type: string;
  entity_id: string;
  canonical_name: string;
  identifier_map?: Record<string, string>;
  country_code?: string | null;
  sector?: string | null;
  metadata?: Record<string, unknown>;
  tenant_id?: string | null;
}

export interface ExposureMeasureDefinition {
  measure_id: string;
  measure_version: string;
  display_name: string;
  domain: ExposureDomain;
  unit_dimension: string;
  financial_basis: string;
  numerator_definition: string;
  denominator_definition?: string | null;
  aggregation_rule: string;
  missing_data_policy: string;
  required_sources: string[];
  allowed_derivation_methods: string[];
  description: string;
}

export interface ExposureCoverageSummary {
  total_relevant_denominator: string | number;
  eligible_covered_denominator: string | number;
  coverage_ratio: string | number;
  covered_dimensions: string[];
  uncovered_dimensions: string[];
  unallocated_residual_amount?: string | number | null;
  unallocated_residual_percentage?: string | number | null;
  coverage_status: CoverageStatus;
  notes: string[];
}

export interface AtlasExposureResult {
  exposure_id: string;
  analysis_run_id: string;
  subject_entity_ref: CanonicalGraphNodeRef;
  target_entity_ref: CanonicalGraphNodeRef;
  related_event_id?: string | null;
  exposure_domain: ExposureDomain;
  exposure_type: ExposureType;
  exposure_measure_id: string;
  evidence_class: ExposureEvidenceClass;
  relationship_strength: ExposureRelationshipStrength;
  amount?: string | number | null;
  currency?: string | null;
  unit: string;
  percentage?: string | number | null;
  numerator_value?: string | number | null;
  denominator_value?: string | number | null;
  denominator_reference?: string | null;
  reporting_period?: string | null;
  market_data_as_of?: string | null;
  valid_at?: string | null;
  known_as_of: string;
  calculation_method_id: string;
  calculation_version: string;
  assumption_set_id?: string | null;
  source_manifest_id?: string | null;
  input_lineage_ids: string[];
  graph_path_ids: string[];
  coverage_status: CoverageStatus;
  coverage_ratio?: string | number | null;
  uncertainty_class: UncertaintyClass;
  explanation: string;
  limitations_disclaimer: string;
  warnings: string[];
  tenant_id?: string | null;
  created_at: string;
}

export interface ExposureScenarioShock {
  shock_id: string;
  target_dimension: string;
  target_identifier: string;
  shock_value: string | number;
  shock_unit: string;
  description?: string | null;
}

export interface ExposureScenarioDefinition {
  scenario_id: string;
  scenario_name: string;
  owner_id: string;
  shocks: ExposureScenarioShock[];
  methodology_version: string;
  market_data_as_of?: string | null;
  financial_data_as_of?: string | null;
  known_as_of: string;
  description: string;
  created_at: string;
}

export interface ExposureScenarioRun {
  run_id: string;
  scenario_id: string;
  status: AnalysisRunStatus;
  subject_entity_ref: CanonicalGraphNodeRef;
  results: AtlasExposureResult[];
  total_conditional_pnl: string | number;
  base_currency: string;
  warnings: string[];
  assumptions_notice: string;
  generated_at: string;
}

export interface ExposureAnalysisRun {
  run_id: string;
  subject_ref: CanonicalGraphNodeRef;
  event_id?: string | null;
  exposure_domains: ExposureDomain[];
  status: AnalysisRunStatus;
  results: AtlasExposureResult[];
  coverage_summary?: ExposureCoverageSummary | null;
  graph_revision?: string | null;
  financial_data_revision?: string | null;
  known_as_of: string;
  valid_at?: string | null;
  calculation_versions: Record<string, string>;
  warnings: string[];
  tenant_id?: string | null;
  started_at: string;
  completed_at?: string | null;
}
