"use client";

/**
 * Drawing Settings Panel Component for ATLAS Charts (Stage 71).
 *
 * Implements an institutional floating/docked toolbar for inspecting and modifying
 * the active selected drawing:
 * - Color palette picker (institutional color accents).
 * - Line width selector (1, 2, 3, 4px).
 * - Line stroke style (Solid, Dashed, Dotted).
 * - Fill opacity slider for zone & measurement shapes.
 * - Lock/Unlock protection against accidental edits.
 * - Visibility toggle.
 * - Direct numerical coordinate editor modal launcher.
 * - Delete action.
 */

import React from "react";
import {
  Edit3,
  Eye,
  EyeOff,
  Lock,
  Minus,
  Trash2,
  Unlock,
} from "lucide-react";
import { DrawingObject, DrawingStyle, LineStrokeStyle } from "@/lib/charts/drawings/types";

export interface DrawingSettingsPanelProps {
  drawing: DrawingObject | null;
  onUpdateStyle: (drawingId: string, style: Partial<DrawingStyle>) => void;
  onToggleLock: (drawingId: string) => void;
  onToggleVisibility: (drawingId: string) => void;
  onDelete: (drawingId: string) => void;
  onOpenCoordinateEditor: (drawing: DrawingObject) => void;
  onClose: () => void;
}

const COLOR_PALETTE = [
  { name: "Cyan", value: "#38bdf8" },
  { name: "Emerald", value: "#10b981" },
  { name: "Amber", value: "#f59e0b" },
  { name: "Purple", value: "#a855f7" },
  { name: "Rose", value: "#f43f5e" },
  { name: "Zinc", value: "#e4e4e7" },
];

const STROKE_STYLES: { label: string; value: LineStrokeStyle }[] = [
  { label: "Solid", value: "solid" },
  { label: "Dashed", value: "dashed" },
  { label: "Dotted", value: "dotted" },
];

export function DrawingSettingsPanel({
  drawing,
  onUpdateStyle,
  onToggleLock,
  onToggleVisibility,
  onDelete,
  onOpenCoordinateEditor,
  onClose,
}: DrawingSettingsPanelProps) {
  if (!drawing) return null;

  const isZoneOrMeasure =
    drawing.type === "rectangle" ||
    drawing.type === "price_range" ||
    drawing.type === "time_range" ||
    drawing.type === "price_time_measure";

  return (
    <div
      className="absolute top-3 left-1/2 -translate-x-1/2 bg-zinc-950/95 border border-zinc-700/80 rounded-md shadow-2xl p-1.5 flex items-center gap-2 z-30 backdrop-blur select-none text-zinc-200"
      role="dialog"
      aria-label="Drawing Settings"
    >
      {/* Drawing Type Badge */}
      <div className="flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-cyan-400 font-medium">
        <span>{drawing.type.replace(/_/g, " ").toUpperCase()}</span>
      </div>

      <div className="w-px h-5 bg-zinc-800" />

      {/* Color Palette */}
      <div className="flex items-center gap-1">
        {COLOR_PALETTE.map((c) => (
          <button
            key={c.value}
            onClick={() => onUpdateStyle(drawing.id, { color: c.value })}
            title={c.name}
            className={`w-4 h-4 rounded-full transition-transform ${
              drawing.style.color === c.value
                ? "ring-2 ring-white ring-offset-1 ring-offset-zinc-950 scale-110"
                : "hover:scale-105 opacity-80 hover:opacity-100"
            }`}
            style={{ backgroundColor: c.value }}
          />
        ))}
      </div>

      <div className="w-px h-5 bg-zinc-800" />

      {/* Line Width */}
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4].map((w) => (
          <button
            key={w}
            onClick={() => onUpdateStyle(drawing.id, { lineWidth: w })}
            title={`Line Width: ${w}px`}
            className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-medium transition-colors ${
              drawing.style.lineWidth === w
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
            }`}
          >
            {w}px
          </button>
        ))}
      </div>

      <div className="w-px h-5 bg-zinc-800" />

      {/* Line Stroke Style */}
      <div className="flex items-center gap-1">
        {STROKE_STYLES.map((s) => (
          <button
            key={s.value}
            onClick={() => onUpdateStyle(drawing.id, { lineStyle: s.value })}
            title={`Line Style: ${s.label}`}
            className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-medium transition-colors ${
              drawing.style.lineStyle === s.value
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Fill Opacity Slider for Zones & Measurements */}
      {isZoneOrMeasure && (
        <>
          <div className="w-px h-5 bg-zinc-800" />
          <div className="flex items-center gap-1.5 px-1 text-[10px] font-mono text-zinc-400">
            <span>Fill:</span>
            <input
              type="range"
              min="0"
              max="0.5"
              step="0.05"
              value={drawing.style.fillOpacity}
              onChange={(e) =>
                onUpdateStyle(drawing.id, { fillOpacity: parseFloat(e.target.value) })
              }
              className="w-14 h-1 accent-cyan-400 bg-zinc-800 rounded cursor-pointer"
              title={`Fill Opacity: ${(drawing.style.fillOpacity * 100).toFixed(0)}%`}
            />
          </div>
        </>
      )}

      <div className="w-px h-5 bg-zinc-800" />

      {/* Numerical Coordinate Editor Button */}
      <button
        onClick={() => onOpenCoordinateEditor(drawing)}
        title="Edit Financial Coordinates"
        className="p-1 rounded text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
      >
        <Edit3 className="w-3.5 h-3.5" />
      </button>

      {/* Lock Toggle */}
      <button
        onClick={() => onToggleLock(drawing.id)}
        title={drawing.locked ? "Unlock Drawing" : "Lock Drawing"}
        className={`p-1 rounded transition-colors ${
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
        title={drawing.visible ? "Hide Drawing" : "Show Drawing"}
        className={`p-1 rounded transition-colors ${
          !drawing.visible
            ? "text-zinc-500 bg-zinc-900"
            : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
        }`}
      >
        {drawing.visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
      </button>

      {/* Delete Button */}
      <button
        onClick={() => onDelete(drawing.id)}
        title="Delete Drawing (Del)"
        className="p-1 rounded text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>

      {/* Close Panel Button */}
      <button
        onClick={onClose}
        title="Deselect"
        className="p-1 rounded text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors text-xs font-mono"
      >
        ✕
      </button>
    </div>
  );
}
