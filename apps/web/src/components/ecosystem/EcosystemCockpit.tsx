"use client";

import React, { useState, useEffect } from "react";
import { MCPRegistry } from "./mcp/MCPRegistry";
import { PluginRegistry } from "./plugins/PluginRegistry";
import { PackageRegistry } from "./packages/PackageRegistry";
import { TemplateBrowser } from "./templates/TemplateBrowser";
import { MarketplaceCatalog } from "./marketplace/MarketplaceCatalog";
import { DeveloperDashboard } from "./developers/DeveloperDashboard";
import type {
  CustomToolDefinition,
  DeveloperApp,
  EcosystemOverview,
  EcosystemTemplate,
  GitConnection,
  MarketplaceItem,
  MCPConnection,
  MCPServerDefinition,
  PackageInstallation,
  PluginInstallation,
  PluginManifest,
} from "@/lib/ecosystem/types";
import { ecosystemApi } from "@/lib/ecosystem/api";

export type EcosystemTab =
  | "overview"
  | "mcp"
  | "plugins"
  | "packages"
  | "templates"
  | "marketplace"
  | "developers";

interface EcosystemCockpitProps {
  defaultTab?: EcosystemTab;
  initialOverview?: EcosystemOverview;
  initialServers?: MCPServerDefinition[];
  initialConnections?: MCPConnection[];
  initialPlugins?: PluginManifest[];
  initialInstallations?: PluginInstallation[];
  initialPackages?: PackageInstallation[];
  initialTemplates?: EcosystemTemplate[];
  initialMarketplaceItems?: MarketplaceItem[];
  initialTools?: CustomToolDefinition[];
  initialApps?: DeveloperApp[];
  initialGitConnections?: GitConnection[];
}

