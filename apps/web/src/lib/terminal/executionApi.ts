/**
 * API client for Stage 123 Sandboxed Terminal Execution Platform.
 */

import type {
  CliCommandDef,
  ExecutionOutputChunk,
  ExecutionStatusResponse,
  ExecutionSubmitRequest,
  PythonEnvironment,
  SqlSource,
  SqlValidateResponse,
  TerminalExecutionDetail,
} from "./executionTypes";

const API_BASE = "/api/v1/terminal";

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errData: any = {};
    try {
      errData = await res.json();
    } catch {
      errData = { message: res.statusText };
    }
    const message =
      errData?.detail?.message ||
      errData?.detail ||
      errData?.error ||
      `Execution API request failed: ${res.status}`;
    const error = new Error(message);
    (error as any).code = errData?.detail?.code || errData?.code || "TERMINAL_EXECUTION_ERROR";
    (error as any).status = res.status;
    throw error;
  }

  return res.json();
}

export const executionApi = {
  /** Submit code or command for sandboxed execution */
  async submitExecution(req: ExecutionSubmitRequest): Promise<TerminalExecutionDetail> {
    return request<TerminalExecutionDetail>("/executions", {
      method: "POST",
      body: JSON.stringify(req),
    });
  },

  /** Retrieve complete execution record */
  async getExecution(executionId: string): Promise<TerminalExecutionDetail> {
    return request<TerminalExecutionDetail>(`/executions/${executionId}`);
  },

  /** Fast polling endpoint for status transitions */
  async getExecutionStatus(executionId: string): Promise<ExecutionStatusResponse> {
    return request<ExecutionStatusResponse>(`/executions/${executionId}/status`);
  },

  /** Retrieve ordered bounded output chunks */
  async getExecutionOutput(executionId: string): Promise<ExecutionOutputChunk[]> {
    return request<ExecutionOutputChunk[]>(`/executions/${executionId}/output`);
  },

  /** Cancel active execution */
  async cancelExecution(executionId: string): Promise<TerminalExecutionDetail> {
    return request<TerminalExecutionDetail>(`/executions/${executionId}/cancel`, {
      method: "POST",
    });
  },

  /** Query user execution history */
  async listExecutions(params?: {
    session_id?: string;
    execution_type?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<TerminalExecutionDetail[]> {
    const q = new URLSearchParams();
    if (params?.session_id) q.set("session_id", params.session_id);
    if (params?.execution_type) q.set("execution_type", params.execution_type);
    if (params?.status) q.set("status", params.status);
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.offset) q.set("offset", String(params.offset));
    const qs = q.toString();
    return request<TerminalExecutionDetail[]>(`/executions${qs ? `?${qs}` : ""}`);
  },

  /** List operational execution capabilities */
  async getCapabilities(): Promise<any[]> {
    return request<any[]>("/execution-capabilities");
  },

  /** List approved Python runtimes */
  async getPythonEnvironments(): Promise<PythonEnvironment[]> {
    return request<PythonEnvironment[]>("/python/environments");
  },

  /** List authorized analytical SQL sources */
  async getSqlSources(): Promise<SqlSource[]> {
    return request<SqlSource[]>("/sql/sources");
  },

  /** Validate SQL syntax and statement allowlist */
  async validateSql(sqlText: string): Promise<SqlValidateResponse> {
    return request<SqlValidateResponse>("/sql/validate", {
      method: "POST",
      body: JSON.stringify({ sql_text: sqlText }),
    });
  },

  /** List approved registered ATLAS CLI commands */
  async getCliCommands(): Promise<CliCommandDef[]> {
    return request<CliCommandDef[]>("/cli/commands");
  },
};
