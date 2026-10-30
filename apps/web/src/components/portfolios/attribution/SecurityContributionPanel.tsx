"use client";

import React, { useState } from "react";
import {
  formatBps,
  formatPercent,
  formatWeight,
  getEffectColorClass,
} from "@/lib/portfolios/attribution/formatting";
import { AttributionRunDTO, SecurityContributionDTO } from "@/lib/portfolios/attribution/types";
import { ArrowDownRight, ArrowUpRight, Award, TrendingDown, TrendingUp } from "lucide-react";

interface SecurityContributionPanelProps {
  run: AttributionRunDTO;
}

export function SecurityContributionPanel({ run }: SecurityContributionPanelProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<string>("return_contribution");
  const [sortAsc, setSortAsc] = useState<boolean>(false);

  const filteredSecurities = run.security_contributions.filter(
    (s) =>
      s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.category_label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedSecurities = [...filteredSecurities].sort((a, b) => {
    const valA = parseFloat((a as any)[sortField] || "0");
    const valB = parseFloat((b as any)[sortField] || "0");
    return sortAsc ? valA - valB : valB - valA;
  });

  const handleHeaderClick = (field: string) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Contributors & Detractors Spotlight Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* Top 5 Contributors */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-2.5">
            <TrendingUp className="h-4 w-4 text-emerald-400" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
              Top 5 Return Contributors
            </h4>
          </div>
          <div className="mt-3 space-y-2">
            {run.top_contributors.length === 0 ? (
              <div className="text-xs text-atlas-text-muted">No positive contributors.</div>
            ) : (
              run.top_contributors.slice(0, 5).map((c, i) => (
                <div
                  key={c.symbol}
                  className="flex items-center justify-between rounded bg-atlas-surface-2/40 px-3 py-2 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/10 text-[10px] font-bold text-emerald-400">
                      #{i + 1}
                    </span>
                    <div>
                      <div className="font-semibold text-atlas-text-primary">{c.symbol}</div>
                      <div className="text-[10px] text-atlas-text-muted truncate max-w-[140px]">
                        {c.name}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-emerald-400">
                      +{formatBps(c.return_contribution)}
                    </div>
                    <div className="text-[10px] text-atlas-text-muted">
                      Wgt: {formatWeight(c.portfolio_weight)} | Ret: {formatPercent(c.security_return, 2, true)}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Top 5 Detractors */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-2.5">
            <TrendingDown className="h-4 w-4 text-rose-400" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
              Top 5 Return Detractors
            </h4>
          </div>
          <div className="mt-3 space-y-2">
            {run.top_detractors.length === 0 ? (
              <div className="text-xs text-atlas-text-muted">No negative detractors.</div>
            ) : (
              run.top_detractors.slice(0, 5).map((d, i) => (
                <div
                  key={d.symbol}
                  className="flex items-center justify-between rounded bg-atlas-surface-2/40 px-3 py-2 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-rose-500/10 text-[10px] font-bold text-rose-400">
                      #{i + 1}
                    </span>
                    <div>
                      <div className="font-semibold text-atlas-text-primary">{d.symbol}</div>
                      <div className="text-[10px] text-atlas-text-muted truncate max-w-[140px]">
                        {d.name}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-rose-400">
                      {formatBps(d.return_contribution)}
                    </div>
                    <div className="text-[10px] text-atlas-text-muted">
                      Wgt: {formatWeight(d.portfolio_weight)} | Ret: {formatPercent(d.security_return, 2, true)}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Comprehensive Security Contributions Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="flex flex-col gap-2 border-b border-atlas-border-default/40 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Security-Level Return Contributions
            </h3>
            <p className="text-xs text-atlas-text-secondary">
              Formula: Contribution C_j = w_P,j × R_P,j. Total sum reconciles exactly to Portfolio Return.
            </p>
          </div>
          <input
            type="text"
            placeholder="Search symbol or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none w-56"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary">
              <tr>
                <th
                  className="cursor-pointer px-3 py-2.5 font-medium hover:text-atlas-text-primary"
                  onClick={() => handleHeaderClick("rank")}
                >
                  Rank
                </th>
                <th
                  className="cursor-pointer px-3 py-2.5 font-medium hover:text-atlas-text-primary"
                  onClick={() => handleHeaderClick("symbol")}
                >
                  Symbol
                </th>
                <th className="px-3 py-2.5 font-medium font-sans">Security Name</th>
                <th
                  className="cursor-pointer px-3 py-2.5 font-medium hover:text-atlas-text-primary font-sans"
                  onClick={() => handleHeaderClick("category_label")}
                >
                  Sector
                </th>
                <th
                  className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                  onClick={() => handleHeaderClick("portfolio_weight")}
                >
                  Portfolio Weight
                </th>
                <th
                  className="cursor-pointer px-3 py-2.5 text-right font-medium hover:text-atlas-text-primary"
                  onClick={() => handleHeaderClick("security_return")}
                >
                  Security Return
                </th>
                <th
                  className="cursor-pointer px-3 py-2.5 text-right font-semibold text-atlas-accent hover:underline"
                  onClick={() => handleHeaderClick("return_contribution")}
                >
                  Return Contribution
                </th>
                <th className="px-3 py-2.5 text-right font-medium">Bps Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40 text-atlas-text-primary">
              {sortedSecurities.map((sec) => (
                <tr key={sec.symbol} className="hover:bg-atlas-surface-2/40 transition-colors">
                  <td className="px-3 py-2 text-atlas-text-muted">#{sec.rank}</td>
                  <td className="px-3 py-2 font-bold text-atlas-text-primary">{sec.symbol}</td>
                  <td className="px-3 py-2 font-sans truncate max-w-[200px] text-atlas-text-secondary">
                    {sec.name}
                  </td>
                  <td className="px-3 py-2 font-sans text-atlas-text-muted">{sec.category_label}</td>
                  <td className="px-3 py-2 text-right">{formatWeight(sec.portfolio_weight)}</td>
                  <td className={`px-3 py-2 text-right ${getEffectColorClass(sec.security_return)}`}>
                    {formatPercent(sec.security_return, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right font-bold ${getEffectColorClass(sec.return_contribution)}`}>
                    {formatPercent(sec.return_contribution, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right font-semibold ${getEffectColorClass(sec.return_contribution)}`}>
                    {formatBps(sec.return_contribution)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t-2 border-atlas-border-default/80 bg-atlas-surface-2/80 font-semibold text-atlas-text-primary">
              <tr>
                <td colSpan={4} className="px-3 py-2.5 font-sans">
                  Total Reconciled Contributions ({run.security_contributions.length} items)
                </td>
                <td className="px-3 py-2.5 text-right">100.00%</td>
                <td className="px-3 py-2.5 text-right">—</td>
                <td className={`px-3 py-2.5 text-right text-sm font-bold ${getEffectColorClass(run.reconciliation.security_contributions_sum)}`}>
                  {formatPercent(run.reconciliation.security_contributions_sum, 2, true)}
                </td>
                <td className="px-3 py-2.5 text-right">
                  {formatBps(run.reconciliation.security_contributions_sum)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}

