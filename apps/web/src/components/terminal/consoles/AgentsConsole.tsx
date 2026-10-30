"use client";

import React, { useEffect, useState } from "react";
import { fetchAgentStatuses } from "@/lib/terminal/api";
import { AgentStatusRecord, TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { Bot, ShieldAlert, RefreshCw } from "lucide-react";

interface AgentsConsoleProps {
  session: TerminalSession;
  preferences: TerminalUserPreferences;
}

export function AgentsConsole({ preferences }: AgentsConsoleProps) {
  const [agents, setAgents] = useState<AgentStatusRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAgentStatuses();
      setAgents(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load agent statuses";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
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
          <Bot className="h-3.5 w-3.5 text-atlas-accent" />
          <span className="text-atlas-text-primary font-semibold">Agents Operational Inspector</span>
          <span className="text-zinc-500">&bull;</span>
          <span className="text-zinc-400">Source: Registered Platform Agents</span>
        </div>
        <button
          type="button"
          onClick={loadAgents}
          title="Refresh Agents Status"
          className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Notice Banner */}
      <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-950/20 border-b border-amber-900/30 text-amber-300 text-[11px] select-none">
        <ShieldAlert className="h-3.5 w-3.5 text-amber-400 shrink-0" />
        <span>
          Stage 122 provides read-only operational monitoring. Starting autonomous agents or executing agent workflows from Terminal is disabled.
        </span>
      </div>

      {/* Agents Table */}
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
                <th className="py-2 px-3">Agent Identifier</th>
                <th className="py-2 px-3">Display Name</th>
                <th className="py-2 px-3">State</th>
                <th className="py-2 px-3">Source</th>
                <th className="py-2 px-3">Scope</th>
                <th className="py-2 px-3">Last Activity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle/40">
              {agents.map((agent) => (
                <tr key={agent.agent_id} className="hover:bg-atlas-surface-hover/50 transition-colors">
                  <td className="py-2 px-3 font-semibold text-atlas-accent">{agent.agent_id}</td>
                  <td className="py-2 px-3 text-atlas-text-primary">{agent.display_name}</td>
                  <td className="py-2 px-3">
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {agent.state}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-atlas-text-muted">{agent.source}</td>
                  <td className="py-2 px-3 text-atlas-text-muted">{agent.permission_scope}</td>
                  <td className="py-2 px-3 text-atlas-text-muted">
                    {agent.last_activity_at ? new Date(agent.last_activity_at).toLocaleTimeString() : "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

