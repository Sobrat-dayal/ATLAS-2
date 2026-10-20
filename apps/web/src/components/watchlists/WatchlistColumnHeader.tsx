import React, { useState, useRef, useEffect } from "react";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpDown,
  MoreVertical,
  Pin,
  PinOff,
  EyeOff,
  RotateCcw,
  GripVertical,
} from "lucide-react";
import { WatchlistColumnDefinition } from "@/lib/watchlists/columns/types";

interface WatchlistColumnHeaderProps {
  column: WatchlistColumnDefinition;
  width: number;
  isPinned: boolean;
  stickyLeftOffset?: number;
  sortDirection?: "asc" | "desc" | null;
  onSortChange: (columnId: string, direction: "asc" | "desc" | null) => void;
  onResizeCommit: (columnId: string, newWidth: number) => void;
  onTogglePin: (columnId: string) => void;
  onHideColumn: (columnId: string) => void;
  onResetWidth: (columnId: string) => void;
  // Drag and drop
  onColumnDragStart: (e: React.DragEvent<HTMLElement>, columnId: string) => void;
  onColumnDragOver: (e: React.DragEvent<HTMLElement>, columnId: string) => void;
  onColumnDragLeave: (e: React.DragEvent<HTMLElement>) => void;
  onColumnDrop: (e: React.DragEvent<HTMLElement>, targetColumnId: string) => void;
  isDragTarget?: boolean;
}

