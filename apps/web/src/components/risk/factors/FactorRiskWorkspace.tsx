"use client";

import React from "react";
import {
  FactorRiskRunDTO,
  SecurityFactorExposureDTO,
} from "@/lib/risk/types";
import {
  formatFactorLoading,
  formatVolPercent,
  formatWeight,
  getModelDiagnosticStatusBadge,
} from "@/lib/risk/formatting";
import {
  Activity,
  AlertCircle,
  BarChart2,
  CheckCircle2,
  Cpu,
  Layers,
  RefreshCw,
  Shield,
  TrendingUp,
} from "lucide-react";

interface FactorRiskWorkspaceProps {
  factorRun: FactorRiskRunDTO | null;
  securityExposures?: SecurityFactorExposureDTO[];
  calculating: boolean;
  onRecalculate: () => void;
}

export function FactorRiskWorkspace({
  factorRun,
  securityExposures,
  calculating,
  onRecalculate,
}: FactorRiskWorkspaceProps) {
  if (!factorRun) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-atlas-border-default/60 rounded m-4 bg-atlas-surface-1/40">
        <Cpu className="h-10 w-10 text-atlas-text-secondary/50 mb-3 animate-pulse" />
        <h3 className="text-sm font-semibold text-atlas-text-primary">No Factor Risk Run Available</h3>
        <p className="text-xs text-atlas-text-secondary max-w-md mt-1 mb-4">
          Execute multi-factor regression and covariance decomposition to analyze systematic and idiosyncratic risk.
        </p>
        <button
          onClick={onRecalculate}
          disabled={calculating}
          className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-black transition hover:bg-atlas-accent/90 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${calculating ? "animate-spin" : ""}`} />
          Calculate Factor Risk
        </button>
      </div>
    );
  }

  const sysVarRatio =
    factorRun.total_variance > 0
      ? (factorRun.systematic_variance / factorRun.total_variance) * 100
      : 0;
  const specVarRatio =
    factorRun.total_variance > 0
      ? (factorRun.specific_variance / factorRun.total_variance) * 100
      : 0;

  const diagBadge = getModelDiagnosticStatusBadge(factorRun.diagnostics.status);

  return (
    <div className="space-y-4 p-4">
      {/* 1. Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
              Multi-Factor Equity Risk
            </span>
            <span className="rounded bg-atlas-surface-2 px-1.5 py-0.5 text-[10px] font-mono text-atlas-text-secondary border border-atlas-border-default">
              {factorRun.model_id} v{factorRun.model_version}
            </span>
          </div>

          <div className="h-4 w-px bg-atlas-border-default" />

          {/* Diagnostic Status Badge */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-atlas-text-secondary">Diagnostics:</span>
            <span
              className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase ${diagBadge.bgClass} ${diagBadge.textClass} ${diagBadge.borderClass}`}
            >
              {diagBadge.label} (Cond: {factorRun.diagnostics.condition_number.toFixed(1)})
            </span>
          </div>

          {/* Reconciliation Status */}
          {factorRun.is_reconciled && (
            <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Reconciled (diff &lt; 1e-5)
            </span>
          )}
        </div>

        <button
          onClick={onRecalculate}
          disabled={calculating}
          className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-black transition hover:bg-atlas-accent/90 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${calculating ? "animate-spin" : ""}`} />
          Recalculate Factors
        </button>
      </div>

      {/* 2. Top Summary Metrics Grid */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Volatility */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Total Risk (σ_P)</span>
            <Activity className="h-4 w-4 text-atlas-accent" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-atlas-text-primary">
            {formatVolPercent(factorRun.total_volatility)}
          </div>
          <div className="mt-1 flex items-center justify-between text-[11px] text-atlas-text-secondary">
            <span>Total Variance (V_P):</span>
            <span className="font-mono">{factorRun.total_variance.toFixed(6)}</span>
          </div>
        </div>

        {/* Systematic Risk */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Systematic Risk</span>
            <TrendingUp className="h-4 w-4 text-sky-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-sky-400">
            {formatVolPercent(Math.sqrt(Math.max(0, factorRun.systematic_variance)))}
          </div>
          <div className="mt-1 flex items-center justify-between text-[11px] text-atlas-text-secondary">
            <span>Share of Variance:</span>
            <span className="font-mono text-sky-400 font-semibold">{sysVarRatio.toFixed(1)}%</span>
          </div>
        </div>

        {/* Specific / Idiosyncratic Risk */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Specific (Residual)</span>
            <Shield className="h-4 w-4 text-amber-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-amber-400">
            {formatVolPercent(Math.sqrt(Math.max(0, factorRun.specific_variance)))}
          </div>
          <div className="mt-1 flex items-center justify-between text-[11px] text-atlas-text-secondary">
            <span>Share of Variance:</span>
            <span className="font-mono text-amber-400 font-semibold">{specVarRatio.toFixed(1)}%</span>
          </div>
        </div>

        {/* Factor Count & Rank */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5">
          <div className="flex items-center justify-between text-atlas-text-secondary">
            <span className="text-[11px] uppercase tracking-wider font-semibold">Design Matrix Rank</span>
            <Layers className="h-4 w-4 text-purple-400" />
          </div>
          <div className="mt-1 text-2xl font-bold font-mono text-purple-400">
            {factorRun.diagnostics.design_matrix_rank} / {factorRun.diagnostics.factor_count}
          </div>
          <div className="mt-1 flex items-center justify-between text-[11px] text-atlas-text-secondary">
            <span>Observations:</span>
            <span className="font-mono">{factorRun.diagnostics.observation_count} days</span>
          </div>
        </div>
      </div>

      {/* 3. Factor Exposure & Risk Contribution Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="border-b border-atlas-border-default/40 p-3">
          <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
            Systematic Factor Exposures & Euler Risk Contributions
          </h4>
          <p className="text-[11px] text-atlas-text-secondary mt-0.5">
            Euler variance contribution VC_k = b_k (F b)_k and volatility contribution RC_k = VC_k / σ_P.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default/40 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3">Factor</th>
                <th className="py-2.5 px-3">Name</th>
                <th className="py-2.5 px-3 text-right">Portfolio Loading (b_P)</th>
                <th className="py-2.5 px-3 text-right">Benchmark (b_B)</th>
                <th className="py-2.5 px-3 text-right">Active Tilt (b_A)</th>
                <th className="py-2.5 px-3 text-right">Var Contrib (VC_k)</th>
                <th className="py-2.5 px-3 text-right">Vol Contrib (RC_k)</th>
                <th className="py-2.5 px-3 text-right">% Variance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/30 font-mono text-atlas-text-primary">
              {factorRun.factor_contributions.map((c) => {
                const b_p = c.portfolio_exposure;
                const b_b = factorRun.benchmark_exposures?.[c.factor_id] ?? 0;
                const b_a = factorRun.active_exposures?.[c.factor_id] ?? (b_p - b_b);
                const activeColor = b_a > 0.05 ? "text-emerald-400" : b_a < -0.05 ? "text-rose-400" : "text-atlas-text-secondary";

                return (
                  <tr key={c.factor_id} className="hover:bg-atlas-surface-2/30 transition">
                    <td className="py-2.5 px-3 font-semibold text-atlas-accent">{c.factor_id.replace("FACTOR_", "")}</td>
                    <td className="py-2.5 px-3 font-sans text-atlas-text-primary">{c.factor_name}</td>
                    <td className="py-2.5 px-3 text-right font-bold">{formatFactorLoading(b_p)}</td>
                    <td className="py-2.5 px-3 text-right text-atlas-text-secondary">{formatFactorLoading(b_b)}</td>
                    <td className={`py-2.5 px-3 text-right font-semibold ${activeColor}`}>
                      {formatFactorLoading(b_a)}
                    </td>
                    <td className="py-2.5 px-3 text-right">{c.variance_contribution.toFixed(6)}</td>
                    <td className="py-2.5 px-3 text-right font-bold text-sky-400">{formatVolPercent(c.volatility_contribution)}</td>
                    <td className="py-2.5 px-3 text-right">{(c.percentage_of_variance * 100).toFixed(1)}%</td>
                  </tr>
                );
              })}

              {/* Specific Risk Row */}
              <tr className="bg-atlas-surface-2/40 font-semibold border-t border-atlas-border-default/60">
                <td className="py-2.5 px-3 text-amber-400">SPECIFIC</td>
                <td className="py-2.5 px-3 font-sans text-amber-400">Idiosyncratic Residual Risk</td>
                <td className="py-2.5 px-3 text-right text-atlas-text-secondary">—</td>
                <td className="py-2.5 px-3 text-right text-atlas-text-secondary">—</td>
                <td className="py-2.5 px-3 text-right text-atlas-text-secondary">—</td>
                <td className="py-2.5 px-3 text-right text-amber-400">
                  {factorRun.specific_variance.toFixed(6)}
                </td>
                <td className="py-2.5 px-3 text-right font-bold text-amber-400">
                  {formatVolPercent(factorRun.specific_risk_contribution)}
                </td>
                <td className="py-2.5 px-3 text-right text-amber-400">{specVarRatio.toFixed(1)}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. Security-Level Factor Exposures Table */}
      {factorRun.security_exposures && factorRun.security_exposures.length > 0 && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
          <div className="border-b border-atlas-border-default/40 p-3">
            <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
              Security-Level Factor Loadings & Regression Fit
            </h4>
            <p className="text-[11px] text-atlas-text-secondary mt-0.5">
              Ordinary Least Squares (OLS) beta loadings, residual variance s_ε^2, and R-squared goodness of fit.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-xs">
              <thead>
                <tr className="border-b border-atlas-border-default/40 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary font-semibold uppercase tracking-wider">
                  <th className="py-2 px-3">Symbol</th>
                  {factorRun.factor_ids.map((fid) => (
                    <th key={fid} className="py-2 px-3 text-right">
                      {fid.replace("FACTOR_", "")} Beta
                    </th>
                  ))}
                  <th className="py-2 px-3 text-right">Intercept (α)</th>
                  <th className="py-2 px-3 text-right">R²</th>
                  <th className="py-2 px-3 text-right">Residual Var (s_ε²)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/30 font-mono text-atlas-text-primary">
                {factorRun.security_exposures.map((sec) => (
                  <tr key={sec.symbol} className="hover:bg-atlas-surface-2/30 transition">
                    <td className="py-2 px-3 font-bold text-atlas-accent">{sec.symbol}</td>
                    {factorRun.factor_ids.map((fid) => {
                      const b = sec.factor_betas[fid] ?? 0;
                      return (
                        <td key={fid} className="py-2 px-3 text-right">
                          {formatFactorLoading(b)}
                        </td>
                      );
                    })}
                    <td className="py-2 px-3 text-right">{sec.intercept ? sec.intercept.toFixed(4) : "0.0000"}</td>
                    <td className="py-2 px-3 text-right font-bold text-sky-400">
                      {(sec.r_squared * 100).toFixed(1)}%
                    </td>
                    <td className="py-2 px-3 text-right text-atlas-text-secondary">
                      {sec.residual_variance.toFixed(6)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

