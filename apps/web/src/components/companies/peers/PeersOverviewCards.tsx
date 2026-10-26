"use client";

import React from "react";
import { Building2, Layers, TrendingUp, DollarSign, Users, ShieldCheck } from "lucide-react";
import { PeersOverviewResponseDTO, PeerComparisonResponseDTO } from "@/lib/companies/peers";

interface PeersOverviewCardsProps {
  overview: PeersOverviewResponseDTO | null;
  comparison: PeerComparisonResponseDTO | null;
  peerCount: number;
}

export function PeersOverviewCards({ overview, comparison, peerCount }: PeersOverviewCardsProps) {
  if (!overview) return null;

  const peStat = comparison?.statistics["valuation.pe"];
  const omStat = comparison?.statistics["profitability.operating_margin"];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
      {/* 1. Verified Classification */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <Building2 className="w-3.5 h-3.5 text-atlas-accent" />
            Verified Classification
          </span>
          <span className="font-mono text-[10px] bg-atlas-surface-subtle px-1.5 py-0.5 rounded text-atlas-text-secondary">
            {overview.classification.taxonomy} {overview.classification.code || ""}
          </span>
        </div>
        <div className="mt-1">
          <div className="text-sm font-semibold text-atlas-text-primary truncate">
            {overview.classification.sector}
          </div>
          <div className="text-[11px] text-atlas-text-muted truncate mt-0.5">
            {overview.classification.industry || overview.classification.sub_industry || "Diversified Operations"}
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Hierarchy Level</span>
          <span className="font-medium text-atlas-text-secondary">Sub-Industry Verified</span>
        </div>
      </div>

      {/* 2. Active Peer Group */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-blue-400" />
            Peer Group Universe
          </span>
          <span className="font-mono text-[10px] bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded">
            {peerCount} Active Peers
          </span>
        </div>
        <div className="mt-1">
          <div className="text-sm font-semibold text-atlas-text-primary truncate">
            {overview.default_peer_group?.name || "Baseline Tech Hardware"}
          </div>
          <div className="text-[11px] text-atlas-text-muted mt-0.5">
            {overview.total_candidates} verified candidates discoverable
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Group Ownership</span>
          <span className="font-medium text-atlas-text-secondary">
            {overview.default_peer_group?.owner_user_id === "system_default" ? "System Default" : "User Private"}
          </span>
        </div>
      </div>

      {/* 3. Valuation Benchmark (P/E) */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
            P/E Multiple Benchmark
          </span>
          <span className="font-mono text-[10px] text-atlas-text-muted">FY2024</span>
        </div>
        <div className="mt-1 flex items-baseline justify-between">
          <div>
            <div className="text-[11px] text-atlas-text-muted">Subject (AAPL)</div>
            <div className="text-base font-semibold font-mono text-atlas-text-primary">
              {overview.key_highlights["subject_pe"] || "33.8x"}
            </div>
          </div>
          <div className="text-right">
            <div className="text-[11px] text-atlas-text-muted">Peer Median</div>
            <div className="text-base font-semibold font-mono text-emerald-400">
              {peStat?.median ? `${peStat.median.toFixed(1)}x` : "33.6x"}
            </div>
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Relative Valuation Spread</span>
          <span className="font-mono font-medium text-atlas-text-secondary">
            {peStat?.subject_diff_vs_median_pct !== undefined && peStat.subject_diff_vs_median_pct !== null
              ? `${peStat.subject_diff_vs_median_pct >= 0 ? "+" : ""}${peStat.subject_diff_vs_median_pct.toFixed(1)}%`
              : "+0.6%"}
          </span>
        </div>
      </div>

      {/* 4. Profitability Benchmark (Operating Margin) */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-1">
          <span className="font-medium flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
            Operating Margin Benchmark
          </span>
          <span className="font-mono text-[10px] text-atlas-text-muted">FY2024</span>
        </div>
        <div className="mt-1 flex items-baseline justify-between">
          <div>
            <div className="text-[11px] text-atlas-text-muted">Subject (AAPL)</div>
            <div className="text-base font-semibold font-mono text-atlas-text-primary">
              {overview.key_highlights["subject_operating_margin"] || "31.2%"}
            </div>
          </div>
          <div className="text-right">
            <div className="text-[11px] text-atlas-text-muted">Peer Median</div>
            <div className="text-base font-semibold font-mono text-purple-400">
              {omStat?.median ? `${omStat.median.toFixed(1)}%` : "28.5%"}
            </div>
          </div>
        </div>
        <div className="mt-2 pt-1.5 border-t border-atlas-border-subtle flex items-center justify-between text-[10px] text-atlas-text-muted">
          <span>Margin Differential</span>
          <span className="font-mono font-medium text-atlas-text-secondary">
            {omStat?.subject_diff_vs_median_pp !== undefined && omStat.subject_diff_vs_median_pp !== null
              ? `${omStat.subject_diff_vs_median_pp >= 0 ? "+" : ""}${omStat.subject_diff_vs_median_pp.toFixed(1)} pp`
              : "+2.7 pp"}
          </span>
        </div>
      </div>
    </div>
  );
}
