"use client";

import React, { useState } from "react";
import type {
  CustomToolDefinition,
  CustomToolTestResult,
  DeveloperApp,
  GitConnection,
} from "@/lib/ecosystem/types";
import { ecosystemApi } from "@/lib/ecosystem/api";

interface DeveloperDashboardProps {
  initialTools?: CustomToolDefinition[];
  initialApps?: DeveloperApp[];
  initialGitConnections?: GitConnection[];
}

export const DeveloperDashboard: React.FC<DeveloperDashboardProps> = ({
  initialTools = [],
  initialApps = [],
  initialGitConnections = [],
}) => {
  const [activeSubTab, setActiveSubTab] = useState<"tools" | "apps" | "git" | "sdk">("tools");
  const [tools, setTools] = useState<CustomToolDefinition[]>(initialTools);
  const [apps, setApps] = useState<DeveloperApp[]>(initialApps);
  const [gitConnections, setGitConnections] = useState<GitConnection[]>(initialGitConnections);

  // Tool editor state
  const [toolId, setToolId] = useState("");
  const [toolName, setToolName] = useState("");
  const [toolDesc, setToolDesc] = useState("");
  const [inputSchemaStr, setInputSchemaStr] = useState('{\n  "type": "object",\n  "properties": {\n    "query": {"type": "string"}\n  },\n  "required": ["query"]\n}');
  const [outputSchemaStr, setOutputSchemaStr] = useState('{\n  "type": "object",\n  "properties": {\n    "result": {"type": "string"}\n  },\n  "required": ["result"]\n}');
  const [testPayloadStr, setTestPayloadStr] = useState('{\n  "query": "financial statements"\n}');
  const [testResult, setTestResult] = useState<CustomToolTestResult | null>(null);

  // App & Credential state
  const [appName, setAppName] = useState("");
  const [appDesc, setAppDesc] = useState("");
  const [newCred, setNewCred] = useState<{ client_id: string; client_secret: string } | null>(null);

  // Git state
  const [gitUrl, setGitUrl] = useState("");
  const [gitBranch, setGitBranch] = useState("main");

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // --- Handlers ---
  const handleRegisterTool = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      const inSchema = JSON.parse(inputSchemaStr);
      const outSchema = JSON.parse(outputSchemaStr);
      const res = await ecosystemApi.registerCustomTool({
        tool_id: toolId,
        name: toolName,
        description: toolDesc,
        input_schema: inSchema,
        output_schema: outSchema,
      });
      setSuccessMsg(`Tool '${res.name}' registered successfully.`);
      setTools((prev) => [
        ...prev,
        {
          tool_id: res.tool_id,
          publisher_id: "local-dev",
          name: res.name,
          description: toolDesc,
          version: "1.0.0",
          input_schema: inSchema,
          output_schema: outSchema,
          side_effect_class: "READ_ONLY",
          execution_adapter: "TRANSFORMATION",
          is_published: false,
        },
      ]);
      setToolId("");
      setToolName("");
      setToolDesc("");
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to register tool.");
    }
  };

  const handleTestTool = async () => {
    setErrorMsg(null);
    try {
      const payload = JSON.parse(testPayloadStr);
      const res = await ecosystemApi.testCustomTool({
        tool_id: toolId || tools[0]?.tool_id || "atlas.custom.discounted_cash_flow",
        input_payload: payload,
      });
      setTestResult(res);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Test execution failed.");
    }
  };

  const handleRegisterApp = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.registerDeveloperApp({
        name: appName,
        description: appDesc,
        allowed_scopes: ["atlas.agents:read", "atlas.tools:read", "atlas.research:read"],
      });
      setApps((prev) => [
        ...prev,
        {
          app_id: res.app_id,
          name: res.name,
          description: appDesc,
          status: "ACTIVE",
          allowed_scopes: ["atlas.agents:read", "atlas.tools:read"],
          created_at: new Date().toISOString(),
        },
      ]);
      setAppName("");
      setAppDesc("");
      setSuccessMsg(`App '${res.name}' created.`);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to create app.");
    }
  };

  const handleIssueCredential = async (appId: string) => {
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.issueAppCredential(appId, ["atlas.agents:read", "atlas.tools:read"]);
      setNewCred({ client_id: res.client_id, client_secret: res.client_secret });
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to issue credential.");
    }
  };

  const handleCreateGitConn = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.createGitConnection({
        provider: "GITHUB",
        repository_url: gitUrl,
        default_branch: gitBranch,
      });
      setGitConnections((prev) => [
        ...prev,
        {
          connection_id: res.connection_id,
          provider: "GITHUB",
          repository_url: gitUrl,
          default_branch: gitBranch,
          status: "CONNECTED",
          created_at: new Date().toISOString(),
        },
      ]);
      setGitUrl("");
      setSuccessMsg("Git repository connection created.");
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to connect Git repository.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Sub-Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-zinc-800 pb-3 gap-2">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-100">
            Developer Platform &amp; Integration Lab
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Custom Tool SDK, Testing Lab, Scoped External APIs, Git Repository integration, and developer documentation.
          </p>
        </div>

        <div className="flex rounded border border-zinc-800 bg-[#111] p-0.5 text-xs">
          {(["tools", "apps", "git", "sdk"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveSubTab(tab)}
              className={`rounded px-3 py-1 font-medium transition ${
                activeSubTab === tab
                  ? "bg-zinc-800 text-zinc-100 shadow"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {tab === "tools"
                ? "Custom Tools"
                : tab === "apps"
                ? "Developer Apps"
                : tab === "git"
                ? "Git Integration"
                : "SDK & Docs"}
            </button>
          ))}
        </div>
      </div>

      {errorMsg && (
        <div className="rounded border border-rose-900 bg-rose-950/60 p-2.5 text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {successMsg && (
        <div className="rounded border border-emerald-800 bg-emerald-950/60 p-2.5 text-xs text-emerald-300">
          {successMsg}
        </div>
      )}

      {/* --- SUBTAB: Custom Tools & Testing Lab --- */}
      {activeSubTab === "tools" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Tool Registration Form */}
            <form onSubmit={handleRegisterTool} className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3 text-xs">
              <h3 className="font-bold uppercase tracking-wider text-zinc-300">Register Custom Tool</h3>
              <div>
                <label className="text-zinc-400">Tool ID (Namespace: atlas.custom.*)</label>
                <input
                  type="text"
                  required
                  value={toolId}
                  onChange={(e) => setToolId(e.target.value)}
                  placeholder="atlas.custom.pe_ratio_calculator"
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
                />
              </div>
              <div>
                <label className="text-zinc-400">Tool Name</label>
                <input
                  type="text"
                  required
                  value={toolName}
                  onChange={(e) => setToolName(e.target.value)}
                  placeholder="P/E Ratio Calculator"
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
                />
              </div>
              <div>
                <label className="text-zinc-400">Description</label>
                <input
                  type="text"
                  value={toolDesc}
                  onChange={(e) => setToolDesc(e.target.value)}
                  placeholder="Calculates trailing and forward price-to-earnings ratios."
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
                />
              </div>
              <div>
                <label className="text-zinc-400">Input Schema (JSON Schema)</label>
                <textarea
                  rows={4}
                  value={inputSchemaStr}
                  onChange={(e) => setInputSchemaStr(e.target.value)}
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono text-[11px]"
                />
              </div>
              <div>
                <label className="text-zinc-400">Output Schema (JSON Schema)</label>
                <textarea
                  rows={4}
                  value={outputSchemaStr}
                  onChange={(e) => setOutputSchemaStr(e.target.value)}
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono text-[11px]"
                />
              </div>
              <button
                type="submit"
                className="rounded bg-emerald-900 border border-emerald-700 px-3 py-1.5 font-semibold text-emerald-200 hover:bg-emerald-800"
              >
                Register Custom Tool
              </button>
            </form>

            {/* Testing Lab */}
            <div className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3 text-xs flex flex-col justify-between">
              <div className="space-y-3">
                <h3 className="font-bold uppercase tracking-wider text-zinc-300">Tool Testing Lab</h3>
                <p className="text-zinc-400 text-[11px]">
                  Execute custom transformation tools with mock inputs. Validates input compliance and verifies output adherence to the declared output schema.
                </p>
                <div>
                  <label className="text-zinc-400">Test Input Payload (JSON)</label>
                  <textarea
                    rows={6}
                    value={testPayloadStr}
                    onChange={(e) => setTestPayloadStr(e.target.value)}
                    className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono text-[11px]"
                  />
                </div>
                <button
                  onClick={handleTestTool}
                  className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 font-semibold text-zinc-200 hover:bg-zinc-700"
                >
                  Run Schema Test
                </button>
              </div>

              {testResult && (
                <div
                  className={`rounded border p-3 text-xs space-y-1 font-mono ${
                    testResult.passed
                      ? "border-emerald-800 bg-emerald-950/40 text-emerald-300"
                      : "border-rose-900 bg-rose-950/40 text-rose-300"
                  }`}
                >
                  <div className="font-bold">
                    Result: {testResult.passed ? "PASSED (Schema Compliant)" : "FAILED"}
                  </div>
                  <div className="text-[11px]">Execution Time: {testResult.duration_ms} ms</div>
                  {testResult.output_payload && (
                    <pre className="text-[10px] mt-1 bg-black p-2 rounded overflow-x-auto text-zinc-300">
                      {JSON.stringify(testResult.output_payload, null, 2)}
                    </pre>
                  )}
                  {testResult.error_message && (
                    <div className="text-[11px] text-rose-300">{testResult.error_message}</div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Registered Custom Tools Table */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
              Registered Custom Tools ({tools.length})
            </h3>
            <div className="rounded border border-zinc-800 bg-[#0a0a0a] overflow-hidden text-xs">
              <table className="w-full text-left">
                <thead className="border-b border-zinc-800 bg-zinc-900/50 text-zinc-400">
                  <tr>
                    <th className="p-2.5 font-medium">Tool ID</th>
                    <th className="p-2.5 font-medium">Name</th>
                    <th className="p-2.5 font-medium">Adapter</th>
                    <th className="p-2.5 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {tools.map((t) => (
                    <tr key={t.tool_id} className="hover:bg-zinc-900/30">
                      <td className="p-2.5 font-mono text-zinc-300">{t.tool_id}</td>
                      <td className="p-2.5 text-zinc-200">{t.name}</td>
                      <td className="p-2.5 font-mono text-zinc-400 text-[11px]">{t.execution_adapter}</td>
                      <td className="p-2.5">
                        <span
                          className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                            t.is_published
                              ? "bg-emerald-950 border border-emerald-800 text-emerald-400"
                              : "bg-zinc-800 text-zinc-400"
                          }`}
                        >
                          {t.is_published ? "PUBLISHED" : "DRAFT"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* --- SUBTAB: Developer Applications & API Keys --- */}
      {activeSubTab === "apps" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Register App Form */}
            <form onSubmit={handleRegisterApp} className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3 text-xs">
              <h3 className="font-bold uppercase tracking-wider text-zinc-300">Register External Application</h3>
              <div>
                <label className="text-zinc-400">Application Name</label>
                <input
                  type="text"
                  required
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  placeholder="e.g. Risk Analytics Python Service"
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
                />
              </div>
              <div>
                <label className="text-zinc-400">Description</label>
                <input
                  type="text"
                  value={appDesc}
                  onChange={(e) => setAppDesc(e.target.value)}
                  placeholder="External analytics worker."
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
                />
              </div>
              <button
                type="submit"
                className="rounded bg-emerald-900 border border-emerald-700 px-3 py-1.5 font-semibold text-emerald-200 hover:bg-emerald-800"
              >
                Register Application
              </button>
            </form>

            {/* Issued Credential Modal */}
            {newCred && (
              <div className="rounded border border-amber-800 bg-amber-950/30 p-4 space-y-2 text-xs font-mono">
                <div className="font-bold text-amber-300">
                  New API Credential Issued — Copy Secret Now!
                </div>
                <p className="text-[11px] text-zinc-300">
                  The client secret is displayed once only. It is hashed using SHA-256 before storing.
                </p>
                <div className="bg-black p-2.5 rounded border border-zinc-800 space-y-1">
                  <div>Client ID: <span className="text-emerald-400">{newCred.client_id}</span></div>
                  <div>Client Secret: <span className="text-amber-400">{newCred.client_secret}</span></div>
                </div>
                <button
                  onClick={() => setNewCred(null)}
                  className="rounded border border-zinc-700 bg-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300"
                >
                  I Have Secured My Secret
                </button>
              </div>
            )}
          </div>

          {/* Registered Apps Table */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
              Registered Applications ({apps.length})
            </h3>
            <div className="rounded border border-zinc-800 bg-[#0a0a0a] overflow-hidden text-xs">
              <table className="w-full text-left">
                <thead className="border-b border-zinc-800 bg-zinc-900/50 text-zinc-400">
                  <tr>
                    <th className="p-2.5 font-medium">App ID</th>
                    <th className="p-2.5 font-medium">Name</th>
                    <th className="p-2.5 font-medium">Status</th>
                    <th className="p-2.5 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {apps.map((app) => (
                    <tr key={app.app_id} className="hover:bg-zinc-900/30">
                      <td className="p-2.5 font-mono text-zinc-400">{app.app_id}</td>
                      <td className="p-2.5 text-zinc-200">{app.name}</td>
                      <td className="p-2.5">
                        <span
                          className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                            app.status === "ACTIVE"
                              ? "bg-emerald-950 border border-emerald-800 text-emerald-400"
                              : "bg-rose-950 border border-rose-800 text-rose-400"
                          }`}
                        >
                          {app.status}
                        </span>
                      </td>
                      <td className="p-2.5 text-right space-x-2">
                        {app.status === "ACTIVE" && (
                          <button
                            onClick={() => handleIssueCredential(app.app_id)}
                            className="rounded border border-zinc-700 bg-zinc-800 px-2.5 py-0.5 text-[11px] text-zinc-300 hover:bg-zinc-700"
                          >
                            + Issue API Key
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* --- SUBTAB: Git Integrations --- */}
      {activeSubTab === "git" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <form onSubmit={handleCreateGitConn} className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3 text-xs">
              <h3 className="font-bold uppercase tracking-wider text-zinc-300">Connect Git Repository</h3>
              <div>
                <label className="text-zinc-400">Repository URL (HTTPS or SSH)</label>
                <input
                  type="text"
                  required
                  value={gitUrl}
                  onChange={(e) => setGitUrl(e.target.value)}
                  placeholder="https://github.com/my-org/my-agent-repo.git"
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
                />
              </div>
              <div>
                <label className="text-zinc-400">Default Branch</label>
                <input
                  type="text"
                  value={gitBranch}
                  onChange={(e) => setGitBranch(e.target.value)}
                  className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
                />
              </div>
              <button
                type="submit"
                className="rounded bg-emerald-900 border border-emerald-700 px-3 py-1.5 font-semibold text-emerald-200 hover:bg-emerald-800"
              >
                Save Repository Connection
              </button>
            </form>

            <div className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-2 text-xs">
              <h3 className="font-bold uppercase tracking-wider text-zinc-300">Git Provenance Security</h3>
              <p className="text-zinc-400 text-[11px]">
                Importing agent packages from Git records the immutable commit SHA, publisher signature, and import timestamp.
                Destructive remote actions like force-pushing or automated script execution are barred.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
              Connected Repositories ({gitConnections.length})
            </h3>
            <div className="rounded border border-zinc-800 bg-[#0a0a0a] overflow-hidden text-xs">
              <table className="w-full text-left">
                <thead className="border-b border-zinc-800 bg-zinc-900/50 text-zinc-400">
                  <tr>
                    <th className="p-2.5 font-medium">Provider</th>
                    <th className="p-2.5 font-medium">Repository URL</th>
                    <th className="p-2.5 font-medium">Branch</th>
                    <th className="p-2.5 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {gitConnections.map((conn) => (
                    <tr key={conn.connection_id} className="hover:bg-zinc-900/30">
                      <td className="p-2.5 font-mono text-zinc-300">{conn.provider}</td>
                      <td className="p-2.5 font-mono text-zinc-200">{conn.repository_url}</td>
                      <td className="p-2.5 font-mono text-zinc-400">{conn.default_branch}</td>
                      <td className="p-2.5">
                        <span className="rounded bg-emerald-950 border border-emerald-800 px-1.5 py-0.5 text-[10px] text-emerald-400 font-semibold">
                          {conn.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* --- SUBTAB: SDK & CLI Documentation --- */}
      {activeSubTab === "sdk" && (
        <div className="space-y-4 text-xs font-mono">
          <div className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3">
            <h3 className="font-bold uppercase tracking-wider text-zinc-300 font-sans">
              ATLAS Developer CLI (`atlas-dev`)
            </h3>
            <p className="text-zinc-400 font-sans text-[11px]">
              Scaffold, validate, and build production `.atlas-agent` packages locally:
            </p>
            <pre className="rounded bg-black p-3 text-emerald-400 border border-zinc-800 overflow-x-auto text-[11px]">
{`# 1. Initialize a new agent package project
atlas-dev init agent --name "SEC Filings Analyst" --dir ./my-agent

# 2. Validate package structure, checksums & secret scanning
atlas-dev validate ./dist/my-agent-1.0.0.atlas-agent

# 3. Test a custom tool definition against sample payloads
python -m atlas.ecosystem.cli test --tool-id atlas.custom.dcf`}
            </pre>
          </div>

          <div className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3">
            <h3 className="font-bold uppercase tracking-wider text-zinc-300 font-sans">
              External ATLAS MCP Server Integration
            </h3>
            <p className="text-zinc-400 font-sans text-[11px]">
              Connect external MCP clients (Cursor, Claude Desktop, Antigravity, custom agents) to ATLAS:
            </p>
            <pre className="rounded bg-black p-3 text-zinc-300 border border-zinc-800 overflow-x-auto text-[11px]">
{`{
  "mcpServers": {
    "atlas": {
      "command": "python",
      "args": ["-m", "atlas.ecosystem.external_mcp"],
      "env": {
        "ATLAS_API_KEY": "atlas_live_xxxxxxxxxxxxxxxx",
        "ATLAS_ENDPOINT": "https://api.atlas.financial/v1"
      }
    }
  }
}`}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

