"use client";

import { useAtlasApplicationContext, AtlasTimeRangePreset } from "@/hooks/application-context";
import { Clock } from "lucide-react";
import { useState, useRef, useEffect } from "react";

const PRESETS: { label: string; value: AtlasTimeRangePreset }[] = [
  { label: "1D", value: "1d" },
  { label: "5D", value: "5d" },
  { label: "1M", value: "1m" },
  { label: "3M", value: "3m" },
  { label: "6M", value: "6m" },
  { label: "YTD", value: "ytd" },
  { label: "1Y", value: "1y" },
  { label: "5Y", value: "5y" },
  { label: "MAX", value: "max" },
];

export function GlobalTimeRangeControl() {
  const { timeRange, setTimeRangePreset } = useAtlasApplicationContext();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const displayLabel = timeRange.mode === "preset" && timeRange.preset
    ? PRESETS.find(p => p.value === timeRange.preset)?.label || timeRange.preset.toUpperCase()
    : "CUSTOM";

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 h-7 px-2 rounded-sm bg-atlas-surface-2 border border-atlas-border-default text-xs font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors"
        title="Global Analysis Timeframe"
        aria-label="Global Time Range"
      >
        <Clock className="h-3.5 w-3.5" />
        <span>{displayLabel}</span>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-32 bg-atlas-surface-2 border border-atlas-border-default rounded-sm shadow-xl z-50 overflow-hidden">
          <div className="px-2 py-1.5 text-[10px] font-bold text-atlas-text-muted uppercase tracking-wider border-b border-atlas-border-default">
            Analysis Range
          </div>
          <div className="py-1">
            {PRESETS.map((preset) => (
              <button
                key={preset.value}
                onClick={() => {
                  setTimeRangePreset(preset.value);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-1.5 text-xs transition-colors ${
                  timeRange.preset === preset.value
                    ? "bg-atlas-surface-selected text-atlas-accent font-medium"
                    : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
