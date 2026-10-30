"use client";

import React, { useState } from "react";
import { SectorRiskSnapshotDTO } from "@/lib/risk/types";
import {
  formatSignedPercent,
  formatVolPercent,
  formatWeight,
} from "@/lib/risk/formatting";
import {
  ChevronDown,
  ChevronRight,
  Layers,
  PieChart,
  RefreshCw,
  Scale,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

interface SectorRiskWorkspaceProps {
  snapshot: SectorRiskSnapshotDTO | null;
  loading: boolean;
  onRefresh: () => void;
}

export function SectorRiskWorkspace({
  snapshot,
  loading,
  onRefresh,
}: SectorRiskWorkspaceProps) {
  const [expandedSectors, setExpandedSectors] = useState<Record<string, boolean>>({});

  const toggleSector = (secName: string) => {
    setExpandedSectors((prev) => ({
      ...prev,
      [secName]: !prev[secName],
    }));
  };

  if (!snapshot) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-atlas-border-default/60 rounded m-4 bg-atlas-surface-1/40">
        <PieChart className="h-10 w-10 text-atlas-text-secondary/50 mb-3 animate-pulse" />
        <h3 className="text-sm font-semibold text-atlas-text-primary">No Sector Risk Snapshot Available</h3>
        <p className="text-xs text-atlas-text-secondary max-w-md mt-1 mb-4">
          Decompose portfolio covariance risk across economic sectors and drill down into industry risk contributions.
        </p>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-black transition hover:bg-atlas-accent/90 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Load Sector Risk
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {/* 1. Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
            Sector & Industry Euler Risk Attribution
          </span>

          <div className="h-4 w-px bg-atlas-border-default" />

          {snapshot.is_reconciled && (
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
              <ShieldCheck className="h-3.5 w-3.5" />
              Reconciled (∑ VC_s ≡ V_P)
            </span>
          )}
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-atlas-surface-2 border border-atlas-border-default px-2.5 py-1 text-xs text-atlas-text-secondary hover:text-atlas-text-primary transition disabled:opacity-50"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* 2. Top Summary Metrics Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Total Portfolio Volatility</span>
            <TrendingUp className="h-4 w-4 text-atlas-accent" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-atlas-text-primary">
            {formatVolPercent(snapshot.portfolio_volatility)}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary">
            Square root of portfolio variance
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Total Portfolio Variance</span>
            <Scale className="h-4 w-4 text-sky-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-sky-400">
            {snapshot.portfolio_variance.toFixed(6)}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary">
            Exact sum of sector variance contributions
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Sectors & Industries</span>
            <Layers className="h-4 w-4 text-purple-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-purple-400">
            {snapshot.sectors.length} Sectors
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary font-mono">
            {snapshot.industries.length} Detailed Industries
          </div>
        </div>
      </div>

      {/* 3. Sector Euler Risk Contribution Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="border-b border-atlas-border-default/40 p-3">
          <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
            Sector Euler Risk Decomposition & Active Benchmark Weights
          </h4>
          <p className="text-[11px] text-atlas-text-secondary mt-0.5">
            Variance contribution VC_s = ∑ w_i (Σ w)_i and volatility contribution RC_s = VC_s / σ_P. Click a sector to expand industry breakdown.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default/40 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Sector</th>
                <th className="py-2.5 px-3 text-right">Portfolio Weight</th>
                <th className="py-2.5 px-3 text-right">Benchmark Weight</th>
                <th className="py-2.5 px-3 text-right">Active Tilt</th>
                <th className="py-2.5 px-3 text-right">Var Contrib (VC_s)</th>
                <th className="py-2.5 px-3 text-right">Vol Contrib (RC_s)</th>
                <th className="py-2.5 px-3 text-right">% Variance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/30 font-mono text-atlas-text-primary">
              {snapshot.sectors.map((sec) => {
                const isExpanded = !!expandedSectors[sec.sector_name];
                const active = sec.active_weight ?? 0;
                const activeColor =
                  active > 0.02
                    ? "text-emerald-400"
                    : active < -0.02
                    ? "text-rose-400"
                    : "text-atlas-text-secondary";

                const secIndustries = snapshot.industries.filter(
                  (ind) => ind.sector_name === sec.sector_name
                );

                return (
                  <React.Fragment key={sec.sector_name}>
                    <tr
                      onClick={() => toggleSector(sec.sector_name)}
                      className="hover:bg-atlas-surface-2/40 cursor-pointer transition"
                    >
                      <td className="py-2.5 px-3 flex items-center gap-2 font-sans font-semibold text-atlas-accent">
                        {isExpanded ? (
                          <ChevronDown className="h-3.5 w-3.5 text-atlas-text-secondary" />
                        ) : (
                          <ChevronRight className="h-3.5 w-3.5 text-atlas-text-secondary" />
                        )}
                        {sec.sector_name}
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold text-sky-400">
                        {formatWeight(sec.weight)}
                      </td>
                      <td className="py-2.5 px-3 text-right text-atlas-text-secondary">
                        {sec.benchmark_weight !== null && sec.benchmark_weight !== undefined
                          ? formatWeight(sec.benchmark_weight)
                          : "—"}
                      </td>
                      <td className={`py-2.5 px-3 text-right font-semibold ${activeColor}`}>
                        {formatSignedPercent(active)}
                      </td>
                      <td className="py-2.5 px-3 text-right">{sec.variance_contribution.toFixed(6)}</td>
                      <td className="py-2.5 px-3 text-right font-bold text-sky-400">
                        {formatVolPercent(sec.volatility_contribution)}
                      </td>
                      <td className="py-2.5 px-3 text-right font-semibold">
                        {(sec.percentage_of_variance * 100).toFixed(1)}%
                      </td>
                    </tr>

                    {/* Expanded Industry Sub-rows */}
                    {isExpanded &&
                      secIndustries.map((ind) => (
                        <tr
                          key={`${ind.sector_name}-${ind.industry_name}`}
                          className="bg-atlas-surface-2/20 text-[11px] text-atlas-text-secondary"
                        >
                          <td className="py-1.5 pl-8 pr-3 font-sans">↳ {ind.industry_name}</td>
                          <td className="py-1.5 px-3 text-right">{formatWeight(ind.weight)}</td>
                          <td className="py-1.5 px-3 text-right text-atlas-text-secondary/50">—</td>
                          <td className="py-1.5 px-3 text-right text-atlas-text-secondary/50">—</td>
                          <td className="py-1.5 px-3 text-right">
                            {ind.variance_contribution.toFixed(6)}
                          </td>
                          <td className="py-1.5 px-3 text-right text-sky-400">
                            {formatVolPercent(ind.volatility_contribution)}
                          </td>
                          <td className="py-1.5 px-3 text-right">—</td>
                        </tr>
                      ))}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

