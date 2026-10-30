"use client";

import React from "react";
import { ArrowUpRight, BarChart3, LineChart } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface EconomicsPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

const MACRO_SERIES = [
  { series: "US CPI (YoY)", current: "2.40%", previous: "2.50%", releaseDate: "Oct 2026", impact: "High" },
  { series: "US Core PCE (YoY)", current: "2.70%", previous: "2.80%", releaseDate: "Oct 2026", impact: "High" },
  { series: "Fed Funds Upper Target", current: "4.75%", previous: "5.00%", releaseDate: "Sep 2026", impact: "High" },
  { series: "US Unemployment Rate", current: "4.10%", previous: "4.20%", releaseDate: "Oct 2026", impact: "Medium" },
  { series: "Non-Farm Payrolls", current: "+254K", previous: "+159K", releaseDate: "Oct 2026", impact: "High" },
  { series: "US Real GDP (Annualized)", current: "+2.80%", previous: "+3.00%", releaseDate: "Q3 2026", impact: "Medium" },
];

export function EconomicsPanelAdapter({}: EconomicsPanelAdapterProps) {
  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
        <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
          <LineChart className="w-3.5 h-3.5 text-blue-400" />
          <span>Macro & Economic Indicators</span>
        </div>
        <span className="text-[10px] text-atlas-text-muted">US Macro</span>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar p-2">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-default text-[10px] text-atlas-text-muted uppercase">
              <th className="py-1 px-2">Indicator Series</th>
              <th className="py-1 px-2 text-right">Actual</th>
              <th className="py-1 px-2 text-right">Prior</th>
              <th className="py-1 px-2 text-right">Release</th>
            </tr>
          </thead>
          <tbody>
            {MACRO_SERIES.map((s) => (
              <tr key={s.series} className="border-b border-atlas-border-subtle hover:bg-atlas-surface-hover">
                <td className="py-1.5 px-2 font-bold text-atlas-text-primary">{s.series}</td>
                <td className="py-1.5 px-2 text-right text-emerald-400 font-semibold">{s.current}</td>
                <td className="py-1.5 px-2 text-right text-atlas-text-muted">{s.previous}</td>
                <td className="py-1.5 px-2 text-right text-[10px] text-atlas-text-muted">{s.releaseDate}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

