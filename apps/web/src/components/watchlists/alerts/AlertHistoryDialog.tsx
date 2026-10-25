"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, Clock, History, RefreshCw, X } from "lucide-react";
import {
  WatchlistAlertRule,
  WatchlistAlertTrigger,
} from "@/lib/watchlists/alerts/types";
import { formatConditionLabel } from "@/lib/watchlists/alerts/formatting";

interface AlertHistoryDialogProps {
  isOpen: boolean;
  onClose: () => void;
  alert: WatchlistAlertRule | null;
  fetchHistory: (alertId: string) => Promise<WatchlistAlertTrigger[]>;
}

export function AlertHistoryDialog({
  isOpen,
  onClose,
  alert,
  fetchHistory,
}: AlertHistoryDialogProps) {
  const [triggers, setTriggers] = useState<WatchlistAlertTrigger[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = React.useCallback(async () => {
    if (!alert) return;
    try {
      setLoading(true);
      setError(null);
      const data = await fetchHistory(alert.id);
      setTriggers(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load trigger history";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [alert, fetchHistory]);

  useEffect(() => {
    if (isOpen && alert) {
      loadData();
    }
  }, [isOpen, alert, loadData]);

  if (!isOpen || !alert) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="alert-history-title"
    >
      <div className="w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-zinc-900/80 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-sky-400" />
            <h2 id="alert-history-title" className="text-sm font-semibold text-zinc-100">
              Trigger Audit History: {alert.symbol}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={loadData}
              disabled={loading}
              className="p-1 text-zinc-400 hover:text-zinc-200 rounded hover:bg-zinc-800 transition-colors"
              title="Refresh History"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1 text-zinc-400 hover:text-zinc-200 rounded hover:bg-zinc-800 transition-colors"
              aria-label="Close dialog"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Rule Summary */}
        <div className="px-4 py-2 bg-zinc-900/40 border-b border-zinc-800 flex items-center justify-between text-[11px] text-zinc-400">
          <div>
            <span>Condition: </span>
            <span className="font-semibold text-zinc-200">
              {formatConditionLabel(alert.rule_type)} {alert.threshold_decimal}{" "}
              {alert.threshold_unit}
            </span>
          </div>
          <div>
            <span>Measure: </span>
            <span className="font-semibold text-zinc-200">{alert.quote_measure}</span>
          </div>
        </div>

        {/* Content Table */}
        <div className="p-4 max-h-96 overflow-y-auto">
          {error && (
            <div className="p-2.5 bg-rose-950/50 border border-rose-800 rounded text-rose-300 mb-3">
              {error}
            </div>
          )}

          {triggers.length === 0 && !loading && (
            <div className="py-8 text-center text-zinc-500">
              <Clock className="w-8 h-8 mx-auto mb-2 opacity-40" />
              <p>No trigger events recorded for this alert rule yet.</p>
              <p className="text-[10px] text-zinc-600 mt-1">
                Triggers are durably committed upon qualified financial condition satisfaction.
              </p>
            </div>
          )}

          {triggers.length > 0 && (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] uppercase text-zinc-500">
                  <th className="py-2 px-2">Trigger Time (UTC)</th>
                  <th className="py-2 px-2">Observed</th>
                  <th className="py-2 px-2">Threshold</th>
                  <th className="py-2 px-2">Source / Venue</th>
                  <th className="py-2 px-2 text-right">Delivery Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {triggers.map((t) => (
                  <tr key={t.id} className="hover:bg-zinc-900/40">
                    <td className="py-2 px-2 text-zinc-300">
                      {new Date(t.evaluated_at).toLocaleString("en-US", {
                        hour12: false,
                        month: "short",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      })}
                    </td>
                    <td className="py-2 px-2 font-bold text-zinc-100">
                      {t.observation_value.toFixed(2)}
                    </td>
                    <td className="py-2 px-2 text-zinc-400">
                      {t.threshold_value.toFixed(2)}
                    </td>
                    <td className="py-2 px-2 text-zinc-400 text-[10px]">
                      {t.source}
                      {t.venue ? ` (${t.venue})` : ""}
                    </td>
                    <td className="py-2 px-2 text-right">
                      <span
                        className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          t.notification_status === "DELIVERED"
                            ? "text-emerald-400 bg-emerald-950/60 border border-emerald-800/80"
                            : t.notification_status === "PENDING"
                              ? "text-amber-400 bg-amber-950/60 border border-amber-800/80"
                              : "text-rose-400 bg-rose-950/60 border border-rose-800/80"
                        }`}
                      >
                        {t.notification_status === "DELIVERED" && (
                          <CheckCircle2 className="w-3 h-3" />
                        )}
                        {t.notification_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-3 bg-zinc-900/60 border-t border-zinc-800 text-[10px] text-zinc-500">
          <span>Total Triggers: {triggers.length}</span>
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
