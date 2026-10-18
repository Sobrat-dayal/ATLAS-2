"use client";

/**
 * Accessible Numerical Coordinate Editor Component for ATLAS Charts (Stage 71).
 *
 * Provides institutional keyboard and screen-reader access to precision financial
 * coordinates { time, price } for every drawing anchor:
 * - Direct numeric input for price levels.
 * - Date/time picker and Unix timestamp editor for time anchors.
 * - Non-NaN and finite coordinate validation.
 * - Atomic commit to DrawingSessionStore with Undo tracking.
 */

import React, { useState } from "react";
import { DrawingAnchor, DrawingObject } from "@/lib/charts/drawings/types";

export interface DrawingCoordinateEditorProps {
  drawing: DrawingObject | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (drawingId: string, updatedAnchors: DrawingAnchor[]) => void;
}

export function DrawingCoordinateEditor({
  drawing,
  isOpen,
  onClose,
  onSave,
}: DrawingCoordinateEditorProps) {
  if (!isOpen || !drawing) return null;

  const [anchors, setAnchors] = useState<DrawingAnchor[]>(() =>
    JSON.parse(JSON.stringify(drawing.anchors))
  );
  const [error, setError] = useState<string | null>(null);

  const handlePriceChange = (index: number, val: string) => {
    const num = parseFloat(val);
    setAnchors((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], price: isNaN(num) ? 0 : num };
      return copy;
    });
  };

  const handleTimeChange = (index: number, val: string) => {
    // Attempt parsing ISO string or date
    const parsed = Date.parse(val);
    if (!isNaN(parsed)) {
      const unixSec = Math.floor(parsed / 1000);
      setAnchors((prev) => {
        const copy = [...prev];
        copy[index] = { ...copy[index], time: unixSec };
        return copy;
      });
    }
  };

  const handleTimestampChange = (index: number, val: string) => {
    const num = parseInt(val, 10);
    if (!isNaN(num)) {
      setAnchors((prev) => {
        const copy = [...prev];
        copy[index] = { ...copy[index], time: num };
        return copy;
      });
    }
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    for (let i = 0; i < anchors.length; i++) {
      const a = anchors[i];
      if (isNaN(a.price) || !isFinite(a.price)) {
        setError(`Anchor ${i + 1} has an invalid price value.`);
        return;
      }
      if (isNaN(a.time) || a.time <= 0) {
        setError(`Anchor ${i + 1} has an invalid timestamp value.`);
        return;
      }
    }

    onSave(drawing.id, anchors);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 select-none"
      role="dialog"
      aria-modal="true"
      aria-labelledby="coord-editor-title"
    >
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg shadow-2xl w-full max-w-md overflow-hidden text-zinc-100 font-sans">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/60">
          <div>
            <h2 id="coord-editor-title" className="text-sm font-bold font-mono tracking-tight text-zinc-100">
              FINANCIAL COORDINATE EDITOR
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5 font-mono">
              {drawing.type.replace(/_/g, " ").toUpperCase()} [{drawing.id.substring(0, 10)}]
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-200 p-1 text-sm font-mono"
            aria-label="Close coordinate editor"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSave} className="p-4 flex flex-col gap-4">
          {error && (
            <div className="p-2 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono">
              {error}
            </div>
          )}

          {anchors.map((anchor, idx) => {
            const dateStr = new Date(anchor.time * 1000).toISOString().slice(0, 16);

            return (
              <div
                key={idx}
                className="flex flex-col gap-2 p-3 rounded bg-zinc-900/50 border border-zinc-800/80"
              >
                <div className="text-xs font-mono font-semibold text-cyan-400">
                  ANCHOR {idx + 1}
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {/* Price Input */}
                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-mono text-zinc-400">
                      Price ({drawing.context.quotation_unit || "USD"}):
                    </label>
                    <input
                      type="number"
                      step="any"
                      value={anchor.price}
                      onChange={(e) => handlePriceChange(idx, e.target.value)}
                      className="w-full px-2 py-1 bg-zinc-950 border border-zinc-700 rounded text-xs font-mono text-zinc-100 focus:outline-none focus:border-cyan-500"
                      required
                    />
                  </div>

                  {/* Date Input */}
                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-mono text-zinc-400">Date/Time (UTC):</label>
                    <input
                      type="datetime-local"
                      value={dateStr}
                      onChange={(e) => handleTimeChange(idx, e.target.value)}
                      className="w-full px-2 py-1 bg-zinc-950 border border-zinc-700 rounded text-xs font-mono text-zinc-100 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                {/* Unix timestamp input */}
                <div className="flex items-center justify-between text-[10px] font-mono text-zinc-500">
                  <span>Unix Timestamp (sec):</span>
                  <input
                    type="number"
                    value={anchor.time}
                    onChange={(e) => handleTimestampChange(idx, e.target.value)}
                    className="w-32 px-1.5 py-0.5 bg-zinc-950 border border-zinc-800 rounded text-[10px] font-mono text-zinc-400"
                  />
                </div>
              </div>
            );
          })}

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded text-xs font-mono text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3 py-1.5 rounded text-xs font-mono font-medium bg-cyan-600 hover:bg-cyan-500 text-black shadow-md transition-colors"
            >
              Apply Coordinates
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
