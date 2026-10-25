"use client";

import React from "react";
import {
  Clock,
  Edit2,
  History,
  Pause,
  Play,
  Trash2,
} from "lucide-react";
import {
  WatchlistAlertRule,
} from "@/lib/watchlists/alerts/types";
import {
  formatAlertState,
  formatConditionLabel,
  formatEvaluationStatus,
  formatRecurrenceLabel,
  formatThresholdDisplay,
} from "@/lib/watchlists/alerts/formatting";

interface AlertRuleRowProps {
  alert: WatchlistAlertRule;
  onEdit: (alert: WatchlistAlertRule) => void;
  onDelete: (alert: WatchlistAlertRule) => void;
  onPause: (alertId: string) => void;
  onResume: (alertId: string) => void;
  onViewHistory: (alert: WatchlistAlertRule) => void;
}

export function AlertRuleRow({
  alert,
  onEdit,
  onDelete,
  onPause,
  onResume,
  onViewHistory,
}: AlertRuleRowProps) {
  const evalState = alert.evaluation_state;
  const stateFmt = formatAlertState(alert.state);
  const evalFmt = evalState
    ? formatEvaluationStatus(evalState.evaluation_status)
    : { label: "Idle", variant: "neutral" as const };

  return (
    <tr className="hover:bg-zinc-900/40 border-b border-zinc-800/60 font-mono text-xs transition-colors">
      {/* Instrument */}
      <td className="py-2.5 px-3">
        <div className="flex items-center gap-2">
          <span className="font-bold text-zinc-100">{alert.symbol}</span>
          <span className="text-[10px] text-zinc-500">v{alert.revision}</span>
        </div>
      </td>

      {/* Condition & Measure */}
      <td className="py-2.5 px-3">
        <div className="flex flex-col">
          <span className="text-zinc-200">
            {formatConditionLabel(alert.rule_type)}
          </span>
          <span className="text-[10px] text-zinc-400">
            {alert.quote_measure}
            {alert.reference_methodology ? ` • ${alert.reference_methodology}` : ""}
          </span>
        </div>
      </td>

      {/* Threshold */}
      <td className="py-2.5 px-3 font-semibold text-zinc-100">
        {formatThresholdDisplay(
          alert.threshold_decimal,
          alert.threshold_unit,
          alert.rule_type,
        )}
      </td>

      {/* Recurrence & Cooldown */}
      <td className="py-2.5 px-3 text-[11px] text-zinc-400">
        {formatRecurrenceLabel(alert.recurrence_policy, alert.cooldown_seconds)}
      </td>

      {/* Status Badges */}
      <td className="py-2.5 px-3">
        <div className="flex items-center gap-1.5 flex-wrap">
          {/* User state badge */}
          <span
            className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${stateFmt.badgeClass}`}
          >
            {stateFmt.label}
          </span>

          {/* Evaluator health status badge if enabled */}
          {alert.enabled && (
            <span
              className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                evalFmt.variant === "armed"
                  ? "text-sky-400 bg-sky-950/60"
                  : evalFmt.variant === "triggered"
                    ? "text-emerald-400 bg-emerald-950/60"
                    : evalFmt.variant === "cooldown"
                      ? "text-amber-400 bg-amber-950/60"
                      : evalFmt.variant === "warning"
                        ? "text-rose-400 bg-rose-950/60"
                        : "text-zinc-400 bg-zinc-900"
              }`}
            >
              {evalFmt.label}
            </span>
          )}
        </div>
      </td>

      {/* Last Trigger */}
      <td className="py-2.5 px-3 text-[11px] text-zinc-400">
        {evalState?.last_trigger_at ? (
          <span className="flex items-center gap-1 text-zinc-300">
            <Clock className="w-3 h-3 text-zinc-500" />
            {new Date(evalState.last_trigger_at).toLocaleTimeString("en-US", {
              hour12: false,
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
            })}
          </span>
        ) : (
          <span className="text-zinc-600">Never</span>
        )}
      </td>

      {/* Actions */}
      <td className="py-2.5 px-3 text-right">
        <div className="flex items-center justify-end gap-1">
          {/* Pause / Resume */}
          {alert.enabled ? (
            <button
              type="button"
              onClick={() => onPause(alert.id)}
              className="p-1 rounded text-zinc-400 hover:text-amber-300 hover:bg-zinc-800 transition-colors"
              title="Pause Alert Evaluation"
              aria-label={`Pause alert for ${alert.symbol}`}
            >
              <Pause className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => onResume(alert.id)}
              className="p-1 rounded text-zinc-400 hover:text-emerald-300 hover:bg-zinc-800 transition-colors"
              title="Resume Alert Evaluation"
              aria-label={`Resume alert for ${alert.symbol}`}
            >
              <Play className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Trigger History */}
          <button
            type="button"
            onClick={() => onViewHistory(alert)}
            className="p-1 rounded text-zinc-400 hover:text-sky-300 hover:bg-zinc-800 transition-colors"
            title="View Trigger History"
            aria-label={`View trigger history for ${alert.symbol}`}
          >
            <History className="w-3.5 h-3.5" />
          </button>

          {/* Edit */}
          <button
            type="button"
            onClick={() => onEdit(alert)}
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            title="Edit Alert Parameters"
            aria-label={`Edit alert for ${alert.symbol}`}
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>

          {/* Delete */}
          <button
            type="button"
            onClick={() => onDelete(alert)}
            className="p-1 rounded text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 transition-colors"
            title="Delete Alert"
            aria-label={`Delete alert for ${alert.symbol}`}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </td>
    </tr>
  );
}
