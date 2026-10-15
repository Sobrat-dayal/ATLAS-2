"use client";

import React from "react";
import { FundCoverageSummary as FundCoverageSummaryType } from "@/lib/markets/funds";
import { Activity, Database, Layers, ShieldCheck } from "lucide-react";

export interface FundCoverageSummaryProps {
  coverage?: FundCoverageSummaryType;
  generatedAt?: string;
  scope?: string;
}

export function FundCoverageSummary({
  coverage,
  generatedAt,
  scope,
}: FundCoverageSummaryProps) {
  if (!coverage) return null;

  return (
    <div className="mb-5">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Metric 1: Total Canonical Funds */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Total Funds</span>
            <Layers className="h-3.5 w-3.5 text-blue-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.configured_funds_count}
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            {coverage.etf_count} ETFs · {coverage.mutual_fund_count} Mutual · {coverage.closed_end_fund_count} CEF
          </p>
        </div>

        {/* Metric 2: Exchange-Listed Products */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Exchange Listed</span>
            <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.exchange_listed_count}
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            Traded venue listings
          </p>
        </div>

        {/* Metric 3: Latest Quotes (Exchange Traded) */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Latest Quotes</span>
            <Activity className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-emerald-400">
            {coverage.available_quotes_count}
            <span className="text-xs font-normal text-[var(--atlas-text-tertiary)] ml-1">
              / {coverage.exchange_listed_count} listed
            </span>
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            Exchange trade series
          </p>
        </div>

        {/* Metric 4: Official NAV Observations */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Official NAVs</span>
            <Database className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-amber-400">
            {coverage.available_nav_count}
            <span className="text-xs font-normal text-[var(--atlas-text-tertiary)] ml-1">
              / {coverage.configured_funds_count} total
            </span>
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            Dated valuation points
          </p>
        </div>
      </div>

      {(generatedAt || scope) && (
        <div className="flex items-center justify-between text-[10px] text-[var(--atlas-text-tertiary)] mt-1.5 px-0.5">
          <span>Scope: {scope || "authorized_canonical_fund_directory"}</span>
          {generatedAt && (
            <span>
              As of: {new Date(generatedAt).toLocaleTimeString("en-US", { hour12: false })}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
