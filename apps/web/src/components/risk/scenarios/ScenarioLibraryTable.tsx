"use client";

import React from "react";
import { RiskScenarioDTO } from "@/lib/risk/types";
import {
  Flame,
  History,
  Play,
  Plus,
  Sliders,
  TrendingDown,
  Zap,
} from "lucide-react";

interface ScenarioLibraryTableProps {
  scenarios: RiskScenarioDTO[];
  executing: boolean;
  onExecuteScenario: (scenarioId: string) => void;
  onOpenCreateModal: () => void;
  onCompareScenarios: () => void;
  comparing: boolean;
}

export function ScenarioLibraryTable({
  scenarios,
  executing,
  onExecuteScenario,
  onOpenCreateModal,
  onCompareScenarios,
  comparing,
}: ScenarioLibraryTableProps) {
  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-3">
      {/* Header and Action Controls */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-2">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-amber-400" />
          <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
            Institutional Scenario Library & Stress Testing Catalogue
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onCompareScenarios}
            disabled={comparing || scenarios.length === 0}
            className="flex items-center gap-1.5 rounded bg-atlas-surface-2 px-2.5 py-1 text-xs font-medium text-atlas-text-secondary hover:bg-atlas-surface-3 hover:text-atlas-text-primary transition border border-atlas-border-default/60 disabled:opacity-50"
          >
            <Sliders className="h-3.5 w-3.5 text-atlas-accent-blue" />
            <span>{comparing ? "Comparing..." : "Compare All"}</span>
          </button>
          <button
            onClick={onOpenCreateModal}
            className="flex items-center gap-1.5 rounded bg-atlas-accent-blue px-3 py-1 text-xs font-medium text-white hover:bg-atlas-accent-blue/90 transition shadow-sm"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>Create Custom Scenario</span>
          </button>
        </div>
      </div>

      {/* Scenario Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2 text-[11px] font-semibold text-atlas-text-secondary uppercase">
              <th className="py-2 px-3">Scenario Name</th>
              <th className="py-2 px-3">Type</th>
              <th className="py-2 px-3">Shocks Configured</th>
              <th className="py-2 px-3">Description</th>
              <th className="py-2 px-3">Status</th>
              <th className="py-2 px-3 text-right">Execute</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/40">
            {scenarios.map((scen) => {
              const isPredefined = scen.is_predefined || scen.is_system_predefined;
              return (
                <tr
                  key={scen.scenario_id}
                  className="hover:bg-atlas-surface-2/60 transition group"
                >
                  <td className="py-2.5 px-3">
                    <div className="font-bold text-atlas-text-primary flex items-center gap-1.5">
                      {isPredefined ? (
                        <History className="h-3.5 w-3.5 text-amber-400" />
                      ) : (
                        <Zap className="h-3.5 w-3.5 text-atlas-accent-blue" />
                      )}
                      {scen.name}
                    </div>
                    <div className="font-mono text-[10px] text-atlas-text-muted mt-0.5">
                      {scen.scenario_id}
                    </div>
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider ${
                        scen.scenario_type === "HISTORICAL_EPISODE"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                      }`}
                    >
                      {scen.scenario_type.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <div className="flex flex-wrap gap-1 max-w-[260px]">
                      {scen.shocks.map((sh, idx) => (
                        <span
                          key={idx}
                          className="rounded bg-atlas-surface-3 px-1.5 py-0.5 font-mono text-[10px] text-atlas-text-secondary border border-atlas-border-default/40"
                        >
                          {sh.target_identifier}:{" "}
                          <span
                            className={
                              sh.magnitude < 0 ? "text-rose-400 font-bold" : "text-emerald-400 font-bold"
                            }
                          >
                            {(sh.magnitude * 100).toFixed(1)}%
                          </span>
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-2.5 px-3 text-atlas-text-secondary max-w-[240px] truncate text-[11px]">
                    {scen.description}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="text-[10px] text-atlas-text-muted font-medium">
                      {isPredefined ? "System Predefined" : "Custom Scenario"}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={() => onExecuteScenario(scen.scenario_id)}
                      disabled={executing}
                      className="inline-flex items-center gap-1 rounded bg-amber-500/15 px-2.5 py-1 text-xs font-medium text-amber-300 hover:bg-amber-500/25 border border-amber-500/30 transition disabled:opacity-50"
                    >
                      <Play className="h-3 w-3 fill-amber-300 text-amber-300" />
                      <span>Shock</span>
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

