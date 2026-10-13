/**
 * Authenticated API client for Stage 54 Approval Requests and Decisions.
 *
 * NOTE: Approvals are created exclusively by trusted backend producers.
 * There is NO public create approval API endpoint.
 */

import {
  ApprovalCountsResponse,
  ApprovalDecisionInput,
  ApprovalDecisionResponse,
  ApprovalDetail,
  ApprovalListResponse,
  ApprovalStatusFilter,
} from "./types";

export interface ApprovalRequestOptions {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}

function getBaseUrl(options?: ApprovalRequestOptions): string {
  if (options?.baseUrl) return options.baseUrl;
  return process.env.NEXT_PUBLIC_API_URL || "";
}

function getHeaders(token?: string | null): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(res: Response, fallbackMessage: string): Promise<T> {
  if (!res.ok) {
    let errorMessage = `${fallbackMessage} (${res.status})`;
    try {
      const errJson = await res.json();
      if (errJson?.detail) {
        errorMessage = typeof errJson.detail === "string" ? errJson.detail : JSON.stringify(errJson.detail);
      } else if (errJson?.error?.message) {
        errorMessage = errJson.error.message;
      }
    } catch {
      // fallback
    }
    throw new Error(errorMessage);
  }
  return res.json() as Promise<T>;
}

export async function listApprovals(
  params?: {
    status?: ApprovalStatusFilter;
    limit?: number;
    cursor?: string | null;
  },
  options?: ApprovalRequestOptions
): Promise<ApprovalListResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.cursor) searchParams.set("cursor", params.cursor);

  const qs = searchParams.toString();
  const url = `${baseUrl}/api/v1/approvals${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  return handleResponse<ApprovalListResponse>(res, "Failed to list approval requests");
}

export async function getApprovalCounts(
  options?: ApprovalRequestOptions
): Promise<ApprovalCountsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/approvals/counts`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  return handleResponse<ApprovalCountsResponse>(res, "Failed to fetch approval counts");
}

export async function getApprovalDetail(
  approvalId: string,
  options?: ApprovalRequestOptions
): Promise<ApprovalDetail> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/approvals/${approvalId}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  return handleResponse<ApprovalDetail>(res, "Failed to fetch approval details");
}

export async function decideApproval(
  approvalId: string,
  payload: ApprovalDecisionInput,
  options?: ApprovalRequestOptions
): Promise<ApprovalDecisionResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/approvals/${approvalId}/decision`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
    body: JSON.stringify(payload),
  });

  return handleResponse<ApprovalDecisionResponse>(res, "Failed to record approval decision");
}
