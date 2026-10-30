"use client";

import React, { useState } from "react";
import { formatRatio } from "@/lib/risk/formatting";
import { CovarianceDiagnosticsDTO } from "@/lib/risk/types";
import {
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Grid,
  Info,
  Layers,
  Sparkles,
} from "lucide-react";

interface CovarianceDiagnosticsPanelProps {
  diagnostics: CovarianceDiagnosticsDTO | null;
}

export function CovarianceDiagnosticsPanel({
  diagnostics,
}: CovarianceDiagnosticsPanelProps) {
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number; val: number } | null>(null);

  if (!diagnostics) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center text-xs text-atlas-text-muted">
        No covariance diagnostics available. Run the Covariance Parametric risk model to inspect matrix properties.
      </div>
    );
  }

  const d = diagnostics;
  const matrix = d.correlation_matrix || [];
  const symbols = d.symbols || [];

  const getHeatmapColor = (val: number) => {
    // val from -1.0 to 1.0
    if (val >= 0.8) return "bg-rose-500/80 text-white";
    if (val >= 0.5) return "bg-rose-500/40 text-rose-200";
    if (val >= 0.2) return "bg-amber-500/30 text-amber-200";
    if (val >= -0.2) return "bg-zinc-800 text-zinc-300";
    if (val >= -0.5) return "bg-cyan-500/30 text-cyan-200";
    return "bg-blue-600/60 text-white";
  };

  return (
    <div className="space-y-4">
      {/* Top Cards Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-5">
        {/* 1. PSD Check */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              PSD Status
            </span>
            <CheckCircle2
              className={`h-3.5 w-3.5 ${d.is_psd ? "text-emerald-400" : "text-rose-400"}`}
            />
          </div>
          <div
            className={`mt-1 text-base font-bold ${
              d.is_psd ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {d.is_psd ? "Positive Semi-Definite" : "Non-PSD (Degenerate)"}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            λ_min: {d.min_eigenvalue.toExponential(3)}
          </div>
        </div>

        {/* 2. Condition Number */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Condition Number
            </span>
            <Cpu className="h-3.5 w-3.5 text-atlas-text-secondary" />
          </div>
          <div className="mt-1 text-base font-bold text-atlas-text-primary">
            {formatRatio(d.condition_number, 1)}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            {d.condition_number < 100
              ? "Well-Conditioned"
              : d.condition_number < 1000
              ? "Moderate Collinearity"
              : "Ill-Conditioned"}
          </div>
        </div>

        {/* 3. Diversification Ratio */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Diversification Ratio
            </span>
            <Sparkles className="h-3.5 w-3.5 text-atlas-accent-gold" />
          </div>
          <div className="mt-1 text-base font-bold text-atlas-accent-gold">
            {formatRatio(d.diversification_ratio, 2)}x
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            Σ(w_i σ_i) / σ_P ≥ 1.0
          </div>
        </div>

        {/* 4. Matrix Dimensions */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Dimensions
            </span>
            <Layers className="h-3.5 w-3.5 text-blue-400" />
          </div>
          <div className="mt-1 text-base font-bold text-atlas-text-primary">
            {d.dimensions} × {d.dimensions}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            {symbols.length} Assets / Cash
          </div>
        </div>

        {/* 5. Regularization */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-secondary">
              Shrinkage / Ridge
            </span>
            <Grid className="h-3.5 w-3.5 text-purple-400" />
          </div>
          <div className="mt-1 text-base font-bold text-atlas-text-primary">
            {d.regularization_applied ? "Shrinkage Applied" : "Sample Covariance"}
          </div>
          <div className="mt-1 text-[10px] text-atlas-text-muted">
            Ledoit-Wolf / Diagonal
          </div>
        </div>
      </div>

      {/* Correlation Heatmap */}
      {matrix.length > 0 && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-3">
            <div>
              <h4 className="text-sm font-semibold text-atlas-text-primary">
                Correlation Matrix Heatmap
              </h4>
              <p className="mt-0.5 text-xs text-atlas-text-muted">
                Pairwise Pearson correlation coefficients between portfolio constituents.
              </p>
            </div>

            {hoveredCell && (
              <div className="flex items-center gap-2 rounded bg-atlas-surface-2 px-2.5 py-1 text-xs">
                <span className="font-semibold text-atlas-text-primary">
                  {symbols[hoveredCell.row]} ↔ {symbols[hoveredCell.col]}:
                </span>
                <span className="font-mono font-bold text-atlas-accent-gold">
                  {hoveredCell.val.toFixed(3)}
                </span>
              </div>
            )}
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="border-collapse font-mono text-[11px]">
              <thead>
                <tr>
                  <th className="p-1 text-left text-atlas-text-muted"></th>
                  {symbols.map((sym) => (
                    <th key={sym} className="p-1.5 text-center font-medium text-atlas-text-secondary">
                      {sym}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.map((row, rIdx) => (
                  <tr key={symbols[rIdx] || rIdx}>
                    <td className="p-1.5 font-medium text-atlas-text-secondary">
                      {symbols[rIdx]}
                    </td>
                    {row.map((val, cIdx) => (
                      <td
                        key={cIdx}
                        className={`h-8 w-14 cursor-pointer p-1 text-center font-semibold transition ${getHeatmapColor(
                          val
                        )}`}
                        onMouseEnter={() =>
                          setHoveredCell({ row: rIdx, col: cIdx, val })
                        }
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        {val.toFixed(2)}
                      </td>
                    ))}
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

