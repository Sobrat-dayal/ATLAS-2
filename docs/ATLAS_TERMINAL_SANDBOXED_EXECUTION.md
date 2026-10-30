# ATLAS Stage 123: Sandboxed Terminal Execution Platform

## 1. Executive Summary

Stage 123 implements the **Institutional-Grade Sandboxed Terminal Execution Platform** for ATLAS. Building upon the Stage 122 multi-session developer shell, Stage 123 delivers isolated, permission-controlled, bounded runtime execution for:
1. **Python Quantitative Computing**: Subprocess-isolated sandbox with complete platform secret redaction, ephemeral working directories, strict compute quotas, execution timeouts, and pinned library support (NumPy, math, statistics).
2. **Permission-Controlled SQL Query Engine**: Analytical read-only execution with defense-in-depth statement allowlisting (SELECT and WITH ... SELECT only), rejecting all destructive mutations, multiple statements, and privileged functions, backed by isolated in-memory test fixtures (`test_prices`) and analytical views.
3. **Approved ATLAS CLI Command Router**: Pure application-level command router (`atlas help`, `atlas version`, `atlas status`, `atlas workspace list`, `atlas context show`, `atlas instrument inspect`, `atlas portfolio list`, `atlas risk models`, `atlas data sources`), strictly disallowing shell commands (`rm -rf /`) and rejecting unknown inputs with `TERMINAL_CLI_COMMAND_UNKNOWN`.

---

## 2. Trust Boundaries and Isolation Architecture

```
+--------------------------------------------------------------------------+
|                     ATLAS Web UI (Next.js / React)                       |
|           Bottom Drawer: PythonConsole, SqlConsole, AtlasCliConsole       |
+--------------------------------------------------------------------------+
                                     │  (HTTPS POST /api/v1/terminal/executions)
                                     ▼
+--------------------------------------------------------------------------+
|                 ATLAS API Gateway (FastAPI / AuthPrincipal)              |
|   RLS Verification, Tenant Isolation, Quota Enforcement, Session Checks   |
+--------------------------------------------------------------------------+
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
+---------------------+   +---------------------+   +---------------------+
|   Python Sandbox    |   |     SQL Engine      |   |   ATLAS CLI Router  |
|  Unprivileged Child |   |  Read-Only Allowed  |   |  Registered Command |
|  Scrubbed Env Vars  |   |  AST & Engine Guard |   |  No Host Shell      |
|  Ephemeral TempDir  |   |  test_prices Fixture|   |  Deterministic Out  |
+---------------------+   +---------------------+   +---------------------+
```

### 2.1 Python Sandbox Isolation
- **Process Isolation**: Code runs in a dedicated child subprocess (`sys.executable -B -s`) in an ephemeral directory (`tempfile.mkdtemp`).
- **Environment Variable Scrubbing**: All sensitive keys matching `TOKEN`, `KEY`, `SECRET`, `PASS`, `DATABASE`, `SUPABASE`, `AUTH`, `DB` are stripped prior to execution.
- **Resource Constraints**: Default 1 core, 512MB RAM, 10s execution timeout (max 30s), 64KB max output.
- **Path Redaction**: Absolute host filesystem paths in Python tracebacks are normalized to `/sandbox/main.py`.
- **Ephemeral Cleanup**: Temporary directory and all generated files are unlinked in a guaranteed `finally` block.

### 2.2 SQL Permission Controls
- **Statement Allowlist**: Only `SELECT` and `WITH ... SELECT` queries are permitted.
- **Prohibited Operations**: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `MERGE`, `GRANT`, `REVOKE`, `COPY`, `CALL`, `DO`, `EXEC`, multiple statements, and destructive CTEs are rejected with `TERMINAL_SQL_STATEMENT_NOT_ALLOWED`.
- **Engine-Level Authorizer**: SQLite in-memory instance enforces `SQLITE_SELECT`, `SQLITE_READ`, and `SQLITE_FUNCTION` (action 31) only; all other operations receive `SQLITE_DENY`.
- **Reference Fixture**: `test_prices` table (`AAA` 100, `BBB` 150, `CCC` 200) verified with standard queries and aggregation (`AVG(price) = 150`).

