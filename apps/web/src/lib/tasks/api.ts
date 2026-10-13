/**
 * Authenticated API client for Stage 54 Personal Tasks.
 */

import {
  CreateTaskInput,
  Task,
  TaskCountsResponse,
  TaskListResponse,
  TaskStatusFilter,
  UpdateTaskInput,
} from "./types";

export interface TaskRequestOptions {
  token?: string | null;
  baseUrl?: string;
  signal?: AbortSignal;
}

function getBaseUrl(options?: TaskRequestOptions): string {
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

export async function listTasks(
  params?: {
    status?: TaskStatusFilter;
    limit?: number;
    cursor?: string | null;
  },
  options?: TaskRequestOptions
): Promise<TaskListResponse> {
  const baseUrl = getBaseUrl(options);
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.cursor) searchParams.set("cursor", params.cursor);

  const qs = searchParams.toString();
  const url = `${baseUrl}/api/v1/tasks${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  return handleResponse<TaskListResponse>(res, "Failed to list personal tasks");
}

export async function getTaskCounts(
  options?: TaskRequestOptions
): Promise<TaskCountsResponse> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/tasks/counts`;

  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
  });

  return handleResponse<TaskCountsResponse>(res, "Failed to fetch task counts");
}

export async function createTask(
  payload: CreateTaskInput,
  options?: TaskRequestOptions
): Promise<Task> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/tasks`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
    body: JSON.stringify(payload),
  });

  return handleResponse<Task>(res, "Failed to create personal task");
}

export async function updateTask(
  taskId: string,
  payload: UpdateTaskInput,
  options?: TaskRequestOptions
): Promise<Task> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/tasks/${taskId}`;

  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
    body: JSON.stringify(payload),
  });

  return handleResponse<Task>(res, "Failed to update personal task");
}

export async function completeTask(
  taskId: string,
  expectedVersion?: number,
  options?: TaskRequestOptions
): Promise<Task> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/tasks/${taskId}/complete`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
    body: JSON.stringify(expectedVersion != null ? { expected_version: expectedVersion } : {}),
  });

  return handleResponse<Task>(res, "Failed to complete personal task");
}

export async function reopenTask(
  taskId: string,
  expectedVersion?: number,
  options?: TaskRequestOptions
): Promise<Task> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/tasks/${taskId}/reopen`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
    body: JSON.stringify(expectedVersion != null ? { expected_version: expectedVersion } : {}),
  });

  return handleResponse<Task>(res, "Failed to reopen personal task");
}

export async function cancelTask(
  taskId: string,
  expectedVersion?: number,
  options?: TaskRequestOptions
): Promise<Task> {
  const baseUrl = getBaseUrl(options);
  const url = `${baseUrl}/api/v1/tasks/${taskId}/cancel`;

  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(options?.token),
    credentials: "include",
    signal: options?.signal,
    cache: "no-store",
    body: JSON.stringify(expectedVersion != null ? { expected_version: expectedVersion } : {}),
  });

  return handleResponse<Task>(res, "Failed to cancel personal task");
}
