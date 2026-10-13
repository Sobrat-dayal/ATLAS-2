"use client";

import React from "react";
import { MarketGroupSummary } from "@/lib/markets/types";

export interface MarketsGroupSelectorProps {
  groups: MarketGroupSummary[];
  selectedGroup: string;
  onSelectGroup: (groupId: string) => void;
}

export function MarketsGroupSelector({
  groups,
  selectedGroup,
  onSelectGroup,
}: MarketsGroupSelectorProps) {
  if (!groups || groups.length === 0) return null;

  return (
    <div
      role="tablist"
      aria-label="Filter market asset classes"
      className="flex items-center gap-1.5 overflow-x-auto pb-1 mb-4 no-scrollbar border-b border-[var(--atlas-border-subtle)]"
    >
      {groups.map((group) => {
        const isSelected = selectedGroup.toLowerCase() === group.id.toLowerCase();

        return (
          <button
            key={group.id}
            role="tab"
            aria-selected={isSelected}
            tabIndex={isSelected ? 0 : -1}
            onClick={() => onSelectGroup(group.id)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-t-md whitespace-nowrap transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 ${
              isSelected
                ? "bg-[var(--atlas-surface-card)] text-emerald-400 border-b-2 border-emerald-400 font-semibold"
                : "text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-card)]/50"
            }`}
          >
            <span>{group.label}</span>
            <span
              className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                isSelected
                  ? "bg-emerald-500/20 text-emerald-300"
                  : "bg-zinc-800 text-zinc-400"
              }`}
            >
              {group.count}
            </span>
          </button>
        );
      })}
    </div>
  );
}
