"use client";

import React from "react";
import { VaRModelType } from "@/lib/risk/types";
import { Layers, ShieldCheck, Zap } from "lucide-react";

interface TailModelComparisonTableProps {
  activeModel: VaRModelType;
  onSelectModel: (model: VaRModelType) => void;
}

export function TailModelComparisonTable({
  activeModel,
  onSelectModel,
}: TailModelComparisonTableProps) {
  const models = [
    {
      id: "HISTORICAL_SIMULATION" as VaRModelType,
      name: "Historical Simulation",
      subtitle: "Non-Parametric Empirical Quantile",
      assumptions: "Past returns reflect future distribution; no parametric distributional assumption.",
      esMethod: "Fractional Tail Integration",
      tailFatnessHandling: "Captures historical fat tails, skewness, and non-linear dependencies directly.",
      limitations: "Sensitive to sample window; cannot predict shocks beyond historical sample extremes.",
      complexity: "O(N log N) sorting; instantaneous execution.",
    },
    {
      id: "PARAMETRIC_NORMAL" as VaRModelType,
      name: "Parametric Delta-Normal",
      subtitle: "Gaussian Variance-Covariance Analytical",
      assumptions: "Multivariate normal returns; linear portfolio payoff w'r.",
      esMethod: "Closed-Form Gaussian Integration: -μ + σ [φ(z) / (1-α)]",
      tailFatnessHandling: "Underestimates fat tails (kurtosis = 3.0 assumption); asymptotic ratio 1.25x at 95%.",
      limitations: "Underestimates tail loss probability during severe market stress (black swans).",
      complexity: "O(K² + K) matrix product; analytical closed-form.",
    },
    {
      id: "MONTE_CARLO_GAUSSIAN" as VaRModelType,
      name: "Monte Carlo Simulation",
      subtitle: "Correlated Gaussian Factor Paths",
      assumptions: "Simulated joint paths from regularized PSD covariance Σ = A Aᵀ.",
      esMethod: "Sample Average of Tail Quantile Losses",
      tailFatnessHandling: "Flexible factor framework; reproducible via deterministic PRNG seed.",
      limitations: "Sampling error varies as 1/√M; computationally heavier than parametric.",
      complexity: "O(K³ + M·K) Cholesky + simulation.",
    },
  ];

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-3">
      <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-2">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-atlas-accent-blue" />
          <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
            Institutional VaR & ES Model Framework Comparison
          </h3>
        </div>
        <div className="text-[11px] text-atlas-text-muted">
          Active: <span className="font-semibold text-atlas-accent-blue">{activeModel}</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2 text-[11px] font-semibold text-atlas-text-secondary uppercase">
              <th className="py-2 px-3">Risk Model</th>
              <th className="py-2 px-3">Distribution Assumptions</th>
              <th className="py-2 px-3">ES Formulation</th>
              <th className="py-2 px-3">Tail Fatness Handling</th>
              <th className="py-2 px-3">Known Caveats</th>
              <th className="py-2 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/40">
            {models.map((m) => {
              const isActive = activeModel === m.id;
              return (
                <tr
                  key={m.id}
                  className={`hover:bg-atlas-surface-2/60 transition ${
                    isActive ? "bg-atlas-accent-blue/5" : ""
                  }`}
                >
                  <td className="py-2.5 px-3">
                    <div className="font-bold text-atlas-text-primary flex items-center gap-1.5">
                      {m.name}
                      {isActive && (
                        <span className="rounded bg-atlas-accent-blue/20 text-atlas-accent-blue border border-atlas-accent-blue/40 px-1 py-0.2 text-[9px] uppercase font-bold">
                          Active
                        </span>
                      )}
                    </div>
                    <div className="text-[10px] text-atlas-text-muted mt-0.5">{m.subtitle}</div>
                  </td>
                  <td className="py-2.5 px-3 text-atlas-text-secondary max-w-[200px] leading-relaxed">
                    {m.assumptions}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-[11px] text-atlas-text-secondary max-w-[200px]">
                    {m.esMethod}
                  </td>
                  <td className="py-2.5 px-3 text-atlas-text-secondary max-w-[220px] leading-relaxed">
                    {m.tailFatnessHandling}
                  </td>
                  <td className="py-2.5 px-3 text-rose-300/80 max-w-[200px] leading-relaxed text-[11px]">
                    {m.limitations}
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={() => onSelectModel(m.id)}
                      disabled={isActive}
                      className={`rounded px-2.5 py-1 text-xs font-medium transition ${
                        isActive
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 cursor-default"
                          : "bg-atlas-surface-2 text-atlas-text-secondary hover:bg-atlas-accent-blue hover:text-white"
                      }`}
                    >
                      {isActive ? "Selected" : "Select"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

