/**
 * Stage 123 Preparatory Execution Contracts.
 *
 * NOTE: These contracts define future interfaces for Stage 123 (Sandboxed Terminal Execution).
 * Stage 122 does NOT implement command execution.
 */

import { TerminalType } from "./types";

export interface ExecutionCapabilityDefinition {
  capability_id: string;
  terminal_type: TerminalType;
  supported: boolean;
  enabled: boolean;
  requires_sandbox: boolean;
  required_permissions: string[];
  resource_limits_reference: string;
  execution_api_version: string;
}

export interface ExecutionRequestSchemaContract {
  request_id: string;
  session_id: string;
  terminal_type: TerminalType;
  execution_capability_id: string;
  payload: string;
  workspace_context_reference?: Record<string, unknown>;
  expected_environment_reference?: string;
  idempotency_key?: string;
}

export interface ExecutionStatusContract {
  execution_id: string;
  session_id: string;
  status: "QUEUED" | "STARTING" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED" | "TIMED_OUT";
  started_at?: string;
  completed_at?: string;
  exit_status?: number;
  resource_usage?: {
    cpu_time_ms?: number;
    peak_memory_bytes?: number;
    output_line_count?: number;
  };
  error_code?: string;
}

export interface ExecutionOutputStreamingContract {
  event_id: string;
  execution_id: string;
  session_id: string;
  stream_type: "stdout" | "stderr" | "system";
  sequence_number: number;
  content: string;
  timestamp: string;
}

export interface CancellationContract {
  execution_id: string;
  session_id: string;
  requested_by_user_id: string;
  cancellation_reason: string;
  timestamp: string;
}

