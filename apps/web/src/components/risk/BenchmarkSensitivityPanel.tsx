"use client";

import React from "react";
import { formatRatio, formatVolPercent } from "@/lib/risk/formatting";
import { BenchmarkSensitivityDTO } from "@/lib/risk/types";
import {
  AlertTriangle,
  CheckCircle2,
  Compass,
  Info,
  Percent,
  ShieldAlert,
} from "lucide-react";

interface BenchmarkSensitivityPanelProps {
  benchmarkSensitivity: BenchmarkSensitivityDTO | null;
}

export function BenchmarkSensitivityPanel({
  benchmarkSensitivity,
}: BenchmarkSensitivityPanelProps) {
  if (!benchmarkSensitivity) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center text-xs text-atlas-text-muted">
        No benchmark sensitivity analytics available for the selected portfolio.
      </div>
    );
  }

  const b = benchmarkSensitivity;
  const isDegraded = b.status !== "VALID";

  return (
    <div className="space-y-4">
      {/* Warning banner if degraded */}
      {isDegraded && (
        <div className="flex items-start gap-2.5 rounded border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-300">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
          <div>
            <span className="font-semibold">Benchmark Sensitivity Warning: </span>
            {b.warning || "Insufficient matched observations or degenerate benchmark variance."}
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Left: Benchmark Identity & Core Metrics */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-3">
            <Compass className="h-4 w-4 text-emerald-400" />
            <h4 className="text-sm font-semibold text-atlas-text-primary">
              Benchmark Specifications
            </h4>
          </div>

          <div className="mt-3 space-y-2.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Benchmark Symbol:</span>
              <span className="font-mono font-semibold text-atlas-text-primary">
                {b.benchmark_symbol}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Benchmark Name:</span>
              <span className="text-atlas-text-primary text-right">{b.benchmark_name}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Matched Observations:</span>
              <span className="font-mono text-atlas-text-primary">
                {b.matched_observations} dates
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Sample Covariance:</span>
              <span className="font-mono text-atlas-text-primary">
                {b.covariance !== null && b.covariance !== undefined
                  ? b.covariance.toExponential(4)
                  : "—"}
              </span>
            </div>
          </div>
        </div>

        {/* Middle: Sensitivity Coefficients */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-3">
            <Percent className="h-4 w-4 text-cyan-400" />
            <h4 className="text-sm font-semibold text-atlas-text-primary">
              Sensitivity & Systematic Risk
            </h4>
          </div>

          <div className="mt-3 space-y-3">
            <div className="flex items-center justify-between rounded bg-atlas-surface-2 p-2 text-xs">
              <div>
                <div className="font-medium text-atlas-text-secondary">Historical Beta (β)</div>
                <div className="text-[10px] text-atlas-text-muted">Cov(P, B) / Var(B)</div>
              </div>
              <div className="font-mono text-base font-bold text-emerald-400">
                {formatRatio(b.beta, 3)}
              </div>
            </div>

            <div className="flex items-center justify-between rounded bg-atlas-surface-2 p-2 text-xs">
              <div>
                <div className="font-medium text-atlas-text-secondary">Correlation (ρ)</div>
                <div className="text-[10px] text-atlas-text-muted">Pearson Correlation Coefficient</div>
              </div>
              <div className="font-mono text-base font-bold text-cyan-400">
                {formatRatio(b.correlation, 3)}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Active Risk & Tracking Error */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-3">
            <ShieldAlert className="h-4 w-4 text-purple-400" />
            <h4 className="text-sm font-semibold text-atlas-text-primary">
              Active Risk & Volatility
            </h4>
          </div>

          <div className="mt-3 space-y-2.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Portfolio Volatility:</span>
              <span className="font-mono text-atlas-text-primary">
                {formatVolPercent(b.portfolio_volatility_annualized, 2)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-atlas-text-secondary">Benchmark Volatility:</span>
              <span className="font-mono text-atlas-text-primary">
                {formatVolPercent(b.benchmark_volatility_annualized, 2)}
              </span>
            </div>
            <div className="flex items-center justify-between border-t border-atlas-border-default/30 pt-2 font-medium">
              <span className="text-purple-300">Annualized Tracking Error:</span>
              <span className="font-mono text-sm font-bold text-purple-400">
                {formatVolPercent(b.tracking_error_annualized, 2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimers & Methodology Disclosure */}
      <div className="flex items-start gap-2.5 rounded border border-atlas-border-default/40 bg-atlas-surface-1/60 p-3 text-xs text-atlas-text-muted">
        <Info className="h-4 w-4 shrink-0 text-atlas-accent-blue mt-0.5" />
        <div className="space-y-1">
          <p className="font-medium text-atlas-text-secondary">
            Methodological Disclosures:
          </p>
          <p>
            Historical Beta reflects empirical co-movement and systematic sensitivity to the selected benchmark. It does not establish causal dependency, nor does it guarantee future market response during systemic market dislocations. Tracking error measures dispersion of active returns $(R_P - R_B)$ and scales via square-root-of-time ($\sqrt{252}$).
          </p>
        </div>
      </div>
    </div>
  );
}

