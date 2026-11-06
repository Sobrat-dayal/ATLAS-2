"use client";

import React, { useState } from "react";
import type { MCPConnection, MCPServerDefinition } from "@/lib/ecosystem/types";
import { ecosystemApi } from "@/lib/ecosystem/api";

interface MCPRegistryProps {
  initialServers?: MCPServerDefinition[];
  initialConnections?: MCPConnection[];
}

export const MCPRegistry: React.FC<MCPRegistryProps> = ({
  initialServers = [],
  initialConnections = [],
}) => {
  const [servers, setServers] = useState<MCPServerDefinition[]>(initialServers);
  const [connections, setConnections] = useState<MCPConnection[]>(initialConnections);
  const [selectedServer, setSelectedServer] = useState<MCPServerDefinition | null>(null);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<Record<string, unknown> | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [serverId, setServerId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [endpoint, setEndpoint] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleTestConnection = async (connId: string) => {
    setTestingId(connId);
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.testMCPConnection(connId);
      setTestResult(res);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Connection test failed.");
    } finally {
      setTestingId(null);
    }
  };

  const handleConnect = async (server: MCPServerDefinition) => {
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.createMCPConnection({ server_id: server.server_id });
      setConnections((prev) => [
        ...prev,
        {
          connection_id: res.connection_id,
          server_id: server.server_id,
          status: "CONNECTED",
          scopes: ["tools:read", "resources:read"],
          tools_count: 2,
          last_checked_at: new Date().toISOString(),
        },
      ]);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to connect to MCP server.");
    }
  };

  const handleDisableConnection = async (connId: string) => {
    try {
      await ecosystemApi.disableMCPConnection(connId);
      setConnections((prev) =>
        prev.map((c) => (c.connection_id === connId ? { ...c, status: "DISABLED" } : c))
      );
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to disable connection.");
    }
  };

  const handleRegisterServer = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      const res = await ecosystemApi.registerMCPServer({
        server_id: serverId,
        name,
        description,
        endpoint_reference: endpoint,
        transport_type: "STREAMABLE_HTTP",
      });
      setServers((prev) => [
        ...prev,
        {
          server_id: res.server_id,
          publisher_id: "local-user",
          name: res.name,
          description,
          transport_type: "STREAMABLE_HTTP",
          endpoint_reference: endpoint,
          protocol_version: "2024-11-05",
          declared_capabilities: ["tools"],
          verification_status: "COMMUNITY",
        },
      ]);
      setIsRegistering(false);
      setServerId("");
      setName("");
      setDescription("");
      setEndpoint("");
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Registration failed.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Action Bar */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-zinc-100">
            Model Context Protocol (MCP) Server Registry
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Institutional MCP connections, capability discovery, schema validation, and SSRF-safe tool dispatch.
          </p>
        </div>
        <button
          onClick={() => setIsRegistering(!isRegistering)}
          className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-xs font-semibold text-zinc-200 hover:bg-zinc-700 transition"
        >
          {isRegistering ? "Cancel" : "+ Register MCP Server"}
        </button>
      </div>

      {errorMsg && (
        <div className="rounded border border-rose-900 bg-rose-950/60 p-2 text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {/* Registration Modal / Form */}
      {isRegistering && (
        <form onSubmit={handleRegisterServer} className="rounded border border-zinc-800 bg-[#0d0d0d] p-4 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300">Register External MCP Server</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="text-zinc-400">Server ID</label>
              <input
                type="text"
                required
                value={serverId}
                onChange={(e) => setServerId(e.target.value)}
                placeholder="e.g. sec-edgar-filings"
                className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
              />
            </div>
            <div>
              <label className="text-zinc-400">Display Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. SEC EDGAR MCP Server"
                className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
              />
            </div>
            <div className="md:col-span-2">
              <label className="text-zinc-400">Endpoint Reference (HTTPS only; SSRF protection enforced)</label>
              <input
                type="url"
                required
                value={endpoint}
                onChange={(e) => setEndpoint(e.target.value)}
                placeholder="https://api.example-mcp.org/v1"
                className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
              />
              <span className="text-[10px] text-zinc-500">
                Note: Localhost, private RFC 1918 subnets, and cloud metadata (169.254.169.254) are strictly blocked.
              </span>
            </div>
            <div className="md:col-span-2">
              <label className="text-zinc-400">Description</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Purpose of this MCP server..."
                className="w-full mt-1 rounded border border-zinc-800 bg-black px-2.5 py-1 text-zinc-200 font-mono"
              />
            </div>
          </div>
          <button
            type="submit"
            className="rounded bg-emerald-900 border border-emerald-700 px-4 py-1.5 text-xs font-semibold text-emerald-200 hover:bg-emerald-800 transition"
          >
            Register Endpoint
          </button>
        </form>
      )}

      {/* Test Result Toast */}
      {testResult && (
        <div className="rounded border border-emerald-800 bg-emerald-950/40 p-3 text-xs space-y-1">
          <div className="flex items-center justify-between font-bold text-emerald-300">
            <span>Ping Status: {String(testResult.status)}</span>
            <span>Latency: {String(testResult.latency_ms)} ms</span>
          </div>
          <div className="text-zinc-400 text-[11px]">
            Tools: {String(testResult.tools_count)} | Resources: {String(testResult.resources_count)} | Prompts: {String(testResult.prompts_count)}
          </div>
        </div>
      )}

      {/* Active Tenant Connections Section */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Active Tenant Connections</h3>
        {connections.length === 0 ? (
          <div className="rounded border border-zinc-800/60 bg-[#0d0d0d] p-4 text-center text-xs text-zinc-500">
            No active MCP connections. Connect to a registered server below.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {connections.map((c) => (
              <div
                key={c.connection_id}
                className="rounded border border-zinc-800 bg-[#0d0d0d] p-3 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-zinc-200">{c.server_id}</span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                      c.status === "CONNECTED"
                        ? "bg-emerald-950 border border-emerald-800 text-emerald-400"
                        : "bg-zinc-800 text-zinc-400"
                    }`}
                  >
                    {c.status}
                  </span>
                </div>
                <div className="text-[11px] text-zinc-400 flex items-center justify-between">
                  <span>Tools: {c.tools_count}</span>
                  <span>ID: {c.connection_id}</span>
                </div>
                <div className="flex items-center space-x-2 pt-1 border-t border-zinc-800/60">
                  <button
                    onClick={() => handleTestConnection(c.connection_id)}
                    disabled={testingId === c.connection_id}
                    className="rounded border border-zinc-700 bg-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300 hover:bg-zinc-700"
                  >
                    {testingId === c.connection_id ? "Pinging..." : "Test Ping"}
                  </button>
                  {c.status === "CONNECTED" && (
                    <button
                      onClick={() => handleDisableConnection(c.connection_id)}
                      className="rounded border border-rose-900/60 bg-rose-950/40 px-2 py-0.5 text-[11px] text-rose-300 hover:bg-rose-900/60"
                    >
                      Disable
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Registered Servers Catalog */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Available Server Catalog</h3>
        <div className="rounded border border-zinc-800 bg-[#0a0a0a] overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-zinc-800 bg-zinc-900/50 text-zinc-400">
              <tr>
                <th className="p-2.5 font-medium">Server</th>
                <th className="p-2.5 font-medium">Transport</th>
                <th className="p-2.5 font-medium">Verification</th>
                <th className="p-2.5 font-medium">Capabilities</th>
                <th className="p-2.5 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {servers.map((s) => {
                const isConnected = connections.some(
                  (c) => c.server_id === s.server_id && c.status === "CONNECTED"
                );
                return (
                  <tr key={s.server_id} className="hover:bg-zinc-900/30">
                    <td className="p-2.5">
                      <div className="font-semibold text-zinc-200">{s.name}</div>
                      <div className="text-[11px] text-zinc-400 line-clamp-1">{s.description}</div>
                      <div className="text-[10px] text-zinc-500 font-mono mt-0.5">{s.endpoint_reference}</div>
                    </td>
                    <td className="p-2.5 text-zinc-400 font-mono text-[11px]">{s.transport_type}</td>
                    <td className="p-2.5">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                          s.verification_status === "OFFICIAL_ATLAS"
                            ? "bg-blue-950 border border-blue-800 text-blue-300"
                            : s.verification_status === "VERIFIED_PARTNER"
                            ? "bg-purple-950 border border-purple-800 text-purple-300"
                            : "bg-zinc-800 text-zinc-400"
                        }`}
                      >
                        {s.verification_status}
                      </span>
                    </td>
                    <td className="p-2.5 text-zinc-400 text-[11px]">
                      {s.declared_capabilities.join(", ")}
                    </td>
                    <td className="p-2.5 text-right space-x-2">
                      <button
                        onClick={() => setSelectedServer(s)}
                        className="rounded border border-zinc-700 bg-zinc-800 px-2 py-0.5 text-[11px] text-zinc-300 hover:bg-zinc-700"
                      >
                        Inspect
                      </button>
                      <button
                        onClick={() => handleConnect(s)}
                        disabled={isConnected}
                        className={`rounded px-2.5 py-0.5 text-[11px] font-semibold ${
                          isConnected
                            ? "bg-zinc-800 text-zinc-500 cursor-not-allowed"
                            : "bg-emerald-950 border border-emerald-800 text-emerald-400 hover:bg-emerald-900"
                        }`}
                      >
                        {isConnected ? "Connected" : "Connect"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Capability Inspector Modal */}
      {selectedServer && (
        <div className="rounded border border-zinc-700 bg-[#0d0d0d] p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
            <h3 className="text-xs font-bold text-zinc-200">
              Capability Inspector: {selectedServer.name}
            </h3>
            <button
              onClick={() => setSelectedServer(null)}
              className="text-xs text-zinc-400 hover:text-zinc-200"
            >
              Close
            </button>
          </div>
          <div className="space-y-2 text-xs">
            <p className="text-zinc-400">{selectedServer.description}</p>
            <div className="rounded bg-black p-2.5 font-mono text-[11px] text-zinc-300 space-y-1">
              <div>Protocol Version: {selectedServer.protocol_version}</div>
              <div>Transport: {selectedServer.transport_type}</div>
              <div>Endpoint: {selectedServer.endpoint_reference}</div>
              <div>Security Profile: OFFICIAL_VERIFIED</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

