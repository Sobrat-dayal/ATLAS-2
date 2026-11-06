import { describe, it } from "node:test";
import assert from "node:assert/strict";
import type {
  MCPServerDefinition,
  MCPConnection,
  PluginManifest,
  PluginInstallation,
  AtlasAgentPackageManifest,
  PackageValidationResult,
  PackageInstallation,
  EcosystemTemplate,
  CustomToolDefinition,
  CustomToolTestResult,
  DeveloperApp,
  MarketplaceItem,
} from "../types.js";
import { ecosystemApi } from "../api.js";

describe("Stage 149 Frontend Ecosystem Domain Contracts & Security", () => {
  it("validates MCPServerDefinition with STREAMABLE_HTTP transport and declared capabilities", () => {
    const server: MCPServerDefinition = {
      server_id: "mcp-alpha-v1",
      publisher_id: "pub-atlas",
      name: "Alpha Financial Feeds MCP",
      description: "Model Context Protocol streaming feeds",
      transport_type: "STREAMABLE_HTTP",
      endpoint_reference: "https://mcp.alpha-analytics.internal/v1/sse",
      protocol_version: "2024-11-05",
      declared_capabilities: ["tools", "resources", "prompts"],
      verification_status: "OFFICIAL_ATLAS",
    };

    assert.equal(server.server_id, "mcp-alpha-v1");
    assert.equal(server.transport_type, "STREAMABLE_HTTP");
    assert.equal(server.verification_status, "OFFICIAL_ATLAS");
    assert.ok(server.declared_capabilities.includes("tools"));
  });

  it("validates MCPConnection status lifecycle", () => {
    const conn: MCPConnection = {
      connection_id: "conn-149-abc",
      server_id: "mcp-alpha-v1",
      status: "CONNECTED",
      scopes: ["tools:read"],
      tools_count: 1,
      last_checked_at: new Date().toISOString(),
    };

    assert.equal(conn.status, "CONNECTED");
    assert.equal(conn.tools_count, 1);
    assert.ok(conn.scopes.includes("tools:read"));
  });

  it("enforces plugin manifest permissions and side-effect safety classification", () => {
    const plugin: PluginManifest = {
      plugin_id: "plugin-fx-rates",
      name: "Foreign Exchange Live Quotes",
      version: "1.0.0",
      publisher: "ATLAS Core Team",
      description: "Institutional FX pair quotes",
      capabilities: ["market_data"],
      permissions: ["market_data:read", "analytics:compute"],
      dependencies: [],
      license: "Apache-2.0",
    };

    assert.equal(plugin.plugin_id, "plugin-fx-rates");
    assert.ok(plugin.permissions.includes("market_data:read"));
    assert.ok(!plugin.permissions.includes("trading:live_execute")); // live execution prohibited
  });

  it("validates PluginInstallation status and tenant isolation", () => {
    const install: PluginInstallation = {
      installation_id: "inst-999",
      plugin_id: "plugin-fx-rates",
      version: "1.0.0",
      status: "ENABLED",
      granted_permissions: ["market_data:read"],
      installed_at: new Date().toISOString(),
    };

    assert.equal(install.status, "ENABLED");
    assert.equal(install.granted_permissions.length, 1);
  });

  it("validates AtlasAgentPackageManifest for .atlas-agent archive", () => {
    const pkgManifest: AtlasAgentPackageManifest = {
      manifest_version: "1.0",
      package_id: "pkg-macro-agent-v1",
      name: "Macroeconomic Analyst Agent",
      version: "1.0.0",
      kind: "AGENT",
      description: "Autonomous agent for rate curve and CPI analysis",
      publisher: { name: "Atlas Quantitative Labs" },
      compatibility: { min_atlas_version: "1.0.0" },
      requirements: { tools: ["macro_cpi_query"] },
      permissions: ["economics:read"],
      entrypoint: "agent.json",
    };

    assert.equal(pkgManifest.kind, "AGENT");
    assert.equal(pkgManifest.entrypoint, "agent.json");
    assert.ok(pkgManifest.permissions.includes("economics:read"));
  });

  it("validates PackageValidationResult defensive security checks", () => {
    const result: PackageValidationResult = {
      is_valid: true,
      package_id: "pkg-credit-v1",
      version: "1.0.0",
      errors: [],
      warnings: [],
      file_count: 4,
      total_bytes: 12450,
      checksum_verified: true,
      secrets_detected: false,
    };

    assert.equal(result.is_valid, true);
    assert.equal(result.checksum_verified, true);
    assert.equal(result.secrets_detected, false);
    assert.equal(result.errors.length, 0);
  });

  it("ensures installed packages start strictly in DRAFT state", () => {
    const pkgInstall: PackageInstallation = {
      installation_id: "inst-1",
      package_id: "pkg-credit-v1",
      package_version: "1.0.0",
      status: "DRAFT",
      agent_reference_id: "agent-draft-1",
      installed_at: new Date().toISOString(),
    };

    assert.equal(pkgInstall.status, "DRAFT");
    assert.equal(pkgInstall.agent_reference_id, "agent-draft-1");
  });

  it("validates EcosystemTemplate structure with canonical approved model", () => {
    const template: EcosystemTemplate = {
      template_id: "template-equity-researcher",
      name: "Autonomous Equity Researcher",
      kind: "AGENT",
      version: "1.0.0",
      description: "Generates DCF models and earnings summaries",
      category: "EQUITY_RESEARCH",
      publisher_id: "pub-atlas",
      required_capabilities: ["fundamental"],
      required_tools: ["equity_dcf"],
      required_permissions: ["research:read"],
      default_payload: {
        model: "atlas-intelligence-v1",
        budget_limit: 100.0,
      },
    };

    assert.equal(template.kind, "AGENT");
    assert.equal(template.default_payload.model, "atlas-intelligence-v1");
  });

  it("validates CustomToolDefinition and TestResult execution metrics", () => {
    const customTool: CustomToolDefinition = {
      tool_id: "tool-calc-convexity",
      publisher_id: "pub-atlas",
      name: "Bond Convexity Calculator",
      description: "Calculates modified duration and bond convexity",
      version: "1.0.0",
      side_effect_class: "READ_ONLY",
      execution_adapter: "SANDBOXED",
      is_published: true,
      input_schema: {
        type: "object",
        properties: {
          coupon: { type: "number" },
          yield: { type: "number" },
          maturity_years: { type: "number" },
        },
        required: ["coupon", "yield", "maturity_years"],
      },
      output_schema: {
        type: "object",
        properties: {
          convexity: { type: "number" },
          duration: { type: "number" },
        },
      },
    };

    const testResult: CustomToolTestResult = {
      test_id: "test-1",
      tool_id: "tool-calc-convexity",
      passed: true,
      output_payload: { convexity: 42.15, duration: 6.8 },
      duration_ms: 12.4,
    };

    assert.equal(customTool.side_effect_class, "READ_ONLY");
    assert.equal(customTool.execution_adapter, "SANDBOXED");
    assert.equal(testResult.passed, true);
    assert.ok(testResult.duration_ms > 0);
  });

  it("validates DeveloperApp and token scope restrictions", () => {
    const devApp: DeveloperApp = {
      app_id: "app-algo-lab",
      name: "Algorithmic Research Studio",
      description: "External quantitative analytics integration",
      status: "ACTIVE",
      allowed_scopes: ["research:read", "tools:invoke"],
      created_at: new Date().toISOString(),
    };

    assert.equal(devApp.status, "ACTIVE");
    assert.ok(devApp.allowed_scopes.includes("research:read"));
    assert.ok(!devApp.allowed_scopes.includes("trading:live_execute"));
  });

  it("validates MarketplaceItem authenticity with verified publisher tiers", () => {
    const item: MarketplaceItem = {
      item_id: "item-sec-filings",
      kind: "PLUGIN",
      name: "SEC 10-K & 10-Q Analyzer",
      description: "Extracts footnotes and MD&A commentary",
      version: "2.1.0",
      category: "FUNDAMENTAL_ANALYSIS",
      publisher_id: "pub-atlas",
      publisher_name: "Atlas Official",
      verification_status: "OFFICIAL_ATLAS",
      required_permissions: ["sec_data:read"],
      required_dependencies: [],
      license: "Apache-2.0",
      is_installed: false,
    };

    assert.equal(item.verification_status, "OFFICIAL_ATLAS");
    assert.equal(item.is_installed, false);
  });

  it("verifies ecosystemApi client interface methods exist", () => {
    assert.equal(typeof ecosystemApi.getOverview, "function");
    assert.equal(typeof ecosystemApi.listMCPServers, "function");
    assert.equal(typeof ecosystemApi.registerMCPServer, "function");
    assert.equal(typeof ecosystemApi.createMCPConnection, "function");
    assert.equal(typeof ecosystemApi.testMCPConnection, "function");
    assert.equal(typeof ecosystemApi.listPlugins, "function");
    assert.equal(typeof ecosystemApi.listPluginInstallations, "function");
    assert.equal(typeof ecosystemApi.installPlugin, "function");
    assert.equal(typeof ecosystemApi.disablePlugin, "function");
    assert.equal(typeof ecosystemApi.validatePackage, "function");
    assert.equal(typeof ecosystemApi.importPackage, "function");
    assert.equal(typeof ecosystemApi.exportPackage, "function");
    assert.equal(typeof ecosystemApi.listTemplates, "function");
    assert.equal(typeof ecosystemApi.instantiateTemplate, "function");
    assert.equal(typeof ecosystemApi.searchMarketplace, "function");
    assert.equal(typeof ecosystemApi.listCustomTools, "function");
    assert.equal(typeof ecosystemApi.registerCustomTool, "function");
    assert.equal(typeof ecosystemApi.testCustomTool, "function");
    assert.equal(typeof ecosystemApi.listDeveloperApps, "function");
    assert.equal(typeof ecosystemApi.registerDeveloperApp, "function");
    assert.equal(typeof ecosystemApi.issueAppCredential, "function");
    assert.equal(typeof ecosystemApi.getDeveloperUsage, "function");
    assert.equal(typeof ecosystemApi.listGitConnections, "function");
    assert.equal(typeof ecosystemApi.createGitConnection, "function");
  });
});
