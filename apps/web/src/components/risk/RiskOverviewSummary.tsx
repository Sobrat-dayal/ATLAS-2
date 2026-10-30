"use client";

import React from "react";
import {
  formatDays,
  formatRatio,
  formatSignedPercent,
  formatVolPercent,
  getCalculationStatusBadge,
  getDataCoverageBadge,
} from "@/lib/risk/formatting";
import {
  BenchmarkSensitivityDTO,
  PortfolioRiskSummaryDTO,
  RiskCalculationRunDTO,
  RiskDataCoverageDTO,
} from "@/lib/risk/types";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  CheckCircle2,
  Compass,
  Database,
  Flame,
  Gauge,
  Percent,
  ShieldAlert,
} from "lucide-react";

interface RiskOverviewSummaryProps {
  summary: PortfolioRiskSummaryDTO | null;
  run: RiskCalculationRunDTO | null;
  benchmarkSensitivity: BenchmarkSensitivityDTO | null;
  dataQuality: RiskDataCoverageDTO | null;
}

export function RiskOverviewSummary({
  summary,
  run,
  benchmarkSensitivity,
  dataQuality,
}: RiskOverviewSummaryProps) {
  const histVol = summary?.historical_volatility ?? run?.historical_volatility;
  const modelVol = summary?.model_volatility ?? run?.model_estimated_volatility;
  const maxDD = summary?.max_drawdown ?? run?.max_drawdown;
  const curDD = summary?.current_drawdown ?? run?.current_drawdown;
  const beta = summary?.beta ?? benchmarkSensitivity?.beta;
  const correlation = summary?.correlation ?? benchmarkSensitivity?.correlation;
  const trackingError = summary?.tracking_error ?? benchmarkSensitivity?.tracking_error_annualized;
  const coverageRatio = summary?.coverage_ratio ?? dataQuality?.coverage_ratio ?? 1.0;
  const coverageStatus = dataQuality?.status ?? (coverageRatio >= 1.0 ? "FULL" : "ACCEPTABLE");

  const calcStatus = summary?.status ?? run?.status ?? "COMPLETED";
  const calcBadge = getCalculationStatusBadge(calcStatus);
  const covBadge = getDataCoverageBadge(coverageStatus);

  return (
    <div className="space-y-3">
      {/* Top Banner Status Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-atlas-border-default/60 bg-atlas-surface-1 px-4 py-2 text-xs">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-atlas-text-primary">ATLAS Core Risk Foundation</span>
          <span className="text-atlas-text-muted">|</span>
          <span className="text-atlas-text-secondary">
            Currency: <span className="font-medium text-atlas-text-primary">{summary?.reporting_currency || run?.reporting_currency || "USD"}</span>
          </span>
          <span className="text-atlas-text-muted">|</span>
          <span className="text-atlas-text-secondary">
            As-of: <span className="font-mono text-atlas-text-primary">{summary?.as_of?.substring(0, 10) || run?.calculation_as_of?.substring(0, 10) || "Live"}</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Data Quality Badge */}
          <div
            className={`flex items-center gap-1 rounded border px-2 py-0.5 font-medium ${covBadge.bgClass} ${covBadge.textClass} ${covBadge.borderClass}`}
          >
            <Database className="h-3 w-3" />
            <span>Coverage: {(coverageRatio * 100).toFixed(1)}% ({covBadge.label})</span>
          </div>

          {/* Calculation Status Badge */}
          <div
            className={`flex items-center gap-1 rounded border px-2 py-0.5 font-medium ${calcBadge.bgClass} ${calcBadge.textClass} ${calcBadge.borderClass}`}
          >
            <CheckCircle2 className="h-3 w-3" />
            <span>{calcBadge.label}</span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
        {/* 1. Historical Volatility */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Historical Vol
            </span>
            <Activity className="h-3.5 w-3.5 text-atlas-accent-gold" />
          </div>
          <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
            {formatVolPercent(histVol, 2)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            Annualized (K=252, Bessel s)
          </div>
        </div>

        {/* 2. Model-Estimated Volatility */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Model Vol (Euler)
            </span>
            <Gauge className="h-3.5 w-3.5 text-blue-400" />
          </div>
          <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
            {formatVolPercent(modelVol, 2)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            Parametric: √(wᵀ Σ w)
          </div>
        </div>

        {/* 3. Max Drawdown */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Max Drawdown
            </span>
            <Flame className="h-3.5 w-3.5 text-rose-400" />
          </div>
          <div className="mt-1 text-lg font-semibold text-rose-400">
            {formatSignedPercent(maxDD, 2)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            Peak-to-Trough Watermark
          </div>
        </div>

        {/* 4. Current Drawdown */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Current Drawdown
            </span>
            <ArrowDownRight className="h-3.5 w-3.5 text-amber-400" />
          </div>
          <div className="mt-1 text-lg font-semibold text-amber-400">
            {formatSignedPercent(curDD, 2)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            {(curDD ?? 0) === 0 ? "At All-Time High" : "Under Water"}
          </div>
        </div>

        {/* 5. Benchmark Beta */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Beta (β)
            </span>
            <Compass className="h-3.5 w-3.5 text-emerald-400" />
          </div>
          <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
            {formatRatio(beta, 2)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            vs {benchmarkSensitivity?.benchmark_symbol || "SPY"} (Cov/Var)
          </div>
        </div>

        {/* 6. Benchmark Correlation */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Correlation (ρ)
            </span>
            <Percent className="h-3.5 w-3.5 text-cyan-400" />
          </div>
          <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
            {formatRatio(correlation, 2)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            Pearson Sample r
          </div>
        </div>

        {/* 7. Tracking Error */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Tracking Error
            </span>
            <ShieldAlert className="h-3.5 w-3.5 text-purple-400" />
          </div>
          <div className="mt-1 text-lg font-semibold text-atlas-text-primary">
            {formatVolPercent(trackingError, 2)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            Annualized Active Vol
          </div>
        </div>
      </div>
    </div>
  );
}

