"use client";

import React from "react";
import {
  formatDays,
  formatSignedPercent,
  getDrawdownEpisodeBadge,
} from "@/lib/risk/formatting";
import { DrawdownEpisodeDTO } from "@/lib/risk/types";
import { CheckCircle2, Clock, Flame } from "lucide-react";

interface DrawdownEpisodesTableProps {
  episodes: DrawdownEpisodeDTO[];
}

export function DrawdownEpisodesTable({ episodes }: DrawdownEpisodesTableProps) {
  if (!episodes || episodes.length === 0) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center text-xs text-atlas-text-muted">
        No significant drawdown episodes detected in the current observation window.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded border border-atlas-border-default/60 bg-atlas-surface-1">
      <div className="border-b border-atlas-border-default/40 px-4 py-3">
        <h4 className="text-sm font-semibold text-atlas-text-primary">
          Historical Drawdown Episodes Breakdown
        </h4>
        <p className="mt-0.5 text-xs text-atlas-text-muted">
          Chronological catalogue of peak-to-trough drawdowns and empirical recovery horizons.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] font-medium text-atlas-text-secondary">
              <th className="py-2.5 px-4 font-sans">Status</th>
              <th className="py-2.5 px-3">Peak Date</th>
              <th className="py-2.5 px-3 text-right">Peak Level</th>
              <th className="py-2.5 px-3">Trough Date</th>
              <th className="py-2.5 px-3 text-right">Trough Level</th>
              <th className="py-2.5 px-3 text-right">Max Drawdown</th>
              <th className="py-2.5 px-3 text-right">Time to Trough</th>
              <th className="py-2.5 px-3">Recovery Date</th>
              <th className="py-2.5 px-4 text-right">Recovery Horizon</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/30">
            {episodes.map((ep) => {
              const badge = getDrawdownEpisodeBadge(ep.status);
              return (
                <tr key={ep.episode_id} className="transition hover:bg-atlas-surface-2/40">
                  <td className="py-2 px-4 font-sans">
                    <span
                      className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-[10px] font-semibold ${badge.bgClass} ${badge.textClass} ${badge.borderClass}`}
                    >
                      {ep.status === "RECOVERED" ? (
                        <CheckCircle2 className="h-2.5 w-2.5" />
                      ) : (
                        <Flame className="h-2.5 w-2.5" />
                      )}
                      {badge.label}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-atlas-text-primary">
                    {ep.peak_date.substring(0, 10)}
                  </td>
                  <td className="py-2 px-3 text-right text-atlas-text-secondary">
                    {ep.peak_value.toFixed(2)}
                  </td>
                  <td className="py-2 px-3 text-rose-400 font-medium">
                    {ep.trough_date.substring(0, 10)}
                  </td>
                  <td className="py-2 px-3 text-right text-rose-400 font-medium">
                    {ep.trough_value.toFixed(2)}
                  </td>
                  <td className="py-2 px-3 text-right font-bold text-rose-400">
                    {formatSignedPercent(ep.max_drawdown, 2)}
                  </td>
                  <td className="py-2 px-3 text-right text-atlas-text-secondary font-sans">
                    {formatDays(ep.time_to_trough_days)}
                  </td>
                  <td className="py-2 px-3 text-emerald-400">
                    {ep.recovery_date ? ep.recovery_date.substring(0, 10) : "—"}
                  </td>
                  <td className="py-2 px-4 text-right text-atlas-text-primary font-sans">
                    {ep.recovery_duration_days !== null && ep.recovery_duration_days !== undefined
                      ? formatDays(ep.recovery_duration_days)
                      : "Unrecovered"}
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

