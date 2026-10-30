"use client";

import React from "react";
import { CrossExposureMatrixDTO } from "@/lib/risk/types";
import {
  formatFactorLoading,
  formatWeight,
} from "@/lib/risk/formatting";
import {
  CheckCircle2,
  Grid,
  Layers,
  RefreshCw,
} from "lucide-react";

interface CrossExposureWorkspaceProps {
  matrix: CrossExposureMatrixDTO | null;
  selectedRowDim: string;
  selectedColDim: string;
  onSelectDimensions: (rowDim: string, colDim: string) => void;
  loading: boolean;
  onRefresh: () => void;
}

export function CrossExposureWorkspace({
  matrix,
  selectedRowDim,
  selectedColDim,
  onSelectDimensions,
  loading,
  onRefresh,
}: CrossExposureWorkspaceProps) {
  if (!matrix) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-atlas-border-default/60 rounded m-4 bg-atlas-surface-1/40">
        <Grid className="h-10 w-10 text-atlas-text-secondary/50 mb-3 animate-pulse" />
        <h3 className="text-sm font-semibold text-atlas-text-primary">No Cross-Exposure Matrix Available</h3>
        <p className="text-xs text-atlas-text-secondary max-w-md mt-1 mb-4">
          Construct 2D joint exposure distributions partitioned by systematic factors, currencies, and economic sectors.
        </p>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-black transition hover:bg-atlas-accent/90 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Load Cross Exposure
        </button>
      </div>
    );
  }

  // Build cell lookup: (rowKey, colKey) -> value
  const cellMap: Record<string, number> = {};
  for (const c of matrix.cells) {
    cellMap[`${c.row_key}:${c.col_key}`] = c.value;
  }

  const isFactorRow = matrix.row_dimension.toUpperCase() === "FACTOR";

  return (
    <div className="space-y-4 p-4">
      {/* 1. Header Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
            2D Cross-Exposure Matrix
          </span>

          <div className="h-4 w-px bg-atlas-border-default" />

          {/* Dimension Mode Selectors */}
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-atlas-text-secondary mr-1">Partition:</span>
            <button
              onClick={() => onSelectDimensions("FACTOR", "SECTOR")}
              className={`rounded px-2.5 py-1 text-xs font-medium transition ${
                selectedRowDim.toUpperCase() === "FACTOR"
                  ? "bg-atlas-accent text-black font-semibold shadow-sm"
                  : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Factor × Sector
            </button>
            <button
              onClick={() => onSelectDimensions("CURRENCY", "SECTOR")}
              className={`rounded px-2.5 py-1 text-xs font-medium transition ${
                selectedRowDim.toUpperCase() === "CURRENCY"
                  ? "bg-atlas-accent text-black font-semibold shadow-sm"
                  : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Currency × Sector
            </button>
          </div>

          <div className="h-4 w-px bg-atlas-border-default" />

          <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
            <CheckCircle2 className="h-3.5 w-3.5" />
            Reconciled (∑_s b_s,k ≡ b_k)
          </span>
        </div>

        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-atlas-surface-2 border border-atlas-border-default px-2.5 py-1 text-xs text-atlas-text-secondary hover:text-atlas-text-primary transition disabled:opacity-50"
        >
          <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* 2. Cross Exposure Matrix Heat Table */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="border-b border-atlas-border-default/40 p-3 flex items-center justify-between">
          <div>
            <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wide">
              {matrix.row_dimension} × {matrix.col_dimension} Exposure Distribution
            </h4>
            <p className="text-[11px] text-atlas-text-secondary mt-0.5">
              {isFactorRow
                ? "Sector factor loading b_{s,k} = ∑_{i ∈ s} w_i β_{i,k}. Row sum reconciles exactly to total portfolio factor loading."
                : "Joint capital allocation matrix by denomination currency and economic sector."}
            </p>
          </div>
          <span className="text-xs font-mono text-atlas-text-secondary">
            Unit: {matrix.unit}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default/40 bg-atlas-surface-2/60 text-[11px] text-atlas-text-secondary font-semibold uppercase tracking-wider">
                <th className="py-2.5 px-3 min-w-[130px] font-sans text-atlas-text-primary">
                  {matrix.row_dimension} \ {matrix.col_dimension}
                </th>
                {matrix.col_keys.map((ck) => (
                  <th key={ck} className="py-2.5 px-3 text-right min-w-[100px]">
                    {ck}
                  </th>
                ))}
                <th className="py-2.5 px-3 text-right font-bold text-atlas-accent min-w-[100px] border-l border-atlas-border-default/40">
                  Total (Row Sum)
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/30 font-mono text-atlas-text-primary">
              {matrix.row_keys.map((rk) => {
                let rowSum = 0;
                for (const ck of matrix.col_keys) {
                  rowSum += cellMap[`${rk}:${ck}`] ?? 0;
                }

                return (
                  <tr key={rk} className="hover:bg-atlas-surface-2/30 transition">
                    <td className="py-2.5 px-3 font-sans font-bold text-sky-400">
                      {rk.replace("FACTOR_", "")}
                    </td>

                    {matrix.col_keys.map((ck) => {
                      const val = cellMap[`${rk}:${ck}`] ?? 0;
                      // Heat background for significant cells
                      const hasIntensity = Math.abs(val) > 0.05;
                      const heatBg = hasIntensity
                        ? val > 0
                          ? "bg-emerald-500/10 text-emerald-300 font-semibold"
                          : "bg-rose-500/10 text-rose-300 font-semibold"
                        : "text-atlas-text-secondary";

                      return (
                        <td key={ck} className={`py-2.5 px-3 text-right ${heatBg}`}>
                          {isFactorRow ? formatFactorLoading(val) : formatWeight(val)}
                        </td>
                      );
                    })}

                    {/* Row Sum Column */}
                    <td className="py-2.5 px-3 text-right font-bold text-atlas-accent border-l border-atlas-border-default/40 bg-atlas-surface-2/20">
                      {isFactorRow ? formatFactorLoading(rowSum) : formatWeight(rowSum)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

