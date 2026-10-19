import React from "react";
import { GripVertical } from "lucide-react";
import { WatchlistItem } from "@/lib/watchlists/types";
import {
  formatChange,
  formatPrice,
  getAssetClassBadge,
} from "@/lib/watchlists/formatting";
import { WatchlistColumnDefinition } from "@/lib/watchlists/columns/types";
import { WatchlistStatusBadge } from "./WatchlistStatusBadge";
import { WatchlistRowActions } from "./WatchlistRowActions";

interface WatchlistRowProps {
  item: WatchlistItem;
  index: number;
  totalCount: number;
  visibleColumns: WatchlistColumnDefinition[];
  pinnedColumnIds: string[];
  columnWidths: Record<string, number>;
  stickyOffsets: Map<string, number>;
  isSelected: boolean;
  isDragging: boolean;
  isDragOver: boolean;
  onSelect: () => void;
  onDragStart: (e: React.DragEvent<HTMLTableRowElement>, index: number) => void;
  onDragOver: (e: React.DragEvent<HTMLTableRowElement>, index: number) => void;
  onDragLeave: (e: React.DragEvent<HTMLTableRowElement>) => void;
  onDrop: (e: React.DragEvent<HTMLTableRowElement>, index: number) => void;
  onDragEnd: (e: React.DragEvent<HTMLTableRowElement>) => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onRemove: () => void;
}

