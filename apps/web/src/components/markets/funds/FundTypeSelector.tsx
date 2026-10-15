"use client";

import React from "react";
import { FundTypeOption } from "@/lib/markets/funds";

export interface FundTypeSelectorProps {
  selectedType: string;
  onSelectType: (type: string) => void;
  options?: FundTypeOption[];
}

const DEFAULT_TYPES = [
  { id: "ALL", label: "All Funds" },
  { id: "ETF", label: "ETFs" },
  { id: "OPEN_END_MUTUAL_FUND", label: "Mutual Funds" },
  { id: "CLOSED_END_FUND", label: "Closed-End Funds" },
];

export function FundTypeSelector({
  selectedType,
  onSelectType,
  options,
}: FundTypeSelectorProps) {
  const typeMap = new Map<string, number>();
  if (options) {
    options.forEach((opt) => typeMap.set(opt.id, opt.count));
  }

  return (
    <div
      role="tablist"
      aria-label="Filter funds by vehicle structure"
      className="flex items-center gap-1.5 p-1 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-lg mb-4 overflow-x-auto no-scrollbar"
    >
      {DEFAULT_TYPES.map((t) => {
        const isSelected = selectedType === t.id;
        const count = t.id === "ALL" ? undefined : typeMap.get(t.id);

        return (
          <button
            key={t.id}
            role="tab"
            aria-selected={isSelected}
            onClick={() => onSelectType(t.id)}
            className={`inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md whitespace-nowrap transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 ${
              isSelected
                ? "bg-zinc-800 text-emerald-400 font-semibold shadow-sm border border-zinc-700/60"
                : "text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] hover:bg-zinc-800/40"
            }`}
          >
            <span>{t.label}</span>
            {count !== undefined && (
              <span
                className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${
                  isSelected
                    ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/50"
                    : "bg-zinc-900 text-zinc-500 border border-zinc-800"
                }`}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
