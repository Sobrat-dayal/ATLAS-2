"use client";

import React from "react";
import {
  GodsEyeLensType,
  GodsEyeViewMode,
} from "@/lib/intelligence/gods-eye/types";
import {
  Globe,
  Radio,
  Building2,
  ShieldAlert,
  Anchor,
  Flame,
  PieChart,
  History,
  RotateCcw,
  Search,
  Eye,
  Sliders,
  Maximize2,
  Box,
  Map as MapIcon,
  Columns,
} from "lucide-react";

interface GodsEyeToolbarProps {
  activeLens: GodsEyeLensType;
  onSelectLens: (lens: GodsEyeLensType) => void;
  viewMode: GodsEyeViewMode;
  onSelectViewMode: (mode: GodsEyeViewMode) => void;
  asOfDate: string | null;
  onChangeAsOfDate: (date: string | null) => void;
  entityFilter: string;
  onChangeEntityFilter: (val: string) => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

export function GodsEyeToolbar({
  activeLens,
  onSelectLens,
  viewMode,
  onSelectViewMode,
  asOfDate,
  onChangeAsOfDate,
  entityFilter,
  onChangeEntityFilter,
  onRefresh,
  isLoading = false,
}: GodsEyeToolbarProps) {
  const lenses: Array<{ id: GodsEyeLensType; label: string; icon: React.ReactNode }> = [
    { id: "GLOBAL_EVENTS", label: "Global", icon: <Globe className="w-3.5 h-3.5" /> },
    { id: "MONETARY_POLICY", label: "Monetary", icon: <Radio className="w-3.5 h-3.5" /> },
    { id: "CORPORATE_INTELLIGENCE", label: "Corporate", icon: <Building2 className="w-3.5 h-3.5" /> },
    { id: "GEOPOLITICAL", label: "Geopolitical", icon: <ShieldAlert className="w-3.5 h-3.5" /> },
    { id: "COMMODITY_INFRASTRUCTURE", label: "Commodities", icon: <Anchor className="w-3.5 h-3.5" /> },
    { id: "PHYSICAL_WORLD", label: "Hazards", icon: <Flame className="w-3.5 h-3.5" /> },
    { id: "PORTFOLIO_INTELLIGENCE", label: "Portfolio", icon: <PieChart className="w-3.5 h-3.5" /> },
    { id: "HISTORICAL_RESEARCH", label: "History", icon: <History className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="px-3 py-2 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-2 font-mono text-xs select-none">
      {/* Left: Brand Badge & 8 Lens Selector */}
      <div className="flex items-center gap-2 overflow-x-auto">
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded shrink-0">
          <Eye className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          <span className="font-bold tracking-wider text-[11px]">GOD&apos;S EYE</span>
        </div>

        <div className="flex items-center gap-1 bg-zinc-900/90 border border-zinc-800 p-0.5 rounded">
          {lenses.map((l) => {
            const isActive = activeLens === l.id;
            return (
              <button
                key={l.id}
                onClick={() => onSelectLens(l.id)}
                className={`px-2 py-1 rounded transition-colors flex items-center gap-1 shrink-0 ${
                  isActive
                    ? "bg-amber-600 text-white font-semibold shadow"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
                title={l.label}
              >
                {l.icon}
                <span className="hidden sm:inline text-[11px]">{l.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: 2D/3D Mode, As-Of Time Travel & Search Filter */}
      <div className="flex items-center gap-2 flex-wrap">
        {/* Spatial Mode Switcher */}
        <div className="flex items-center gap-0.5 bg-zinc-900 border border-zinc-800 p-0.5 rounded">
          <button
            onClick={() => onSelectViewMode("TWO_DIMENSIONAL")}
            className={`px-2 py-0.5 rounded flex items-center gap-1 text-[11px] ${
              viewMode === "TWO_DIMENSIONAL"
                ? "bg-zinc-800 text-sky-400 font-bold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
            title="2D Map View (MapLibre)"
          >
            <MapIcon className="w-3 h-3" />
            <span>2D</span>
          </button>
          <button
            onClick={() => onSelectViewMode("THREE_DIMENSIONAL_GLOBE")}
            className={`px-2 py-0.5 rounded flex items-center gap-1 text-[11px] ${
              viewMode === "THREE_DIMENSIONAL_GLOBE"
                ? "bg-zinc-800 text-emerald-400 font-bold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
            title="3D Globe View (CesiumJS)"
          >
            <Box className="w-3 h-3" />
            <span>3D</span>
          </button>
          <button
            onClick={() => onSelectViewMode("HYBRID_SPLIT")}
            className={`px-2 py-0.5 rounded flex items-center gap-1 text-[11px] ${
              viewMode === "HYBRID_SPLIT"
                ? "bg-zinc-800 text-purple-400 font-bold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
            title="Hybrid Split Screen"
          >
            <Columns className="w-3 h-3" />
            <span>Split</span>
          </button>
        </div>

        {/* Quick Filter */}
        <div className="relative">
          <Search className="w-3 h-3 text-zinc-500 absolute left-2 top-2" />
          <input
            type="text"
            placeholder="Filter entity..."
            value={entityFilter}
            onChange={(e) => onChangeEntityFilter(e.target.value)}
            className="w-28 sm:w-36 pl-7 pr-2 py-1 rounded bg-zinc-900 border border-zinc-800 text-[11px] text-zinc-200 focus:outline-none focus:border-amber-500"
          />
        </div>

        {/* Historical As-Of Date Picker / Live Indicator */}
        {asOfDate ? (
          <div className="flex items-center gap-1 bg-amber-950/60 border border-amber-800/80 px-2 py-0.5 rounded text-amber-300 text-[10px]">
            <History className="w-3 h-3 text-amber-400" />
            <span>As-Of: {new Date(asOfDate).toLocaleDateString()}</span>
            <button
              onClick={() => onChangeAsOfDate(null)}
              className="ml-1 text-amber-400 hover:text-white font-bold"
              title="Reset to Live Knowledge"
            >
              ✕
            </button>
          </div>
        ) : (
          <button
            onClick={() => onChangeAsOfDate("2024-05-01T12:00:00Z")}
            className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded text-zinc-400 hover:text-amber-400 text-[10px] transition-colors"
            title="Enter historical time travel mode"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>LIVE WORLD</span>
          </button>
        )}

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="p-1 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-100 disabled:opacity-50"
          title="Refresh Situational Awareness"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-amber-400" : ""}`} />
        </button>
      </div>
    </div>
  );
}

