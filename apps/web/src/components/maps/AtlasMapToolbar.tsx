"use client";

import React from "react";
import {
  Plus,
  Minus,
  Compass,
  Maximize,
  Bookmark,
  FolderOpen,
  PanelLeft,
  PanelRight,
  Building2,
} from "lucide-react";
import { AtlasMapSearch } from "./AtlasMapSearch";
import { AtlasMapStyleSwitcher } from "./AtlasMapStyleSwitcher";
import { GlobeModeSwitcher } from "./globe/GlobeModeSwitcher";
import { SpatialAnalyticsToolbar } from "./analytics/SpatialAnalyticsToolbar";
import { GeographicSearchResult, MapBasemapStyle } from "@/lib/maps/types";
import { RendererMode } from "@/lib/maps/globe/types";

interface AtlasMapToolbarProps {
  currentStyleId: string;
  onStyleSelect: (style: MapBasemapStyle) => void;
  rendererMode?: RendererMode;
  onModeChange?: (mode: RendererMode) => void;
  isAnalyticsOpen?: boolean;
  onToggleAnalytics?: () => void;
  isCorporateModeOpen?: boolean;
  onToggleCorporateMode?: () => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  searchResults: GeographicSearchResult[];
  isSearching: boolean;
  isSearchOpen: boolean;
  onSelectSearchResult: (result: GeographicSearchResult) => void;
  onClearSearch: () => void;
  onCloseSearch: () => void;
  currentZoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetOrientation: () => void;
  onFitGlobal: () => void;
  onOpenSaveDialog: () => void;
  onOpenViewsModal: () => void;
  isLayerPanelOpen: boolean;
  onToggleLayerPanel: () => void;
  isInspectorOpen: boolean;
  onToggleInspector: () => void;
}

