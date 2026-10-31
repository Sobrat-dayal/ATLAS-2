/**
 * TypeScript Contracts for ATLAS Intelligence Scoring (Stage 139).
 */

export type ScoreStatus =
  | "AVAILABLE"
  | "PARTIAL"
  | "INSUFFICIENT_DATA"
  | "NOT_APPLICABLE"
  | "STALE"
  | "MODEL_UNVALIDATED"
  | "MODEL_DISABLED"
  | "SOURCE_UNAVAILABLE"
  | "PERMISSION_DENIED"
  | "CALCULATION_FAILED";

export type ScoreScale =
  | "BOUNDED_INDEX_0_100"
  | "ORDINAL_RANK"
  | "PROBABILITY_0_1";

export type ScoreObjectiveId =
  | "EVENT_REVIEW_PRIORITY"
  | "EVENT_ENTITY_RELEVANCE"
  | "PORTFOLIO_EVENT_ATTENTION"
  | "ECONOMIC_EVENT_RELEVANCE"
  | "GEOGRAPHIC_EVENT_RELEVANCE"
  | "SOURCE_EVIDENCE_ASSESSMENT";

export type FactorTransformationMethod =
  | "BINARY_ELIGIBILITY"
  | "BOUNDED_PROPORTION"
  | "EXPONENTIAL_DECAY"
  | "DISTANCE_STEP_FUNCTION"
  | "ORDINAL_MAPPING"
  | "DIRECT_SCALE";

export interface FactorContribution {
  factor_id: string;
  factor_name: string;
  raw_value?: unknown;
  transformed_value: number;
  transformation_method: FactorTransformationMethod;
  weight: number;
  contribution_points: number;
  is_missing: boolean;
  source_reference?: string | null;
  explanation: string;
}

export interface ScoreUncertaintyMetadata {
  coverage_ratio: number;
  available_feature_count: number;
  required_feature_count: number;
  missing_features: string[];
  has_source_conflicts: boolean;
  conflict_notes: string[];
  limitations: string[];
  is_calibration_applicable: boolean;
  calibration_target?: string | null;
}

export interface ScoreLineageRecord {
  feature_snapshot_id: string;
  model_id: string;
  model_version: string;
  policy_id: string;
  event_revision?: number | null;
  graph_revision?: number | null;
  exposure_run_id?: string | null;
  source_ids: string[];
  computation_host: string;
}

export interface AtlasIntelligenceScore {
  score_id: string;
  score_type: string;
  scoring_objective: ScoreObjectiveId;
  subject_reference: Record<string, unknown>;
  context_reference?: Record<string, unknown> | null;
  event_id?: string | null;
  entity_id?: string | null;
  portfolio_id?: string | null;
  model_id: string;
  model_version: string;
  score_value?: number | null;
  score_scale: ScoreScale;
  score_interpretation: string;
  score_status: ScoreStatus;
  factor_contributions: FactorContribution[];
  uncertainty: ScoreUncertaintyMetadata;
  lineage: ScoreLineageRecord;
  valid_at: string;
  known_as_of: string;
  computed_at: string;
  tenant_scope?: string | null;
}

export interface RankedItem {
  rank: number;
  score: AtlasIntelligenceScore;
  tie_breaker_key: string;
}

export interface ScoringObjectiveDefinition {
  objective_id: ScoreObjectiveId;
  name: string;
  target_construct: string;
  intended_use: string;
  prohibited_interpretations: string[];
  eligible_subject_types: string[];
  default_scale: ScoreScale;
  required_features: string[];
  optional_features: string[];
}

export interface ScoringFactorWeightConfig {
  factor_id: string;
  weight: number;
  half_life_hours?: number | null;
  max_bound?: number | null;
}

export interface IntelligenceScoringPolicy {
  policy_id: string;
  policy_version: string;
  score_objective: ScoreObjectiveId;
  description: string;
  factor_configs: ScoringFactorWeightConfig[];
  missing_data_policy: string;
  min_coverage_threshold: number;
  governance_status: string;
  is_default: boolean;
  tenant_id?: string | null;
}

export interface ScoringModelDefinition {
  model_id: string;
  model_name: string;
  model_family: string;
  objective_id: ScoreObjectiveId;
  active_version: string;
  supported_versions: string[];
  score_scale: ScoreScale;
  default_policy_id: string;
  governance_status: string;
  is_production: boolean;
  approved_by?: string | null;
  approved_at?: string | null;
}

export interface ScoringEvaluationManifest {
  evaluation_id: string;
  model_id: string;
  model_version: string;
  evaluation_dataset: string;
  time_window_start: string;
  time_window_end: string;
  sample_size: number;
  ndcg_at_10?: number | null;
  precision_at_5?: number | null;
  mean_reciprocal_rank?: number | null;
  brier_score?: number | null;
  expected_calibration_error?: number | null;
  drift_detected: boolean;
  validation_status: string;
  evaluated_at: string;
}

export interface ScoringTelemetrySummary {
  model_id: string;
  active_version: string;
  total_scores_computed: number;
  mean_score_value: number;
  high_priority_fraction: number;
  average_coverage_ratio: number;
  missing_features_rate: number;
  drift_status: string;
  last_evaluated_at: string;
}

export interface ScoringCapabilitiesResponse {
  system_name: string;
  version: string;
  supported_objectives: string[];
  supported_scales: string[];
  active_models_count: number;
  compliance_guarantees: string[];
}
