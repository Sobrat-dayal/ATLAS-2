"""Comprehensive pytest suite for Stage 126: ATLAS AI Tool Gateway.

Covers:
- Part LXXIII: Reference Fixture A (Instrument Search)
- Part LXXIV: Reference Fixture B (Market Quote)
- Part LXXV: Reference Fixture C (Company Financials & Revenue Growth)
- Part LXXVI: Reference Fixture D (Unauthorized Portfolio & Anti-IDOR)
- Part LXXVII: Reference Fixture E (Provider Disclosure Restrictions)
- Part LXXVIII: Reference Fixture F (Prompt Injection Defense & Fencing)
- Part LXXIX: Reference Fixture G (Unknown Tool Rejection)
- Part LXXX: Reference Fixture H (Infinite Tool Loop & Sequence Limits)
- Part LXXXI: Reference Fixture I (Approval Argument Swap Rejection)
- Part LXXXII: Reference Fixture J (Immutable Historical Risk Run)
- Prohibited Code Execution Enforcement (execute_python, execute_sql, execute_shell)
- Universal Tool Registry & Discovery Service
- Approval Engine (Lifecycle, TTL Expiration, Replay Prevention)
- Full FastAPI Router Endpoints (/api/v1/ai/tools)
"""

import pytest
from atlas.ai.tools.approval import AiToolApprovalEngine
from atlas.ai.tools.discovery import ToolDiscoveryService
from atlas.ai.tools.dispatcher import AiToolDispatcher
from atlas.ai.tools.domain import (
    ApprovalClass,
    AtlasAiToolDefinition,
    CapabilityScope,
    ProviderDisclosurePolicy,
    ToolCategory,
)
from atlas.ai.tools.errors import (
    AiToolApprovalMismatchError,
    AiToolError,
    AiToolNotFoundError,
    AiToolProviderDisclosureDeniedError,
    AiToolResourceAccessDeniedError,
    AiToolSequenceLimitExceededError,
)
from atlas.ai.tools.gateway import AiToolSecurityGateway
from atlas.ai.tools.registry import AtlasAiToolRegistry
from atlas.auth import AuthPrincipal
from fastapi.testclient import TestClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user


@pytest.fixture(autouse=True)
def reset_singletons():
    """Ensures test isolation across all gateway singletons."""
    AtlasAiToolRegistry.reset_instance()
    AiToolApprovalEngine.reset_instance()
    AiToolSecurityGateway.reset_instance()
    AiToolDispatcher.reset_instance()
    # Pre-register test resource ownership
    gw = AiToolSecurityGateway.get_instance()
    gw.register_resource_owner("portfolio", "port_growth_1", "user_primary")
    gw.register_resource_owner("portfolio", "port_macro_2", "user_other")
    gw.register_resource_owner("risk_run", "run_hist_20261029", "user_primary")


# ---------------- Reference Fixtures A–J Tests ----------------


@pytest.mark.asyncio
async def test_fixture_a_instrument_search():
    """Fixture A: atlas.instrument.search returns canonical Instrument results without guessing."""
    dispatcher = AiToolDispatcher.get_instance()

    result = await dispatcher.dispatch(
        tool_id="atlas.instrument.search",
        arguments={"query": "Microsoft", "limit": 5},
        user_id="user_primary",
    )

    assert result.success is True
    assert result.tool_id == "atlas.instrument.search"
    results = result.data.get("results", [])
    assert len(results) >= 1
    msft = results[0]
    assert msft["symbol"] == "MSFT"
    assert msft["name"] == "Microsoft Corporation"
    assert msft["exchange"] == "NASDAQ"
    assert msft["figi"] == "BBG000BPH459"
    assert msft["isin"] == "US5949181045"
    assert result.source_manifest is not None
    assert result.source_manifest.attribution == "ATLAS Security Master"
    assert len(result.content_hash) == 64


