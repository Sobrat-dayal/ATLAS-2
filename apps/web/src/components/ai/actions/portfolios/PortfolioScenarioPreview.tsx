"use client";

import React from "react";
import { ActionDTO } from "@/lib/ai/actions/types";

interface PortfolioScenarioPreviewProps {
  action: ActionDTO;
}

export function PortfolioScenarioPreview({ action }: PortfolioScenarioPreviewProps) {
  const args = action.proposed_arguments;
  const targetWeights: Record<string, number> = args.target_weights || {};

  return (
    <div className="space-y-3 text-xs">
      {/* Strict Stage 128 Institutional Guardrail Disclaimer */}
      <div className="p-3 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-300 space-y-1">
        <div className="flex items-center gap-2 font-semibold">
          <span>⚠</span>
          <span>Hypothetical Allocation Proposal — Not Executed</span>
        </div>
        <p className="text-[11px] text-amber-200/80 leading-relaxed">
          Stage 128 strictly enforces analytical simulation only. Zero broker orders will be
          submitted. Actual cash balances, position ledgers, and transaction accounting remain unmodified.
        </p>
      </div>

      <div className="border border-neutral-800 rounded overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-neutral-900 text-neutral-400 font-medium border-b border-neutral-800">
            <tr>
              <th className="px-3 py-1.5">Asset / Sector</th>
              <th className="px-3 py-1.5">Proposed Target Weight</th>
              <th className="px-3 py-1.5">Target Allocation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-850">
            {Object.entries(targetWeights).map(([asset, weight]) => (
              <tr key={asset} className="hover:bg-neutral-850/30">
                <td className="px-3 py-1.5 font-medium text-neutral-200">{asset}</td>
                <td className="px-3 py-1.5 font-mono text-emerald-400 font-semibold">
                  {(weight * 100).toFixed(1)}%
                </td>
                <td className="px-3 py-1.5">
                  <div className="w-32 bg-neutral-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full"
                      style={{ width: `${Math.min(100, Math.max(0, weight * 100))}%` }}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

