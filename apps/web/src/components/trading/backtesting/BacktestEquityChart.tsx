"use client";

import React, { useState } from "react";
import { EquitySnapshot } from "@/lib/trading/backtesting/types";
import { formatCurrency, formatPercent } from "@/lib/trading/backtesting/formatters";
import { LineChart, BarChart3, TrendingDown } from "lucide-react";

interface BacktestEquityChartProps {
  equityCurve: EquitySnapshot[];
  initialCash: number;
}

export function BacktestEquityChart({ equityCurve, initialCash }: BacktestEquityChartProps) {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 text-center text-neutral-400">
        <LineChart className="w-10 h-10 mx-auto text-neutral-600 mb-2" />
        <p className="text-sm">No historical simulation snapshots available.</p>
      </div>
    );
  }

  // Dimensions
  const width = 800;
  const heightUpper = 260;
  const heightLower = 100;
  const padding = { top: 20, right: 30, bottom: 25, left: 65 };

  // Calculate scales
  const equities = equityCurve.map((d) => d.equity);
  const minEq = Math.min(...equities, initialCash) * 0.98;
  const maxEq = Math.max(...equities, initialCash) * 1.02;
  const maxEqRange = maxEq - minEq || 1;

  const drawdowns = equityCurve.map((d) => d.drawdown_pct);
  const maxDd = Math.max(...drawdowns, 5.0) * 1.1; // at least 5% scale

  const getX = (idx: number) =>
    padding.left +
    (idx / (equityCurve.length - 1 || 1)) * (width - padding.left - padding.right);

  const getUpperY = (val: number) =>
    heightUpper -
    padding.bottom -
    ((val - minEq) / maxEqRange) * (heightUpper - padding.top - padding.bottom);

  const getLowerY = (ddPct: number) =>
    padding.top + (ddPct / maxDd) * (heightLower - padding.top - padding.bottom);

  // Build SVG Paths
  const equityPoints = equityCurve
    .map((d, i) => `${getX(i).toFixed(1)},${getUpperY(d.equity).toFixed(1)}`)
    .join(" ");

  const equityAreaPath = `M ${getX(0)},${heightUpper - padding.bottom} ${equityCurve
    .map((d, i) => `L ${getX(i).toFixed(1)},${getUpperY(d.equity).toFixed(1)}`)
    .join(" ")} L ${getX(equityCurve.length - 1)},${heightUpper - padding.bottom} Z`;

  const drawdownAreaPath = `M ${getX(0)},${padding.top} ${equityCurve
    .map((d, i) => `L ${getX(i).toFixed(1)},${getLowerY(d.drawdown_pct).toFixed(1)}`)
    .join(" ")} L ${getX(equityCurve.length - 1)},${padding.top} Z`;

  const activePoint = hoverIndex !== null ? equityCurve[hoverIndex] : equityCurve[equityCurve.length - 1];

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 text-neutral-200">
      {/* Header with active snapshot information */}
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-neutral-800 mb-4 gap-2">
        <div className="flex items-center gap-2">
          <LineChart className="w-5 h-5 text-amber-400" />
          <h3 className="text-sm font-semibold tracking-wide">
            Portfolio Equity Curve & Underwater Drawdowns
          </h3>
        </div>

        {activePoint && (
          <div className="flex items-center gap-4 text-xs font-mono bg-neutral-950/80 px-3 py-1.5 rounded-lg border border-neutral-800">
            <span className="text-neutral-400">{activePoint.timestamp}</span>
            <span className="text-neutral-300">
              Equity:{" "}
              <strong
                className={
                  activePoint.equity >= initialCash ? "text-emerald-400" : "text-rose-400"
                }
              >
                {formatCurrency(activePoint.equity)}
              </strong>
            </span>
            <span className="text-neutral-400">
              Cash: <strong className="text-neutral-200">{formatCurrency(activePoint.cash)}</strong>
            </span>
            <span className="text-rose-400">
              DD: <strong>-{activePoint.drawdown_pct.toFixed(2)}%</strong>
            </span>
          </div>
        )}
      </div>

      {/* Upper Panel: Equity Curve SVG */}
      <div className="relative">
        <svg
          viewBox={`0 0 ${width} ${heightUpper}`}
          className="w-full h-auto overflow-visible select-none"
          onMouseLeave={() => setHoverIndex(null)}
        >
          <defs>
            <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
            const val = minEq + pct * maxEqRange;
            const y = getUpperY(val);
            return (
              <g key={pct}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#262626"
                  strokeDasharray="2,2"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  textAnchor="end"
                  fontSize="9"
                  fill="#737373"
                  className="font-mono"
                >
                  ${(val / 1000).toFixed(0)}k
                </text>
              </g>
            );
          })}

          {/* Initial Cash Benchmark Line */}
          <line
            x1={padding.left}
            y1={getUpperY(initialCash)}
            x2={width - padding.right}
            y2={getUpperY(initialCash)}
            stroke="#525252"
            strokeDasharray="4,4"
          />

          {/* Equity Gradient Area */}
          <path d={equityAreaPath} fill="url(#eqGrad)" />

          {/* Equity Line */}
          <polyline
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={equityPoints}
          />

          {/* Hover Crosshair */}
          {hoverIndex !== null && (
            <g>
              <line
                x1={getX(hoverIndex)}
                y1={padding.top}
                x2={getX(hoverIndex)}
                y2={heightUpper - padding.bottom}
                stroke="#f59e0b"
                strokeWidth="1"
                strokeDasharray="2,2"
              />
              <circle
                cx={getX(hoverIndex)}
                cy={getUpperY(equityCurve[hoverIndex].equity)}
                r="4"
                fill="#f59e0b"
                stroke="#18181b"
                strokeWidth="2"
              />
            </g>
          )}

          {/* Invisible hover triggers */}
          {equityCurve.map((_, i) => (
            <rect
              key={i}
              x={getX(i) - (width / equityCurve.length) / 2}
              y={padding.top}
              width={width / equityCurve.length}
              height={heightUpper - padding.bottom - padding.top}
              fill="transparent"
              onMouseEnter={() => setHoverIndex(i)}
            />
          ))}
        </svg>
      </div>

      {/* Lower Panel: Underwater Drawdown Chart */}
      <div className="mt-2 pt-2 border-t border-neutral-800">
        <div className="flex items-center justify-between text-[11px] font-mono text-neutral-500 mb-1">
          <span className="flex items-center gap-1 text-rose-400">
            <TrendingDown className="w-3.5 h-3.5" /> Underwater Drawdown Profile
          </span>
          <span>Peak Trough Scale (0% to -{maxDd.toFixed(1)}%)</span>
        </div>

        <svg viewBox={`0 0 ${width} ${heightLower}`} className="w-full h-auto overflow-visible select-none">
          <defs>
            <linearGradient id="ddGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.0" />
              <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.3" />
            </linearGradient>
          </defs>

          {/* Baseline 0% line */}
          <line
            x1={padding.left}
            y1={padding.top}
            x2={width - padding.right}
            y2={padding.top}
            stroke="#525252"
          />

          {/* Drawdown Area */}
          <path d={drawdownAreaPath} fill="url(#ddGrad)" />

          {/* Drawdown Line */}
          <polyline
            fill="none"
            stroke="#f43f5e"
            strokeWidth="1.5"
            points={equityCurve
              .map((d, i) => `${getX(i).toFixed(1)},${getLowerY(d.drawdown_pct).toFixed(1)}`)
              .join(" ")}
          />

          {/* Drawdown Y-Axis labels */}
          <text
            x={padding.left - 8}
            y={padding.top + 3}
            textAnchor="end"
            fontSize="9"
            fill="#737373"
            className="font-mono"
          >
            0%
          </text>
          <text
            x={padding.left - 8}
            y={heightLower - padding.bottom}
            textAnchor="end"
            fontSize="9"
            fill="#737373"
            className="font-mono"
          >
            -{maxDd.toFixed(0)}%
          </text>

          {/* Date Axis labels */}
          <text
            x={padding.left}
            y={heightLower - 5}
            textAnchor="start"
            fontSize="9"
            fill="#737373"
            className="font-mono"
          >
            {equityCurve[0].timestamp.split(" ")[0]}
          </text>
          <text
            x={width - padding.right}
            y={heightLower - 5}
            textAnchor="end"
            fontSize="9"
            fill="#737373"
            className="font-mono"
          >
            {equityCurve[equityCurve.length - 1].timestamp.split(" ")[0]}
          </text>
        </svg>
      </div>
    </div>
  );
}

