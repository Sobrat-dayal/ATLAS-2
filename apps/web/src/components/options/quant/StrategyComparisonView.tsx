"use client";

import React from "react";
import { GitCompare, AlertTriangle, ShieldCheck, Check, Info } from "lucide-react";
import { StrategyComparisonItem } from "@/lib/options/quant/types";

interface StrategyComparisonViewProps {
  comparisonItems: StrategyComparisonItem[];
  isLoading?: boolean;
}

export function StrategyComparisonView({
  comparisonItems,
  isLoading = false,
}: StrategyComparisonViewProps) {
  if (isLoading) {
    return (
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-6 text-center text-xs text-zinc-400 font-mono">
        Comparing derivatives strategies across risk-return profiles...
      </div>
    );
  }

  if (!comparisonItems || comparisonItems.length === 0) {
    return (
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-6 text-center text-xs text-zinc-500 font-mono">
        Add multiple strategy definitions to compare risk-return profiles, Greeks, and break-evens.
      </div>
    );
  }

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2.5">
        <div className="flex items-center gap-2">
          <GitCompare className="w-4 h-4 text-indigo-400" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">
            Multi-Strategy Comparative Analysis
          </h4>
        </div>
        <span className="text-[10px] text-zinc-500 font-mono">
          {comparisonItems.length} Strategies Evaluated
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs font-mono border-collapse min-w-[650px]">
          <thead>
            <tr className="border-b border-zinc-800 text-[11px] text-zinc-400 text-left bg-zinc-950/40">
              <th className="p-2.5">Strategy</th>
              <th className="p-2.5">Net Flow</th>
              <th className="p-2.5">Max Profit</th>
              <th className="p-2.5">Max Loss</th>
              <th className="p-2.5">Break-Even(s)</th>
              <th className="p-2.5">RoR Ratio</th>
              <th className="p-2.5">Net Greeks (Δ / Γ / ν / Θ)</th>
              <th className="p-2.5">Risk Profile</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-850">
            {comparisonItems.map((item) => {
              const isDebit = item.net_debit_credit < 0;
              const isCredit = item.net_debit_credit > 0;

              return (
                <tr key={item.strategy_id} className="hover:bg-zinc-850/40 transition-colors">
                  <td className="p-2.5 font-semibold text-zinc-200">
                    <div className="text-sm">{item.strategy_name}</div>
                    <div className="text-[10px] text-zinc-500 font-normal">{item.strategy_id}</div>
                  </td>

                  <td className="p-2.5">
                    <span
                      className={`font-semibold ${
                        isDebit ? "text-rose-400" : isCredit ? "text-emerald-400" : "text-zinc-300"
                      }`}
                    >
                      {isDebit
                        ? `Debit ($${Math.abs(item.net_debit_credit).toFixed(2)})`
                        : isCredit
                        ? `Credit ($${item.net_debit_credit.toFixed(2)})`
                        : "Even"}
                    </span>
                  </td>

                  <td className="p-2.5 font-semibold text-emerald-400">
                    {item.max_profit !== null && item.max_profit !== undefined
                      ? `$${item.max_profit.toFixed(2)}`
                      : "Uncapped"}
                  </td>

                  <td className="p-2.5 font-semibold text-rose-400">
                    {item.unbounded_risk ? (
                      <span className="flex items-center gap-1 text-rose-400">
                        <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                        Unbounded
                      </span>
                    ) : item.max_loss !== null && item.max_loss !== undefined ? (
                      `$${item.max_loss.toFixed(2)}`
                    ) : (
                      "—"
                    )}
                  </td>

                  <td className="p-2.5 text-zinc-300">
                    {item.break_even_points.length > 0
                      ? item.break_even_points.map((b) => `$${b.toFixed(2)}`).join(", ")
                      : "None"}
                  </td>

                  <td className="p-2.5 font-semibold text-zinc-200">
                    {item.return_on_risk_ratio !== null && item.return_on_risk_ratio !== undefined
                      ? `${item.return_on_risk_ratio.toFixed(2)}x`
                      : "—"}
                  </td>

                  <td className="p-2.5 text-zinc-400 font-mono text-[11px]">
                    <div className="flex items-center gap-2">
                      <span className={item.net_delta >= 0 ? "text-emerald-400" : "text-rose-400"}>
                        Δ {item.net_delta.toFixed(2)}
                      </span>
                      <span className="text-amber-400">Γ {item.net_gamma.toFixed(3)}</span>
                      <span className="text-cyan-400">ν {item.net_vega.toFixed(2)}</span>
                      <span className="text-purple-400">Θ {item.net_theta.toFixed(2)}</span>
                    </div>
                  </td>

                  <td className="p-2.5">
                    {item.unbounded_risk ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-rose-950/80 text-rose-300 border border-rose-800/60 flex items-center gap-1 w-max">
                        <AlertTriangle className="w-3 h-3 text-rose-400" />
                        Naked Risk
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-950/80 text-emerald-300 border border-emerald-800/60 flex items-center gap-1 w-max">
                        <ShieldCheck className="w-3 h-3 text-emerald-400" />
                        Defined Risk
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
