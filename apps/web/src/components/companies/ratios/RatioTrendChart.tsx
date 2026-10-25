"use client";

import React, { useMemo, useState } from "react";
import { RatioHistoryResponse, RatioHistoryPointDTO } from "@/lib/companies/ratios/types";
import { Badge, Button } from "@/design-system";
import { TrendingUp, TrendingDown, Minus, X, Activity } from "lucide-react";

export interface RatioTrendChartProps {
  series: RatioHistoryResponse;
  onClose?: () => void;
}

export function RatioTrendChart({ series, onClose }: RatioTrendChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // Extract numerical points and filter valid points
  const points = series.series;

  const validPoints = useMemo(() => {
    return points
      .map((p: RatioHistoryPointDTO, idx: number) => ({
        ...p,
        originalIndex: idx,
        numValue:
          p.exact_value !== null && p.exact_value !== undefined && p.status === "AVAILABLE"
            ? typeof p.exact_value === "number"
              ? p.exact_value
              : parseFloat(p.exact_value)
            : null,
      }))
      .filter((p) => p.numValue !== null) as Array<{
      period_id: string;
      fiscal_year: number;
      period_type: string;
      status: string;
      formatted_value: string;
      originalIndex: number;
      numValue: number;
    }>;
  }, [points]);

  // SVG dimensions
  const width = 640;
  const height = 200;
  const padding = { top: 25, right: 30, bottom: 35, left: 60 };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Min / Max computation
  const { minVal, maxVal, yZero } = useMemo(() => {
    if (validPoints.length === 0) {
      return { minVal: 0, maxVal: 1, yZero: null };
    }
    const vals = validPoints.map((p) => p.numValue);
    let min = Math.min(...vals);
    let max = Math.max(...vals);

    if (min === max) {
      min = min * 0.9;
      max = max * 1.1;
      if (min === 0 && max === 0) {
        max = 1;
      }
    } else {
      const margin = (max - min) * 0.15;
      min -= margin;
      max += margin;
    }

    let zeroY: number | null = null;
    if (min < 0 && max > 0) {
      const range = max - min;
      zeroY = padding.top + chartHeight - ((0 - min) / range) * chartHeight;
    }

    return { minVal: min, maxVal: max, yZero: zeroY };
  }, [validPoints, chartHeight, padding.top]);

  // Coordinate mapping
  const coordinates = useMemo(() => {
    if (points.length === 0) return [];

    const range = maxVal - minVal || 1;
    const stepX = points.length > 1 ? chartWidth / (points.length - 1) : chartWidth / 2;

    return points.map((p: RatioHistoryPointDTO, idx: number) => {
      const x = padding.left + (points.length > 1 ? idx * stepX : chartWidth / 2);
      const num =
        p.exact_value !== null && p.exact_value !== undefined && p.status === "AVAILABLE"
          ? typeof p.exact_value === "number"
            ? p.exact_value
            : parseFloat(p.exact_value)
          : null;
      const y =
        num !== null
          ? padding.top + chartHeight - ((num - minVal) / range) * chartHeight
          : null;

      return {
        ...p,
        x,
        y,
        num,
        index: idx,
      };
    });
  }, [points, minVal, maxVal, chartWidth, chartHeight, padding.left, padding.top]);

  // Construct SVG line segments (skipping unavailable/null points)
  const lineSegments = useMemo(() => {
    const segments: Array<Array<{ x: number; y: number }>> = [];
    let currentSegment: Array<{ x: number; y: number }> = [];

    coordinates.forEach((pt: { x: number; y: number | null }) => {
      if (pt.y !== null) {
        currentSegment.push({ x: pt.x, y: pt.y });
      } else {
        if (currentSegment.length > 0) {
          segments.push(currentSegment);
          currentSegment = [];
        }
      }
    });

    if (currentSegment.length > 0) {
      segments.push(currentSegment);
    }

    return segments;
  }, [coordinates]);

  // Trend analysis (earliest valid to latest valid)
  const trendInfo = useMemo(() => {
    if (validPoints.length < 2) return { direction: "neutral", change: "N/A" };
    const first = validPoints[0].numValue;
    const last = validPoints[validPoints.length - 1].numValue;
    const diff = last - first;

    if (Math.abs(diff) < 0.0001) {
      return { direction: "neutral", change: "Flat" };
    } else if (diff > 0) {
      return {
        direction: "up",
        change: `+${diff.toFixed(2)}${series.unit_kind === "PERCENT" ? "%" : ""}`,
      };
    } else {
      return {
        direction: "down",
        change: `${diff.toFixed(2)}${series.unit_kind === "PERCENT" ? "%" : ""}`,
      };
    }
  }, [validPoints, series.unit_kind]);

  return (
    <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4 space-y-3 shadow-xs">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-atlas-border-subtle">
        <div className="flex items-center gap-2.5">
          <Activity className="w-4 h-4 text-atlas-accent" />
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-xs font-bold text-atlas-text-primary tracking-wide">
                {series.ratio_name}
              </h4>
              <Badge variant="outline" className="text-[10px] uppercase font-mono">
                {series.category}
              </Badge>
            </div>
            <div className="text-[11px] text-atlas-text-muted font-mono mt-0.5">
              ID: {series.ratio_id} • Unit: {series.unit_kind}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Trend Badge */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="text-atlas-text-muted">Multi-Period Trend:</span>
            {trendInfo.direction === "up" && (
              <span className="flex items-center text-atlas-positive font-bold gap-0.5">
                <TrendingUp className="w-3.5 h-3.5" />
                {trendInfo.change}
              </span>
            )}
            {trendInfo.direction === "down" && (
              <span className="flex items-center text-atlas-negative font-bold gap-0.5">
                <TrendingDown className="w-3.5 h-3.5" />
                {trendInfo.change}
              </span>
            )}
            {trendInfo.direction === "neutral" && (
              <span className="flex items-center text-atlas-text-muted font-bold gap-0.5">
                <Minus className="w-3.5 h-3.5" />
                Flat
              </span>
            )}
          </div>

          {onClose && (
            <Button
              variant="secondary"
              size="sm"
              onClick={onClose}
              className="h-7 w-7 p-0"
              title="Close Trend Chart"
            >
              <X className="w-3.5 h-3.5" />
            </Button>
          )}
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
                  x={padding.left - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="fill-atlas-text-muted font-mono text-[9px]"
                >
                  {val.toFixed(series.unit_kind === "PERCENT" ? 1 : 2)}
                  {series.unit_kind === "PERCENT" ? "%" : ""}
                </text>
              </g>
            );
          })}

          {/* Zero Baseline if applicable */}
          {yZero !== null && (
            <line
              x1={padding.left}
              y1={yZero}
              x2={width - padding.right}
              y2={yZero}
              stroke="currentColor"
              className="text-atlas-border-default"
              strokeWidth="1.25"
            />
          )}

          {/* Line Segments */}
          {lineSegments.map((seg, sIdx) => {
            const pathData = seg
              .map((pt, pIdx) => `${pIdx === 0 ? "M" : "L"} ${pt.x} ${pt.y}`)
              .join(" ");

            return (
              <path
                key={sIdx}
                d={pathData}
                fill="none"
                stroke="var(--color-atlas-accent, #3b82f6)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            );
          })}

          {/* Data Points */}
          {coordinates.map((pt, idx: number) => {
            const isHovered = hoveredIndex === idx;

            return (
              <g
                key={idx}
                onMouseEnter={() => setHoveredIndex(idx)}
                onMouseLeave={() => setHoveredIndex(null)}
                className="cursor-pointer"
              >
                {/* Vertical Guideline on Hover */}
                {isHovered && (
                  <line
                    x1={pt.x}
                    y1={padding.top}
                    x2={pt.x}
                    y2={height - padding.bottom}
                    stroke="currentColor"
                    className="text-atlas-border-default"
                    strokeDasharray="2 2"
                    strokeWidth="1"
                  />
                )}

                {/* Point Marker */}
                {pt.y !== null ? (
                  <circle
                    cx={pt.x}
                    cy={pt.y}
                    r={isHovered ? 5 : 3.5}
                    className={
                      isHovered
                        ? "fill-atlas-surface-1 stroke-atlas-accent stroke-2"
                        : "fill-atlas-accent stroke-atlas-surface-1 stroke-1"
                    }
                  />
                ) : (
                  /* Marker for Unavailable / N/M */
                  <circle
                    cx={pt.x}
                    cy={padding.top + chartHeight / 2}
                    r={2.5}
                    className="fill-atlas-text-muted opacity-40"
                  />
                )}

                {/* X-Axis Period Label */}
                <text
                  x={pt.x}
                  y={height - padding.bottom + 16}
                  textAnchor="middle"
                  className={`text-[9px] font-mono ${
                    isHovered
                      ? "fill-atlas-text-primary font-bold"
                      : "fill-atlas-text-muted"
                  }`}
                >
                  {pt.period_id}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredIndex !== null && coordinates[hoveredIndex] && (
          <div
            className="absolute top-2 pointer-events-none bg-atlas-surface-2 border border-atlas-border-default rounded-sm px-2.5 py-1.5 shadow-md text-xs font-mono space-y-0.5 z-10"
            style={{
              left: Math.min(
                Math.max(coordinates[hoveredIndex].x - 60, 10),
                width - 150
              ),
            }}
          >
            <div className="text-[10px] text-atlas-text-muted">
              Period: <span className="text-atlas-text-primary font-bold">{coordinates[hoveredIndex].period_id}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-atlas-text-muted">Value:</span>
              <span
                className={`font-bold ${
                  coordinates[hoveredIndex].status === "AVAILABLE"
                    ? "text-atlas-positive"
                    : "text-atlas-text-muted"
                }`}
              >
                {coordinates[hoveredIndex].formatted_value}
              </span>
            </div>
            <div className="text-[9px] text-atlas-text-muted">
              Status: {coordinates[hoveredIndex].status}
            </div>
          </div>
        )}
      </div>

      {/* Summary Stats Footer */}
      {validPoints.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-atlas-border-subtle text-[11px] font-mono">
          <div>
            <span className="text-atlas-text-muted">Latest ({validPoints[validPoints.length - 1].period_id}): </span>
            <span className="font-bold text-atlas-text-primary">
              {validPoints[validPoints.length - 1].formatted_value}
            </span>
          </div>
          <div>
            <span className="text-atlas-text-muted">Min: </span>
            <span className="font-bold text-atlas-text-secondary">
              {Math.min(...validPoints.map((p) => p.numValue)).toFixed(2)}
              {series.unit_kind === "PERCENT" ? "%" : ""}
            </span>
          </div>
          <div>
            <span className="text-atlas-text-muted">Max: </span>
            <span className="font-bold text-atlas-text-secondary">
              {Math.max(...validPoints.map((p) => p.numValue)).toFixed(2)}
              {series.unit_kind === "PERCENT" ? "%" : ""}
            </span>
          </div>
          <div>
            <span className="text-atlas-text-muted">Avg: </span>
            <span className="font-bold text-atlas-text-secondary">
              {(
                validPoints.reduce((acc, p) => acc + p.numValue, 0) / validPoints.length
              ).toFixed(2)}
              {series.unit_kind === "PERCENT" ? "%" : ""}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