export const EcosystemCockpit: React.FC<EcosystemCockpitProps> = ({
  defaultTab = "overview",
  initialOverview,
  initialServers = [],
  initialConnections = [],
  initialPlugins = [],
  initialInstallations = [],
  initialPackages = [],
  initialTemplates = [],
  initialMarketplaceItems = [],
  initialTools = [],
  initialApps = [],
  initialGitConnections = [],
}) => {
  const [activeTab, setActiveTab] = useState<EcosystemTab>(defaultTab);
  const [overview, setOverview] = useState<EcosystemOverview | null>(initialOverview || null);
  const [loadingOverview, setLoadingOverview] = useState<boolean>(!initialOverview);
  const [errorOverview, setErrorOverview] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (!initialOverview) {
      setLoadingOverview(true);
      ecosystemApi
        .getOverview()
        .then((data) => {
          if (isMounted) {
            setOverview(data);
            setLoadingOverview(false);
          }
        })
        .catch((err) => {
          if (isMounted) {
            setErrorOverview(err instanceof Error ? err.message : "Failed to load overview");
            setLoadingOverview(false);
          }
        });
    }
    return () => {
      isMounted = false;
    };
  }, [initialOverview]);

  return (
    <div className="space-y-4 p-4 min-h-[calc(100vh-4rem)] bg-[#070707] text-zinc-200 font-mono">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-zinc-800 pb-3 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold uppercase tracking-wider text-zinc-100">
              ATLAS ECOSYSTEM &amp; EXTENSIBILITY PLATFORM
            </h1>
            <span className="rounded bg-sky-950 border border-sky-800 px-1.5 py-0.5 text-[10px] text-sky-400 font-semibold">
              STAGE 149
            </span>
            <span className="rounded bg-emerald-950/60 border border-emerald-800 px-1.5 py-0.5 text-[10px] text-emerald-400 font-medium">
              SAFETY FIREWALL: SANDBOX ONLY
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Model Context Protocol registry, secure plugin sandboxes, .atlas-agent package verification, developer SDKs and truthful marketplace.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex flex-wrap rounded border border-zinc-800 bg-[#111] p-0.5 text-xs">
          <button
            onClick={() => setActiveTab("overview")}
            className={`rounded px-2.5 py-1 font-medium transition ${
              activeTab === "overview"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab("mcp")}
            className={`rounded px-2.5 py-1 font-medium transition ${
              activeTab === "mcp"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            MCP Registry
          </button>
          <button
            onClick={() => setActiveTab("plugins")}
            className={`rounded px-2.5 py-1 font-medium transition ${
              activeTab === "plugins"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Plugins
          </button>
          <button
            onClick={() => setActiveTab("packages")}
            className={`rounded px-2.5 py-1 font-medium transition ${
              activeTab === "packages"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Packages (.atlas-agent)
          </button>
          <button
            onClick={() => setActiveTab("templates")}
            className={`rounded px-2.5 py-1 font-medium transition ${
              activeTab === "templates"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Templates
          </button>
          <button
            onClick={() => setActiveTab("marketplace")}
            className={`rounded px-2.5 py-1 font-medium transition ${
              activeTab === "marketplace"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Marketplace
          </button>
          <button
            onClick={() => setActiveTab("developers")}
            className={`rounded px-2.5 py-1 font-medium transition ${
              activeTab === "developers"
                ? "bg-zinc-800 text-zinc-100 shadow"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Developer Platform
          </button>
        </div>
      </div>

      {/* Main Tab Views */}
      <div className="pt-2">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Defensive Security Banner */}
            <div className="p-3.5 rounded border border-amber-900/60 bg-amber-950/20 text-xs text-amber-200/90 flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <span className="font-bold text-amber-400 uppercase tracking-wide mr-2">
                  Institutional Security Policies Active:
                </span>
                <span>
                  1. Zero Live Trading (Read &amp; Sandbox only). 2. SSRF Protection on MCP endpoints (Localhost / RFC1918 / Cloud Metadata blocked). 3. Zip-Slip, Decompression Bomb &amp; Secret scanning enforced on package ingestion. 4. Draft-first instantiation policy.
                </span>
              </div>
              <div className="shrink-0 flex items-center space-x-2">
                <span className="px-2 py-0.5 rounded bg-emerald-900/40 border border-emerald-700 text-emerald-400 font-semibold text-[10px]">
                  AUDIT LOGGING ON
                </span>
                <span className="px-2 py-0.5 rounded bg-blue-900/40 border border-blue-700 text-blue-400 font-semibold text-[10px]">
                  MCP CLIENT V1.0
                </span>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              <div
                onClick={() => setActiveTab("mcp")}
                className="cursor-pointer p-3 rounded border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition"
              >
                <div className="text-[10px] uppercase text-zinc-500 font-semibold">MCP Servers</div>
                <div className="text-xl font-bold text-zinc-100 mt-1">
                  {loadingOverview ? "..." : overview?.mcp_servers_count ?? initialServers.length}
                </div>
                <div className="text-[10px] text-zinc-400 mt-0.5">
                  {overview?.mcp_connections_count ?? initialConnections.length} Active Connections
                </div>
              </div>

              <div
                onClick={() => setActiveTab("plugins")}
                className="cursor-pointer p-3 rounded border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition"
              >
                <div className="text-[10px] uppercase text-zinc-500 font-semibold">Plugins</div>
                <div className="text-xl font-bold text-zinc-100 mt-1">
                  {loadingOverview ? "..." : overview?.installed_plugins_count ?? initialInstallations.length}
                </div>
                <div className="text-[10px] text-emerald-400 mt-0.5">Sandboxed &amp; Scoped</div>
              </div>

              <div
                onClick={() => setActiveTab("packages")}
                className="cursor-pointer p-3 rounded border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition"
              >
                <div className="text-[10px] uppercase text-zinc-500 font-semibold">Packages</div>
                <div className="text-xl font-bold text-zinc-100 mt-1">
                  {loadingOverview ? "..." : overview?.installed_packages_count ?? initialPackages.length}
                </div>
                <div className="text-[10px] text-cyan-400 mt-0.5">.atlas-agent Verified</div>
              </div>

              <div
                onClick={() => setActiveTab("templates")}
                className="cursor-pointer p-3 rounded border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition"
              >
                <div className="text-[10px] uppercase text-zinc-500 font-semibold">Templates</div>
                <div className="text-xl font-bold text-zinc-100 mt-1">
                  {initialTemplates.length > 0 ? initialTemplates.length : 3}
                </div>
                <div className="text-[10px] text-purple-400 mt-0.5">Instant Draft Ready</div>
              </div>

              <div
                onClick={() => setActiveTab("marketplace")}
                className="cursor-pointer p-3 rounded border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition"
              >
                <div className="text-[10px] uppercase text-zinc-500 font-semibold">Marketplace</div>
                <div className="text-xl font-bold text-zinc-100 mt-1">
                  {loadingOverview ? "..." : overview?.marketplace_items_count ?? initialMarketplaceItems.length}
                </div>
                <div className="text-[10px] text-amber-400 mt-0.5">No Fake Reviews</div>
              </div>

              <div
                onClick={() => setActiveTab("developers")}
                className="cursor-pointer p-3 rounded border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition"
              >
                <div className="text-[10px] uppercase text-zinc-500 font-semibold">Custom Tools</div>
                <div className="text-xl font-bold text-zinc-100 mt-1">
                  {loadingOverview ? "..." : overview?.custom_tools_count ?? initialTools.length}
                </div>
                <div className="text-[10px] text-sky-400 mt-0.5">Schema Validated</div>
              </div>

              <div
                onClick={() => setActiveTab("developers")}
                className="cursor-pointer p-3 rounded border border-zinc-800 bg-zinc-950 hover:border-zinc-700 transition"
              >
                <div className="text-[10px] uppercase text-zinc-500 font-semibold">Developer Apps</div>
                <div className="text-xl font-bold text-zinc-100 mt-1">
                  {loadingOverview ? "..." : overview?.developer_apps_count ?? initialApps.length}
                </div>
                <div className="text-[10px] text-zinc-400 mt-0.5">API Keys &amp; Webhooks</div>
              </div>
            </div>

            {errorOverview && (
              <div className="text-xs text-red-400 bg-red-950/20 border border-red-900 p-2 rounded">
                {errorOverview}
              </div>
            )}

            {/* Quick Action Portals */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded border border-zinc-800 bg-zinc-950/60 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-200">Connect MCP Server</h3>
                  <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                    Connect external toolsets via the Model Context Protocol over Server-Sent Events (SSE) or Stdio transports with built-in SSRF protection.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab("mcp")}
                  className="mt-4 px-3 py-1.5 rounded bg-sky-950 border border-sky-800 text-sky-300 text-xs font-medium hover:bg-sky-900 transition self-start"
                >
                  Manage MCP Registry &rarr;
                </button>
              </div>

              <div className="p-4 rounded border border-zinc-800 bg-zinc-950/60 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-200">Package Importer / Exporter</h3>
                  <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                    Import or export standalone .atlas-agent packages with cryptographic SHA-256 integrity, path traversal protection and automated secret scrubbing.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab("packages")}
                  className="mt-4 px-3 py-1.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300 text-xs font-medium hover:bg-cyan-900 transition self-start"
                >
                  Open Package Lab &rarr;
                </button>
              </div>

              <div className="p-4 rounded border border-zinc-800 bg-zinc-950/60 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-200">Custom Tool Studio &amp; SDK</h3>
                  <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                    Author JSON Schema tools, execute unit test fixtures with latency benchmarks, generate scoped API credentials, and sync with Git repositories.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab("developers")}
                  className="mt-4 px-3 py-1.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 text-xs font-medium hover:bg-emerald-900 transition self-start"
                >
                  Open Developer Platform &rarr;
                </button>
              </div>
            </div>

            {/* Recent Ecosystem Audit Events */}
            <div className="rounded border border-zinc-800 bg-zinc-950 p-4">
              <div className="flex items-center justify-between mb-3 border-b border-zinc-800 pb-2">
                <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wide">
                  Recent Ecosystem Governance &amp; Audit Log
                </h3>
                <span className="text-[10px] text-zinc-500">Immutable Ledger</span>
              </div>

              {overview?.recent_events && overview.recent_events.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="text-[10px] text-zinc-500 border-b border-zinc-800 uppercase">
                      <tr>
                        <th className="py-2 px-3">Timestamp</th>
                        <th className="py-2 px-3">Event Type</th>
                        <th className="py-2 px-3">Resource Type</th>
                        <th className="py-2 px-3">Resource ID</th>
                        <th className="py-2 px-3">Event ID</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-900">
                      {overview.recent_events.map((ev) => (
                        <tr key={ev.event_id} className="hover:bg-zinc-900/40">
                          <td className="py-2 px-3 text-zinc-400">{new Date(ev.timestamp).toLocaleTimeString()}</td>
                          <td className="py-2 px-3 font-semibold text-sky-400">{ev.event_type}</td>
                          <td className="py-2 px-3 text-zinc-300">{ev.resource_type}</td>
                          <td className="py-2 px-3 font-mono text-zinc-400">{ev.resource_id}</td>
                          <td className="py-2 px-3 text-[10px] text-zinc-600 font-mono">{ev.event_id.slice(0, 8)}...</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-zinc-600">
                  No ecosystem audit events recorded yet for this session.
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "mcp" && (
          <MCPRegistry
            initialServers={initialServers}
            initialConnections={initialConnections}
          />
        )}

        {activeTab === "plugins" && (
          <PluginRegistry
            initialPlugins={initialPlugins}
            initialInstallations={initialInstallations}
          />
        )}

        {activeTab === "packages" && (
          <PackageRegistry
            initialInstallations={initialPackages}
          />
        )}

        {activeTab === "templates" && (
          <TemplateBrowser
            initialTemplates={initialTemplates}
          />
        )}

        {activeTab === "marketplace" && (
          <MarketplaceCatalog
            initialItems={initialMarketplaceItems}
          />
        )}

        {activeTab === "developers" && (
          <DeveloperDashboard
            initialTools={initialTools}
            initialApps={initialApps}
            initialGitConnections={initialGitConnections}
          />
        )}
      </div>
    </div>
  );
};
