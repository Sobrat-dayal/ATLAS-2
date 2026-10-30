"""Comprehensive verification test suite for Stage 123 Sandboxed Terminal Execution Platform.

Covers:
- Part LXXXII: Python Reference Tests (Arithmetic, List Sum, NumPy, Exceptions, Output Separation)
- Part LXXXIII: Python Isolation & Security (Environment scrubbing, Quotas, Timeout, Cancellation, User Isolation)
- Part LXXXIV: SQL Reference Tests (test_prices dataset query & AVG aggregation)
- Part LXXXV: SQL Security Tests (Allowlist SELECT, WITH SELECT, Deny INSERT/UPDATE/DELETE/DROP/Multi-statements)
- Part LXXXVI: CLI Reference Tests (atlas help, atlas version, atlas workspace list, unknown command, shell command)
- Part LXXXVIII: Execution Lifecycle & State Machine
- FastAPI API Endpoints Integration
"""

import threading
import time
from typing import Generator

import pytest
from atlas.auth import AuthPrincipal
from atlas.terminal.enums import TerminalType
from atlas.terminal.execution.domain import (
    ExecutionStatus,
    ResourceProfile,
)
from atlas.terminal.execution.errors import (
    TerminalCliCommandUnknownError,
    TerminalExecutionAccessDeniedError,
    TerminalExecutionInputTooLargeError,
    TerminalSqlStatementNotAllowedError,
)
from atlas.terminal.execution.python_sandbox import PythonSandboxRunner
from atlas.terminal.execution.service import TerminalExecutionService
from atlas.terminal.execution.sql_runner import SqlSandboxRunner, validate_sql_statement
from atlas.terminal.execution.state_machine import ExecutionStateMachine
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app

# ---------------- Fixtures ----------------


@pytest.fixture
def exec_service() -> TerminalExecutionService:
    return TerminalExecutionService.get_instance()


@pytest.fixture
def test_user_id() -> str:
    return "usr_quant_trader_123"


@pytest.fixture
def mock_python_session(exec_service: TerminalExecutionService, test_user_id: str) -> str:
    session = exec_service.repository.create_session(
        user_id=test_user_id,
        terminal_type=TerminalType.PYTHON,
        display_name="Python Quantitative Scratchpad",
    )
    return session.session_id


@pytest.fixture
def mock_sql_session(exec_service: TerminalExecutionService, test_user_id: str) -> str:
    session = exec_service.repository.create_session(
        user_id=test_user_id,
        terminal_type=TerminalType.SQL,
        display_name="SQL Analytics Console",
    )
    return session.session_id


@pytest.fixture
def mock_cli_session(exec_service: TerminalExecutionService, test_user_id: str) -> str:
    session = exec_service.repository.create_session(
        user_id=test_user_id,
        terminal_type=TerminalType.ATLAS_CLI,
        display_name="ATLAS CLI Console",
    )
    return session.session_id


@pytest.fixture
def client(test_user_id: str) -> Generator[TestClient, None, None]:
    principal = AuthPrincipal(
        sub=test_user_id,
        email="quant@institution.atlas",
        role="authenticated",
    )
    app.dependency_overrides[get_current_user] = lambda: principal
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ============================================================================
# PART LXXXII — PYTHON REFERENCE TESTS
# ============================================================================


