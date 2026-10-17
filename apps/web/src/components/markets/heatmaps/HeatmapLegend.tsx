"use client";

import React from "react";

export function HeatmapLegend() {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-2 rounded-md bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-[11px]">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-[var(--atlas-text-tertiary)] uppercase tracking-wider text-[10px]">
          Performance Scale
        </span>
        <div className="flex items-center gap-1">
          {/* Negative scale */}
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-red-600 text-white">
            -5%+
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-red-800 text-red-200">
            -2.5%
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-red-950 text-red-300">
            -1%
          </span>

          {/* Zero return */}
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-300 border border-zinc-700/50">
            0.00%
          </span>

          {/* Positive scale */}
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300">
            +1%
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-700 text-emerald-100">
            +2.5%
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-500 text-white">
            +5%+
          </span>
        </div>
      </div>

      {/* Explicit Missing Data Category */}
      <div className="flex items-center gap-1.5">
        <span className="inline-block w-3.5 h-3.5 rounded bg-zinc-900 border border-dashed border-zinc-600"></span>
        <span className="text-[var(--atlas-text-tertiary)]">
          Missing Data / Excluded (Never colored as 0%)
        </span>
      </div>
    </div>
  );
}
