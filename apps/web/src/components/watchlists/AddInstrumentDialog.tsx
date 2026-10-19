import React, { useState, useEffect, useRef } from "react";
import { X, Search, Plus, Check, Loader2, AlertCircle } from "lucide-react";
import { searchEntities, GlobalSearchEntityResult } from "@/lib/search";
import { getAssetClassBadge } from "@/lib/watchlists/formatting";

interface AddInstrumentDialogProps {
  isOpen: boolean;
  watchlistName: string;
  existingInstrumentIds: Set<string>;
  onClose: () => void;
  onAdd: (data: { instrument_entity_id: string; market_series_id?: string }) => Promise<void>;
}

export function AddInstrumentDialog({
  isOpen,
  watchlistName,
  existingInstrumentIds,
  onClose,
  onAdd,
}: AddInstrumentDialogProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<GlobalSearchEntityResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [addingId, setAddingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!isOpen) {
      setQuery("");
      setResults([]);
      setError(null);
      setAddingId(null);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    }
  }, [isOpen]);

  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      setLoading(false);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const timer = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await searchEntities({
          query: trimmed,
          limit: 25,
          signal: controller.signal,
        });
        setResults(res.results || []);
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setError("Failed to query canonical financial instruments.");
        }
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  if (!isOpen) return null;

  const handleAdd = async (result: GlobalSearchEntityResult) => {
    try {
      setAddingId(result.entity_id);
      setError(null);
      await onAdd({
        instrument_entity_id: result.entity_id,
        market_series_id: result.scope_display_name || undefined,
      });
    } catch (err: any) {
      setError(err?.message || "Failed to add instrument to watchlist.");
    } finally {
      setAddingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div
        className="w-full max-w-lg bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-150"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-instrument-title"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/50 shrink-0">
          <div>
            <h2 id="add-instrument-title" className="text-xs font-semibold uppercase tracking-wider text-zinc-100 flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-zinc-400" />
              Add Instrument to "{watchlistName}"
            </h2>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Search canonical financial catalog by ticker, ISIN, or company name
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-200 p-1 rounded hover:bg-zinc-800/80 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Input Bar */}
        <div className="p-3 border-b border-zinc-800 bg-zinc-900/30 shrink-0">
          <div className="relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search symbol (e.g. AAPL, BTC/USD, SPY, US10Y)..."
              className="w-full pl-9 pr-8 py-2 text-xs bg-zinc-900 border border-zinc-700/80 rounded text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 focus:border-zinc-400 font-mono"
              autoFocus
            />
            {loading && (
              <Loader2 className="w-4 h-4 text-zinc-400 animate-spin absolute right-3 top-1/2 -translate-y-1/2" />
            )}
          </div>
        </div>

        {/* Error Feedback */}
        {error && (
          <div className="p-2.5 mx-3 mt-3 rounded bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-start gap-2 shrink-0">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Results List */}
        <div className="overflow-y-auto p-2 divide-y divide-zinc-800/60 flex-1 min-h-[220px]">
          {query.trim() === "" ? (
            <div className="py-12 text-center text-xs text-zinc-500">
              Type a ticker, company name, or asset symbol to search across markets.
            </div>
          ) : loading && results.length === 0 ? (
            <div className="py-12 flex flex-col items-center justify-center text-xs text-zinc-500 gap-2">
              <Loader2 className="w-5 h-5 animate-spin text-zinc-400" />
              <span>Querying canonical instrument catalog...</span>
            </div>
          ) : results.length === 0 ? (
            <div className="py-12 text-center text-xs text-zinc-400">
              No matching financial instruments found for "{query}".
            </div>
          ) : (
            results.map((item) => {
              const badge = getAssetClassBadge(item.entity_type);
              const isAlreadyAdded = existingInstrumentIds.has(item.entity_id);
              const isAddingThis = addingId === item.entity_id;

              return (
                <div
                  key={item.entity_id}
                  className="flex items-center justify-between p-2.5 hover:bg-zinc-900/60 rounded transition-colors group"
                >
                  <div className="flex-1 min-w-0 pr-3">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-xs font-semibold text-zinc-100 font-mono tracking-wide">
                        {item.matched_text || item.display_name}
                      </span>
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-mono font-medium border border-zinc-700 bg-zinc-800 text-zinc-300">
                        {badge.label}
                      </span>
                      {item.scope_display_name && (
                        <span className="text-[10px] font-mono text-zinc-400">
                          {item.scope_display_name}
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-zinc-400 truncate">
                      {item.display_name !== item.matched_text ? item.display_name : item.canonical_name}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleAdd(item)}
                    disabled={isAlreadyAdded || isAddingThis}
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded transition-colors shrink-0 ${
                      isAlreadyAdded
                        ? "bg-zinc-800 text-zinc-500 border border-zinc-700/50 cursor-not-allowed"
                        : "bg-zinc-100 text-zinc-900 hover:bg-white"
                    }`}
                  >
                    {isAlreadyAdded ? (
                      <>
                        <Check className="w-3 h-3 text-zinc-400" />
                        Added
                      </>
                    ) : isAddingThis ? (
                      <>
                        <Loader2 className="w-3 h-3 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <Plus className="w-3 h-3" />
                        Add
                      </>
                    )}
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 border-t border-zinc-800 bg-zinc-900/50 flex justify-between items-center text-[10px] text-zinc-400 shrink-0">
          <span>{results.length} canonical results</span>
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1 text-xs text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
