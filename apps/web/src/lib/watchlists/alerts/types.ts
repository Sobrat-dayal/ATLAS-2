/**
 * TypeScript Type Definitions for Watchlist Alerts V1 (Stage 80).
 */

export type AlertRuleType =
  | "PRICE_ABOVE"
  | "PRICE_BELOW"
  | "CROSSING_ABOVE"
  | "CROSSING_BELOW"
  | "PERCENTAGE_CHANGE_ABOVE"
  | "PERCENTAGE_CHANGE_BELOW";

export type QuoteMeasure =
  | "LAST"
  | "BID"
  | "ASK"
  | "MID"
  | "OPEN"
  | "HIGH"
  | "LOW"
  | "CLOSE"
  | "NAV"
  | "YIELD";

export type ComparisonOperator =
  | "GREATER_THAN"
  | "LESS_THAN"
  | "CROSS_ABOVE"
  | "CROSS_BELOW";

export type RecurrencePolicy = "ONE_SHOT" | "RECURRING";

export type AlertState = "ENABLED" | "PAUSED" | "DISABLED" | "EXPIRED" | "DELETED";

export type AlertEvaluationStatus =
  | "WAITING_FOR_BASELINE"
  | "ARMED"
  | "TRIGGERED"
  | "COOLDOWN"
  | "DATA_UNAVAILABLE"
  | "DEGRADED"
  | "ENTITLEMENT_DENIED"
  | "EXPIRED"
  | "COMPLETED";

export type ArmedSide = "ABOVE" | "BELOW" | "AT";

export type ReferenceMethodology =
  | "SESSION_PREVIOUS_CLOSE"
  | "ROLLING_24H"
  | "PREVIOUS_NAV";

export type NotificationDeliveryStatus = "PENDING" | "DELIVERED" | "RETRYING" | "FAILED";

export interface WatchlistAlertEvaluationState {
  alert_id: string;
  rule_revision: number;
  evaluation_status: AlertEvaluationStatus;
  baseline_established: boolean;
  armed_side: ArmedSide | null;
  last_qualified_value: number | null;
  last_qualified_observation_time: string | null;
  last_qualified_observation_identity: string | null;
  last_trigger_at: string | null;
  cooldown_until: string | null;
  updated_at: string;
}

export interface WatchlistAlertRule {
  id: string;
  owner_user_id: string;
  watchlist_id: string;
  watchlist_item_id: string;
  instrument_entity_id: string;
  market_series_identity: string;
  symbol: string;
  rule_type: AlertRuleType;
  rule_version: number;
  quote_measure: QuoteMeasure;
  comparison_operator: ComparisonOperator;
  threshold_decimal: number;
  threshold_unit: string;
  reference_methodology: ReferenceMethodology | null;
  recurrence_policy: RecurrencePolicy;
  cooldown_seconds: number;
  expires_at: string | null;
  enabled: boolean;
  state: AlertState;
  revision: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  evaluation_state: WatchlistAlertEvaluationState | null;
}

export interface WatchlistAlertTrigger {
  id: string;
  alert_id: string;
  rule_revision: number;
  owner_user_id: string;
  watchlist_id: string;
  watchlist_item_id: string;
  instrument_entity_id: string;
  market_series_identity: string;
  symbol: string;
  event_identity: string;
  observation_value: number;
  threshold_value: number;
  quote_measure: string;
  rule_type: string;
  source: string;
  venue: string | null;
  observation_time: string;
  evaluated_at: string;
  trigger_dedup_key: string;
  notification_status: NotificationDeliveryStatus;
  created_at: string;
}

export interface CreateAlertPayload {
  watchlist_item_id: string;
  instrument_entity_id: string;
  market_series_identity: string;
  symbol: string;
  rule_type: AlertRuleType;
  quote_measure: QuoteMeasure;
  comparison_operator?: ComparisonOperator;
  threshold_decimal: number;
  threshold_unit: string;
  reference_methodology?: ReferenceMethodology | null;
  recurrence_policy: RecurrencePolicy;
  cooldown_seconds?: number;
  expires_at?: string | null;
  notes?: string | null;
}

export interface UpdateAlertPayload {
  expected_revision: number;
  threshold_decimal?: number;
  threshold_unit?: string;
  quote_measure?: QuoteMeasure;
  recurrence_policy?: RecurrencePolicy;
  cooldown_seconds?: number;
  expires_at?: string | null;
  notes?: string | null;
}

export interface AlertListResponse {
  items: WatchlistAlertRule[];
  total: number;
  page: number;
  page_size: number;
}

export interface AlertCapabilitiesResponse {
  supported_rule_types: AlertRuleType[];
  supported_quote_measures: QuoteMeasure[];
  cooldown_presets_seconds: number[];
  reference_methodologies: ReferenceMethodology[];
  asset_class_measures: Record<string, QuoteMeasure[]>;
  quotas: {
    max_active_alerts_per_user: number;
    max_alerts_per_instrument: number;
  };
}

export interface AlertHealthResponse {
  status: string;
  evaluator: {
    worker_running: boolean;
    active_indexed_series: number;
    total_indexed_rules: number;
  };
  timestamp: string;
}
