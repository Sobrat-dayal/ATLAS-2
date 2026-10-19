import React, { useMemo, useState } from "react";
import { WatchlistItem } from "@/lib/watchlists/types";
import {
  COLUMN_MAP,
  REQUIRED_COLUMN_ID,
  calculateStickyLeftOffsets,
} from "@/lib/watchlists/columns/registry";
import {
  WatchlistColumnConfigV1,
  WatchlistColumnDefinition,
} from "@/lib/watchlists/columns/types";
import { WatchlistColumnHeader } from "./WatchlistColumnHeader";
import { WatchlistRow } from "./WatchlistRow";

interface WatchlistTableProps {
  items: WatchlistItem[];
  config: WatchlistColumnConfigV1;
  onUpdateConfig: (newConfig: WatchlistColumnConfigV1) => void;
  selectedItemId: string | null;
  onSelectItem: (item: WatchlistItem) => void;
  onRemoveItem: (item: WatchlistItem) => void;
  onReorder: (newOrderedItems: WatchlistItem[]) => void;
}

export function WatchlistTable({
  items,
  config,
  onUpdateConfig,
  selectedItemId,
  onSelectItem,
  onRemoveItem,
  onReorder,
}: WatchlistTableProps) {
  // Row drag reorder state (Stage 76)
  const [draggedRowIndex, setDraggedRowIndex] = useState<number | null>(null);
  const [dragOverRowIndex, setDragOverRowIndex] = useState<number | null>(null);
  const [liveAnnouncement, setLiveAnnouncement] = useState<string>("");

  // Column drag reorder state (Stage 77)
  const [draggedColId, setDraggedColId] = useState<string | null>(null);
  const [dragTargetColId, setDragTargetColId] = useState<string | null>(null);

  // 1. Resolve visible column definitions in current display order
  const visibleColumns = useMemo<WatchlistColumnDefinition[]>(() => {
    // Follow ordered_column_ids filtering for visible ones
    const visibleSet = new Set(config.visible_column_ids);
    const orderedVisible: WatchlistColumnDefinition[] = [];

    for (const colId of config.ordered_column_ids) {
      if (visibleSet.has(colId)) {
        const def = COLUMN_MAP.get(colId);
        if (def) orderedVisible.push(def);
      }
    }

    // Ensure required symbol is present
    if (!orderedVisible.some((c) => c.id === REQUIRED_COLUMN_ID)) {
      const symDef = COLUMN_MAP.get(REQUIRED_COLUMN_ID);
      if (symDef) orderedVisible.unshift(symDef);
    }

    return orderedVisible;
  }, [config.ordered_column_ids, config.visible_column_ids]);

  // 2. Calculate sticky left offsets for pinned columns
  const stickyOffsets = useMemo(() => {
    return calculateStickyLeftOffsets(
      visibleColumns,
      config.pinned_left_column_ids,
      config.widths,
      72 // 32px drag handle + 40px index column
    );
  }, [visibleColumns, config.pinned_left_column_ids, config.widths]);

  // 3. Client-side financial sorting over complete membership items
  const sortedItems = useMemo(() => {
    const { column_id, direction } = config.sort;
    if (!column_id || !direction) {
      return items; // Default manual membership order
    }

    const colDef = COLUMN_MAP.get(column_id);
    if (!colDef || !colDef.can_sort) {
      return items;
    }

    const isDesc = direction === "desc";

    const getRawValue = (item: WatchlistItem): unknown => {
      switch (column_id) {
        case "instrument.symbol":
          return item.symbol;
        case "instrument.name":
          return item.display_name || item.canonical_name;
        case "instrument.asset_class":
          return item.asset_class;
        case "market.venue":
          return item.venue;
        case "quote.latest_measure":
          return item.is_quote_available ? item.last_price : null;
        case "quote.change":
          return item.is_quote_available ? item.percentage_change : null;
        case "quote.kind":
          return item.is_quote_available ? item.quote_measure : null;
        case "quote.as_of":
          return item.is_quote_available ? item.source_timestamp : null;
        case "quality.freshness":
          return item.freshness_status;
        case "quality.source":
          return item.provider;
        default:
          return null;
      }
    };

    // Separate valid vs missing rows (missing-values-last semantics on both asc and desc)
    const valid: { item: WatchlistItem; parsed: number | string; manualPos: number }[] = [];
    const missing: { item: WatchlistItem; manualPos: number }[] = [];

    items.forEach((item, idx) => {
      const raw = getRawValue(item);
      if (raw === null || raw === undefined || raw === "" || raw === "—") {
        missing.push({ item, manualPos: idx });
      } else {
        let parsed: number | string;
        if (colDef.sort_policy === "numeric") {
          const cleaned = String(raw).replace(/[%+,]/g, "").trim();
          const n = parseFloat(cleaned);
          parsed = isNaN(n) ? 0 : n;
        } else {
          parsed = String(raw).toLowerCase();
        }
        valid.push({ item, parsed, manualPos: idx });
      }
    });

    // Stable sort valid items by manualPos first, then by parsed value
    valid.sort((a, b) => a.manualPos - b.manualPos);
    valid.sort((a, b) => {
      if (a.parsed < b.parsed) return isDesc ? 1 : -1;
      if (a.parsed > b.parsed) return isDesc ? -1 : 1;
      return 0;
    });

    // Missing items retain manual order
    missing.sort((a, b) => a.manualPos - b.manualPos);

    return [...valid.map((v) => v.item), ...missing.map((m) => m.item)];
  }, [items, config.sort]);

  // =========================================================================
  // Column Operations
  // =========================================================================

  const handleSortChange = (columnId: string, direction: "asc" | "desc" | null) => {
    onUpdateConfig({
      ...config,
      sort: { column_id: direction ? columnId : null, direction },
    });
    const colName = COLUMN_MAP.get(columnId)?.label || columnId;
    if (direction) {
      setLiveAnnouncement(`Sorted table by ${colName} ${direction === "asc" ? "ascending" : "descending"}`);
    } else {
      setLiveAnnouncement(`Cleared sort, restored manual watchlist order`);
    }
  };

  const handleResizeCommit = (columnId: string, newWidth: number) => {
    onUpdateConfig({
      ...config,
      widths: {
        ...config.widths,
        [columnId]: newWidth,
      },
    });
  };

  const handleTogglePin = (columnId: string) => {
    const isPinned = config.pinned_left_column_ids.includes(columnId);
    let newPinned: string[];
    if (isPinned) {
      newPinned = config.pinned_left_column_ids.filter((id) => id !== columnId);
      setLiveAnnouncement(`Unpinned ${COLUMN_MAP.get(columnId)?.label || columnId}`);
    } else {
      if (config.pinned_left_column_ids.length >= 5) return;
      newPinned = [...config.pinned_left_column_ids, columnId];
      setLiveAnnouncement(`Pinned ${COLUMN_MAP.get(columnId)?.label || columnId} to left`);
    }
    onUpdateConfig({
      ...config,
      pinned_left_column_ids: newPinned,
    });
  };

  const handleHideColumn = (columnId: string) => {
    if (columnId === REQUIRED_COLUMN_ID) return;
    const newVisible = config.visible_column_ids.filter((id) => id !== columnId);
    const newPinned = config.pinned_left_column_ids.filter((id) => id !== columnId);
    onUpdateConfig({
      ...config,
      visible_column_ids: newVisible,
      pinned_left_column_ids: newPinned,
    });
    setLiveAnnouncement(`Hidden column ${COLUMN_MAP.get(columnId)?.label || columnId}`);
  };

  const handleResetWidth = (columnId: string) => {
    const def = COLUMN_MAP.get(columnId);
    if (!def) return;
    onUpdateConfig({
      ...config,
      widths: {
        ...config.widths,
        [columnId]: def.default_width,
      },
    });
  };

  // Drag and drop column reordering
  const handleColumnDragStart = (e: React.DragEvent<HTMLElement>, columnId: string) => {
    e.dataTransfer.setData("text/plain", columnId);
    e.dataTransfer.effectAllowed = "move";
    setDraggedColId(columnId);
  };

  const handleColumnDragOver = (e: React.DragEvent<HTMLElement>, columnId: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (dragTargetColId !== columnId) {
      setDragTargetColId(columnId);
    }
  };

  const handleColumnDragLeave = () => {
    // left target
  };

  const handleColumnDrop = (e: React.DragEvent<HTMLElement>, targetColumnId: string) => {
    e.preventDefault();
    if (!draggedColId || draggedColId === targetColumnId) {
      setDraggedColId(null);
      setDragTargetColId(null);
      return;
    }

    const currentOrder = [...config.ordered_column_ids];
    const sourceIndex = currentOrder.indexOf(draggedColId);
    const targetIndex = currentOrder.indexOf(targetColumnId);

    if (sourceIndex === -1 || targetIndex === -1) {
      setDraggedColId(null);
      setDragTargetColId(null);
      return;
    }

    const [moved] = currentOrder.splice(sourceIndex, 1);
    currentOrder.splice(targetIndex, 0, moved);

    const visibleSet = new Set(config.visible_column_ids);
    const newVisible = currentOrder.filter((id) => visibleSet.has(id));

    setDraggedColId(null);
    setDragTargetColId(null);

    const movedName = COLUMN_MAP.get(moved)?.label || moved;
    setLiveAnnouncement(`Moved column ${movedName} to new position`);

    onUpdateConfig({
      ...config,
      ordered_column_ids: currentOrder,
      visible_column_ids: newVisible,
    });
  };

  // =========================================================================
  // Row Drag and Drop Reordering (Stage 76)
  // =========================================================================

  const handleRowDragStart = (e: React.DragEvent<HTMLTableRowElement>, index: number) => {
    setDraggedRowIndex(index);
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", index.toString());
  };

  const handleRowDragOver = (e: React.DragEvent<HTMLTableRowElement>, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (dragOverRowIndex !== index) {
      setDragOverRowIndex(index);
    }
  };

  const handleRowDragLeave = () => {
    // left row area
  };

  const handleRowDrop = (e: React.DragEvent<HTMLTableRowElement>, targetIndex: number) => {
    e.preventDefault();
    if (draggedRowIndex === null || draggedRowIndex === targetIndex) {
      setDraggedRowIndex(null);
      setDragOverRowIndex(null);
      return;
    }

    const newItems = [...items];
    const [moved] = newItems.splice(draggedRowIndex, 1);
    newItems.splice(targetIndex, 0, moved);

    setDraggedRowIndex(null);
    setDragOverRowIndex(null);
    setLiveAnnouncement(`Moved ${moved.symbol} to position ${targetIndex + 1} of ${newItems.length}`);
    onReorder(newItems);
  };

  const handleRowDragEnd = () => {
    setDraggedRowIndex(null);
    setDragOverRowIndex(null);
  };

  const handleMoveUp = (index: number) => {
    if (index <= 0) return;
    const newItems = [...items];
    const [moved] = newItems.splice(index, 1);
    newItems.splice(index - 1, 0, moved);
    setLiveAnnouncement(`Moved ${moved.symbol} up to position ${index}`);
    onReorder(newItems);
  };

  const handleMoveDown = (index: number) => {
    if (index >= items.length - 1) return;
    const newItems = [...items];
    const [moved] = newItems.splice(index, 1);
    newItems.splice(index + 1, 0, moved);
    setLiveAnnouncement(`Moved ${moved.symbol} down to position ${index + 2}`);
    onReorder(newItems);
  };

  return (
    <div className="w-full overflow-x-auto rounded border border-zinc-800 bg-zinc-950 shadow-sm">
      {/* Screen reader live announcement */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {liveAnnouncement}
      </div>

      <table className="w-full text-left border-collapse" aria-label="Watchlist Financial Instruments">
        <thead>
          <tr className="border-b border-zinc-800 bg-zinc-900/90 text-[10px] font-mono uppercase tracking-wider text-zinc-400 select-none">
            {/* Fixed Leading Column 1: Row Drag Handle (Sticky left: 0px, width 32px) */}
            <th
              scope="col"
              style={{ position: "sticky", left: "0px", zIndex: 30 }}
              className="w-8 px-2 py-2 text-center bg-zinc-900 border-b border-zinc-800"
            >
              <span className="sr-only">Drag to Reorder</span>
            </th>

            {/* Fixed Leading Column 2: Position # (Sticky left: 32px, width 40px) */}
            <th
              scope="col"
              style={{ position: "sticky", left: "32px", zIndex: 30 }}
              className="w-10 px-2 py-2 text-center bg-zinc-900 border-r border-zinc-800 border-b"
            >
              #
            </th>

            {/* Dynamic Configured Column Headers */}
            {visibleColumns.map((col) => (
              <WatchlistColumnHeader
                key={col.id}
                column={col}
                width={config.widths[col.id] ?? col.default_width}
                isPinned={config.pinned_left_column_ids.includes(col.id)}
                stickyLeftOffset={stickyOffsets.get(col.id)}
                sortDirection={config.sort.column_id === col.id ? config.sort.direction : null}
                onSortChange={handleSortChange}
                onResizeCommit={handleResizeCommit}
                onTogglePin={handleTogglePin}
                onHideColumn={handleHideColumn}
                onResetWidth={handleResetWidth}
                onColumnDragStart={handleColumnDragStart}
                onColumnDragOver={handleColumnDragOver}
                onColumnDragLeave={handleColumnDragLeave}
                onColumnDrop={handleColumnDrop}
                isDragTarget={dragTargetColId === col.id}
              />
            ))}

            {/* Fixed Trailing Column: Actions */}
            <th scope="col" className="px-3 py-2 text-right bg-zinc-900/90 border-b border-zinc-800">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/40">
          {sortedItems.map((item, index) => (
            <WatchlistRow
              key={item.id}
              item={item}
              index={index}
              totalCount={sortedItems.length}
              visibleColumns={visibleColumns}
              pinnedColumnIds={config.pinned_left_column_ids}
              columnWidths={config.widths}
              stickyOffsets={stickyOffsets}
              isSelected={item.id === selectedItemId}
              isDragging={draggedRowIndex === index}
              isDragOver={dragOverRowIndex === index}
              onSelect={() => onSelectItem(item)}
              onDragStart={handleRowDragStart}
              onDragOver={handleRowDragOver}
              onDragLeave={handleRowDragLeave}
              onDrop={handleRowDrop}
              onDragEnd={handleRowDragEnd}
              onMoveUp={() => handleMoveUp(index)}
              onMoveDown={() => handleMoveDown(index)}
              onRemove={() => onRemoveItem(item)}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
