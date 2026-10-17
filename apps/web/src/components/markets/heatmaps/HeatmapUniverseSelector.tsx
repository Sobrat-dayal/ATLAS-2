"use client";

import React from "react";
import { HeatmapUniverseDefinition } from "@/lib/markets/heatmaps";

interface HeatmapUniverseSelectorProps {
  universes: HeatmapUniverseDefinition[];
  selectedUniverseId: string;
  onSelectUniverse: (id: string) => void;
  disabled?: boolean;
}

export function HeatmapUniverseSelector({
  universes,
  selectedUniverseId,
  onSelectUniverse,
  disabled = false,
}: HeatmapUniverseSelectorProps) {
  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor="heatmap-universe-select"
        className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)]"
      >
        Universe
      </label>
      <select
        id="heatmap-universe-select"
        value={selectedUniverseId}
        onChange={(e) => onSelectUniverse(e.target.value)}
        disabled={disabled}
        className="h-8 px-2.5 text-xs font-medium rounded bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] hover:border-[var(--atlas-border-default)] focus:outline-none focus:ring-1 focus:ring-[var(--atlas-accent-primary)] cursor-pointer disabled:opacity-50"
      >
        {universes.map((u) => (
          <option key={u.universe_id} value={u.universe_id}>
            {u.display_name} ({u.asset_class.toUpperCase()})
          </option>
        ))}
      </select>
    </div>
  );
}
