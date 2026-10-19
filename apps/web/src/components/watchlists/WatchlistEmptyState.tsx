import React from "react";
import { Plus, ListPlus, Layers } from "lucide-react";

interface WatchlistEmptyStateProps {
  variant: "no_watchlists" | "empty_watchlist";
  watchlistName?: string;
  onCreateWatchlist?: () => void;
  onAddInstrument?: () => void;
}

export function WatchlistEmptyState({
  variant,
  watchlistName,
  onCreateWatchlist,
  onAddInstrument,
}: WatchlistEmptyStateProps) {
  if (variant === "no_watchlists") {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4 text-center border border-dashed border-zinc-800 rounded-lg bg-zinc-900/30">
        <div className="w-12 h-12 rounded-full bg-zinc-800/80 flex items-center justify-center text-zinc-400 mb-4 border border-zinc-700/50">
          <Layers className="w-6 h-6 text-zinc-300" />
        </div>
        <h3 className="text-sm font-semibold text-zinc-100 uppercase tracking-wider mb-1">
          No Watchlists Configured
        </h3>
        <p className="text-xs text-zinc-400 max-w-sm mb-6 leading-relaxed">
          Create a persistent, multi-asset watchlist to organize and monitor canonical financial
          instruments, authorized market quotes, and cross-navigation links.
        </p>
        <button
          type="button"
          onClick={onCreateWatchlist}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs font-medium rounded bg-zinc-100 text-zinc-900 hover:bg-white transition-colors focus:outline-none focus:ring-1 focus:ring-zinc-400"
        >
          <Plus className="w-4 h-4" />
          Create First Watchlist
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center border border-dashed border-zinc-800 rounded-lg bg-zinc-900/20">
      <div className="w-10 h-10 rounded-full bg-zinc-800/60 flex items-center justify-center text-zinc-400 mb-3 border border-zinc-700/40">
        <ListPlus className="w-5 h-5 text-zinc-300" />
      </div>
      <h3 className="text-xs font-semibold text-zinc-200 uppercase tracking-wider mb-1">
        {watchlistName ? `Watchlist "${watchlistName}" is Empty` : "Watchlist is Empty"}
      </h3>
      <p className="text-xs text-zinc-400 max-w-sm mb-5 leading-relaxed">
        Search for equities, ETFs, FX pairs, cryptocurrencies, bonds, or futures to add them to this list.
      </p>
      <button
        type="button"
        onClick={onAddInstrument}
        className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded bg-zinc-800 text-zinc-200 hover:bg-zinc-700 border border-zinc-700 transition-colors focus:outline-none focus:ring-1 focus:ring-zinc-400"
      >
        <Plus className="w-3.5 h-3.5" />
        Add Financial Instrument
      </button>
    </div>
  );
}
