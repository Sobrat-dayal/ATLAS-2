"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, Clock, Edit2, HelpCircle, X } from "lucide-react";
import {
  QuoteMeasure,
  RecurrencePolicy,
  UpdateAlertPayload,
  WatchlistAlertRule,
} from "@/lib/watchlists/alerts/types";
import {
  formatConditionLabel,
  formatQuoteMeasure,
} from "@/lib/watchlists/alerts/formatting";

interface EditAlertDialogProps {
  isOpen: boolean;
  onClose: () => void;
  alert: WatchlistAlertRule | null;
  onSubmit: (alertId: string, payload: UpdateAlertPayload) => Promise<unknown>;
}

export function EditAlertDialog({
  isOpen,
  onClose,
  alert,
  onSubmit,
}: EditAlertDialogProps) {
  const [threshold, setThreshold] = useState<string>("");
  const [recurrence, setRecurrence] = useState<RecurrencePolicy>("RECURRING");
  const [cooldown, setCooldown] = useState<number>(300);
  const [quoteMeasure, setQuoteMeasure] = useState<QuoteMeasure>("LAST");
  const [expiresAt, setExpiresAt] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (alert) {
      setThreshold(String(alert.threshold_decimal));
      setRecurrence(alert.recurrence_policy);
      setCooldown(alert.cooldown_seconds || 0);
      setQuoteMeasure(alert.quote_measure);
      setExpiresAt(alert.expires_at ? alert.expires_at.slice(0, 16) : "");
      setNotes(alert.notes || "");
      setError(null);
    }
  }, [alert]);

  if (!isOpen || !alert) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseFloat(threshold);
    if (isNaN(val)) {
      setError("Please enter a valid numeric threshold.");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const payload: UpdateAlertPayload = {
        expected_revision: alert.revision,
        threshold_decimal: val,
        threshold_unit: alert.threshold_unit,
        quote_measure: quoteMeasure,
        recurrence_policy: recurrence,
        cooldown_seconds: recurrence === "RECURRING" ? cooldown : 0,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
        notes: notes.trim() || null,
      };

      await onSubmit(alert.id, payload);
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update alert";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-alert-title"
    >
      <div className="w-full max-w-lg bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-zinc-900/80 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <Edit2 className="w-4 h-4 text-sky-400" />
            <h2 id="edit-alert-title" className="text-sm font-semibold text-zinc-100">
              Edit Watchlist Alert: {alert.symbol}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 text-zinc-400 hover:text-zinc-200 rounded hover:bg-zinc-800 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Target & Condition Badge */}
          <div className="p-3 bg-zinc-900/50 border border-zinc-800 rounded flex items-center justify-between">
            <div>
              <span className="font-bold text-zinc-100 text-sm">{alert.symbol}</span>
              <span className="ml-2 text-zinc-400">
                {formatConditionLabel(alert.rule_type)}
              </span>
            </div>
            <span className="text-[10px] text-zinc-500">
              Revision: v{alert.revision}
            </span>
          </div>

          {error && (
            <div className="p-2.5 bg-rose-950/50 border border-rose-800 rounded text-rose-300 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Threshold & Measure */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Threshold ({alert.threshold_unit})
              </label>
              <div className="relative">
                <input
                  type="number"
                  step="any"
                  required
                  value={threshold}
                  onChange={(e) => setThreshold(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-100 focus:outline-none focus:border-sky-500"
                />
                <span className="absolute right-2.5 top-1.5 text-zinc-400 text-[11px]">
                  {alert.threshold_unit}
                </span>
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Quote Measure
              </label>
              <select
                value={quoteMeasure}
                onChange={(e) => setQuoteMeasure(e.target.value as QuoteMeasure)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
              >
                <option value="LAST">{formatQuoteMeasure("LAST")}</option>
                <option value="BID">{formatQuoteMeasure("BID")}</option>
                <option value="ASK">{formatQuoteMeasure("ASK")}</option>
                <option value="MID">{formatQuoteMeasure("MID")}</option>
                <option value="OPEN">{formatQuoteMeasure("OPEN")}</option>
                <option value="HIGH">{formatQuoteMeasure("HIGH")}</option>
                <option value="LOW">{formatQuoteMeasure("LOW")}</option>
                <option value="CLOSE">{formatQuoteMeasure("CLOSE")}</option>
                <option value="NAV">{formatQuoteMeasure("NAV")}</option>
                <option value="YIELD">{formatQuoteMeasure("YIELD")}</option>
              </select>
            </div>
          </div>

          {/* Recurrence & Cooldown */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Recurrence Policy
              </label>
              <select
                value={recurrence}
                onChange={(e) => setRecurrence(e.target.value as RecurrencePolicy)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
              >
                <option value="RECURRING">Recurring (Re-arms on move)</option>
                <option value="ONE_SHOT">One-Shot (Auto-Disables)</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-zinc-400 mb-1">
                Cooldown Window
              </label>
              <select
                disabled={recurrence === "ONE_SHOT"}
                value={cooldown}
                onChange={(e) => setCooldown(parseInt(e.target.value, 10))}
                className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500 disabled:opacity-40"
              >
                <option value={0}>None (Instant Re-Arm)</option>
                <option value={60}>1 Minute</option>
                <option value={300}>5 Minutes</option>
                <option value={900}>15 Minutes</option>
                <option value={3600}>1 Hour</option>
                <option value={86400}>1 Day</option>
              </select>
            </div>
          </div>

          {/* Expiration */}
          <div>
            <label className="block text-[11px] font-medium text-zinc-400 mb-1 flex items-center gap-1">
              <Clock className="w-3 h-3 text-zinc-400" />
              <span>Optional Expiration (UTC)</span>
            </label>
            <input
              type="datetime-local"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-700 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Re-arming baseline reset notice */}
          <div className="p-2.5 bg-zinc-900/40 border border-zinc-800 rounded flex items-start gap-2 text-[10px] text-zinc-400">
            <HelpCircle className="w-3.5 h-3.5 mt-0.5 text-sky-400 shrink-0" />
            <span>
              Updating threshold or measure increments rule revision and resets the
              crossing evaluation baseline to prevent false retroactive triggers.
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-1.5 rounded bg-sky-600 text-white font-medium hover:bg-sky-500 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <Edit2 className="w-3.5 h-3.5" />
              <span>{submitting ? "Saving..." : "Save Changes"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
