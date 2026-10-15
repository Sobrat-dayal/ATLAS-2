"use client";

import React from "react";
import { EquityCoverageSummary as CoverageSummaryType } from "@/lib/markets/equities";
import { Activity, Globe, Landmark, Layers } from "lucide-react";

export interface EquityCoverageSummaryProps {
  coverage?: CoverageSummaryType;
  generatedAt?: string;
  scope?: string;
}

export function EquityCoverageSummary({
  coverage,
  generatedAt,
  scope,
}: EquityCoverageSummaryProps) {
  if (!coverage) return null;

  return (
    <div className="mb-5">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Metric 1: Total Canonical Equities */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Canonical Equities</span>
            <Layers className="h-3.5 w-3.5 text-blue-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.configured_equities_count}
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            Catalog coverage
          </p>
        </div>

        {/* Metric 2: Covered Venues / Exchanges */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Covered Exchanges</span>
            <Landmark className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.covered_exchanges_count}
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            Distinct venue MICs
          </p>
        </div>

        {/* Metric 3: Market Countries */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Market Countries</span>
            <Globe className="h-3.5 w-3.5 text-amber-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-[var(--atlas-text-primary)]">
            {coverage.market_countries_count}
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            Listing jurisdictions
          </p>
        </div>

        {/* Metric 4: Live / Available Quotes */}
        <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md p-3">
          <div className="flex items-center justify-between text-xs text-[var(--atlas-text-secondary)] mb-1">
            <span className="font-medium">Latest Quotes</span>
            <Activity className="h-3.5 w-3.5 text-sky-400" aria-hidden="true" />
          </div>
          <div className="text-lg sm:text-xl font-bold font-mono text-emerald-400">
            {coverage.available_quotes_count}
            <span className="text-xs font-normal text-[var(--atlas-text-tertiary)] ml-1">
              / {coverage.returned_count} visible
            </span>
          </div>
          <p className="text-[10px] text-[var(--atlas-text-tertiary)] mt-0.5 truncate">
            Active price observations
          </p>
        </div>
      </div>

      {(generatedAt || scope) && (
        <div className="flex items-center justify-between text-[10px] text-[var(--atlas-text-tertiary)] mt-1.5 px-0.5">
          <span>Scope: {scope || "authorized_canonical_equity_directory"}</span>
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
