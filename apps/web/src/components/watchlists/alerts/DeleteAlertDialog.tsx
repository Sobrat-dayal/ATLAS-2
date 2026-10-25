"use client";

import React, { useState } from "react";
import { AlertTriangle, Trash2, X } from "lucide-react";
import { WatchlistAlertRule } from "@/lib/watchlists/alerts/types";

interface DeleteAlertDialogProps {
  isOpen: boolean;
  onClose: () => void;
  alert: WatchlistAlertRule | null;
  onConfirm: (alertId: string) => Promise<unknown>;
}

export function DeleteAlertDialog({
  isOpen,
  onClose,
  alert,
  onConfirm,
}: DeleteAlertDialogProps) {
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !alert) return null;

  const handleDelete = async () => {
    try {
      setDeleting(true);
      setError(null);
      await onConfirm(alert.id);
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete alert";
      setError(msg);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-alert-title"
    >
      <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-zinc-900/80 border-b border-zinc-800">
          <div className="flex items-center gap-2 text-rose-400">
            <AlertTriangle className="w-4 h-4" />
            <h2 id="delete-alert-title" className="text-sm font-semibold text-zinc-100">
              Delete Alert Rule
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

        <div className="p-4 space-y-3">
          <p className="text-zinc-300">
            Are you sure you want to delete the alert rule for{" "}
            <span className="font-bold text-zinc-100">{alert.symbol}</span>?
          </p>

          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded space-y-1 text-zinc-400 text-[11px]">
            <div>
              <span className="text-zinc-500">Condition: </span>
              <span className="text-zinc-300 font-semibold">{alert.rule_type}</span>
            </div>
            <div>
              <span className="text-zinc-500">Threshold: </span>
              <span className="text-zinc-300 font-semibold">
                {alert.threshold_decimal} {alert.threshold_unit}
              </span>
            </div>
            <div>
              <span className="text-zinc-500">Measure: </span>
              <span className="text-zinc-300 font-semibold">{alert.quote_measure}</span>
            </div>
          </div>

          <p className="text-[11px] text-zinc-500">
            Historical trigger records will be retained in your audit log according to
            retention policies, but live background evaluation will terminate immediately.
          </p>

          {error && (
            <div className="p-2.5 bg-rose-950/50 border border-rose-800 rounded text-rose-300">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              disabled={deleting}
              className="px-3 py-1.5 rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleting}
              className="px-3 py-1.5 rounded bg-rose-600 text-white font-medium hover:bg-rose-500 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{deleting ? "Deleting..." : "Delete Alert"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
