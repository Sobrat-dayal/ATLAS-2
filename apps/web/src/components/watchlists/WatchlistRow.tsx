import React from "react";
import { GripVertical } from "lucide-react";
import { WatchlistItem } from "@/lib/watchlists/types";
import {
  formatChange,
  formatPrice,
  getAssetClassBadge,
} from "@/lib/watchlists/formatting";
import { WatchlistStatusBadge } from "./WatchlistStatusBadge";
import { WatchlistRowActions } from "./WatchlistRowActions";

interface WatchlistRowProps {
  item: WatchlistItem;
  index: number;
  totalCount: number;
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
      {/* Drag handle */}
      <td
        className="w-8 px-2 py-2 text-zinc-600 group-hover:text-zinc-400 cursor-grab active:cursor-grabbing text-center"
        title="Drag to reorder"
        onClick={(e) => e.stopPropagation()}
      >
        <GripVertical className="w-3.5 h-3.5 inline-block" />
      </td>

      {/* Position index */}
      <td className="w-10 px-2 py-2 text-zinc-500 font-mono text-[11px] text-center">
        {index + 1}
      </td>

      {/* Symbol & Name */}
      <td className="px-3 py-2 min-w-[140px] max-w-[200px]">
        <div className="font-mono font-semibold text-zinc-100 tracking-wide text-xs truncate">
          {item.symbol}
        </div>
        <div className="text-[10px] text-zinc-400 truncate max-w-[180px]">
          {item.display_name}
        </div>
      </td>

      {/* Type badge */}
      <td className="px-2.5 py-2 whitespace-nowrap">
        <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border border-zinc-700 bg-zinc-800 text-zinc-300">
          {badge.label}
        </span>
      </td>

      {/* Venue / Market */}
      <td className="px-2.5 py-2 font-mono text-[11px] text-zinc-400 whitespace-nowrap">
        {item.venue || "—"}
      </td>

      {/* Latest Measure */}
      <td className="px-3 py-2 text-right whitespace-nowrap font-mono">
        <div className="text-zinc-100 font-semibold text-xs">
          {formattedPrice}
        </div>
        <div className="text-[10px] text-zinc-400 uppercase tracking-wider">
          {item.quote_measure || "Last"} {item.quote_currency || ""}
        </div>
      </td>

      {/* Change */}
      <td className={`px-3 py-2 text-right whitespace-nowrap font-mono text-xs font-medium ${changeColor}`}>
        {changeData.text}
      </td>

      {/* Status / Freshness */}
      <td className="px-2.5 py-2 whitespace-nowrap text-center">
        <WatchlistStatusBadge
          freshnessStatus={item.freshness_status}
          deliveryDelayStatus={item.delivery_delay_status}
          delaySeconds={item.delay_seconds}
        />
      </td>

      {/* Actions */}
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
