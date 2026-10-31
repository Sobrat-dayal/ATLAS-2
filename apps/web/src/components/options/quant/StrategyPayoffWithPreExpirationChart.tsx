"use client";

import React, { useMemo } from "react";
import { PayoffCoordinate, PreExpirationValuationPoint } from "@/lib/options/quant/types";
import { TrendingUp, Info } from "lucide-react";

interface StrategyPayoffWithPreExpirationChartProps {
  expirationCurve: PayoffCoordinate[];
  preExpirationCurve?: PreExpirationValuationPoint[] | null;
  currentSpot: number;
  breakEvenPoints: number[];
  maxProfit?: number | null;
  maxLoss?: number | null;
  isUnboundedLoss?: boolean;
}

export function StrategyPayoffWithPreExpirationChart({
  expirationCurve,
  preExpirationCurve,
  currentSpot,
  breakEvenPoints,
  maxProfit,
  maxLoss,
  isUnboundedLoss = false,
}: StrategyPayoffWithPreExpirationChartProps) {
  // Compute bounds for responsive SVG scaling
  const chartMetrics = useMemo(() => {
    if (!expirationCurve || expirationCurve.length === 0) return null;

    let minX = Infinity;
    let maxX = -Infinity;
    let minY = Infinity;
    let maxY = -Infinity;

    for (const pt of expirationCurve) {
      if (pt.underlying_price < minX) minX = pt.underlying_price;
      if (pt.underlying_price > maxX) maxX = pt.underlying_price;
      if (pt.payoff < minY) minY = pt.payoff;
      if (pt.payoff > maxY) maxY = pt.payoff;
    }

    if (preExpirationCurve && preExpirationCurve.length > 0) {
      for (const pt of preExpirationCurve) {
        if (pt.pre_expiration_npv < minY) minY = pt.pre_expiration_npv;
        if (pt.pre_expiration_npv > maxY) maxY = pt.pre_expiration_npv;
      }
    }

    // Always include zero line and current spot in view
    if (minY > 0) minY = -100;
    if (maxY < 0) maxY = 100;
    if (currentSpot < minX) minX = currentSpot * 0.95;
    if (currentSpot > maxX) maxX = currentSpot * 1.05;

    // Pad Y axis slightly
    const yRange = maxY - minY || 100;
    minY -= yRange * 0.08;
    maxY += yRange * 0.08;

    const xRange = maxX - minX || 100;

    return { minX, maxX, minY, maxY, xRange, yRange };
  }, [expirationCurve, preExpirationCurve, currentSpot]);

  if (!chartMetrics) {
    return (
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-6 text-center text-xs text-zinc-500 font-mono">
        Add strategy legs to render expiration and pre-expiration payoff curves.
      </div>
    );
  }

  const { minX, maxX, minY, maxY, xRange, yRange } = chartMetrics;

  // Chart dimensions in SVG viewBox coordinate space
  const svgWidth = 800;
  const svgHeight = 360;
  const padLeft = 60;
  const padRight = 30;
  const padTop = 30;
  const padBottom = 40;

  const plotWidth = svgWidth - padLeft - padRight;
  const plotHeight = svgHeight - padTop - padBottom;

  const toSvgX = (x: number) => padLeft + ((x - minX) / xRange) * plotWidth;
  const toSvgY = (y: number) => padTop + plotHeight - ((y - minY) / yRange) * plotHeight;

  // Generate SVG path for expiration payoff curve
  const expirationPath = expirationCurve
    .map((pt, i) => `${i === 0 ? "M" : "L"} ${toSvgX(pt.underlying_price).toFixed(1)} ${toSvgY(pt.payoff).toFixed(1)}`)
    .join(" ");

  // Generate SVG path for pre-expiration mark-to-market curve
  const preExpirationPath =
    preExpirationCurve && preExpirationCurve.length > 0
      ? preExpirationCurve
          .map(
            (pt, i) =>
              `${i === 0 ? "M" : "L"} ${toSvgX(pt.underlying_price).toFixed(1)} ${toSvgY(
                pt.pre_expiration_npv
              ).toFixed(1)}`
          )
          .join(" ")
      : null;

  const zeroY = toSvgY(0);
  const spotX = toSvgX(currentSpot);

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800 pb-2.5">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">
            Strategy Payoff & Pre-Expiration Valuation (QuantLib)
          </h4>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-[11px] font-mono">
          <div className="flex items-center gap-1.5 text-zinc-300">
            <span className="w-4 h-0.5 bg-emerald-400 inline-block" />
            <span>At Expiration (T = Expiry)</span>
          </div>
          {preExpirationPath && (
            <div className="flex items-center gap-1.5 text-indigo-400">
              <span className="w-4 h-0.5 border-t-2 border-dashed border-indigo-400 inline-block" />
              <span>Mark-to-Market (t &lt; T)</span>
            </div>
          )}
          <div className="flex items-center gap-1.5 text-amber-400">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
            <span>Spot (${currentSpot.toFixed(2)})</span>
          </div>
        </div>
      </div>

      <div className="relative w-full aspect-[20/9] bg-zinc-950/70 rounded border border-zinc-850 p-1">
        <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-full">
          {/* Zero P&L horizontal reference line */}
          <line
            x1={padLeft}
            y1={zeroY}
            x2={svgWidth - padRight}
            y2={zeroY}
            stroke="#52525b"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />
          <text
            x={padLeft - 8}
            y={zeroY + 4}
            fill="#a1a1aa"
            fontSize="10"
            fontFamily="monospace"
            textAnchor="end"
          >
            $0
          </text>

          {/* Current Spot Price vertical marker */}
          <line
            x1={spotX}
            y1={padTop}
            x2={spotX}
            y2={svgHeight - padBottom}
            stroke="#f59e0b"
            strokeWidth="1.5"
            strokeDasharray="3 3"
          />
          <text
            x={spotX}
            y={padTop - 6}
            fill="#fbbf24"
            fontSize="10"
            fontFamily="monospace"
            textAnchor="middle"
          >
            Spot ${currentSpot.toFixed(2)}
          </text>

          {/* Break-even vertical markers */}
          {breakEvenPoints.map((be, idx) => {
            const beX = toSvgX(be);
            if (beX < padLeft || beX > svgWidth - padRight) return null;
            return (
              <g key={idx}>
                <line
                  x1={beX}
                  y1={zeroY - 12}
                  x2={beX}
                  y2={zeroY + 12}
                  stroke="#38bdf8"
                  strokeWidth="2"
                />
                <circle cx={beX} cy={zeroY} r="3.5" fill="#38bdf8" />
                <text
                  x={beX}
                  y={svgHeight - padBottom + 16}
                  fill="#7dd3fc"
                  fontSize="10"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  BE ${be.toFixed(2)}
                </text>
              </g>
            );
          })}

          {/* Pre-Expiration Mark-to-Market Curve (t < T) */}
          {preExpirationPath && (
            <path
              d={preExpirationPath}
              fill="none"
              stroke="#818cf8"
              strokeWidth="2.5"
              strokeDasharray="6 4"
            />
          )}

          {/* Expiration Payoff Curve (T = Expiry) */}
          <path d={expirationPath} fill="none" stroke="#34d399" strokeWidth="2.5" />

          {/* Min / Max labels on Y-axis */}
          <text
            x={padLeft - 8}
            y={padTop + 10}
            fill="#71717a"
            fontSize="10"
            fontFamily="monospace"
            textAnchor="end"
          >
            ${maxY.toFixed(0)}
          </text>
          <text
            x={padLeft - 8}
            y={svgHeight - padBottom}
            fill="#71717a"
            fontSize="10"
            fontFamily="monospace"
            textAnchor="end"
          >
            ${minY.toFixed(0)}
          </text>

          {/* Underlying prices on X-axis */}
          <text
            x={padLeft}
            y={svgHeight - padBottom + 16}
            fill="#71717a"
            fontSize="10"
            fontFamily="monospace"
            textAnchor="start"
          >
            ${minX.toFixed(0)}
          </text>
          <text
            x={svgWidth - padRight}
            y={svgHeight - padBottom + 16}
            fill="#71717a"
            fontSize="10"
            fontFamily="monospace"
            textAnchor="end"
          >
            ${maxX.toFixed(0)}
          </text>
        </svg>
      </div>

      {/* Summary KPI Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
        <div className="bg-zinc-950/60 border border-zinc-800/80 rounded p-2.5">
          <span className="text-[10px] text-zinc-500 font-mono uppercase">Max Profit</span>
          <div className="text-base font-bold font-mono text-emerald-400 mt-0.5">
            {maxProfit !== null && maxProfit !== undefined ? `$${maxProfit.toFixed(2)}` : "Uncapped"}
          </div>
        </div>

        <div className="bg-zinc-950/60 border border-zinc-800/80 rounded p-2.5">
          <span className="text-[10px] text-zinc-500 font-mono uppercase">Max Loss</span>
          <div className="text-base font-bold font-mono text-rose-400 mt-0.5">
            {isUnboundedLoss ? (
              <span className="text-rose-400">Unbounded (Naked)</span>
            ) : maxLoss !== null && maxLoss !== undefined ? (
              `$${maxLoss.toFixed(2)}`
            ) : (
              "—"
            )}
          </div>
        </div>

        <div className="bg-zinc-950/60 border border-zinc-800/80 rounded p-2.5">
          <span className="text-[10px] text-zinc-500 font-mono uppercase">Break-Even(s)</span>
          <div className="text-base font-bold font-mono text-cyan-300 mt-0.5">
            {breakEvenPoints.length > 0
              ? breakEvenPoints.map((b) => `$${b.toFixed(2)}`).join(", ")
              : "None"}
          </div>
        </div>

        <div className="bg-zinc-950/60 border border-zinc-800/80 rounded p-2.5">
          <span className="text-[10px] text-zinc-500 font-mono uppercase">Risk Status</span>
          <div className="text-base font-bold font-mono text-zinc-200 mt-0.5">
            {isUnboundedLoss ? "Capped Profit / Infinite Loss" : "Defined Risk"}
          </div>
        </div>
      </div>
    </div>
  );
}

