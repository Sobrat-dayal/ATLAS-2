"use client";

/**
 * Chart Drawing Toolbar Component for ATLAS Charts (Stage 71).
 *
 * Implements a compact left-side institutional drawing toolbar:
 * - Direct selection of all 9 canonical drawing tools.
 * - Cursor / Selection mode toggle.
 * - Visual active state, hover tooltips, and keyboard shortcuts.
 * - Smart Snapping toggle with status badge (OFF, BAR, OHLC).
 * - History command dispatchers (Undo, Redo).
 * - Drawing Manager list toggle and Clear All action.
 */

import React from "react";
import {
  ArrowLeftRight,
  ArrowUpDown,
  GitCommit,
  Layers,
  Magnet,
  Maximize2,
  Minus,
  MousePointer2,
  MoveRight,
  Redo2,
  Split,
  Square,
  Trash2,
  TrendingUp,
  Undo2,
} from "lucide-react";
import { DrawingType, SnappingMode } from "@/lib/charts/drawings/types";

export interface DrawingToolbarProps {
  activeTool: DrawingType | null;
  snappingMode: SnappingMode;
  canUndo: boolean;
  canRedo: boolean;
  drawingCount: number;
  isManagerOpen: boolean;
  onSelectTool: (tool: DrawingType | null) => void;
  onCycleSnapping: () => void;
  onUndo: () => void;
  onRedo: () => void;
  onToggleManager: () => void;
  onClearDrawings: () => void;
}

interface ToolButtonDef {
  type: DrawingType | null;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  shortcut?: string;
}

const TOOL_BUTTONS: ToolButtonDef[] = [
  { type: null, label: "Select / Move (Esc)", icon: MousePointer2, shortcut: "V" },
  { type: "trendline", label: "Trendline (2 points)", icon: TrendingUp, shortcut: "T" },
  { type: "horizontal_line", label: "Horizontal Line", icon: Minus, shortcut: "H" },
  { type: "horizontal_ray", label: "Horizontal Ray", icon: MoveRight, shortcut: "J" },
  { type: "vertical_line", label: "Vertical Line", icon: Split, shortcut: "Y" },
  { type: "rectangle", label: "Rectangle Zone", icon: Square, shortcut: "R" },
  { type: "price_range", label: "Price Range Measurement", icon: ArrowUpDown, shortcut: "P" },
  { type: "time_range", label: "Time Range Measurement", icon: ArrowLeftRight, shortcut: "M" },
  { type: "price_time_measure", label: "Price & Time Measurement", icon: Maximize2, shortcut: "D" },
  { type: "fibonacci_retracement", label: "Fibonacci Retracement", icon: GitCommit, shortcut: "F" },
];

