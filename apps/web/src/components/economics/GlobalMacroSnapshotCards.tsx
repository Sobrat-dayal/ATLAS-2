"use client";

import React from "react";
import {
  TrendingUp,
  Percent,
  Landmark,
  Users,
  ShieldCheck,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from "lucide-react";
import { GlobalMacroOverviewResponseDTO } from "@/lib/economics";

interface GlobalMacroSnapshotCardsProps {
  overview: GlobalMacroOverviewResponseDTO | null;
  onSelectSeries?: (seriesId: string) => void;
}

export function GlobalMacroSnapshotCards({ overview, onSelectSeries }: GlobalMacroSnapshotCardsProps) {
  if (!overview || !overview.major_economies || overview.major_economies.length === 0) {
    return null;
  }

  // Find US and Euro Area benchmarks
  const usSummary = overview.major_economies.find((m) => m.geography.iso_code === "US");
  const eaSummary = overview.major_economies.find((m) => m.geography.iso_code === "EA");
  const cnSummary = overview.major_economies.find((m) => m.geography.iso_code === "CN");
  const inSummary = overview.major_economies.find((m) => m.geography.iso_code === "IN");

  const usGdp = usSummary?.gdp_growth_qoq;
  const usCpi = usSummary?.cpi_inflation_yoy;
  const usFedRate = usSummary?.policy_rate;
  const usUnemp = usSummary?.unemployment_rate;

  const eaCpi = eaSummary?.cpi_inflation_yoy;
  const cnGdp = cnSummary?.gdp_growth_qoq;
  const inGdp = inSummary?.gdp_growth_qoq;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
      {/* 1. Real GDP Growth Anchor */}
      <div className="p-3.5 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1.5">
          <span className="font-medium flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            Real GDP Growth
          </span>
          <span className="font-mono text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded">
            {usGdp?.reference_period || "Q3 2024"}
          </span>
        </div>
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-atlas-text-primary">
              {usGdp ? `+${usGdp.value.toFixed(1)}%` : "N/A"}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">QoQ Ann. (US)</span>
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-1 flex items-center gap-2">
            <span>IN: {inGdp ? `+${inGdp.value.toFixed(1)}%` : "N/A"}</span>
            <span className="text-atlas-border-subtle">|</span>
            <span>CN: {cnGdp ? `+${cnGdp.value.toFixed(1)}%` : "N/A"}</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            BEA Advance / Revised
          </span>
          {usSummary?.gdp_growth_series_id && onSelectSeries && (
            <button
              onClick={() => onSelectSeries(usSummary.gdp_growth_series_id!)}
              className="text-emerald-400 hover:text-emerald-300 font-medium"
            >
              Chart Series &rarr;
            </button>
          )}
        </div>
      </div>

      {/* 2. Headline Inflation Anchor */}
      <div className="p-3.5 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1.5">
          <span className="font-medium flex items-center gap-1.5">
            <Percent className="w-3.5 h-3.5 text-blue-400" />
            Headline Inflation (CPI)
          </span>
          <span className="font-mono text-[10px] bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded">
            {usCpi?.reference_period || "2024-09"}
          </span>
        </div>
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-atlas-text-primary">
              {usCpi ? `${usCpi.value.toFixed(1)}%` : "N/A"}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">YoY (US BLS)</span>
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-1 flex items-center gap-2">
            <span>Euro Area HICP: {eaCpi ? `${eaCpi.value.toFixed(1)}%` : "1.7%"}</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-blue-400" />
            BLS All Urban Consumers
          </span>
          {usSummary?.cpi_series_id && onSelectSeries && (
            <button
              onClick={() => onSelectSeries(usSummary.cpi_series_id!)}
              className="text-blue-400 hover:text-blue-300 font-medium"
            >
              Chart Series &rarr;
            </button>
          )}
        </div>
      </div>

      {/* 3. Central Bank Policy Target Rate */}
      <div className="p-3.5 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1.5">
          <span className="font-medium flex items-center gap-1.5">
            <Landmark className="w-3.5 h-3.5 text-purple-400" />
            Policy Interest Rate
          </span>
          <span className="font-mono text-[10px] bg-purple-500/10 text-purple-400 px-1.5 py-0.5 rounded">
            {usFedRate?.reference_period || "2024-09"}
          </span>
        </div>
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-atlas-text-primary">
              {usFedRate ? `${usFedRate.value.toFixed(2)}%` : "5.00%"}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">Fed Upper Target</span>
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-1 flex items-center gap-2">
            <span className="text-amber-400 flex items-center gap-0.5">
              <ArrowDownRight className="w-3 h-3" />
              -50 bps FOMC Cut (Sep 2024)
            </span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-purple-400" />
            Federal Reserve Target Range
          </span>
          {usSummary?.policy_rate_series_id && onSelectSeries && (
            <button
              onClick={() => onSelectSeries(usSummary.policy_rate_series_id!)}
              className="text-purple-400 hover:text-purple-300 font-medium"
            >
              Chart Series &rarr;
            </button>
          )}
        </div>
      </div>

      {/* 4. Unemployment & Labor Market */}
      <div className="p-3.5 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1.5">
          <span className="font-medium flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-amber-400" />
            Unemployment Rate
          </span>
          <span className="font-mono text-[10px] bg-amber-500/10 text-amber-400 px-1.5 py-0.5 rounded">
            {usUnemp?.reference_period || "2024-09"}
          </span>
        </div>
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-atlas-text-primary">
              {usUnemp ? `${usUnemp.value.toFixed(1)}%` : "4.1%"}
            </span>
            <span className="text-xs text-atlas-text-muted font-mono">U-3 Labor Force</span>
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-1 flex items-center gap-2">
            <span className="text-emerald-400 flex items-center gap-0.5">
              <ArrowDownRight className="w-3 h-3" />
              -0.1 %p vs Aug 2024
            </span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-amber-400" />
            BLS Household Survey
          </span>
          {usSummary?.unemployment_series_id && onSelectSeries && (
            <button
              onClick={() => onSelectSeries(usSummary.unemployment_series_id!)}
              className="text-amber-400 hover:text-amber-300 font-medium"
            >
              Chart Series &rarr;
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
