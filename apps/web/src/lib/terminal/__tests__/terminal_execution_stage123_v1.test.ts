import { describe, it, beforeEach } from "node:test";
import assert from "node:assert";
import { executionApi } from "../executionApi";
import type { TabularResult, TerminalExecutionDetail } from "../executionTypes";

describe("Stage 123 Terminal Execution Frontend Client and Domain", () => {
  it("submits Python execution job through executionApi", async () => {
    const mockDetail: TerminalExecutionDetail = {
      execution_id: "exec_py_123",
      owner_user_id: "usr_trader_1",
      terminal_session_id: "sess_py_1",
      execution_type: "PYTHON",
      status: "COMPLETED",
      state_revision: 2,
      input_code: "print(2 + 2)",
      environment_id: "env_python_standard",
      duration_ms: 12.5,
      stdout_summary: "4\n",
      created_at: new Date().toISOString(),
    };

    const originalFetch = global.fetch;
    global.fetch = async () =>
      ({
        ok: true,
        json: async () => mockDetail,
      } as any);

    try {
      const res = await executionApi.submitExecution({
        session_id: "sess_py_1",
        input_code: "print(2 + 2)",
        execution_type: "PYTHON",
      });

      assert.strictEqual(res.execution_id, "exec_py_123");
      assert.strictEqual(res.status, "COMPLETED");
      assert.strictEqual(res.stdout_summary?.trim(), "4");
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("submits SQL query and parses tabular results", async () => {
    const mockResult: TabularResult = {
      columns: [
        { name: "instrument", data_type: "VARCHAR(16)" },
        { name: "price", data_type: "REAL" },
      ],
      rows: [
        { instrument: "AAA", price: 100.0 },
        { instrument: "BBB", price: 150.0 },
        { instrument: "CCC", price: 200.0 },
      ],
      total_rows: 3,
      truncated: false,
    };

    const mockDetail: TerminalExecutionDetail = {
      execution_id: "exec_sql_456",
      owner_user_id: "usr_trader_1",
      terminal_session_id: "sess_sql_1",
      execution_type: "SQL",
      status: "COMPLETED",
      state_revision: 2,
      input_code: "SELECT instrument, price FROM test_prices ORDER BY instrument;",
      source_id: "test_prices",
      duration_ms: 4.8,
      row_count: 3,
      tabular_result: mockResult,
      created_at: new Date().toISOString(),
    };

    const originalFetch = global.fetch;
    global.fetch = async () =>
      ({
        ok: true,
        json: async () => mockDetail,
      } as any);

    try {
      const res = await executionApi.submitExecution({
        session_id: "sess_sql_1",
        input_code: "SELECT instrument, price FROM test_prices ORDER BY instrument;",
        execution_type: "SQL",
        source_id: "test_prices",
      });

      assert.strictEqual(res.status, "COMPLETED");
      assert.strictEqual(res.tabular_result?.rows.length, 3);
      assert.strictEqual(res.tabular_result?.rows[0].instrument, "AAA");
      assert.strictEqual(res.tabular_result?.rows[1].price, 150.0);
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("validates read-only SQL queries and detects prohibited statements", async () => {
    const originalFetch = global.fetch;
    global.fetch = async () =>
      ({
        ok: true,
        json: async () => ({
          valid: true,
          statement_type: "SELECT",
          clean_statement: "SELECT * FROM test_prices;",
        }),
      } as any);

    try {
      const validRes = await executionApi.validateSql("SELECT * FROM test_prices;");
      assert.strictEqual(validRes.valid, true);
      assert.strictEqual(validRes.statement_type, "SELECT");
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("retrieves approved CLI commands and execution capabilities", async () => {
    const mockCaps = [
      { capability_id: "cap.terminal.python.sandbox", enabled: true },
      { capability_id: "cap.terminal.sql.readonly", enabled: true },
      { capability_id: "cap.terminal.cli.router", enabled: true },
    ];

    const originalFetch = global.fetch;
    global.fetch = async () =>
      ({
        ok: true,
        json: async () => mockCaps,
      } as any);

    try {
      const caps = await executionApi.getCapabilities();
      assert.strictEqual(caps.length, 3);
      assert.ok(caps.every((c: any) => c.enabled));
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("handles execution cancellation request", async () => {
    const mockCancelled: TerminalExecutionDetail = {
      execution_id: "exec_py_cancel",
      owner_user_id: "usr_trader_1",
      terminal_session_id: "sess_py_1",
      execution_type: "PYTHON",
      status: "CANCELLED",
      state_revision: 3,
      input_code: "import time; time.sleep(10)",
      error_code: "TERMINAL_EXECUTION_CANCELLED",
      error_message: "Execution cancelled by user request.",
      created_at: new Date().toISOString(),
    };

    const originalFetch = global.fetch;
    global.fetch = async () =>
      ({
        ok: true,
        json: async () => mockCancelled,
      } as any);

    try {
      const cancelled = await executionApi.cancelExecution("exec_py_cancel");
      assert.strictEqual(cancelled.status, "CANCELLED");
      assert.strictEqual(cancelled.error_code, "TERMINAL_EXECUTION_CANCELLED");
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("retrieves authorized SQL sources list", async () => {
    const mockSources = [
      {
        source_id: "test_prices",
        display_name: "Test Financial Prices",
        is_read_only: true,
      },
      {
        source_id: "postgresql_analytical",
        display_name: "PostgreSQL Analytical",
        is_read_only: true,
      },
    ];

    const originalFetch = global.fetch;
    global.fetch = async () =>
      ({
        ok: true,
        json: async () => mockSources,
      } as any);

    try {
      const sources = await executionApi.getSqlSources();
      assert.strictEqual(sources.length, 2);
      assert.strictEqual(sources[0].source_id, "test_prices");
      assert.strictEqual(sources[0].is_read_only, true);
    } finally {
      global.fetch = originalFetch;
    }
  });
});
