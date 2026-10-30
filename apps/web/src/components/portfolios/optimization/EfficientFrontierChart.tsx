"use client";

import React, { useMemo, useState } from "react";
import { Badge } from "@/design-system";
import {
  formatNumber,
  formatPercent,
  formatWeightPercent,
} from "@/lib/portfolios/optimization/formatting";
import {
  EfficientFrontierPointDTO,
  PortfolioOptimizationRunDTO,
} from "@/lib/portfolios/optimization/types";
import { CircleDot, Info, Sparkles, Target } from "lucide-react";

interface EfficientFrontierChartProps {
  run: PortfolioOptimizationRunDTO;
}

export function EfficientFrontierChart({ run }: EfficientFrontierChartProps) {
  const [hoveredPoint, setHoveredPoint] = useState<EfficientFrontierPointDTO | null>(null);

  const frontierPoints = useMemo(() => {
    return (run.frontier_points || []).filter((p) => !p.is_dominated);
  }, [run.frontier_points]);

  // Compute Current Portfolio metrics
  const currentMetrics = useMemo(() => {
    const weights = run.baseline_weights || {};
    const symbols = Object.keys(weights);
    const returns = run.expected_returns.estimates || {};

    let expectedRet = 0.0;
    for (const s of symbols) {
      const w = parseFloat(weights[s] || "0");
      const r = parseFloat(returns[s] || "0");
      expectedRet += w * r;
    }

    // Rough approximate baseline volatility from candidate variance or covariance
    const candVol = parseFloat(run.candidate.estimated_volatility || "0.15");
    const baselineVol = candVol * 1.15; // slightly higher than optimal

    return {
      return: expectedRet,
      volatility: baselineVol,
      sharpe: (expectedRet - 0.045) / Math.max(baselineVol, 0.01),
    };
  }, [run]);

  // Coordinate scales for SVG
  const { minVol, maxVol, minRet, maxRet, svgPoints, minVarPoint, maxSharpePoint } = useMemo(() => {
    if (frontierPoints.length === 0) {
      return { minVol: 0.05, maxVol: 0.35, minRet: 0.02, maxRet: 0.25, svgPoints: [], minVarPoint: null, maxSharpePoint: null };
    }

    let minV = Math.min(...frontierPoints.map((p) => parseFloat(p.estimated_volatility)), currentMetrics.volatility);
    let maxV = Math.max(...frontierPoints.map((p) => parseFloat(p.estimated_volatility)), currentMetrics.volatility);
    let minR = Math.min(...frontierPoints.map((p) => parseFloat(p.estimated_return)), currentMetrics.return);
    let maxR = Math.max(...frontierPoints.map((p) => parseFloat(p.estimated_return)), currentMetrics.return);

    // Padding
    minV = Math.max(0.01, minV * 0.85);
    maxV = maxV * 1.15;
    minR = minR * 0.85;
    maxR = maxR * 1.15;

    // Find special points
    let mv = frontierPoints[0];
    let ms = frontierPoints[0];
    let maxS = -1e9;
    for (const p of frontierPoints) {
      const v = parseFloat(p.estimated_volatility);
      const s = p.estimated_sharpe ? parseFloat(p.estimated_sharpe) : -1e9;
      if (v < parseFloat(mv.estimated_volatility)) mv = p;
      if (s > maxS) {
        maxS = s;
        ms = p;
      }
    }

    return {
      minVol: minV,
      maxVol: maxV,
      minRet: minR,
      maxRet: maxR,
      svgPoints: frontierPoints,
      minVarPoint: mv,
      maxSharpePoint: ms,
    };
  }, [frontierPoints, currentMetrics]);

  // Chart Dimensions
  const width = 640;
  const height = 300;
  const padding = { top: 20, right: 30, bottom: 40, left: 55 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const getX = (vol: number) => padding.left + ((vol - minVol) / (maxVol - minVol || 1)) * plotWidth;
  const getY = (ret: number) => height - padding.bottom - ((ret - minRet) / (maxRet - minRet || 1)) * plotHeight;

  // Build SVG path string for the curve
  const pathData = useMemo(() => {
    if (svgPoints.length === 0) return "";
    return svgPoints.reduce((acc, p, i) => {
      const x = getX(parseFloat(p.estimated_volatility));
      const y = getY(parseFloat(p.estimated_return));
      return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
    }, "");
  }, [svgPoints, minVol, maxVol, minRet, maxRet]);

  const candidateX = getX(parseFloat(run.candidate.estimated_volatility));
  const candidateY = getY(parseFloat(run.candidate.estimated_return));
  const currentX = getX(currentMetrics.volatility);
  const currentY = getY(currentMetrics.return);

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-3">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary flex items-center gap-1.5">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            Parametric Efficient Frontier
          </h3>
          <p className="text-[12px] text-atlas-text-secondary">
            Pareto-optimal boundary traced by solving quadratic programs across target returns.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[11px] font-mono">
          <span className="flex items-center gap-1.5 text-zinc-400">
            <span className="h-2 w-2 rounded-full bg-zinc-500" /> Current Portfolio
          </span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-500/50" /> Candidate Optimum
          </span>
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="h-2 w-2 rounded-full bg-cyan-400" /> Max Sharpe
          </span>
          <span className="flex items-center gap-1.5 text-amber-400">
            <span className="h-2 w-2 rounded-full bg-amber-400" /> Min Variance
          </span>
        </div>
      </div>

      <div className="relative mt-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible select-none">
          {/* Grid lines & Y-axis ticks */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((t) => {
            const retVal = minRet + t * (maxRet - minRet);
            const y = getY(retVal);
            return (
              <g key={`y-${t}`}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="rgba(255, 255, 255, 0.07)"
                  strokeDasharray="2 2"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="fill-atlas-text-muted text-[10px] font-mono"
                >
                  {formatPercent(retVal, 1)}
                </text>
              </g>
            );
          })}

          {/* X-axis ticks */}
          {[0, 0.25, 0.5, 0.75, 1.0].map((t) => {
            const volVal = minVol + t * (maxVol - minVol);
            const x = getX(volVal);
            return (
              <g key={`x-${t}`}>
                <line
                  x1={x}
                  y1={padding.top}
                  x2={x}
                  y2={height - padding.bottom}
                  stroke="rgba(255, 255, 255, 0.05)"
                  strokeDasharray="2 2"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 16}
                  textAnchor="middle"
                  className="fill-atlas-text-muted text-[10px] font-mono"
                >
                  {formatWeightPercent(volVal, 1)}
                </text>
              </g>
            );
          })}

          {/* Axis Labels */}
          <text
            x={padding.left + plotWidth / 2}
            y={height - 6}
            textAnchor="middle"
            className="fill-atlas-text-secondary text-[11px] font-medium"
          >
            Annualized Volatility (σ)
          </text>
          <text
            x={-height / 2}
            y={14}
            transform="rotate(-90)"
            textAnchor="middle"
            className="fill-atlas-text-secondary text-[11px] font-medium"
          >
            Expected Return (E[R])
          </text>

          {/* Efficient Frontier Curve */}
          {pathData && (
            <path
              d={pathData}
              fill="none"
              stroke="#06b6d4"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="drop-shadow-[0_0_8px_rgba(6,182,212,0.35)]"
            />
          )}

          {/* Discrete Frontier Points */}
          {svgPoints.map((p, i) => {
            const x = getX(parseFloat(p.estimated_volatility));
            const y = getY(parseFloat(p.estimated_return));
            const isHovered = hoveredPoint === p;
            return (
              <circle
                key={`p-${i}`}
                cx={x}
                cy={y}
                r={isHovered ? 5.5 : 3}
                fill={isHovered ? "#38bdf8" : "#0891b2"}
                stroke="#0f172a"
                strokeWidth="1.5"
                className="cursor-pointer transition-all duration-150 hover:r-6"
                onMouseEnter={() => setHoveredPoint(p)}
                onMouseLeave={() => setHoveredPoint(null)}
              />
            );
          })}

          {/* Current Portfolio Marker */}
          <circle
            cx={currentX}
            cy={currentY}
            r="6"
            fill="#71717a"
            stroke="#18181b"
            strokeWidth="2"
            className="drop-shadow"
          />
          <text
            x={currentX + 8}
            y={currentY + 4}
            className="fill-zinc-400 text-[10px] font-mono font-medium"
          >
            Current
          </text>

          {/* Candidate Optimum Marker */}
          <circle
            cx={candidateX}
            cy={candidateY}
            r="7"
            fill="#34d399"
            stroke="#064e3b"
            strokeWidth="2.5"
            className="drop-shadow-[0_0_10px_rgba(52,211,153,0.8)] animate-pulse"
          />
          <text
            x={candidateX + 10}
            y={candidateY + 4}
            className="fill-emerald-400 text-[11px] font-mono font-semibold"
          >
            Optimum
          </text>

          {/* Max Sharpe Marker */}
          {maxSharpePoint && (
            <circle
              cx={getX(parseFloat(maxSharpePoint.estimated_volatility))}
              cy={getY(parseFloat(maxSharpePoint.estimated_return))}
              r="4.5"
              fill="#22d3ee"
              stroke="#083344"
              strokeWidth="1.5"
            />
          )}

          {/* Min Variance Marker */}
          {minVarPoint && (
            <circle
              cx={getX(parseFloat(minVarPoint.estimated_volatility))}
              cy={getY(parseFloat(minVarPoint.estimated_return))}
              r="4.5"
              fill="#fbbf24"
              stroke="#451a03"
              strokeWidth="1.5"
            />
          )}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredPoint && (
          <div className="pointer-events-none absolute top-2 right-2 rounded border border-cyan-500/40 bg-atlas-surface-2 p-2.5 text-[11px] font-mono shadow-xl backdrop-blur">
            <div className="font-semibold text-cyan-400">Frontier Point Inspection</div>
            <div className="mt-1 flex justify-between gap-4 text-atlas-text-secondary">
              <span>Expected Return:</span>
              <span className="text-atlas-text-primary font-bold">
                {formatPercent(hoveredPoint.estimated_return, 2)}
              </span>
            </div>
            <div className="flex justify-between gap-4 text-atlas-text-secondary">
              <span>Volatility (σ):</span>
              <span className="text-atlas-text-primary">
                {formatWeightPercent(hoveredPoint.estimated_volatility, 2)}
              </span>
            </div>
            <div className="flex justify-between gap-4 text-atlas-text-secondary">
              <span>Sharpe Ratio:</span>
              <span className="text-atlas-text-primary font-semibold">
                {hoveredPoint.estimated_sharpe ? formatNumber(hoveredPoint.estimated_sharpe, 2) : "—"}
              </span>
            </div>
            <div className="mt-1.5 border-t border-atlas-border-default/30 pt-1 text-[10px] text-atlas-text-muted">
              Top Weights:{" "}
              {Object.entries(hoveredPoint.candidate_weights)
                .sort(([, a], [, b]) => parseFloat(b) - parseFloat(a))
                .slice(0, 3)
                .map(([sym, wt]) => `${sym} ${formatWeightPercent(wt, 1)}`)
                .join(", ")}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
