/**
 * Client API for Stage 125: ATLAS AI Context Awareness Engine.
 */

import {
  AiContextCapability,
  AiContextEnvelope,
  AiContextPreferences,
  AiContextPreviewRequest,
  AiContextSourceManifest,
  ContextItem,
  ContextType,
  UpdateAiContextPreferencesRequest,
} from "./types";

const API_BASE = "/api/v1/ai/context";

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
      if (errJson.detail) {
        if (typeof errJson.detail === "string") {
          errorDetail = errJson.detail;
        } else if (errJson.detail.message) {
          errorDetail = errJson.detail.message;
        }
      }
    } catch {
      // Fallback
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function fetchContextCapabilities(): Promise<AiContextCapability[]> {
  return request<AiContextCapability[]>("/capabilities");
}

export async function fetchContextPreferences(): Promise<AiContextPreferences> {
  return request<AiContextPreferences>("/preferences");
}

export async function updateContextPreferences(
  payload: UpdateAiContextPreferencesRequest
): Promise<AiContextPreferences> {
  return request<AiContextPreferences>("/preferences", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function fetchContextPreview(
  payload: AiContextPreviewRequest
): Promise<AiContextEnvelope> {
  return request<AiContextEnvelope>("/preview", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function resolveContextItem(
  contextType: ContextType,
  targetId: string,
  parameters?: Record<string, unknown>
): Promise<{ item: ContextItem }> {
  return request<{ item: ContextItem }>("/resolve", {
    method: "POST",
    body: JSON.stringify({
      context_type: contextType,
      target_id: targetId,
      parameters: parameters || {},
    }),
  });
}

export async function fetchContextManifest(
  generationId: string
): Promise<AiContextSourceManifest> {
  return request<AiContextSourceManifest>(`/manifests/${generationId}`);
}

