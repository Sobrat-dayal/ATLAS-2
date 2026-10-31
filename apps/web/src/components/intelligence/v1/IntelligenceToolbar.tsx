"use client";

import React from "react";
import { IntelligenceViewType } from "@/lib/intelligence/v1/types";
import {
  Layers,
  Radio,
  Building2,
  Network,
  PieChart,
  Globe,
  Sliders,
  History,
  Database,
  Search,
  ShieldCheck,
  AlertCircle
} from "lucide-react";

interface IntelligenceToolbarProps {
  activeView: IntelligenceViewType;
  onSelectView: (view: IntelligenceViewType) => void;
  onOpenSearch: () => void;
  asOfDate?: string | null;
  degradedSourceCount?: number;
}

export function IntelligenceToolbar({
  activeView,
  onSelectView,
  onOpenSearch,
  asOfDate,
  degradedSourceCount = 0
}: IntelligenceToolbarProps) {
  const views: Array<{ id: IntelligenceViewType; label: string; icon: React.ReactNode }> = [
    { id: "OVERVIEW", label: "Overview", icon: <Layers className="w-3.5 h-3.5" /> },
    { id: "EVENTS", label: "Event Monitor", icon: <Radio className="w-3.5 h-3.5" /> },
    { id: "SCORING", label: "Priority Scoring", icon: <Sliders className="w-3.5 h-3.5" /> },
    { id: "ENTITIES", label: "Entities", icon: <Building2 className="w-3.5 h-3.5" /> },
    { id: "GRAPH", label: "Knowledge Graph", icon: <Network className="w-3.5 h-3.5" /> },
    { id: "EXPOSURE", label: "Exposure Engine", icon: <PieChart className="w-3.5 h-3.5" /> },
    { id: "GEOGRAPHY", label: "Geography", icon: <Globe className="w-3.5 h-3.5" /> },
    { id: "INVESTIGATIONS", label: "Investigations", icon: <Sliders className="w-3.5 h-3.5" /> },
    { id: "HISTORY", label: "Historical As-Of", icon: <History className="w-3.5 h-3.5" /> },
    { id: "SOURCES", label: "Data Quality", icon: <Database className="w-3.5 h-3.5" /> }
  ];

  return (
    <div className="px-3 py-2 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-2 font-mono text-xs select-none">
      {/* Primary Intelligence View Tabs */}
      <div className="flex items-center gap-1 overflow-x-auto bg-zinc-900/90 border border-zinc-800 p-0.5 rounded">
        {views.map((v) => {
          const isActive = activeView === v.id;
          return (
            <button
              key={v.id}
              onClick={() => onSelectView(v.id)}
              className={`px-2.5 py-1 rounded transition-colors flex items-center gap-1.5 shrink-0 ${
                isActive
                  ? "bg-sky-600 text-white font-semibold shadow"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {v.icon}
              <span>{v.label}</span>
            </button>
          );
        })}
      </div>

      {/* Global Actions Bar: Search, Historical As-Of Pill, Source Status */}
      <div className="flex items-center gap-2">
        {/* Global Search Trigger */}
        <button
          onClick={onOpenSearch}
          className="px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-zinc-100 flex items-center gap-1.5 transition-colors"
          title="Search events, companies, and sources (Ctrl+K)"
        >
          <Search className="w-3.5 h-3.5 text-sky-400" />
          <span className="text-[11px]">Search Intelligence...</span>
        </button>

        {/* Historical As-Of Indicator */}
        {asOfDate ? (
          <div className="px-2 py-0.5 rounded bg-amber-950/40 border border-amber-800/80 text-amber-300 text-[10px] flex items-center gap-1">
            <History className="w-3 h-3 text-amber-400" />
            <span>As-Of: {new Date(asOfDate).toLocaleDateString()}</span>
          </div>
        ) : (
          <div className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 text-[10px] flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>LIVE KNOWLEDGE</span>
          </div>
        )}

        {/* Source Health Indicator */}
        <button
          onClick={() => onSelectView("SOURCES")}
          className={`px-2 py-0.5 rounded border text-[10px] flex items-center gap-1 transition-colors ${
            degradedSourceCount > 0
              ? "bg-amber-950/30 border-amber-800 text-amber-300"
              : "bg-zinc-900 border-zinc-800 text-emerald-400"
          }`}
          title="View data sources freshness and coverage"
        >
          {degradedSourceCount > 0 ? (
            <>
              <AlertCircle className="w-3 h-3 text-amber-400" />
              <span>{degradedSourceCount} Degraded Feed</span>
            </>
          ) : (
            <>
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              <span>Feeds Healthy</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

