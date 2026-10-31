"use client";

import React from "react";
import {
  Plane,
  Ship,
  Satellite,
  CloudAlert,
  Activity,
  Flame,
  Layers,
  CheckSquare,
  Square,
  Info,
} from "lucide-react";
import { LiveObservationCategory } from "@/lib/maps/live/types";
import { getCategoryLabel } from "@/lib/maps/live/freshness";

interface LiveLayerPanelProps {
  activeCategories: Set<LiveObservationCategory>;
  onToggleCategory: (cat: LiveObservationCategory) => void;
  onSelectAll: () => void;
  onClearAll: () => void;
  countsByCategory: Record<string, number>;
  onOpenSourceStatus: () => void;
}

const CATEGORIES: {
  category: LiveObservationCategory;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}[] = [
  { category: "AIRCRAFT", icon: Plane, color: "text-sky-400" },
  { category: "VESSEL", icon: Ship, color: "text-blue-400" },
  { category: "SATELLITE", icon: Satellite, color: "text-indigo-400" },
  { category: "WEATHER_ALERT", icon: CloudAlert, color: "text-amber-400" },
  { category: "EARTHQUAKE", icon: Activity, color: "text-emerald-400" },
  { category: "ACTIVE_FIRE", icon: Flame, color: "text-orange-400" },
];

export function LiveLayerPanel({
  activeCategories,
  onToggleCategory,
  onSelectAll,
  onClearAll,
  countsByCategory,
  onOpenSourceStatus,
}: LiveLayerPanelProps) {
  return (
    <div className="w-72 bg-zinc-950/95 border border-zinc-800 rounded-lg shadow-2xl backdrop-blur-md p-3.5 flex flex-col gap-3 text-xs font-mono text-zinc-300">
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-2">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span className="font-semibold tracking-wide text-zinc-100 uppercase">
            Live Physical Layers
          </span>
        </div>
        <button
          onClick={onOpenSourceStatus}
          className="text-zinc-400 hover:text-emerald-400 transition-colors p-1"
          title="View Upstream Source Health & Feeds"
        >
          <Info className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="flex items-center justify-between text-[11px] text-zinc-400 px-0.5">
        <span>Toggle Observation Feeds:</span>
        <div className="flex items-center gap-2">
          <button
            onClick={onSelectAll}
            className="hover:text-emerald-400 transition-colors underline"
          >
            All
          </button>
          <span>/</span>
          <button
            onClick={onClearAll}
            className="hover:text-rose-400 transition-colors underline"
          >
            None
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        {CATEGORIES.map(({ category, icon: Icon, color }) => {
          const isActive = activeCategories.has(category);
          const count = countsByCategory[category] || 0;

          return (
            <button
              key={category}
              onClick={() => onToggleCategory(category)}
              className={`flex items-center justify-between p-2 rounded border transition-all text-left ${
                isActive
                  ? "bg-zinc-900 border-zinc-700 text-zinc-100 shadow-sm"
                  : "bg-zinc-950/40 border-zinc-900 text-zinc-500 hover:border-zinc-800"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-4 h-4 flex items-center justify-center ${
                    isActive ? "text-emerald-400" : "text-zinc-600"
                  }`}
                >
                  {isActive ? (
                    <CheckSquare className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <Square className="w-3.5 h-3.5 text-zinc-600" />
                  )}
                </div>
                <Icon className={`w-3.5 h-3.5 ${color}`} />
                <span className="font-medium text-[11px] truncate">
                  {getCategoryLabel(category)}
                </span>
              </div>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded ${
                  isActive
                    ? "bg-zinc-800 text-zinc-300 border border-zinc-700"
                    : "bg-zinc-900/50 text-zinc-600"
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      <div className="border-t border-zinc-900 pt-2 flex items-center justify-between text-[10px] text-zinc-500">
        <span>Display Age Clock:</span>
        <span className="text-zinc-400">Physical (observed_at)</span>
      </div>
    </div>
  );
}
