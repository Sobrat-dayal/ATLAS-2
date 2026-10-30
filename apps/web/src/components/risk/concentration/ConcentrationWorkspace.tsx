"use client";

import React from "react";
import {
  ConcentrationDimension,
  ConcentrationSnapshotDTO,
} from "@/lib/risk/types";
import {
  formatCurrency,
  formatEffectiveHoldings,
  formatHHI,
  formatWeight,
  getConcentrationClassification,
} from "@/lib/risk/formatting";
import {
  Building2,
  Coins,
  Globe2,
  Layers,
  PieChart,
  RefreshCw,
  Scale,
  ShieldAlert,
} from "lucide-react";

interface ConcentrationWorkspaceProps {
  snapshot: ConcentrationSnapshotDTO | null;
  selectedDimension: ConcentrationDimension;
  onSelectDimension: (dim: ConcentrationDimension) => void;
  loading: boolean;
  onRefresh: () => void;
}

export function ConcentrationWorkspace({
  snapshot,
  selectedDimension,
  onSelectDimension,
  loading,
  onRefresh,
}: ConcentrationWorkspaceProps) {
  const dimensions: { id: ConcentrationDimension; label: string; icon: React.ReactNode }[] = [
    { id: "SECURITY", label: "Security Level", icon: <Coins className="h-3.5 w-3.5" /> },
    { id: "ISSUER", label: "Issuer Consolidated", icon: <Building2 className="h-3.5 w-3.5 text-atlas-accent" /> },
    { id: "SECTOR", label: "Sector", icon: <PieChart className="h-3.5 w-3.5" /> },
    { id: "INDUSTRY", label: "Industry", icon: <Layers className="h-3.5 w-3.5" /> },
    { id: "ASSET_CLASS", label: "Asset Class", icon: <Scale className="h-3.5 w-3.5" /> },
    { id: "COUNTRY", label: "Country", icon: <Globe2 className="h-3.5 w-3.5" /> },
  ];

  if (!snapshot) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-atlas-border-default/60 rounded m-4 bg-atlas-surface-1/40">
        <Scale className="h-10 w-10 text-atlas-text-secondary/50 mb-3 animate-pulse" />
        <h3 className="text-sm font-semibold text-atlas-text-primary">No Concentration Snapshot Available</h3>
        <p className="text-xs text-atlas-text-secondary max-w-md mt-1 mb-4">
          Select a concentration dimension to evaluate HHI, effective holdings count, and Top-N concentration.
        </p>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-black transition hover:bg-atlas-accent/90 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Load Concentration Data
        </button>
      </div>
    );
  }

  const classification = getConcentrationClassification(snapshot.hhi);

  return (
    <div className="space-y-4 p-4">
      {/* 1. Dimension Selector Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-2.5">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-semibold text-atlas-text-secondary uppercase tracking-wider mr-1">
            Dimension:
          </span>
          {dimensions.map((d) => (
            <button
              key={d.id}
              onClick={() => onSelectDimension(d.id)}
              className={`flex items-center gap-1.5 rounded px-2.5 py-1 text-xs font-medium transition ${
                selectedDimension === d.id
                  ? "bg-atlas-accent text-black font-semibold shadow-sm"
                  : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              {d.icon}
              {d.label}
            </button>
          ))}
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

      {/* 2. Top Metric Cards */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {/* HHI */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Herfindahl Index (HHI)</span>
            <span className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase ${classification.badgeClass}`}>
              {classification.label}
            </span>
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-atlas-text-primary">
            {formatHHI(snapshot.hhi)}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary">
            {classification.description}
          </div>
        </div>

        {/* Effective Holdings Count */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Effective Holdings (N_eff)</span>
            <Layers className="h-4 w-4 text-sky-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-sky-400">
            {formatEffectiveHoldings(snapshot.effective_number_of_holdings)}
          </div>
          <div className="mt-1 text-[11px] text-atlas-text-secondary">
            N_eff = 1 / HHI (equivalent equal-weight portfolio)
          </div>
        </div>

        {/* Top 1 & Top 3 Concentration */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Top Holdings Weight</span>
            <ShieldAlert className="h-4 w-4 text-amber-400" />
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-amber-400">
              {formatWeight(snapshot.top_1_weight)}
            </span>
            <span className="text-xs text-atlas-text-secondary font-mono">Top 1</span>
          </div>
          <div className="mt-1 flex items-center justify-between text-[11px] text-atlas-text-secondary font-mono">
            <span>Top 3: {formatWeight(snapshot.top_3_weight)}</span>
            <span>Top 5: {formatWeight(snapshot.top_5_weight)}</span>
          </div>
        </div>

        {/* Entity Counts */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Partition Entities</span>
            <Building2 className="h-4 w-4 text-purple-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-purple-400">
            {snapshot.items.length} {selectedDimension.toLowerCase()}s
          </div>
          <div className="mt-1 flex items-center justify-between text-[11px] text-atlas-text-secondary font-mono">
            <span>Positions: {snapshot.total_positions_count}</span>
            <span>Issuers: {snapshot.total_issuers_count}</span>
          </div>
        </div>
      </div>

      {/* 3. Detailed Partition Breakdown Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="border-b border-atlas-border-default/40 p-3 flex items-center justify-between">
          <div>
            <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
              Concentration Partition ({selectedDimension})
            </h4>
            <p className="text-[11px] text-atlas-text-secondary mt-0.5">
              Ranked cumulative capital distribution across portfolio constituents.
            </p>
          </div>
          <span className="text-xs font-mono text-atlas-text-secondary">
            Coverage: {(snapshot.coverage_ratio * 100).toFixed(1)}%
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default/40 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3 w-12 text-center">Rank</th>
                <th className="py-2.5 px-3">Identifier / Name</th>
                <th className="py-2.5 px-3 text-right">Weight</th>
                <th className="py-2.5 px-3 text-right">Market Value</th>
                <th className="py-2.5 px-3 text-center">Securities</th>
                <th className="py-2.5 px-3">Underlying Holdings</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/30 font-mono text-atlas-text-primary">
              {snapshot.items.map((item) => (
                <tr key={item.identifier} className="hover:bg-atlas-surface-2/30 transition">
                  <td className="py-2.5 px-3 text-center font-bold text-atlas-text-secondary">#{item.rank}</td>
                  <td className="py-2.5 px-3">
                    <div className="font-bold text-atlas-accent">{item.identifier}</div>
                    {item.name !== item.identifier && (
                      <div className="text-[10px] text-atlas-text-secondary font-sans">{item.name}</div>
                    )}
                  </td>
                  <td className="py-2.5 px-3 text-right font-bold text-sky-400">
                    {formatWeight(item.weight)}
                  </td>
                  <td className="py-2.5 px-3 text-right text-atlas-text-primary">
                    {formatCurrency(item.market_value)}
                  </td>
                  <td className="py-2.5 px-3 text-center text-atlas-text-secondary">
                    {item.securities_count}
                  </td>
                  <td className="py-2.5 px-3 text-atlas-text-secondary text-[11px]">
                    {item.security_symbols.join(", ") || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

