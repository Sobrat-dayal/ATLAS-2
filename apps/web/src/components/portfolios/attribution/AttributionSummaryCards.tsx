"use client";

import React from "react";
import { Badge } from "@/design-system";
import {
  formatBps,
  formatPercent,
  getEffectBgClass,
  getEffectColorClass,
  getReconciliationBadge,
} from "@/lib/portfolios/attribution/formatting";
import { AttributionRunDTO } from "@/lib/portfolios/attribution/types";
import {
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  PieChart,
  ShieldAlert,
  Sparkles,
  TrendingUp,
} from "lucide-react";

interface AttributionSummaryCardsProps {
  run: AttributionRunDTO;
}

export function AttributionSummaryCards({ run }: AttributionSummaryCardsProps) {
  const recBadge = getReconciliationBadge(run.reconciliation.status);
  const activeNum = parseFloat(run.active_return || "0");
  const allocNum = parseFloat(run.total_allocation_effect || "0");
  const selectNum = parseFloat(run.total_selection_effect || "0");
  const interNum = parseFloat(run.total_interaction_effect || "0");

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
      {/* Portfolio Return */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
          Portfolio Return
        </div>
        <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
          {formatPercent(run.portfolio_return, 2, true)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          NAV-Weighted
        </div>
      </div>

      {/* Benchmark Return */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
          Benchmark ({run.benchmark_id.replace("BENCHMARK_", "")})
        </div>
        <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
          {formatPercent(run.benchmark_return, 2, true)}
        </div>
        <div className="mt-1 truncate text-[11px] text-atlas-text-muted" title={run.benchmark_name}>
          {run.benchmark_name}
        </div>
      </div>

      {/* Active Return */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
            Active Return
          </span>
          {activeNum >= 0 ? (
            <ArrowUpRight className="h-3.5 w-3.5 text-emerald-400" />
          ) : (
            <ArrowDownRight className="h-3.5 w-3.5 text-rose-400" />
          )}
        </div>
        <div className={`mt-1 text-lg font-bold ${getEffectColorClass(run.active_return)}`}>
          {formatPercent(run.active_return, 2, true)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          {formatBps(run.active_return)}
        </div>
      </div>

      {/* Allocation Effect */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
          Allocation Effect
        </div>
        <div className={`mt-1 text-base font-semibold ${getEffectColorClass(run.total_allocation_effect)}`}>
          {formatPercent(run.total_allocation_effect, 2, true)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          {formatBps(run.total_allocation_effect)}
        </div>
      </div>

      {/* Selection Effect */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
          Selection Effect
        </div>
        <div className={`mt-1 text-base font-semibold ${getEffectColorClass(run.total_selection_effect)}`}>
          {formatPercent(run.total_selection_effect, 2, true)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          {formatBps(run.total_selection_effect)}
        </div>
      </div>

      {/* Interaction Effect */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
          Interaction
        </div>
        <div className={`mt-1 text-base font-semibold ${getEffectColorClass(run.total_interaction_effect)}`}>
          {formatPercent(run.total_interaction_effect, 2, true)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          {formatBps(run.total_interaction_effect)}
        </div>
      </div>

      {/* Audit & Reconciliation */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
          Audit Status
        </div>
        <div className="mt-1.5 flex items-center gap-1.5">
          <span
            className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold ${recBadge.colorClass}`}
          >
            {recBadge.label}
          </span>
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          Residual: {formatBps(run.reconciliation_residual)}
        </div>
      </div>
    </div>
  );
}

