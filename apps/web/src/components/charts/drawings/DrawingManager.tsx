"use client";

/**
 * Accessible Drawing Manager Drawer Component for ATLAS Charts (Stage 71).
 *
 * Implements an institutional list view of all active chart drawings:
 * - Direct row-click selection.
 * - Lock/Unlock and Visibility toggles per drawing.
 * - Coordinate editing modal launcher.
 * - Individual and batch deletion.
 * - Full keyboard navigation and screen-reader accessibility.
 */

import React from "react";
import { Edit3, Eye, EyeOff, Lock, Trash2, Unlock, X } from "lucide-react";
import { DrawingObject } from "@/lib/charts/drawings/types";

export interface DrawingManagerProps {
  isOpen: boolean;
  drawings: DrawingObject[];
  selectedDrawingId: string | null;
  onClose: () => void;
  onSelectDrawing: (id: string) => void;
  onToggleLock: (id: string) => void;
  onToggleVisibility: (id: string) => void;
  onDelete: (id: string) => void;
  onClearAll: () => void;
  onOpenCoordinateEditor: (drawing: DrawingObject) => void;
}

export function DrawingManager({
  isOpen,
  drawings,
  selectedDrawingId,
  onClose,
  onSelectDrawing,
  onToggleLock,
  onToggleVisibility,
  onDelete,
  onClearAll,
  onOpenCoordinateEditor,
}: DrawingManagerProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-y-0 right-0 z-40 w-80 md:w-96 bg-zinc-950 border-l border-zinc-800 shadow-2xl flex flex-col select-none text-zinc-100 font-sans"
      role="region"
      aria-label="Drawing Manager"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/60">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-bold font-mono tracking-tight text-zinc-100">
            DRAWING MANAGER
          </h2>
          <span className="px-1.5 py-0.5 text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 rounded">
            {drawings.length}
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-zinc-400 hover:text-zinc-100 p-1 rounded hover:bg-zinc-800"
          aria-label="Close drawing manager"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Drawing List */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
        {drawings.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-zinc-500 text-xs font-mono">
            <span>No drawings on chart</span>
            <span className="text-[10px] mt-1 text-zinc-600">
              Select a tool from the left toolbar to draw
            </span>
          </div>
        ) : (
          drawings.map((drawing) => {
            const isSelected = drawing.id === selectedDrawingId;
            const primaryPrice = drawing.anchors[0]?.price.toFixed(2) ?? "0.00";
            const secondaryPrice =
              drawing.anchors.length > 1
                ? ` → ${drawing.anchors[1]?.price.toFixed(2)}`
                : "";

            return (
              <div
                key={drawing.id}
                onClick={() => onSelectDrawing(drawing.id)}
                className={`flex items-center justify-between p-2.5 rounded border transition-colors cursor-pointer ${
                  isSelected
                    ? "bg-cyan-950/40 border-cyan-500/60 shadow-sm"
                    : "bg-zinc-900/40 border-zinc-800/80 hover:bg-zinc-800/60 hover:border-zinc-700"
                }`}
              >
                {/* Info */}
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: drawing.style.color }}
                  />
                  <div className="flex flex-col min-w-0">
                    <span className="text-xs font-mono font-medium text-zinc-200 truncate">
                      {drawing.type.replace(/_/g, " ").toUpperCase()}
                    </span>
                    <span className="text-[10px] font-mono text-zinc-400">
                      ${primaryPrice}
                      {secondaryPrice}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div
                  className="flex items-center gap-1 flex-shrink-0"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Coordinate Editor */}
                  <button
                    onClick={() => onOpenCoordinateEditor(drawing)}
                    title="Edit Coordinates"
                    className="p-1 rounded text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>

                  {/* Lock Toggle */}
                  <button
                    onClick={() => onToggleLock(drawing.id)}
                    title={drawing.locked ? "Unlock" : "Lock"}
                    className={`p-1 rounded ${
                      drawing.locked
                        ? "text-amber-400 bg-amber-500/10"
                        : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
                    }`}
                  >
                    {drawing.locked ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
                  </button>

                  {/* Visibility Toggle */}
                  <button
                    onClick={() => onToggleVisibility(drawing.id)}
                    title={drawing.visible ? "Hide" : "Show"}
                    className={`p-1 rounded ${
                      !drawing.visible
                        ? "text-zinc-600"
                        : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
                    }`}
                  >
                    {drawing.visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                  </button>

                  {/* Delete */}
                  <button
                    onClick={() => onDelete(drawing.id)}
                    title="Delete"
                    className="p-1 rounded text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      {drawings.length > 0 && (
        <div className="p-3 border-t border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
          <span className="text-[11px] font-mono text-zinc-400">
            Capacity: {drawings.length} / 250
          </span>
          <button
            onClick={onClearAll}
            className="px-2.5 py-1 rounded bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-mono flex items-center gap-1 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear All</span>
          </button>
        </div>
      )}
    </div>
  );
}