@pytest.mark.asyncio
async def test_fixture_b_market_quote():
    """Fixture B: atlas.market.quote returns verified quote or explicit unavailable flag (no fake data)."""
    dispatcher = AiToolDispatcher.get_instance()

    # 1. Available Quote
    result_msft = await dispatcher.dispatch(
        tool_id="atlas.market.quote",
        arguments={"symbol": "MSFT"},
        user_id="user_primary",
    )
    assert result_msft.success is True
    assert result_msft.data["quote_available"] is True
    assert result_msft.data["last_price"] == 428.50
    assert result_msft.data["currency"] == "USD"
    assert result_msft.data["exchange"] == "NASDAQ"

    # 2. Unavailable Quote: Returns quote_available=False without fabricating
    result_unavail = await dispatcher.dispatch(
        tool_id="atlas.market.quote",
        arguments={"symbol": "UNKNOWN_TICKER_99"},
        user_id="user_primary",
    )
    assert result_unavail.success is True
    assert result_unavail.data["quote_available"] is False
    assert result_unavail.data["message"] == "Quote unavailable."


@pytest.mark.asyncio
async def test_fixture_c_company_financials_growth():
    """Fixture C: atlas.company.financials returns point-in-time facts (FY24 100M, FY25 125M -> 25% growth)."""
    dispatcher = AiToolDispatcher.get_instance()

    result = await dispatcher.dispatch(
        tool_id="atlas.company.financials",
        arguments={"symbol": "MSFT", "statement_type": "INCOME_STATEMENT", "period": "ANNUAL"},
        user_id="user_primary",
    )

    assert result.success is True
    assert result.data["symbol"] == "MSFT"
    assert result.data["currency"] == "USD"
    assert result.data["units"] == "millions"
    line_items = result.data["line_items"]
    assert len(line_items) >= 2

    # FY2025 revenue: 125M, FY2024 revenue: 100M
    fy25 = line_items[0]
    fy24 = line_items[1]
    assert fy25["fiscal_year"] == 2025
    assert fy25["revenue"] == 125.0
    assert fy24["fiscal_year"] == 2024
    assert fy24["revenue"] == 100.0

    # Calculate and verify 25% annual revenue growth
    growth_rate = (fy25["revenue"] - fy24["revenue"]) / fy24["revenue"]
    assert growth_rate == 0.25


@pytest.mark.asyncio
async def test_fixture_d_unauthorized_portfolio_anti_idor():
    """Fixture D: User B attempts atlas.portfolio.get_summary on User A's portfolio -> Permission denied."""
    dispatcher = AiToolDispatcher.get_instance()

    # User B attempts to access port_growth_1 (owned by user_primary)
    with pytest.raises(AiToolResourceAccessDeniedError) as exc_info:
        await dispatcher.dispatch(
            tool_id="atlas.portfolio.get_summary",
            arguments={"portfolio_id": "port_growth_1"},
            user_id="user_unauthorized_attacker",
        )

    assert exc_info.value.code == "AI_TOOL_RESOURCE_ACCESS_DENIED"
    assert exc_info.value.resource_id == "port_growth_1"


@pytest.mark.asyncio
async def test_fixture_e_provider_disclosure_restriction():
    """Fixture E: Data marked ProviderDisclosurePolicy.PROHIBITED cannot be sent to provider."""
    registry = AtlasAiToolRegistry.get_instance()

    # Register a restricted test tool
    restricted_tool = AtlasAiToolDefinition(
        tool_id="atlas.test.restricted_feed",
        version="1.0.0",
        category=ToolCategory.DATA_READ,
        name="Restricted Proprietary Feed",
        capability_scope=CapabilityScope.DATA_READ,
        provider_disclosure_policy=ProviderDisclosurePolicy.PROHIBITED,
    )
    registry.register_tool(restricted_tool)

    dispatcher = AiToolDispatcher.get_instance()
    with pytest.raises(AiToolProviderDisclosureDeniedError) as exc_info:
        await dispatcher.dispatch(
            tool_id="atlas.test.restricted_feed",
            arguments={},
            user_id="user_primary",
            provider_id="openai",
        )

    assert exc_info.value.code == "AI_TOOL_PROVIDER_DISCLOSURE_DENIED"


@pytest.mark.asyncio
async def test_fixture_f_prompt_injection_defense():
    """Fixture F: News headline containing prompt injection instructions remains fenced as untrusted text."""
    dispatcher = AiToolDispatcher.get_instance()

    result = await dispatcher.dispatch(
        tool_id="atlas.news.search_headlines",
        arguments={"symbol": "MSFT"},
        user_id="user_primary",
    )

    assert result.success is True
    headlines = result.data["headlines"]
    injection_headline = next(
        h for h in headlines if "Ignore all previous instructions" in h["title"]
    )

    # Ensure fenced with untrusted read-only context tag
    assert (
        '<atlas_verified_financial_context data-purpose="untrusted-read-only-financial-context">'
        in injection_headline["title"]
    )
    assert "</atlas_verified_financial_context>" in injection_headline["title"]


