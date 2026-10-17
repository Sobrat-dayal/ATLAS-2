"use client";

import React from "react";
import {
  Clock,
  RefreshCw,
  Search,
  ShieldCheck,
} from "lucide-react";
import { formatTimestamp } from "@/lib/markets/movers";

export interface MarketMoversHeaderProps {
  onRefresh: () => void;
  isRefreshing: boolean;
  isLoading: boolean;
  rankingCalculatedAt?: string | null;
  universeDisplayName?: string;
}

export function MarketMoversHeader({
  onRefresh,
  isRefreshing,
  isLoading,
  rankingCalculatedAt,
  universeDisplayName,
}: MarketMoversHeaderProps) {
  const handleOpenSearch = () => {
    window.dispatchEvent(
      new KeyboardEvent("keydown", {
        key: "k",
        ctrlKey: true,
        bubbles: true,
      })
    );
  };

  return (
    <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[var(--atlas-border-subtle)] pb-4 mb-4">
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--atlas-text-primary)]">
            Market Movers
          </h1>
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-[var(--atlas-surface-card)] text-[var(--atlas-text-tertiary)] border border-[var(--atlas-border-subtle)]">
            Module 02 / Movers
          </span>
          {universeDisplayName && (
            <span className="hidden md:inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-emerald-950/40 text-emerald-400 border border-emerald-800/40">
              <ShieldCheck className="h-3 w-3" />
              {universeDisplayName}
            </span>
          )}
        </div>
        <p className="text-xs sm:text-sm text-[var(--atlas-text-secondary)] mt-0.5">
          Explore significant price movements and trading activity across supported markets.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {rankingCalculatedAt && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-[var(--atlas-text-tertiary)] bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded">
            <Clock className="h-3.5 w-3.5 text-zinc-400" />
            <span>As-Of {formatTimestamp(rankingCalculatedAt)}</span>
          </div>
        )}

        <button
          type="button"
          onClick={handleOpenSearch}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          title="Search Instruments (Ctrl+K)"
        >
          <Search className="h-3.5 w-3.5" aria-hidden="true" />
          <span className="hidden md:inline">Search (Ctrl+K)</span>
        </button>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isLoading || isRefreshing}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          title="Refresh Movers Ranking"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`}
            aria-hidden="true"
          />
          <span>{isRefreshing ? "Refreshing..." : "Refresh"}</span>
        </button>
      </div>
    </header>
  );
}
