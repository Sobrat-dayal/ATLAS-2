"use client";

import React, { useState } from "react";
import { Grid, TrendingUp, HelpCircle } from "lucide-react";
import { ScenarioMatrixResult, ScenarioOutcome } from "@/lib/options/quant/types";

interface StrategyScenarioMatrixProps {
  matrixResult?: ScenarioMatrixResult | null;
  isLoading?: boolean;
}

export function StrategyScenarioMatrix({ matrixResult, isLoading = false }: StrategyScenarioMatrixProps) {
  const [displayMode, setDisplayMode] = useState<"PNL_DOLLAR" | "PNL_PERCENT" | "DELTA">("PNL_DOLLAR");

  if (isLoading) {
    return (
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-6 text-center text-xs text-zinc-400 font-mono">
        Computing 2D Spot × Volatility Mark-to-Market matrix across scenario nodes...
      </div>
    );
  }

  if (!matrixResult || !matrixResult.matrix_grid || matrixResult.matrix_grid.length === 0) {
    return (
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-6 text-center text-xs text-zinc-500 font-mono">
        Run scenario matrix analysis to evaluate multi-factor spot and volatility stress shocks.
      </div>
    );
  }

  const { spot_shifts_pct, vol_shifts_pct, matrix_grid, base_spot, base_vol } = matrixResult;

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800 pb-2.5">
        <div className="flex items-center gap-2">
          <Grid className="w-4 h-4 text-indigo-400" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">
            2D Spot × Volatility Stress Matrix
          </h4>
          <span className="text-[10px] text-zinc-500 font-mono">
            Base Spot: ${base_spot.toFixed(2)} | Base Vol: {(base_vol * 100).toFixed(1)}%
          </span>
        </div>

        {/* Display Mode Toggles */}
        <div className="flex items-center gap-1 bg-zinc-950/80 p-0.5 rounded border border-zinc-800 text-[11px] font-mono">
          <button
            onClick={() => setDisplayMode("PNL_DOLLAR")}
            className={`px-2 py-0.5 rounded transition-colors ${
              displayMode === "PNL_DOLLAR"
                ? "bg-indigo-600 text-white font-medium"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            P&L ($)
          </button>
          <button
            onClick={() => setDisplayMode("PNL_PERCENT")}
            className={`px-2 py-0.5 rounded transition-colors ${
              displayMode === "PNL_PERCENT"
                ? "bg-indigo-600 text-white font-medium"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            P&L (%)
          </button>
          <button
            onClick={() => setDisplayMode("DELTA")}
            className={`px-2 py-0.5 rounded transition-colors ${
              displayMode === "DELTA"
                ? "bg-indigo-600 text-white font-medium"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Delta (Δ)
          </button>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs font-mono border-collapse min-w-[500px]">
          <thead>
            <tr className="border-b border-zinc-800 text-[11px] text-zinc-500">
              <th className="p-2 text-left bg-zinc-950/40">IV Shift \ Spot Shift</th>
              {spot_shifts_pct.map((sShift, colIdx) => {
                const sPrice = base_spot * (1.0 + sShift);
                return (
                  <th key={colIdx} className="p-2 text-center bg-zinc-950/40">
                    <div>{sShift > 0 ? `+${(sShift * 100).toFixed(0)}%` : `${(sShift * 100).toFixed(0)}%`}</div>
                    <div className="text-[10px] text-zinc-400 font-normal">${sPrice.toFixed(2)}</div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {matrix_grid.map((row, rowIdx) => {
              const vShift = vol_shifts_pct[rowIdx];
              const effectiveVol = Math.max(0.01, base_vol + vShift);
              return (
                <tr key={rowIdx} className="border-b border-zinc-900/80">
                  <td className="p-2 font-medium bg-zinc-950/40 text-zinc-400 whitespace-nowrap">
                    <div>{vShift > 0 ? `+${(vShift * 100).toFixed(0)}% Vol` : `${(vShift * 100).toFixed(0)}% Vol`}</div>
                    <div className="text-[10px] text-zinc-500 font-normal">{(effectiveVol * 100).toFixed(1)}% IV</div>
                  </td>
                  {row.map((cell: ScenarioOutcome, colIdx: number) => {
                    const pnl = cell.pnl_dollar;
                    const isProfit = pnl > 0.01;
                    const isLoss = pnl < -0.01;
                    const isZeroShift =
                      Math.abs(spot_shifts_pct[colIdx]) < 1e-4 && Math.abs(vShift) < 1e-4;

                    return (
                      <td
                        key={colIdx}
                        className={`p-2.5 text-center transition-colors ${
                          isZeroShift
                            ? "bg-indigo-950/30 border border-indigo-700/50"
                            : isProfit
                            ? "bg-emerald-950/20 text-emerald-300 hover:bg-emerald-950/40"
                            : isLoss
                            ? "bg-rose-950/20 text-rose-300 hover:bg-rose-950/40"
                            : "bg-zinc-950/30 text-zinc-400"
                        }`}
                      >
                        {displayMode === "PNL_DOLLAR" && (
                          <div>
                            <div className={`font-bold ${isProfit ? "text-emerald-400" : isLoss ? "text-rose-400" : "text-zinc-300"}`}>
                              {pnl >= 0 ? `+$${pnl.toFixed(2)}` : `-$${Math.abs(pnl).toFixed(2)}`}
                            </div>
                            <div className="text-[9px] text-zinc-500 mt-0.5">
                              MtM: ${cell.mark_to_market_value.toFixed(2)}
                            </div>
                          </div>
                        )}

                        {displayMode === "PNL_PERCENT" && (
                          <div className={`font-bold ${isProfit ? "text-emerald-400" : isLoss ? "text-rose-400" : "text-zinc-300"}`}>
                            {cell.pnl_percentage >= 0
                              ? `+${cell.pnl_percentage.toFixed(1)}%`
                              : `${cell.pnl_percentage.toFixed(1)}%`}
                          </div>
                        )}

                        {displayMode === "DELTA" && (
                          <div>
                            <div className="font-bold text-zinc-200">
                              Δ {cell.aggregate_delta.toFixed(2)}
                            </div>
                            <div className="text-[9px] text-zinc-500 mt-0.5">
                              Γ {cell.aggregate_gamma.toFixed(3)}
                            </div>
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="text-[10px] text-zinc-500 font-mono flex items-center justify-between">
        <span>Highlighted outline indicates base market condition (0% Spot Shift, 0% Vol Shift)</span>
        <span>Revalued via QuantLib thread-safe context</span>
      </div>
    </div>
  );
}