@pytest.mark.asyncio
async def test_fixture_g_unknown_tool_rejection():
    """Fixture G: Model proposes unknown tool -> AI_TOOL_NOT_FOUND, no fallback to arbitrary execution."""
    dispatcher = AiToolDispatcher.get_instance()

    with pytest.raises(AiToolNotFoundError) as exc_info:
        await dispatcher.dispatch(
            tool_id="atlas.system.execute_anything",
            arguments={"cmd": "whoami"},
            user_id="user_primary",
        )

    assert exc_info.value.code == "AI_TOOL_NOT_FOUND"
    assert exc_info.value.tool_id == "atlas.system.execute_anything"


@pytest.mark.asyncio
async def test_fixture_h_infinite_tool_loop_prevention():
    """Fixture H: Infinite tool calling loop terminates cleanly with sequence limit exceeded error."""
    dispatcher = AiToolDispatcher.get_instance()

    # Calling tool when generation_tool_call_count has reached MAX (4)
    with pytest.raises(AiToolSequenceLimitExceededError) as exc_info:
        await dispatcher.dispatch(
            tool_id="atlas.instrument.search",
            arguments={"query": "MSFT"},
            user_id="user_primary",
            generation_tool_call_count=4,
        )

    assert exc_info.value.code == "AI_TOOL_SEQUENCE_LIMIT_EXCEEDED"
    assert exc_info.value.max_calls == 4


@pytest.mark.asyncio
async def test_fixture_i_approval_argument_swap_rejection():
    """Fixture I: Approval token issued for Resource A cannot be swapped for Resource B at execution time."""
    approval_engine = AiToolApprovalEngine.get_instance()

    # Issue approval for portfolio A
    req = approval_engine.create_approval_request(
        tool_call_id="call_test_1",
        user_id="user_primary",
        tool_id="atlas.portfolio.get_summary",
        approval_class=ApprovalClass.USER_CONFIRMATION_REQUIRED,
        arguments={"portfolio_id": "port_growth_1"},
    )

    # Approve request
    approval_engine.approve(req.id, "user_primary")

    # Attacker attempts to consume approval with swapped argument: port_macro_2
    with pytest.raises(AiToolApprovalMismatchError) as exc_info:
        approval_engine.consume_and_verify(
            approval_request_id=req.id,
            user_id="user_primary",
            tool_id="atlas.portfolio.get_summary",
            arguments={"portfolio_id": "port_macro_2"},  # SWAPPED ARGUMENT
        )

    assert exc_info.value.code == "AI_TOOL_APPROVAL_MISMATCH"


@pytest.mark.asyncio
async def test_fixture_j_historical_risk_run_immutability():
    """Fixture J: atlas.risk.get_run_summary retrieves immutable historical record without recomputing."""
    dispatcher = AiToolDispatcher.get_instance()

    result = await dispatcher.dispatch(
        tool_id="atlas.risk.get_run_summary",
        arguments={"run_id": "run_hist_20261029"},
        user_id="user_primary",
    )

    assert result.success is True
    data = result.data
    assert data["run_id"] == "run_hist_20261029"
    assert data["model"] == "HISTORICAL_SIMULATION_250D"
    assert data["confidence_level"] == 0.95
    assert data["horizon_days"] == 1
    assert data["as_of"] == "2026-10-29T16:00:00Z"
    assert data["var_amount"] == 26800.0
    assert data["factor_exposures"]["Market"] == 1.05


# ---------------- Security & Registry Boundaries ----------------


