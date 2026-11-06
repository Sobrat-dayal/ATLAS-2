"""
Stage 149 Ecosystem API Router:
Model Context Protocol (MCP) Registry, Custom Tools, Plugin Architecture,
.atlas-agent Packages, Templates, Git Integration, Marketplace, and Developer Platform.
"""

from __future__ import annotations

import base64
from typing import Annotated, Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from atlas.auth import AuthPrincipal
from atlas.ecosystem.domain import (
    AuditEventType,
    GitProvider,
    MCPTransportType,
    ToolExecutionAdapter,
    ToolSideEffectClass,
    VerificationStatus,
)
from atlas.ecosystem.errors import (
    CustomToolExecutionError,
    CustomToolNotFoundError,
    CustomToolValidationError,
    DeveloperAppNotFoundError,
    DeveloperCredentialRevokedError,
    DeveloperRateLimitExceededError,
    EcosystemError,
    FinancialSafetyViolationError,
    MCPConnectionError,
    MCPServerNotFoundError,
    MCPSSRFSecurityError,
    PackageIntegrityError,
    PackageNotFoundError,
    PackageSecurityError,
    PackageValidationError,
    PermissionDeniedEcosystemError,
    PluginNotFoundError,
    PluginRevokedError,
    PluginValidationError,
    ResourceQuotaExceededError,
)
from atlas.ecosystem.developers import DeveloperPlatformService
from atlas.ecosystem.external_mcp import ExternalAtlasMCPService
from atlas.ecosystem.git_integration import GitIntegrationService
from atlas.ecosystem.marketplace import MarketplaceService
from atlas.ecosystem.mcp import MCPRegistryService
from atlas.ecosystem.observability import EcosystemObservabilityService
from atlas.ecosystem.packages import AgentPackageManager
from atlas.ecosystem.plugins import PluginRegistryService
from atlas.ecosystem.templates import EcosystemTemplateService
from atlas.ecosystem.tools import CustomToolRegistryService
from atlas_api.auth.dependencies import get_current_user

router = APIRouter(prefix="/ecosystem", tags=["Ecosystem"])

# Service singletons for the API runtime
_mcp_service = MCPRegistryService()
_tools_service = CustomToolRegistryService()
_plugins_service = PluginRegistryService()
_packages_service = AgentPackageManager()
_templates_service = EcosystemTemplateService()
_git_service = GitIntegrationService(_packages_service)
_marketplace_service = MarketplaceService()
_developers_service = DeveloperPlatformService()
_external_mcp_service = ExternalAtlasMCPService()
_observability_service = EcosystemObservabilityService()


def _identity(principal: AuthPrincipal) -> tuple[str, str]:
    tenant_id = str(principal.raw_claims.get("tenant_id", principal.sub))
    owner_id = principal.user_id
    return tenant_id, owner_id


# ---------------------------------------------------------------------------
# Dependency Getters (Allowing test fixture overrides)
# ---------------------------------------------------------------------------

def get_mcp_service() -> MCPRegistryService:
    return _mcp_service


def get_tools_service() -> CustomToolRegistryService:
    return _tools_service


def get_plugins_service() -> PluginRegistryService:
    return _plugins_service


def get_packages_service() -> AgentPackageManager:
    return _packages_service


def get_templates_service() -> EcosystemTemplateService:
    return _templates_service


def get_git_service() -> GitIntegrationService:
    return _git_service


def get_marketplace_service() -> MarketplaceService:
    return _marketplace_service


def get_developers_service() -> DeveloperPlatformService:
    return _developers_service


def get_external_mcp_service() -> ExternalAtlasMCPService:
    return _external_mcp_service


def get_observability_service() -> EcosystemObservabilityService:
    return _observability_service


# ---------------------------------------------------------------------------
# Request & Response Models
# ---------------------------------------------------------------------------

# Overview
class EcosystemOverviewResponse(BaseModel):
    mcp_servers_count: int
    mcp_connections_count: int
    installed_plugins_count: int
    custom_tools_count: int
    installed_packages_count: int
    marketplace_items_count: int
    developer_apps_count: int
    recent_events: List[Dict[str, Any]]