export function WatchlistRow({
  item,
  index,
  totalCount,
  visibleColumns,
  pinnedColumnIds,
  columnWidths,
  stickyOffsets,
  isSelected,
  isDragging,
  isDragOver,
  onSelect,
  onDragStart,
  onDragOver,
  onDragLeave,
  onDrop,
  onDragEnd,
  onMoveUp,
  onMoveDown,
  onRemove,
}: WatchlistRowProps) {
  const badge = getAssetClassBadge(item.asset_class);
  const formattedPrice = formatPrice(item.last_price, item.asset_class, item.quote_currency);
  const changeData = formatChange(item.absolute_change, item.percentage_change);

  let changeColor = "text-zinc-500";
  if (changeData.direction === "up") {
    changeColor = "text-emerald-400";
  } else if (changeData.direction === "down") {
    changeColor = "text-rose-400";
  } else if (changeData.direction === "flat") {
    changeColor = "text-zinc-400";
  }

  const isNameColumnVisible = visibleColumns.some((c) => c.id === "instrument.name");

  return (
    <tr
      draggable
      onDragStart={(e) => onDragStart(e, index)}
      onDragOver={(e) => onDragOver(e, index)}
      onDragLeave={onDragLeave}
      onDrop={(e) => onDrop(e, index)}
      onDragEnd={onDragEnd}
      onClick={onSelect}
      className={`border-b border-zinc-800/60 transition-colors cursor-pointer select-none text-xs group ${
        isSelected
          ? "bg-zinc-800/80 border-l-2 border-l-sky-500"
          : "hover:bg-zinc-900/70 bg-zinc-950"
      } ${isDragging ? "opacity-40 bg-zinc-800" : ""} ${
        isDragOver ? "border-t-2 border-t-sky-400" : ""
      }`}
    >
      {/* Leading Fixed Column 1: Drag handle (Sticky left: 0px, width 32px) */}
      <td
        style={{ position: "sticky", left: "0px", zIndex: 20 }}
        className="w-8 px-2 py-2 text-zinc-600 group-hover:text-zinc-400 cursor-grab active:cursor-grabbing text-center bg-zinc-950 group-hover:bg-zinc-900/90"
        title="Drag row to reorder watchlist instruments"
        onClick={(e) => e.stopPropagation()}
      >
        <GripVertical className="w-3.5 h-3.5 inline-block" />
      </td>

      {/* Leading Fixed Column 2: Position index # (Sticky left: 32px, width 40px) */}
      <td
        style={{ position: "sticky", left: "32px", zIndex: 20 }}
        className="w-10 px-2 py-2 text-zinc-500 font-mono text-[11px] text-center border-r border-zinc-800/40 bg-zinc-950 group-hover:bg-zinc-900/90"
      >
        {index + 1}
      </td>

      {/* Dynamic Registered Columns */}
      {visibleColumns.map((col) => {
        const isPinned = pinnedColumnIds.includes(col.id);
        const offsetLeft = stickyOffsets.get(col.id);
        const width = columnWidths[col.id] ?? col.default_width;

        const cellStyle: React.CSSProperties = {
          width: `${width}px`,
          minWidth: `${col.min_width}px`,
          maxWidth: `${col.max_width}px`,
          ...(isPinned
            ? {
                position: "sticky",
                left: offsetLeft !== undefined ? `${offsetLeft}px` : "72px",
                zIndex: 10,
              }
            : {}),
        };

        const pinnedBorder = isPinned ? "border-r border-zinc-800/80 bg-zinc-950 group-hover:bg-zinc-900/90" : "";

        // Cell content by column ID
        switch (col.id) {
          case "instrument.symbol":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-3 py-2 ${pinnedBorder}`}
              >
                <div className="font-mono font-bold text-zinc-100 tracking-wide text-xs truncate">
                  {item.symbol}
                </div>
                {!isNameColumnVisible && (
                  <div className="text-[10px] text-zinc-400 truncate">
                    {item.display_name}
                  </div>
                )}
              </td>
            );

          case "instrument.name":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-3 py-2 text-zinc-300 text-xs truncate ${pinnedBorder}`}
                title={item.display_name || item.canonical_name}
              >
                <span className="truncate block">
                  {item.display_name || item.canonical_name}
                </span>
              </td>
            );

          case "instrument.asset_class":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 whitespace-nowrap ${pinnedBorder}`}
              >
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border border-zinc-700 bg-zinc-800 text-zinc-300">
                  {badge.label}
                </span>
              </td>
            );

          case "instrument.subtype":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 text-zinc-400 font-mono text-[11px] truncate ${pinnedBorder}`}
              >
                {item.asset_class.toUpperCase()}
              </td>
            );

          case "instrument.identifier":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 text-zinc-400 font-mono text-[11px] truncate ${pinnedBorder}`}
              >
                {item.symbol}
              </td>
            );

          case "market.venue":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 font-mono text-[11px] text-zinc-400 truncate ${pinnedBorder}`}
              >
                {item.venue || "—"}
              </td>
            );

          case "market.currency":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 font-mono text-[11px] text-zinc-400 truncate ${pinnedBorder}`}
              >
                {item.quote_currency || "USD"}
              </td>
            );

          case "market.listing_country":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 font-mono text-[11px] text-zinc-400 truncate ${pinnedBorder}`}
              >
                US
              </td>
            );

          case "quote.latest_measure":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-3 py-2 text-right whitespace-nowrap font-mono ${pinnedBorder}`}
              >
                {item.is_quote_available ? (
                  <>
                    <div className="text-zinc-100 font-semibold text-xs tabular-nums">
                      {formattedPrice}
                    </div>
                    <div className="text-[10px] text-zinc-400 uppercase tracking-wider">
                      {item.quote_measure || "Last"} {item.quote_currency || ""}
                    </div>
                  </>
                ) : (
                  <span className="text-zinc-500 font-normal" title="Quote observation unavailable">
                    —
                  </span>
                )}
              </td>
            );

          case "quote.change":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-3 py-2 text-right whitespace-nowrap font-mono text-xs font-medium tabular-nums ${changeColor} ${pinnedBorder}`}
              >
                {item.is_quote_available ? changeData.text : "—"}
              </td>
            );

          case "quote.kind":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 whitespace-nowrap ${pinnedBorder}`}
              >
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800">
                  {item.quote_measure || "Last"}
                </span>
              </td>
            );

          case "quote.as_of":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 font-mono text-[10px] text-zinc-400 whitespace-nowrap ${pinnedBorder}`}
              >
                {item.source_timestamp
                  ? new Date(item.source_timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "—"}
              </td>
            );

          case "quality.freshness":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 whitespace-nowrap text-center ${pinnedBorder}`}
              >
                <WatchlistStatusBadge
                  freshnessStatus={item.freshness_status}
                  deliveryDelayStatus={item.delivery_delay_status}
                  delaySeconds={item.delay_seconds}
                />
              </td>
            );

          case "quality.source":
            return (
              <td
                key={col.id}
                style={cellStyle}
                className={`px-2.5 py-2 font-mono text-[10px] text-zinc-400 truncate ${pinnedBorder}`}
              >
                {item.provider || "CANONICAL"}
              </td>
            );

          default:
            return (
              <td key={col.id} style={cellStyle} className={`px-2.5 py-2 text-zinc-400 ${pinnedBorder}`}>
                —
              </td>
            );
        }
      })}

      {/* Trailing Fixed Column: Actions */}
      <td className="px-3 py-2 whitespace-nowrap text-right">
        <WatchlistRowActions
          item={item}
          index={index}
          totalCount={totalCount}
          onMoveUp={onMoveUp}
          onMoveDown={onMoveDown}
          onRemove={onRemove}
        />
      </td>
    </tr>
  );
}
