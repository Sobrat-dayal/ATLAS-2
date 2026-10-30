/**
 * Domain types for ATLAS Stage 123: Sandboxed Terminal Execution Platform.
 */

export type ExecutionType = "PYTHON" | "SQL" | "ATLAS_CLI";

export type ExecutionStatus =
  | "CREATED"
  | "VALIDATING"
  | "QUEUED"
  | "PREPARING"
  | "STARTING"
  | "RUNNING"
  | "STREAMING"
  | "COMPLETED"
  | "FAILED"
  | "CANCEL_REQUESTED"
  | "CANCELLED"
  | "TIMED_OUT"
  | "RESOURCE_LIMIT_EXCEEDED"
  | "SECURITY_DENIED"
  | "INFRASTRUCTURE_FAILED";

export type StreamOutputType =
  | "stdout"
  | "stderr"
  | "tabular"
  | "artifact"
  | "error"
  | "system";

export type CommandMutabilityClass =
  | "READ_ONLY"
  | "COMPUTATIONAL"
  | "MUTATING"
  | "PRIVILEGED";

export interface ResourceProfile {
  profile_id: string;
  name: string;
  cpu_cores: number;
  memory_mb: number;
  timeout_seconds: number;
  max_output_bytes: number;
  max_rows: number;
}

export interface TabularColumn {
  name: string;
  data_type: string;
}

export interface TabularResult {
  columns: TabularColumn[];
  rows: Record<string, any>[];
  total_rows: number;
  truncated: boolean;
  as_of?: string | null;
}

export interface ExecutionArtifact {
  artifact_id: string;
  execution_id: string;
  name: string;
  mime_type: string;
  byte_size: number;
  storage_path: string;
  created_at: string;
}

export interface ExecutionOutputChunk {
  execution_id: string;
  seq_num: number;
  stream_type: StreamOutputType;
  payload: string;
  timestamp: string;
}

export interface TerminalExecutionDetail {
  execution_id: string;
  owner_user_id: string;
  tenant_id?: string | null;
  terminal_session_id: string;
  execution_type: ExecutionType;
  status: ExecutionStatus;
  state_revision: number;
  input_code: string;
  environment_id?: string | null;
  source_id?: string | null;
  duration_ms?: number | null;
  error_code?: string | null;
  error_message?: string | null;
  row_count?: number | null;
  stdout_summary?: string | null;
  tabular_result?: TabularResult | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface ExecutionStatusResponse {
  execution_id: string;
  status: ExecutionStatus;
  state_revision: number;
  duration_ms?: number | null;
  error_code?: string | null;
  error_message?: string | null;
}

export interface ExecutionSubmitRequest {
  session_id: string;
  input_code: string;
  execution_type?: ExecutionType;
  environment_id?: string;
  source_id?: string;
  workspace_id?: string;
  idempotency_key?: string;
  timeout_seconds?: number;
}

export interface PythonEnvironment {
  environment_id: string;
  name: string;
  version: string;
  python_version: string;
  packages: Record<string, string>;
  is_default: boolean;
  resource_profiles: string[];
}

export interface SqlSource {
  source_id: string;
  display_name: string;
  source_type: string;
  allowed_schemas: string[];
  allowed_views: string[];
  is_read_only: boolean;
  default_row_limit: number;
  timeout_seconds: number;
  description: string;
}

export interface SqlValidateResponse {
  valid: boolean;
  statement_type: string;
  clean_statement: string;
  error?: string | null;
}

export interface CliCommandDef {
  command_id: string;
  namespace: string;
  name: string;
  description: string;
  usage: string;
  arguments_schema: Record<string, any>[];
  examples: string[];
  mutability_class: CommandMutabilityClass;
}
