/**
 * TypeScript type definitions for Stage 124 AI Assistant V1 and AppShell Overlay.
 */

export type MessageRole = "user" | "assistant" | "system";

export type MessageStatus =
  | "PENDING"
  | "STREAMING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export type GenerationStatus =
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface RouteContext {
  route: string;
  module_name: string;
  summary: string;
}

export interface ModelCapability {
  model_id: string;
  name: string;
  provider: string;
  description: string;
  context_window: number;
  supports_streaming: boolean;
  cost_per_1k_input: number;
  cost_per_1k_output: number;
  is_default: boolean;
}

export interface AiMessage {
  message_id: string;
  conversation_id: string;
  owner_user_id: string;
  tenant_id?: string | null;
  role: MessageRole;
  content: string;
  status: MessageStatus;
  route_context?: RouteContext | null;
  token_count: number;
  generation_run_id?: string | null;
  error_code?: string | null;
  error_message?: string | null;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AiConversation {
  conversation_id: string;
  owner_user_id: string;
  tenant_id?: string | null;
  title: string;
  model_id: string;
  provider: string;
  system_prompt_override?: string | null;
  is_archived: boolean;
  is_pinned: boolean;
  pinned_at?: string | null;
  message_count: number;
  total_tokens: number;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  last_message_at?: string | null;
}

export interface AiGenerationRun {
  generation_id: string;
  conversation_id: string;
  user_message_id: string;
  assistant_message_id?: string | null;
  status: GenerationStatus;
  model_id: string;
  provider: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  duration_ms?: number | null;
  error_code?: string | null;
  error_message?: string | null;
  created_at: string;
  finished_at?: string | null;
}

export interface AiUserPreferences {
  preference_id: string;
  owner_user_id: string;
  tenant_id?: string | null;
  default_model_id: string;
  temperature: number;
  send_on_enter: boolean;
  sound_enabled: boolean;
  overlay_dock_side: "right" | "left";
  overlay_width_px: number;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface StreamEvent {
  event_type: "run_started" | "delta" | "run_completed" | "run_cancelled" | "error";
  data: Record<string, unknown>;
}

