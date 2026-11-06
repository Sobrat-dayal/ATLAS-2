"use client";

import React, { useState } from "react";
import type { TeamDefinition } from "@/lib/agents/types";

interface TeamRegistryProps {
  initialTeams?: TeamDefinition[];
  onPublishTeam?: (teamId: string) => void;
  onActivateTeam?: (teamId: string) => void;
  onDisableTeam?: (teamId: string) => void;
  onSelectTeam?: (team: TeamDefinition) => void;
  onCreateTeamClick?: () => void;
}

export const TeamRegistry: React.FC<TeamRegistryProps> = ({
  initialTeams = [],
  onPublishTeam,
  onActivateTeam,
  onDisableTeam,
  onSelectTeam,
  onCreateTeamClick,
}) => {
  const [teams, setTeams] = useState<TeamDefinition[]>(initialTeams);

  const statusColor = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return "text-emerald-400 bg-emerald-950/40 border-emerald-800";
      case "PUBLISHED":
        return "text-blue-400 bg-blue-950/40 border-blue-800";
      case "PAUSED":
        return "text-amber-400 bg-amber-950/40 border-amber-800";
      case "DISABLED":
        return "text-zinc-500 bg-zinc-900 border-zinc-700";
      default:
        return "text-zinc-400 bg-zinc-900 border-zinc-800";
    }
  };

  return (
    <div className="space-y-4 text-zinc-200">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-100">
            AI Teams Registry
          </h2>
          <p className="text-xs text-zinc-400">
            Configured multi-agent worker squads with coordinator, specialists, and reviewers.
          </p>
        </div>
        {onCreateTeamClick && (
          <button
            onClick={onCreateTeamClick}
            className="rounded border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-xs font-medium text-zinc-200 hover:bg-zinc-700 transition"
          >
            + Build Team
          </button>
        )}
      </div>

      <div className="overflow-x-auto rounded border border-zinc-800 bg-[#0c0c0c]">
        <table className="w-full text-left text-xs font-mono">
          <thead className="border-b border-zinc-800 bg-[#121212] text-zinc-400">
            <tr>
              <th className="px-3 py-2">Team Name</th>
              <th className="px-3 py-2">Objective</th>
              <th className="px-3 py-2">Coordinator</th>
              <th className="px-3 py-2">Members</th>
              <th className="px-3 py-2">Version</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Budget</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {teams.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-3 py-6 text-center text-zinc-500">
                  No multi-agent teams configured. Build a new team to begin collaborative orchestration.
                </td>
              </tr>
            ) : (
              teams.map((t) => (
                <tr
                  key={t.team_id}
                  onClick={() => onSelectTeam?.(t)}
                  className="hover:bg-zinc-900/40 cursor-pointer transition"
                >
                  <td className="px-3 py-2 font-medium text-zinc-200">
                    <div>{t.name}</div>
                    <div className="text-[10px] text-zinc-500 font-normal">{t.description}</div>
                  </td>
                  <td className="px-3 py-2 text-zinc-400 max-w-xs truncate">{t.objective}</td>
                  <td className="px-3 py-2 text-indigo-400 font-medium">
                    {t.coordinator_agent_id ? `${t.coordinator_agent_id.slice(0, 10)}...` : "Assigned"}
                  </td>
                  <td className="px-3 py-2 text-zinc-300">{t.members.length} agents</td>
                  <td className="px-3 py-2 text-zinc-400">v{t.version}</td>
                  <td className="px-3 py-2">
                    <span className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold border ${statusColor(t.status)}`}>
                      {t.status}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-zinc-300">${t.budget_limit_usd.toFixed(2)}</td>
                  <td className="px-3 py-2 text-right space-x-1" onClick={(e) => e.stopPropagation()}>
                    {t.status === "DRAFT" && (
                      <button
                        onClick={() => onPublishTeam?.(t.team_id)}
                        className="rounded border border-blue-800 bg-blue-950/30 px-2 py-0.5 text-[10px] text-blue-400 hover:bg-blue-900/50"
                      >
                        Publish
                      </button>
                    )}
                    {t.status === "PUBLISHED" && (
                      <button
                        onClick={() => onActivateTeam?.(t.team_id)}
                        className="rounded border border-emerald-800 bg-emerald-950/30 px-2 py-0.5 text-[10px] text-emerald-400 hover:bg-emerald-900/50"
                      >
                        Activate
                      </button>
                    )}
                    {t.status !== "DISABLED" && (
                      <button
                        onClick={() => onDisableTeam?.(t.team_id)}
                        className="rounded border border-zinc-700 bg-zinc-900 px-2 py-0.5 text-[10px] text-zinc-400 hover:bg-zinc-800"
                      >
                        Disable
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

