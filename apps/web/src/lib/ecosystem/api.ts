/**
 * Client API for ATLAS Stage 149 Ecosystem.
 */

import type {
  CustomToolDefinition,
  CustomToolTestResult,
  DeveloperApp,
  DeveloperUsageRecord,
  EcosystemOverview,
  EcosystemTemplate,
  GitConnection,
  MarketplaceItem,
  MCPConnection,
  MCPServerDefinition,
  PackageInstallation,
  PackageValidationResult,
  PluginInstallation,
  PluginManifest,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorBody.detail || `HTTP Error ${res.status}`);
  }
  return res.json();
}

export const ecosystemApi = {
  // Overview
  async getOverview(): Promise<EcosystemOverview> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/overview`, { credentials: "include" });
    return handleResponse<EcosystemOverview>(res);
  },

  // MCP
  async listMCPServers(): Promise<MCPServerDefinition[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/mcp/servers`, { credentials: "include" });
    return handleResponse<MCPServerDefinition[]>(res);
  },

  async registerMCPServer(payload: {
    server_id: string;
    name: string;
    description: string;
    transport_type?: string;
    endpoint_reference: string;
    allow_internal_mock?: boolean;
  }): Promise<{ server_id: string; name: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/mcp/servers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return handleResponse(res);
  },

  async listMCPConnections(): Promise<MCPConnection[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/mcp/connections`, { credentials: "include" });
    return handleResponse<MCPConnection[]>(res);
  },

  async createMCPConnection(payload: {
    server_id: string;
    authorization_scopes?: string[];
  }): Promise<{ connection_id: string; status: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/mcp/connections`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return handleResponse(res);
  },

  async testMCPConnection(connectionId: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/mcp/connections/${connectionId}/test`, {
      method: "POST",
      credentials: "include",
    });
    return handleResponse(res);
  },

  async disableMCPConnection(connectionId: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/mcp/connections/${connectionId}/disable`, {
      method: "POST",
      credentials: "include",
    });
    return handleResponse(res);
  },

  // Custom Tools
  async listCustomTools(): Promise<CustomToolDefinition[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/tools`, { credentials: "include" });
    return handleResponse<CustomToolDefinition[]>(res);
  },

  async registerCustomTool(payload: {
    tool_id: string;
    name: string;
    description: string;
    version?: string;
    input_schema: Record<string, unknown>;
    output_schema: Record<string, unknown>;
    required_scopes?: string[];
  }): Promise<{ tool_id: string; name: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/tools`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return handleResponse(res);
  },

  async testCustomTool(payload: {
    tool_id: string;
    input_payload: Record<string, unknown>;
  }): Promise<CustomToolTestResult> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/tools/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return handleResponse<CustomToolTestResult>(res);
  },

  // Plugins
  async listPlugins(): Promise<PluginManifest[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/plugins`, { credentials: "include" });
    return handleResponse<PluginManifest[]>(res);
  },

  async listPluginInstallations(): Promise<PluginInstallation[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/plugins/installations`, { credentials: "include" });
    return handleResponse<PluginInstallation[]>(res);
  },

  async installPlugin(
    pluginId: string,
    grantedPermissions: string[]
  ): Promise<{ installation_id: string; status: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/plugins/${pluginId}/install`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ granted_permissions: grantedPermissions }),
      credentials: "include",
    });
    return handleResponse(res);
  },

  async disablePlugin(installationId: string): Promise<{ installation_id: string; status: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/plugins/installations/${installationId}/disable`, {
      method: "POST",
      credentials: "include",
    });
    return handleResponse(res);
  },

  // Packages (.atlas-agent)
  async listPackageInstallations(): Promise<PackageInstallation[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/packages/installations`, { credentials: "include" });
    return handleResponse<PackageInstallation[]>(res);
  },

  async validatePackage(archiveBase64: string): Promise<PackageValidationResult> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/packages/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ archive_base64: archiveBase64 }),
      credentials: "include",
    });
    return handleResponse<PackageValidationResult>(res);
  },

  async importPackage(payload: {
    archive_base64: string;
    granted_permissions?: string[];
  }): Promise<{ package_id: string; agent_id: string; installation_status: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/packages/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return handleResponse(res);
  },

  async exportPackage(agentId: string, packageId?: string): Promise<{
    package_id: string;
    filename: string;
    archive_base64: string;
  }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/packages/export`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: agentId, package_id: packageId }),
      credentials: "include",
    });
    return handleResponse(res);
  },

  // Templates
  async listTemplates(kind?: string): Promise<EcosystemTemplate[]> {
    const url = kind ? `${BASE_URL}/api/v1/ecosystem/templates?kind=${kind}` : `${BASE_URL}/api/v1/ecosystem/templates`;
    const res = await fetch(url, { credentials: "include" });
    return handleResponse<EcosystemTemplate[]>(res);
  },

  async instantiateTemplate(templateId: string, customName?: string): Promise<{ agent_id: string; name: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/templates/${templateId}/instantiate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ custom_name: customName }),
      credentials: "include",
    });
    return handleResponse(res);
  },

  // Git
  async listGitConnections(): Promise<GitConnection[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/git/connections`, { credentials: "include" });
    return handleResponse<GitConnection[]>(res);
  },

  async createGitConnection(payload: {
    provider: string;
    repository_url: string;
    default_branch?: string;
  }): Promise<{ connection_id: string; status: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/git/connections`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return handleResponse(res);
  },

  // Marketplace
  async searchMarketplace(params?: { q?: string; kind?: string; category?: string }): Promise<MarketplaceItem[]> {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.set("q", params.q);
    if (params?.kind) searchParams.set("kind", params.kind);
    if (params?.category) searchParams.set("category", params.category);
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/marketplace/catalog?${searchParams.toString()}`, {
      credentials: "include",
    });
    return handleResponse<MarketplaceItem[]>(res);
  },

  // Developers
  async listDeveloperApps(): Promise<DeveloperApp[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/developers/apps`, { credentials: "include" });
    return handleResponse<DeveloperApp[]>(res);
  },

  async registerDeveloperApp(payload: {
    name: string;
    description: string;
    allowed_scopes?: string[];
  }): Promise<{ app_id: string; name: string }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/developers/apps`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    });
    return handleResponse(res);
  },

  async issueAppCredential(
    appId: string,
    scopes: string[]
  ): Promise<{ credential_id: string; client_id: string; client_secret: string; scopes: string[] }> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/developers/apps/${appId}/credentials`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scopes }),
      credentials: "include",
    });
    return handleResponse(res);
  },

  async getDeveloperUsage(): Promise<DeveloperUsageRecord[]> {
    const res = await fetch(`${BASE_URL}/api/v1/ecosystem/developers/usage`, { credentials: "include" });
    return handleResponse<DeveloperUsageRecord[]>(res);
  },
};
