import React from "react";
import { ChevronDown, Plus } from "lucide-react";
import { WatchlistSummary } from "@/lib/watchlists/types";

interface WatchlistSelectorProps {
  watchlists: WatchlistSummary[];
  activeWatchlistId: string | null;
  onSelectWatchlist: (id: string) => void;
  onCreateNew: () => void;
}

export function WatchlistSelector({
  watchlists,
  activeWatchlistId,
  onSelectWatchlist,
  onCreateNew,
}: WatchlistSelectorProps) {
  if (watchlists.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      {/* Desktop/Tablet Horizontal Tabs */}
      <div className="hidden sm:flex items-center gap-1 overflow-x-auto max-w-[500px] py-1">
        {watchlists.map((w) => {
          const isActive = w.id === activeWatchlistId;
          return (
            <button
              key={w.id}
              type="button"
              onClick={() => onSelectWatchlist(w.id)}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium whitespace-nowrap transition-colors ${
                isActive
                  ? "bg-zinc-800 text-zinc-100 border border-zinc-700"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 border border-transparent"
              }`}
            >
              <span>{w.name}</span>
              <span
                className={`px-1 py-0.2 rounded text-[10px] font-mono ${
                  isActive ? "bg-zinc-700 text-zinc-200" : "bg-zinc-800/80 text-zinc-500"
                }`}
              >
                {w.item_count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Mobile Select Dropdown */}
      <div className="sm:hidden relative">
        <select
          value={activeWatchlistId || ""}
          onChange={(e) => onSelectWatchlist(e.target.value)}
          className="appearance-none bg-zinc-900 border border-zinc-700 rounded px-3 py-1.5 pr-8 text-xs font-medium text-zinc-100 focus:outline-none focus:ring-1 focus:ring-zinc-400"
          aria-label="Select Watchlist"
        >
          {watchlists.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name} ({w.item_count})
            </option>
          ))}
        </select>
        <ChevronDown className="w-3.5 h-3.5 text-zinc-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
      </div>

      {/* New Watchlist Mini Button */}
      <button
        type="button"
        onClick={onCreateNew}
        className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-zinc-800 transition-colors"
        title="Create New Watchlist"
        aria-label="Create New Watchlist"
      >
        <Plus className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
