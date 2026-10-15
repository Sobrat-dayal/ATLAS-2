"use client";

import React from "react";
import Link from "next/link";
import { ArrowUpRight, BarChart2, Globe, LayoutDashboard, RefreshCw, Search } from "lucide-react";

export interface FxHeaderProps {
  onRefresh: () => void;
  isRefreshing: boolean;
  isLoading: boolean;
}

export function FxHeader({
  onRefresh,
  isRefreshing,
  isLoading,
}: FxHeaderProps) {
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
            Foreign Exchange
          </h1>
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-[var(--atlas-surface-card)] text-[var(--atlas-text-tertiary)] border border-[var(--atlas-border-subtle)]">
            Module 02 / FX
          </span>
        </div>
        <p className="text-xs sm:text-sm text-[var(--atlas-text-secondary)] mt-0.5">
          Explore supported currency pairs and spot exchange-rate observations.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={handleOpenSearch}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          title="Search Instruments (Ctrl+K)"
        >
          <Search className="h-3.5 w-3.5" aria-hidden="true" />
          <span className="hidden md:inline">Search (Ctrl+K)</span>
        </button>

        <Link
          href="/markets"
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
        >
          <LayoutDashboard className="h-3.5 w-3.5 text-sky-400" aria-hidden="true" />
          <span>Overview</span>
        </Link>

        <Link
          href="/charts"
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
        >
          <BarChart2 className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
          <span>Charts</span>
          <ArrowUpRight className="h-3 w-3 opacity-60" aria-hidden="true" />
        </Link>

        <Link
          href="/economics"
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
        >
          <Globe className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
          <span>Economics</span>
          <ArrowUpRight className="h-3 w-3 opacity-60" aria-hidden="true" />
        </Link>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isRefreshing || isLoading}
          aria-label="Refresh FX directory"
          className="p-1.5 rounded text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin text-emerald-400" : ""}`}
            aria-hidden="true"
          />
        </button>
      </div>
    </header>
  );
}