# MCP
class RegisterMCPServerRequest(BaseModel):
    server_id: str = Field(min_length=3, max_length=120)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="")
    transport_type: str = Field(default="STREAMABLE_HTTP")
    endpoint_reference: str = Field(min_length=5)
    protocol_version: str = Field(default="2024-11-05")
    declared_capabilities: List[str] = Field(default_factory=lambda: ["tools"])
    allow_internal_mock: bool = False


class CreateMCPConnectionRequest(BaseModel):
    server_id: str
    credential_reference: Optional[str] = None
    authorization_scopes: List[str] = Field(default_factory=lambda: ["tools:read", "resources:read"])


class InvokeMCPToolRequest(BaseModel):
    tool_id: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


# Custom Tools
class RegisterCustomToolRequest(BaseModel):
    tool_id: str = Field(min_length=3, max_length=120)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="")
    version: str = Field(default="1.0.0")
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_scopes: List[str] = Field(default_factory=list)
    side_effect_class: str = Field(default="READ_ONLY")
    execution_adapter: str = Field(default="TRANSFORMATION")
    timeout_seconds: int = 15
    declarative_config: Dict[str, Any] = Field(default_factory=dict)


class TestCustomToolRequest(BaseModel):
    tool_id: str
    input_payload: Dict[str, Any]
    mock_responses: Optional[Dict[str, Any]] = None


# Plugins
class RegisterPluginRequest(BaseModel):
    plugin_id: str
    name: str
    version: str
    publisher: str
    description: str
    manifest_version: str = "1.0"
    compatible_atlas_versions: str = ">=1.0.0"
    capabilities: List[str] = Field(default_factory=lambda: ["agent_tool"])
    permissions: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    license: str = "MIT"


class InstallPluginRequest(BaseModel):
    granted_permissions: List[str] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)


# Packages (.atlas-agent)
class ExportPackageRequest(BaseModel):
    agent_id: str
    publisher_id: str = "atlas-user"
    package_id: Optional[str] = None
    version: str = "1.0.0"


class ImportPackageRequest(BaseModel):
    archive_base64: str
    granted_permissions: List[str] = Field(default_factory=lambda: ["READ_RESEARCH"])


class ValidatePackageRequest(BaseModel):
    archive_base64: str


# Templates
class InstantiateTemplateRequest(BaseModel):
    custom_name: Optional[str] = None


# Git
class CreateGitConnectionRequest(BaseModel):
    provider: str = "GITHUB"
    repository_url: str
    default_branch: str = "main"
    auth_type: str = "TOKEN"


class ImportFromGitRequest(BaseModel):
    connection_id: str
    source_path: str
    archive_base64: str
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    granted_permissions: List[str] = Field(default_factory=lambda: ["READ_RESEARCH"])


# Developer Apps
class RegisterDeveloperAppRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="")
    redirect_uris: List[str] = Field(default_factory=list)
    allowed_scopes: List[str] = Field(default_factory=lambda: ["atlas.agents:read", "atlas.tools:read"])


class IssueCredentialRequest(BaseModel):
    scopes: List[str]


# External MCP Invocation
class ExternalMCPInvokeRequest(BaseModel):
    tool_id: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    granted_scopes: List[str] = Field(default_factory=lambda: ["atlas.research:read", "atlas.companies:read", "atlas.markets:read", "atlas.workflows:read"])


# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------

