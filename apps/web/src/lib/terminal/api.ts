/**
 * Typed client API for Stage 122 Terminal HTTP endpoints.
 */

import {
  AgentStatusRecord,
  CliCommandHelp,
  LogEntry,
  McpConnectionRecord,
  TerminalCapability,
  TerminalSession,
  TerminalType,
  TerminalUserPreferences,
} from "./types";

const API_BASE = "/api/v1/terminal";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errorDetail = `Terminal API Error: ${res.statusText}`;
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}

export async function fetchTerminalCapabilities(): Promise<{
  stage: number;
  stage_title: string;
  consoles: Record<string, TerminalCapability>;
  stage_123_contracts: Record<string, unknown>;
}> {
  return request("/capabilities");
}

export async function fetchCliHelp(command?: string): Promise<CliCommandHelp[]> {
  const query = command ? `?command=${encodeURIComponent(command)}` : "";
  return request(`/cli/help${query}`);
}

export async function fetchTerminalSessions(workspaceId?: string): Promise<TerminalSession[]> {
  const query = workspaceId ? `?workspace_id=${encodeURIComponent(workspaceId)}` : "";
  return request(`/sessions${query}`);
}

export async function createTerminalSession(payload: {
  terminal_type: TerminalType;
  display_name?: string;
  workspace_id?: string | null;
  initial_draft?: string;
}): Promise<TerminalSession> {
  return request("/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateTerminalSession(
  sessionId: string,
  payload: {
    display_name?: string;
    draft_content?: string;
    scrollback_limit?: number;
    expected_version?: number;
  }
): Promise<TerminalSession> {
  return request(`/sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function closeTerminalSession(sessionId: string): Promise<void> {
  return request(`/sessions/${sessionId}`, {
    method: "DELETE",
  });
}

export async function reorderTerminalSessions(sessionIds: string[]): Promise<TerminalSession[]> {
  return request("/sessions/order", {
    method: "PATCH",
    body: JSON.stringify({ session_ids: sessionIds }),
  });
}

export async function fetchTerminalPreferences(): Promise<TerminalUserPreferences> {
  return request("/preferences");
}

export async function updateTerminalPreferences(
  payload: Partial<TerminalUserPreferences>
): Promise<TerminalUserPreferences> {
  return request("/preferences", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function fetchTerminalLogs(params?: {
  severity?: string;
  service?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<LogEntry[]> {
  const q = new URLSearchParams();
  if (params?.severity) q.set("severity", params.severity);
  if (params?.service) q.set("service", params.service);
  if (params?.search) q.set("search", params.search);
  if (params?.limit) q.set("limit", String(params.limit));
  if (params?.offset) q.set("offset", String(params.offset));

  const queryStr = q.toString() ? `?${q.toString()}` : "";
  return request(`/logs${queryStr}`);
}

export async function fetchAgentStatuses(): Promise<AgentStatusRecord[]> {
  return request("/agents/status");
}

export async function fetchMcpConnections(): Promise<McpConnectionRecord[]> {
  return request("/mcp/connections");
}

