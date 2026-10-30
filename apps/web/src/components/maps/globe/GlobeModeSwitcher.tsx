/**
 * 2D / 3D Map Mode Segmented Controller (Stage 130).
 *
 * Provides instant, lossless switching between 2D MapLibre and 3D Cesium Earth.
 */

"use client";

import React from "react";
import { RendererMode } from "@/lib/maps/globe/types";
import { Map, Globe } from "lucide-react";

interface GlobeModeSwitcherProps {
  mode: RendererMode;
  onModeChange: (mode: RendererMode) => void;
  disabled?: boolean;
}

export function GlobeModeSwitcher({
  mode,
  onModeChange,
  disabled = false,
}: GlobeModeSwitcherProps) {
  return (
    <div
      role="group"
      aria-label="Map Mode Selector"
      className="inline-flex items-center rounded bg-atlas-surface-2 p-0.5 border border-atlas-border-subtle shadow-sm"
    >
      <button
        type="button"
        disabled={disabled}
        onClick={() => onModeChange("2D")}
        className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded transition-colors ${
          mode === "2D"
            ? "bg-atlas-surface-selected text-atlas-text-primary shadow-xs font-semibold"
            : "text-atlas-text-muted hover:text-atlas-text-primary"
        } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
        aria-pressed={mode === "2D"}
      >
        <Map className="w-3.5 h-3.5" />
        <span>2D Map</span>
      </button>

      <button
        type="button"
        disabled={disabled}
        onClick={() => onModeChange("3D")}
        className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded transition-colors ${
          mode === "3D"
            ? "bg-atlas-accent text-white shadow-xs font-semibold"
            : "text-atlas-text-muted hover:text-atlas-text-primary"
        } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
        aria-pressed={mode === "3D"}
      >
        <Globe className="w-3.5 h-3.5" />
        <span>3D Earth</span>
      </button>
    </div>
  );
}

