/**
 * Type contracts for Stage 49 Persistent Notifications.
 */

export type NotificationCategory =
  | "general"
  | "system"
  | "security"
  | "data"
  | "market"
  | "research"
  | "account";

export type NotificationSeverity = "info" | "success" | "warning" | "error";

export type NotificationActionKind = "none" | "internal_route" | "entity_route";

export type NotificationListFilter = "all" | "unread" | "archived";

export interface NotificationItem {
  notification_id: string;
  category: NotificationCategory;
  severity: NotificationSeverity;
  title: string;
  message: string;
  action_kind: NotificationActionKind;
  action_route: string | null;
  action_entity_id: string | null;
  created_at: string;
  read_at: string | null;
  archived_at: string | null;
}

export interface NotificationListResponse {
  items: NotificationItem[];
  next_cursor: string | null;
  has_more: boolean;
  unread_count?: number | null;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkAllReadResponse {
  updated_count: number;
}
