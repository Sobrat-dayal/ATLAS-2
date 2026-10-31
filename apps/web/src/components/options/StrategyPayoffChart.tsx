"use client";

import React, { useState } from "react";
import { PayoffCoordinate } from "@/lib/options/types";
import { formatCurrency } from "@/lib/options/formatters";

interface StrategyPayoffChartProps {
  coordinates: PayoffCoordinate[];
  breakevens: number[];
  currency?: string;
  maxProfit?: number | null;
  maxLoss?: number | null;
  isUnboundedProfit?: boolean;
  isUnboundedLoss?: boolean;
}

export function StrategyPayoffChart({
  coordinates,
  breakevens,
  currency = "USD",
  maxProfit,
  maxLoss,
  isUnboundedProfit,
  isUnboundedLoss,
}: StrategyPayoffChartProps) {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!coordinates || coordinates.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-zinc-900/40 rounded-lg border border-zinc-800 text-xs text-zinc-500">
        Add strategy legs or select a template to visualize the expiration payoff diagram.
      </div>
    );
  }

  const prices = coordinates.map((c) => c.underlying_price);
  const payoffs = coordinates.map((c) => c.payoff);

  const minX = Math.min(...prices);
  const maxX = Math.max(...prices);
  let minY = Math.min(0, ...payoffs);
  let maxY = Math.max(0, ...payoffs);

  // Add margin to Y axis
  const ySpan = Math.max(maxY - minY, 100);
  minY -= ySpan * 0.1;
  maxY += ySpan * 0.1;

  const width = 700;
  const height = 300;
  const padding = { top: 20, right: 30, bottom: 40, left: 60 };

  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  const scaleX = (price: number) =>
    padding.left + ((price - minX) / (maxX - minX || 1)) * plotW;

  const scaleY = (payoff: number) =>
    padding.top + (1 - (payoff - minY) / (maxY - minY || 1)) * plotH;

  const zeroY = scaleY(0);

  // Build SVG path points
  const pointsStr = coordinates
    .map((c) => `${scaleX(c.underlying_price)},${scaleY(c.payoff)}`)
    .join(" ");

  const hoverCoord = hoverIndex !== null ? coordinates[hoverIndex] : null;

  return (
    <div className="relative w-full bg-zinc-900/60 border border-zinc-800 rounded-lg p-3">
      <div className="flex items-center justify-between text-xs mb-2">
        <span className="font-bold text-zinc-300">Expiration Payoff Profile (T = Expiration Cutoff)</span>
        <div className="flex items-center gap-4 text-[11px]">
          <div>
            <span className="text-zinc-500">Max Profit: </span>
            <span className="font-mono font-bold text-emerald-400">
              {isUnboundedProfit ? "∞ (Unbounded)" : maxProfit !== null && maxProfit !== undefined ? formatCurrency(maxProfit, currency) : "—"}
            </span>
          </div>
          <div>
            <span className="text-zinc-500">Max Loss: </span>
            <span className="font-mono font-bold text-rose-400">
              {isUnboundedLoss ? "∞ (Unbounded Risk)" : maxLoss !== null && maxLoss !== undefined ? formatCurrency(-Math.abs(maxLoss), currency) : "—"}
            </span>
          </div>
        </div>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto overflow-visible select-none"
        onMouseLeave={() => setHoverIndex(null)}
      >
        {/* Shaded Areas: Profit above zero line, Loss below zero line */}
        <defs>
          <linearGradient id="profitGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
          </linearGradient>
          <linearGradient id="lossGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.0" />
            <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.25" />
          </linearGradient>
        </defs>

        {/* Zero baseline */}
        <line
          x1={padding.left}
          y1={zeroY}
          x2={width - padding.right}
          y2={zeroY}
          stroke="#52525b"
          strokeWidth="1.5"
          strokeDasharray="4 2"
        />
        <text
          x={padding.left - 8}
          y={zeroY + 4}
          textAnchor="end"
          className="text-[10px] font-mono fill-zinc-500"
        >
          $0
        </text>

        {/* Breakeven Vertical Lines */}
        {breakevens.map((be) => {
          const bx = scaleX(be);
          if (bx < padding.left || bx > width - padding.right) return null;
          return (
            <g key={be}>
              <line
                x1={bx}
                y1={padding.top}
                x2={bx}
                y2={height - padding.bottom}
                stroke="#eab308"
                strokeWidth="1"
                strokeDasharray="3 3"
              />
              <text
                x={bx}
                y={padding.top - 5}
                textAnchor="middle"
                className="text-[9px] font-mono fill-amber-400 font-bold"
              >
                BE: {formatCurrency(be, currency)}
              </text>
            </g>
          );
        })}

        {/* The Payoff Curve Line */}
        <polyline
          fill="none"
          stroke="#06b6d4"
          strokeWidth="2.5"
          points={pointsStr}
        />

        {/* Interactive Hover Hit Zones */}
        {coordinates.map((coord, idx) => {
          const cx = scaleX(coord.underlying_price);
          const cy = scaleY(coord.payoff);
          return (
            <circle
              key={idx}
              cx={cx}
              cy={cy}
              r="6"
              className="fill-transparent hover:fill-cyan-400/40 cursor-crosshair transition-colors"
              onMouseEnter={() => setHoverIndex(idx)}
            />
          );
        })}

        {/* Active Hover Marker */}
        {hoverCoord && (
          <g>
            <circle
              cx={scaleX(hoverCoord.underlying_price)}
              cy={scaleY(hoverCoord.payoff)}
              r="5"
              className={hoverCoord.payoff >= 0 ? "fill-emerald-400" : "fill-rose-400"}
              stroke="#ffffff"
              strokeWidth="2"
            />
            <line
              x1={scaleX(hoverCoord.underlying_price)}
              y1={padding.top}
              x2={scaleX(hoverCoord.underlying_price)}
              y2={height - padding.bottom}
              stroke="#71717a"
              strokeWidth="1"
              strokeDasharray="2 2"
            />
          </g>
        )}

        {/* X Axis Ticks */}
        {coordinates
          .filter((_, i) => i % Math.max(1, Math.floor(coordinates.length / 6)) === 0)
          .map((coord, i) => {
            const x = scaleX(coord.underlying_price);
            return (
              <g key={i}>
                <line
                  x1={x}
                  y1={height - padding.bottom}
                  x2={x}
                  y2={height - padding.bottom + 5}
                  stroke="#3f3f46"
                />
                <text
                  x={x}
                  y={height - padding.bottom + 18}
                  textAnchor="middle"
                  className="text-[10px] font-mono fill-zinc-400"
                >
                  {coord.underlying_price.toFixed(1)}
                </text>
              </g>
            );
          })}
      </svg>

      {/* Hover Readout Tooltip */}
      {hoverCoord && (
        <div className="absolute top-12 left-20 bg-zinc-950/90 border border-zinc-700 rounded p-2 text-xs font-mono shadow-lg pointer-events-none">
          <div className="text-zinc-400">
            Settlement Price:{" "}
            <span className="text-white font-bold">
              {formatCurrency(hoverCoord.underlying_price, currency)}
            </span>
          </div>
          <div className="mt-0.5">
            P&L at Expiration:{" "}
            <span
              className={`font-bold ${
                hoverCoord.payoff >= 0 ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {formatCurrency(hoverCoord.payoff, currency)}
            </span>
            {hoverCoord.is_breakeven && (
              <span className="ml-1 text-[10px] text-amber-300 font-sans font-semibold">
                (Breakeven)
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

