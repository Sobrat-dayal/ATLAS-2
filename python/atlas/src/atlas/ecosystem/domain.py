"""
Typed domain contracts for ATLAS Stage 149:
MCP, Plugin and Agent Ecosystem — Extensibility Platform, Agent Package System,
Developer SDK, Integration Registry, and Marketplace Foundation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, List, Optional, Tuple


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MCPTransportType(StrEnum):
    STREAMABLE_HTTP = "STREAMABLE_HTTP"
    STDIO = "STDIO"


class VerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    COMMUNITY = "COMMUNITY"
    VERIFIED_PARTNER = "VERIFIED_PARTNER"
    OFFICIAL_ATLAS = "OFFICIAL_ATLAS"


class MCPConnectionStatus(StrEnum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    FAILED = "FAILED"
    DISABLED = "DISABLED"
    REVOKED = "REVOKED"


class ToolSideEffectClass(StrEnum):
    READ_ONLY = "READ_ONLY"
    READ_RESOURCE_COST = "READ_RESOURCE_COST"
    INTERNAL_WRITE = "INTERNAL_WRITE"
    EXTERNAL_WRITE = "EXTERNAL_WRITE"


class ToolExecutionAdapter(StrEnum):
    DECLARATIVE_HTTP = "DECLARATIVE_HTTP"
    TRANSFORMATION = "TRANSFORMATION"
    MCP_FORWARD = "MCP_FORWARD"
    SANDBOXED = "SANDBOXED"


class PluginStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    VALIDATING = "VALIDATING"
    AWAITING_PERMISSION = "AWAITING_PERMISSION"
    INSTALLED = "INSTALLED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UPDATE_AVAILABLE = "UPDATE_AVAILABLE"
    REVOKED = "REVOKED"
    UNINSTALLED = "UNINSTALLED"


class PackageKind(StrEnum):
    ATLAS_AGENT = "atlas-agent"
    PLUGIN = "plugin"
    TOOL = "tool"
    WORKFLOW = "workflow"
    TEAM = "team"


class PackageStatus(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"
    REVOKED = "REVOKED"


class GitProvider(StrEnum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    GENERIC_GIT = "GENERIC_GIT"


class DeveloperAppStatus(StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class AuditEventType(StrEnum):
    MCP_SERVER_REGISTERED = "MCP_SERVER_REGISTERED"
    MCP_CONNECTION_CREATED = "MCP_CONNECTION_CREATED"
    MCP_CONNECTION_REVOKED = "MCP_CONNECTION_REVOKED"
    MCP_TOOL_DISCOVERED = "MCP_TOOL_DISCOVERED"
    MCP_TOOL_INVOKED = "MCP_TOOL_INVOKED"
    MCP_TOOL_DENIED = "MCP_TOOL_DENIED"
    PLUGIN_REGISTERED = "PLUGIN_REGISTERED"
    PLUGIN_INSTALLED = "PLUGIN_INSTALLED"
    PLUGIN_UPDATED = "PLUGIN_UPDATED"
    PLUGIN_DISABLED = "PLUGIN_DISABLED"
    PLUGIN_UNINSTALLED = "PLUGIN_UNINSTALLED"
    PACKAGE_IMPORTED = "PACKAGE_IMPORTED"
    PACKAGE_VALIDATED = "PACKAGE_VALIDATED"
    PACKAGE_REJECTED = "PACKAGE_REJECTED"
    PACKAGE_EXPORTED = "PACKAGE_EXPORTED"
    PACKAGE_PUBLISHED = "PACKAGE_PUBLISHED"
    PACKAGE_INSTALLED = "PACKAGE_INSTALLED"
    PACKAGE_REVOKED = "PACKAGE_REVOKED"
    TOOL_REGISTERED = "TOOL_REGISTERED"
    TOOL_TESTED = "TOOL_TESTED"
    TOOL_PUBLISHED = "TOOL_PUBLISHED"
    DEVELOPER_APP_REGISTERED = "DEVELOPER_APP_REGISTERED"
    API_CREDENTIAL_ISSUED = "API_CREDENTIAL_ISSUED"
    API_CREDENTIAL_REVOKED = "API_CREDENTIAL_REVOKED"
    EXTERNAL_API_INVOKED = "EXTERNAL_API_INVOKED"
    EXTERNAL_MCP_INVOKED = "EXTERNAL_MCP_INVOKED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"


# ---------------------------------------------------------------------------
# MCP Domain Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MCPToolSnapshot:
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any] = field(default_factory=dict)
    required_permissions: Tuple[str, ...] = field(default_factory=tuple)
    risk_classification: str = "READ_ONLY"
    timeout_seconds: int = 30


@dataclass(frozen=True, slots=True)
class MCPResourceSnapshot:
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


@dataclass(frozen=True, slots=True)
class MCPCapabilitySnapshot:
    tools: Tuple[MCPToolSnapshot, ...] = field(default_factory=tuple)
    resources: Tuple[MCPResourceSnapshot, ...] = field(default_factory=tuple)
    prompts: Tuple[str, ...] = field(default_factory=tuple)
    protocol_version: str = "2024-11-05"
    captured_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class MCPServerDefinition:
    server_id: str
    publisher_id: str
    name: str
    description: str
    transport_type: MCPTransportType
    endpoint_reference: str
    protocol_version: str
    declared_capabilities: Tuple[str, ...]
    security_profile: str
    verification_status: VerificationStatus
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class MCPConnection:
    connection_id: str
    tenant_id: str
    owner_id: str
    server_id: str
    credential_reference: Optional[str]
    authorization_scopes: Tuple[str, ...]
    connection_status: MCPConnectionStatus
    capabilities_snapshot: Optional[MCPCapabilitySnapshot]
    last_checked_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# Custom Tool Domain Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CustomToolDefinition:
    tool_id: str
    publisher_id: str
    name: str
    description: str
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_scopes: Tuple[str, ...]
    side_effect_class: ToolSideEffectClass
    execution_adapter: ToolExecutionAdapter
    timeout_seconds: int = 15
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    resource_policy: Dict[str, Any] = field(default_factory=dict)
    declarative_config: Dict[str, Any] = field(default_factory=dict)
    is_published: bool = False
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class CustomToolTestFixture:
    test_id: str
    tool_id: str
    input_payload: Dict[str, Any]
    mock_responses: Dict[str, Any] = field(default_factory=dict)
    expected_success: bool = True


@dataclass(frozen=True, slots=True)
class CustomToolTestResult:
    test_id: str
    tool_id: str
    passed: bool
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0
    tested_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# Plugin Domain Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    publisher: str
    description: str
    manifest_version: str = "1.0"
    compatible_atlas_versions: str = ">=1.0.0"
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    permissions: Tuple[str, ...] = field(default_factory=tuple)
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    entrypoints: Dict[str, str] = field(default_factory=dict)
    integrity_hash: str = ""
    license: str = "MIT"


@dataclass(frozen=True, slots=True)
class PluginInstallation:
    installation_id: str
    tenant_id: str
    owner_id: str
    plugin_id: str
    version: str
    status: PluginStatus
    granted_permissions: Tuple[str, ...]
    configuration: Dict[str, Any] = field(default_factory=dict)
    installed_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# .atlas-agent Package Domain Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtlasAgentPackageManifest:
    manifest_version: str
    package_id: str
    name: str
    version: str
    kind: str
    description: str
    publisher: Dict[str, Any]
    compatibility: Dict[str, str]
    requirements: Dict[str, List[str]]
    permissions: Tuple[str, ...]
    entrypoint: str = "agent/definition.json"


@dataclass(frozen=True, slots=True)
class PackageValidationResult:
    is_valid: bool
    package_id: Optional[str] = None
    version: Optional[str] = None
    manifest: Optional[AtlasAgentPackageManifest] = None
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    file_count: int = 0
    total_bytes: int = 0
    checksum_verified: bool = False
    secrets_detected: bool = False


@dataclass(frozen=True, slots=True)
class PackageExportResult:
    package_id: str
    version: str
    filename: str
    archive_bytes: bytes
    sha256_hash: str
    file_count: int
    exported_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class PackageImportResult:
    package_id: str
    version: str
    agent_id: str
    installation_status: str
    installed_version: str
    requires_configuration: bool
    missing_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    imported_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class PackageInstallation:
    installation_id: str
    tenant_id: str
    owner_id: str
    package_id: str
    package_version: str
    status: str  # DRAFT, INSTALLED, ACTIVE, DISABLED, REVOKED
    permission_grants: Tuple[str, ...]
    agent_reference_id: Optional[str] = None
    installed_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# Templates Domain Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EcosystemTemplate:
    template_id: str
    name: str
    description: str
    kind: str  # AGENT, TEAM, WORKFLOW
    version: str
    category: str
    publisher_id: str
    required_capabilities: Tuple[str, ...] = field(default_factory=tuple)
    required_tools: Tuple[str, ...] = field(default_factory=tuple)
    required_permissions: Tuple[str, ...] = field(default_factory=tuple)
    default_payload: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# Git Integration Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GitConnection:
    connection_id: str
    tenant_id: str
    owner_id: str
    provider: GitProvider
    repository_url: str
    default_branch: str
    auth_type: str  # TOKEN, OAUTH
    status: str  # CONNECTED, DISCONNECTED, FAILED
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class GitImportProvenance:
    connection_id: str
    repository_url: str
    commit_sha: str
    branch: str
    source_path: str
    package_id: str
    imported_by: str
    imported_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# Marketplace & Publisher Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Publisher:
    publisher_id: str
    owner_id: str
    tenant_id: str
    display_name: str
    description: str
    verification_status: VerificationStatus
    contact_email: str = ""
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# Developer Platform Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DeveloperApp:
    app_id: str
    developer_id: str
    tenant_id: str
    name: str
    description: str
    redirect_uris: Tuple[str, ...] = field(default_factory=tuple)
    allowed_scopes: Tuple[str, ...] = field(default_factory=tuple)
    status: DeveloperAppStatus = DeveloperAppStatus.ACTIVE
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class ApiCredential:
    credential_id: str
    app_id: str
    tenant_id: str
    client_id: str
    client_secret_hash: str
    scopes: Tuple[str, ...]
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class DeveloperUsageRecord:
    app_id: str
    tenant_id: str
    endpoint: str
    requests_count: int
    errors_count: int
    tokens_consumed: int
    last_invoked_at: datetime = field(default_factory=utc_now)


# ---------------------------------------------------------------------------
# External ATLAS MCP Server Entities
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExternalMCPToolDefinition:
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_scope: str
    is_read_only: bool = True


@dataclass(frozen=True, slots=True)
class ExternalMCPInvocationResult:
    tool_id: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


# ---------------------------------------------------------------------------
# Ecosystem Audit Event
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EcosystemAuditEvent:
    event_id: str
    tenant_id: str
    actor_id: str
    event_type: AuditEventType
    resource_id: str
    resource_type: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=utc_now)

