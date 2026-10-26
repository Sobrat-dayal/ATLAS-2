/**
 * TypeScript Interfaces and DTOs for Global Economic Calendar (Stage 92).
 */

export type EconomicEventKind =
  | "ECONOMIC_STATISTICS_RELEASE"
  | "CENTRAL_BANK_POLICY_MEETING"
  | "CENTRAL_BANK_POLICY_DECISION"
  | "CENTRAL_BANK_OFFICIAL_PUBLICATION"
  | "OTHER_VERIFIED_MACRO_EVENT";

export type EconomicEventCategory =
  | "GDP"
  | "INFLATION"
  | "LABOR_MARKET"
  | "INDUSTRIAL_ACTIVITY"
  | "CONSUMPTION"
  | "HOUSING"
  | "BUSINESS_SURVEYS"
  | "FISCAL"
  | "EXTERNAL_SECTOR"
  | "MONETARY_POLICY";

export type SchedulePrecision =
  | "EXACT_INSTANT"
  | "LOCAL_DATE_TIME"
  | "DATE_ONLY"
  | "UNKNOWN";

export type EconomicEventStatus =
  | "SCHEDULED"
  | "RESCHEDULED"
  | "RELEASE_VERIFIED"
  | "POSTPONED"
  | "CANCELLED"
  | "STATUS_UNKNOWN";

export type ReleaseStage =
  | "ADVANCE"
  | "PRELIMINARY"
  | "FIRST_RELEASE"
  | "REVISED"
  | "FINAL";

export type EconomicEventImportance =
  | "HIGH"
  | "MEDIUM"
  | "LOW"
  | "UNCLASSIFIED";

export type ForecastAggregationMethod =
  | "MEDIAN"
  | "MEAN"
  | "WEIGHTED_MEAN"
  | "OFFICIAL_PROJECTION"
  | "UNSPECIFIED";

export type SurpriseDirection =
  | "ABOVE_CONSENSUS"
  | "BELOW_CONSENSUS"
  | "IN_LINE"
  | "NOT_APPLICABLE";

export type EventAlertType =
  | "BEFORE_SCHEDULED_RELEASE"
  | "WHEN_RELEASE_VERIFIED"
  | "WHEN_SCHEDULE_CHANGES"
  | "WHEN_OFFICIAL_REVISION_PUBLISHED";

export type AlertStatus =
  | "ACTIVE"
  | "PAUSED"
  | "FIRED"
  | "CANCELLED"
  | "EXPIRED";

export type CalendarViewPreset =
  | "all"
  | "today"
  | "tomorrow"
  | "this_week"
  | "next_week"
  | "upcoming"
  | "released"
  | "central_bank"
  | "my_alerts";

export interface EconomicReleaseFamilyDTO {
  family_id: string;
  name: string;
  category: EconomicEventCategory;
  geography_id: string;
  agency_name: string;
  default_importance: EconomicEventImportance;
  description: string;
}

export interface EconomicEventObservationDTO {
  observation_id: string;
  event_id: string;
  economic_series_id: string;
  indicator_name: string;
  reference_period: string;
  actual_value?: number | null;
  previous_value?: number | null;
  revised_previous_value?: number | null;
  unit: string;
  release_stage: ReleaseStage;
  source_revision: string;
}

export interface ConsensusSnapshotDTO {
  snapshot_id: string;
  event_id: string;
  economic_series_id: string;
  consensus_value: number;
  unit: string;
  aggregation_method: ForecastAggregationMethod;
  contributor_count?: number | null;
  snapshot_timestamp: string;
  provider_name: string;
}

export interface EconomicSurpriseMetricDTO {
  event_id: string;
  economic_series_id: string;
  actual_value: number;
  consensus_value: number;
  unit: string;
  surprise_value: number;
  percentage_point_diff?: number | null;
  basis_point_diff?: number | null;
  relative_surprise_pct?: number | null;
  direction: SurpriseDirection;
  methodology_version: string;
}

export interface ScheduleRevisionDTO {
  revision_id: string;
  event_id: string;
  previous_scheduled_time: string;
  new_scheduled_time: string;
  reason?: string | null;
  revised_at: string;
}

export interface EconomicCalendarEventDTO {
  event_id: string;
  official_event_identifier: string;
  event_kind: EconomicEventKind;
  category: EconomicEventCategory;
  release_family_id: string;
  title: string;
  geographic_entity_ids: string[];
  institution_entity_id?: string | null;
  scheduled_start: string; // UTC ISO string
  scheduled_end?: string | null;
  scheduled_start_display: string;
  display_timezone: string;
  schedule_precision: SchedulePrecision;
  source_timezone: string;
  reference_period: string;
  release_stage: ReleaseStage;
  event_status: EconomicEventStatus;
  importance: EconomicEventImportance;
  indicators: string[];
  official_source_id: string;
  official_source_name: string;
  official_source_url: string;
  published_at?: string | null;
  is_verified: boolean;
  primary_series_id?: string | null;
  actual_value?: number | null;
  consensus_value?: number | null;
  previous_value?: number | null;
  revised_previous_value?: number | null;
  unit?: string | null;
  surprise?: EconomicSurpriseMetricDTO | null;
}

export interface EconomicCalendarEventDetailDTO {
  event: EconomicCalendarEventDTO;
  observations: EconomicEventObservationDTO[];
  consensus_snapshots: ConsensusSnapshotDTO[];
  schedule_revisions: ScheduleRevisionDTO[];
  surprises: EconomicSurpriseMetricDTO[];
  notes?: string | null;
  provenance_id: string;
  source_revision: string;
}

export interface CalendarQueryContextDTO {
  display_timezone: string;
  start_date?: string | null;
  end_date?: string | null;
  view_preset: string;
  total_events: number;
}

export interface EconomicCalendarResponseDTO {
  context: CalendarQueryContextDTO;
  events: EconomicCalendarEventDTO[];
  categories: string[];
  supported_geographies: string[];
}

export interface UserEventAlertDTO {
  alert_id: string;
  owner_user_id: string;
  event_id: string;
  event_title: string;
  scheduled_time: string;
  alert_type: EventAlertType;
  reminder_offset_minutes: number;
  is_enabled: boolean;
  status: AlertStatus;
  created_at: string;
  last_triggered_at?: string | null;
  trigger_count: number;
}

export interface CreateEventAlertRequestDTO {
  event_id: string;
  alert_type?: EventAlertType;
  reminder_offset_minutes?: number;
  is_enabled?: boolean;
}

export interface UpdateEventAlertRequestDTO {
  reminder_offset_minutes?: number;
  is_enabled?: boolean;
  status?: AlertStatus;
}

export interface AlertDeliveryIntentDTO {
  intent_id: string;
  alert_id: string;
  owner_user_id: string;
  event_id: string;
  title: string;
  body: string;
  scheduled_for: string;
  delivered_at?: string | null;
  is_delivered: boolean;
  delivery_error?: string | null;
}

export interface EconomicCalendarCoverageDTO {
  supported_geographies: string[];
  supported_categories: string[];
  total_events_count: number;
  verified_events_count: number;
  forecast_coverage_pct: number;
  schedule_precision_coverage: Record<string, number>;
}
