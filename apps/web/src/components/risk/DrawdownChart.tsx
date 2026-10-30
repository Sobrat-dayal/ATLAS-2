"use client";

import React, { useState } from "react";
import { formatSignedPercent } from "@/lib/risk/formatting";
import { DrawdownsResponseDTO } from "@/lib/risk/types";
import { AlertCircle, Flame } from "lucide-react";

interface DrawdownChartProps {
  drawdownData: DrawdownsResponseDTO | null;
}

export function DrawdownChart({ drawdownData }: DrawdownChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const wealthSeries = drawdownData?.wealth_index_series || [];
  const ddSeries = drawdownData?.drawdown_series || [];

  if (wealthSeries.length < 2 || ddSeries.length < 2) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center">
        <Flame className="h-8 w-8 text-rose-500/50" />
        <h4 className="mt-2 text-sm font-semibold text-atlas-text-primary">
          Insufficient Historical Wealth Index Observations
        </h4>
        <p className="mt-1 max-w-sm text-xs text-atlas-text-muted">
          Drawdown analytics require a cash-flow-adjusted wealth index series with at least two valuation dates.
        </p>
      </div>
    );
  }

  // Min and max for drawdown (drawdowns are <= 0)
  const ddValues = ddSeries.map((d) => d[1]);
  const minDD = Math.min(-0.05, Math.min(...ddValues) * 1.15); // e.g. -0.28
  const maxDD = 0.0;
  const ddRange = Math.abs(minDD);

  const width = 800;
  const height = 240;
  const padding = { top: 15, right: 30, bottom: 35, left: 60 };

  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  const getX = (idx: number) => padding.left + (idx / (ddSeries.length - 1)) * plotWidth;
  const getY = (val: number) => padding.top + ((0 - val) / ddRange) * plotHeight;

  // Path for drawdown
  const pathD = ddSeries
    .map((d, i) => `${i === 0 ? "M" : "L"} ${getX(i).toFixed(1)} ${getY(d[1]).toFixed(1)}`)
    .join(" ");

  const zeroY = getY(0);
  const areaD = `${pathD} L ${getX(ddSeries.length - 1).toFixed(1)} ${zeroY.toFixed(1)} L ${padding.left.toFixed(1)} ${zeroY.toFixed(1)} Z`;

  // Maximum Drawdown marker
  let maxDDPt = { idx: 0, val: 0 };
  ddSeries.forEach((d, i) => {
    if (d[1] < maxDDPt.val) {
      maxDDPt = { idx: i, val: d[1] };
    }
  });

  const hovered =
    hoveredIndex !== null && hoveredIndex >= 0 && hoveredIndex < ddSeries.length
      ? {
          date: ddSeries[hoveredIndex][0],
          drawdown: ddSeries[hoveredIndex][1],
          wealth: wealthSeries[hoveredIndex] ? wealthSeries[hoveredIndex][1] : 100,
        }
      : null;

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Underwater Drawdown Profile & Valley Fill
            </h3>
            <span className="rounded bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-medium text-rose-400">
              D(t) = W(t)/P(t) - 1
            </span>
          </div>
          <p className="mt-0.5 text-xs text-atlas-text-muted">
            Continuous percentage loss from the running historical high watermark (cash-flow-neutral).
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <span className="text-atlas-text-secondary">
            Max Drawdown:{" "}
            <span className="font-semibold text-rose-400">
              {formatSignedPercent(drawdownData?.max_drawdown, 2)}
            </span>
          </span>
          <span className="text-atlas-text-muted">|</span>
          <span className="text-atlas-text-secondary">
            Current Drawdown:{" "}
            <span className="font-semibold text-amber-400">
              {formatSignedPercent(drawdownData?.current_drawdown, 2)}
            </span>
          </span>
        </div>
      </div>

      <div className="relative mt-4">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full overflow-visible font-mono text-[10px]"
          onMouseLeave={() => setHoveredIndex(null)}
        >
          <defs>
            <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.05" />
              <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.35" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, -0.25, -0.5, -0.75, -1.0].map((step) => {
            const val = step * ddRange;
            const y = getY(val);
            return (
              <g key={step}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#27272a"
                  strokeDasharray="3 3"
                />
                <text x={padding.left - 8} y={y + 3} textAnchor="end" fill="#71717a">
                  {(val * 100).toFixed(0)}%
                </text>
              </g>
            );
          })}

          {/* Zero baseline (Peak Watermark) */}
          <line
            x1={padding.left}
            y1={zeroY}
            x2={width - padding.right}
            y2={zeroY}
            stroke="#52525b"
            strokeWidth="1.5"
          />

          {/* Drawdown area fill */}
          <path d={areaD} fill="url(#drawdownGradient)" />

          {/* Drawdown line */}
          <path d={pathD} fill="none" stroke="#f43f5e" strokeWidth="2" strokeLinecap="round" />

          {/* Max Drawdown Trough Marker */}
          {maxDDPt.val < 0 && (
            <g>
              <circle
                cx={getX(maxDDPt.idx)}
                cy={getY(maxDDPt.val)}
                r="5"
                fill="#f43f5e"
                stroke="#18181b"
                strokeWidth="2"
              />
              <text
                x={getX(maxDDPt.idx)}
                y={getY(maxDDPt.val) + 16}
                textAnchor="middle"
                fill="#f43f5e"
                className="font-semibold"
              >
                MDD {(maxDDPt.val * 100).toFixed(1)}%
              </text>
            </g>
          )}

          {/* Interactive hover overlay */}
          {ddSeries.map((d, idx) => {
            const x = getX(idx);
            const isHovered = hoveredIndex === idx;
            return (
              <g key={d[0]}>
                <rect
                  x={x - 8}
                  y={padding.top}
                  width={16}
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
                      stroke="#f43f5e"
                      strokeWidth="1"
                      strokeDasharray="2 2"
                    />
                    <circle
                      cx={x}
                      cy={getY(d[1])}
                      r="4"
                      fill="#f43f5e"
                      stroke="#18181b"
                      strokeWidth="2"
                    />
                  </>
                )}
              </g>
            );
          })}

          {/* Dates */}
          <text x={padding.left} y={height - 12} fill="#71717a" textAnchor="start">
            {ddSeries[0]?.[0]?.substring(0, 10)}
          </text>
          {ddSeries.length > 2 && (
            <text
              x={getX(Math.floor(ddSeries.length / 2))}
              y={height - 12}
              fill="#71717a"
              textAnchor="middle"
            >
              {ddSeries[Math.floor(ddSeries.length / 2)]?.[0]?.substring(0, 10)}
            </text>
          )}
          <text x={width - padding.right} y={height - 12} fill="#71717a" textAnchor="end">
            {ddSeries[ddSeries.length - 1]?.[0]?.substring(0, 10)}
          </text>
        </svg>

        {hovered && (
          <div className="absolute top-2 right-4 rounded border border-atlas-border-default/80 bg-atlas-surface-2/95 px-3 py-1.5 text-xs shadow-lg backdrop-blur">
            <div className="font-semibold text-atlas-text-primary">{hovered.date.substring(0, 10)}</div>
            <div className="mt-0.5 flex items-center justify-between gap-4 text-atlas-text-secondary">
              <span>Drawdown:</span>
              <span className="font-mono font-medium text-rose-400">
                {formatSignedPercent(hovered.drawdown, 2)}
              </span>
            </div>
            <div className="flex items-center justify-between gap-4 text-atlas-text-secondary">
              <span>Wealth Index:</span>
              <span className="font-mono text-atlas-text-primary">
                {hovered.wealth.toFixed(2)}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

