"use client";

import React from "react";
import { Badge } from "@/design-system";
import { formatCurrency, formatRate, getCompletenessBadge } from "@/lib/portfolios/performance/formatting";
import { PerformanceResponse } from "@/lib/portfolios/performance/types";
import {
  ArrowDownRight,
  ArrowUpRight,
  Award,
  Calendar,
  DollarSign,
  Layers,
  Scale,
  TrendingUp,
} from "lucide-react";

interface PerformanceSummaryCardsProps {
  summary: PerformanceResponse | null;
  loading: boolean;
}

export function PerformanceSummaryCards({ summary, loading }: PerformanceSummaryCardsProps) {
  if (loading || !summary) {
    return (
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-28 animate-pulse rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1 p-4"
          />
        ))}
      </div>
    );
  }

  const twr = summary.twr_cumulative ? parseFloat(summary.twr_cumulative) : null;
  const isTwrPositive = twr !== null && twr > 0;
  const isTwrNegative = twr !== null && twr < 0;

  const ann = summary.twr_annualized ? parseFloat(summary.twr_annualized) : null;
  const mwr = summary.mwr_xirr ? parseFloat(summary.mwr_xirr) : null;
  const gain = parseFloat(summary.investment_gain);
  const isGainPositive = gain > 0;

  const completeness = getCompletenessBadge(summary.data_quality.completeness);

  return (
    <div className="space-y-3">
      {/* Top Banner Notice for Data Quality */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1/50 px-3 py-1.5 text-xs">
        <div className="flex items-center gap-2">
          <Badge variant={completeness.variant}>
            {completeness.label}
          </Badge>
          <span className="text-atlas-text-secondary">
            Period: <span className="font-mono text-atlas-text-primary">{summary.period_type}</span> ({new Date(summary.period_start).toLocaleDateString()} &rarr; {new Date(summary.period_end).toLocaleDateString()})
          </span>
          <span className="text-atlas-border-default">|</span>
          <span className="text-atlas-text-secondary">
            Methodology: <span className="font-medium text-atlas-text-primary">{summary.methodology === "EXACT_TWR" ? "Exact Subperiod TWR" : "Modified Dietz (Approx)"}</span>
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px] text-atlas-text-tertiary">
          <span>Rev: #{summary.calculation_version}</span>
          <span>Hash: {summary.input_hash.slice(0, 8)}...</span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {/* Card 1: Time-Weighted Return (Cumulative) */}
        <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-3 shadow-xs">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-medium">Time-Weighted Return</span>
            <TrendingUp className="h-4 w-4 text-atlas-accent" />
          </div>
          <div className="mt-1.5 flex items-baseline gap-2">
            <span
              className={`text-2xl font-bold font-mono tracking-tight ${
                isTwrPositive
                  ? "text-emerald-400"
                  : isTwrNegative
                  ? "text-rose-400"
                  : "text-atlas-text-primary"
              }`}
            >
              {formatRate(summary.twr_cumulative)}
            </span>
            <span className="text-[11px] text-atlas-text-tertiary">cumulative</span>
          </div>
          <div className="mt-2 flex items-center justify-between border-t border-atlas-border-default/40 pt-1.5 text-[11px] text-atlas-text-secondary">
            <span>Subperiods: {summary.subperiods.length}</span>
            <span>Unbiased by flows</span>
          </div>
        </div>

        {/* Card 2: Annualized TWR Return */}
        <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-3 shadow-xs">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-medium">Annualized Return (CAGR)</span>
            <Calendar className="h-4 w-4 text-atlas-accent" />
          </div>
          <div className="mt-1.5 flex items-baseline gap-2">
            <span
              className={`text-2xl font-bold font-mono tracking-tight ${
                ann && ann > 0
                  ? "text-emerald-400"
                  : ann && ann < 0
                  ? "text-rose-400"
                  : "text-atlas-text-primary"
              }`}
            >
              {summary.twr_annualized ? formatRate(summary.twr_annualized) : "N/A (<1Y)"}
            </span>
            <span className="text-[11px] text-atlas-text-tertiary">p.a.</span>
          </div>
          <div className="mt-2 flex items-center justify-between border-t border-atlas-border-default/40 pt-1.5 text-[11px] text-atlas-text-secondary">
            <span>Formula: (1+R)^(365/D) - 1</span>
            <span>Geometric</span>
          </div>
        </div>

        {/* Card 3: Money-Weighted Return / XIRR */}
        <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-3 shadow-xs">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-medium">Money-Weighted (XIRR)</span>
            <Scale className="h-4 w-4 text-atlas-accent" />
          </div>
          <div className="mt-1.5 flex items-baseline gap-2">
            <span
              className={`text-2xl font-bold font-mono tracking-tight ${
                mwr && mwr > 0
                  ? "text-emerald-400"
                  : mwr && mwr < 0
                  ? "text-rose-400"
                  : "text-atlas-text-primary"
              }`}
            >
              {summary.mwr_xirr ? formatRate(summary.mwr_xirr) : "--"}
            </span>
            <span className="text-[11px] text-atlas-text-tertiary">investor IRR</span>
          </div>
          <div className="mt-2 flex items-center justify-between border-t border-atlas-border-default/40 pt-1.5 text-[11px] text-atlas-text-secondary">
            <span>ACT/365 solver</span>
            <span>Flow-weighted</span>
          </div>
        </div>

        {/* Card 4: Net Investment Gain / Loss */}
        <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-3 shadow-xs">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-medium">Net Investment Gain</span>
            <DollarSign className="h-4 w-4 text-atlas-accent" />
          </div>
          <div className="mt-1.5 flex items-baseline gap-2">
            <span
              className={`text-2xl font-bold font-mono tracking-tight ${
                isGainPositive
                  ? "text-emerald-400"
                  : gain < 0
                  ? "text-rose-400"
                  : "text-atlas-text-primary"
              }`}
            >
              {isGainPositive ? `+${formatCurrency(gain, summary.base_currency)}` : formatCurrency(gain, summary.base_currency)}
            </span>
          </div>
          <div className="mt-2 flex items-center justify-between border-t border-atlas-border-default/40 pt-1.5 text-[11px] text-atlas-text-secondary">
            <span>Ending - Beg - NetFlows</span>
            <span>{summary.base_currency}</span>
          </div>
        </div>
      </div>

      {/* Balance Reconciliation Bar */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1 p-3 text-xs">
        <div>
          <div className="text-atlas-text-tertiary text-[11px]">Beginning Value</div>
          <div className="mt-0.5 font-mono font-medium text-atlas-text-primary">
            {formatCurrency(summary.beginning_value, summary.base_currency)}
          </div>
        </div>
        <div>
          <div className="text-atlas-text-tertiary text-[11px]">Net External Flows</div>
          <div className="mt-0.5 font-mono font-medium text-atlas-text-primary flex items-center gap-1">
            {parseFloat(summary.net_external_flows) > 0 ? (
              <ArrowUpRight className="h-3 w-3 text-emerald-400" />
            ) : parseFloat(summary.net_external_flows) < 0 ? (
              <ArrowDownRight className="h-3 w-3 text-blue-400" />
            ) : null}
            {formatCurrency(summary.net_external_flows, summary.base_currency)}
          </div>
        </div>
        <div>
          <div className="text-atlas-text-tertiary text-[11px]">Ending Marked Value</div>
          <div className="mt-0.5 font-mono font-semibold text-atlas-accent">
            {formatCurrency(summary.ending_value, summary.base_currency)}
          </div>
        </div>
        <div>
          <div className="text-atlas-text-tertiary text-[11px]">Total Contributions / Withdrawals</div>
          <div className="mt-0.5 font-mono text-[11px] text-atlas-text-secondary">
            +{formatCurrency(summary.total_contributions, summary.base_currency)} / -{formatCurrency(summary.total_withdrawals, summary.base_currency)}
          </div>
        </div>
      </div>
    </div>
  );
}
