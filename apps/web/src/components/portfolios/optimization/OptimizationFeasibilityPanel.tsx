"use client";

import React from "react";
import {
  CandidatePortfolioDTO,
  SolverDiagnosticsDTO,
} from "@/lib/portfolios/optimization/types";
import { getFeasibilityBadge } from "@/lib/portfolios/optimization/formatting";
import { AlertCircle, CheckCircle, Info, ShieldCheck } from "lucide-react";

interface OptimizationFeasibilityPanelProps {
  candidate: CandidatePortfolioDTO;
  diagnostics?: SolverDiagnosticsDTO;
}

export function OptimizationFeasibilityPanel({
  candidate,
  diagnostics,
}: OptimizationFeasibilityPanelProps) {
  const badge = getFeasibilityBadge(candidate.feasibility_status);
  const slacks = Object.entries(candidate.constraint_slacks || {});
  const activeConstraints = diagnostics?.active_constraints || [];

  return (
    <div className="space-y-4">
      {/* Feasibility Overview Card */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-atlas-surface-2">
              <ShieldCheck className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-atlas-text-primary">
                  Mathematical Feasibility & Slack Verification
                </h3>
                <span
                  className={`rounded border px-2 py-0.5 text-xs font-semibold ${badge.className}`}
                >
                  {badge.label}
                </span>
              </div>
              <p className="mt-0.5 text-xs text-atlas-text-muted">
                Kuhn-Tucker (KKT) stationarity and boundary slack evaluation.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div>
              <span className="text-atlas-text-muted">Max Violation:</span>{" "}
              <span className="font-mono font-semibold text-atlas-text-primary">
                {diagnostics
                  ? Number(diagnostics.max_constraint_violation).toExponential(3)
                  : "0.00e+0"}
              </span>
            </div>
            <div>
              <span className="text-atlas-text-muted">Active / Binding:</span>{" "}
              <span className="font-mono font-semibold text-cyan-300">
                {activeConstraints.length}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Binding Constraints Summary */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Active Constraints */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
            Binding Constraints ({activeConstraints.length})
          </h4>
          <p className="mb-3 text-[11px] text-atlas-text-muted">
            Constraints operating on their boundary (slack ≈ 0), exerting positive shadow prices / dual multipliers on the objective.
          </p>

          {activeConstraints.length === 0 ? (
            <div className="rounded bg-atlas-surface-2/40 p-3 text-xs text-atlas-text-muted">
              No constraints are currently binding at boundary limits.
            </div>
          ) : (
            <div className="space-y-1.5">
              {activeConstraints.map((c, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between rounded bg-atlas-surface-2/50 px-3 py-2 text-xs"
                >
                  <span className="font-mono font-medium text-amber-300">{c}</span>
                  <span className="rounded bg-amber-500/10 px-2 py-0.5 text-[10px] font-semibold text-amber-400">
                    BINDING
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Slacks Table */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
            Constraint Slacks
          </h4>
          <p className="mb-3 text-[11px] text-atlas-text-muted">
            Distance between candidate weights and constraint limits (g_j(w) &le; 0).
          </p>

          {slacks.length === 0 ? (
            <div className="rounded bg-atlas-surface-2/40 p-3 text-xs text-atlas-text-muted">
              No custom constraint slacks recorded.
            </div>
          ) : (
            <div className="max-h-56 overflow-y-auto space-y-1 pr-1">
              {slacks.map(([key, val]) => {
                const numVal = parseFloat(val);
                const isBinding = Math.abs(numVal) < 1e-4;

                return (
                  <div
                    key={key}
                    className="flex items-center justify-between rounded bg-atlas-surface-2/30 px-3 py-1.5 text-xs font-mono"
                  >
                    <span className="text-atlas-text-secondary">{key}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-atlas-text-primary">
                        {numVal.toFixed(6)}
                      </span>
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                          isBinding
                            ? "bg-amber-500/10 text-amber-300"
                            : "bg-emerald-500/10 text-emerald-300"
                        }`}
                      >
                        {isBinding ? "LIMIT" : "OK"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
