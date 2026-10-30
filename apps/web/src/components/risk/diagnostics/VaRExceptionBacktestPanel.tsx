"use client";

import React from "react";
import {
  VaRBacktestRunDTO,
  VaRModelType,
} from "@/lib/risk/types";
import {
  formatVaRReturn,
  getKupiecStatusBadge,
  getVaRModelLabel,
} from "@/lib/risk/formatting";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Play,
  RefreshCw,
  Scale,
  ShieldCheck,
  TrendingDown,
} from "lucide-react";

interface VaRExceptionBacktestPanelProps {
  backtest: VaRBacktestRunDTO | null;
  running: boolean;
  selectedModel: VaRModelType;
  selectedConfidence: number;
  selectedWindowSize: number;
  onSelectModel: (m: VaRModelType) => void;
  onSelectConfidence: (c: number) => void;
  onSelectWindowSize: (w: number) => void;
  onRunBacktest: () => void;
}

export function VaRExceptionBacktestPanel({
  backtest,
  running,
  selectedModel,
  selectedConfidence,
  selectedWindowSize,
  onSelectModel,
  onSelectConfidence,
  onSelectWindowSize,
  onRunBacktest,
}: VaRExceptionBacktestPanelProps) {
  const kupiec = backtest?.kupiec_result;
  const statusBadge = kupiec ? getKupiecStatusBadge(kupiec.status) : null;
  const observations = backtest?.observations || [];
  const exceptions = observations.filter((o) => o.is_exception);

  // SVG Chart Dimensions
  const chartHeight = 160;
  const chartWidth = 720;
  const paddingLeft = 35;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 25;
  const innerWidth = chartWidth - paddingLeft - paddingRight;
  const innerHeight = chartHeight - paddingTop - paddingBottom;

  const maxVal = Math.max(
    ...observations.map((o) => Math.max(o.forecast_var, o.realized_loss)),
    0.05
  );

  return (
    <div className="space-y-4">
      {/* 1. Backtest Configuration Controls */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Model Selector */}
          <div className="flex items-center gap-1">
            <span className="text-[11px] font-medium text-atlas-text-secondary uppercase tracking-wider mr-1">
              Model:
            </span>
            {(
              [
                { id: "HISTORICAL_SIMULATION", label: "Historical Sim" },
                { id: "PARAMETRIC_NORMAL", label: "Parametric Normal" },
              ] as const
            ).map((m) => (
              <button
                key={m.id}
                onClick={() => onSelectModel(m.id)}
                className={`rounded px-2.5 py-1 text-xs font-medium transition ${
                  selectedModel === m.id
                    ? "bg-atlas-accent-blue text-white shadow-sm"
                    : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>

          <div className="h-4 w-px bg-atlas-border-default/60 hidden sm:block" />

          {/* Confidence Selector */}
          <div className="flex items-center gap-1">
            <span className="text-[11px] font-medium text-atlas-text-secondary uppercase tracking-wider mr-1">
              Confidence:
            </span>
            {[0.95, 0.99].map((c) => (
              <button
                key={c}
                onClick={() => onSelectConfidence(c)}
                className={`rounded px-2 py-1 text-xs font-mono font-medium transition ${
                  selectedConfidence === c
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                {(c * 100).toFixed(1)}%
              </button>
            ))}
          </div>

          <div className="h-4 w-px bg-atlas-border-default/60 hidden sm:block" />

          {/* Window Size Selector */}
          <div className="flex items-center gap-1">
            <span className="text-[11px] font-medium text-atlas-text-secondary uppercase tracking-wider mr-1">
              Window:
            </span>
            {[100, 250, 500].map((w) => (
              <button
                key={w}
                onClick={() => onSelectWindowSize(w)}
                className={`rounded px-2 py-1 text-xs font-mono font-medium transition ${
                  selectedWindowSize === w
                    ? "bg-purple-500/20 text-purple-300 border border-purple-500/40"
                    : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                {w}D
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={onRunBacktest}
          disabled={running}
          className="flex items-center gap-1.5 rounded bg-atlas-accent-blue px-3.5 py-1.5 text-xs font-medium text-white hover:bg-atlas-accent-blue/90 disabled:opacity-50 transition shadow-sm"
        >
          <Play className={`h-3.5 w-3.5 ${running ? "animate-spin" : "fill-white"}`} />
          <span>{running ? "Backtesting..." : "Run VaR Backtest"}</span>
        </button>
      </div>

      {/* 2. Kupiec POF Scorecard */}
      {kupiec ? (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-2">
            <div className="flex items-center gap-2">
              <Scale className="h-4 w-4 text-atlas-accent-blue" />
              <div>
                <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
                  Kupiec Proportion of Failures (POF) Likelihood Ratio Test
                </h3>
                <span className="text-[10px] text-atlas-text-muted">
                  Unconditional Coverage Null Hypothesis H₀: p = {(1 - kupiec.confidence_level).toFixed(3)}
                </span>
              </div>
            </div>

            {statusBadge && (
              <span
                className={`rounded border px-2.5 py-1 text-xs font-semibold uppercase flex items-center gap-1.5 ${statusBadge.bgClass} ${statusBadge.textClass} ${statusBadge.borderClass}`}
              >
                {kupiec.status === "ACCEPT_UNCONDITIONAL_COVERAGE" ? (
                  <CheckCircle2 className="h-3.5 w-3.5" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5" />
                )}
                {statusBadge.label}
              </span>
            )}
          </div>

          {/* Test Statistics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 text-xs font-mono">
            {/* Stat 1: LR Statistic */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-2">
              <div className="text-[10px] text-atlas-text-muted font-sans">LR_UC Statistic</div>
              <div
                className={`text-base font-bold ${
                  kupiec.likelihood_ratio_stat > 3.841459 ? "text-rose-400" : "text-emerald-400"
                }`}
              >
                {kupiec.likelihood_ratio_stat.toFixed(4)}
              </div>
              <div className="text-[9px] text-atlas-text-muted">vs 3.8415 critical</div>
            </div>

            {/* Stat 2: P-Value */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-2">
              <div className="text-[10px] text-atlas-text-muted font-sans">P-Value (Chi² df=1)</div>
              <div className="text-base font-bold text-atlas-text-primary">
                {kupiec.p_value.toFixed(4)}
              </div>
              <div className="text-[9px] text-atlas-text-muted">
                {kupiec.p_value >= 0.05 ? "p >= 0.05 (Valid)" : "p < 0.05 (Reject)"}
              </div>
            </div>

            {/* Stat 3: Total Observations */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-2">
              <div className="text-[10px] text-atlas-text-muted font-sans">Sample Size (N)</div>
              <div className="text-base font-bold text-atlas-text-primary">
                {kupiec.total_observations}
              </div>
              <div className="text-[9px] text-atlas-text-muted">
                {kupiec.is_adequate_sample ? "Sample Adequate (>=30)" : "Small Sample (<30)"}
              </div>
            </div>

            {/* Stat 4: Exception Count */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-2">
              <div className="text-[10px] text-atlas-text-muted font-sans">Observed Exceptions (x)</div>
              <div className="text-base font-bold text-amber-300">
                {kupiec.exception_count}
              </div>
              <div className="text-[9px] text-atlas-text-muted">trading days breached</div>
            </div>

            {/* Stat 5: Expected Exceptions */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-2">
              <div className="text-[10px] text-atlas-text-muted font-sans">Expected Failures (p₀·N)</div>
              <div className="text-base font-bold text-atlas-text-primary">
                {kupiec.expected_exceptions.toFixed(1)}
              </div>
              <div className="text-[9px] text-atlas-text-muted">
                at {((1 - kupiec.confidence_level) * 100).toFixed(1)}% alpha
              </div>
            </div>

            {/* Stat 6: Failure Rate */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-2">
              <div className="text-[10px] text-atlas-text-muted font-sans">Empirical Rate (p̂)</div>
              <div className="text-base font-bold text-atlas-text-primary">
                {(kupiec.empirical_failure_rate * 100).toFixed(2)}%
              </div>
              <div className="text-[9px] text-atlas-text-muted">
                Target: {((1 - kupiec.confidence_level) * 100).toFixed(2)}%
              </div>
            </div>
          </div>

          {/* Warning notice if sample is small */}
          {kupiec.warning && (
            <div className="flex items-center gap-2 rounded border border-amber-500/30 bg-amber-500/10 p-2 text-xs text-amber-300">
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
              <span>{kupiec.warning}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-8 text-center text-xs text-atlas-text-muted">
          <ShieldCheck className="h-8 w-8 mx-auto text-atlas-text-muted opacity-40 mb-2" />
          <p className="font-medium text-atlas-text-secondary">No Backtest Executed</p>
          <p className="mt-1">
            Click &quot;Run VaR Backtest&quot; above to evaluate historical rolling VaR forecasts against realized losses and perform the Kupiec POF Likelihood Ratio test.
          </p>
        </div>
      )}

      {/* 3. Rolling VaR Forecast vs Realized Loss Chart */}
      {observations.length > 0 && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-3">
          <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-2">
            <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
              Rolling Point-in-Time VaR Forecast vs. Realized Loss Trajectory
            </h3>
            <div className="flex items-center gap-3 text-[11px] text-atlas-text-muted">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-amber-400" /> Forecast VaR Threshold
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-blue-400" /> Realized Loss
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-rose-500" /> VaR Breach Exception
              </span>
            </div>
          </div>

          <div className="relative w-full overflow-x-auto">
            <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-44 select-none">
              {/* Grid Lines */}
              <line
                x1={paddingLeft}
                y1={paddingTop + innerHeight}
                x2={chartWidth - paddingRight}
                y2={paddingTop + innerHeight}
                stroke="#475569"
                strokeWidth="1"
              />
              <line
                x1={paddingLeft}
                y1={paddingTop + innerHeight / 2}
                x2={chartWidth - paddingRight}
                y2={paddingTop + innerHeight / 2}
                stroke="#334155"
                strokeDasharray="2,2"
                strokeWidth="0.5"
              />

              {/* Y Axis Labels */}
              <text
                x={paddingLeft - 6}
                y={paddingTop + 4}
                fill="#64748b"
                fontSize="9"
                textAnchor="end"
                fontFamily="monospace"
              >
                {formatVaRReturn(maxVal)}
              </text>
              <text
                x={paddingLeft - 6}
                y={paddingTop + innerHeight}
                fill="#64748b"
                fontSize="9"
                textAnchor="end"
                fontFamily="monospace"
              >
                0.0%
              </text>

              {/* Realized Loss Line */}
              <polyline
                fill="none"
                stroke="#60a5fa"
                strokeWidth="1"
                points={observations
                  .map((obs, idx) => {
                    const x = paddingLeft + (idx / (observations.length - 1 || 1)) * innerWidth;
                    const y = paddingTop + innerHeight - (Math.max(0, obs.realized_loss) / maxVal) * innerHeight;
                    return `${x},${y}`;
                  })
                  .join(" ")}
              />

              {/* VaR Forecast Line */}
              <polyline
                fill="none"
                stroke="#f59e0b"
                strokeWidth="1.5"
                strokeDasharray="3,2"
                points={observations
                  .map((obs, idx) => {
                    const x = paddingLeft + (idx / (observations.length - 1 || 1)) * innerWidth;
                    const y = paddingTop + innerHeight - (Math.max(0, obs.forecast_var) / maxVal) * innerHeight;
                    return `${x},${y}`;
                  })
                  .join(" ")}
              />

              {/* Exception Breach Dots */}
              {observations.map((obs, idx) => {
                if (!obs.is_exception) return null;
                const x = paddingLeft + (idx / (observations.length - 1 || 1)) * innerWidth;
                const y = paddingTop + innerHeight - (Math.max(0, obs.realized_loss) / maxVal) * innerHeight;
                return (
                  <circle
                    key={idx}
                    cx={x}
                    cy={y}
                    r="3.5"
                    fill="#e11d48"
                    stroke="#ffffff"
                    strokeWidth="1"
                  />
                );
              })}

              {/* Dates along X axis */}
              <text
                x={paddingLeft}
                y={paddingTop + innerHeight + 15}
                fill="#64748b"
                fontSize="9"
                fontFamily="monospace"
              >
                {observations[0]?.observation_date?.substring(0, 10)}
              </text>
              <text
                x={chartWidth - paddingRight}
                y={paddingTop + innerHeight + 15}
                fill="#64748b"
                fontSize="9"
                textAnchor="end"
                fontFamily="monospace"
              >
                {observations[observations.length - 1]?.observation_date?.substring(0, 10)}
              </text>
            </svg>
          </div>
        </div>
      )}

      {/* 4. Historical Exceptions Table */}
      {exceptions.length > 0 && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-2">
          <div className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
            <AlertCircle className="h-3.5 w-3.5" />
            <span>Recorded VaR Exception Observations ({exceptions.length} Breaches)</span>
          </div>

          <div className="overflow-x-auto max-h-48 overflow-y-auto">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2 text-[10px] text-atlas-text-secondary uppercase">
                  <th className="py-1.5 px-3">Breach Date</th>
                  <th className="py-1.5 px-3 text-right">Forecast VaR</th>
                  <th className="py-1.5 px-3 text-right">Realized Loss</th>
                  <th className="py-1.5 px-3 text-right">Exceedance Margin</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/40 text-[11px]">
                {exceptions.map((ex, idx) => (
                  <tr key={idx} className="hover:bg-atlas-surface-2/60 transition">
                    <td className="py-1.5 px-3 text-atlas-text-primary">
                      {ex.observation_date?.substring(0, 10)}
                    </td>
                    <td className="py-1.5 px-3 text-right text-amber-400">
                      {formatVaRReturn(ex.forecast_var)}
                    </td>
                    <td className="py-1.5 px-3 text-right font-bold text-rose-400">
                      {formatVaRReturn(ex.realized_loss)}
                    </td>
                    <td className="py-1.5 px-3 text-right font-bold text-red-500">
                      +{formatVaRReturn(ex.exceedance_amount)}
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