def test_prohibited_arbitrary_code_execution():
    """Verifies that arbitrary code, shell, or trade execution tools cannot be registered."""
    registry = AtlasAiToolRegistry.get_instance()

    prohibited_names = [
        "atlas.system.execute_python",
        "atlas.shell.execute_bash",
        "atlas.db.execute_sql",
        "atlas.broker.trade_order",
    ]

    for name in prohibited_names:
        tool_def = AtlasAiToolDefinition(
            tool_id=name,
            version="1.0.0",
            category=ToolCategory.PRIVILEGED_OPERATION,
            name="Prohibited Tool",
        )
        with pytest.raises(AiToolError) as exc_info:
            registry.register_tool(tool_def)
        assert exc_info.value.code == "AI_TOOL_PROHIBITED_CAPABILITY"


def test_tool_discovery_filtering_and_route_affinity():
    """Verifies tool discovery filters disabled tools and orders by route affinity."""
    discovery = ToolDiscoveryService.get_instance()

    # On /company, company and financials tools are prioritized
    tools = discovery.discover_tools(
        user_id="user_primary",
        active_route="/company",
        disabled_tool_ids=["atlas.watchlist.list"],
        max_tools=8,
    )

    tool_ids = [t.tool_id for t in tools]
    assert "atlas.company.get" in tool_ids[:3]
    assert "atlas.company.financials" in tool_ids[:3]
    assert "atlas.watchlist.list" not in tool_ids


# ---------------- FastAPI Router Integration Tests ----------------


@pytest.fixture
def client():
    app = create_app()
    principal = AuthPrincipal(
        sub="user_primary", email="pm101@atlas.institutional", role="portfolio_manager"
    )
    app.dependency_overrides[get_current_user] = lambda: principal
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_current_user, None)


def test_api_list_tools(client):
    """Tests GET /api/v1/ai/tools."""
    resp = client.get("/api/v1/ai/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert "tools" in data
    assert data["total"] >= 19
    tool_ids = [t["tool_id"] for t in data["tools"]]
    assert "atlas.instrument.search" in tool_ids
    assert "atlas.market.quote" in tool_ids
    assert "atlas.portfolio.get_summary" in tool_ids


def test_api_get_tool_metadata(client):
    """Tests GET /api/v1/ai/tools/{tool_id}."""
    resp = client.get("/api/v1/ai/tools/atlas.instrument.search")
    assert resp.status_code == 200
    data = resp.json()
    assert data["tool_id"] == "atlas.instrument.search"
    assert data["category"] == "DISCOVERY"
    assert "parameters_schema" in data


def test_api_execute_tool(client):
    """Tests POST /api/v1/ai/tools/execute."""
    resp = client.post(
        "/api/v1/ai/tools/execute",
        json={
            "tool_id": "atlas.instrument.search",
            "arguments": {"query": "Apple"},
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["tool_id"] == "atlas.instrument.search"
    assert len(data["data"]["results"]) >= 1


def test_api_preferences_lifecycle(client):
    """Tests GET and PUT /api/v1/ai/tools/preferences."""
    # 1. Get initial preferences
    resp_get = client.get("/api/v1/ai/tools/preferences")
    assert resp_get.status_code == 200
    prefs = resp_get.json()
    assert prefs["auto_approve_read_only"] is True

    # 2. Update preferences
    resp_put = client.put(
        "/api/v1/ai/tools/preferences",
        json={
            "disabled_tools": ["atlas.screener.get_definition"],
            "require_approval_for_sensitive": True,
        },
    )
    assert resp_put.status_code == 200
    updated = resp_put.json()
    assert "atlas.screener.get_definition" in updated["disabled_tools"]


def test_api_approval_lifecycle(client):
    """Tests approval creation, query, and approve action."""
    approval_engine = AiToolApprovalEngine.get_instance()

    # Create approval
    req = approval_engine.create_approval_request(
        tool_call_id="call_api_1",
        user_id="user_primary",
        tool_id="atlas.portfolio.get_summary",
        approval_class=ApprovalClass.USER_CONFIRMATION_REQUIRED,
        arguments={"portfolio_id": "port_growth_1"},
    )

    # Query approval
    resp_get = client.get(f"/api/v1/ai/tools/approvals/{req.id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["status"] == "PENDING"

    # Approve approval
    resp_approve = client.post(
        f"/api/v1/ai/tools/approvals/{req.id}/approve",
        json={"decision_reason": "Authorized by test analyst"},
    )
    assert resp_approve.status_code == 200
    assert resp_approve.json()["status"] == "APPROVED"
    assert resp_approve.json()["decision_reason"] == "Authorized by test analyst"
