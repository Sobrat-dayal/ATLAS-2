/**
 * TypeScript types and contracts for ATLAS AI Financial Action Engine (Stage 128).
 */

export type AiActionType =
  // Charts
  | "atlas.chart.select_instrument"
  | "atlas.chart.set_timeframe"
  | "atlas.chart.set_date_range"
  | "atlas.chart.set_type"
  | "atlas.chart.add_indicator"
  | "atlas.chart.remove_indicator"
  | "atlas.chart.update_indicator"
  | "atlas.chart.add_comparison"
  | "atlas.chart.remove_comparison"
  | "atlas.chart.save_configuration"
  | "atlas.chart.restore_configuration"
  // Screeners
  | "atlas.screener.create_draft"
  | "atlas.screener.add_filter"
  | "atlas.screener.update_filter"
  | "atlas.screener.remove_filter"
  | "atlas.screener.set_universe"
  | "atlas.screener.set_sort"
  | "atlas.screener.set_columns"
  | "atlas.screener.preview"
  | "atlas.screener.execute"
  | "atlas.screener.save"
  | "atlas.screener.update_saved"
  | "atlas.screener.restore_revision"
  // Portfolios
  | "atlas.portfolio.analyze_allocation"
  | "atlas.portfolio.propose_targets"
  | "atlas.portfolio.calculate_allocation_delta"
  | "atlas.portfolio.create_scenario_draft"
  | "atlas.portfolio.compare_allocations"
  | "atlas.portfolio.save_scenario_draft"
  // Risk
  | "atlas.risk.get_models"
  | "atlas.risk.validate_parameters"
  | "atlas.risk.preview_run"
  | "atlas.risk.start_run"
  | "atlas.risk.get_run_status"
  | "atlas.risk.cancel_run"
  | "atlas.risk.get_run_results"
  | "atlas.risk.compare_runs"
  | "atlas.risk.run_stress_scenario";

export type AiActionClassification =
  | "READ_ONLY"
  | "SESSION_UI_CHANGE"
  | "USER_PREFERENCE_CHANGE"
  | "PERSISTENT_CONFIGURATION_CHANGE"
  | "SAVED_ANALYTICAL_DRAFT"
  | "COMPUTATION_JOB"
  | "FINANCIAL_LEDGER_MUTATION"
  | "BROKER_SIDE_EFFECT"
  | "EXTERNAL_SIDE_EFFECT"
  | "PRIVILEGED_OPERATION";

export type ApprovalPolicy =
  | "AUTO_READ_ONLY"
  | "USER_PREVIEW_CONFIRM"
  | "EXPLICIT_SENSITIVE_APPROVAL"
  | "COMPUTATION_COST_APPROVAL"
  | "PROHIBITED";

export type ReversibilityPolicy =
  | "REVERSIBLE"
  | "COMPENSATABLE"
  | "NON_REVERSIBLE"
  | "CANCELLABLE_ONLY";

export type ActionLifecycleState =
  | "REQUESTED"
  | "INTERPRETING"
  | "RESOLVING_CONTEXT"
  | "VALIDATING"
  | "PREVIEW_READY"
  | "APPROVAL_REQUIRED"
  | "APPROVED"
  | "DENIED"
  | "EXPIRED"
  | "QUEUED"
  | "EXECUTING"
  | "VERIFYING"
  | "COMPLETED"
  | "PARTIALLY_COMPLETED"
  | "FAILED"
  | "CANCEL_REQUESTED"
  | "CANCELLED"
  | "CONFLICTED"
  | "UNAVAILABLE";

export interface ActionDiffDTO {
  field_path: string;
  before_value: any;
  after_value: any;
  change_type: "ADD" | "MODIFY" | "REMOVE";
  validation_status: string;
  financial_impact_if_computable?: string | null;
}

export interface ActionPreviewDTO {
  preview_id: string;
  action_id: string;
  target_resource_type: string;
  target_resource_id: string;
  current_state: Record<string, any>;
  proposed_state: Record<string, any>;
  diffs: ActionDiffDTO[];
  financial_assumptions: string[];
  estimated_cost: "NONE" | "LOW" | "MEDIUM" | "HIGH";
  approval_policy: ApprovalPolicy;
  reversibility_policy: ReversibilityPolicy;
  preview_hash: string;
  created_at: string;
  expires_at: string;
}

export interface ActionDTO {
  action_id: string;
  action_type: AiActionType;
  action_version: string;
  target_module: "charts" | "screeners" | "portfolios" | "risk";
  target_resource_type: string;
  target_resource_id: string;
  actor_user_id: string;
  tenant_scope: string;
  proposed_arguments: Record<string, any>;
  normalized_arguments_hash: string;
  expected_resource_revision: string;
  classification: AiActionClassification;
  approval_policy: ApprovalPolicy;
  reversibility_policy: ReversibilityPolicy;
  action_status: ActionLifecycleState;
  preview?: ActionPreviewDTO | null;
  created_at: string;
  expires_at?: string | null;
}

export interface ActionPlanResponse {
  plan_id: string;
  owner_user_id: string;
  tenant_id: string;
  user_intent: string;
  actions: ActionDTO[];
  dependency_graph: Record<string, string[]>;
  conversation_id?: string | null;
  status: ActionLifecycleState;
  created_at: string;
  expires_at?: string | null;
}

export interface ActionCapabilityDTO {
  action_type: string;
  action_version: string;
  target_module: string;
  classification: string;
  approval_policy: string;
  reversibility_policy: string;
  description: string;
  parameters_schema: Record<string, any>;
}

export interface ActionCapabilitiesResponse {
  capabilities: ActionCapabilityDTO[];
  total_count: number;
}

export interface ExecutionReceiptDTO {
  receipt_id: string;
  action_id: string;
  plan_id: string;
  tool_call_id?: string | null;
  actor_user_id: string;
  target_resource_id: string;
  target_revision_before: string;
  target_revision_after: string;
  operation_status: ActionLifecycleState;
  started_at: string;
  completed_at: string;
  result_reference: Record<string, any>;
  diffs: ActionDiffDTO[];
  source_manifest_id?: string | null;
  error_code?: string | null;
  error_message?: string | null;
  undo_reference?: string | null;
}

export interface ExecuteActionPlanResponse {
  plan_id: string;
  status: ActionLifecycleState;
  executed_actions: number;
  receipts: ExecutionReceiptDTO[];
  is_partially_completed: boolean;
  error?: string | null;
}

export interface UndoActionResponse {
  action_id: string;
  status: string;
  restored_revision: string;
  receipt_id: string;
  undone_at: string;
}

export interface ActionHistoryItemDTO {
  action_id: string;
  plan_id: string;
  action_type: string;
  target_module: string;
  target_resource_id: string;
  status: ActionLifecycleState;
  created_at: string;
  completed_at?: string | null;
  receipt_id?: string | null;
  is_reversible: boolean;
}

export interface ActionHistoryResponse {
  history: ActionHistoryItemDTO[];
  total_count: number;
}

