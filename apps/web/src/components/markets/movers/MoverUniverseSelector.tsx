"use client";

import React from "react";
import { Layers } from "lucide-react";
import { MoverUniverseDefinition } from "@/lib/markets/movers";

export interface MoverUniverseSelectorProps {
  universes: MoverUniverseDefinition[];
  selectedUniverseId: string;
  onSelectUniverse: (universeId: string) => void;
  disabled?: boolean;
}

export function MoverUniverseSelector({
  universes,
  selectedUniverseId,
  onSelectUniverse,
  disabled,
}: MoverUniverseSelectorProps) {
  if (!universes || universes.length === 0) return null;

  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-2">
      <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)] font-medium">
        <Layers className="h-3.5 w-3.5 text-zinc-400" />
        <span>Universe:</span>
      </div>

      <div
        role="group"
        aria-label="Select ranking universe"
        className="flex flex-wrap items-center gap-1.5 p-1 bg-[var(--atlas-surface-card)] rounded-md border border-[var(--atlas-border-subtle)]"
      >
        {universes.map((univ) => {
          const isSelected = univ.universe_id === selectedUniverseId;
          return (
            <button
              key={univ.universe_id}
              type="button"
              disabled={disabled || !univ.is_active}
              onClick={() => onSelectUniverse(univ.universe_id)}
              className={`inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded transition-all focus:outline-none focus:ring-1 focus:ring-emerald-500/50 ${
                isSelected
                  ? "bg-zinc-800 text-emerald-400 font-semibold shadow-sm border border-emerald-500/30"
                  : "text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] hover:bg-zinc-800/50 border border-transparent"
              } disabled:opacity-40 disabled:cursor-not-allowed`}
              title={`${univ.display_name} (${univ.asset_class.toUpperCase()})`}
            >
              <span>{univ.display_name}</span>
              <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-zinc-900/60 text-zinc-400 border border-zinc-700/40 uppercase">
                {univ.asset_class}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
