"use client";

import React, { useMemo, useState } from "react";
import { PerformanceSeriesPoint } from "@/lib/portfolios/performance/types";
import { formatRate } from "@/lib/portfolios/performance/formatting";

interface TimeWeightedGrowthChartProps {
  points: PerformanceSeriesPoint[];
  benchmarkName?: string | null;
  baseCurrency: string;
}

export function TimeWeightedGrowthChart({
  points,
  benchmarkName,
  baseCurrency,
}: TimeWeightedGrowthChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const parsed = useMemo(() => {
    if (!points || points.length === 0) return [];
    return points.map((p, idx) => ({
      index: idx,
      date: new Date(p.timestamp),
      dateStr: new Date(p.timestamp).toLocaleDateString(),
      portfolioIndexed: parseFloat(p.indexed_twr || "100.00"),
      benchmarkIndexed: p.benchmark_indexed ? parseFloat(p.benchmark_indexed) : null,
      portfolioValue: parseFloat(p.portfolio_value || "0.00"),
      cashFlowAmount: p.cash_flow_amount ? parseFloat(p.cash_flow_amount) : null,
      cashFlowType: p.cash_flow_type,
    }));
  }, [points]);

  if (parsed.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1 text-xs text-atlas-text-tertiary">
        No performance series points available for this period.
      </div>
    );
  }

  // Calculate SVG bounds
  const minVal = Math.min(
    95,
    ...parsed.map((p) => Math.min(p.portfolioIndexed, p.benchmarkIndexed ?? p.portfolioIndexed))
  );
  const maxVal = Math.max(
    105,
    ...parsed.map((p) => Math.max(p.portfolioIndexed, p.benchmarkIndexed ?? p.portfolioIndexed))
  );

  const range = maxVal - minVal || 1;
  const width = 800;
  const height = 260;
  const paddingX = 40;
  const paddingY = 30;
  const chartW = width - paddingX * 2;
  const chartH = height - paddingY * 2;

  const getX = (idx: number) => {
    if (parsed.length <= 1) return paddingX + chartW / 2;
    return paddingX + (idx / (parsed.length - 1)) * chartW;
  };

  const getY = (val: number) => {
    return height - paddingY - ((val - minVal) / range) * chartH;
  };

  // Generate paths
  const portPath = parsed
    .map((p, i) => `${i === 0 ? "M" : "L"} ${getX(i)} ${getY(p.portfolioIndexed)}`)
    .join(" ");

  const benchPath = parsed[0]?.benchmarkIndexed !== null
    ? parsed
        .map((p, i) => `${i === 0 ? "M" : "L"} ${getX(i)} ${getY(p.benchmarkIndexed ?? 100)}`)
        .join(" ")
    : null;

  const baselineY = getY(100.0);

  const activePoint = hoveredIndex !== null ? parsed[hoveredIndex] : parsed[parsed.length - 1];

  return (
    <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-4 shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-2.5">
        <div>
          <h4 className="text-xs font-semibold text-atlas-text-primary">
            Time-Weighted Growth of $100.00 (Flow-Adjusted)
          </h4>
          <p className="text-[11px] text-atlas-text-secondary">
            Cumulative growth rebased to 100.00 at period inception. Flow-neutral geometric compounding.
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-atlas-accent" />
            <span className="text-atlas-text-primary">Portfolio:</span>
            <span className="font-semibold text-atlas-text-primary">
              {activePoint ? activePoint.portfolioIndexed.toFixed(2) : "100.00"}
            </span>
            <span className="text-[11px] text-atlas-text-tertiary">
              ({formatRate((activePoint?.portfolioIndexed ?? 100) / 100 - 1)})
            </span>
          </div>

          {benchPath && (
            <div className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-400" />
              <span className="text-atlas-text-primary">{benchmarkName || "Benchmark"}:</span>
              <span className="font-semibold text-amber-400">
                {activePoint?.benchmarkIndexed ? activePoint.benchmarkIndexed.toFixed(2) : "--"}
              </span>
              <span className="text-[11px] text-atlas-text-tertiary">
                ({activePoint?.benchmarkIndexed ? formatRate(activePoint.benchmarkIndexed / 100 - 1) : "--"})
              </span>
            </div>
          )}
        </div>
      </div>

      {/* SVG Chart Area */}
      <div className="relative mt-3">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="h-64 w-full overflow-visible font-mono text-[10px]"
        >
          {/* Horizontal grid lines */}
          <line
            x1={paddingX}
            y1={baselineY}
            x2={width - paddingX}
            y2={baselineY}
            stroke="#475569"
            strokeDasharray="4 4"
            strokeWidth="1"
          />
          <text
            x={paddingX - 6}
            y={baselineY + 3}
            fill="#94a3b8"
            textAnchor="end"
            fontSize="10"
          >
            100.0
          </text>

          <line
            x1={paddingX}
            y1={paddingY}
            x2={width - paddingX}
            y2={paddingY}
            stroke="#334155"
            strokeDasharray="2 2"
            strokeWidth="0.5"
          />
          <text
            x={paddingX - 6}
            y={paddingY + 3}
            fill="#64748b"
            textAnchor="end"
            fontSize="10"
          >
            {maxVal.toFixed(1)}
          </text>

          <line
            x1={paddingX}
            y1={height - paddingY}
            x2={width - paddingX}
            y2={height - paddingY}
            stroke="#334155"
            strokeDasharray="2 2"
            strokeWidth="0.5"
          />
          <text
            x={paddingX - 6}
            y={height - paddingY + 3}
            fill="#64748b"
            textAnchor="end"
            fontSize="10"
          >
            {minVal.toFixed(1)}
          </text>

          {/* Benchmark line */}
          {benchPath && (
            <path
              d={benchPath}
              fill="none"
              stroke="#fbbf24"
              strokeWidth="1.75"
              strokeDasharray="5 3"
            />
          )}

          {/* Portfolio line */}
          <path
            d={portPath}
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Interactive point nodes & cash flow markers */}
          {parsed.map((p, idx) => {
            const cx = getX(idx);
            const cy = getY(p.portfolioIndexed);
            const isHovered = hoveredIndex === idx;

            return (
              <g
                key={idx}
                onMouseEnter={() => setHoveredIndex(idx)}
                onMouseLeave={() => setHoveredIndex(null)}
                className="cursor-pointer"
              >
                {/* Cash flow highlight marker */}
                {p.cashFlowAmount && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={6}
                    fill={p.cashFlowAmount > 0 ? "#10b981" : "#3b82f6"}
                    fillOpacity="0.3"
                    stroke={p.cashFlowAmount > 0 ? "#10b981" : "#3b82f6"}
                    strokeWidth="1.5"
                  />
                )}

                {/* Point circle */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? 4.5 : 2.5}
                  fill={isHovered ? "#ffffff" : "#38bdf8"}
                  stroke="#0f172a"
                  strokeWidth="1.5"
                />

                {/* Hover vertical crosshair */}
                {isHovered && (
                  <line
                    x1={cx}
                    y1={paddingY}
                    x2={cx}
                    y2={height - paddingY}
                    stroke="#94a3b8"
                    strokeWidth="1"
                    strokeDasharray="3 3"
                  />
                )}
              </g>
            );
          })}
        </svg>

        {/* Date axis ticks */}
        <div className="flex justify-between px-10 text-[10px] font-mono text-atlas-text-tertiary">
          <span>{parsed[0]?.dateStr}</span>
          {parsed.length > 2 && (
            <span>{parsed[Math.floor(parsed.length / 2)]?.dateStr}</span>
          )}
          <span>{parsed[parsed.length - 1]?.dateStr}</span>
        </div>
      </div>

      {/* Legend & Cash Flow Annotations */}
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-atlas-border-default/40 pt-2 text-[11px] text-atlas-text-secondary">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            External Contribution
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-blue-400" />
            External Withdrawal
          </span>
        </div>
        <span className="text-atlas-text-tertiary">
          Excludes internal trades and reinvested dividends from cash flows.
        </span>
      </div>
    </div>
  );
}

