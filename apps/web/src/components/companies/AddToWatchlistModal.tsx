"use client";

import { useEffect, useState } from "react";
import { Button } from "@/design-system";
import { addWatchlistItem, listWatchlists } from "@/lib/watchlists/api";
import { WatchlistListResponse, WatchlistSummary } from "@/lib/watchlists/types";
import { Check, Loader2, Plus, X } from "lucide-react";

export interface AddToWatchlistModalProps {
  isOpen: boolean;
  onClose: () => void;
  instrumentEntityId: string;
  instrumentSymbol?: string | null;
  instrumentName: string;
}

export function AddToWatchlistModal({
  isOpen,
  onClose,
  instrumentEntityId,
  instrumentSymbol,
  instrumentName,
}: AddToWatchlistModalProps) {
  const [watchlists, setWatchlists] = useState<WatchlistSummary[]>([]);
  const [selectedWatchlistId, setSelectedWatchlistId] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;

    listWatchlists(1, 50)
      .then((resp: WatchlistListResponse) => {
        if (!isMounted) return;
        setWatchlists(resp.items || []);
        if (resp.items && resp.items.length > 0) {
          setSelectedWatchlistId(resp.items[0].id);
        }
      })
      .catch((err: unknown) => {
        if (!isMounted) return;
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg || "Failed to load watchlists");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen]);

  const handleClose = () => {
    setSuccess(false);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  const handleAdd = async () => {
    if (!selectedWatchlistId) return;

    setSubmitting(true);
    setError(null);

    try {
      // Critical Stage 81 boundary requirement: NEVER pass Company UUID to Watchlist membership!
      // Must pass verified Financial Instrument Entity UUID:
      await addWatchlistItem(selectedWatchlistId, {
        instrument_entity_id: instrumentEntityId,
      });

      setSuccess(true);
      setTimeout(() => {
        onClose();
      }, 1200);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg || "Failed to add instrument to watchlist");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="watchlist-modal-title"
        className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm w-full max-w-md shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4 text-atlas-accent" />
            <h3 id="watchlist-modal-title" className="text-sm font-semibold text-atlas-text-primary">
              Add to Watchlist
            </h3>
          </div>
          <button
            type="button"
            onClick={handleClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary p-1 focus:outline-none"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div className="bg-atlas-surface-0 border border-atlas-border-subtle rounded-sm p-3">
            <div className="text-xs text-atlas-text-muted">Target Security</div>
            <div className="flex items-baseline gap-2 mt-0.5">
              {instrumentSymbol && (
                <span className="font-mono font-bold text-atlas-text-primary text-sm">
                  {instrumentSymbol}
                </span>
              )}
              <span className="text-xs text-atlas-text-secondary truncate">{instrumentName}</span>
            </div>
            <div className="font-mono text-[10px] text-atlas-text-muted mt-1 truncate">
              ID: {instrumentEntityId}
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-6 text-xs text-atlas-text-muted gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-atlas-accent" />
              <span>Loading owned watchlists...</span>
            </div>
          ) : watchlists.length === 0 ? (
            <div className="text-xs text-atlas-text-muted py-4 text-center">
              No watchlists available. Create a watchlist in the Watchlists module first.
            </div>
          ) : (
            <div className="space-y-2">
              <label htmlFor="watchlist-select" className="text-xs font-medium text-atlas-text-secondary">
                Select Destination Watchlist
              </label>
              <select
                id="watchlist-select"
                value={selectedWatchlistId}
                onChange={(e) => setSelectedWatchlistId(e.target.value)}
                disabled={submitting || success}
                className="w-full bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-3 py-2 text-xs text-atlas-text-primary focus:outline-none focus:ring-1 focus:ring-atlas-accent"
              >
                {watchlists.map((wl) => (
                  <option key={wl.id} value={wl.id}>
                    {wl.name} ({wl.item_count} items)
                  </option>
                ))}
              </select>
            </div>
          )}

          {error && (
            <div className="text-xs text-atlas-negative bg-atlas-negative/10 border border-atlas-negative/20 p-2.5 rounded-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="flex items-center gap-2 text-xs text-atlas-positive bg-atlas-positive/10 border border-atlas-positive/20 p-2.5 rounded-sm">
              <Check className="w-4 h-4" />
              <span>Successfully added security to watchlist!</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-2.5 px-4 py-3 border-t border-atlas-border-default bg-atlas-surface-2">
          <Button variant="secondary" size="sm" onClick={handleClose} disabled={submitting}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleAdd}
            disabled={submitting || loading || watchlists.length === 0 || success}
          >
            {submitting ? (
              <span className="flex items-center gap-1.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Adding...
              </span>
            ) : success ? (
              <span className="flex items-center gap-1.5">
                <Check className="w-3.5 h-3.5" />
                Added
              </span>
            ) : (
              "Add Security"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