### 2.3 Approved ATLAS CLI Router
- **Command Whitelist**: No unrestricted shell commands (`rm -rf /`, `dir`, `ls`, `sh`, `bash`) are ever forwarded to an OS shell.
- **Strict Error Code**: Unrecognized or shell commands return `TERMINAL_CLI_COMMAND_UNKNOWN`.
- **Registered Operations**:
  - `atlas help [cmd]`: Syntax and examples.
  - `atlas version`: Authoritative version metadata (ATLAS OS v2.4.0, Stage 123).
  - `atlas status` / `atlas system status`: System diagnostics, kernel health, and context bus.
  - `atlas workspace list`: Authorized workspace desks.
  - `atlas context show`: Global linking channels (A-D) and active entity.
  - `atlas instrument inspect <sym>`: Master financial instrument metadata.
  - `atlas portfolio list`: Authorized portfolio holdings.
  - `atlas risk models`: Institutional risk factor models.
  - `atlas data sources`: Analytical data feeds.

---

## 3. Execution Lifecycle & State Machine

Execution statuses progress monotonically through legal transitions:
1. `CREATED`: Initial submission.
2. `QUEUED`: Enqueued in scheduler, subject to per-user concurrency quotas (max 2 concurrent).
3. `RUNNING`: Dispatched to sandboxed worker runner.
4. `STREAMING`: Emitting bounded output chunks.
5. **Terminal Outcomes**:
   - `COMPLETED`: Clean exit with stdout/tabular results.
   - `FAILED`: Uncaught exception or syntax error.
   - `CANCELLED`: Interrupted via user cancellation token.
   - `TIMED_OUT`: Hard timeout reached.
   - `SECURITY_DENIED`: Rejected by sandbox security policy or engine authorizer.

---

## 4. REST API Specification

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/terminal/executions` | Submit code, query, or command for execution |
| `GET` | `/api/v1/terminal/executions/{id}` | Retrieve execution details, status, and summary |
| `GET` | `/api/v1/terminal/executions/{id}/status` | Fast status polling endpoint |
| `GET` | `/api/v1/terminal/executions/{id}/output` | Retrieve bounded, ordered streaming output chunks |
| `POST` | `/api/v1/terminal/executions/{id}/cancel` | Request graceful cancellation of active execution |
| `GET` | `/api/v1/terminal/executions` | User execution history with pagination & filters |
| `GET` | `/api/v1/terminal/execution-capabilities` | Live operational execution capabilities |
| `GET` | `/api/v1/terminal/python/environments` | Approved Python sandbox environments manifest |
| `GET` | `/api/v1/terminal/python/resource-profiles` | Compute and memory resource profiles |
| `GET` | `/api/v1/terminal/sql/sources` | Authorized analytical SQL sources |
| `GET` | `/api/v1/terminal/sql/sources/{id}/schema` | Approved schema views and columns |
| `POST` | `/api/v1/terminal/sql/validate` | Pre-flight SQL allowlist validation |
| `GET` | `/api/v1/terminal/cli/commands` | Registered approved CLI commands catalog |
| `GET` | `/api/v1/terminal/cli/commands/{id}` | Detailed command schema and usage |

---

## 5. Verification Matrix

- **Backend Pytest Suite (`apps/api/tests/test_terminal_execution_stage123_v1.py`)**: 20/20 passed in 14.03s.
- **Backend Stage 122 Regression (`apps/api/tests/test_terminal_stage122_v1.py`)**: 13/13 passed.
- **Frontend Unit Tests (`src/lib/terminal/__tests__/terminal_execution_stage123_v1.test.ts`)**: 6/6 passed.
- **Frontend Full Test Suite (`apps/web`)**: 217/217 passed across 13 suites.
- **Linting & Formatting (`ruff check`, `ruff format`)**: 100% clean across all modules.
- **Next.js Production Build**: 38/38 routes compiled without errors.

