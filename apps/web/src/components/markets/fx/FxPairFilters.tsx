"use client";

import React from "react";
import { CurrencyItem } from "@/lib/markets/fx";
import { RotateCcw, Search, X } from "lucide-react";

export interface FxPairFiltersProps {
  query: string;
  onQueryChange: (q: string) => void;
  baseCurrency: string;
  onBaseCurrencyChange: (c: string) => void;
  quoteCurrency: string;
  onQuoteCurrencyChange: (c: string) => void;
  onReset: () => void;
  currencies: CurrencyItem[];
  totalMatched?: number;
}

export function FxPairFilters({
  query,
  onQueryChange,
  baseCurrency,
  onBaseCurrencyChange,
  quoteCurrency,
  onQuoteCurrencyChange,
  onReset,
  currencies,
  totalMatched,
}: FxPairFiltersProps) {
  const isFiltered =
    query.trim() !== "" || baseCurrency !== "all" || quoteCurrency !== "all";

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3.5 sm:p-4 mb-5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Left: Search input */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--atlas-text-tertiary)] pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search currency pairs, symbols (e.g. EUR/USD, JPY) or names..."
            aria-label="Search currency pairs"
            className="w-full pl-9 pr-8 py-1.5 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] placeholder-[var(--atlas-text-tertiary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          />
          {query && (
            <button
              type="button"
              onClick={() => onQueryChange("")}
              aria-label="Clear search query"
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)]"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {/* Right: Dropdowns and Reset */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Base Currency Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-medium text-[var(--atlas-text-secondary)] whitespace-nowrap">
              Base:
            </span>
            <select
              value={baseCurrency}
              onChange={(e) => onBaseCurrencyChange(e.target.value)}
              aria-label="Filter by Base Currency"
              className="py-1.5 px-2.5 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50 cursor-pointer"
            >
              <option value="all">All Base Currencies</option>
              {currencies.map((c) => (
                <option key={`base-${c.code}`} value={c.code}>
                  {c.code} ({c.name})
                </option>
              ))}
            </select>
          </div>

          {/* Quote Currency Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-medium text-[var(--atlas-text-secondary)] whitespace-nowrap">
              Quote:
            </span>
            <select
              value={quoteCurrency}
              onChange={(e) => onQuoteCurrencyChange(e.target.value)}
              aria-label="Filter by Quote Currency"
              className="py-1.5 px-2.5 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50 cursor-pointer"
            >
              <option value="all">All Quote Currencies</option>
              {currencies.map((c) => (
                <option key={`quote-${c.code}`} value={c.code}>
                  {c.code} ({c.name})
                </option>
              ))}
            </select>
          </div>

          {/* Reset Filters button */}
          {isFiltered && (
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 rounded transition-colors"
              title="Reset all filters"
            >
              <RotateCcw className="h-3 w-3" />
              <span>Reset</span>
            </button>
          )}

          {/* Matched Count */}
          {totalMatched !== undefined && (
            <span className="text-[11px] font-mono text-[var(--atlas-text-tertiary)] ml-1 whitespace-nowrap">
              {totalMatched} {totalMatched === 1 ? "pair" : "pairs"}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
