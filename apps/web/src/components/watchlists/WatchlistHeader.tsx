import React from "react";
import { Plus, Edit3, Trash2, Clock, RefreshCw, SlidersHorizontal, ArrowUpDown, X, RotateCw } from "lucide-react";
import { WatchlistDetail, WatchlistSummary } from "@/lib/watchlists/types";
import { COLUMN_MAP } from "@/lib/watchlists/columns/registry";
import { RealtimeConnectionState } from "@/lib/realtime/types";
import { LiveDataQuality } from "@/lib/watchlists/live";
import { WatchlistSelector } from "./WatchlistSelector";
import { WatchlistConnectionStatus } from "./WatchlistConnectionStatus";
import { WatchlistDataQuality } from "./WatchlistDataQuality";

interface WatchlistHeaderProps {
  watchlists: WatchlistSummary[];
  activeWatchlist: WatchlistDetail | null;
  activeWatchlistId: string | null;
  isRefreshing?: boolean;
  visibleColumnCount?: number;
  activeSort?: { column_id: string | null; direction: "asc" | "desc" | null };
  connectionState?: RealtimeConnectionState;
  dataQuality?: LiveDataQuality;
  activeSubscribedCount?: number;
  onSelectWatchlist: (id: string) => void;
  onCreateNew: () => void;
  onAddInstrument: () => void;
  onRename: () => void;
  onDelete: () => void;
  onRefresh: () => void;
  onReconnect?: () => void;
  onRefreshSort?: () => void;
  onOpenColumns?: () => void;
  onClearSort?: () => void;
}

export function WatchlistHeader({
  watchlists,
  activeWatchlist,
  activeWatchlistId,
  isRefreshing,
  visibleColumnCount = 7,
  activeSort,
  connectionState,
  dataQuality,
  activeSubscribedCount = 0,
  onSelectWatchlist,
  onCreateNew,
  onAddInstrument,
  onRename,
  onDelete,
  onRefresh,
  onReconnect,
  onRefreshSort,
  onOpenColumns,
  onClearSort,
}: WatchlistHeaderProps) {
  const formattedUpdated = activeWatchlist?.updated_at
    ? new Date(activeWatchlist.updated_at).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : null;

  const sortedColName = activeSort?.column_id ? COLUMN_MAP.get(activeSort.column_id)?.label || activeSort.column_id : null;

  return (
    <div className="flex flex-col gap-3 pb-3 border-b border-zinc-800">
      {/* Top Row: Watchlist Selector, Live Indicators & Primary Actions */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <WatchlistSelector
            watchlists={watchlists}
            activeWatchlistId={activeWatchlistId}
            onSelectWatchlist={onSelectWatchlist}
            onCreateNew={onCreateNew}
          />

          {/* Realtime Live Indicators */}
          {activeWatchlist && (
            <div className="hidden md:flex items-center gap-2">
              <WatchlistConnectionStatus
                connectionState={connectionState || "DISCONNECTED"}
                onReconnect={onReconnect}
              />
              <WatchlistDataQuality
                dataQuality={dataQuality || "realtime"}
                activeCount={activeSubscribedCount}
                totalCount={activeWatchlist.total_items}
              />
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {activeWatchlist && (
            <>
              {onOpenColumns && (
                <button
                  type="button"
                  onClick={onOpenColumns}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 text-xs font-medium transition-colors"
                  title="Configure Columns"
                >
                  <SlidersHorizontal className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Columns</span>
                  <span className="text-[10px] font-mono px-1 rounded bg-zinc-800 text-zinc-400">
                    {visibleColumnCount}
                  </span>
                </button>
              )}

              <button
                type="button"
                onClick={onRefresh}
                disabled={isRefreshing}
                className="p-1.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-zinc-800 transition-colors"
                title="Refresh Quotes"
                aria-label="Refresh Quotes"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
              </button>

              <button
                type="button"
                onClick={onAddInstrument}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-100 text-zinc-900 hover:bg-white text-xs font-medium transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Instrument</span>
              </button>

              <button
                type="button"
                onClick={onRename}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 text-xs font-medium transition-colors"
                title="Rename Watchlist"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Rename</span>
              </button>

              <button
                type="button"
                onClick={onDelete}
                className="p-1.5 rounded text-zinc-400 hover:text-red-400 hover:bg-red-950/30 border border-zinc-800 transition-colors"
                title="Delete Watchlist"
                aria-label="Delete Watchlist"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </>
          )}

          {!activeWatchlist && (
            <button
              type="button"
              onClick={onCreateNew}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-zinc-100 text-zinc-900 hover:bg-white text-xs font-medium transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create Watchlist</span>
            </button>
          )}
        </div>
      </div>

      {/* Sub-header: Active list title, revision, item count, sort indicator, and description */}
      {activeWatchlist && (
        <div className="flex flex-wrap items-baseline justify-between gap-2 pt-1">
          <div className="flex flex-col gap-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-base font-bold text-zinc-100 tracking-tight">
                {activeWatchlist.name}
              </h1>
              <span className="text-[10px] font-mono text-zinc-500 uppercase px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">
                Rev {activeWatchlist.revision}
              </span>
              <span className="text-xs text-zinc-400 font-mono">
                {activeWatchlist.total_items} {activeWatchlist.total_items === 1 ? "instrument" : "instruments"}
              </span>

              {/* Active Sort Indicator Badge */}
              {sortedColName && activeSort?.direction && (
                <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-700/80 text-[11px] font-mono text-zinc-300">
                  <ArrowUpDown className="w-3 h-3 text-zinc-400" />
                  <span>Sorted by {sortedColName} · {activeSort.direction === "asc" ? "Asc" : "Desc"}</span>
                  {onRefreshSort && (
                    <button
                      type="button"
                      onClick={onRefreshSort}
                      className="ml-1 text-zinc-400 hover:text-zinc-200 inline-flex items-center gap-0.5"
                      title="Re-apply sort order over latest live quote values"
                    >
                      <RotateCw className="w-2.5 h-2.5" />
                      <span className="text-[10px]">Re-sort</span>
                    </button>
                  )}
                  {onClearSort && (
                    <button
                      type="button"
                      onClick={onClearSort}
                      className="text-zinc-500 hover:text-zinc-200 ml-0.5"
                      title="Clear sort and restore manual order"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  )}
                </div>
              )}
            </div>
            {activeWatchlist.description && (
              <p className="text-xs text-zinc-400 mt-0.5 max-w-xl">
                {activeWatchlist.description}
              </p>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Mobile-only live indicators */}
            <div className="flex md:hidden items-center gap-2">
              <WatchlistConnectionStatus
                connectionState={connectionState || "DISCONNECTED"}
                onReconnect={onReconnect}
              />
            </div>

            {formattedUpdated && (
              <div className="flex items-center gap-1 text-[10px] font-mono text-zinc-500">
                <Clock className="w-3 h-3 text-zinc-500" />
                <span>Updated {formattedUpdated}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
