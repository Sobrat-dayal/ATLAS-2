/**
 * TypeScript Type Definitions for Stage 126: ATLAS AI Tool Gateway.
 */

export type AiToolCategory =
  | 'DISCOVERY'
  | 'DATA_READ'
  | 'ANALYTICAL_READ'
  | 'STATUS_READ'
  | 'COMPUTATIONAL'
  | 'USER_STATE_MUTATION'
  | 'FINANCIAL_MUTATION'
  | 'EXTERNAL_SIDE_EFFECT'
  | 'PRIVILEGED_OPERATION';

export type AiToolCallStatus =
  | 'PROPOSED'
  | 'VALIDATING'
  | 'AUTHORIZING'
  | 'APPROVAL_REQUIRED'
  | 'APPROVED'
  | 'DENIED'
  | 'QUEUED'
  | 'RUNNING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCEL_REQUESTED'
  | 'CANCELLED'
  | 'TIMED_OUT'
  | 'REJECTED';

export type AiApprovalClass =
  | 'NO_APPROVAL_REQUIRED'
  | 'USER_CONFIRMATION_REQUIRED'
  | 'STEP_UP_AUTH_REQUIRED'
  | 'ADMIN_APPROVAL_REQUIRED'
  | 'PROHIBITED';

export type AiApprovalStatus = 'PENDING' | 'APPROVED' | 'DENIED' | 'EXPIRED';

export interface AiToolDescriptor {
  tool_id: string;
  version: string;
  category: AiToolCategory;
  name: string;
  description: string;
  capability_scope: string;
  approval_class: AiApprovalClass;
  provider_disclosure_policy: 'ALLOWED' | 'REDACTED' | 'PROHIBITED';
  parameters_schema: Record<string, unknown>;
  returns_schema: Record<string, unknown>;
  lifecycle_status: 'REGISTERED' | 'ENABLED' | 'DISABLED' | 'DEPRECATED' | 'UNAVAILABLE';
  timeout_seconds: number;
  rate_limit_per_minute: number;
}

export interface AiToolSourceManifest {
  tool_id: string;
  data_source: string;
  as_of: string;
  attribution: string;
  record_count: number;
}

export interface AiToolResult {
  tool_call_id: string;
  tool_id: string;
  success: boolean;
  data: unknown;
  source_manifest?: AiToolSourceManifest | null;
  execution_time_ms: number;
  as_of: string;
  error_code?: string | null;
  error_message?: string | null;
  truncated?: boolean;
  content_hash?: string;
}

export interface AiToolCall {
  id: string;
  tool_id: string;
  tool_version: string;
  status: AiToolCallStatus;
  arguments: Record<string, unknown>;
  normalized_arguments_hash: string;
  result?: unknown;
  error_code?: string | null;
  error_message?: string | null;
  execution_time_ms?: number | null;
  approval_class: AiApprovalClass;
  approval_request_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AiToolApprovalRequest {
  id: string;
  tool_call_id: string;
  user_id: string;
  tool_id: string;
  approval_class: AiApprovalClass;
  normalized_arguments_hash: string;
  arguments_summary: Record<string, unknown>;
  status: AiApprovalStatus;
  expires_at: string;
  consumed_at?: string | null;
  decision_reason?: string | null;
  created_at: string;
}

export interface AiToolPreferences {
  user_id: string;
  enabled_tools: string[];
  disabled_tools: string[];
  auto_approve_read_only: boolean;
  require_approval_for_sensitive: boolean;
  updated_at: string;
}

export interface AiToolExecuteRequest {
  tool_id: string;
  arguments: Record<string, unknown>;
  generation_run_id?: string;
  conversation_id?: string;
  approval_request_id?: string;
}

