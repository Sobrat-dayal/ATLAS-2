import React, { useState } from "react";
import { X, Plus, AlertCircle } from "lucide-react";

interface CreateWatchlistDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; description?: string }) => Promise<void>;
}

export function CreateWatchlistDialog({
  isOpen,
  onClose,
  onSubmit,
}: CreateWatchlistDialogProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Watchlist name is required.");
      return;
    }
    if (trimmed.length > 100) {
      setError("Watchlist name must not exceed 100 characters.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await onSubmit({
        name: trimmed,
        description: description.trim() || undefined,
      });
      setName("");
      setDescription("");
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to create watchlist.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div
        className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-watchlist-title"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
          <h2 id="create-watchlist-title" className="text-xs font-semibold uppercase tracking-wider text-zinc-100 flex items-center gap-2">
            <Plus className="w-3.5 h-3.5 text-zinc-400" />
            Create New Watchlist
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

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-2.5 rounded bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label htmlFor="watchlist-name" className="block text-xs font-medium text-zinc-300 mb-1">
              Watchlist Name <span className="text-red-400">*</span>
            </label>
            <input
              id="watchlist-name"
              type="text"
              required
              maxLength={100}
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (error) setError(null);
              }}
              placeholder="e.g. Global Equities, Tech Giants, Crypto Macro"
              className="w-full px-3 py-1.5 text-xs bg-zinc-900 border border-zinc-700/80 rounded text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-zinc-400"
              autoFocus
            />
            <div className="flex justify-between items-center mt-1 text-[10px] text-zinc-500">
              <span>Unique name within your account</span>
              <span>{name.length}/100</span>
            </div>
          </div>

          <div>
            <label htmlFor="watchlist-desc" className="block text-xs font-medium text-zinc-300 mb-1">
              Description <span className="text-zinc-500">(Optional)</span>
            </label>
            <textarea
              id="watchlist-desc"
              rows={2}
              maxLength={500}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief summary or investment strategy context"
              className="w-full px-3 py-1.5 text-xs bg-zinc-900 border border-zinc-700/80 rounded text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-zinc-400 resize-none"
            />
            <div className="flex justify-end mt-1 text-[10px] text-zinc-500">
              <span>{description.length}/500</span>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800/80">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="px-3.5 py-1.5 text-xs font-medium rounded bg-zinc-100 text-zinc-900 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Creating..." : "Create Watchlist"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
