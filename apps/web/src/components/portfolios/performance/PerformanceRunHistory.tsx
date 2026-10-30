"use client";

import React from "react";
import { formatRate } from "@/lib/portfolios/performance/formatting";
import { PerformanceRunSummaryDTO } from "@/lib/portfolios/performance/types";
import { History, ShieldCheck } from "lucide-react";

interface PerformanceRunHistoryProps {
  runs: PerformanceRunSummaryDTO[];
}

export function PerformanceRunHistory({ runs }: PerformanceRunHistoryProps) {
  if (!runs || runs.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-sm border border-atlas-border-default/60 bg-atlas-surface-1 text-xs text-atlas-text-tertiary">
        No historical calculation runs recorded for this portfolio.
      </div>
    );
  }

  return (
    <div className="rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-4 shadow-xs">
      <div className="border-b border-atlas-border-default/40 pb-2.5">
        <h4 className="text-xs font-semibold text-atlas-text-primary flex items-center gap-1.5">
          <History className="h-4 w-4 text-atlas-accent" />
          Historical Calculation Runs & Audit Trail
        </h4>
        <p className="text-[11px] text-atlas-text-secondary">
          Immutable audit record of all performance runs, parameter states, and cryptographic input hashes.
        </p>
      </div>

      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-atlas-border-default/60 text-[11px] text-atlas-text-tertiary">
              <th className="py-2 pr-3 font-medium">Timestamp (UTC)</th>
              <th className="px-2 py-2 font-medium">Period</th>
              <th className="px-2 py-2 font-medium">Methodology</th>
              <th className="px-2 py-2 text-right font-medium">TWR</th>
              <th className="px-2 py-2 text-right font-medium">MWR (XIRR)</th>
              <th className="px-2 py-2 font-medium">Status</th>
              <th className="py-2 pl-3 font-medium text-right">Input Hash</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/30">
            {runs.map((r) => (
              <tr key={r.run_id} className="hover:bg-atlas-surface-2/40 transition-colors">
                <td className="py-2.5 pr-3 text-atlas-text-secondary whitespace-nowrap">
                  {new Date(r.created_at).toLocaleString()}
                </td>
                <td className="px-2 py-2.5 text-atlas-text-primary whitespace-nowrap font-medium">
                  {r.period_type}
                </td>
                <td className="px-2 py-2.5 text-atlas-text-secondary whitespace-nowrap font-sans text-[11px]">
                  {r.methodology === "EXACT_TWR" ? "Exact Subperiod" : "Modified Dietz"}
                </td>
                <td className="px-2 py-2.5 text-right font-semibold text-atlas-accent whitespace-nowrap">
                  {formatRate(r.twr_cumulative)}
                </td>
                <td className="px-2 py-2.5 text-right font-semibold text-atlas-text-primary whitespace-nowrap">
                  {formatRate(r.mwr_xirr)}
                </td>
                <td className="px-2 py-2.5 whitespace-nowrap">
                  <span className="inline-flex items-center rounded-xs bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-sans font-medium text-emerald-400">
                    {r.status}
                  </span>
                </td>
                <td className="py-2.5 pl-3 text-right text-[11px] text-atlas-text-tertiary whitespace-nowrap">
                  {r.input_hash ? `${r.input_hash.slice(0, 10)}...` : "--"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

