"use client";

/**
 * Toast / Status Banner for Layout Restoration Results (Stage 74).
 *
 * Displays:
 * - Restored layout confirmation
 * - Exact counts of restored panels, drawings, indicators, and sync groups
 * - Non-destructive notice if any items are degraded or awaiting data
 */

import React from "react";
import { CheckCircle2, AlertTriangle, X } from "lucide-react";
import { RestorationReport } from "@/lib/charts";

interface LayoutRestoreStatusProps {
  report: RestorationReport | null;
  onDismiss: () => void;
}

export function LayoutRestoreStatus({ report, onDismiss }: LayoutRestoreStatusProps) {
  if (!report) return null;

  const hasDegraded = report.degradedPanels.length > 0;

  return (
    <div
      className={`fixed bottom-12 right-6 z-40 max-w-sm w-full p-3.5 rounded-lg border shadow-xl font-mono text-xs animate-in slide-in-from-bottom-3 duration-200 ${
        hasDegraded
          ? "bg-amber-950/90 border-amber-800 text-amber-200"
          : "bg-zinc-950/95 border-emerald-800/80 text-emerald-300"
      }`}
      role="status"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 font-semibold">
          {hasDegraded ? (
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          )}
          <span>{hasDegraded ? "RESTORED WITH WARNINGS" : "WORKSPACE RESTORED"}</span>
        </div>
        <button
          onClick={onDismiss}
          className="text-zinc-400 hover:text-zinc-200 p-0.5"
          aria-label="Dismiss restoration status"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="mt-2 text-[11px] text-zinc-300 space-y-0.5">
        <div>
          Charts: <strong className="text-zinc-100">{report.restoredPanels}/{report.totalPanels}</strong>
        </div>
        <div>
          Indicators: <strong className="text-zinc-100">{report.restoredIndicatorsCount}</strong> | Drawings:{" "}
          <strong className="text-zinc-100">{report.restoredDrawingsCount}</strong>
        </div>
        <div>
          Sync Groups: <strong className="text-zinc-100">{report.restoredSyncGroupsCount}</strong>
        </div>
      </div>

      {hasDegraded && (
        <div className="mt-2 pt-1.5 border-t border-amber-800/60 text-[10px] text-amber-300/90">
          {report.degradedPanels.map((dp, idx) => (
            <div key={idx}>
              • Panel {dp.panelId} ({dp.symbol}): {dp.reason}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
