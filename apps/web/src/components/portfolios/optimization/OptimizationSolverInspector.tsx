"use client";

import React, { useState } from "react";
import {
  CovarianceEstimateDTO,
  ExpectedReturnEstimateDTO,
  SolverDiagnosticsDTO,
} from "@/lib/portfolios/optimization/types";
import { getSolverStatusBadge } from "@/lib/portfolios/optimization/formatting";
import {
  Activity,
  AlertCircle,
  Binary,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  Hash,
  ShieldCheck,
} from "lucide-react";

interface OptimizationSolverInspectorProps {
  diagnostics: SolverDiagnosticsDTO;
  covariance?: CovarianceEstimateDTO;
  expectedReturns?: ExpectedReturnEstimateDTO;
  inputHash?: string;
}

export function OptimizationSolverInspector({
  diagnostics,
  covariance,
  expectedReturns,
  inputHash,
}: OptimizationSolverInspectorProps) {
  const [showMatrix, setShowMatrix] = useState<boolean>(false);
  const statusBadge = getSolverStatusBadge(diagnostics.status);

  return (
    <div className="space-y-4">
      {/* Top Banner / Diagnostics Summary */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-atlas-surface-2">
              <Cpu className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-atlas-text-primary">
                  Convex Optimization Solver Diagnostics
                </h3>
                <span
                  className={`rounded border px-2 py-0.5 text-xs font-semibold ${statusBadge.className}`}
                >
                  {statusBadge.label}
                </span>
              </div>
              <p className="mt-0.5 text-xs text-atlas-text-muted">
                Engine: {diagnostics.solver_name} • Problem Type: {diagnostics.problem_type}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
            <div className="flex items-center gap-1.5 text-atlas-text-secondary">
              <Clock className="h-3.5 w-3.5 text-atlas-accent" />
              <span>{diagnostics.solve_time_ms.toFixed(2)} ms</span>
            </div>
            <div className="flex items-center gap-1.5 text-atlas-text-secondary">
              <Activity className="h-3.5 w-3.5 text-emerald-400" />
              <span>{diagnostics.iterations} iters</span>
            </div>
            <div className="flex items-center gap-1.5 text-atlas-text-secondary">
              <Binary className="h-3.5 w-3.5 text-cyan-400" />
              <span>
                f(w*) ={" "}
                {diagnostics.objective_value !== undefined && diagnostics.objective_value !== null
                  ? Number(diagnostics.objective_value).toFixed(6)
                  : "N/A"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Warnings Banner if any */}
      {diagnostics.warnings && diagnostics.warnings.length > 0 && (
        <div className="flex items-start gap-2.5 rounded border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-300">
          <AlertCircle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
          <div>
            <span className="font-semibold">Solver Advisory:</span>
            <ul className="mt-1 list-disc pl-4 space-y-0.5">
              {diagnostics.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Numerical Details Grid */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Solver Execution Metrics */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
            KKT Stationarity & Violation
          </h4>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between border-b border-atlas-border-default/40 pb-1.5">
              <span className="text-atlas-text-muted">Maximum Constraint Violation</span>
              <span className="font-mono font-bold text-atlas-text-primary">
                {Number(diagnostics.max_constraint_violation).toExponential(4)}
              </span>
            </div>

            <div className="flex justify-between border-b border-atlas-border-default/40 pb-1.5">
              <span className="text-atlas-text-muted">Active Binding Constraints</span>
              <span className="font-mono font-bold text-cyan-300">
                {diagnostics.active_constraints.length}
              </span>
            </div>

            <div className="flex justify-between border-b border-atlas-border-default/40 pb-1.5">
              <span className="text-atlas-text-muted">Solver Convergence Status</span>
              <span className="font-mono font-semibold text-emerald-400">
                {diagnostics.status}
              </span>
            </div>

            <div className="flex justify-between pb-1.5">
              <span className="text-atlas-text-muted">Input Reproducibility Hash</span>
              <span className="font-mono text-[11px] text-atlas-text-secondary truncate max-w-[220px]" title={inputHash}>
                {inputHash || "N/A"}
              </span>
            </div>
          </div>
        </div>

        {/* Covariance Matrix Health */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
              Covariance Matrix Health
            </h4>
            {covariance && (
              <button
                onClick={() => setShowMatrix(!showMatrix)}
                className="text-[11px] text-cyan-400 hover:underline"
              >
                {showMatrix ? "Hide Matrix" : "View Heatmap"}
              </button>
            )}
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between border-b border-atlas-border-default/40 pb-1.5">
              <span className="text-atlas-text-muted">Estimation Model</span>
              <span className="font-mono font-semibold text-atlas-text-primary">
                {covariance?.model || "LEDOIT_WOLF_SHRINKAGE"}
              </span>
            </div>

            <div className="flex justify-between border-b border-atlas-border-default/40 pb-1.5">
              <span className="text-atlas-text-muted">Positive Semi-Definite (PSD)</span>
              <div className="flex items-center gap-1 font-mono font-bold text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                <span>{covariance?.is_psd ? "VERIFIED (λ_min ≥ 0)" : "NO"}</span>
              </div>
            </div>

            <div className="flex justify-between border-b border-atlas-border-default/40 pb-1.5">
              <span className="text-atlas-text-muted">Condition Number (κ)</span>
              <span className="font-mono font-bold text-atlas-text-primary">
                {covariance?.condition_number ? covariance.condition_number.toFixed(2) : "1.00"}
              </span>
            </div>

            <div className="flex justify-between pb-1.5">
              <span className="text-atlas-text-muted">Regularization / Jitter Applied</span>
              <span className="font-mono text-atlas-text-secondary">
                {covariance?.regularization_applied ? "YES (Diagonal loading)" : "NO"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Covariance Matrix Table / Heatmap if toggled */}
      {showMatrix && covariance && covariance.matrix && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4 overflow-x-auto">
          <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
            Covariance Matrix (Annualized)
          </h4>
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="border-b border-atlas-border-default/60 text-atlas-text-muted">
                <th className="py-1 px-2 text-left">Asset</th>
                {covariance.symbols.map((sym) => (
                  <th key={sym} className="py-1 px-2 text-right">
                    {sym}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40">
              {covariance.symbols.map((rowSym, rIdx) => (
                <tr key={rowSym} className="hover:bg-atlas-surface-2/40">
                  <td className="py-1 px-2 font-bold text-atlas-text-primary">{rowSym}</td>
                  {covariance.symbols.map((_, cIdx) => {
                    const val = covariance.matrix[rIdx]?.[cIdx] ?? 0;
                    return (
                      <td
                        key={cIdx}
                        className={`py-1 px-2 text-right ${
                          rIdx === cIdx ? "text-cyan-300 font-semibold" : "text-atlas-text-secondary"
                        }`}
                      >
                        {val.toFixed(5)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
