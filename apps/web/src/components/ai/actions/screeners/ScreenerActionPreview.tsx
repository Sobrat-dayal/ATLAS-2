"use client";

import React from "react";
import { ActionDTO } from "@/lib/ai/actions/types";

interface ScreenerActionPreviewProps {
  action: ActionDTO;
}

export function ScreenerActionPreview({ action }: ScreenerActionPreviewProps) {
  const args = action.proposed_arguments;
  const filters: Array<{ metric_id: string; operator: string; value: any }> =
    args.filters || [];

  return (
    <div className="space-y-3 text-xs">
      <div className="flex flex-wrap items-center gap-2">
        <span className="px-2 py-1 rounded bg-neutral-900 border border-neutral-800 text-neutral-300">
          <strong className="text-neutral-500 font-semibold uppercase text-[10px] mr-1.5">Universe:</strong>
          <span className="font-mono text-cyan-400">{args.universe || "IN_NIFTY500"}</span>
        </span>
        <span className="px-2 py-1 rounded bg-neutral-900 border border-neutral-800 text-neutral-300">
          <strong className="text-neutral-500 font-semibold uppercase text-[10px] mr-1.5">Active Rules:</strong>
          <span>{filters.length}</span>
        </span>
      </div>

      {filters.length > 0 && (
        <div className="border border-neutral-800 rounded overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-neutral-900 text-neutral-400 font-medium border-b border-neutral-800">
              <tr>
                <th className="px-3 py-1.5">Financial Metric</th>
                <th className="px-3 py-1.5">Condition</th>
                <th className="px-3 py-1.5">Threshold Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-850">
              {filters.map((f, idx) => (
                <tr key={idx} className="hover:bg-neutral-850/30">
                  <td className="px-3 py-1.5 font-mono text-neutral-200">{f.metric_id}</td>
                  <td className="px-3 py-1.5 font-mono text-neutral-400">{f.operator}</td>
                  <td className="px-3 py-1.5 font-mono text-emerald-400 font-semibold">
                    {typeof f.value === "number" && f.value > 1000000
                      ? f.value.toLocaleString()
                      : String(f.value)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

