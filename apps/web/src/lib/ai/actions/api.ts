/**
 * API client functions for ATLAS AI Financial Action Engine (Stage 128).
 */

import {
  ActionCapabilitiesResponse,
  ActionHistoryResponse,
  ActionPlanResponse,
  ExecuteActionPlanResponse,
  ExecutionReceiptDTO,
  UndoActionResponse,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errBody: any;
    try {
      errBody = await res.json();
    } catch {
      errBody = { message: res.statusText };
    }
    const error: any = new Error(errBody.detail?.message || errBody.message || "Request failed");
    error.status = res.status;
    error.code = errBody.detail?.code || errBody.code;
    error.details = errBody.detail?.details || errBody.details;
    throw error;
  }

  return res.json();
}

export async function getActionCapabilities(): Promise<ActionCapabilitiesResponse> {
  return fetchJson<ActionCapabilitiesResponse>("/api/v1/ai/actions/capabilities");
}

export async function createActionPlan(
  intent: string,
  conversationId?: string,
  contextHints?: Record<string, any>
): Promise<ActionPlanResponse> {
  return fetchJson<ActionPlanResponse>("/api/v1/ai/actions/plan", {
    method: "POST",
    body: JSON.stringify({
      intent,
      conversation_id: conversationId,
      context_hints: contextHints || {},
    }),
  });
}

export async function getActionPlan(planId: string): Promise<ActionPlanResponse> {
  return fetchJson<ActionPlanResponse>(`/api/v1/ai/actions/plans/${encodeURIComponent(planId)}`);
}

export async function approveAction(
  planId: string,
  actionId: string,
  previewHash: string,
  expectedResourceRevision: string
): Promise<{ approval_id: string; status: string }> {
  return fetchJson<{ approval_id: string; status: string }>(
    `/api/v1/ai/actions/plans/${encodeURIComponent(planId)}/approve`,
    {
      method: "POST",
      body: JSON.stringify({
        action_id: actionId,
        preview_hash: previewHash,
        expected_resource_revision: expectedResourceRevision,
      }),
    }
  );
}

export async function denyAction(
  planId: string,
  actionId: string,
  reason?: string
): Promise<{ action_id: string; status: string }> {
  return fetchJson<{ action_id: string; status: string }>(
    `/api/v1/ai/actions/plans/${encodeURIComponent(planId)}/deny`,
    {
      method: "POST",
      body: JSON.stringify({
        action_id: actionId,
        reason,
      }),
    }
  );
}

export async function executeActionPlan(
  planId: string,
  idempotencyKey: string
): Promise<ExecuteActionPlanResponse> {
  return fetchJson<ExecuteActionPlanResponse>(
    `/api/v1/ai/actions/plans/${encodeURIComponent(planId)}/execute`,
    {
      method: "POST",
      body: JSON.stringify({
        plan_id: planId,
        idempotency_key: idempotencyKey,
      }),
    }
  );
}

export async function getActionReceipt(receiptId: string): Promise<ExecutionReceiptDTO> {
  return fetchJson<ExecutionReceiptDTO>(
    `/api/v1/ai/actions/receipts/${encodeURIComponent(receiptId)}`
  );
}

export async function undoAction(
  actionId: string,
  receiptId: string
): Promise<UndoActionResponse> {
  return fetchJson<UndoActionResponse>(
    `/api/v1/ai/actions/actions/${encodeURIComponent(actionId)}/undo`,
    {
      method: "POST",
      body: JSON.stringify({
        action_id: actionId,
        receipt_id: receiptId,
      }),
    }
  );
}

export async function getActionHistory(): Promise<ActionHistoryResponse> {
  return fetchJson<ActionHistoryResponse>("/api/v1/ai/actions/history");
}

