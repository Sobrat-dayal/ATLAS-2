"use client";

import React from "react";
import { CrossAssetUniverseDefinition } from "@/lib/markets/cross-asset";
import { Globe } from "lucide-react";

interface CrossAssetUniverseSelectorProps {
  universes: CrossAssetUniverseDefinition[];
  selectedUniverseId: string;
  onSelectUniverse: (id: string) => void;
  isLoading: boolean;
}

export function CrossAssetUniverseSelector({
  universes,
  selectedUniverseId,
  onSelectUniverse,
  isLoading,
}: CrossAssetUniverseSelectorProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label
        htmlFor="cross-asset-universe-select"
        className="text-[11px] font-medium text-[var(--atlas-text-secondary)] uppercase tracking-wider flex items-center gap-1.5"
      >
        <Globe className="w-3.5 h-3.5 text-indigo-400" />
        <span>Market Universe</span>
      </label>
      <div className="relative">
        <select
          id="cross-asset-universe-select"
          value={selectedUniverseId}
          onChange={(e) => onSelectUniverse(e.target.value)}
          disabled={isLoading || universes.length === 0}
          className="w-full sm:w-72 bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] text-xs rounded border border-[var(--atlas-border-subtle)] px-2.5 py-1.5 focus:outline-none focus:border-[var(--atlas-border-focus)] transition-colors disabled:opacity-50 cursor-pointer"
        >
          {universes.map((u) => (
            <option key={u.universe_id} value={u.universe_id}>
              {u.display_name} ({u.member_count} assets)
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
