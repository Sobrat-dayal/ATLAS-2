/**
 * REST API Client for Saved Chart Layouts (Stage 74).
 *
 * Implements:
 * - GET /api/v1/charts/layouts
 * - POST /api/v1/charts/layouts
 * - GET /api/v1/charts/layouts/{id}
 * - PUT /api/v1/charts/layouts/{id} (with If-Match ETag header)
 * - PATCH /api/v1/charts/layouts/{id}
 * - POST /api/v1/charts/layouts/{id}/duplicate
 * - DELETE /api/v1/charts/layouts/{id}
 * - GET /api/v1/charts/layouts/{id}/export
 */

import {
  LayoutExportEnvelope,
  SavedChartLayoutDocumentV1,
  SavedLayoutDetail,
  SavedLayoutSummary,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "";
}

function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
  };
  return headers;
}

export class LayoutApiError extends Error {
  public status: number;
  public details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "LayoutApiError";
    this.status = status;
    this.details = details;
  }
}

export class LayoutConflictApiError extends LayoutApiError {
  constructor(message: string, status: number) {
    super(message, status);
    this.name = "LayoutConflictApiError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 204) {
    return true as unknown as T;
  }

  let json: any = null;
  try {
    json = await res.json();
  } catch {
    // Response had no JSON body
  }

  if (!res.ok) {
    const errorMsg =
      json?.error?.message ||
      json?.detail ||
      `Request failed with status ${res.status}`;

    if (res.status === 412 || res.status === 409) {
      throw new LayoutConflictApiError(errorMsg, res.status);
    }
    throw new LayoutApiError(errorMsg, res.status, json);
  }

  return json as T;
}

export async function fetchSavedLayouts(
  page: number = 1,
  pageSize: number = 50,
  search?: string
): Promise<{ items: SavedLayoutSummary[]; total: number }> {
  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  if (search) params.set("search", search);

  const url = `${getBaseApiUrl()}/api/v1/charts/layouts?${params.toString()}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return handleResponse<{ items: SavedLayoutSummary[]; total: number }>(res);
}

export async function fetchSavedLayout(id: string): Promise<SavedLayoutDetail> {
  const url = `${getBaseApiUrl()}/api/v1/charts/layouts/${id}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return handleResponse<SavedLayoutDetail>(res);
}

export async function createSavedLayout(payload: {
  name: string;
  description?: string;
  document: SavedChartLayoutDocumentV1;
  is_default?: boolean;
}): Promise<SavedLayoutDetail> {
  const url = `${getBaseApiUrl()}/api/v1/charts/layouts`;
  const res = await fetch(url, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  return handleResponse<SavedLayoutDetail>(res);
}

export async function updateSavedLayout(
  id: string,
  payload: {
    document: SavedChartLayoutDocumentV1;
    expected_revision: number;
  }
): Promise<SavedLayoutDetail> {
  const url = `${getBaseApiUrl()}/api/v1/charts/layouts/${id}`;
  const headers = getAuthHeaders();
  headers["If-Match"] = `W/"${payload.expected_revision}"`;

  const res = await fetch(url, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload),
  });

  return handleResponse<SavedLayoutDetail>(res);
}

export async function patchSavedLayoutMetadata(
  id: string,
  payload: {
    name?: string;
    description?: string;
    is_default?: boolean;
  }
): Promise<SavedLayoutDetail> {
  const url = `${getBaseApiUrl()}/api/v1/charts/layouts/${id}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  return handleResponse<SavedLayoutDetail>(res);
}

export async function duplicateSavedLayout(
  id: string,
  newName?: string
): Promise<SavedLayoutDetail> {
  const url = `${getBaseApiUrl()}/api/v1/charts/layouts/${id}/duplicate`;
  const res = await fetch(url, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ new_name: newName || null }),
  });

  return handleResponse<SavedLayoutDetail>(res);
}

export async function deleteSavedLayout(id: string): Promise<boolean> {
  const url = `${getBaseApiUrl()}/api/v1/charts/layouts/${id}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  return handleResponse<boolean>(res);
}

export async function exportSavedLayout(id: string): Promise<LayoutExportEnvelope> {
  const url = `${getBaseApiUrl()}/api/v1/charts/layouts/${id}/export`;
  const res = await fetch(url, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  return handleResponse<LayoutExportEnvelope>(res);
}
