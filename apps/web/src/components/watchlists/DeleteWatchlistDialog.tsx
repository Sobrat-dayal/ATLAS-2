import React, { useState } from "react";
import { X, Trash2, AlertTriangle } from "lucide-react";

interface DeleteWatchlistDialogProps {
  isOpen: boolean;
  watchlistName: string;
  itemCount: number;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export function DeleteWatchlistDialog({
  isOpen,
  watchlistName,
  itemCount,
  onClose,
  onConfirm,
}: DeleteWatchlistDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    try {
      setLoading(true);
      setError(null);
      await onConfirm();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to delete watchlist.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div
        className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-watchlist-title"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-red-950/20">
          <h2 id="delete-watchlist-title" className="text-xs font-semibold uppercase tracking-wider text-red-300 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            Delete Watchlist
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-200 p-1 rounded hover:bg-zinc-800/80 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 space-y-3">
          {error && (
            <div className="p-2.5 rounded bg-red-950/40 border border-red-800/60 text-red-300 text-xs">
              {error}
            </div>
          )}

          <p className="text-xs text-zinc-300 leading-relaxed">
            Are you sure you want to permanently delete the watchlist{" "}
            <span className="font-semibold text-zinc-100 font-mono">"{watchlistName}"</span>?
          </p>

          <div className="p-2.5 rounded bg-zinc-900 border border-zinc-800 text-[11px] text-zinc-400 space-y-1">
            <p>
              • All <span className="text-zinc-200 font-medium">{itemCount}</span> member items in this list will be removed.
            </p>
            <p className="text-zinc-500">
              • Canonical financial instruments and historical data are unaffected.
            </p>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-zinc-800/80">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirm}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded bg-red-600 text-white hover:bg-red-500 disabled:opacity-50 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              {loading ? "Deleting..." : "Delete Watchlist"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
