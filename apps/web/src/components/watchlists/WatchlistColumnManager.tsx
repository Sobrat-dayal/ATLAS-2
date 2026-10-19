import React, { useMemo, useState } from "react";
import { X, Search, RotateCcw, ArrowUp, ArrowDown, Pin, Eye, EyeOff } from "lucide-react";
import {
  COLUMN_CATALOG,
  MAX_VISIBLE_COLUMNS,
  REQUIRED_COLUMN_ID,
} from "@/lib/watchlists/columns/registry";
import { WatchlistColumnConfigV1 } from "@/lib/watchlists/columns/types";

interface WatchlistColumnManagerProps {
  isOpen: boolean;
  config: WatchlistColumnConfigV1;
  onClose: () => void;
  onUpdateConfig: (newConfig: WatchlistColumnConfigV1) => void;
  onResetDefaults: () => void;
}

export function WatchlistColumnManager({
  isOpen,
  config,
  onClose,
  onUpdateConfig,
  onResetDefaults,
}: WatchlistColumnManagerProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredColumns = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return COLUMN_CATALOG;
    return COLUMN_CATALOG.filter(
      (c) =>
        c.label.toLowerCase().includes(q) ||
        c.id.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  if (!isOpen) return null;

  const visibleSet = new Set(config.visible_column_ids);
  const pinnedSet = new Set(config.pinned_left_column_ids);

  const handleToggleColumn = (colId: string) => {
    if (colId === REQUIRED_COLUMN_ID) return; // Cannot hide required symbol

    let newVisible: string[];
    if (visibleSet.has(colId)) {
      newVisible = config.visible_column_ids.filter((id) => id !== colId);
    } else {
      if (config.visible_column_ids.length >= MAX_VISIBLE_COLUMNS) {
        return; // Exceeded limit
      }
      newVisible = [...config.visible_column_ids, colId];
    }

    // Also remove from pinned if hidden
    const newPinned = config.pinned_left_column_ids.filter((id) => newVisible.includes(id));

    onUpdateConfig({
      ...config,
      visible_column_ids: newVisible,
      pinned_left_column_ids: newPinned,
    });
  };

  const handleTogglePin = (colId: string) => {
    const def = COLUMN_CATALOG.find((c) => c.id === colId);
    if (!def || !def.can_pin) return;

    let newPinned: string[];
    if (pinnedSet.has(colId)) {
      newPinned = config.pinned_left_column_ids.filter((id) => id !== colId);
    } else {
      if (config.pinned_left_column_ids.length >= 5) return;
      newPinned = [...config.pinned_left_column_ids, colId];
    }

    onUpdateConfig({
      ...config,
      pinned_left_column_ids: newPinned,
    });
  };

  const handleMoveOrder = (colId: string, direction: "up" | "down") => {
    const currentIndex = config.ordered_column_ids.indexOf(colId);
    if (currentIndex === -1) return;

    const newIndex = direction === "up" ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= config.ordered_column_ids.length) return;

    const newOrder = [...config.ordered_column_ids];
    const [moved] = newOrder.splice(currentIndex, 1);
    newOrder.splice(newIndex, 0, moved);

    // Also sync visible columns order
    const newVisibleOrder = newOrder.filter((id) => visibleSet.has(id));

    onUpdateConfig({
      ...config,
      ordered_column_ids: newOrder,
      visible_column_ids: newVisibleOrder,
    });
  };

  const categories: { key: string; label: string }[] = [
    { key: "identity", label: "Instrument Identity" },
    { key: "market", label: "Trading Market" },
    { key: "quote", label: "Available Quote Snapshot" },
    { key: "quality", label: "Source & Data Quality" },
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-150"
      role="dialog"
      aria-modal="true"
      aria-labelledby="column-manager-title"
    >
      <div className="flex flex-col w-full max-w-xl max-h-[85vh] rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-100 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800 bg-zinc-900/50">
          <div>
            <h2 id="column-manager-title" className="text-sm font-semibold text-zinc-100">
              Configure Watchlist Columns
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Select, reorder, and pin financial data columns for this watchlist.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
            aria-label="Close columns dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Toolbar: Search and visible counter */}
        <div className="flex items-center justify-between gap-3 px-5 py-3 border-b border-zinc-800/60 bg-zinc-900/20">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search columns by name, source or category..."
              className="w-full pl-8 pr-3 py-1.5 rounded bg-zinc-900 border border-zinc-800 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
            />
          </div>
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400 whitespace-nowrap">
            <span>Visible:</span>
            <span
              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                config.visible_column_ids.length >= MAX_VISIBLE_COLUMNS
                  ? "bg-amber-950/40 text-amber-400 border border-amber-800/40"
                  : "bg-zinc-800 text-zinc-200"
              }`}
            >
              {config.visible_column_ids.length} / {MAX_VISIBLE_COLUMNS}
            </span>
          </div>
        </div>

        {/* Column Catalog List Grouped by Category */}
        <div className="flex-1 overflow-y-auto px-5 py-3 space-y-5">
          {categories.map((cat) => {
            const colsInCat = filteredColumns.filter((c) => c.category === cat.key);
            if (colsInCat.length === 0) return null;

            return (
              <div key={cat.key} className="space-y-2">
                <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-semibold">
                  {cat.label}
                </div>
                <div className="divide-y divide-zinc-900 rounded border border-zinc-900 bg-zinc-900/20">
                  {colsInCat.map((col) => {
                    const isVisible = visibleSet.has(col.id);
                    const isPinned = pinnedSet.has(col.id);
                    const isRequired = col.id === REQUIRED_COLUMN_ID;

                    return (
                      <div
                        key={col.id}
                        className={`flex items-center justify-between p-2.5 transition-colors ${
                          isVisible ? "bg-zinc-900/30" : "opacity-60 hover:opacity-100"
                        }`}
                      >
                        <div className="flex items-start gap-3 min-w-0 pr-2">
                          <label className="flex items-center gap-2.5 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              checked={isVisible}
                              disabled={isRequired}
                              onChange={() => handleToggleColumn(col.id)}
                              className="rounded border-zinc-700 bg-zinc-900 text-zinc-100 focus:ring-0 focus:ring-offset-0 disabled:opacity-50"
                            />
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-medium text-zinc-200">
                                  {col.label}
                                </span>
                                {isRequired && (
                                  <span className="text-[9px] font-mono uppercase px-1 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
                                    Required
                                  </span>
                                )}
                                <span className="text-[9px] font-mono text-zinc-500">
                                  {col.value_type}
                                </span>
                              </div>
                              <p className="text-[11px] text-zinc-400 mt-0.5 line-clamp-1">
                                {col.description}
                              </p>
                            </div>
                          </label>
                        </div>

                        {/* Actions for visible columns: Pin, Move Up, Move Down */}
                        {isVisible && (
                          <div className="flex items-center gap-1 shrink-0">
                            {col.can_pin && (
                              <button
                                type="button"
                                onClick={() => handleTogglePin(col.id)}
                                className={`p-1 rounded text-xs transition-colors ${
                                  isPinned
                                    ? "bg-zinc-800 text-zinc-200 border border-zinc-700"
                                    : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/60"
                                }`}
                                title={isPinned ? "Unpin from left" : "Pin column to left"}
                                aria-label={isPinned ? "Unpin column" : "Pin column"}
                              >
                                <Pin className="w-3 h-3" />
                              </button>
                            )}

                            <button
                              type="button"
                              onClick={() => handleMoveOrder(col.id, "up")}
                              disabled={config.ordered_column_ids.indexOf(col.id) === 0}
                              className="p-1 rounded text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/60 disabled:opacity-30 disabled:pointer-events-none"
                              title="Move column left / up"
                            >
                              <ArrowUp className="w-3 h-3" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleMoveOrder(col.id, "down")}
                              disabled={
                                config.ordered_column_ids.indexOf(col.id) ===
                                config.ordered_column_ids.length - 1
                              }
                              className="p-1 rounded text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/60 disabled:opacity-30 disabled:pointer-events-none"
                              title="Move column right / down"
                            >
                              <ArrowDown className="w-3 h-3" />
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-zinc-800 bg-zinc-900/50">
          <button
            type="button"
            onClick={onResetDefaults}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset to Defaults</span>
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-zinc-100 text-zinc-900 hover:bg-white text-xs font-semibold transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
