"use client";

import React from "react";
import { Badge } from "@/design-system";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  formatWeightPercent,
  getObjectiveLabel,
  getSolverStatusBadge,
} from "@/lib/portfolios/optimization/formatting";
import { PortfolioOptimizationRunDTO } from "@/lib/portfolios/optimization/types";
import {
  Activity,
  ArrowRightLeft,
  CheckCircle2,
  Cpu,
  DollarSign,
  Gauge,
  Percent,
  TrendingUp,
} from "lucide-react";

interface OptimizationSummaryCardsProps {
  run: PortfolioOptimizationRunDTO;
}

export function OptimizationSummaryCards({ run }: OptimizationSummaryCardsProps) {
  const cand = run.candidate;
  const solverBadge = getSolverStatusBadge(run.diagnostics.status);

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {/* 1. Expected Return */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
            Expected Return
          </span>
          <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
        </div>
        <div className="mt-1 text-lg font-semibold text-emerald-400">
          {formatPercent(cand.estimated_return, 2)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          Annualized ({run.expected_returns.model.replace(/_/g, " ")})
        </div>
      </div>

      {/* 2. Expected Volatility */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
            Expected Volatility
          </span>
          <Activity className="h-3.5 w-3.5 text-atlas-accent-gold" />
        </div>
        <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
          {formatWeightPercent(cand.estimated_volatility, 2)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          Annualized Dispersion (σ)
        </div>
      </div>

      {/* 3. Sharpe Ratio */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
            Sharpe Ratio
          </span>
          <Gauge className="h-3.5 w-3.5 text-cyan-400" />
        </div>
        <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
          {cand.estimated_sharpe ? formatNumber(cand.estimated_sharpe, 2) : "—"}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          Excess / Volatility (Rf = 4.5%)
        </div>
      </div>

      {/* 4. One-Way Turnover */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
            Rebalancing Turnover
          </span>
          <ArrowRightLeft className="h-3.5 w-3.5 text-blue-400" />
        </div>
        <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
          {formatWeightPercent(cand.estimated_turnover, 2)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          One-Way Capital Reallocation
        </div>
      </div>

      {/* 5. Estimated Cost */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
            Est. Transaction Cost
          </span>
          <DollarSign className="h-3.5 w-3.5 text-amber-400" />
        </div>
        <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
          {formatCurrency(cand.estimated_cost, run.base_currency)}
        </div>
        <div className="mt-1 text-[11px] text-atlas-text-muted">
          Based on 10 bps friction rate
        </div>
      </div>

      {/* 6. Solver Diagnostics */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
            Solver Status
          </span>
          <Cpu className="h-3.5 w-3.5 text-purple-400" />
        </div>
        <div className="mt-1 flex items-center gap-1.5">
          <Badge variant={solverBadge.variant} className="text-[11px] font-mono uppercase">
            {solverBadge.label}
          </Badge>
        </div>
        <div className="mt-1 truncate text-[11px] text-atlas-text-muted">
          {run.diagnostics.iterations} iters in {run.diagnostics.solve_time_ms}ms
        </div>
      </div>
    </div>
  );
}