export function DrawingToolbar({
  activeTool,
  snappingMode,
  canUndo,
  canRedo,
  drawingCount,
  isManagerOpen,
  onSelectTool,
  onCycleSnapping,
  onUndo,
  onRedo,
  onToggleManager,
  onClearDrawings,
}: DrawingToolbarProps) {
  return (
    <div
      className="flex flex-col items-center bg-zinc-950/95 border-r border-zinc-800/80 p-1.5 gap-1 select-none z-20 backdrop-blur"
      role="toolbar"
      aria-label="Chart Drawing Tools"
    >
      {/* Tool Selection Buttons */}
      <div className="flex flex-col gap-0.5">
        {TOOL_BUTTONS.map((btn) => {
          const Icon = btn.icon;
          const isActive = activeTool === btn.type;

          return (
            <button
              key={btn.type || "select"}
              onClick={() => onSelectTool(isActive && btn.type !== null ? null : btn.type)}
              title={`${btn.label}${btn.shortcut ? ` [${btn.shortcut}]` : ""}`}
              aria-label={btn.label}
              aria-pressed={isActive}
              className={`relative group w-8 h-8 rounded flex items-center justify-center transition-colors ${
                isActive
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 border border-transparent"
              }`}
            >
              <Icon className="w-4 h-4" />
              {/* Tooltip */}
              <span className="absolute left-10 hidden group-hover:flex items-center px-2 py-1 rounded bg-zinc-900 border border-zinc-700/80 text-[11px] font-mono text-zinc-200 whitespace-nowrap shadow-xl z-50 pointer-events-none">
                {btn.label}
              </span>
            </button>
          );
        })}
      </div>

      <div className="w-5 h-px bg-zinc-800/80 my-1" />

      {/* Smart Snapping Toggle */}
      <button
        onClick={onCycleSnapping}
        title={`Smart Snapping: ${snappingMode} (Click to toggle)`}
        aria-label={`Smart Snapping: ${snappingMode}`}
        className={`relative group w-8 h-8 rounded flex flex-col items-center justify-center transition-colors ${
          snappingMode !== "OFF"
            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
            : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/80 border border-transparent"
        }`}
      >
        <Magnet className="w-3.5 h-3.5" />
        <span className="text-[8px] font-mono font-bold leading-none mt-0.5">
          {snappingMode === "OFF" ? "OFF" : snappingMode === "NEAREST_BAR" ? "BAR" : "OHLC"}
        </span>
        {/* Tooltip */}
        <span className="absolute left-10 hidden group-hover:flex items-center px-2 py-1 rounded bg-zinc-900 border border-zinc-700/80 text-[11px] font-mono text-zinc-200 whitespace-nowrap shadow-xl z-50 pointer-events-none">
          Smart Snapping: {snappingMode}
        </span>
      </button>

      <div className="w-5 h-px bg-zinc-800/80 my-1" />

      {/* History Controls: Undo & Redo */}
      <div className="flex flex-col gap-0.5">
        <button
          onClick={onUndo}
          disabled={!canUndo}
          title="Undo (Ctrl+Z)"
          aria-label="Undo"
          className="relative group w-8 h-8 rounded flex items-center justify-center text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-zinc-400 border border-transparent transition-colors"
        >
          <Undo2 className="w-4 h-4" />
          <span className="absolute left-10 hidden group-hover:flex items-center px-2 py-1 rounded bg-zinc-900 border border-zinc-700/80 text-[11px] font-mono text-zinc-200 whitespace-nowrap shadow-xl z-50 pointer-events-none">
            Undo (Ctrl+Z)
          </span>
        </button>

        <button
          onClick={onRedo}
          disabled={!canRedo}
          title="Redo (Ctrl+Shift+Z)"
          aria-label="Redo"
          className="relative group w-8 h-8 rounded flex items-center justify-center text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-zinc-400 border border-transparent transition-colors"
        >
          <Redo2 className="w-4 h-4" />
          <span className="absolute left-10 hidden group-hover:flex items-center px-2 py-1 rounded bg-zinc-900 border border-zinc-700/80 text-[11px] font-mono text-zinc-200 whitespace-nowrap shadow-xl z-50 pointer-events-none">
            Redo (Ctrl+Shift+Z)
          </span>
        </button>
      </div>

      <div className="w-5 h-px bg-zinc-800/80 my-1" />

      {/* Drawing Manager List Toggle */}
      <button
        onClick={onToggleManager}
        title={`Drawings Manager (${drawingCount})`}
        aria-label="Drawings Manager"
        className={`relative group w-8 h-8 rounded flex items-center justify-center transition-colors ${
          isManagerOpen
            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
            : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 border border-transparent"
        }`}
      >
        <Layers className="w-4 h-4" />
        {drawingCount > 0 && (
          <span className="absolute -top-1 -right-1 px-1 min-w-[14px] h-[14px] rounded-full bg-cyan-500 text-black text-[9px] font-bold font-mono flex items-center justify-center">
            {drawingCount}
          </span>
        )}
        <span className="absolute left-10 hidden group-hover:flex items-center px-2 py-1 rounded bg-zinc-900 border border-zinc-700/80 text-[11px] font-mono text-zinc-200 whitespace-nowrap shadow-xl z-50 pointer-events-none">
          Drawing Manager ({drawingCount})
        </span>
      </button>

      {/* Clear Drawings */}
      <button
        onClick={onClearDrawings}
        disabled={drawingCount === 0}
        title="Clear All Drawings"
        aria-label="Clear All Drawings"
        className="relative group w-8 h-8 rounded flex items-center justify-center text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-zinc-400 border border-transparent transition-colors"
      >
        <Trash2 className="w-4 h-4" />
        <span className="absolute left-10 hidden group-hover:flex items-center px-2 py-1 rounded bg-zinc-900 border border-zinc-700/80 text-[11px] font-mono text-zinc-200 whitespace-nowrap shadow-xl z-50 pointer-events-none">
          Clear All Drawings
        </span>
      </button>
    </div>
  );
}
