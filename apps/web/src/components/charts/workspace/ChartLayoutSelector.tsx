"use client";

/**
 * Chart Layout Selector Component for ATLAS Charts (Stage 72).
 *
 * Provides institutional layout switching for:
 * - Single full-area chart
 * - Two-column horizontal split
 * - Two-row vertical split
 * - Three-chart left-focus
 * - Three-chart top-focus
 * - Four-chart 2x2 grid
 *
 * Visual grid mini-diagrams, keyboard accessibility, and state persistence.
 */

import React, { useEffect, useRef, useState } from "react";
import { ChevronDown, LayoutGrid } from "lucide-react";
import {
  CHART_LAYOUTS,
  ChartLayoutId,
  ORDERED_LAYOUT_IDS,
} from "@/lib/charts/workspace";

export interface ChartLayoutSelectorProps {
  currentLayout: ChartLayoutId;
  onSelectLayout: (layoutId: ChartLayoutId) => void;
  disabled?: boolean;
}

function LayoutIcon({ id, className = "w-4 h-4" }: { id: ChartLayoutId; className?: string }) {
  switch (id) {
    case "single":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor">
          <rect x="2" y="2" width="12" height="12" rx="1.5" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
        </svg>
      );
    case "two-columns":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor">
          <rect x="2" y="2" width="5.5" height="12" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="8.5" y="2" width="5.5" height="12" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
        </svg>
      );
    case "two-rows":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor">
          <rect x="2" y="2" width="12" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="2" y="8.5" width="12" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
        </svg>
      );
    case "three-left-focus":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor">
          <rect x="2" y="2" width="7" height="12" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="10" y="2" width="4" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="10" y="8.5" width="4" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
        </svg>
      );
    case "three-top-focus":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor">
          <rect x="2" y="2" width="12" height="6.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="2" y="9.5" width="5.5" height="4.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="8.5" y="9.5" width="5.5" height="4.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
        </svg>
      );
    case "four-grid":
      return (
        <svg viewBox="0 0 16 16" className={className} fill="none" stroke="currentColor">
          <rect x="2" y="2" width="5.5" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="8.5" y="2" width="5.5" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="2" y="8.5" width="5.5" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
          <rect x="8.5" y="8.5" width="5.5" height="5.5" rx="1" strokeWidth="1.5" fill="currentColor" fillOpacity="0.2" />
        </svg>
      );
    default:
      return <LayoutGrid className={className} />;
  }
}

export function ChartLayoutSelector({
  currentLayout,
  onSelectLayout,
  disabled = false,
}: ChartLayoutSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const activeDef = CHART_LAYOUTS[currentLayout] || CHART_LAYOUTS.single;

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [isOpen]);

  // Close on escape
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  return (
    <div className="relative inline-block text-left" ref={containerRef}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded font-mono font-medium border text-xs transition-colors ${
          isOpen
            ? "bg-cyan-950/70 border-cyan-500/80 text-cyan-300"
            : "bg-zinc-950 border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-zinc-100"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        title={`Chart Layout: ${activeDef.label} (Click to switch)`}
        aria-label="Multi-chart layout selector"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <LayoutIcon id={currentLayout} className="w-3.5 h-3.5 text-cyan-400" />
        <span className="hidden sm:inline">{activeDef.label}</span>
        <ChevronDown className="w-3 h-3 text-zinc-400" />
      </button>

      {isOpen && (
        <div
          role="menu"
          aria-orientation="vertical"
          className="absolute right-0 sm:left-0 top-full mt-1.5 w-64 bg-zinc-950 border border-zinc-800 rounded-md shadow-2xl z-50 p-1.5 divide-y divide-zinc-900"
        >
          <div className="px-2 py-1 text-[11px] font-mono text-zinc-500 uppercase tracking-wider font-semibold">
            Multi-Chart Layout Presets (V1)
          </div>

          <div className="grid grid-cols-2 gap-1.5 pt-1.5">
            {ORDERED_LAYOUT_IDS.map((layoutId) => {
              const def = CHART_LAYOUTS[layoutId];
              const isSelected = layoutId === currentLayout;

              return (
                <button
                  key={layoutId}
                  type="button"
                  role="menuitem"
                  onClick={() => {
                    onSelectLayout(layoutId);
                    setIsOpen(false);
                  }}
                  className={`flex flex-col items-center gap-1.5 p-2 rounded border text-center transition-all ${
                    isSelected
                      ? "bg-cyan-950/60 border-cyan-500/80 text-cyan-200"
                      : "bg-zinc-900/60 border-zinc-800/80 hover:bg-zinc-800/80 hover:border-zinc-700 text-zinc-300"
                  }`}
                  title={def.description}
                >
                  <LayoutIcon
                    id={layoutId}
                    className={`w-6 h-6 ${isSelected ? "text-cyan-400" : "text-zinc-400"}`}
                  />
                  <div className="flex flex-col items-center">
                    <span className="text-[11px] font-mono font-medium leading-tight">
                      {def.label}
                    </span>
                    <span className="text-[9px] font-mono text-zinc-500">
                      {def.panelCount} {def.panelCount === 1 ? "panel" : "panels"}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="px-2 pt-2 text-[10px] text-zinc-500 leading-tight">
            Independent instruments, intervals, technical indicators, and drawings per panel.
          </div>
        </div>
      )}
    </div>
  );
}
