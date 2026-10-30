/**
 * Domain types for ATLAS Stage 122: Integrated Terminal Shell.
 */

export type TerminalType =
  | "ATLAS_CLI"
  | "PYTHON"
  | "SQL"
  | "LOGS"
  | "AGENTS"
  | "MCP";

export type SessionLifecycle = "ACTIVE" | "MINIMIZED" | "CLOSED" | "ARCHIVED";

export type ConnectionState =
  | "NOT_CONFIGURED"
  | "CONFIGURED"
  | "CONNECTING"
  | "CONNECTED"
  | "DISCONNECTED"
  | "ERROR"
  | "ACCESS_RESTRICTED";

export type ExecutionCapability = "DISABLED" | "SANDBOX_REQUIRED" | "PERMITTED";

export type SessionStatus =
  | "INITIALIZING"
  | "READY"
  | "INPUT_ONLY"
  | "READ_ONLY"
  | "EXECUTION_UNAVAILABLE"
  | "CONNECTING"
  | "CONNECTED"
  | "DISCONNECTED"
  | "ERROR"
  | "CLOSED";

export type OutputRecordType =
  | "SYSTEM_MESSAGE"
  | "LOCAL_INPUT"
  | "HELP_TEXT"
  | "STATUS_MESSAGE"
  | "READ_ONLY_LOG"
  | "ERROR"
  | "WARNING"
  | "EXECUTION_RESULT";

export type LogSeverity = "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";

export type TerminalCursorStyle = "BLOCK" | "LINE" | "UNDERLINE";

export interface TerminalSession {
  session_id: string;
  owner_user_id: string;
  terminal_type: TerminalType;
  display_name: string;
  lifecycle: SessionLifecycle;
  connection_state: ConnectionState;
  execution_capability: ExecutionCapability;
  status: SessionStatus;
  session_order: number;
  workspace_id?: string | null;
  configuration_schema_version: number;
  version: number;
  draft_content: string;
  scrollback_limit: number;
  created_at: string;
  updated_at: string;
  last_active_at: string;
  closed_at?: string | null;
}

export interface TerminalUserPreferences {
  user_id: string;
  font_size: number;
  font_family: string;
  line_height: number;
  scrollback_limit: number;
  cursor_style: TerminalCursorStyle;
  word_wrap: boolean;
  terminal_height: number;
  default_tab_type: TerminalType;
  restore_previous_tabs: boolean;
  timestamp_display: boolean;
  updated_at: string;
}

export interface TerminalOutputRecord {
  output_id: string;
  session_id: string;
  record_type: OutputRecordType;
  content: string;
  content_format?: "text/plain" | "text/ansi" | "application/json";
  severity?: LogSeverity;
  source: string;
  created_at: string;
  source_reference?: Record<string, unknown>;
}

export interface LogEntry {
  log_id: string;
  timestamp: string;
  level: LogSeverity;
  service: string;
  message: string;
  metadata?: Record<string, unknown>;
}

export interface AgentStatusRecord {
  agent_id: string;
  display_name: string;
  state: string;
  last_activity_at?: string | null;
  source: string;
  permission_scope: string;
}

export interface McpConnectionRecord {
  server_id: string;
  display_name: string;
  status: ConnectionState;
  available_tools_count: number;
  resources_count: number;
  last_checked_at?: string | null;
  configured_in: string;
}

export interface TerminalCapability {
  terminal_type: TerminalType;
  display_label: string;
  description: string;
  icon_name: string;
  supports_multiline: boolean;
  supports_draft_persistence: boolean;
  supports_real_read_data: boolean;
  supports_arbitrary_execution: boolean;
  execution_status_notice: string;
  stage_122_status: string;
}

export interface CliCommandHelp {
  command: string;
  syntax: string;
  summary: string;
  example: string;
  category: string;
}
