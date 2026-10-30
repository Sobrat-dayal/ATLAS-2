"use client";

import React, { useEffect, useState } from "react";
import { fetchMcpConnections } from "@/lib/terminal/api";
import { McpConnectionRecord, TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { Network, ShieldAlert, RefreshCw } from "lucide-react";

interface McpConsoleProps {
  session: TerminalSession;
  preferences: TerminalUserPreferences;
}

export function McpConsole({ preferences }: McpConsoleProps) {
  const [connections, setConnections] = useState<McpConnectionRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadConnections = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchMcpConnections();
      setConnections(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load MCP connections";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConnections();
  }, []);

  return (
    <div
      className="flex flex-col flex-1 h-full bg-atlas-surface-0 overflow-hidden font-mono"
      style={{
        fontSize: `${preferences.font_size}px`,
        fontFamily: preferences.font_family,
        lineHeight: preferences.line_height,
      }}
    >
      {/* Subheader */}
      <div className="flex items-center justify-between px-3 py-1 bg-atlas-surface-1 border-b border-atlas-border-subtle text-[11px] select-none text-atlas-text-muted">
        <div className="flex items-center gap-2">
          <Network className="h-3.5 w-3.5 text-atlas-accent" />
          <span className="text-atlas-text-primary font-semibold">Model Context Protocol (MCP) Registry</span>
          <span className="text-zinc-500">&bull;</span>
          <span className="text-zinc-400">Source: mcp/configs</span>
        </div>
        <button
          type="button"
          onClick={loadConnections}
          title="Refresh MCP Connections"
          className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Notice Banner */}
      <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-950/20 border-b border-amber-900/30 text-amber-300 text-[11px] select-none">
        <ShieldAlert className="h-3.5 w-3.5 text-amber-400 shrink-0" />
        <span>
          Stage 122 provides read-only MCP connection inspection. Direct tool invocation or agent execution from Terminal is disabled.
        </span>
      </div>

      {/* MCP Table */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-3">
        {error && (
          <div className="p-2 text-xs text-rose-400 bg-rose-950/20 rounded border border-rose-800/30 mb-3">
            {error}
          </div>
        )}

        <div className="border border-atlas-border-subtle rounded-md overflow-hidden bg-atlas-surface-1/40">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-subtle bg-atlas-surface-1 text-atlas-text-muted uppercase text-[10px] tracking-wider">
                <th className="py-2 px-3">Server Identifier</th>
                <th className="py-2 px-3">Display Name</th>
                <th className="py-2 px-3">Status</th>
                <th className="py-2 px-3">Available Tools</th>
                <th className="py-2 px-3">Resources</th>
                <th className="py-2 px-3">Configured In</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle/40">
              {connections.map((conn) => (
                <tr key={conn.server_id} className="hover:bg-atlas-surface-hover/50 transition-colors">
                  <td className="py-2 px-3 font-semibold text-atlas-accent">{conn.server_id}</td>
                  <td className="py-2 px-3 text-atlas-text-primary">{conn.display_name}</td>
                  <td className="py-2 px-3">
                    <span
                      className={`px-1.5 py-0.2 rounded text-[9px] font-bold uppercase border ${
                        conn.status === "CONFIGURED" || conn.status === "CONNECTED"
                          ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                          : "bg-zinc-500/15 text-zinc-400 border-zinc-500/30"
                      }`}
                    >
                      {conn.status}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-atlas-text-muted">{conn.available_tools_count}</td>
                  <td className="py-2 px-3 text-atlas-text-muted">{conn.resources_count}</td>
                  <td className="py-2 px-3 text-atlas-text-muted">{conn.configured_in}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

