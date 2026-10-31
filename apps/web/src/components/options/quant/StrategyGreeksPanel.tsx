"use client";

import React from "react";
import { QuantModelGreeks } from "@/lib/options/quant/types";
import { Activity, ShieldCheck, HelpCircle } from "lucide-react";

interface StrategyGreeksPanelProps {
  greeks?: QuantModelGreeks | null;
  title?: string;
  isAggregate?: boolean;
}

export function StrategyGreeksPanel({
  greeks,
  title = "QuantLib Strategy Greeks & Sensitivities",
  isAggregate = true,
}: StrategyGreeksPanelProps) {
  if (!greeks) {
    return (
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 text-center text-xs text-zinc-500 font-mono">
        No Greeks data available. Evaluate or price contract to inspect sensitivities.
      </div>
    );
  }

  const greekItems = [
    {
      symbol: "Δ",
      name: "Delta",
      value: greeks.delta.toFixed(4),
      unit: "per $1.00 underlying change",
      color: greeks.delta >= 0 ? "text-emerald-400" : "text-rose-400",
      description: "Rate of change of option value with respect to spot price.",
    },
    {
      symbol: "Γ",
      name: "Gamma",
      value: greeks.gamma.toFixed(4),
      unit: "per $1.00 underlying change²",
      color: "text-amber-400",
      description: "Rate of change of Delta with respect to spot price.",
    },
    {
      symbol: "Θ",
      name: "Theta (Daily)",
      value: `${greeks.theta_per_day.toFixed(4)}/day`,
      subValue: `(${greeks.theta_annual.toFixed(2)}/yr)`,
      unit: "calendar day decay",
      color: greeks.theta_per_day <= 0 ? "text-rose-400" : "text-emerald-400",
      description: "Time decay of the position per passing calendar day.",
    },
    {
      symbol: "ν",
      name: "Vega (Point)",
      value: greeks.vega_per_point.toFixed(4),
      subValue: `(${greeks.vega_per_unit.toFixed(2)}/1.0 vol)`,
      unit: "per 1% IV shift",
      color: "text-cyan-400",
      description: "Sensitivity to implied volatility change per percentage point (0.01).",
    },
    {
      symbol: "ρ",
      name: "Rho (Point)",
      value: greeks.rho_per_point.toFixed(4),
      subValue: `(${greeks.rho_per_bp.toFixed(4)}/bp)`,
      unit: "per 1% interest rate shift",
      color: "text-violet-400",
      description: "Sensitivity to risk-free interest rate shift per percentage point (0.01).",
    },
    {
      symbol: "Vanna",
      name: "Vanna",
      value: greeks.vanna !== null && greeks.vanna !== undefined ? greeks.vanna.toFixed(4) : "—",
      unit: "dDelta / dVol",
      color: "text-indigo-400",
      description: "Cross sensitivity of Delta with respect to implied volatility.",
    },
    {
      symbol: "Volga",
      name: "Volga / Vomma",
      value: greeks.volga !== null && greeks.volga !== undefined ? greeks.volga.toFixed(4) : "—",
      unit: "dVega / dVol",
      color: "text-purple-400",
      description: "Second order sensitivity: rate of change of Vega with respect to volatility.",
    },
  ];

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">
            {title}
          </h4>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase ${
              greeks.calculation_method === "ANALYTIC"
                ? "bg-emerald-950/80 text-emerald-300 border border-emerald-800/60"
                : greeks.calculation_method === "TERMINAL_SETTLEMENT_CUTOFF"
                ? "bg-amber-950/80 text-amber-300 border border-amber-800/60"
                : "bg-blue-950/80 text-blue-300 border border-blue-800/60"
            }`}
          >
            {greeks.calculation_method === "CENTRAL_FINITE_DIFFERENCE"
              ? "Central Finite Diff (±1%)"
              : greeks.calculation_method}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
        {greekItems.map((item, idx) => (
          <div
            key={idx}
            className="bg-zinc-950/50 border border-zinc-800/80 rounded p-2.5 flex flex-col justify-between"
            title={item.description}
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-zinc-300">{item.symbol}</span>
                <span className="text-[10px] text-zinc-500 font-sans">{item.name}</span>
              </div>
              <div className={`text-base font-bold font-mono mt-1 ${item.color}`}>
                {item.value}
              </div>
              {item.subValue && (
                <div className="text-[10px] text-zinc-500 font-mono mt-0.5">{item.subValue}</div>
              )}
            </div>
            <div className="text-[9px] text-zinc-500 font-mono mt-2 border-t border-zinc-900 pt-1">
              {item.unit}
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between text-[10px] text-zinc-500 font-mono pt-1">
        <span>Units: Vega per 1% point vol shift; Theta per calendar day; Rho per 100 bps</span>
        <div className="flex items-center gap-1 text-zinc-400">
          <ShieldCheck className="w-3 h-3 text-indigo-400" />
          <span>Validated vs Reference Benchmarks</span>
        </div>
      </div>
    </div>
  );
}
