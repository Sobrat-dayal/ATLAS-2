"use client";

import React, { useState } from "react";
import { LossDistributionDTO, TailRiskCalculationRunDTO } from "@/lib/risk/types";
import { formatVaRReturn } from "@/lib/risk/formatting";
import { BarChart2, Info } from "lucide-react";

interface LossDistributionChartProps {
  distribution: LossDistributionDTO | null;
  run: TailRiskCalculationRunDTO | null;
}

export function LossDistributionChart({ distribution, run }: LossDistributionChartProps) {
  const [hoveredBin, setHoveredBin] = useState<{
    binStart: number;
    binEnd: number;
    freq: number;
    relFreq: number;
  } | null>(null);

  if (!distribution || !distribution.bins || distribution.bins.length === 0) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center text-xs text-atlas-text-muted">
        <BarChart2 className="h-8 w-8 mx-auto text-atlas-text-muted opacity-40 mb-2" />
        <p>Loss distribution histogram will appear once tail risk is calculated.</p>
      </div>
    );
  }

  const bins = distribution.bins;
  const maxFreq = Math.max(...bins.map((b) => b.frequency), 1);
  const varFraction = run?.var_result?.var_fraction ?? run?.var_result?.var_return ?? 0;

  // Chart Dimensions
  const chartHeight = 180;
  const chartWidth = 720;
  const paddingLeft = 35;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 25;

  const innerWidth = chartWidth - paddingLeft - paddingRight;
  const innerHeight = chartHeight - paddingTop - paddingBottom;
  const barWidth = Math.max(1, innerWidth / bins.length - 2);

  const minLoss = distribution.min_loss ?? 0;
  const maxLoss = distribution.max_loss ?? 0;
  const lossSpan = maxLoss - minLoss || 1;

  // Compute VaR position X coordinate in SVG
  const varNormalized = Math.max(0, Math.min(1, (varFraction - minLoss) / lossSpan));
  const varX = paddingLeft + varNormalized * innerWidth;

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-3">
      {/* Chart Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-2">
        <div className="flex items-center gap-2">
          <BarChart2 className="h-4 w-4 text-atlas-accent-blue" />
          <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
            Tail Loss Distribution & Quantile Histogram
          </h3>
        </div>
        <div className="flex items-center gap-3 text-[11px] text-atlas-text-muted">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-slate-500" /> Normal Region
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-rose-500" /> Beyond VaR Tail Loss
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-400" /> VaR Cutoff ({((run?.confidence_level ?? 0.95) * 100).toFixed(1)}%)
          </span>
        </div>
      </div>

      {/* SVG Histogram */}
      <div className="relative w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full h-48 select-none"
        >
          {/* Grid lines */}
          <line
            x1={paddingLeft}
            y1={paddingTop}
            x2={chartWidth - paddingRight}
            y2={paddingTop}
            stroke="#334155"
            strokeDasharray="2,2"
            strokeWidth="0.5"
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
          <line
            x1={paddingLeft}
            y1={paddingTop + innerHeight}
            x2={chartWidth - paddingRight}
            y2={paddingTop + innerHeight}
            stroke="#475569"
            strokeWidth="1"
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
            {maxFreq}
          </text>
          <text
            x={paddingLeft - 6}
            y={paddingTop + innerHeight / 2 + 3}
            fill="#64748b"
            fontSize="9"
            textAnchor="end"
            fontFamily="monospace"
          >
            {Math.round(maxFreq / 2)}
          </text>
          <text
            x={paddingLeft - 6}
            y={paddingTop + innerHeight}
            fill="#64748b"
            fontSize="9"
            textAnchor="end"
            fontFamily="monospace"
          >
            0
          </text>

          {/* Histogram Bars */}
          {bins.map((bin, idx) => {
            const barHeight = (bin.frequency / maxFreq) * innerHeight;
            const x = paddingLeft + (idx / bins.length) * innerWidth + 1;
            const y = paddingTop + innerHeight - barHeight;

            // Is this bin in the tail (greater than or equal to VaR)?
            const isTail = bin.bin_end >= varFraction;

            return (
              <rect
                key={idx}
                x={x}
                y={y}
                width={barWidth}
                height={Math.max(1, barHeight)}
                fill={isTail ? "#e11d48" : "#3b82f6"}
                fillOpacity={isTail ? "0.85" : "0.5"}
                className="transition-colors hover:fill-amber-400 cursor-pointer"
                onMouseEnter={() =>
                  setHoveredBin({
                    binStart: bin.bin_start,
                    binEnd: bin.bin_end,
                    freq: bin.frequency,
                    relFreq: bin.relative_frequency,
                  })
                }
                onMouseLeave={() => setHoveredBin(null)}
              />
            );
          })}

          {/* VaR Cutoff Vertical Line */}
          {varFraction >= minLoss && varFraction <= maxLoss && (
            <g>
              <line
                x1={varX}
                y1={paddingTop}
                x2={varX}
                y2={paddingTop + innerHeight}
                stroke="#f59e0b"
                strokeWidth="1.5"
                strokeDasharray="4,3"
              />
              <text
                x={varX}
                y={paddingTop - 5}
                fill="#f59e0b"
                fontSize="10"
                fontWeight="bold"
                textAnchor="middle"
                fontFamily="monospace"
              >
                VaR ({formatVaRReturn(varFraction)})
              </text>
            </g>
          )}

          {/* X Axis Labels */}
          <text
            x={paddingLeft}
            y={paddingTop + innerHeight + 15}
            fill="#64748b"
            fontSize="9"
            textAnchor="start"
            fontFamily="monospace"
          >
            Min: {formatVaRReturn(minLoss)}
          </text>
          <text
            x={chartWidth - paddingRight}
            y={paddingTop + innerHeight + 15}
            fill="#64748b"
            fontSize="9"
            textAnchor="end"
            fontFamily="monospace"
          >
            Max: {formatVaRReturn(maxLoss)}
          </text>
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredBin && (
          <div className="absolute top-2 right-4 rounded border border-atlas-border-default/80 bg-atlas-surface-2 p-2 text-xs shadow-lg font-mono">
            <div className="text-atlas-text-primary font-bold">
              Range: {formatVaRReturn(hoveredBin.binStart)} → {formatVaRReturn(hoveredBin.binEnd)}
            </div>
            <div className="text-atlas-text-secondary mt-0.5">
              Count: <span className="text-amber-400 font-bold">{hoveredBin.freq}</span> (
              {(hoveredBin.relFreq * 100).toFixed(1)}%)
            </div>
          </div>
        )}
      </div>

      {/* Quantiles Matrix Chips */}
      {distribution.quantiles && (
        <div className="border-t border-atlas-border-default/40 pt-2.5">
          <div className="flex items-center gap-1.5 text-[11px] font-medium text-atlas-text-secondary uppercase tracking-wider mb-2">
            <Info className="h-3.5 w-3.5 text-atlas-accent-blue" />
            <span>Loss Distribution Quantiles & Moments</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-xs">
            <div className="rounded bg-atlas-surface-2 p-1.5 border border-atlas-border-default/40">
              <div className="text-[10px] text-atlas-text-muted">Mean Loss</div>
              <div className="font-mono font-semibold text-atlas-text-primary">
                {formatVaRReturn(distribution.mean_loss)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2 p-1.5 border border-atlas-border-default/40">
              <div className="text-[10px] text-atlas-text-muted">Median (p50)</div>
              <div className="font-mono font-semibold text-atlas-text-primary">
                {formatVaRReturn(distribution.quantiles.p50)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2 p-1.5 border border-atlas-border-default/40">
              <div className="text-[10px] text-atlas-text-muted">p90 Loss</div>
              <div className="font-mono font-semibold text-atlas-text-primary">
                {formatVaRReturn(distribution.quantiles.p90)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2 p-1.5 border border-atlas-border-default/40">
              <div className="text-[10px] text-rose-400">p95 Loss</div>
              <div className="font-mono font-bold text-rose-400">
                {formatVaRReturn(distribution.quantiles.p95)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2 p-1.5 border border-atlas-border-default/40">
              <div className="text-[10px] text-rose-400">p97.5 Loss</div>
              <div className="font-mono font-bold text-rose-400">
                {formatVaRReturn(distribution.quantiles.p97_5 ?? distribution.quantiles["p97.5"])}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2 p-1.5 border border-atlas-border-default/40">
              <div className="text-[10px] text-red-500">p99 Loss</div>
              <div className="font-mono font-bold text-red-500">
                {formatVaRReturn(distribution.quantiles.p99)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2 p-1.5 border border-atlas-border-default/40">
              <div className="text-[10px] text-red-500">Worst Tail Loss</div>
              <div className="font-mono font-bold text-red-500">
                {formatVaRReturn(distribution.max_loss)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

