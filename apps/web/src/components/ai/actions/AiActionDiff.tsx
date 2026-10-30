"use client";

import React from "react";
import { ActionDiffDTO } from "@/lib/ai/actions/types";

interface AiActionDiffProps {
  diffs: ActionDiffDTO[];
}

export function AiActionDiff({ diffs }: AiActionDiffProps) {
  if (!diffs || diffs.length === 0) {
    return (
      <div className="text-xs text-neutral-500 italic p-2 border border-neutral-800 rounded bg-neutral-900/40">
        No state field modifications detected.
      </div>
    );
  }

  return (
    <div className="border border-neutral-800 rounded overflow-hidden text-xs">
      <table className="w-full text-left border-collapse">
        <thead className="bg-neutral-900 text-neutral-400 font-medium border-b border-neutral-800">
          <tr>
            <th className="px-3 py-1.5">Field</th>
            <th className="px-3 py-1.5">Current Value</th>
            <th className="px-3 py-1.5">Proposed Value</th>
            <th className="px-3 py-1.5">Financial Delta / Impact</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-850">
          {diffs.map((d, idx) => (
            <tr key={`${d.field_path}-${idx}`} className="hover:bg-neutral-850/30 transition-colors">
              <td className="px-3 py-1.5 font-mono text-neutral-300">
                {d.field_path}
              </td>
              <td className="px-3 py-1.5 font-mono text-neutral-400">
                {typeof d.before_value === "object"
                  ? JSON.stringify(d.before_value)
                  : String(d.before_value ?? "—")}
              </td>
              <td className="px-3 py-1.5 font-mono text-emerald-400 font-semibold">
                {typeof d.after_value === "object"
                  ? JSON.stringify(d.after_value)
                  : String(d.after_value)}
              </td>
              <td className="px-3 py-1.5 text-neutral-300">
                {d.financial_impact_if_computable ? (
                  <span className="inline-block px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium">
                    {d.financial_impact_if_computable}
                  </span>
                ) : (
                  <span className="text-neutral-500">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

