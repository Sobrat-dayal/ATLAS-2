"use client";

import React, { useState, useRef, useEffect } from "react";
import { Layers, Check } from "lucide-react";
import { PRESET_BASEMAP_STYLES } from "@/lib/maps/styles";
import { MapBasemapStyle } from "@/lib/maps/types";

interface AtlasMapStyleSwitcherProps {
  currentStyleId: string;
  onStyleSelect: (style: MapBasemapStyle) => void;
}

export function AtlasMapStyleSwitcher({
  currentStyleId,
  onStyleSelect,
}: AtlasMapStyleSwitcherProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const current =
    PRESET_BASEMAP_STYLES.find((s) => s.style_id === currentStyleId) ||
    PRESET_BASEMAP_STYLES[0];

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="h-8 px-2.5 flex items-center gap-1.5 bg-atlas-surface-2 border border-atlas-border-default rounded text-xs text-atlas-text-secondary hover:text-atlas-text-primary hover:border-atlas-border-strong font-mono transition-colors"
        title="Switch Basemap Style"
      >
        <Layers className="w-3.5 h-3.5 text-blue-400" />
        <span className="hidden sm:inline">{current.display_name.replace("ATLAS ", "")}</span>
      </button>

      {isOpen && (
        <div className="absolute top-9 left-0 z-50 w-56 bg-atlas-surface-1 border border-atlas-border-default rounded shadow-xl overflow-hidden font-mono text-xs">
          <div className="px-3 py-1.5 text-[10px] text-atlas-text-muted bg-atlas-surface-2/60 border-b border-atlas-border-default uppercase font-semibold">
            Basemap Styles
          </div>
          <div className="p-1 space-y-0.5">
            {PRESET_BASEMAP_STYLES.map((style) => (
              <button
                key={style.style_id}
                type="button"
                onClick={() => {
                  onStyleSelect(style);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-2.5 py-1.5 rounded flex items-center justify-between text-xs transition-colors ${
                  style.style_id === currentStyleId
                    ? "bg-blue-600/20 text-blue-400 font-medium"
                    : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
                }`}
              >
                <div>
                  <div>{style.display_name}</div>
                  <div className="text-[10px] text-atlas-text-muted">{style.license_reference}</div>
                </div>
                {style.style_id === currentStyleId && <Check className="w-3.5 h-3.5 text-blue-400" />}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

