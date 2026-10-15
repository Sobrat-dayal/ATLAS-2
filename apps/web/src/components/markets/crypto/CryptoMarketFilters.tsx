"use client";

import React from "react";
import { Filter, RotateCcw, Search } from "lucide-react";
import { CryptoFilterOptionsResponse } from "@/lib/markets/crypto";

export interface CryptoMarketFiltersProps {
  query: string;
  onQueryChange: (q: string) => void;
  baseAsset: string;
  onBaseAssetChange: (b: string) => void;
  quoteAsset: string;
  onQuoteAssetChange: (q: string) => void;
  venue: string;
  onVenueChange: (v: string) => void;
  quoteAssetType: string;
  onQuoteAssetTypeChange: (t: string) => void;
  onReset: () => void;
  filterOptions: CryptoFilterOptionsResponse | null;
  totalMatched: number;
  isLoading: boolean;
}

export function CryptoMarketFilters({
  query,
  onQueryChange,
  baseAsset,
  onBaseAssetChange,
  quoteAsset,
  onQuoteAssetChange,
  venue,
  onVenueChange,
  quoteAssetType,
  onQuoteAssetTypeChange,
  onReset,
  filterOptions,
  totalMatched,
  isLoading,
}: CryptoMarketFiltersProps) {
  const isFiltered =
    query.trim() !== "" ||
    baseAsset !== "all" ||
    quoteAsset !== "all" ||
    venue !== "all" ||
    quoteAssetType !== "all";

  return (
    <div className="flex flex-col gap-3 p-3 rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] mb-4">
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search input */}
        <div className="relative flex-1">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[var(--atlas-text-tertiary)] pointer-events-none"
            aria-hidden="true"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search crypto pairs (e.g. BTC/USDT, ETH, Coinbase, Binance)..."
            aria-label="Search crypto markets by pair, symbol, or venue"
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-[var(--atlas-surface-input)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] placeholder-[var(--atlas-text-tertiary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          />
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Base Asset Dropdown */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="crypto-base-filter" className="text-xs text-[var(--atlas-text-tertiary)] whitespace-nowrap">
              Base:
            </label>
            <select
              id="crypto-base-filter"
              value={baseAsset}
              onChange={(e) => onBaseAssetChange(e.target.value)}
              className="px-2 py-1.5 text-xs bg-[var(--atlas-surface-input)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            >
              <option value="all">All Base Assets</option>
              {filterOptions?.base_assets.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          {/* Quote Asset Dropdown */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="crypto-quote-filter" className="text-xs text-[var(--atlas-text-tertiary)] whitespace-nowrap">
              Quote:
            </label>
            <select
              id="crypto-quote-filter"
              value={quoteAsset}
              onChange={(e) => onQuoteAssetChange(e.target.value)}
              className="px-2 py-1.5 text-xs bg-[var(--atlas-surface-input)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            >
              <option value="all">All Quote Assets</option>
              {filterOptions?.quote_assets.map((q) => (
                <option key={q} value={q}>
                  {q}
                </option>
              ))}
            </select>
          </div>

          {/* Venue Dropdown */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="crypto-venue-filter" className="text-xs text-[var(--atlas-text-tertiary)] whitespace-nowrap">
              Exchange:
            </label>
            <select
              id="crypto-venue-filter"
              value={venue}
              onChange={(e) => onVenueChange(e.target.value)}
              className="px-2 py-1.5 text-xs bg-[var(--atlas-surface-input)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            >
              <option value="all">All Exchanges</option>
              {filterOptions?.venues.map((v) => (
                <option key={v.venue_id} value={v.venue_id}>
                  {v.name}
                </option>
              ))}
            </select>
          </div>

          {/* Quote Asset Type Dropdown */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="crypto-quote-type-filter" className="text-xs text-[var(--atlas-text-tertiary)] whitespace-nowrap">
              Denomination:
            </label>
            <select
              id="crypto-quote-type-filter"
              value={quoteAssetType}
              onChange={(e) => onQuoteAssetTypeChange(e.target.value)}
              className="px-2 py-1.5 text-xs bg-[var(--atlas-surface-input)] border border-[var(--atlas-border-subtle)] rounded text-[var(--atlas-text-primary)] focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            >
              <option value="all">All Types</option>
              <option value="fiat">Fiat (USD, EUR)</option>
              <option value="stablecoin">Stablecoin (USDT)</option>
              <option value="crypto">Crypto (BTC)</option>
            </select>
          </div>

          {/* Reset Filters button */}
          {isFiltered && (
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1 px-2 py-1.5 text-xs font-medium text-amber-400 hover:text-amber-300 bg-amber-950/20 hover:bg-amber-950/40 border border-amber-800/40 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-amber-500/50"
              title="Reset active filters"
            >
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter status summary */}
      <div className="flex items-center justify-between text-[11px] text-[var(--atlas-text-tertiary)] pt-1 border-t border-[var(--atlas-border-subtle)]">
        <div className="flex items-center gap-1.5">
          <Filter className="h-3 w-3 text-emerald-400" aria-hidden="true" />
          <span>
            {isLoading ? "Filtering spot markets..." : `${totalMatched} spot markets available`}
          </span>
        </div>
        <div className="text-[10px] font-mono text-[var(--atlas-text-tertiary)]">
          Exchange-aware spot markets &middot; No perpetuals &middot; No derivatives
        </div>
      </div>
    </div>
  );
}