@router.get("/overview", response_model=EcosystemOverviewResponse)
def get_ecosystem_overview(
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
    tools: Annotated[CustomToolRegistryService, Depends(get_tools_service)],
    packages: Annotated[AgentPackageManager, Depends(get_packages_service)],
    marketplace: Annotated[MarketplaceService, Depends(get_marketplace_service)],
    developers: Annotated[DeveloperPlatformService, Depends(get_developers_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)

    servers = mcp.list_servers()
    conns = mcp.list_connections(tenant_id=tenant_id, owner_id=owner_id)
    inst_plugins = plugins.list_installations(tenant_id=tenant_id, owner_id=owner_id)
    cust_tools = tools.list_tools()
    inst_pkgs = packages.list_installations(tenant_id=tenant_id, owner_id=owner_id)
    market_items = marketplace.search_catalog()
    dev_apps = developers.list_apps(tenant_id=tenant_id)
    recent_events = [
        {
            "event_id": e.event_id,
            "event_type": str(e.event_type),
            "resource_id": e.resource_id,
            "resource_type": e.resource_type,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in obs.list_events(tenant_id=tenant_id, limit=10)
    ]

    return {
        "mcp_servers_count": len(servers),
        "mcp_connections_count": len(conns),
        "installed_plugins_count": len(inst_plugins),
        "custom_tools_count": len(cust_tools),
        "installed_packages_count": len(inst_pkgs),
        "marketplace_items_count": len(market_items),
        "developer_apps_count": len(dev_apps),
        "recent_events": recent_events,
    }


# ---------------------------------------------------------------------------
# MCP Endpoints
# ---------------------------------------------------------------------------

@router.get("/mcp/servers")
def list_mcp_servers(
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
) -> Any:
    return [
        {
            "server_id": s.server_id,
            "publisher_id": s.publisher_id,
            "name": s.name,
            "description": s.description,
            "transport_type": str(s.transport_type),
            "endpoint_reference": s.endpoint_reference,
            "protocol_version": s.protocol_version,
            "declared_capabilities": list(s.declared_capabilities),
            "verification_status": str(s.verification_status),
            "created_at": s.created_at.isoformat(),
        }
        for s in mcp.list_servers()
    ]


@router.post("/mcp/servers")
def register_mcp_server(
    payload: RegisterMCPServerRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        transport = MCPTransportType(payload.transport_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid transport_type: {payload.transport_type}")

    try:
        server = mcp.register_server(
            server_id=payload.server_id,
            publisher_id=owner_id,
            name=payload.name,
            description=payload.description,
            transport_type=transport,
            endpoint_reference=payload.endpoint_reference,
            protocol_version=payload.protocol_version,
            declared_capabilities=tuple(payload.declared_capabilities),
            allow_internal_mock=payload.allow_internal_mock,
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.MCP_SERVER_REGISTERED,
            resource_id=server.server_id,
            resource_type="MCPServer",
        )
        return {
            "server_id": server.server_id,
            "name": server.name,
            "endpoint_reference": server.endpoint_reference,
            "status": "REGISTERED",
        }
    except MCPSSRFSecurityError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/mcp/servers/{server_id}")
def get_mcp_server_detail(
    server_id: str,
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
) -> Any:
    try:
        s = mcp.get_server(server_id)
        return {
            "server_id": s.server_id,
            "publisher_id": s.publisher_id,
            "name": s.name,
            "description": s.description,
            "transport_type": str(s.transport_type),
            "endpoint_reference": s.endpoint_reference,
            "protocol_version": s.protocol_version,
            "declared_capabilities": list(s.declared_capabilities),
            "verification_status": str(s.verification_status),
        }
    except MCPServerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/mcp/servers/{server_id}/revoke")
def revoke_mcp_server(
    server_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        revoked = mcp.revoke_server(server_id)
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.MCP_CONNECTION_REVOKED,
            resource_id=server_id,
            resource_type="MCPServer",
        )
        return {"server_id": revoked.server_id, "verification_status": str(revoked.verification_status)}
    except MCPServerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/mcp/connections")
def list_mcp_connections(
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    conns = mcp.list_connections(tenant_id=tenant_id, owner_id=owner_id)
    return [
        {
            "connection_id": c.connection_id,
            "server_id": c.server_id,
            "status": str(c.connection_status),
            "scopes": list(c.authorization_scopes),
            "tools_count": len(c.capabilities_snapshot.tools) if c.capabilities_snapshot else 0,
            "last_checked_at": c.last_checked_at.isoformat() if c.last_checked_at else None,
        }
        for c in conns
    ]


@router.post("/mcp/connections")
def create_mcp_connection(
    payload: CreateMCPConnectionRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        conn = mcp.create_connection(
            tenant_id=tenant_id,
            owner_id=owner_id,
            server_id=payload.server_id,
            credential_reference=payload.credential_reference,
            authorization_scopes=tuple(payload.authorization_scopes),
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.MCP_CONNECTION_CREATED,
            resource_id=conn.connection_id,
            resource_type="MCPConnection",
        )
        return {
            "connection_id": conn.connection_id,
            "server_id": conn.server_id,
            "status": str(conn.connection_status),
            "tools_count": len(conn.capabilities_snapshot.tools) if conn.capabilities_snapshot else 0,
        }
    except (MCPServerNotFoundError, MCPConnectionError, MCPSSRFSecurityError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/mcp/connections/{connection_id}/test")
def test_mcp_connection(
    connection_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        return mcp.test_connection(connection_id=connection_id, tenant_id=tenant_id, owner_id=owner_id)
    except (MCPConnectionError, MCPServerNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/mcp/connections/{connection_id}/disable")
def disable_mcp_connection(
    connection_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        conn = mcp.disable_connection(connection_id=connection_id, tenant_id=tenant_id, owner_id=owner_id)
        return {"connection_id": conn.connection_id, "status": str(conn.connection_status)}
    except MCPConnectionError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/mcp/connections/{connection_id}")
def revoke_mcp_connection(
    connection_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        mcp.revoke_connection(connection_id=connection_id, tenant_id=tenant_id, owner_id=owner_id)
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.MCP_CONNECTION_REVOKED,
            resource_id=connection_id,
            resource_type="MCPConnection",
        )
        return {"connection_id": connection_id, "status": "REVOKED"}
    except MCPConnectionError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/mcp/connections/{connection_id}/invoke")
def invoke_mcp_tool(
    connection_id: str,
    payload: InvokeMCPToolRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    mcp: Annotated[MCPRegistryService, Depends(get_mcp_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        res = mcp.invoke_tool(
            connection_id=connection_id,
            tool_id=payload.tool_id,
            arguments=payload.arguments,
            tenant_id=tenant_id,
            owner_id=owner_id,
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.MCP_TOOL_INVOKED,
            resource_id=payload.tool_id,
            resource_type="MCPTool",
            details={"connection_id": connection_id},
        )
        return res
    except FinancialSafetyViolationError as exc:
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.MCP_TOOL_DENIED,
            resource_id=payload.tool_id,
            resource_type="MCPTool",
            details={"reason": str(exc)},
        )
        raise HTTPException(status_code=403, detail=str(exc))
    except MCPConnectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ---------------------------------------------------------------------------
# Custom Tool Endpoints
# ---------------------------------------------------------------------------

@router.get("/tools")
def list_custom_tools(
    tools: Annotated[CustomToolRegistryService, Depends(get_tools_service)],
) -> Any:
    return [
        {
            "tool_id": t.tool_id,
            "publisher_id": t.publisher_id,
            "name": t.name,
            "description": t.description,
            "version": t.version,
            "input_schema": t.input_schema,
            "output_schema": t.output_schema,
            "side_effect_class": str(t.side_effect_class),
            "execution_adapter": str(t.execution_adapter),
            "is_published": t.is_published,
        }
        for t in tools.list_tools()
    ]


@router.post("/tools")
def register_custom_tool(
    payload: RegisterCustomToolRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    tools: Annotated[CustomToolRegistryService, Depends(get_tools_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        side_effect = ToolSideEffectClass(payload.side_effect_class)
        adapter = ToolExecutionAdapter(payload.execution_adapter)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        t = tools.register_tool(
            tool_id=payload.tool_id,
            publisher_id=owner_id,
            name=payload.name,
            description=payload.description,
            version=payload.version,
            input_schema=payload.input_schema,
            output_schema=payload.output_schema,
            required_scopes=tuple(payload.required_scopes),
            side_effect_class=side_effect,
            execution_adapter=adapter,
            timeout_seconds=payload.timeout_seconds,
            declarative_config=payload.declarative_config,
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.TOOL_REGISTERED,
            resource_id=t.tool_id,
            resource_type="CustomTool",
        )
        return {"tool_id": t.tool_id, "name": t.name, "status": "DRAFT"}
    except (CustomToolValidationError, FinancialSafetyViolationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/tools/{tool_id}")
def get_custom_tool_detail(
    tool_id: str,
    tools: Annotated[CustomToolRegistryService, Depends(get_tools_service)],
) -> Any:
    try:
        t = tools.get_tool(tool_id)
        return {
            "tool_id": t.tool_id,
            "name": t.name,
            "description": t.description,
            "version": t.version,
            "input_schema": t.input_schema,
            "output_schema": t.output_schema,
            "is_published": t.is_published,
        }
    except CustomToolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/tools/{tool_id}/publish")
def publish_custom_tool(
    tool_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    tools: Annotated[CustomToolRegistryService, Depends(get_tools_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        t = tools.publish_tool(tool_id)
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.TOOL_PUBLISHED,
            resource_id=t.tool_id,
            resource_type="CustomTool",
        )
        return {"tool_id": t.tool_id, "is_published": t.is_published}
    except CustomToolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/tools/test")
def test_custom_tool(
    payload: TestCustomToolRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    tools: Annotated[CustomToolRegistryService, Depends(get_tools_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        res = tools.test_tool(
            test_id=f"test-{payload.tool_id}",
            tool_id=payload.tool_id,
            input_payload=payload.input_payload,
            mock_responses=payload.mock_responses,
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.TOOL_TESTED,
            resource_id=payload.tool_id,
            resource_type="CustomTool",
            details={"passed": res.passed},
        )
        return {
            "test_id": res.test_id,
            "tool_id": res.tool_id,
            "passed": res.passed,
            "output_payload": res.output_payload,
            "error_message": res.error_message,
            "duration_ms": res.duration_ms,
        }
    except CustomToolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---------------------------------------------------------------------------
# Plugins Endpoints
# ---------------------------------------------------------------------------

@router.get("/plugins")
def list_plugins(
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
) -> Any:
    return [
        {
            "plugin_id": p.plugin_id,
            "name": p.name,
            "version": p.version,
            "publisher": p.publisher,
            "description": p.description,
            "capabilities": list(p.capabilities),
            "permissions": list(p.permissions),
            "dependencies": list(p.dependencies),
            "license": p.license,
        }
        for p in plugins.list_plugins()
    ]


@router.post("/plugins")
def register_plugin(
    payload: RegisterPluginRequest,
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        manifest = plugins.register_plugin(
            plugin_id=payload.plugin_id,
            name=payload.name,
            version=payload.version,
            publisher=payload.publisher,
            description=payload.description,
            manifest_version=payload.manifest_version,
            compatible_atlas_versions=payload.compatible_atlas_versions,
            capabilities=tuple(payload.capabilities),
            permissions=tuple(payload.permissions),
            dependencies=tuple(payload.dependencies),
            license=payload.license,
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.PLUGIN_REGISTERED,
            resource_id=manifest.plugin_id,
            resource_type="Plugin",
        )
        return {"plugin_id": manifest.plugin_id, "name": manifest.name}
    except PluginValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/plugins/installations")
def list_plugin_installations(
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    insts = plugins.list_installations(tenant_id=tenant_id, owner_id=owner_id)
    return [
        {
            "installation_id": i.installation_id,
            "plugin_id": i.plugin_id,
            "version": i.version,
            "status": str(i.status),
            "granted_permissions": list(i.granted_permissions),
            "installed_at": i.installed_at.isoformat(),
        }
        for i in insts
    ]


@router.post("/plugins/{plugin_id}/install")
def install_plugin(
    plugin_id: str,
    payload: InstallPluginRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        inst = plugins.install_plugin(
            plugin_id=plugin_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            granted_permissions=tuple(payload.granted_permissions),
            configuration=payload.configuration,
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.PLUGIN_INSTALLED,
            resource_id=inst.installation_id,
            resource_type="PluginInstallation",
            details={"plugin_id": plugin_id},
        )
        return {
            "installation_id": inst.installation_id,
            "plugin_id": inst.plugin_id,
            "status": str(inst.status),
        }
    except (PluginNotFoundError, PluginValidationError, PermissionDeniedEcosystemError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/plugins/installations/{installation_id}/enable")
def enable_plugin_installation(
    installation_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        inst = plugins.enable_plugin(installation_id=installation_id, tenant_id=tenant_id, owner_id=owner_id)
        return {"installation_id": inst.installation_id, "status": str(inst.status)}
    except (PluginNotFoundError, PluginRevokedError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/plugins/installations/{installation_id}/disable")
def disable_plugin_installation(
    installation_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        inst = plugins.disable_plugin(installation_id=installation_id, tenant_id=tenant_id, owner_id=owner_id)
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.PLUGIN_DISABLED,
            resource_id=installation_id,
            resource_type="PluginInstallation",
        )
        return {"installation_id": inst.installation_id, "status": str(inst.status)}
    except PluginNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/plugins/installations/{installation_id}")
def uninstall_plugin_installation(
    installation_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    plugins: Annotated[PluginRegistryService, Depends(get_plugins_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        plugins.uninstall_plugin(installation_id=installation_id, tenant_id=tenant_id, owner_id=owner_id)
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.PLUGIN_UNINSTALLED,
            resource_id=installation_id,
            resource_type="PluginInstallation",
        )
        return {"installation_id": installation_id, "status": "UNINSTALLED"}
    except PluginNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---------------------------------------------------------------------------
# Packages (.atlas-agent) Endpoints
# ---------------------------------------------------------------------------

@router.get("/packages/installations")
def list_package_installations(
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    packages: Annotated[AgentPackageManager, Depends(get_packages_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    return [
        {
            "installation_id": inst.installation_id,
            "package_id": inst.package_id,
            "package_version": inst.package_version,
            "status": inst.status,
            "agent_reference_id": inst.agent_reference_id,
            "installed_at": inst.installed_at.isoformat(),
        }
        for inst in packages.list_installations(tenant_id=tenant_id, owner_id=owner_id)
    ]


@router.post("/packages/export")
def export_agent_package(
    payload: ExportPackageRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    packages: Annotated[AgentPackageManager, Depends(get_packages_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        res = packages.export_agent(
            agent_id=payload.agent_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            publisher_id=payload.publisher_id,
            package_id=payload.package_id,
            version=payload.version,
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.PACKAGE_EXPORTED,
            resource_id=res.package_id,
            resource_type="AgentPackage",
        )
        return {
            "package_id": res.package_id,
            "version": res.version,
            "filename": res.filename,
            "sha256_hash": res.sha256_hash,
            "file_count": res.file_count,
            "archive_base64": base64.b64encode(res.archive_bytes).decode("utf-8"),
        }
    except (PackageValidationError, PackageSecurityError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/packages/validate")
def validate_agent_package(
    payload: ValidatePackageRequest,
    packages: Annotated[AgentPackageManager, Depends(get_packages_service)],
) -> Any:
    try:
        archive_bytes = base64.b64decode(payload.archive_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 payload.")

    res = packages.validate_package_bytes(archive_bytes)
    return {
        "is_valid": res.is_valid,
        "package_id": res.package_id,
        "version": res.version,
        "errors": list(res.errors),
        "warnings": list(res.warnings),
        "file_count": res.file_count,
        "total_bytes": res.total_bytes,
        "checksum_verified": res.checksum_verified,
        "secrets_detected": res.secrets_detected,
    }


@router.post("/packages/import")
def import_agent_package(
    payload: ImportPackageRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    packages: Annotated[AgentPackageManager, Depends(get_packages_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        archive_bytes = base64.b64decode(payload.archive_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 payload.")

    try:
        res = packages.import_package(
            archive_bytes=archive_bytes,
            tenant_id=tenant_id,
            owner_id=owner_id,
            granted_permissions=tuple(payload.granted_permissions),
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.PACKAGE_IMPORTED,
            resource_id=res.package_id,
            resource_type="AgentPackage",
            details={"agent_id": res.agent_id},
        )
        return {
            "package_id": res.package_id,
            "version": res.version,
            "agent_id": res.agent_id,
            "installation_status": res.installation_status,
            "installed_version": res.installed_version,
        }
    except (PackageValidationError, PackageIntegrityError, PackageSecurityError) as exc:
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.PACKAGE_REJECTED,
            resource_id="unknown",
            resource_type="AgentPackage",
            details={"reason": str(exc)},
        )
        raise HTTPException(status_code=400, detail=str(exc))


# ---------------------------------------------------------------------------
# Templates Endpoints
# ---------------------------------------------------------------------------

@router.get("/templates")
def list_ecosystem_templates(
    templates: Annotated[EcosystemTemplateService, Depends(get_templates_service)],
    kind: Optional[str] = None,
) -> Any:
    return [
        {
            "template_id": t.template_id,
            "name": t.name,
            "description": t.description,
            "kind": t.kind,
            "version": t.version,
            "category": t.category,
            "publisher_id": t.publisher_id,
            "required_capabilities": list(t.required_capabilities),
            "required_tools": list(t.required_tools),
            "required_permissions": list(t.required_permissions),
            "default_payload": t.default_payload,
        }
        for t in templates.list_templates(kind=kind)
    ]


@router.post("/templates/{template_id}/instantiate")
def instantiate_template(
    template_id: str,
    payload: InstantiateTemplateRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    templates: Annotated[EcosystemTemplateService, Depends(get_templates_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        agent = templates.instantiate_agent(
            template_id=template_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            custom_name=payload.custom_name,
        )
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "status": str(agent.status),
            "role": agent.role,
        }
    except EcosystemError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ---------------------------------------------------------------------------
# Git Integration Endpoints
# ---------------------------------------------------------------------------

@router.get("/git/connections")
def list_git_connections(
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    git_svc: Annotated[GitIntegrationService, Depends(get_git_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    return [
        {
            "connection_id": c.connection_id,
            "provider": str(c.provider),
            "repository_url": c.repository_url,
            "default_branch": c.default_branch,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
        }
        for c in git_svc.list_connections(tenant_id=tenant_id, owner_id=owner_id)
    ]


@router.post("/git/connections")
def create_git_connection(
    payload: CreateGitConnectionRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    git_svc: Annotated[GitIntegrationService, Depends(get_git_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        provider = GitProvider(payload.provider)
        conn = git_svc.create_connection(
            tenant_id=tenant_id,
            owner_id=owner_id,
            provider=provider,
            repository_url=payload.repository_url,
            default_branch=payload.default_branch,
            auth_type=payload.auth_type,
        )
        return {
            "connection_id": conn.connection_id,
            "repository_url": conn.repository_url,
            "status": conn.status,
        }
    except (PackageSecurityError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/git/connections/{connection_id}")
def delete_git_connection(
    connection_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    git_svc: Annotated[GitIntegrationService, Depends(get_git_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        git_svc.remove_connection(connection_id=connection_id, tenant_id=tenant_id, owner_id=owner_id)
        return {"connection_id": connection_id, "status": "DELETED"}
    except EcosystemError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---------------------------------------------------------------------------
# Marketplace Endpoints
# ---------------------------------------------------------------------------

@router.get("/marketplace/catalog")
def search_marketplace_catalog(
    marketplace: Annotated[MarketplaceService, Depends(get_marketplace_service)],
    q: Optional[str] = None,
    kind: Optional[str] = None,
    category: Optional[str] = None,
) -> Any:
    items = marketplace.search_catalog(query=q, kind=kind, category=category)
    return [
        {
            "item_id": i.item_id,
            "kind": i.kind,
            "name": i.name,
            "description": i.description,
            "version": i.version,
            "category": i.category,
            "publisher_id": i.publisher_id,
            "publisher_name": i.publisher_name,
            "verification_status": str(i.verification_status),
            "required_permissions": list(i.required_permissions),
            "required_dependencies": list(i.required_dependencies),
            "license": i.license,
            "is_installed": i.is_installed,
        }
        for i in items
    ]


@router.get("/marketplace/items/{item_id}")
def get_marketplace_item_detail(
    item_id: str,
    marketplace: Annotated[MarketplaceService, Depends(get_marketplace_service)],
) -> Any:
    try:
        i = marketplace.get_item(item_id)
        return {
            "item_id": i.item_id,
            "kind": i.kind,
            "name": i.name,
            "description": i.description,
            "version": i.version,
            "category": i.category,
            "publisher_id": i.publisher_id,
            "publisher_name": i.publisher_name,
            "verification_status": str(i.verification_status),
            "required_permissions": list(i.required_permissions),
            "required_dependencies": list(i.required_dependencies),
            "license": i.license,
        }
    except EcosystemError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---------------------------------------------------------------------------
# Developer Platform Endpoints
# ---------------------------------------------------------------------------

@router.get("/developers/apps")
def list_developer_apps(
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    dev_svc: Annotated[DeveloperPlatformService, Depends(get_developers_service)],
) -> Any:
    tenant_id, _ = _identity(user)
    return [
        {
            "app_id": a.app_id,
            "name": a.name,
            "description": a.description,
            "status": str(a.status),
            "allowed_scopes": list(a.allowed_scopes),
            "created_at": a.created_at.isoformat(),
        }
        for a in dev_svc.list_apps(tenant_id=tenant_id)
    ]


@router.post("/developers/apps")
def register_developer_app(
    payload: RegisterDeveloperAppRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    dev_svc: Annotated[DeveloperPlatformService, Depends(get_developers_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    app = dev_svc.register_app(
        developer_id=owner_id,
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        redirect_uris=tuple(payload.redirect_uris),
        allowed_scopes=tuple(payload.allowed_scopes),
    )
    obs.record_event(
        tenant_id=tenant_id,
        actor_id=owner_id,
        event_type=AuditEventType.DEVELOPER_APP_REGISTERED,
        resource_id=app.app_id,
        resource_type="DeveloperApp",
    )
    return {
        "app_id": app.app_id,
        "name": app.name,
        "status": str(app.status),
        "allowed_scopes": list(app.allowed_scopes),
    }


@router.post("/developers/apps/{app_id}/credentials")
def issue_app_credential(
    app_id: str,
    payload: IssueCredentialRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    dev_svc: Annotated[DeveloperPlatformService, Depends(get_developers_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        cred, raw_secret = dev_svc.issue_credential(
            app_id=app_id,
            tenant_id=tenant_id,
            scopes=tuple(payload.scopes),
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.API_CREDENTIAL_ISSUED,
            resource_id=cred.credential_id,
            resource_type="ApiCredential",
        )
        return {
            "credential_id": cred.credential_id,
            "client_id": cred.client_id,
            "client_secret": raw_secret,  # Only shown once
            "scopes": list(cred.scopes),
        }
    except (DeveloperAppNotFoundError, PermissionDeniedEcosystemError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/developers/apps/{app_id}/revoke")
def revoke_developer_app(
    app_id: str,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    dev_svc: Annotated[DeveloperPlatformService, Depends(get_developers_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        app = dev_svc.revoke_app(app_id)
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.API_CREDENTIAL_REVOKED,
            resource_id=app.app_id,
            resource_type="DeveloperApp",
        )
        return {"app_id": app.app_id, "status": str(app.status)}
    except DeveloperAppNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/developers/usage")
def get_developer_api_usage(
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    dev_svc: Annotated[DeveloperPlatformService, Depends(get_developers_service)],
) -> Any:
    tenant_id, _ = _identity(user)
    return [
        {
            "app_id": u.app_id,
            "endpoint": u.endpoint,
            "requests_count": u.requests_count,
            "errors_count": u.errors_count,
            "tokens_consumed": u.tokens_consumed,
            "last_invoked_at": u.last_invoked_at.isoformat(),
        }
        for u in dev_svc.get_usage(tenant_id=tenant_id)
    ]


# ---------------------------------------------------------------------------
# External ATLAS MCP Server Endpoints
# ---------------------------------------------------------------------------

@router.get("/external-mcp/tools")
def list_external_mcp_tools(
    ext_mcp: Annotated[ExternalAtlasMCPService, Depends(get_external_mcp_service)],
) -> Any:
    return [
        {
            "tool_id": t.tool_id,
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema,
            "output_schema": t.output_schema,
            "required_scope": t.required_scope,
            "is_read_only": t.is_read_only,
        }
        for t in ext_mcp.list_tools()
    ]


@router.post("/external-mcp/invoke")
def invoke_external_mcp_tool(
    payload: ExternalMCPInvokeRequest,
    user: Annotated[AuthPrincipal, Depends(get_current_user)],
    ext_mcp: Annotated[ExternalAtlasMCPService, Depends(get_external_mcp_service)],
    obs: Annotated[EcosystemObservabilityService, Depends(get_observability_service)],
) -> Any:
    tenant_id, owner_id = _identity(user)
    try:
        res = ext_mcp.invoke_tool(
            tool_id=payload.tool_id,
            arguments=payload.arguments,
            tenant_id=tenant_id,
            granted_scopes=tuple(payload.granted_scopes),
        )
        obs.record_event(
            tenant_id=tenant_id,
            actor_id=owner_id,
            event_type=AuditEventType.EXTERNAL_MCP_INVOKED,
            resource_id=payload.tool_id,
            resource_type="ExternalMCPTool",
            details={"success": res.success},
        )
        return {
            "tool_id": res.tool_id,
            "success": res.success,
            "output": res.output,
            "error": res.error,
            "execution_time_ms": res.execution_time_ms,
        }
    except (FinancialSafetyViolationError, PermissionDeniedEcosystemError) as exc:
        raise HTTPException(status_code=403, detail=str(exc))
