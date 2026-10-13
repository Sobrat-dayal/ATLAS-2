/**
 * Strict TypeScript models for Stage 53 Home Personalized Activity.
 */

export type ActivityEventType = "MODULE_OPENED" | "ENTITY_SELECTED";

export interface UserActivityItem {
  activity_id: string;
  event_type: ActivityEventType;
  module_id?: string | null;
  module_label?: string | null;
  entity_id?: string | null;
  entity_display_name?: string | null;
  entity_type?: string | null;
  occurred_at: string;
  resume_target: string;
  is_accessible: boolean;
}

export interface UserActivityListResponse {
  schema_version: number;
  enabled: boolean;
  items: UserActivityItem[];
  next_cursor?: string | null;
  has_more: boolean;
}

export interface RecordActivityEventRequest {
  event_type: ActivityEventType;
  module_id?: string | null;
  entity_id?: string | null;
  client_event_id: string;
}

export interface ActivityConsentRequest {
  enabled: boolean;
}

export interface ActivityConsentResponse {
  enabled: boolean;
  updated_at: string;
}

export interface ClearActivityResponse {
  deleted_count: number;
  cleared: boolean;
}
