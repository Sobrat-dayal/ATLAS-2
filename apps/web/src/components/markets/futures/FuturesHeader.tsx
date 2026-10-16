"use client";

import React from "react";
import Link from "next/link";
import {
  BarChart2,
  BookOpen,
  Globe,
  LayoutDashboard,
  RefreshCw,
  Search,
} from "lucide-react";

export interface FuturesHeaderProps {
  onRefresh: () => void;
  isRefreshing: boolean;
  isLoading: boolean;
}

export function FuturesHeader({
  onRefresh,
  isRefreshing,
  isLoading,
}: FuturesHeaderProps) {
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
            Futures &amp; Commodities
          </h1>
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-[var(--atlas-surface-card)] text-[var(--atlas-text-tertiary)] border border-[var(--atlas-border-subtle)]">
            Module 02 / Futures
          </span>
        </div>
        <p className="text-xs sm:text-sm text-[var(--atlas-text-secondary)] mt-0.5">
          Explore supported commodities, exchange-listed Futures contracts, settlement data, and market observations.
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
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors"
        >
          <LayoutDashboard className="h-3.5 w-3.5" aria-hidden="true" />
          <span className="hidden lg:inline">Markets</span> Overview
        </Link>

        <Link
          href="/economics"
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors"
        >
          <Globe className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Economics</span>
        </Link>

        <Link
          href="/charts"
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors"
        >
          <BarChart2 className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Charts</span>
        </Link>

        <Link
          href="/research"
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors"
        >
          <BookOpen className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Research</span>
        </Link>

        <button
          type="button"
          onClick={onRefresh}
          disabled={isRefreshing || isLoading}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors disabled:opacity-50 focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          title="Refresh Market Data"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin text-emerald-400" : ""}`}
            aria-hidden="true"
          />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>
    </header>
  );
}
