/**
 * Frontend API client for Stage 49 Persistent Notifications.
 */

import {
  MarkAllReadResponse,
  NotificationItem,
  NotificationListFilter,
  NotificationListResponse,
  UnreadCountResponse,
} from "./types";

export interface RequestOptions {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}

function getBaseUrl(options?: RequestOptions): string {
  if (options?.baseUrl) return options.baseUrl;
  return process.env.NEXT_PUBLIC_API_URL || "";
}

function getHeaders(token?: string | null): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function listNotifications(
  params?: {
    filter?: NotificationListFilter;
    limit?: number;
    cursor?: string | null;
  },
  options?: RequestOptions
): Promise<NotificationListResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();
  if (params?.filter) {
    searchParams.set("filter", params.filter);
  }
  if (params?.limit) {
    searchParams.set("limit", String(params.limit));
  }
  if (params?.cursor) {
    searchParams.set("cursor", params.cursor);
  }

  const qs = searchParams.toString();
  const url = `${baseUrl}/api/v1/notifications${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to list notifications: HTTP ${res.status}`);
  }

  return (await res.json()) as NotificationListResponse;
}

export async function getUnreadNotificationCount(
  options?: RequestOptions
): Promise<UnreadCountResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/notifications/unread-count`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch unread notification count: HTTP ${res.status}`);
  }

  return (await res.json()) as UnreadCountResponse;
}

export async function markNotificationRead(
  notificationId: string,
  options?: RequestOptions
): Promise<NotificationItem> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/notifications/${notificationId}/read`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to mark notification as read: HTTP ${res.status}`);
  }

  return (await res.json()) as NotificationItem;
}

export async function markNotificationUnread(
  notificationId: string,
  options?: RequestOptions
): Promise<NotificationItem> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/notifications/${notificationId}/unread`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to mark notification as unread: HTTP ${res.status}`);
  }

  return (await res.json()) as NotificationItem;
}

export async function markAllNotificationsRead(
  options?: RequestOptions
): Promise<MarkAllReadResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/notifications/read-all`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to mark all notifications as read: HTTP ${res.status}`);
  }

  return (await res.json()) as MarkAllReadResponse;
}

export async function archiveNotification(
  notificationId: string,
  options?: RequestOptions
): Promise<NotificationItem> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/notifications/${notificationId}/archive`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
  });

  if (!res.ok) {
    throw new Error(`Failed to archive notification: HTTP ${res.status}`);
  }

  return (await res.json()) as NotificationItem;
}
