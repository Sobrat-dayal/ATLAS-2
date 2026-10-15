"use client";

import React from "react";
import { FundFilterOptionsResponse } from "@/lib/markets/funds";
import { FilterX, Search } from "lucide-react";

export interface FundDirectoryFiltersProps {
  query: string;
  onQueryChange: (q: string) => void;
  marketCountry: string;
  onCountryChange: (c: string) => void;
  exchange: string;
  onExchangeChange: (e: string) => void;
  domicile: string;
  onDomicileChange: (d: string) => void;
  fundCategory: string;
  onCategoryChange: (cat: string) => void;
  shareClassCurrency: string;
  onCurrencyChange: (cur: string) => void;
  onReset: () => void;
  options?: FundFilterOptionsResponse;
  totalMatched?: number;
}

export function FundDirectoryFilters({
  query,
  onQueryChange,
  marketCountry,
  onCountryChange,
  exchange,
  onExchangeChange,
  domicile,
  onDomicileChange,
  fundCategory,
  onCategoryChange,
  shareClassCurrency,
  onCurrencyChange,
  onReset,
  options,
  totalMatched,
}: FundDirectoryFiltersProps) {
  const isFiltered =
    query.trim() !== "" ||
    marketCountry !== "all" ||
    exchange !== "all" ||
    domicile !== "all" ||
    fundCategory !== "all" ||
    shareClassCurrency !== "all";

  return (
    <div className="flex flex-col gap-3 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3 mb-4">
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--atlas-text-tertiary)]" />
          <input
            type="search"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search funds by name, ticker (e.g. SPY, VOO, VTSAX)..."
            aria-label="Search funds by name or ticker"
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] placeholder-[var(--atlas-text-tertiary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          />
        </div>

        {/* Total Matched Indicator */}
        {totalMatched !== undefined && (
          <div className="text-xs text-[var(--atlas-text-secondary)] whitespace-nowrap self-center">
            Matched:{" "}
            <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
              {totalMatched}
            </span>{" "}
            funds
          </div>
        )}
      </div>

      {/* Filter Dropdowns Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 pt-1 border-t border-[var(--atlas-border-subtle)]/60">
        {/* Country Filter */}
        <div>
          <label htmlFor="country-filter" className="block text-[10px] font-medium text-[var(--atlas-text-tertiary)] mb-1">
            Listing Market
          </label>
          <select
            id="country-filter"
            value={marketCountry}
            onChange={(e) => onCountryChange(e.target.value)}
            className="w-full py-1 px-2 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Markets</option>
            {options?.countries.map((c) => (
              <option key={c.code} value={c.name}>
                {c.name} ({c.count})
              </option>
            ))}
          </select>
        </div>

        {/* Exchange Filter */}
        <div>
          <label htmlFor="exchange-filter" className="block text-[10px] font-medium text-[var(--atlas-text-tertiary)] mb-1">
            Exchange Venue
          </label>
          <select
            id="exchange-filter"
            value={exchange}
            onChange={(e) => onExchangeChange(e.target.value)}
            className="w-full py-1 px-2 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Venues</option>
            {options?.exchanges.map((ex) => (
              <option key={ex.mic} value={ex.mic}>
                {ex.mic} - {ex.name} ({ex.count})
              </option>
            ))}
          </select>
        </div>

        {/* Domicile Filter */}
        <div>
          <label htmlFor="domicile-filter" className="block text-[10px] font-medium text-[var(--atlas-text-tertiary)] mb-1">
            Fund Domicile
          </label>
          <select
            id="domicile-filter"
            value={domicile}
            onChange={(e) => onDomicileChange(e.target.value)}
            className="w-full py-1 px-2 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Domiciles</option>
            {options?.domiciles.map((d) => (
              <option key={d.name} value={d.name}>
                {d.name} ({d.count})
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div>
          <label htmlFor="category-filter" className="block text-[10px] font-medium text-[var(--atlas-text-tertiary)] mb-1">
            Asset Category
          </label>
          <select
            id="category-filter"
            value={fundCategory}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="w-full py-1 px-2 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <option value="all">All Categories</option>
            {options?.categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.label} ({cat.count})
              </option>
            ))}
          </select>
        </div>

        {/* Currency Filter & Reset */}
        <div className="flex items-end gap-1.5">
          <div className="flex-1">
            <label htmlFor="currency-filter" className="block text-[10px] font-medium text-[var(--atlas-text-tertiary)] mb-1">
              Currency
            </label>
            <select
              id="currency-filter"
              value={shareClassCurrency}
              onChange={(e) => onCurrencyChange(e.target.value)}
              className="w-full py-1 px-2 text-xs bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            >
              <option value="all">All CCY</option>
              {options?.currencies.map((cur) => (
                <option key={cur.code} value={cur.code}>
                  {cur.code} ({cur.count})
                </option>
              ))}
            </select>
          </div>

          {isFiltered && (
            <button
              type="button"
              onClick={onReset}
              className="py-1 px-2 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-rose-400 bg-zinc-800/80 hover:bg-zinc-800 border border-[var(--atlas-border-subtle)] rounded transition-colors focus:outline-none focus:ring-1 focus:ring-rose-500/50"
              title="Reset all filters"
            >
              <FilterX className="h-3.5 w-3.5" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