export function WatchlistColumnHeader({
  column,
  width,
  isPinned,
  stickyLeftOffset,
  sortDirection,
  onSortChange,
  onResizeCommit,
  onTogglePin,
  onHideColumn,
  onResetWidth,
  onColumnDragStart,
  onColumnDragOver,
  onColumnDragLeave,
  onColumnDrop,
  isDragTarget,
}: WatchlistColumnHeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [resizingWidth, setResizingWidth] = useState<number | null>(null);
  const [isResizing, setIsResizing] = useState(false);
  const startXRef = useRef(0);
  const startWidthRef = useRef(width);
  const menuRef = useRef<HTMLDivElement>(null);

  // Click outside to close context menu
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsMenuOpen(false);
      }
    }
    if (isMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isMenuOpen]);

  // Sorting cycle: null -> asc -> desc -> null
  const handleSortClick = () => {
    if (!column.can_sort) return;
    if (sortDirection === "asc") {
      onSortChange(column.id, "desc");
    } else if (sortDirection === "desc") {
      onSortChange(column.id, null);
    } else {
      onSortChange(column.id, "asc");
    }
  };

  // Resize handler
  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);
    startXRef.current = e.clientX;
    startWidthRef.current = width;
    setResizingWidth(width);

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const delta = moveEvent.clientX - startXRef.current;
      const unclamped = startWidthRef.current + delta;
      const clamped = Math.max(column.min_width, Math.min(column.max_width, unclamped));
      setResizingWidth(clamped);
    };

    const handleMouseUp = (upEvent: MouseEvent) => {
      setIsResizing(false);
      setResizingWidth(null);
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      const delta = upEvent.clientX - startXRef.current;
      const finalWidth = Math.max(
        column.min_width,
        Math.min(column.max_width, startWidthRef.current + delta)
      );
      onResizeCommit(column.id, finalWidth);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  const isNumeric = column.value_type === "MONETARY" || column.value_type === "PERCENTAGE";
  const alignClass = isNumeric ? "text-right justify-end" : "text-left justify-start";

  const effectiveWidth = isResizing && resizingWidth !== null ? resizingWidth : width;

  const pinnedStyles: React.CSSProperties = isPinned
    ? {
        position: "sticky",
        left: stickyLeftOffset !== undefined ? `${stickyLeftOffset}px` : "0px",
        zIndex: 30,
      }
    : {};

  return (
    <th
      scope="col"
      style={{
        width: `${effectiveWidth}px`,
        minWidth: `${column.min_width}px`,
        maxWidth: `${column.max_width}px`,
        ...pinnedStyles,
      }}
      className={`group relative select-none py-2 px-3 text-[10px] font-mono uppercase tracking-wider text-zinc-400 bg-zinc-900/90 border-b border-zinc-800 transition-colors ${
        isDragTarget ? "border-l-2 border-l-blue-500 bg-zinc-800" : ""
      } ${isPinned ? "border-r border-zinc-800/80 shadow-[1px_0_0_0_rgba(39,39,42,1)]" : ""}`}
      draggable
      onDragStart={(e) => onColumnDragStart(e, column.id)}
      onDragOver={(e) => onColumnDragOver(e, column.id)}
      onDragLeave={onColumnDragLeave}
      onDrop={(e) => onColumnDrop(e, column.id)}
      aria-sort={
        sortDirection === "asc"
          ? "ascending"
          : sortDirection === "desc"
          ? "descending"
          : "none"
      }
    >
      <div className={`flex items-center gap-1.5 ${alignClass} w-full`}>
        {/* Reorder grip */}
        <span
          className="cursor-grab active:cursor-grabbing text-zinc-600 hover:text-zinc-300 opacity-0 group-hover:opacity-100 transition-opacity"
          title="Drag column header to reorder"
          aria-hidden="true"
        >
          <GripVertical className="w-2.5 h-2.5" />
        </span>

        {/* Column label with sort trigger */}
        <button
          type="button"
          onClick={handleSortClick}
          className={`flex items-center gap-1 font-semibold truncate hover:text-zinc-200 transition-colors focus:outline-none focus:text-zinc-100 ${
            sortDirection ? "text-zinc-100 font-bold" : ""
          }`}
          title={`${column.description} (Click to sort)`}
        >
          <span className="truncate">{column.label}</span>
          {column.can_sort && (
            <span className="shrink-0 text-zinc-500">
              {sortDirection === "asc" && <ArrowUp className="w-3 h-3 text-zinc-100" />}
              {sortDirection === "desc" && <ArrowDown className="w-3 h-3 text-zinc-100" />}
              {!sortDirection && (
                <ArrowUpDown className="w-2.5 h-2.5 opacity-0 group-hover:opacity-60 transition-opacity" />
              )}
            </span>
          )}
        </button>

        {/* Pinned visual icon */}
        {isPinned && (
          <span title="Pinned column" className="text-zinc-500">
            <Pin className="w-2.5 h-2.5" />
          </span>
        )}

        {/* Column Header Context Menu Button */}
        <div className="relative shrink-0" ref={menuRef}>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setIsMenuOpen(!isMenuOpen);
            }}
            className="p-0.5 rounded text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
            title="Column options"
            aria-label={`Options for ${column.label}`}
          >
            <MoreVertical className="w-3 h-3" />
          </button>

          {/* Dropdown Menu */}
          {isMenuOpen && (
            <div className="absolute right-0 top-full mt-1 w-44 rounded-md border border-zinc-800 bg-zinc-950 p-1 text-xs text-zinc-300 shadow-xl z-50 animate-in fade-in zoom-in-95 duration-100">
              {column.can_sort && (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      onSortChange(column.id, "asc");
                      setIsMenuOpen(false);
                    }}
                    className="flex w-full items-center gap-2 rounded px-2 py-1.5 hover:bg-zinc-800 hover:text-zinc-100 text-left"
                  >
                    <ArrowUp className="w-3 h-3 text-zinc-400" />
                    <span>Sort Ascending</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      onSortChange(column.id, "desc");
                      setIsMenuOpen(false);
                    }}
                    className="flex w-full items-center gap-2 rounded px-2 py-1.5 hover:bg-zinc-800 hover:text-zinc-100 text-left"
                  >
                    <ArrowDown className="w-3 h-3 text-zinc-400" />
                    <span>Sort Descending</span>
                  </button>
                  {sortDirection && (
                    <button
                      type="button"
                      onClick={() => {
                        onSortChange(column.id, null);
                        setIsMenuOpen(false);
                      }}
                      className="flex w-full items-center gap-2 rounded px-2 py-1.5 hover:bg-zinc-800 hover:text-zinc-100 text-left text-zinc-400"
                    >
                      <RotateCcw className="w-3 h-3" />
                      <span>Clear Sort</span>
                    </button>
                  )}
                  <div className="my-1 border-t border-zinc-800/80" />
                </>
              )}

              {column.can_pin && (
                <button
                  type="button"
                  onClick={() => {
                    onTogglePin(column.id);
                    setIsMenuOpen(false);
                  }}
                  className="flex w-full items-center gap-2 rounded px-2 py-1.5 hover:bg-zinc-800 hover:text-zinc-100 text-left"
                >
                  {isPinned ? (
                    <>
                      <PinOff className="w-3 h-3 text-zinc-400" />
                      <span>Unpin Column</span>
                    </>
                  ) : (
                    <>
                      <Pin className="w-3 h-3 text-zinc-400" />
                      <span>Pin to Left</span>
                    </>
                  )}
                </button>
              )}

              <button
                type="button"
                onClick={() => {
                  onResetWidth(column.id);
                  setIsMenuOpen(false);
                }}
                className="flex w-full items-center gap-2 rounded px-2 py-1.5 hover:bg-zinc-800 hover:text-zinc-100 text-left"
              >
                <RotateCcw className="w-3 h-3 text-zinc-400" />
                <span>Reset Width ({column.default_width}px)</span>
              </button>

              {column.can_hide && (
                <>
                  <div className="my-1 border-t border-zinc-800/80" />
                  <button
                    type="button"
                    onClick={() => {
                      onHideColumn(column.id);
                      setIsMenuOpen(false);
                    }}
                    className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100 text-left"
                  >
                    <EyeOff className="w-3 h-3" />
                    <span>Hide Column</span>
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Resize Handle */}
      {column.can_resize && (
        <div
          onMouseDown={handleResizeStart}
          onDoubleClick={() => onResetWidth(column.id)}
          className={`absolute top-0 right-0 w-2 h-full cursor-col-resize select-none hover:bg-zinc-500/40 ${
            isResizing ? "bg-zinc-400" : ""
          }`}
          title="Drag to resize (Double click to reset)"
        />
      )}
    </th>
  );
}
