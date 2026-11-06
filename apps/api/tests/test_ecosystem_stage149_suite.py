"""
ATLAS Stage 149 — MCP, Plugin and Agent Ecosystem Test Suite.
Covers Demonstrations A through M, security controls, SSRF defense, Zip-Slip,
secret scanning, package integrity, custom tool testing lab, and API endpoints.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import zipfile
import pytest
from fastapi.testclient import TestClient

from atlas.agents.domain import AgentDefinition, AgentStatus
from atlas.agents.service import AgentRegistryService
from atlas.auth import AuthPrincipal
from atlas.ecosystem.domain import (
    AuditEventType,
    GitProvider,
    MCPTransportType,
    PackageValidationResult,
    PluginStatus,
    ToolExecutionAdapter,
    ToolSideEffectClass,
    VerificationStatus,
)
from atlas.ecosystem.errors import (
    CustomToolNotFoundError,
    CustomToolValidationError,
    DeveloperAppNotFoundError,
    DeveloperCredentialRevokedError,
    DeveloperRateLimitExceededError,
    FinancialSafetyViolationError,
    MCPConnectionError,
    MCPServerNotFoundError,
    MCPSSRFSecurityError,
    PackageIntegrityError,
    PackageSecurityError,
    PackageValidationError,
    PermissionDeniedEcosystemError,
    PluginNotFoundError,
    PluginRevokedError,
    PluginValidationError,
)
from atlas.ecosystem.developers import DeveloperPlatformService
from atlas.ecosystem.external_mcp import ExternalAtlasMCPService
from atlas.ecosystem.git_integration import GitIntegrationService
from atlas.ecosystem.governance import EcosystemGovernance
from atlas.ecosystem.marketplace import MarketplaceService
from atlas.ecosystem.mcp import MCPRegistryService, validate_endpoint_security
from atlas.ecosystem.observability import EcosystemObservabilityService
from atlas.ecosystem.packages import AgentPackageManager, scan_for_secrets
from atlas.ecosystem.plugins import PluginRegistryService
from atlas.ecosystem.templates import EcosystemTemplateService
from atlas.ecosystem.tools import CustomToolRegistryService
from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app
from atlas_api.routers import agents as agents_router
from atlas_api.routers import ecosystem as eco_router


@pytest.fixture()
def client():
    # Fresh services for clean isolated testing
    agents = agents_router._service
    mcp = MCPRegistryService()
    tools = CustomToolRegistryService()
    plugins = PluginRegistryService()
    packages = AgentPackageManager(agents)
    templates = EcosystemTemplateService(agents)
    git_svc = GitIntegrationService(packages)
    marketplace = MarketplaceService()
    developers = DeveloperPlatformService()
    ext_mcp = ExternalAtlasMCPService()
    obs = EcosystemObservabilityService()

    app.dependency_overrides[agents_router.get_agent_service] = lambda: agents
    app.dependency_overrides[eco_router.get_mcp_service] = lambda: mcp
    app.dependency_overrides[eco_router.get_tools_service] = lambda: tools
    app.dependency_overrides[eco_router.get_plugins_service] = lambda: plugins
    app.dependency_overrides[eco_router.get_packages_service] = lambda: packages
    app.dependency_overrides[eco_router.get_templates_service] = lambda: templates
    app.dependency_overrides[eco_router.get_git_service] = lambda: git_svc
    app.dependency_overrides[eco_router.get_marketplace_service] = lambda: marketplace
    app.dependency_overrides[eco_router.get_developers_service] = lambda: developers
    app.dependency_overrides[eco_router.get_external_mcp_service] = lambda: ext_mcp
    app.dependency_overrides[eco_router.get_observability_service] = lambda: obs
    app.dependency_overrides[get_current_user] = lambda: AuthPrincipal(
        sub="test-user-149",
        raw_claims={"tenant_id": "tenant-149"},
    )

    yield TestClient(app)
    app.dependency_overrides.clear()


# ===========================================================================
# DEMONSTRATION A: MCP Connection & Tool Invocation
# ===========================================================================

def test_A_mcp_connection_discovery_and_invocation() -> None:
    svc = MCPRegistryService()
    server = svc.get_server("official-atlas-research-mcp")
    assert server.verification_status == VerificationStatus.OFFICIAL_ATLAS

    # Connect tenant to server
    conn = svc.create_connection(
        tenant_id="tenant-149",
        owner_id="user-149",
        server_id=server.server_id,
        authorization_scopes=("tools:sec_read", "resources:read"),
    )
    assert conn.connection_status.name == "CONNECTED"
    assert conn.capabilities_snapshot is not None
    assert len(conn.capabilities_snapshot.tools) >= 2

    # Ping / test connection
    ping_result = svc.test_connection(
        connection_id=conn.connection_id,
        tenant_id="tenant-149",
        owner_id="user-149",
    )
    assert ping_result["status"] == "HEALTHY"
    assert ping_result["tools_count"] >= 2

    # Invoke approved tool
    res = svc.invoke_tool(
        connection_id=conn.connection_id,
        tool_id="atlas.research.sec_filings_search",
        arguments={"ticker": "AAPL", "form_type": "10-K"},
        tenant_id="tenant-149",
        owner_id="user-149",
    )
    assert res["status"] == "SUCCESS"
    assert res["output"]["ticker"] == "AAPL"
    assert res["output"]["status"] == "VERIFIED_AUTHENTIC"


# ===========================================================================
# DEMONSTRATION B: SSRF Security Defense on MCP Endpoints
# ===========================================================================

def test_B_mcp_ssrf_security_defenses() -> None:
    # 1. Localhost should be blocked
    with pytest.raises(MCPSSRFSecurityError):
        validate_endpoint_security("http://localhost:8000/mcp")

    # 2. Loopback 127.0.0.1 should be blocked
    with pytest.raises(MCPSSRFSecurityError):
        validate_endpoint_security("http://127.0.0.1:9090/v1")

    # 3. Private RFC 1918 (10.0.0.1, 192.168.1.1) should be blocked
    with pytest.raises(MCPSSRFSecurityError):
        validate_endpoint_security("https://10.0.0.1/mcp")
    with pytest.raises(MCPSSRFSecurityError):
        validate_endpoint_security("https://192.168.1.50/mcp")

    # 4. Cloud metadata service 169.254.169.254 should be blocked
    with pytest.raises(MCPSSRFSecurityError):
        validate_endpoint_security("http://169.254.169.254/latest/meta-data/")

    # 5. Non-http/https should be blocked
    with pytest.raises(MCPSSRFSecurityError):
        validate_endpoint_security("file:///etc/passwd")

    # 6. Valid public endpoint is allowed
    validate_endpoint_security("https://api.sec-edgar.gov/mcp/v1")


# ===========================================================================
# DEMONSTRATION C: Custom Tool Definition, Testing Lab & Publishing
# ===========================================================================

def test_C_custom_tool_testing_lab_and_publishing() -> None:
    svc = CustomToolRegistryService()

    # Register custom DCF tool
    tool = svc.register_tool(
        tool_id="atlas.custom.unit_test_dcf",
        publisher_id="user-149",
        name="Unit Test DCF Modeler",
        description="Calculates firm enterprise value.",
        version="1.0.0",
        input_schema={
            "type": "object",
            "properties": {
                "fcf_projections": {"type": "array"},
                "discount_rate": {"type": "number"},
                "terminal_growth_rate": {"type": "number"},
            },
            "required": ["fcf_projections", "discount_rate", "terminal_growth_rate"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "enterprise_value": {"type": "number"},
                "implied_share_price": {"type": "number"},
            },
            "required": ["enterprise_value", "implied_share_price"],
        },
        required_scopes=("tools:calculate",),
        side_effect_class=ToolSideEffectClass.READ_ONLY,
        execution_adapter=ToolExecutionAdapter.TRANSFORMATION,
    )
    assert not tool.is_published

    # Test in testing lab with valid inputs
    test_res = svc.test_tool(
        test_id="test-1",
        tool_id="atlas.custom.discounted_cash_flow",
        input_payload={
            "fcf_projections": [100.0, 110.0, 120.0],
            "discount_rate": 0.09,
            "terminal_growth_rate": 0.025,
            "net_debt": 20.0,
            "shares_outstanding": 10.0,
        },
    )
    assert test_res.passed
    assert test_res.output_payload is not None
    assert test_res.output_payload["enterprise_value"] > 0

    # Test with schema violation (missing required field)
    invalid_test = svc.test_tool(
        test_id="test-2",
        tool_id="atlas.custom.discounted_cash_flow",
        input_payload={"fcf_projections": [100.0]},  # missing discount_rate
    )
    assert not invalid_test.passed
    assert "missing required field" in (invalid_test.error_message or "")

    # Publish tool
    published = svc.publish_tool("atlas.custom.unit_test_dcf")
    assert published.is_published


# ===========================================================================
# DEMONSTRATION D & E: .atlas-agent Package Export & Import
# ===========================================================================

def test_D_and_E_atlas_agent_export_and_import() -> None:
    agent_svc = AgentRegistryService()
    # Create base agent
    agent = agent_svc.create_agent(
        tenant_id="tenant-149",
        owner_id="user-149",
        name="Equity Research Specialist",
        description="Analyzes equity filings and reports.",
        role="RESEARCHER",
        model_id="atlas-intelligence-v1",
        instructions="Analyze SEC filings rigorously without bias.",
        tool_ids=["atlas.instrument.search"],
        execution_limits={"max_tokens": 4096},
    )

    pm = AgentPackageManager(agent_svc)
    # Export to .atlas-agent
    exported = pm.export_agent(
        agent_id=agent.agent_id,
        tenant_id="tenant-149",
        owner_id="user-149",
        package_id="pkg.equity-research-spec",
        version="1.0.0",
    )
    assert exported.filename.endswith(".atlas-agent")
    assert len(exported.archive_bytes) > 0
    assert exported.sha256_hash is not None

    # Validate package bytes
    val = pm.validate_package_bytes(exported.archive_bytes)
    assert val.is_valid
    assert val.package_id == "pkg.equity-research-spec"
    assert val.checksum_verified
    assert not val.secrets_detected

    # Import package into a second tenant
    imported = pm.import_package(
        archive_bytes=exported.archive_bytes,
        tenant_id="tenant-200",
        owner_id="user-200",
        granted_permissions=("READ_RESEARCH",),
    )
    assert imported.installation_status == "DRAFT"
    assert imported.package_id == "pkg.equity-research-spec"

    # Verify agent exists in draft state in Agent Registry
    installed_agent = agent_svc.get_agent(
        agent_id=imported.agent_id,
        tenant_id="tenant-200",
        owner_id="user-200",
    )
    assert installed_agent.status == AgentStatus.DRAFT
    assert installed_agent.name == "Equity Research Specialist"


# ===========================================================================
# DEMONSTRATION F: Package Integrity Check on Tampered Archive
# ===========================================================================

def test_F_package_tampering_integrity_detection() -> None:
    agent_svc = AgentRegistryService()
    agent = agent_svc.create_agent(
        tenant_id="tenant-149",
        owner_id="user-149",
        name="Integrity Agent",
        description="For tamper detection testing.",
        role="ANALYST",
        model_id="atlas-intelligence-v1",
        instructions="Secure prompt.",
        tool_ids=[],
        execution_limits={},
    )
    pm = AgentPackageManager(agent_svc)
    exported = pm.export_agent(
        agent_id=agent.agent_id,
        tenant_id="tenant-149",
        owner_id="user-149",
    )

    # Tamper with archive by modifying agent/instructions.md without updating checksums.json
    buf_in = io.BytesIO(exported.archive_bytes)
    buf_out = io.BytesIO()
    with zipfile.ZipFile(buf_in, "r") as zin:
        with zipfile.ZipFile(buf_out, "w") as zout:
            for item in zin.infolist():
                if item.filename == "agent/instructions.md":
                    zout.writestr(item.filename, b"TAMPERED PROMPT CONTENT!")
                else:
                    zout.writestr(item.filename, zin.read(item.filename))

    tampered_bytes = buf_out.getvalue()
    val = pm.validate_package_bytes(tampered_bytes)
    assert not val.is_valid
    assert any("Checksum mismatch" in e for e in val.errors)

    # Importing tampered package must raise PackageIntegrityError
    with pytest.raises(PackageIntegrityError):
        pm.import_package(
            archive_bytes=tampered_bytes,
            tenant_id="tenant-149",
            owner_id="user-149",
            granted_permissions=("READ_RESEARCH",),
        )


# ===========================================================================
# DEMONSTRATION G: Secret Scanning Defense in Packages
# ===========================================================================

def test_G_secret_scanning_defense() -> None:
    # Secret pattern detector test
    assert scan_for_secrets("Here is my key: sk-abcdef1234567890abcdef1234567890") is not None
    assert scan_for_secrets("AWS Key: AKIAIOSFODNN7EXAMPLE") is not None
    assert scan_for_secrets("Standard safe instructions.") is None

    # Package containing secret should fail validation
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        manifest = {
            "manifest_version": "1.0",
            "package_id": "pkg.leaky",
            "name": "Leaky Package",
            "version": "1.0.0",
            "kind": "atlas-agent",
            "entrypoint": "agent/definition.json",
        }
        zf.writestr("manifest.json", json.dumps(manifest).encode("utf-8"))
        zf.writestr("agent/definition.json", json.dumps({"name": "Leaky", "role": "Tester"}).encode("utf-8"))
        zf.writestr("agent/instructions.md", b"API Key: sk-123456789012345678901234567890123456")

    pm = AgentPackageManager()
    val = pm.validate_package_bytes(buf.getvalue())
    assert not val.is_valid
    assert val.secrets_detected
    assert any("Prohibited secret pattern" in e for e in val.errors)


# ===========================================================================
# DEMONSTRATION H & I: Plugin Lifecycle & Disabling
# ===========================================================================

def test_H_and_I_plugin_lifecycle_and_disabling() -> None:
    svc = PluginRegistryService()
    manifest = svc.get_plugin("sec-filings-plugin")

    # Install plugin with granted permissions
    inst = svc.install_plugin(
        plugin_id=manifest.plugin_id,
        tenant_id="tenant-149",
        owner_id="user-149",
        granted_permissions=("tools:sec_read", "storage:research_read"),
    )
    assert inst.status == PluginStatus.ENABLED

    # Disable plugin
    disabled = svc.disable_plugin(
        installation_id=inst.installation_id,
        tenant_id="tenant-149",
        owner_id="user-149",
    )
    assert disabled.status == PluginStatus.DISABLED

    # Uninstall plugin
    svc.uninstall_plugin(
        installation_id=inst.installation_id,
        tenant_id="tenant-149",
        owner_id="user-149",
    )
    assert len(svc.list_installations(tenant_id="tenant-149", owner_id="user-149")) == 0


# ===========================================================================
# DEMONSTRATION J: Git Integration & Provenance
# ===========================================================================

def test_J_git_integration_and_provenance() -> None:
    pm = AgentPackageManager()
    git_svc = GitIntegrationService(pm)

    # Valid Git connection
    conn = git_svc.create_connection(
        tenant_id="tenant-149",
        owner_id="user-149",
        provider=GitProvider.GITHUB,
        repository_url="https://github.com/atlas-org/sample-agent.git",
        default_branch="main",
    )
    assert conn.status == "CONNECTED"

    # Reject local filesystem URLs
    with pytest.raises(PackageSecurityError):
        git_svc.create_connection(
            tenant_id="tenant-149",
            owner_id="user-149",
            provider=GitProvider.GENERIC_GIT,
            repository_url="file:///home/user/repo.git",
        )


# ===========================================================================
# DEMONSTRATION K: Marketplace Search & Catalog Integrity
# ===========================================================================

def test_K_marketplace_search_and_truthful_catalog() -> None:
    svc = MarketplaceService()
    items = svc.search_catalog(query="SEC")
    assert len(items) >= 1
    sec_item = items[0]
    assert "SEC" in sec_item.name
    # Verification: Authentic publishers only, no fake stars
    assert sec_item.verification_status in (VerificationStatus.OFFICIAL_ATLAS, VerificationStatus.VERIFIED_PARTNER)


# ===========================================================================
# DEMONSTRATION L: Developer Applications & Scoped API Credentials
# ===========================================================================

def test_L_developer_app_and_credential_revocation() -> None:
    dev = DeveloperPlatformService()
    app = dev.register_app(
        developer_id="user-149",
        tenant_id="tenant-149",
        name="Quant Portfolio Analyzer",
        description="External client.",
        allowed_scopes=("atlas.agents:read", "atlas.tools:read"),
    )
    assert app.status.name == "ACTIVE"

    # Issue API Credential
    cred, raw_secret = dev.issue_credential(
        app_id=app.app_id,
        tenant_id="tenant-149",
        scopes=("atlas.agents:read",),
    )
    assert cred.client_id.startswith("atlas_live_")
    assert raw_secret.startswith("sec_")

    # Verify Credential
    verified = dev.verify_credential(cred.client_id, raw_secret, "atlas.agents:read")
    assert verified.credential_id == cred.credential_id

    # Missing scope raises permission error
    with pytest.raises(PermissionDeniedEcosystemError):
        dev.verify_credential(cred.client_id, raw_secret, "atlas.trading:execute")

    # Revoke application
    dev.revoke_app(app.app_id)
    with pytest.raises(DeveloperCredentialRevokedError):
        dev.verify_credential(cred.client_id, raw_secret, "atlas.agents:read")


# ===========================================================================
# DEMONSTRATION M: External ATLAS MCP Server
# ===========================================================================

def test_M_external_atlas_mcp_server() -> None:
    ext_mcp = ExternalAtlasMCPService()
    tools = ext_mcp.list_tools()
    assert len(tools) >= 4

    # Invoke research tool with permitted scopes
    res = ext_mcp.invoke_tool(
        tool_id="atlas_company_profile",
        arguments={"ticker": "MSFT"},
        tenant_id="tenant-149",
        granted_scopes=("atlas.companies:read",),
    )
    assert res.success
    assert res.output["ticker"] == "MSFT"

    # Missing scope fails
    with pytest.raises(PermissionDeniedEcosystemError):
        ext_mcp.invoke_tool(
            tool_id="atlas_company_profile",
            arguments={"ticker": "MSFT"},
            tenant_id="tenant-149",
            granted_scopes=("atlas.other:scope",),
        )


# ===========================================================================
# FINANCIAL SAFETY FIREWALL TESTS
# ===========================================================================

def test_N_financial_safety_firewall() -> None:
    # 1. Reject live broker orders in custom tool registration
    svc = CustomToolRegistryService()
    with pytest.raises(FinancialSafetyViolationError):
        svc.register_tool(
            tool_id="atlas.broker.submit_order",
            publisher_id="u",
            name="Broker Trade Execution",
            description="Places buy orders",
            version="1.0.0",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            required_scopes=(),
            side_effect_class=ToolSideEffectClass.EXTERNAL_WRITE,
            execution_adapter=ToolExecutionAdapter.DECLARATIVE_HTTP,
        )

    # 2. Reject trading action in governance check
    with pytest.raises(FinancialSafetyViolationError):
        EcosystemGovernance.enforce_financial_safety("submit_market_order", {"execution_mode": "LIVE_MONEY"})


# ===========================================================================
# FASTAPI HTTP ENDPOINT TESTS
# ===========================================================================

def test_O_api_overview_and_mcp_endpoints(client: TestClient) -> None:
    resp = client.get("/api/v1/ecosystem/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["mcp_servers_count"] >= 3
    assert data["marketplace_items_count"] >= 4

    # List MCP servers
    servers_resp = client.get("/api/v1/ecosystem/mcp/servers")
    assert servers_resp.status_code == 200
    servers = servers_resp.json()
    assert len(servers) >= 3

    # Connect to first server
    server_id = servers[0]["server_id"]
    conn_resp = client.post(
        "/api/v1/ecosystem/mcp/connections",
        json={"server_id": server_id, "authorization_scopes": ["tools:read"]},
    )
    assert conn_resp.status_code == 200
    conn_data = conn_resp.json()
    conn_id = conn_data["connection_id"]

    # Test ping on connection
    ping_resp = client.post(f"/api/v1/ecosystem/mcp/connections/{conn_id}/test")
    assert ping_resp.status_code == 200
    assert ping_resp.json()["status"] == "HEALTHY"


def test_P_api_custom_tools_and_marketplace(client: TestClient) -> None:
    # Custom tools listing
    tools_resp = client.get("/api/v1/ecosystem/tools")
    assert tools_resp.status_code == 200
    tools = tools_resp.json()
    assert len(tools) >= 2

    # Marketplace catalog search
    market_resp = client.get("/api/v1/ecosystem/marketplace/catalog?q=SEC")
    assert market_resp.status_code == 200
    assert len(market_resp.json()) >= 1


def test_Q_api_packages_export_and_validate(client: TestClient) -> None:
    # First create an agent via agent API
    create_resp = client.post(
        "/api/v1/agents",
        json={
            "name": "API Test Agent",
            "description": "For API export test",
            "role": "ANALYST",
            "model_id": "atlas-intelligence-v1",
            "instructions": "Rigorously analyze numbers.",
            "tool_ids": [],
            "execution_limits": {},
        },
    )
    assert create_resp.status_code == 201
    agent_id = create_resp.json()["agent_id"]

    # Export agent package
    exp_resp = client.post(
        "/api/v1/ecosystem/packages/export",
        json={"agent_id": agent_id, "package_id": "pkg.api-test"},
    )
    assert exp_resp.status_code == 200
    exp_data = exp_resp.json()
    assert "archive_base64" in exp_data

    # Validate package
    val_resp = client.post(
        "/api/v1/ecosystem/packages/validate",
        json={"archive_base64": exp_data["archive_base64"]},
    )
    assert val_resp.status_code == 200
    assert val_resp.json()["is_valid"] is True

