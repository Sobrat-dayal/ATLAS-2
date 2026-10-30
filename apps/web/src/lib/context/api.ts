/**
 * Typed API Client for ATLAS Stage 121: Global Workspace Linking.
 */

import {
  ChannelState,
  ContextDimension,
  ContextScope,
  ContextSelectionEvent,
  LinkChannel,
  LinkSubscription,
  PanelContextCapability,
  ResolvedEntity,
  SubscriptionMode,
  TransformationType,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}/api/v1/context${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json() as Promise<T>;
}

export async function listChannels(
  workspaceId?: string,
  scope?: ContextScope
): Promise<LinkChannel[]> {
  const params = new URLSearchParams();
  if (workspaceId) params.append("workspace_id", workspaceId);
  if (scope) params.append("scope", scope);
  const q = params.toString() ? `?${params.toString()}` : "";
  return request<LinkChannel[]>(`/channels${q}`);
}

export async function createChannel(data: {
  name: string;
  display_color_token?: string;
  workspace_id?: string;
  scope?: ContextScope;
  supported_dimensions?: ContextDimension[];
  initial_context?: Record<string, unknown>;
}): Promise<LinkChannel> {
  return request<LinkChannel>("/channels", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getChannel(channelId: string): Promise<LinkChannel> {
  return request<LinkChannel>(`/channels/${channelId}`);
}

export async function updateChannel(
  channelId: string,
  data: {
    name?: string;
    display_color_token?: string;
    scope?: ContextScope;
    enabled?: boolean;
    supported_dimensions?: ContextDimension[];
  }
): Promise<LinkChannel> {
  return request<LinkChannel>(`/channels/${channelId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteChannel(channelId: string): Promise<void> {
  return request<void>(`/channels/${channelId}`, {
    method: "DELETE",
  });
}

export async function listChannelMemberships(channelId: string): Promise<LinkSubscription[]> {
  return request<LinkSubscription[]>(`/channels/${channelId}/memberships`);
}

export async function addChannelMembership(
  channelId: string,
  data: {
    panel_instance_id: string;
    mode?: SubscriptionMode;
    inbound_dimensions?: ContextDimension[];
    outbound_dimensions?: ContextDimension[];
    priority_policy?: string;
  }
): Promise<LinkSubscription> {
  return request<LinkSubscription>(`/channels/${channelId}/memberships`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateMembership(
  subscriptionId: string,
  data: {
    mode?: SubscriptionMode;
    inbound_dimensions?: ContextDimension[];
    outbound_dimensions?: ContextDimension[];
    active?: boolean;
  }
): Promise<LinkSubscription> {
  return request<LinkSubscription>(`/memberships/${subscriptionId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function removeMembership(subscriptionId: string): Promise<void> {
  return request<void>(`/memberships/${subscriptionId}`, {
    method: "DELETE",
  });
}

export async function getChannelState(channelId: string): Promise<ChannelState> {
  return request<ChannelState>(`/channels/${channelId}/state`);
}

export async function updateChannelState(
  channelId: string,
  contextUpdates: Record<string, unknown>,
  expectedRevision?: number
): Promise<LinkChannel> {
  return request<LinkChannel>(`/channels/${channelId}/state`, {
    method: "PUT",
    body: JSON.stringify({
      context_updates: contextUpdates,
      expected_revision: expectedRevision,
    }),
  });
}

export async function resolveEntity(
  query: string,
  entityType: string = "INSTRUMENT",
  targetTransformation?: TransformationType
): Promise<ResolvedEntity> {
  return request<ResolvedEntity>("/resolve", {
    method: "POST",
    body: JSON.stringify({
      query,
      entity_type: entityType,
      target_transformation: targetTransformation,
    }),
  });
}

export async function getCapabilities(panelTypeId?: string): Promise<PanelContextCapability[]> {
  const q = panelTypeId ? `?panel_type_id=${panelTypeId}` : "";
  return request<PanelContextCapability[]>(`/capabilities${q}`);
}

export async function dispatchEvent(event: Partial<ContextSelectionEvent>): Promise<{
  status: string;
  event_id: string;
  channel_id: string;
  revision: number;
  delivered_count: number;
  delivered_panel_ids: string[];
}> {
  return request<{
    status: string;
    event_id: string;
    channel_id: string;
    revision: number;
    delivered_count: number;
    delivered_panel_ids: string[];
  }>("/events", {
    method: "POST",
    body: JSON.stringify(event),
  });
}
