"""Unit and integration test suite for Stage 122: Integrated ATLAS Terminal Shell."""

import pytest
from atlas.auth import AuthPrincipal
from atlas.terminal.enums import (
    ConnectionState,
    ExecutionCapability,
    LogSeverity,
    SessionLifecycle,
    SessionStatus,
    TerminalCursorStyle,
    TerminalType,
)
from atlas.terminal.errors import (
    TerminalDraftTooLargeError,
    TerminalExecutionUnavailableError,
    TerminalSessionAccessDeniedError,
    TerminalSessionLimitExceededError,
    TerminalSessionVersionConflictError,
)
from atlas.terminal.repository import TerminalRepository
from atlas.terminal.service import TerminalService
from fastapi.testclient import TestClient

from atlas_api.main import app


@pytest.fixture
def repo():
    return TerminalRepository()


@pytest.fixture
def service(repo):
    return TerminalService(repository=repo)


def test_terminal_capabilities_catalog(service):
    """Verifies that all 6 principal console types exist and execution is disabled."""
    caps = service.get_capabilities()
    assert caps["stage"] == 122
    assert "consoles" in caps
    consoles = caps["consoles"]

    expected_types = ["ATLAS_CLI", "PYTHON", "SQL", "LOGS", "AGENTS", "MCP"]
    for t in expected_types:
        assert t in consoles
        c = consoles[t]
        assert c.supports_arbitrary_execution is False
        assert (
            "Stage 123" in c.execution_status_notice
            or "not applicable" in c.execution_status_notice
            or "disabled" in c.execution_status_notice
        )

    contracts = caps["stage_123_contracts"]
    assert "Stage 123" in contracts["execution_milestone"]
    for cap_def in contracts["capabilities"]:
        assert cap_def.supported is False
        assert cap_def.enabled is False
        assert cap_def.requires_sandbox is True


def test_cli_command_help(service):
    """Verifies static CLI help definitions for registered commands."""
    all_help = service.get_cli_command_help()
    assert len(all_help) >= 6
    commands = [h["command"] for h in all_help]
    assert "help" in commands
    assert "status" in commands
    assert "version" in commands
    assert "workspace" in commands
    assert "context" in commands

    single = service.get_cli_command_help("markets")
    assert len(single) == 1
    assert single[0]["command"] == "markets"


def test_default_sessions_initialization(service):
    """Verifies default 4 institutional tabs created for new users in correct order."""
    user_id = "usr_analyst_122_1"
    sessions = service.list_sessions(user_id=user_id)
    assert len(sessions) == 4

    types = [s.terminal_type for s in sessions]
    assert types == [
        TerminalType.ATLAS_CLI,
        TerminalType.PYTHON,
        TerminalType.SQL,
        TerminalType.LOGS,
    ]

    assert sessions[0].status == SessionStatus.READY
    assert sessions[1].status == SessionStatus.INPUT_ONLY
    assert sessions[2].status == SessionStatus.INPUT_ONLY
    assert sessions[3].status == SessionStatus.READ_ONLY

    for s in sessions:
        assert s.execution_capability == ExecutionCapability.DISABLED
        assert s.lifecycle == SessionLifecycle.ACTIVE
        assert s.connection_state == ConnectionState.CONNECTED


def test_session_lifecycle_crud(service):
    """Tests creating, fetching, updating, reordering, and closing sessions."""
    user_id = "usr_trader_122_crud"
    new_sess = service.create_session(
        user_id=user_id,
        terminal_type=TerminalType.PYTHON,
        display_name="Quantitative Notebook 2",
        initial_draft="import numpy as np\n",
    )
    assert new_sess.display_name == "Quantitative Notebook 2"
    assert new_sess.draft_content == "import numpy as np\n"
    assert new_sess.session_order == 4  # Appended after defaults 0, 1, 2, 3

    fetched = service.get_session(new_sess.session_id, user_id)
    assert fetched.session_id == new_sess.session_id

    updated = service.update_session(
        session_id=new_sess.session_id,
        user_id=user_id,
        display_name="Alpha Model Python",
        draft_content="import numpy as np\nimport scipy\n",
        expected_version=1,
    )
    assert updated.display_name == "Alpha Model Python"
    assert updated.version == 2
    assert "scipy" in updated.draft_content

    # Reorder
    all_sessions = service.list_sessions(user_id)
    reversed_ids = [s.session_id for s in reversed(all_sessions)]
    reordered = service.reorder_sessions(user_id, reversed_ids)
    assert [s.session_id for s in reordered] == reversed_ids

    # Close
    closed = service.close_session(new_sess.session_id, user_id)
    assert closed is True

    remaining = service.list_sessions(user_id)
    assert len(remaining) == 4
    assert new_sess.session_id not in [s.session_id for s in remaining]


def test_session_draft_size_limit(service):
    """Verifies that oversized drafts exceeding 64KB are rejected."""
    user_id = "usr_trader_large_draft"
    oversized = "A" * 70000
    with pytest.raises(TerminalDraftTooLargeError):
        service.create_session(
            user_id=user_id,
            terminal_type=TerminalType.PYTHON,
            initial_draft=oversized,
        )


def test_session_limit_exceeded(service):
    """Verifies maximum session capacity constraint (32 tabs)."""
    user_id = "usr_power_terminal"
    # Seed defaults (4)
    service.list_sessions(user_id)
    # Add 28 more sessions to reach 32
    for i in range(28):
        service.create_session(user_id, TerminalType.ATLAS_CLI, display_name=f"CLI {i}")

    # 33rd session must fail
    with pytest.raises(TerminalSessionLimitExceededError):
        service.create_session(user_id, TerminalType.ATLAS_CLI, display_name="Overflow CLI")