export function AtlasMapToolbar({
  currentStyleId,
  onStyleSelect,
  rendererMode = "2D",
  onModeChange,
  isAnalyticsOpen = false,
  onToggleAnalytics,
  isCorporateModeOpen = false,
  onToggleCorporateMode,
  searchQuery,
  onSearchChange,
  searchResults,
  isSearching,
  isSearchOpen,
  onSelectSearchResult,
  onClearSearch,
  onCloseSearch,
  currentZoom,
  onZoomIn,
  onZoomOut,
  onResetOrientation,
  onFitGlobal,
  onOpenSaveDialog,
  onOpenViewsModal,
  isLayerPanelOpen,
  onToggleLayerPanel,
  isInspectorOpen,
  onToggleInspector,
}: AtlasMapToolbarProps) {
  return (
    <div className="h-10 px-3 bg-atlas-surface-1 border-b border-atlas-border-default flex items-center justify-between gap-2 font-mono text-xs z-20 shrink-0">
      {/* Left section: Panel toggles & Search & Mode Switcher */}
      <div className="flex items-center gap-2">
        {onModeChange && (
          <GlobeModeSwitcher mode={rendererMode} onModeChange={onModeChange} />
        )}

        <button
          type="button"
          onClick={onToggleLayerPanel}
          className={`h-7 px-2 flex items-center gap-1.5 rounded border text-[11px] transition-colors ${
            isLayerPanelOpen
              ? "bg-blue-600/20 text-blue-400 border-blue-500/40"
              : "bg-atlas-surface-2 text-atlas-text-secondary border-atlas-border-default hover:text-atlas-text-primary"
          }`}
          title="Toggle Layers Panel"
        >
          <PanelLeft className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Layers</span>
        </button>

        <AtlasMapSearch
          query={searchQuery}
          onQueryChange={onSearchChange}
          results={searchResults}
          isSearching={isSearching}
          isOpen={isSearchOpen}
          onSelectResult={onSelectSearchResult}
          onClear={onClearSearch}
          onClose={onCloseSearch}
        />
      </div>

      {/* Middle/Right section: Style, Controls, Save, Inspector */}
      <div className="flex items-center gap-1.5">
        <AtlasMapStyleSwitcher
          currentStyleId={currentStyleId}
          onStyleSelect={onStyleSelect}
        />

        {/* Zoom & Camera Controls */}
        <div className="flex items-center bg-atlas-surface-2 border border-atlas-border-default rounded overflow-hidden">
          <button
            type="button"
            onClick={onZoomIn}
            className="p-1.5 hover:bg-atlas-surface-1 text-atlas-text-secondary hover:text-atlas-text-primary transition-colors"
            title="Zoom In"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={onZoomOut}
            className="p-1.5 hover:bg-atlas-surface-1 text-atlas-text-secondary hover:text-atlas-text-primary transition-colors"
            title="Zoom Out"
          >
            <Minus className="w-3.5 h-3.5" />
          </button>
          <div className="px-1.5 text-[10px] text-atlas-text-muted font-mono border-l border-atlas-border-default select-none hidden md:block">
            Z: {currentZoom.toFixed(1)}
          </div>
        </div>

        <button
          type="button"
          onClick={onResetOrientation}
          className="p-1.5 bg-atlas-surface-2 border border-atlas-border-default rounded text-atlas-text-secondary hover:text-atlas-text-primary hover:border-atlas-border-strong transition-colors"
          title="Reset Orientation (North Up)"
        >
          <Compass className="w-3.5 h-3.5 text-blue-400" />
        </button>

        <button
          type="button"
          onClick={onFitGlobal}
          className="p-1.5 bg-atlas-surface-2 border border-atlas-border-default rounded text-atlas-text-secondary hover:text-atlas-text-primary hover:border-atlas-border-strong transition-colors"
          title="Reset Global View"
        >
          <Maximize className="w-3.5 h-3.5" />
        </button>

        <div className="h-4 w-px bg-atlas-border-default mx-0.5" />

        {/* Spatial Analytics (deck.gl + H3) */}
        {onToggleAnalytics && (
          <SpatialAnalyticsToolbar
            isOpen={isAnalyticsOpen}
            onToggle={onToggleAnalytics}
          />
        )}

        {/* Corporate Geography (Stage 132) */}
        {onToggleCorporateMode && (
          <button
            type="button"
            onClick={onToggleCorporateMode}
            className={`h-7 px-2 flex items-center gap-1.5 rounded border text-[11px] transition-colors ${
              isCorporateModeOpen
                ? "bg-sky-600/20 text-sky-400 border-sky-500/40"
                : "bg-atlas-surface-2 text-atlas-text-secondary border-atlas-border-default hover:text-atlas-text-primary"
            }`}
            title="Toggle Corporate Geography Mode"
          >
            <Building2 className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">Corporate</span>
          </button>
        )}

        <div className="h-4 w-px bg-atlas-border-default mx-0.5" />

        {/* Saved Views */}
        <button
          type="button"
          onClick={onOpenSaveDialog}
          className="h-7 px-2 flex items-center gap-1 rounded bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-secondary hover:text-atlas-text-primary hover:border-atlas-border-strong text-[11px] transition-colors"
          title="Save Current Map View"
        >
          <Bookmark className="w-3 h-3 text-blue-400" />
          <span className="hidden md:inline">Save View</span>
        </button>

        <button
          type="button"
          onClick={onOpenViewsModal}
          className="p-1.5 bg-atlas-surface-2 border border-atlas-border-default rounded text-atlas-text-secondary hover:text-atlas-text-primary hover:border-atlas-border-strong transition-colors"
          title="Browse Saved Map Views"
        >
          <FolderOpen className="w-3.5 h-3.5 text-amber-400" />
        </button>

        <div className="h-4 w-px bg-atlas-border-default mx-0.5" />

        {/* Inspector Toggle */}
        <button
          type="button"
          onClick={onToggleInspector}
          className={`h-7 px-2 flex items-center gap-1.5 rounded border text-[11px] transition-colors ${
            isInspectorOpen
              ? "bg-blue-600/20 text-blue-400 border-blue-500/40"
              : "bg-atlas-surface-2 text-atlas-text-secondary border-atlas-border-default hover:text-atlas-text-primary"
          }`}
          title="Toggle Region Inspector"
        >
          <span className="hidden sm:inline">Inspector</span>
          <PanelRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

