"use client";

import React from "react";
import {
  EquityFilterOptionsResponse,
} from "@/lib/markets/equities";
import { RotateCcw, Search } from "lucide-react";

export interface EquityDirectoryFiltersProps {
  query: string;
  onQueryChange: (q: string) => void;
  marketCountry: string;
  onCountryChange: (c: string) => void;
  exchange: string;
  onExchangeChange: (e: string) => void;
  equityType: string;
  onTypeChange: (t: string) => void;
  listingStatus: string;
  onListingStatusChange: (s: string) => void;
  onReset: () => void;
  availableFilters?: EquityFilterOptionsResponse;
  isLoading?: boolean;
}

export function EquityDirectoryFilters({
  query,
  onQueryChange,
  marketCountry,
  onCountryChange,
  exchange,
  onExchangeChange,
  equityType,
  onTypeChange,
  listingStatus,
  onListingStatusChange,
  onReset,
  availableFilters,
  isLoading,
}: EquityDirectoryFiltersProps) {
  const isFiltered =
    query.trim() !== "" ||
    marketCountry !== "all" ||
    exchange !== "all" ||
    equityType !== "all" ||
    listingStatus !== "all";

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3 mb-4">
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
        {/* Search input */}
        <div className="relative flex-1 min-w-[200px]">
          <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-[var(--atlas-text-tertiary)]">
            <Search className="h-3.5 w-3.5" aria-hidden="true" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search equities by symbol, company name, or venue..."
            disabled={isLoading}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-[var(--atlas-surface-input,var(--atlas-surface-card))] text-[var(--atlas-text-primary)] placeholder-[var(--atlas-text-tertiary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50 transition-colors disabled:opacity-50"
          />
        </div>

        {/* Dropdown filters row */}
        <div className="flex flex-wrap items-center gap-2">
          {/* 1. Country Filter */}
          <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)]">
            <label htmlFor="equity-country-select" className="sr-only">
              Market Country
            </label>
            <select
              id="equity-country-select"
              value={marketCountry}
              onChange={(e) => onCountryChange(e.target.value)}
              disabled={isLoading}
              className="py-1.5 px-2 text-xs bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50 cursor-pointer"
            >
              <option value="all">All Countries</option>
              {availableFilters?.countries?.map((c) => (
                <option key={c.code} value={c.name}>
                  {c.name} ({c.count})
                </option>
              ))}
            </select>
          </div>

          {/* 2. Exchange Filter */}
          <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)]">
            <label htmlFor="equity-exchange-select" className="sr-only">
              Exchange
            </label>
            <select
              id="equity-exchange-select"
              value={exchange}
              onChange={(e) => onExchangeChange(e.target.value)}
              disabled={isLoading}
              className="py-1.5 px-2 text-xs bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50 cursor-pointer"
            >
              <option value="all">All Exchanges</option>
              {availableFilters?.exchanges?.map((ex) => (
                <option key={ex.mic} value={ex.mic}>
                  {ex.mic} - {ex.name} ({ex.count})
                </option>
              ))}
            </select>
          </div>

          {/* 3. Equity Subtype Filter */}
          <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)]">
            <label htmlFor="equity-subtype-select" className="sr-only">
              Equity Subtype
            </label>
            <select
              id="equity-subtype-select"
              value={equityType}
              onChange={(e) => onTypeChange(e.target.value)}
              disabled={isLoading}
              className="py-1.5 px-2 text-xs bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50 cursor-pointer"
            >
              <option value="all">All Types</option>
              {availableFilters?.equity_types?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label} ({t.count})
                </option>
              ))}
            </select>
          </div>

          {/* 4. Listing Status Filter */}
          <div className="flex items-center gap-1.5 text-xs text-[var(--atlas-text-secondary)]">
            <label htmlFor="equity-status-select" className="sr-only">
              Listing Status
            </label>
            <select
              id="equity-status-select"
              value={listingStatus}
              onChange={(e) => onListingStatusChange(e.target.value)}
              disabled={isLoading}
              className="py-1.5 px-2 text-xs bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] rounded focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              {availableFilters?.listing_statuses?.map((st) => (
                <option key={st.id} value={st.id}>
                  {st.label} ({st.count})
                </option>
              ))}
            </select>
          </div>

          {/* Reset Filters button */}
          {isFiltered && (
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-rose-500/50"
              title="Reset all filters"
            >
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
