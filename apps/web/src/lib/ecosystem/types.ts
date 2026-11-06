/**
 * TypeScript domain contracts for ATLAS Stage 149 Ecosystem.
 */

export type MCPTransportType = "STREAMABLE_HTTP" | "STDIO";
export type VerificationStatus = "UNVERIFIED" | "COMMUNITY" | "VERIFIED_PARTNER" | "OFFICIAL_ATLAS";
export type MCPConnectionStatus = "DISCONNECTED" | "CONNECTING" | "CONNECTED" | "FAILED" | "DISABLED" | "REVOKED";
export type PluginStatus = "DISCOVERED" | "VALIDATING" | "AWAITING_PERMISSION" | "INSTALLED" | "ENABLED" | "DISABLED" | "UPDATE_AVAILABLE" | "REVOKED" | "UNINSTALLED";
export type ToolSideEffectClass = "READ_ONLY" | "READ_RESOURCE_COST" | "INTERNAL_WRITE" | "EXTERNAL_WRITE";
export type ToolExecutionAdapter = "DECLARATIVE_HTTP" | "TRANSFORMATION" | "MCP_FORWARD" | "SANDBOXED";

export interface MCPToolSnapshot {
  tool_id: string;
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
  required_permissions: string[];
  risk_classification: string;
  timeout_seconds?: number;
}

export interface MCPResourceSnapshot {
  uri: string;
  name: string;
  description: string;
  mime_type: string;
}

export interface MCPCapabilitySnapshot {
  tools: MCPToolSnapshot[];
  resources: MCPResourceSnapshot[];
  prompts: string[];
  protocol_version: string;
  captured_at: string;
}

export interface MCPServerDefinition {
  server_id: string;
  publisher_id: string;
  name: string;
  description: string;
  transport_type: MCPTransportType;
  endpoint_reference: string;
  protocol_version: string;
  declared_capabilities: string[];
  verification_status: VerificationStatus;
  created_at?: string;
}

export interface MCPConnection {
  connection_id: string;
  server_id: string;
  status: MCPConnectionStatus;
  scopes: string[];
  tools_count: number;
  last_checked_at?: string | null;
}

export interface CustomToolDefinition {
  tool_id: string;
  publisher_id: string;
  name: string;
  description: string;
  version: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  side_effect_class: ToolSideEffectClass;
  execution_adapter: ToolExecutionAdapter;
  is_published: boolean;
}

export interface CustomToolTestResult {
  test_id: string;
  tool_id: string;
  passed: boolean;
  output_payload?: Record<string, unknown> | null;
  error_message?: string | null;
  duration_ms: number;
}

export interface PluginManifest {
  plugin_id: string;
  name: string;
  version: string;
  publisher: string;
  description: string;
  capabilities: string[];
  permissions: string[];
  dependencies: string[];
  license: string;
}

export interface PluginInstallation {
  installation_id: string;
  plugin_id: string;
  version: string;
  status: PluginStatus;
  granted_permissions: string[];
  installed_at: string;
}

export interface AtlasAgentPackageManifest {
  manifest_version: string;
  package_id: string;
  name: string;
  version: string;
  kind: string;
  description: string;
  publisher: Record<string, unknown>;
  compatibility: Record<string, string>;
  requirements: Record<string, string[]>;
  permissions: string[];
  entrypoint: string;
}

export interface PackageValidationResult {
  is_valid: boolean;
  package_id?: string | null;
  version?: string | null;
  errors: string[];
  warnings: string[];
  file_count: number;
  total_bytes: number;
  checksum_verified: boolean;
  secrets_detected: boolean;
}

export interface PackageInstallation {
  installation_id: string;
  package_id: string;
  package_version: string;
  status: string;
  agent_reference_id?: string | null;
  installed_at: string;
}

export interface EcosystemTemplate {
  template_id: string;
  name: string;
  description: string;
  kind: "AGENT" | "TEAM" | "WORKFLOW";
  version: string;
  category: string;
  publisher_id: string;
  required_capabilities: string[];
  required_tools: string[];
  required_permissions: string[];
  default_payload: Record<string, unknown>;
}

export interface GitConnection {
  connection_id: string;
  provider: "GITHUB" | "GITLAB" | "GENERIC_GIT";
  repository_url: string;
  default_branch: string;
  status: string;
  created_at: string;
}

export interface MarketplaceItem {
  item_id: string;
  kind: "AGENT" | "TEAM" | "WORKFLOW" | "TOOL" | "MCP" | "PLUGIN";
  name: string;
  description: string;
  version: string;
  category: string;
  publisher_id: string;
  publisher_name: string;
  verification_status: VerificationStatus;
  required_permissions: string[];
  required_dependencies: string[];
  license: string;
  is_installed?: boolean;
}

export interface DeveloperApp {
  app_id: string;
  name: string;
  description: string;
  status: "ACTIVE" | "REVOKED";
  allowed_scopes: string[];
  created_at: string;
}

export interface ApiCredential {
  credential_id: string;
  client_id: string;
  client_secret?: string;
  scopes: string[];
}

export interface DeveloperUsageRecord {
  app_id: string;
  endpoint: string;
  requests_count: number;
  errors_count: number;
  tokens_consumed: number;
  last_invoked_at: string;
}

export interface EcosystemOverview {
  mcp_servers_count: number;
  mcp_connections_count: number;
  installed_plugins_count: number;
  custom_tools_count: number;
  installed_packages_count: number;
  marketplace_items_count: number;
  developer_apps_count: number;
  recent_events: Array<{
    event_id: string;
    event_type: string;
    resource_id: string;
    resource_type: string;
    timestamp: string;
  }>;
}
