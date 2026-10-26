"use client";

import React from "react";
import { EconomicCalendarCoverageDTO } from "@/lib/economics/calendar";
import { ShieldCheck, CheckCircle2, Globe, Layers, Clock, AlertCircle } from "lucide-react";

interface EconomicCalendarCoveragePanelProps {
  coverage: EconomicCalendarCoverageDTO | null;
  isOpen: boolean;
  onClose: () => void;
}

export function EconomicCalendarCoveragePanel({
  coverage,
  isOpen,
  onClose,
}: EconomicCalendarCoveragePanelProps) {
  if (!isOpen || !coverage) return null;

  return (
    <div className="mb-4 p-4 rounded bg-atlas-surface border border-atlas-border-subtle text-xs space-y-4 shadow-xs animate-in fade-in duration-150">
      <div className="flex items-center justify-between border-b border-atlas-border-subtle pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <h3 className="font-bold text-atlas-text-primary text-sm tracking-tight">
            Official Source Registry & Verification Coverage
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-atlas-text-muted hover:text-atlas-text-primary text-xs"
        >
          Dismiss
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-2.5 rounded bg-atlas-background border border-atlas-border-subtle">
          <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
            Covered Jurisdictions
          </span>
          <span className="text-base font-bold text-atlas-text-primary font-mono">
            {coverage.supported_geographies.length} Major Economies
          </span>
          <span className="text-[10px] text-atlas-text-muted block mt-0.5">
            {coverage.supported_geographies.join(", ")}
          </span>
        </div>

        <div className="p-2.5 rounded bg-atlas-background border border-atlas-border-subtle">
          <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
            Macro Categories
          </span>
          <span className="text-base font-bold text-atlas-text-primary font-mono">
            {coverage.supported_categories.length} Taxonomies
          </span>
          <span className="text-[10px] text-atlas-text-muted block mt-0.5">
            GDP, CPI, NFP, Rates, Sales
          </span>
        </div>

        <div className="p-2.5 rounded bg-atlas-background border border-atlas-border-subtle">
          <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
            Total Event Releases
          </span>
          <span className="text-base font-bold text-atlas-text-primary font-mono">
            {coverage.total_events_count} Releases
          </span>
          <span className="text-[10px] text-emerald-400 block mt-0.5">
            {coverage.verified_events_count} Officially Verified
          </span>
        </div>

        <div className="p-2.5 rounded bg-atlas-background border border-atlas-border-subtle">
          <span className="text-[10px] font-mono uppercase text-atlas-text-muted block">
            Consensus Coverage
          </span>
          <span className="text-base font-bold text-atlas-text-primary font-mono">
            {coverage.forecast_coverage_pct.toFixed(1)}%
          </span>
          <span className="text-[10px] text-atlas-text-muted block mt-0.5">
            Licensed pre-release snapshots
          </span>
        </div>
      </div>

      {/* Official Registry Matrix */}
      <div className="space-y-1.5">
        <h4 className="font-semibold text-atlas-text-primary text-[11px] uppercase tracking-wider">
          Integrated Official Statistical Agencies & Central Banks
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-[11px]">
          <div className="p-2 rounded bg-atlas-background border border-atlas-border-subtle font-mono">
            <span className="font-bold text-atlas-text-primary">United States:</span>
            <span className="text-atlas-text-secondary block">
              BLS (CPI, NFP), BEA (GDP), Census, Federal Reserve
            </span>
          </div>

          <div className="p-2 rounded bg-atlas-background border border-atlas-border-subtle font-mono">
            <span className="font-bold text-atlas-text-primary">Euro Area:</span>
            <span className="text-atlas-text-secondary block">
              Eurostat (HICP, GDP), European Central Bank (ECB)
            </span>
          </div>

          <div className="p-2 rounded bg-atlas-background border border-atlas-border-subtle font-mono">
            <span className="font-bold text-atlas-text-primary">United Kingdom:</span>
            <span className="text-atlas-text-secondary block">
              ONS (CPI, Labor, GDP), Bank of England (MPC)
            </span>
          </div>

          <div className="p-2 rounded bg-atlas-background border border-atlas-border-subtle font-mono">
            <span className="font-bold text-atlas-text-primary">Japan:</span>
            <span className="text-atlas-text-secondary block">
              Statistics Bureau (CPI), Cabinet Office, Bank of Japan (BoJ)
            </span>
          </div>

          <div className="p-2 rounded bg-atlas-background border border-atlas-border-subtle font-mono">
            <span className="font-bold text-atlas-text-primary">India:</span>
            <span className="text-atlas-text-secondary block">
              MoSPI (CPI, IIP, GDP), Reserve Bank of India (RBI MPC)
            </span>
          </div>

          <div className="p-2 rounded bg-atlas-background border border-atlas-border-subtle font-mono">
            <span className="font-bold text-atlas-text-primary">China:</span>
            <span className="text-atlas-text-secondary block">
              NBS (CPI, PPI, GDP), People&apos;s Bank of China (PBoC LPR)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