def test_optimistic_concurrency_control(service):
    """Verifies 409 conflict when expected version does not match."""
    user_id = "usr_concurrent_editor"
    sess = service.create_session(user_id, TerminalType.SQL, display_name="Queries")
    assert sess.version == 1

    # First update increments to version 2
    service.update_session(sess.session_id, user_id, draft_content="SELECT 1;", expected_version=1)

    # Stale update with version 1 must raise conflict
    with pytest.raises(TerminalSessionVersionConflictError):
        service.update_session(
            sess.session_id, user_id, draft_content="SELECT 2;", expected_version=1
        )


def test_session_user_isolation(service):
    """Verifies that User A cannot read or mutate User B's sessions."""
    user_a = "usr_alice_122"
    user_b = "usr_bob_122"

    sess_a = service.create_session(user_a, TerminalType.PYTHON, display_name="Alice Scratchpad")

    with pytest.raises(TerminalSessionAccessDeniedError):
        service.get_session(sess_a.session_id, user_b)

    with pytest.raises(TerminalSessionAccessDeniedError):
        service.update_session(sess_a.session_id, user_b, display_name="Hacked Title")

    with pytest.raises(TerminalSessionAccessDeniedError):
        service.close_session(sess_a.session_id, user_b)


def test_preferences_lifecycle(service):
    """Verifies terminal preferences loading and updating."""
    user_id = "usr_prefs_trader"
    pref = service.get_preferences(user_id)
    assert pref.font_size == 12
    assert pref.terminal_height == 320
    assert pref.cursor_style == TerminalCursorStyle.BLOCK

    updated = service.update_preferences(
        user_id=user_id,
        font_size=14,
        terminal_height=420,
        cursor_style=TerminalCursorStyle.LINE,
        word_wrap=False,
    )
    assert updated.font_size == 14
    assert updated.terminal_height == 420
    assert updated.cursor_style == TerminalCursorStyle.LINE
    assert updated.word_wrap is False


def test_log_diagnostics_sanitization(service):
    """Verifies secret redaction and filtering in the read-only Logs feed."""
    diag = service.log_diagnostics
    # Insert log with secret
    diag.record_log(
        level=LogSeverity.ERROR,
        service="atlas.auth",
        message="Authentication failed for token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThis",
        metadata={"api_key": "mock_api_secret_key_123456789"},
    )

    logs = service.query_logs(severity=LogSeverity.ERROR, service="atlas.auth")
    assert len(logs) >= 1
    found = logs[0]
    assert "[REDACTED" in found.message or "ey" not in found.message
    assert "[REDACTED" in str(found.metadata.get("api_key"))


def test_agent_and_mcp_diagnostics(service):
    """Verifies truthful agent and MCP diagnostic inspection."""
    agents = service.get_agent_statuses()
    assert len(agents) >= 1
    assert agents[0].permission_scope == "read_only"

    mcp_conns = service.get_mcp_connections()
    assert len(mcp_conns) >= 1
    for m in mcp_conns:
        assert m.status in (ConnectionState.CONFIGURED, ConnectionState.NOT_CONFIGURED)


def test_execution_strictly_disabled(service):
    """Verifies that arbitrary execution attempt raises TerminalExecutionUnavailableError."""
    with pytest.raises(TerminalExecutionUnavailableError):
        service.execute_command_attempt("python", "print('hello')")


def test_fastapi_terminal_endpoints():
    """Integration test hitting the FastAPI /api/v1/terminal endpoints with mock auth."""
    from atlas_api.auth.dependencies import get_current_user

    async def mock_auth():
        return AuthPrincipal(
            sub="usr_test_terminal_fastapi",
            email="trader@institutional.com",
            role="authenticated",
        )

    app.dependency_overrides[get_current_user] = mock_auth
    client = TestClient(app)

    try:
        # 1. Capabilities
        r = client.get("/api/v1/terminal/capabilities")
        assert r.status_code == 200
        data = r.json()
        assert data["stage"] == 122

        # 2. Sessions list
        r = client.get("/api/v1/terminal/sessions")
        assert r.status_code == 200
        sessions = r.json()
        assert len(sessions) == 4

        # 3. Create session
        r = client.post(
            "/api/v1/terminal/sessions",
            json={"terminal_type": "PYTHON", "display_name": "API Notebook"},
        )
        assert r.status_code == 201
        new_sess = r.json()
        sess_id = new_sess["session_id"]
        assert new_sess["display_name"] == "API Notebook"

        # 4. Update session
        r = client.patch(
            f"/api/v1/terminal/sessions/{sess_id}",
            json={"display_name": "API Notebook Renamed", "draft_content": "x = 42\n"},
        )
        assert r.status_code == 200
        assert r.json()["display_name"] == "API Notebook Renamed"

        # 5. Preferences
        r = client.get("/api/v1/terminal/preferences")
        assert r.status_code == 200

        r = client.put(
            "/api/v1/terminal/preferences",
            json={"font_size": 13, "terminal_height": 380},
        )
        assert r.status_code == 200
        assert r.json()["font_size"] == 13

        # 6. Read-only diagnostics
        r = client.get("/api/v1/terminal/logs?limit=10")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        r = client.get("/api/v1/terminal/agents/status")
        assert r.status_code == 200

        r = client.get("/api/v1/terminal/mcp/connections")
        assert r.status_code == 200

        # 7. Execute attempt blocked
        r = client.post("/api/v1/terminal/execute")
        assert r.status_code == 501
        assert "strictly unavailable in Stage 122" in r.text

    finally:
        app.dependency_overrides.clear()
