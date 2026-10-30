/**
 * Client API for Stage 126: ATLAS AI Tool Gateway.
 */

import {
  AiToolApprovalRequest,
  AiToolCall,
  AiToolDescriptor,
  AiToolExecuteRequest,
  AiToolPreferences,
  AiToolResult,
} from "./types";

const API_BASE = "/api/v1/ai/tools";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // Use fallback errorDetail
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Lists all registered AI tools.
 */
export async function fetchAiTools(
  category?: string,
  includeDisabled: boolean = false
): Promise<AiToolDescriptor[]> {
  const params = new URLSearchParams();
  if (category) params.append("category", category);
  if (includeDisabled) params.append("include_disabled", "true");
  const query = params.toString() ? `?${params.toString()}` : "";
  const res = await request<{ tools: AiToolDescriptor[]; total: number }>(`/${query}`);
  return res.tools;
}

/**
 * Retrieves details for a specific tool.
 */
export async function fetchAiTool(toolId: string): Promise<AiToolDescriptor> {
  return request<AiToolDescriptor>(`/${encodeURIComponent(toolId)}`);
}

/**
 * Lists recent tool calls.
 */
export async function fetchAiToolCalls(limit: number = 50): Promise<AiToolCall[]> {
  const res = await request<{ calls: AiToolCall[]; total: number }>(`/calls?limit=${limit}`);
  return res.calls;
}

/**
 * Retrieves details of a specific tool call.
 */
export async function fetchAiToolCall(callId: string): Promise<AiToolCall> {
  return request<AiToolCall>(`/calls/${encodeURIComponent(callId)}`);
}

/**
 * Dispatches an authorized tool call directly.
 */
export async function executeAiTool(payload: AiToolExecuteRequest): Promise<AiToolResult> {
  return request<AiToolResult>("/execute", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Retrieves tool preferences for the authenticated user.
 */
export async function fetchAiToolPreferences(): Promise<AiToolPreferences> {
  return request<AiToolPreferences>("/preferences");
}

/**
 * Updates tool preferences for the authenticated user.
 */
export async function updateAiToolPreferences(
  updates: Partial<AiToolPreferences>
): Promise<AiToolPreferences> {
  return request<AiToolPreferences>("/preferences", {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

/**
 * Retrieves an approval request by ID.
 */
export async function fetchAiToolApproval(approvalId: string): Promise<AiToolApprovalRequest> {
  return request<AiToolApprovalRequest>(`/approvals/${encodeURIComponent(approvalId)}`);
}

/**
 * Approves a pending tool call request.
 */
export async function approveAiToolCall(
  approvalId: string,
  decisionReason?: string
): Promise<AiToolApprovalRequest> {
  return request<AiToolApprovalRequest>(`/approvals/${encodeURIComponent(approvalId)}/approve`, {
    method: "POST",
    body: JSON.stringify({ decision_reason: decisionReason }),
  });
}

/**
 * Denies a pending tool call request.
 */
export async function denyAiToolCall(
  approvalId: string,
  decisionReason?: string
): Promise<AiToolApprovalRequest> {
  return request<AiToolApprovalRequest>(`/approvals/${encodeURIComponent(approvalId)}/deny`, {
    method: "POST",
    body: JSON.stringify({ decision_reason: decisionReason }),
  });
}