def test_python_reference_basic_arithmetic():
    """Test 288: Basic Arithmetic print(2 + 2) -> 4."""
    runner = PythonSandboxRunner()
    res = runner.execute(
        execution_id="test_arithmetic",
        code="print(2 + 2)",
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.COMPLETED
    assert res["stdout"].strip() == "4"
    assert res["error_code"] is None


def test_python_reference_list_sum():
    """Test 289: List Sum values = [10, 20, 30, 40]; print(sum(values)) -> 100."""
    runner = PythonSandboxRunner()
    code = "values = [10, 20, 30, 40]\nprint(sum(values))"
    res = runner.execute(
        execution_id="test_list_sum",
        code=code,
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.COMPLETED
    assert res["stdout"].strip() == "100"


def test_python_reference_numpy_mean():
    """Test 290: NumPy import numpy as np; print(np.mean([1, 2, 3, 4])) -> 2.5."""
    runner = PythonSandboxRunner()
    code = "import numpy as np\nprint(np.mean([1, 2, 3, 4]))"
    res = runner.execute(
        execution_id="test_numpy",
        code=code,
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.COMPLETED
    assert res["stdout"].strip() == "2.5"


def test_python_reference_exception_reporting():
    """Test 291: Python Exception print(1 / 0) -> Execution Failed ZeroDivisionError."""
    runner = PythonSandboxRunner()
    code = "print(1 / 0)"
    res = runner.execute(
        execution_id="test_zero_div",
        code=code,
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.FAILED
    assert res["error_code"] == "ZeroDivisionError"
    assert "division by zero" in res["error_message"]
    assert "ZeroDivisionError" in res["stderr"]


def test_python_output_separation():
    """Test 292: Output separation between stdout and stderr channels."""
    runner = PythonSandboxRunner()
    code = "import sys\nsys.stdout.write('DATA_LINE\\n')\nsys.stderr.write('WARN_LINE\\n')"
    res = runner.execute(
        execution_id="test_sep",
        code=code,
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.COMPLETED
    assert "DATA_LINE" in res["stdout"]
    assert "WARN_LINE" in res["stderr"]


# ============================================================================
# PART LXXXIII — PYTHON ISOLATION & RESOURCE LIMITS
# ============================================================================


def test_python_isolation_environment_scrubbed():
    """Test 293: Verify sandbox environment variables do not leak platform secrets."""
    runner = PythonSandboxRunner()
    code = "import os\nprint('SUPABASE' in str(os.environ), 'DATABASE' in str(os.environ))"
    res = runner.execute(
        execution_id="test_env_isolation",
        code=code,
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.COMPLETED
    assert res["stdout"].strip() == "False False"


def test_python_input_size_quota_exceeded():
    """Verifies rejection of inputs exceeding maximum allowed size."""
    runner = PythonSandboxRunner(max_input_bytes=100)
    huge_code = "# " + "A" * 200
    with pytest.raises(TerminalExecutionInputTooLargeError):
        runner.execute(
            execution_id="test_quota",
            code=huge_code,
            resource_profile=ResourceProfile(timeout_seconds=5),
        )


def test_python_execution_timeout():
    """Verifies that infinite loops are forcefully terminated at timeout boundary."""
    runner = PythonSandboxRunner()
    infinite_loop = "import time\nwhile True:\n    time.sleep(0.01)"
    profile = ResourceProfile(timeout_seconds=1)
    res = runner.execute(
        execution_id="test_timeout",
        code=infinite_loop,
        resource_profile=profile,
    )
    assert res["status"] == ExecutionStatus.TIMED_OUT
    assert res["error_code"] == "TERMINAL_EXECUTION_TIMED_OUT"


def test_python_execution_cancellation():
    """Verifies that user cancellation event terminates the running subprocess."""
    runner = PythonSandboxRunner()
    code = "import time\ntime.sleep(5)"
    cancel_event = threading.Event()

    def trigger_cancel():
        time.sleep(0.1)
        cancel_event.set()

    t = threading.Thread(target=trigger_cancel)
    t.start()
    res = runner.execute(
        execution_id="test_cancel",
        code=code,
        resource_profile=ResourceProfile(timeout_seconds=10),
        cancellation_event=cancel_event,
    )
    t.join()
    assert res["status"] == ExecutionStatus.CANCELLED
    assert res["error_code"] == "TERMINAL_EXECUTION_CANCELLED"


# ============================================================================
# PART LXXXIV — SQL REFERENCE TESTS
# ============================================================================


def test_sql_reference_query_test_prices():
    """Test 294 & 295: SELECT instrument, price FROM test_prices ORDER BY instrument -> 3 rows."""
    runner = SqlSandboxRunner()
    sql = "SELECT instrument, price FROM test_prices ORDER BY instrument;"
    res = runner.execute(
        execution_id="test_sql_select",
        sql_text=sql,
        source_id="test_prices",
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.COMPLETED
    assert res["row_count"] == 3
    tabular = res["tabular_result"]
    assert tabular is not None
    assert len(tabular.rows) == 3
    assert tabular.rows[0]["instrument"] == "AAA"
    assert tabular.rows[0]["price"] == 100.0
    assert tabular.rows[1]["instrument"] == "BBB"
    assert tabular.rows[1]["price"] == 150.0
    assert tabular.rows[2]["instrument"] == "CCC"
    assert tabular.rows[2]["price"] == 200.0


def test_sql_reference_aggregation():
    """Test 296: SELECT AVG(price) AS average_price FROM test_prices -> average_price = 150."""
    runner = SqlSandboxRunner()
    sql = "SELECT AVG(price) AS average_price FROM test_prices;"
    res = runner.execute(
        execution_id="test_sql_avg",
        sql_text=sql,
        source_id="test_prices",
        resource_profile=ResourceProfile(timeout_seconds=5),
    )
    assert res["status"] == ExecutionStatus.COMPLETED
    tabular = res["tabular_result"]
    assert tabular is not None
    assert len(tabular.rows) == 1
    assert tabular.rows[0]["average_price"] == 150.0


# ============================================================================
# PART LXXXV — SQL SECURITY TESTS
# ============================================================================


def test_sql_security_allowlist_and_deny():
    """Test 298: Statement allowlist and mutation denial."""
    # 1. Valid SELECT is allowed
    assert validate_sql_statement("SELECT * FROM test_prices;")["valid"] is True
    # 2. Valid WITH ... SELECT is allowed
    assert (
        validate_sql_statement(
            "WITH high_p AS (SELECT * FROM test_prices WHERE price > 120) SELECT * FROM high_p;"
        )["valid"]
        is True
    )

    # 3. Prohibited mutations rejected
    forbidden = [
        "INSERT INTO test_prices VALUES ('DDD', 300);",
        "UPDATE test_prices SET price = 999 WHERE instrument = 'AAA';",
        "DELETE FROM test_prices WHERE instrument = 'AAA';",
        "DROP TABLE test_prices;",
        "ALTER TABLE test_prices ADD COLUMN val REAL;",
        "TRUNCATE TABLE test_prices;",
        "CREATE TABLE hack (id INT);",
        "GRANT ALL PRIVILEGES ON test_prices TO PUBLIC;",
        "SELECT * FROM test_prices; SELECT * FROM test_prices;",  # Multiple statements
        "SELECT * INTO new_table FROM test_prices;",
    ]
    for stmt in forbidden:
        with pytest.raises(TerminalSqlStatementNotAllowedError):
            validate_sql_statement(stmt)


# ============================================================================
# PART LXXXVI — CLI REFERENCE TESTS
# ============================================================================


def test_cli_reference_help(
    exec_service: TerminalExecutionService, mock_cli_session: str, test_user_id: str
):
    """Test 299: atlas help returns actual registered command help."""
    res = exec_service.submit_execution(
        user_id=test_user_id,
        session_id=mock_cli_session,
        input_code="atlas help",
    )
    assert res.status == ExecutionStatus.COMPLETED
    assert "Available Registered Commands" in res.stdout_summary
    assert "atlas workspace" in res.stdout_summary


def test_cli_reference_version(
    exec_service: TerminalExecutionService, mock_cli_session: str, test_user_id: str
):
    """Test 300: atlas version returns authoritative system metadata."""
    res = exec_service.submit_execution(
        user_id=test_user_id,
        session_id=mock_cli_session,
        input_code="atlas version",
    )
    assert res.status == ExecutionStatus.COMPLETED
    assert "ATLAS OS v2.4.0 (Stage 123" in res.stdout_summary


def test_cli_reference_workspace_list(
    exec_service: TerminalExecutionService, mock_cli_session: str, test_user_id: str
):
    """Test 301: atlas workspace list returns authorized workspaces."""
    res = exec_service.submit_execution(
        user_id=test_user_id,
        session_id=mock_cli_session,
        input_code="atlas workspace list",
    )
    assert res.status == ExecutionStatus.COMPLETED
    assert res.tabular_result is not None
    assert len(res.tabular_result.rows) >= 1
    assert "Macro Economic Strategy Desk" in res.stdout_summary


def test_cli_reference_unknown_command(
    exec_service: TerminalExecutionService, mock_cli_session: str, test_user_id: str
):
    """Test 302: atlas unknown-command returns TERMINAL_CLI_COMMAND_UNKNOWN."""
    with pytest.raises(TerminalCliCommandUnknownError):
        exec_service.submit_execution(
            user_id=test_user_id,
            session_id=mock_cli_session,
            input_code="atlas unknown-command",
        )


def test_cli_reference_shell_command_rejected(
    exec_service: TerminalExecutionService, mock_cli_session: str, test_user_id: str
):
    """Test 303: rm -rf / is strictly rejected and never forwarded to host shell."""
    with pytest.raises(TerminalCliCommandUnknownError):
        exec_service.submit_execution(
            user_id=test_user_id,
            session_id=mock_cli_session,
            input_code="rm -rf /",
        )


# ============================================================================
# PART LXXXVIII — EXECUTION LIFECYCLE & STATE MACHINE
# ============================================================================


def test_state_machine_legal_and_illegal_transitions():
    """Test 305: Valid transitions succeed, illegal and terminal transitions are rejected."""
    # Legal
    assert ExecutionStateMachine.can_transition(ExecutionStatus.CREATED, ExecutionStatus.QUEUED)
    assert ExecutionStateMachine.can_transition(ExecutionStatus.QUEUED, ExecutionStatus.RUNNING)
    assert ExecutionStateMachine.can_transition(ExecutionStatus.RUNNING, ExecutionStatus.COMPLETED)

    # Illegal
    assert not ExecutionStateMachine.can_transition(
        ExecutionStatus.CREATED, ExecutionStatus.COMPLETED
    )
    # Terminal state lock
    assert ExecutionStateMachine.is_terminal(ExecutionStatus.COMPLETED)
    assert not ExecutionStateMachine.can_transition(
        ExecutionStatus.COMPLETED, ExecutionStatus.RUNNING
    )


def test_user_isolation(
    exec_service: TerminalExecutionService, mock_python_session: str, test_user_id: str
):
    """Verifies User B cannot access or cancel User A's execution."""
    res = exec_service.submit_execution(
        user_id=test_user_id,
        session_id=mock_python_session,
        input_code="print('User A secret calculation')",
    )

    other_user = "usr_adversary_999"
    with pytest.raises(TerminalExecutionAccessDeniedError):
        exec_service.get_execution(res.execution_id, other_user)

    with pytest.raises(TerminalExecutionAccessDeniedError):
        exec_service.cancel_execution(res.execution_id, other_user)


# ============================================================================
# FASTAPI ENDPOINTS INTEGRATION TESTS
# ============================================================================


def test_fastapi_execution_endpoints(client: TestClient, mock_python_session: str):
    """Test HTTP API lifecycle for submission, detail, output, and capabilities."""
    # 1. Capabilities
    r_cap = client.get("/api/v1/terminal/execution-capabilities")
    assert r_cap.status_code == 200
    caps = r_cap.json()
    assert len(caps) >= 3

    # 2. Python Environments
    r_env = client.get("/api/v1/terminal/python/environments")
    assert r_env.status_code == 200
    envs = r_env.json()
    assert len(envs) >= 1
    assert envs[0]["environment_id"] == "env_python_standard"

    # 3. SQL Sources & Validation
    r_src = client.get("/api/v1/terminal/sql/sources")
    assert r_src.status_code == 200
    sources = r_src.json()
    assert any(s["source_id"] == "test_prices" for s in sources)

    r_val = client.post(
        "/api/v1/terminal/sql/validate",
        json={"sql_text": "SELECT instrument, price FROM test_prices;"},
    )
    assert r_val.status_code == 200
    assert r_val.json()["valid"] is True

    # 4. CLI Commands
    r_cli = client.get("/api/v1/terminal/cli/commands")
    assert r_cli.status_code == 200
    assert len(r_cli.json()) >= 5

    # 5. Submit Execution
    payload = {
        "session_id": mock_python_session,
        "input_code": "print(40 + 2)",
        "execution_type": "PYTHON",
    }
    r_exec = client.post("/api/v1/terminal/executions", json=payload)
    assert r_exec.status_code == 201
    data = r_exec.json()
    exec_id = data["execution_id"]
    assert data["status"] == "COMPLETED"
    assert data["stdout_summary"].strip() == "42"

    # 6. Retrieve Execution Detail
    r_detail = client.get(f"/api/v1/terminal/executions/{exec_id}")
    assert r_detail.status_code == 200
    assert r_detail.json()["execution_id"] == exec_id

    # 7. Retrieve Status
    r_status = client.get(f"/api/v1/terminal/executions/{exec_id}/status")
    assert r_status.status_code == 200
    assert r_status.json()["status"] == "COMPLETED"

    # 8. Retrieve Output Chunks
    r_out = client.get(f"/api/v1/terminal/executions/{exec_id}/output")
    assert r_out.status_code == 200
    chunks = r_out.json()
    assert len(chunks) >= 1
    assert "42" in chunks[0]["payload"]
