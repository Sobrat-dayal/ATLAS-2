"use client";

import React, { useMemo, useState } from "react";
import { QuarterlyEarningsItemDTO } from "@/lib/companies/earnings/types";
import { Badge, Button } from "@/design-system";
import { Activity, BarChart2, TrendingUp, TrendingDown, Minus } from "lucide-react";

export interface EarningsActualVsEstimateChartProps {
  items: QuarterlyEarningsItemDTO[];
  currency?: string;
}

export function EarningsActualVsEstimateChart({ items, currency = "USD" }: EarningsActualVsEstimateChartProps) {
  const [metric, setMetric] = useState<"eps" | "revenue">("eps");
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // Take up to 8 quarters and reverse to chronological order (oldest to newest for charting)
  const chartItems = useMemo(() => {
    const valid = items
      .filter((it) => (metric === "eps" ? it.actual_eps !== null : it.actual_revenue !== null))
      .slice(0, 8);
    return [...valid].reverse();
  }, [items, metric]);

  // Chart dimensions
  const width = 640;
  const height = 220;
  const padding = { top: 30, right: 25, bottom: 40, left: 55 };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Max value computation
  const { maxVal, minVal, yZero } = useMemo(() => {
    if (chartItems.length === 0) return { maxVal: 1, minVal: 0, yZero: null };

    const vals: number[] = [];
    chartItems.forEach((it) => {
      if (metric === "eps") {
        if (it.actual_eps !== null && it.actual_eps !== undefined) vals.push(it.actual_eps);
        if (it.estimate_eps !== null && it.estimate_eps !== undefined) vals.push(it.estimate_eps);
      } else {
        if (it.actual_revenue !== null && it.actual_revenue !== undefined)
          vals.push(it.actual_revenue / 1000000000); // Scale to billions
        if (it.estimate_revenue !== null && it.estimate_revenue !== undefined)
          vals.push(it.estimate_revenue / 1000000000);
      }
    });

    if (vals.length === 0) return { maxVal: 1, minVal: 0, yZero: null };

    let max = Math.max(...vals);
    let min = Math.min(...vals);

    if (min >= 0) {
      min = 0;
      max = max * 1.15;
    } else {
      const margin = (max - min) * 0.15;
      max += margin;
      min -= margin;
    }

    let zeroY: number | null = null;
    if (min < 0 && max > 0) {
      const range = max - min;
      zeroY = padding.top + chartHeight - ((0 - min) / range) * chartHeight;
    }

    return { maxVal: max, minVal: min, yZero: zeroY };
  }, [chartItems, metric, chartHeight, padding.top]);

  // Calculate beat statistics
  const beatStats = useMemo(() => {
    if (chartItems.length === 0) return { beatCount: 0, total: 0, beatRate: "0%" };
    const beats = chartItems.filter((it) =>
      metric === "eps" ? it.eps_classification === "BEAT" : it.revenue_classification === "BEAT"
    ).length;
    const rate = Math.round((beats / chartItems.length) * 100);
    return { beatCount: beats, total: chartItems.length, beatRate: `${rate}%` };
  }, [chartItems, metric]);

  const groupWidth = chartItems.length > 0 ? chartWidth / chartItems.length : chartWidth;
  const barWidth = Math.min(Math.max(groupWidth * 0.28, 8), 24);

  return (
    <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4 space-y-3 shadow-xs">
      {/* Header with Metric Toggle and Stats */}
      <div className="flex flex-wrap items-center justify-between pb-2.5 border-b border-atlas-border-subtle gap-2">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-atlas-accent" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
            Actual vs. Consensus Expectations
          </h4>
          <Badge variant="outline" className="font-mono text-[10px]">
            {beatStats.beatCount}/{beatStats.total} Beats ({beatStats.beatRate})
          </Badge>
        </div>

        {/* Metric Selector Toggle */}
        <div className="flex items-center gap-1 bg-atlas-surface-2 p-0.5 rounded-xs border border-atlas-border-subtle">
          <button
            onClick={() => setMetric("eps")}
            className={`px-2.5 py-0.5 text-xs font-mono font-semibold rounded-xs transition-colors ${
              metric === "eps"
                ? "bg-atlas-surface-1 text-atlas-text-primary shadow-xs border border-atlas-border-subtle"
                : "text-atlas-text-muted hover:text-atlas-text-secondary"
            }`}
          >
            Diluted EPS ($)
          </button>
          <button
            onClick={() => setMetric("revenue")}
            className={`px-2.5 py-0.5 text-xs font-mono font-semibold rounded-xs transition-colors ${
              metric === "revenue"
                ? "bg-atlas-surface-1 text-atlas-text-primary shadow-xs border border-atlas-border-subtle"
                : "text-atlas-text-muted hover:text-atlas-text-secondary"
            }`}
          >
            Revenue ($B)
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative w-full overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full max-h-[220px] select-none font-mono text-[10px]"
        >
          {/* Horizontal Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const y = padding.top + chartHeight * ratio;
            const val = maxVal - ratio * (maxVal - minVal);
            return (
              <g key={ratio}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="currentColor"
                  className="text-atlas-border-subtle"
                  strokeDasharray="2 3"
                  strokeWidth="0.75"
                />
                <text
                  x={padding.left - 6}
                  y={y + 3}
                  textAnchor="end"
                  className="fill-atlas-text-muted font-mono text-[9px]"
                >
                  {metric === "eps" ? `$${val.toFixed(2)}` : `$${val.toFixed(0)}B`}
                </text>
              </g>
            );
          })}

          {/* Zero line */}
          {yZero !== null && (
            <line
              x1={padding.left}
              y1={yZero}
              x2={width - padding.right}
              y2={yZero}
              stroke="currentColor"
              className="text-atlas-border-default"
              strokeWidth="1.2"
            />
          )}

          {/* Grouped Bars per Quarter */}
          {chartItems.map((it, idx) => {
            const groupX = padding.left + idx * groupWidth;
            const centerX = groupX + groupWidth / 2;

            const actVal =
              metric === "eps"
                ? it.actual_eps
                : it.actual_revenue !== null && it.actual_revenue !== undefined
                ? it.actual_revenue / 1000000000
                : null;

            const estVal =
              metric === "eps"
                ? it.estimate_eps
                : it.estimate_revenue !== null && it.estimate_revenue !== undefined
                ? it.estimate_revenue / 1000000000
                : null;

            const range = maxVal - minVal || 1;
            const baselineY = yZero !== null ? yZero : padding.top + chartHeight;

            // Bar Y and Height for Estimate (gray bar)
            const estH = estVal !== null && estVal !== undefined ? (Math.abs(estVal) / range) * chartHeight : 0;
            const estY = estVal !== null && estVal !== undefined && estVal >= 0 ? baselineY - estH : baselineY;

            // Bar Y and Height for Actual (colored bar)
            const actH = actVal !== null && actVal !== undefined ? (Math.abs(actVal) / range) * chartHeight : 0;
            const actY = actVal !== null && actVal !== undefined && actVal >= 0 ? baselineY - actH : baselineY;

            const isBeat =
              metric === "eps"
                ? it.eps_classification === "BEAT"
                : it.revenue_classification === "BEAT";

            const isHovered = hoveredIdx === idx;

            return (
              <g
                key={it.fiscal_period}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
                className="cursor-pointer"
              >
                {/* Background highlight on hover */}
                {isHovered && (
                  <rect
                    x={groupX + 4}
                    y={padding.top}
                    width={groupWidth - 8}
                    height={chartHeight}
                    fill="currentColor"
                    className="text-atlas-surface-2 opacity-50"
                    rx="2"
                  />
                )}

                {/* Estimate Bar (left) */}
                {estVal !== null && (
                  <rect
                    x={centerX - barWidth - 1.5}
                    y={estY}
                    width={barWidth}
                    height={estH}
                    fill="currentColor"
                    className="text-atlas-text-muted opacity-40 hover:opacity-60 transition-opacity"
                    rx="1"
                  />
                )}

                {/* Actual Bar (right) */}
                {actVal !== null && (
                  <rect
                    x={centerX + 1.5}
                    y={actY}
                    width={barWidth}
                    height={actH}
                    fill={isBeat ? "var(--color-atlas-positive, #10b981)" : "var(--color-atlas-negative, #ef4444)"}
                    className="transition-all"
                    rx="1"
                  />
                )}

                {/* X Axis Label */}
                <text
                  x={centerX}
                  y={height - padding.bottom + 16}
                  textAnchor="middle"
                  className={`text-[9px] font-mono ${
                    isHovered ? "fill-atlas-text-primary font-bold" : "fill-atlas-text-muted"
                  }`}
                >
                  {it.fiscal_period}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip Box */}
        {hoveredIdx !== null && chartItems[hoveredIdx] && (
          <div
            className="absolute top-2 bg-atlas-surface-2 border border-atlas-border-default rounded-sm px-3 py-2 shadow-md text-xs font-mono space-y-1 z-10 pointer-events-none"
            style={{
              left: Math.min(
                Math.max(padding.left + hoveredIdx * groupWidth - 40, 10),
                width - 180
              ),
            }}
          >
            <div className="font-bold text-atlas-text-primary flex items-center justify-between border-b border-atlas-border-subtle pb-1">
              <span>{chartItems[hoveredIdx].fiscal_period}</span>
              <span
                className={`text-[10px] font-bold ${
                  (metric === "eps"
                    ? chartItems[hoveredIdx].eps_classification
                    : chartItems[hoveredIdx].revenue_classification) === "BEAT"
                    ? "text-atlas-positive"
                    : "text-atlas-negative"
                }`}
              >
                {metric === "eps"
                  ? chartItems[hoveredIdx].eps_classification
                  : chartItems[hoveredIdx].revenue_classification}
              </span>
            </div>
            <div className="flex justify-between gap-4 text-[11px]">
              <span className="text-atlas-text-muted">Actual:</span>
              <span className="font-bold text-atlas-text-primary">
                {metric === "eps"
                  ? chartItems[hoveredIdx].formatted_actual_eps
                  : chartItems[hoveredIdx].formatted_actual_revenue}
              </span>
            </div>
            <div className="flex justify-between gap-4 text-[11px]">
              <span className="text-atlas-text-muted">Consensus Est:</span>
              <span className="font-medium text-atlas-text-secondary">
                {metric === "eps"
                  ? chartItems[hoveredIdx].formatted_estimate_eps
                  : chartItems[hoveredIdx].formatted_estimate_revenue}
              </span>
            </div>
            <div className="flex justify-between gap-4 text-[11px]">
              <span className="text-atlas-text-muted">Surprise:</span>
              <span
                className={`font-bold ${
                  (metric === "eps"
                    ? chartItems[hoveredIdx].eps_surprise_pct || 0
                    : chartItems[hoveredIdx].revenue_surprise_pct || 0) >= 0
                    ? "text-atlas-positive"
                    : "text-atlas-negative"
                }`}
              >
                {metric === "eps"
                  ? chartItems[hoveredIdx].formatted_eps_surprise_pct
                  : chartItems[hoveredIdx].formatted_revenue_surprise_pct}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-atlas-border-subtle text-[11px] font-mono text-atlas-text-muted">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 bg-atlas-positive rounded-xs inline-block" />
            <span>Actual (Beat)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 bg-atlas-negative rounded-xs inline-block" />
            <span>Actual (Miss)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 bg-atlas-text-muted opacity-40 rounded-xs inline-block" />
            <span>Consensus Estimate</span>
          </div>
        </div>

        <span className="text-[10px]">Pre-Release Snapshots • No Look-Ahead</span>
      </div>
    </div>
  );
}
