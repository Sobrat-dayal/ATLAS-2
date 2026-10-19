import React, { useState } from "react";
import { WatchlistItem } from "@/lib/watchlists/types";
import { WatchlistRow } from "./WatchlistRow";

interface WatchlistTableProps {
  items: WatchlistItem[];
  selectedItemId: string | null;
  onSelectItem: (item: WatchlistItem) => void;
  onRemoveItem: (item: WatchlistItem) => void;
  onReorder: (newOrderedItems: WatchlistItem[]) => void;
}

export function WatchlistTable({
  items,
  selectedItemId,
  onSelectItem,
  onRemoveItem,
  onReorder,
}: WatchlistTableProps) {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const [liveAnnouncement, setLiveAnnouncement] = useState<string>("");

  const handleDragStart = (e: React.DragEvent<HTMLTableRowElement>, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = "move";
    e.dataTransfer.setData("text/plain", index.toString());
  };

  const handleDragOver = (e: React.DragEvent<HTMLTableRowElement>, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    if (dragOverIndex !== index) {
      setDragOverIndex(index);
    }
  };

  const handleDragLeave = () => {
    // Left drag area
  };

  const handleDrop = (e: React.DragEvent<HTMLTableRowElement>, targetIndex: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === targetIndex) {
      setDraggedIndex(null);
      setDragOverIndex(null);
      return;
    }

    const newItems = [...items];
    const [moved] = newItems.splice(draggedIndex, 1);
    newItems.splice(targetIndex, 0, moved);

    setDraggedIndex(null);
    setDragOverIndex(null);
    setLiveAnnouncement(`Moved ${moved.symbol} to position ${targetIndex + 1} of ${newItems.length}`);
    onReorder(newItems);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
    setDragOverIndex(null);
  };

  const handleMoveUp = (index: number) => {
    if (index <= 0) return;
    const newItems = [...items];
    const [moved] = newItems.splice(index, 1);
    newItems.splice(index - 1, 0, moved);
    setLiveAnnouncement(`Moved ${moved.symbol} up to position ${index} of ${newItems.length}`);
    onReorder(newItems);
  };

  const handleMoveDown = (index: number) => {
    if (index >= items.length - 1) return;
    const newItems = [...items];
    const [moved] = newItems.splice(index, 1);
    newItems.splice(index + 1, 0, moved);
    setLiveAnnouncement(`Moved ${moved.symbol} down to position ${index + 2} of ${newItems.length}`);
    onReorder(newItems);
  };

  return (
    <div className="w-full overflow-x-auto rounded border border-zinc-800 bg-zinc-950">
      {/* Screen reader live announcement */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {liveAnnouncement}
      </div>

      <table className="w-full text-left border-collapse" aria-label="Watchlist Financial Instruments">
        <thead>
          <tr className="border-b border-zinc-800 bg-zinc-900/60 text-[10px] font-mono uppercase tracking-wider text-zinc-400 select-none">
            <th scope="col" className="w-8 px-2 py-2 text-center">
              <span className="sr-only">Drag to Reorder</span>
            </th>
            <th scope="col" className="w-10 px-2 py-2 text-center">
              #
            </th>
            <th scope="col" className="px-3 py-2 min-w-[140px]">
              Symbol / Instrument
            </th>
            <th scope="col" className="px-2.5 py-2">
              Type
            </th>
            <th scope="col" className="px-2.5 py-2">
              Venue
            </th>
            <th scope="col" className="px-3 py-2 text-right">
              Latest Measure
            </th>
            <th scope="col" className="px-3 py-2 text-right">
              Change
            </th>
            <th scope="col" className="px-2.5 py-2 text-center">
              Status
            </th>
            <th scope="col" className="px-3 py-2 text-right">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/40">
          {items.map((item, index) => (
            <WatchlistRow
              key={item.id}
              item={item}
              index={index}
              totalCount={items.length}
              isSelected={item.id === selectedItemId}
              isDragging={draggedIndex === index}
              isDragOver={dragOverIndex === index}
              onSelect={() => onSelectItem(item)}
              onDragStart={handleDragStart}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onDragEnd={handleDragEnd}
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
