/**
 * 3D Globe Navigation and Command Toolbar (Stage 130).
 *
 * Houses the 2D/3D mode switcher, geographic search bar, camera orientation,
 * zoom controls, tilt toggle, and layer/inspector triggers.
 */

"use client";

import React, { useState } from "react";
import { RendererMode, AtlasGlobeCamera } from "@/lib/maps/globe/types";
import { GlobeModeSwitcher } from "./GlobeModeSwitcher";
import {
  ZoomIn,
  ZoomOut,
  Compass,
  RotateCw,
  Layers,
  Info,
  Bookmark,
  Search,
  Maximize2,
  Globe,
} from "lucide-react";

interface GlobeToolbarProps {
  mode: RendererMode;
  onModeChange: (mode: RendererMode) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetOrientation: () => void;
  onResetGlobalView: () => void;
  onToggleTilt: () => void;
  isTiltActive: boolean;
  onToggleLayers: () => void;
  isLayersOpen: boolean;
  onToggleInspector: () => void;
  isInspectorOpen: boolean;
  onOpenSaveDialog: () => void;
  onSearchSelect?: (item: { lon: number; lat: number; label: string }) => void;
}

export function GlobeToolbar({
  mode,
  onModeChange,
  onZoomIn,
  onZoomOut,
  onResetOrientation,
  onResetGlobalView,
  onToggleTilt,
  isTiltActive,
  onToggleLayers,
  isLayersOpen,
  onToggleInspector,
  isInspectorOpen,
  onOpenSaveDialog,
  onSearchSelect,
}: GlobeToolbarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Quick geocoding lookup for institutional hubs
  const handleSearch = (q: string) => {
    setSearchQuery(q);
    if (!q.trim()) {
      setSearchResults([]);
      return;
    }
    const lower = q.toLowerCase();
    const hubs = [
      { label: "London Financial Core", lon: -0.1276, lat: 51.5074 },
      { label: "New York Wall Street", lon: -74.006, lat: 40.7128 },
      { label: "Tokyo Stock Exchange", lon: 139.7714, lat: 35.6812 },
      { label: "Frankfurt Financial District", lon: 8.6821, lat: 50.1109 },
      { label: "Singapore Financial Hub", lon: 103.851959, lat: 1.29027 },
      { label: "Hong Kong Central", lon: 114.1588, lat: 22.2819 },
      { label: "Zurich Financial Center", lon: 8.5417, lat: 47.3769 },
      { label: "Paris La Défense", lon: 2.2415, lat: 48.8924 },
    ];
    setSearchResults(hubs.filter((h) => h.label.toLowerCase().includes(lower)));
  };

  return (
    <div
      aria-label="3D Globe Navigation Bar"
      className="absolute top-3 left-4 right-4 z-10 flex items-center justify-between pointer-events-none"
    >
      {/* Left Segment: Mode Switcher & Quick Navigation */}
      <div className="flex items-center gap-2 pointer-events-auto">
        <GlobeModeSwitcher mode={mode} onModeChange={onModeChange} />

        {/* Search Bar */}
        <div className="relative">
          <div className="flex items-center rounded bg-atlas-surface-1/90 backdrop-blur-md border border-atlas-border-subtle px-2.5 py-1 text-xs text-atlas-text-primary shadow-sm w-56 focus-within:w-72 focus-within:border-atlas-accent transition-all">
            <Search className="w-3.5 h-3.5 text-atlas-text-muted mr-1.5 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search financial hubs or coordinates..."
              className="bg-transparent border-none outline-hidden text-xs text-atlas-text-primary placeholder:text-atlas-text-muted w-full"
            />
          </div>

          {/* Search Dropdown */}
          {searchResults.length > 0 && (
            <div className="absolute top-full left-0 mt-1 w-full rounded bg-atlas-surface-1 border border-atlas-border-default shadow-xl overflow-hidden py-1 z-30">
              {searchResults.map((res, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    if (onSearchSelect) onSearchSelect(res);
                    setSearchQuery("");
                    setSearchResults([]);
                  }}
                  className="w-full text-left px-3 py-1.5 text-xs text-atlas-text-primary hover:bg-atlas-surface-hover flex items-center justify-between cursor-pointer"
                >
                  <span className="font-medium truncate">{res.label}</span>
                  <span className="text-[10px] text-atlas-text-muted font-mono ml-2">
                    {res.lat.toFixed(2)}°, {res.lon.toFixed(2)}°
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Segment: Camera Controls & Overlays */}
      <div className="flex items-center gap-1.5 pointer-events-auto bg-atlas-surface-1/90 backdrop-blur-md border border-atlas-border-subtle p-1 rounded shadow-sm text-atlas-text-muted">
        <button
          type="button"
          onClick={onResetGlobalView}
          title="Reset to Global Earth View"
          className="p-1.5 rounded hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
        >
          <Globe className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onToggleTilt}
          title={isTiltActive ? "Reset to Top-Down Nadir" : "Tilt to 45° Angled Perspective"}
          className={`p-1.5 rounded transition-colors cursor-pointer ${
            isTiltActive
              ? "text-atlas-accent bg-atlas-accent/10"
              : "hover:text-atlas-text-primary hover:bg-atlas-surface-hover"
          }`}
        >
          <RotateCw className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onResetOrientation}
          title="Reset Orientation to North (Heading = 0°)"
          className="p-1.5 rounded hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
        >
          <Compass className="w-4 h-4" />
        </button>

        <div className="w-[1px] h-4 bg-atlas-border-subtle mx-0.5" />

        <button
          type="button"
          onClick={onZoomIn}
          title="Zoom In"
          className="p-1.5 rounded hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
        >
          <ZoomIn className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onZoomOut}
          title="Zoom Out"
          className="p-1.5 rounded hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
        >
          <ZoomOut className="w-4 h-4" />
        </button>

        <div className="w-[1px] h-4 bg-atlas-border-subtle mx-0.5" />

        <button
          type="button"
          onClick={onToggleLayers}
          title="Toggle Globe Layer Manager"
          className={`p-1.5 rounded transition-colors cursor-pointer ${
            isLayersOpen
              ? "text-atlas-accent bg-atlas-accent/10"
              : "hover:text-atlas-text-primary hover:bg-atlas-surface-hover"
          }`}
        >
          <Layers className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onToggleInspector}
          title="Toggle Feature Inspector"
          className={`p-1.5 rounded transition-colors cursor-pointer ${
            isInspectorOpen
              ? "text-atlas-accent bg-atlas-accent/10"
              : "hover:text-atlas-text-primary hover:bg-atlas-surface-hover"
          }`}
        >
          <Info className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={onOpenSaveDialog}
          title="Save 3D Globe View"
          className="p-1.5 rounded hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer text-atlas-accent"
        >
          <Bookmark className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
