"use client";

import React from "react";
import {
  TailRiskCalculationRunDTO,
  VaRModelType,
} from "@/lib/risk/types";
import {
  formatCurrency,
  formatVaRReturn,
  getVaRModelLabel,
} from "@/lib/risk/formatting";
import {
  AlertTriangle,
  ArrowDownRight,
  Flame,
  Layers,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

interface TailRiskSummaryCardsProps {
  run: TailRiskCalculationRunDTO | null;
  selectedModel: VaRModelType;
  selectedConfidence: number;
  selectedHorizon: number;
  calculating: boolean;
  onSelectModel: (model: VaRModelType) => void;
  onSelectConfidence: (conf: number) => void;
  onSelectHorizon: (horizon: number) => void;
  onRecalculate: () => void;
}

export function TailRiskSummaryCards({
  run,
  selectedModel,
  selectedConfidence,
  selectedHorizon,
  calculating,
  onSelectModel,
  onSelectConfidence,
  onSelectHorizon,
  onRecalculate,
}: TailRiskSummaryCardsProps) {
  const varFraction = run?.var_result?.var_fraction ?? run?.var_result?.var_return ?? null;
  const varMonetary = run?.var_result?.var_monetary ?? run?.var_result?.var_amount ?? null;

  const esFraction = run?.expected_shortfall?.es_fraction ?? run?.expected_shortfall?.es_return ?? null;
  const esMonetary = run?.expected_shortfall?.es_monetary ?? run?.expected_shortfall?.es_amount ?? null;

  // Tail leptokurtosis ratio (ES / VaR)
  const esToVarRatio =
    varFraction && esFraction && varFraction > 0
      ? (esFraction / varFraction).toFixed(2)
      : null;

  const tailSample = run?.expected_shortfall?.tail_loss_observations ?? run?.var_result?.effective_tail_sample_size ?? 0;
  const totalSample = run?.var_result?.total_sample_size ?? 0;

  return (
    <div className="space-y-3">
      {/* 1. Model & Param Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-2.5">
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
                { id: "MONTE_CARLO_GAUSSIAN", label: "Monte Carlo" },
              ] as const
            ).map((m) => (
              <button
                key={m.id}
                onClick={() => onSelectModel(m.id)}
                className={`rounded px-2.5 py-1 text-xs font-medium transition ${
                  selectedModel === m.id
                    ? "bg-atlas-accent-blue text-white shadow-sm"
                    : "bg-atlas-surface-2 text-atlas-text-secondary hover:bg-atlas-surface-3 hover:text-atlas-text-primary"
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
            {[0.95, 0.975, 0.99].map((c) => (
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

          {/* Horizon Selector */}
          <div className="flex items-center gap-1">
            <span className="text-[11px] font-medium text-atlas-text-secondary uppercase tracking-wider mr-1">
              Horizon:
            </span>
            {[1, 5, 10, 20].map((h) => (
              <button
                key={h}
                onClick={() => onSelectHorizon(h)}
                className={`rounded px-2 py-1 text-xs font-mono font-medium transition ${
                  selectedHorizon === h
                    ? "bg-purple-500/20 text-purple-300 border border-purple-500/40"
                    : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                {h}D
              </button>
            ))}
          </div>
        </div>

        {/* Recalculate Trigger Button */}
        <button
          onClick={onRecalculate}
          disabled={calculating}
          className="flex items-center gap-1.5 rounded bg-atlas-accent-blue/15 px-3 py-1.5 text-xs font-medium text-atlas-accent-blue hover:bg-atlas-accent-blue/25 disabled:opacity-50 transition border border-atlas-accent-blue/30"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${calculating ? "animate-spin" : ""}`} />
          <span>{calculating ? "Computing Tail..." : "Recalculate"}</span>
        </button>
      </div>

      {/* 2. Four High-Density KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Card 1: Value at Risk (VaR) */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-semibold uppercase tracking-wider text-[11px] flex items-center gap-1 text-rose-400">
              <ShieldAlert className="h-3.5 w-3.5" />
              Value at Risk (VaR)
            </span>
            <span className="font-mono text-[10px] text-atlas-text-muted">
              {((run?.confidence_level ?? selectedConfidence) * 100).toFixed(1)}% / {run?.horizon_days ?? selectedHorizon}D
            </span>
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-rose-400">
              {varMonetary !== null ? formatCurrency(varMonetary) : "—"}
            </div>
            <div className="text-xs font-mono text-atlas-text-secondary mt-0.5 flex items-center gap-1">
              <ArrowDownRight className="h-3 w-3 text-rose-400" />
              <span>{varFraction !== null ? formatVaRReturn(varFraction) : "—"}</span>
              <span className="text-[10px] text-atlas-text-muted ml-1">portfolio value</span>
            </div>
          </div>
          <div className="mt-3 border-t border-atlas-border-default/40 pt-1.5 text-[10px] text-atlas-text-muted flex justify-between">
            <span>Model:</span>
            <span className="font-medium text-atlas-text-secondary truncate max-w-[140px]">
              {run?.model_type ? getVaRModelLabel(run.model_type) : getVaRModelLabel(selectedModel)}
            </span>
          </div>
        </div>

        {/* Card 2: Expected Shortfall (CVaR) */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-semibold uppercase tracking-wider text-[11px] flex items-center gap-1 text-red-500">
              <Flame className="h-3.5 w-3.5" />
              Expected Shortfall (ES)
            </span>
            <span className="font-mono text-[10px] text-atlas-text-muted">
              Tail Average
            </span>
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-red-500">
              {esMonetary !== null ? formatCurrency(esMonetary) : "—"}
            </div>
            <div className="text-xs font-mono text-atlas-text-secondary mt-0.5 flex items-center gap-1">
              <ArrowDownRight className="h-3 w-3 text-red-500" />
              <span>{esFraction !== null ? formatVaRReturn(esFraction) : "—"}</span>
              <span className="text-[10px] text-atlas-text-muted ml-1">beyond VaR</span>
            </div>
          </div>
          <div className="mt-3 border-t border-atlas-border-default/40 pt-1.5 text-[10px] text-atlas-text-muted flex justify-between">
            <span>Method:</span>
            <span className="font-medium text-atlas-text-secondary truncate max-w-[140px]">
              {run?.expected_shortfall?.method ?? "Tail Integration"}
            </span>
          </div>
        </div>

        {/* Card 3: Leptokurtosis Multiplier (ES / VaR) */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-semibold uppercase tracking-wider text-[11px] flex items-center gap-1 text-amber-400">
              <Layers className="h-3.5 w-3.5" />
              Tail Fatness (ES / VaR)
            </span>
            <span className="font-mono text-[10px] text-atlas-text-muted">
              Kurtosis Ratio
            </span>
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-amber-400">
              {esToVarRatio ? `${esToVarRatio}x` : "—"}
            </div>
            <div className="text-xs text-atlas-text-secondary mt-0.5">
              {esToVarRatio && parseFloat(esToVarRatio) > 1.3 ? (
                <span className="text-rose-400 font-medium">Heavy tail loss profile</span>
              ) : (
                <span className="text-emerald-400 font-medium">Standard tail decay</span>
              )}
            </div>
          </div>
          <div className="mt-3 border-t border-atlas-border-default/40 pt-1.5 text-[10px] text-atlas-text-muted flex justify-between">
            <span>Gaussian Benchmark:</span>
            <span className="font-mono text-atlas-text-secondary">~1.25x</span>
          </div>
        </div>

        {/* Card 4: Tail Observations & Sample Size */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-atlas-text-secondary">
            <span className="font-semibold uppercase tracking-wider text-[11px] flex items-center gap-1 text-sky-400">
              Sample Coverage
            </span>
            <span className="font-mono text-[10px] text-atlas-text-muted">
              History
            </span>
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-atlas-text-primary">
              {tailSample} <span className="text-xs font-normal text-atlas-text-muted">tail pts</span>
            </div>
            <div className="text-xs font-mono text-atlas-text-secondary mt-0.5">
              out of {totalSample} trading days
            </div>
          </div>
          <div className="mt-3 border-t border-atlas-border-default/40 pt-1.5 text-[10px] text-atlas-text-muted flex justify-between">
            <span>Sample Ratio:</span>
            <span className="font-mono text-atlas-text-secondary">
              {totalSample > 0 ? `${((tailSample / totalSample) * 100).toFixed(1)}%` : "—"}
            </span>
          </div>
        </div>
      </div>

      {/* Warning banner if applicable */}
      {run?.var_result?.warning && (
        <div className="flex items-center gap-2 rounded border border-amber-500/30 bg-amber-500/10 p-2 text-xs text-amber-300">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
          <span>{run.var_result.warning}</span>
        </div>
      )}
    </div>
  );
}

