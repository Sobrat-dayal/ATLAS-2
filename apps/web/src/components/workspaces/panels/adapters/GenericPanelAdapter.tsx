"use client";

import React from "react";
import { BookOpen, Database, Filter, Sliders, Sparkles } from "lucide-react";
import { WorkspacePanelInstance } from "@/lib/workspaces/types";

interface GenericPanelAdapterProps {
  panel: WorkspacePanelInstance;
  context: Record<string, unknown>;
  onUpdateContext: (updates: Record<string, unknown>) => void;
  onUpdateConfig: (cfg: Record<string, unknown>) => void;
}

export function GenericPanelAdapter({
  panel,
  context,
  onUpdateContext,
}: GenericPanelAdapterProps) {
  const ptype = panel.panel_type_id;

  if (ptype === "SCREENER") {
    return (
      <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
        <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
          <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
            <Filter className="w-3.5 h-3.5 text-blue-400" />
            <span>Quantitative Screener</span>
          </div>
          <span className="text-[10px] text-atlas-text-muted">Universe: US Equities</span>
        </div>
        <div className="flex-1 overflow-auto p-2">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-default text-[10px] text-atlas-text-muted uppercase">
                <th className="py-1 px-2">Ticker</th>
                <th className="py-1 px-2 text-right">P/E</th>
                <th className="py-1 px-2 text-right">ROIC</th>
                <th className="py-1 px-2 text-right">FCF Yield</th>
              </tr>
            </thead>
            <tbody>
              {[
                { s: "AAPL", pe: "36.0x", roic: "58.2%", fcf: "3.2%" },
                { s: "MSFT", pe: "36.2x", roic: "31.4%", fcf: "2.8%" },
                { s: "NVDA", pe: "66.4x", roic: "92.1%", fcf: "1.9%" },
                { s: "GOOGL", pe: "24.1x", roic: "28.5%", fcf: "4.1%" },
              ].map((row) => (
                <tr
                  key={row.s}
                  onClick={() => onUpdateContext({ INSTRUMENT: row.s, COMPANY: row.s })}
                  className="border-b border-atlas-border-subtle hover:bg-atlas-surface-hover cursor-pointer"
                >
                  <td className="py-1.5 px-2 font-bold text-blue-400">{row.s}</td>
                  <td className="py-1.5 px-2 text-right text-atlas-text-primary">{row.pe}</td>
                  <td className="py-1.5 px-2 text-right text-emerald-400">{row.roic}</td>
                  <td className="py-1.5 px-2 text-right text-atlas-text-primary">{row.fcf}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (ptype === "RESEARCH_DOCUMENT" || ptype === "RESEARCH_REPORT") {
    return (
      <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
        <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
          <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
            <BookOpen className="w-3.5 h-3.5 text-purple-400" />
            <span>Research Document Viewer</span>
          </div>
          <span className="text-[10px] text-atlas-text-muted">Institutional</span>
        </div>
        <div className="flex-1 p-4 overflow-auto custom-scrollbar flex flex-col justify-center items-center text-center">
          <BookOpen className="w-8 h-8 text-atlas-text-muted mb-2 opacity-50" />
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            {panel.title_override || "Equity Research Thesis"}
          </h4>
          <p className="text-[11px] text-atlas-text-muted max-w-[280px] mt-1 font-sans">
            Linked to {(context.COMPANY as string) || (context.INSTRUMENT as string) || "AAPL"}.
            Select a research report or investigation to load document evidence.
          </p>
        </div>
      </div>
    );
  }

  if (ptype === "DATA_TABLE") {
    return (
      <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
        <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
          <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>Financial Data Explorer</span>
          </div>
          <span className="text-[10px] text-atlas-text-muted">Dataset</span>
        </div>
        <div className="flex-1 p-4 overflow-auto custom-scrollbar flex flex-col justify-center items-center text-center">
          <Database className="w-8 h-8 text-atlas-text-muted mb-2 opacity-50" />
          <p className="text-[11px] text-atlas-text-muted">
            Configure custom SQL query or select a data table from the Data Explorer.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
        <div className="flex items-center gap-1.5 text-atlas-text-primary text-[11px] font-semibold">
          <Sliders className="w-3.5 h-3.5 text-amber-400" />
          <span>{panel.title_override || ptype}</span>
        </div>
      </div>
      <div className="flex-1 p-4 overflow-auto custom-scrollbar flex flex-col justify-center items-center text-center">
        <Sparkles className="w-8 h-8 text-atlas-text-muted mb-2 opacity-40" />
        <h4 className="text-xs font-semibold text-atlas-text-primary mb-1">
          {panel.title_override || ptype}
        </h4>
        <p className="text-[11px] text-atlas-text-muted max-w-[280px] font-sans">
          This panel is active and linked to the workspace context engine.
        </p>
      </div>
    </div>
  );
}

