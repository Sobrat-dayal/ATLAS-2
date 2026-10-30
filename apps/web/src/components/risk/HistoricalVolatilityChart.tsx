"use client";

import React, { useState } from "react";
import { formatVolPercent } from "@/lib/risk/formatting";
import { RollingObservationDTO, VolatilityResponseDTO } from "@/lib/risk/types";
import { Activity, Info } from "lucide-react";

interface HistoricalVolatilityChartProps {
  volatilityData: VolatilityResponseDTO | null;
  rollingWindowSize: number;
  onSelectRollingWindow: (size: number) => void;
}

export function HistoricalVolatilityChart({
  volatilityData,
  rollingWindowSize,
  onSelectRollingWindow,
}: HistoricalVolatilityChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const series = volatilityData?.rolling_series || [];
  const histVol = volatilityData?.historical_volatility_annualized;

  if (series.length < 2) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center">
        <Activity className="h-8 w-8 text-atlas-text-muted opacity-50" />
        <h4 className="mt-2 text-sm font-semibold text-atlas-text-primary">
          Insufficient Observations for Rolling Volatility
        </h4>
        <p className="mt-1 max-w-sm text-xs text-atlas-text-muted">
          A minimum of {rollingWindowSize} consecutive return observations is required to construct this rolling volatility series without hindsight.
        </p>
      </div>
    );
  }

  // Calculate SVG bounds
  const values = series.map((s) => s.metric_value);
  const minVal = Math.max(0, Math.min(...values) * 0.85);
  const maxVal = Math.max(...values, histVol ?? 0) * 1.15;
  const range = maxVal - minVal || 0.01;

  const width = 800;
  const height = 260;
  const padding = { top: 20, right: 30, bottom: 40, left: 60 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const getX = (idx: number) => padding.left + (idx / (series.length - 1)) * plotWidth;
  const getY = (val: number) => padding.top + plotHeight - ((val - minVal) / range) * plotHeight;

  // Path coordinates
  const pathD = series
    .map((s, i) => `${i === 0 ? "M" : "L"} ${getX(i).toFixed(1)} ${getY(s.metric_value).toFixed(1)}`)
    .join(" ");

  const areaD = `${pathD} L ${getX(series.length - 1).toFixed(1)} ${(padding.top + plotHeight).toFixed(1)} L ${padding.left.toFixed(1)} ${(padding.top + plotHeight).toFixed(1)} Z`;

  // Hist vol reference line
  const histVolY = histVol !== undefined && histVol !== null ? getY(histVol) : null;

  // Hovered item
  const hovered = hoveredIndex !== null && hoveredIndex >= 0 && hoveredIndex < series.length ? series[hoveredIndex] : null;

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
      {/* Chart Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default/40 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Rolling Historical Volatility Series
            </h3>
            <span className="rounded bg-atlas-accent-gold/10 px-1.5 py-0.5 text-[10px] font-medium text-atlas-accent-gold">
              Annualized (K=252)
            </span>
          </div>
          <p className="mt-0.5 text-xs text-atlas-text-muted">
            Trailing sample standard deviation computed over strictly past observations (no hindsight bias).
          </p>
        </div>

        {/* Window Selector */}
        <div className="flex items-center gap-1 rounded bg-atlas-surface-2 p-1 text-xs">
          {[20, 60, 120, 252].map((w) => (
            <button
              key={w}
              onClick={() => onSelectRollingWindow(w)}
              className={`rounded px-2.5 py-1 text-xs font-medium transition ${
                rollingWindowSize === w
                  ? "bg-atlas-accent-blue text-white shadow-sm"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              {w === 20 ? "20D (1M)" : w === 60 ? "60D (3M)" : w === 120 ? "120D (6M)" : "252D (1Y)"}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Container */}
      <div className="relative mt-4">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full overflow-visible font-mono text-[10px]"
          onMouseLeave={() => setHoveredIndex(null)}
        >
          {/* Defs */}
          <defs>
            <linearGradient id="volGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
            const val = minVal + pct * range;
            const y = getY(val);
            return (
              <g key={pct}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#27272a"
                  strokeDasharray="3 3"
                />
                <text x={padding.left - 8} y={y + 3} textAnchor="end" fill="#71717a">
                  {(val * 100).toFixed(1)}%
                </text>
              </g>
            );
          })}

          {/* Area fill */}
          <path d={areaD} fill="url(#volGradient)" />

          {/* Line stroke */}
          <path d={pathD} fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" />

          {/* Historical Full-Sample Mean Volatility Reference Line */}
          {histVolY !== null && histVolY >= padding.top && histVolY <= padding.top + plotHeight && (
            <g>
              <line
                x1={padding.left}
                y1={histVolY}
                x2={width - padding.right}
                y2={histVolY}
                stroke="#38bdf8"
                strokeWidth="1.5"
                strokeDasharray="4 4"
              />
              <text x={width - padding.right + 4} y={histVolY + 3} fill="#38bdf8" textAnchor="start">
                Avg {(histVol! * 100).toFixed(1)}%
              </text>
            </g>
          )}

          {/* Hover interaction points */}
          {series.map((s, idx) => {
            const x = getX(idx);
            const y = getY(s.metric_value);
            const isHovered = hoveredIndex === idx;
            return (
              <g key={s.window_end}>
                <rect
                  x={x - 10}
                  y={padding.top}
                  width={20}
                  height={plotHeight}
                  fill="transparent"
                  className="cursor-pointer"
                  onMouseEnter={() => setHoveredIndex(idx)}
                />
                {isHovered && (
                  <>
                    <line
                      x1={x}
                      y1={padding.top}
                      x2={x}
                      y2={padding.top + plotHeight}
                      stroke="#f59e0b"
                      strokeWidth="1"
                      strokeDasharray="2 2"
                    />
                    <circle cx={x} cy={y} r="4" fill="#f59e0b" stroke="#18181b" strokeWidth="2" />
                  </>
                )}
              </g>
            );
          })}

          {/* X Axis Dates (First, Middle, Last) */}
          <text x={padding.left} y={height - 15} fill="#71717a" textAnchor="start">
            {series[0]?.window_end?.substring(0, 10)}
          </text>
          {series.length > 2 && (
            <text
              x={getX(Math.floor(series.length / 2))}
              y={height - 15}
              fill="#71717a"
              textAnchor="middle"
            >
              {series[Math.floor(series.length / 2)]?.window_end?.substring(0, 10)}
            </text>
          )}
          <text x={width - padding.right} y={height - 15} fill="#71717a" textAnchor="end">
            {series[series.length - 1]?.window_end?.substring(0, 10)}
          </text>
        </svg>

        {/* Hover Tooltip Overlay */}
        {hovered && (
          <div className="absolute top-2 right-4 rounded border border-atlas-border-default/80 bg-atlas-surface-2/95 px-3 py-1.5 text-xs shadow-lg backdrop-blur">
            <div className="font-semibold text-atlas-text-primary">
              {hovered.window_end.substring(0, 10)}
            </div>
            <div className="mt-0.5 flex items-center justify-between gap-4 text-atlas-text-secondary">
              <span>{rollingWindowSize}D Rolling Vol:</span>
              <span className="font-mono font-medium text-atlas-accent-gold">
                {formatVolPercent(hovered.metric_value, 2)}
              </span>
            </div>
            <div className="text-[10px] text-atlas-text-muted">
              {hovered.observation_count} matched returns
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

