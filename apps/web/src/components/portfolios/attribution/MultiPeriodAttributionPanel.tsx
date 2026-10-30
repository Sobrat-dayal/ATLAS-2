"use client";

import React from "react";
import {
  formatBps,
  formatDateRange,
  formatPercent,
  getEffectColorClass,
} from "@/lib/portfolios/attribution/formatting";
import { AttributionRunDTO } from "@/lib/portfolios/attribution/types";
import { Calendar, CheckCircle2, Link2, ShieldCheck } from "lucide-react";

interface MultiPeriodAttributionPanelProps {
  run: AttributionRunDTO;
}

export function MultiPeriodAttributionPanel({ run }: MultiPeriodAttributionPanelProps) {
  const mp = run.multi_period;

  if (!mp || !mp.periods || mp.periods.length === 0) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-8 text-center">
        <Calendar className="mx-auto h-8 w-8 text-atlas-text-muted" />
        <h4 className="mt-2 text-sm font-semibold text-atlas-text-primary">
          Multi-Period Linking Not Computed
        </h4>
        <p className="mt-1 text-xs text-atlas-text-secondary">
          No sub-period breakdown is available for this single-period evaluation window.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Compound KPI Bridge Cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium text-atlas-text-secondary">
            Compounded Port Ret
          </div>
          <div className="mt-1 text-base font-bold text-atlas-text-primary">
            {formatPercent(mp.compound_portfolio_return, 2, true)}
          </div>
          <div className="mt-0.5 text-[10px] text-atlas-text-muted font-mono">
            {mp.period_count} Sub-Periods
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium text-atlas-text-secondary">
            Compounded Bench Ret
          </div>
          <div className="mt-1 text-base font-bold text-atlas-text-primary">
            {formatPercent(mp.compound_benchmark_return, 2, true)}
          </div>
          <div className="mt-0.5 text-[10px] text-atlas-text-muted font-mono">
            {run.benchmark_id.replace("BENCHMARK_", "")}
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium text-atlas-text-secondary">
            Compounded Active
          </div>
          <div className={`mt-1 text-base font-bold ${getEffectColorClass(mp.compound_active_return)}`}>
            {formatPercent(mp.compound_active_return, 2, true)}
          </div>
          <div className="mt-0.5 text-[10px] text-atlas-text-muted font-mono">
            {formatBps(mp.compound_active_return)}
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium text-atlas-text-secondary">
            Linked Allocation
          </div>
          <div className={`mt-1 text-base font-bold ${getEffectColorClass(mp.linked_allocation_effect)}`}>
            {formatPercent(mp.linked_allocation_effect, 2, true)}
          </div>
          <div className="mt-0.5 text-[10px] text-atlas-text-muted font-mono">
            {formatBps(mp.linked_allocation_effect)}
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium text-atlas-text-secondary">
            Linked Selection
          </div>
          <div className={`mt-1 text-base font-bold ${getEffectColorClass(mp.linked_selection_effect)}`}>
            {formatPercent(mp.linked_selection_effect, 2, true)}
          </div>
          <div className="mt-0.5 text-[10px] text-atlas-text-muted font-mono">
            {formatBps(mp.linked_selection_effect)}
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium text-atlas-text-secondary">
            Linked Interaction
          </div>
          <div className={`mt-1 text-base font-bold ${getEffectColorClass(mp.linked_interaction_effect)}`}>
            {formatPercent(mp.linked_interaction_effect, 2, true)}
          </div>
          <div className="mt-0.5 text-[10px] text-atlas-text-muted font-mono">
            {formatBps(mp.linked_interaction_effect)}
          </div>
        </div>
      </div>

      {/* Discrete Historical Periods Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="flex items-center justify-between border-b border-atlas-border-default/40 p-4">
          <div>
            <div className="flex items-center gap-2">
              <Link2 className="h-4 w-4 text-atlas-accent" />
              <h3 className="text-sm font-semibold text-atlas-text-primary">
                Discrete Historical Sub-Period Breakdown (Carino Logarithmic Linking)
              </h3>
            </div>
            <p className="mt-0.5 text-xs text-atlas-text-secondary">
              Each period t is scaled by logarithmic coefficient c_t such that Σ c_t · (A_t + S_t + I_t) ≡ R_P - R_B exactly.
            </p>
          </div>
          <div className="flex items-center gap-1.5 rounded bg-emerald-500/10 px-2 py-1 text-xs font-medium text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Exact Log Reconciled</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary">
              <tr>
                <th className="px-3 py-2.5 font-medium font-sans">Period</th>
                <th className="px-3 py-2.5 font-medium font-sans">Date Range</th>
                <th className="px-3 py-2.5 text-right font-medium">Port Return</th>
                <th className="px-3 py-2.5 text-right font-medium">Bench Return</th>
                <th className="px-3 py-2.5 text-right font-medium">Active Return</th>
                <th className="px-3 py-2.5 text-right font-medium">Allocation</th>
                <th className="px-3 py-2.5 text-right font-medium">Selection</th>
                <th className="px-3 py-2.5 text-right font-medium">Interaction</th>
                <th className="px-3 py-2.5 text-right font-medium text-atlas-accent">Carino Weight (c_t)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40 text-atlas-text-primary">
              {mp.periods.map((p) => (
                <tr key={p.period_index} className="hover:bg-atlas-surface-2/40 transition-colors">
                  <td className="px-3 py-2 font-sans font-semibold">{p.period_label}</td>
                  <td className="px-3 py-2 text-atlas-text-muted font-sans text-[11px]">
                    {formatDateRange(p.start_date, p.end_date)}
                  </td>
                  <td className="px-3 py-2 text-right">{formatPercent(p.portfolio_return, 2, true)}</td>
                  <td className="px-3 py-2 text-right">{formatPercent(p.benchmark_return, 2, true)}</td>
                  <td className={`px-3 py-2 text-right font-semibold ${getEffectColorClass(p.active_return)}`}>
                    {formatPercent(p.active_return, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right ${getEffectColorClass(p.allocation_effect)}`}>
                    {formatPercent(p.allocation_effect, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right ${getEffectColorClass(p.selection_effect)}`}>
                    {formatPercent(p.selection_effect, 2, true)}
                  </td>
                  <td className={`px-3 py-2 text-right ${getEffectColorClass(p.interaction_effect)}`}>
                    {formatPercent(p.interaction_effect, 2, true)}
                  </td>
                  <td className="px-3 py-2 text-right font-bold text-atlas-accent">
                    {parseFloat(p.carino_weight || "1").toFixed(4)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t-2 border-atlas-border-default/80 bg-atlas-surface-2/80 font-semibold text-atlas-text-primary">
              <tr>
                <td colSpan={2} className="px-3 py-2.5 font-sans">
                  Cumulative Linked Total (Compounded)
                </td>
                <td className="px-3 py-2.5 text-right">{formatPercent(mp.compound_portfolio_return, 2, true)}</td>
                <td className="px-3 py-2.5 text-right">{formatPercent(mp.compound_benchmark_return, 2, true)}</td>
                <td className={`px-3 py-2.5 text-right text-sm font-bold ${getEffectColorClass(mp.compound_active_return)}`}>
                  {formatPercent(mp.compound_active_return, 2, true)}
                </td>
                <td className={`px-3 py-2.5 text-right ${getEffectColorClass(mp.linked_allocation_effect)}`}>
                  {formatPercent(mp.linked_allocation_effect, 2, true)}
                </td>
                <td className={`px-3 py-2.5 text-right ${getEffectColorClass(mp.linked_selection_effect)}`}>
                  {formatPercent(mp.linked_selection_effect, 2, true)}
                </td>
                <td className={`px-3 py-2.5 text-right ${getEffectColorClass(mp.linked_interaction_effect)}`}>
                  {formatPercent(mp.linked_interaction_effect, 2, true)}
                </td>
                <td className="px-3 py-2.5 text-right text-atlas-text-muted">Σ ≡ Active</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}

