"use client";

import React from "react";
import { AnalyticalObservationRow } from "@/lib/research/types";
import { formatPercentageDelta } from "@/lib/research/formatting";
import { Badge } from "@/design-system";

interface AnalysisResultsTableProps {
  observations: AnalyticalObservationRow[];
  currency?: string | null;
  unit?: string;
  onOpenSource?: (sourceId: string) => void;
}

export function AnalysisResultsTable({
  observations,
  onOpenSource,
}: AnalysisResultsTableProps) {
  if (observations.length === 0) {
    return (
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-6 text-center text-xs text-atlas-text-muted">
        No observation records in this analysis run result.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-sm border border-atlas-border-default bg-atlas-surface-0">
      <table className="w-full text-left text-xs">
        <thead className="border-b border-atlas-border-default bg-atlas-surface-1 font-mono text-[11px] text-atlas-text-secondary uppercase">
          <tr>
            <th className="px-3 py-2.5">Period</th>
            <th className="px-3 py-2.5">Metric Concept</th>
            <th className="px-3 py-2.5 text-right">Reported Value</th>
            <th className="px-3 py-2.5">Unit</th>
            <th className="px-3 py-2.5 text-right">Period Δ</th>
            <th className="px-3 py-2.5 text-right">% Growth</th>
            <th className="px-3 py-2.5">Filing / Source Reference</th>
            <th className="px-3 py-2.5 text-center">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-atlas-border-subtle font-mono text-atlas-text-primary">
          {observations.map((row, idx) => {
            const isMissing = row.is_missing;
            const delta = row.period_delta;
            const growth = row.percentage_growth;

            return (
              <tr key={idx} className="hover:bg-atlas-surface-1/50 transition-colors">
                <td className="px-3 py-2.5 font-semibold text-atlas-text-primary whitespace-nowrap">
                  {row.period_label}
                </td>
                <td className="px-3 py-2.5 text-atlas-text-secondary font-sans text-xs">
                  {row.metric_name}
                </td>
                <td className="px-3 py-2.5 text-right font-medium whitespace-nowrap">
                  {isMissing ? (
                    <span className="text-atlas-text-muted italic">Unavailable</span>
                  ) : (
                    row.display_value
                  )}
                </td>
                <td className="px-3 py-2.5 text-atlas-text-muted whitespace-nowrap">
                  {row.unit || row.currency || "—"}
                </td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">
                  {delta != null ? (
                    <span className={delta > 0 ? "text-emerald-500 font-medium" : delta < 0 ? "text-rose-500 font-medium" : "text-atlas-text-muted"}>
                      {delta > 0 ? "+" : ""}{delta.toLocaleString()}
                    </span>
                  ) : (
                    <span className="text-atlas-text-muted">—</span>
                  )}
                </td>
                <td className="px-3 py-2.5 text-right whitespace-nowrap">
                  {growth != null ? (
                    <span className={growth > 0 ? "text-emerald-500 font-medium" : growth < 0 ? "text-rose-500 font-medium" : "text-atlas-text-muted"}>
                      {formatPercentageDelta(growth)}
                    </span>
                  ) : (
                    <span className="text-atlas-text-muted">—</span>
                  )}
                </td>
                <td className="px-3 py-2.5 text-atlas-text-secondary max-w-xs truncate text-[11px]">
                  {row.source_accession ? (
                    <button
                      type="button"
                      onClick={() => row.source_id && onOpenSource?.(row.source_id)}
                      className="text-atlas-accent hover:underline text-left truncate block max-w-full"
                      title={row.source_title || row.source_accession}
                    >
                      {row.source_accession}
                    </button>
                  ) : row.source_title ? (
                    <span className="truncate block" title={row.source_title}>
                      {row.source_title}
                    </span>
                  ) : (
                    <span className="text-atlas-text-muted">Canonical Fact Registry</span>
                  )}
                </td>
                <td className="px-3 py-2.5 text-center whitespace-nowrap">
                  {isMissing ? (
                    <Badge variant="outline" className="text-[10px] text-amber-500 border-amber-500/30">
                      Missing
                    </Badge>
                  ) : row.is_restated ? (
                    <Badge variant="warning" className="text-[10px]">
                      Restated
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="text-[10px] text-emerald-500 border-emerald-500/30">
                      Verified
                    </Badge>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
