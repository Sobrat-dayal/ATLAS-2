/**
 * Typed client API for Stage 124 AI Assistant V1.
 */

import {
  AiConversation,
  AiGenerationRun,
  AiMessage,
  AiUserPreferences,
  ModelCapability,
  RouteContext,
} from "./types";

const API_BASE = "/api/v1/ai";

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
      // Fallback to text
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// ---------------- Conversations ----------------

export async function createConversation(
  title?: string,
  modelId?: string,
  systemPromptOverride?: string
): Promise<AiConversation> {
  return request<AiConversation>("/conversations", {
    method: "POST",
    body: JSON.stringify({
      title: title || "New Conversation",
      model_id: modelId,
      system_prompt_override: systemPromptOverride,
    }),
  });
}

export async function listConversations(
  search?: string,
  isArchived = false,
  limit = 50,
  offset = 0
): Promise<{ items: AiConversation[]; total: number }> {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  params.set("archived", String(isArchived));
  params.set("limit", String(limit));
  params.set("offset", String(offset));

  return request<{ items: AiConversation[]; total: number }>(
    `/conversations?${params.toString()}`
  );
}

export async function getConversation(conversationId: string): Promise<AiConversation> {
  return request<AiConversation>(`/conversations/${conversationId}`);
}

export async function updateConversation(
  conversationId: string,
  updates: {
    title?: string;
    is_archived?: boolean;
    is_pinned?: boolean;
    model_id?: string;
  }
): Promise<AiConversation> {
  return request<AiConversation>(`/conversations/${conversationId}`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
}

export async function deleteConversation(conversationId: string): Promise<void> {
  return request<void>(`/conversations/${conversationId}`, {
    method: "DELETE",
  });
}

// ---------------- Messages ----------------

export async function listMessages(
  conversationId: string,
  limit = 100,
  offset = 0
): Promise<{ items: AiMessage[]; total: number }> {
  return request<{ items: AiMessage[]; total: number }>(
    `/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`
  );
}

export async function sendMessage(
  conversationId: string,
  content: string,
  routeContext?: RouteContext | null
): Promise<{ message: AiMessage; generation_id: string }> {
  return request<{ message: AiMessage; generation_id: string }>(
    `/conversations/${conversationId}/messages`,
    {
      method: "POST",
      body: JSON.stringify({
        content,
        route_context: routeContext,
      }),
    }
  );
}

export async function regenerateMessage(
  conversationId: string,
  targetMessageId?: string
): Promise<{ message: AiMessage; generation_id: string }> {
  return request<{ message: AiMessage; generation_id: string }>(
    `/conversations/${conversationId}/regenerate`,
    {
      method: "POST",
      body: JSON.stringify({
        target_message_id: targetMessageId,
      }),
    }
  );
}

// ---------------- Generations & SSE Streaming ----------------

export async function getGeneration(generationId: string): Promise<AiGenerationRun> {
  return request<AiGenerationRun>(`/generations/${generationId}`);
}

export async function cancelGeneration(generationId: string): Promise<{ cancelled: boolean }> {
  return request<{ cancelled: boolean }>(`/generations/${generationId}/cancel`, {
    method: "POST",
  });
}

export interface StreamEventHandlers {
  onRunStarted?: (data: Record<string, unknown>) => void;
  onDelta?: (delta: string) => void;
  onRunCompleted?: (data: Record<string, unknown>) => void;
  onRunCancelled?: (data: Record<string, unknown>) => void;
  onError?: (err: { error_code?: string; message?: string }) => void;
}

export function streamAiGeneration(
  generationId: string,
  handlers: StreamEventHandlers
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/generations/${generationId}/stream`, {
        signal: controller.signal,
        headers: {
          Accept: "text/event-stream",
        },
      });

      if (!response.ok) {
        handlers.onError?.({
          error_code: "HTTP_ERROR",
          message: `Stream failed with status ${response.status}`,
        });
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        handlers.onError?.({
          error_code: "NO_STREAM_BODY",
          message: "No readable response body available for streaming.",
        });
        return;
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const lines = part.split("\n");
          let currentEvent = "";
          let dataStr = "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              currentEvent = line.slice(7).trim();
            } else if (line.startsWith("data: ")) {
              dataStr = line.slice(6).trim();
            }
          }

          if (dataStr) {
            try {
              const data = JSON.parse(dataStr);
              switch (currentEvent) {
                case "run_started":
                  handlers.onRunStarted?.(data);
                  break;
                case "delta":
                  if (data.delta) {
                    handlers.onDelta?.(data.delta);
                  }
                  break;
                case "run_completed":
                  handlers.onRunCompleted?.(data);
                  break;
                case "run_cancelled":
                  handlers.onRunCancelled?.(data);
                  break;
                case "error":
                  handlers.onError?.(data);
                  break;
              }
            } catch {
              // Ignore partial JSON parse errors
            }
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        // Normal client abort
        return;
      }
      handlers.onError?.({
        error_code: "STREAM_EXCEPTION",
        message: err instanceof Error ? err.message : String(err),
      });
    }
  })();

  return controller;
}

// ---------------- Models & Preferences ----------------

export async function listModels(): Promise<{ models: ModelCapability[] }> {
  return request<{ models: ModelCapability[] }>("/models");
}

export async function getPreferences(): Promise<AiUserPreferences> {
  return request<AiUserPreferences>("/preferences");
}

export async function updatePreferences(
  updates: Partial<AiUserPreferences>
): Promise<AiUserPreferences> {
  return request<AiUserPreferences>("/preferences", {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

