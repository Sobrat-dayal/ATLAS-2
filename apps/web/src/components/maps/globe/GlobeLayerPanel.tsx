/**
 * 3D Globe Layer Manager Panel (Stage 130).
 *
 * Provides granular management of Imagery Providers, Terrain Elevation,
 * OGC 3D Tilesets, and PostGIS vector geographic layers.
 */

"use client";

import React, { useState } from "react";
import {
  GlobeImageryProvider,
  GlobeTerrainProvider,
  Atlas3DTilesetSource,
} from "@/lib/maps/globe/types";
import { Layers, Eye, EyeOff, Mountain, Box, Compass, X } from "lucide-react";

interface GlobeLayerPanelProps {
  isOpen: boolean;
  onClose: () => void;
  imageryProviders: GlobeImageryProvider[];
  activeImageryId: string;
  onSelectImagery: (providerId: string) => void;
  terrainProviders: GlobeTerrainProvider[];
  activeTerrainId: string;
  onSelectTerrain: (providerId: string) => void;
  tilesets: Atlas3DTilesetSource[];
  activeTilesetIds: string[];
  onToggleTileset: (tilesetId: string) => void;
}

export function GlobeLayerPanel({
  isOpen,
  onClose,
  imageryProviders,
  activeImageryId,
  onSelectImagery,
  terrainProviders,
  activeTerrainId,
  onSelectTerrain,
  tilesets,
  activeTilesetIds,
  onToggleTileset,
}: GlobeLayerPanelProps) {
  const [tab, setTab] = useState<"imagery" | "terrain" | "tilesets">("imagery");

  if (!isOpen) return null;

  return (
    <aside
      aria-label="3D Globe Layer Manager"
      className="absolute top-12 left-4 z-20 w-80 max-h-[calc(100%-4rem)] flex flex-col rounded-md bg-atlas-surface-1/95 backdrop-blur-md border border-atlas-border-default shadow-xl text-atlas-text-primary overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-atlas-border-subtle bg-atlas-surface-2/60">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-atlas-accent" />
          <h2 className="text-xs font-semibold tracking-wide uppercase text-atlas-text-primary">
            Globe Layers
          </h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close Layer Manager"
          className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Segmented Category Navigation */}
      <div className="flex border-b border-atlas-border-subtle bg-atlas-surface-1 px-2 pt-2 gap-1 text-[11px] font-medium">
        <button
          type="button"
          onClick={() => setTab("imagery")}
          className={`flex-1 pb-1.5 border-b-2 transition-colors cursor-pointer text-center ${
            tab === "imagery"
              ? "border-atlas-accent text-atlas-accent font-semibold"
              : "border-transparent text-atlas-text-muted hover:text-atlas-text-primary"
          }`}
        >
          Imagery
        </button>
        <button
          type="button"
          onClick={() => setTab("terrain")}
          className={`flex-1 pb-1.5 border-b-2 transition-colors cursor-pointer text-center ${
            tab === "terrain"
              ? "border-atlas-accent text-atlas-accent font-semibold"
              : "border-transparent text-atlas-text-muted hover:text-atlas-text-primary"
          }`}
        >
          Terrain
        </button>
        <button
          type="button"
          onClick={() => setTab("tilesets")}
          className={`flex-1 pb-1.5 border-b-2 transition-colors cursor-pointer text-center ${
            tab === "tilesets"
              ? "border-atlas-accent text-atlas-accent font-semibold"
              : "border-transparent text-atlas-text-muted hover:text-atlas-text-primary"
          }`}
        >
          3D Tiles
        </button>
      </div>

      {/* Content Area */}
      <div className="p-3 overflow-y-auto space-y-3 flex-1 text-xs">
        {/* IMAGERY TAB */}
        {tab === "imagery" && (
          <div className="space-y-2">
            <p className="text-[11px] text-atlas-text-muted mb-2">
              Select authorized satellite or cartographic raster imagery.
            </p>
            {imageryProviders.map((prov) => {
              const isSelected = prov.provider_id === activeImageryId;
              return (
                <div
                  key={prov.provider_id}
                  onClick={() => prov.is_available && onSelectImagery(prov.provider_id)}
                  className={`p-2.5 rounded border transition-colors cursor-pointer ${
                    isSelected
                      ? "bg-atlas-surface-selected/40 border-atlas-accent"
                      : "bg-atlas-surface-2/40 border-atlas-border-subtle hover:bg-atlas-surface-hover"
                  } ${!prov.is_available ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-atlas-text-primary text-xs">
                      {prov.name}
                    </span>
                    {isSelected && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-atlas-accent/20 text-atlas-accent font-medium">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-atlas-text-muted leading-relaxed mb-1.5">
                    {prov.description}
                  </p>
                  <div className="text-[9px] text-atlas-text-muted font-mono truncate">
                    {prov.attribution}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* TERRAIN TAB */}
        {tab === "terrain" && (
          <div className="space-y-2">
            <p className="text-[11px] text-atlas-text-muted mb-2">
              Topographic elevation and vertical reference model.
            </p>
            {terrainProviders.map((terr) => {
              const isSelected = terr.provider_id === activeTerrainId;
              return (
                <div
                  key={terr.provider_id}
                  onClick={() => terr.is_available && onSelectTerrain(terr.provider_id)}
                  className={`p-2.5 rounded border transition-colors cursor-pointer ${
                    isSelected
                      ? "bg-atlas-surface-selected/40 border-atlas-accent"
                      : "bg-atlas-surface-2/40 border-atlas-border-subtle hover:bg-atlas-surface-hover"
                  } ${!terr.is_available ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1.5">
                      <Mountain className="w-3.5 h-3.5 text-atlas-accent" />
                      <span className="font-medium text-atlas-text-primary text-xs">
                        {terr.name}
                      </span>
                    </div>
                    {isSelected && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-atlas-accent/20 text-atlas-accent font-medium">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-atlas-text-muted leading-relaxed mb-1.5">
                    {terr.description}
                  </p>
                  <div className="flex items-center justify-between text-[9px] text-atlas-text-muted">
                    <span>{terr.has_measured_elevation ? "Real Elevation" : "Zero Elevation (Surface)"}</span>
                    <span className="font-mono">{terr.is_available ? "Available" : "Token Required"}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* 3D TILESETS TAB */}
        {tab === "tilesets" && (
          <div className="space-y-2">
            <p className="text-[11px] text-atlas-text-muted mb-2">
              Authorized OGC 3D Tilesets (b3dm city meshes and building volumes).
            </p>
            {tilesets.length === 0 ? (
              <p className="text-xs text-atlas-text-muted italic">No 3D tilesets registered for this tenant.</p>
            ) : (
              tilesets.map((ts) => {
                const isActive = activeTilesetIds.includes(ts.tileset_id);
                return (
                  <div
                    key={ts.tileset_id}
                    className={`p-2.5 rounded border transition-colors ${
                      isActive
                        ? "bg-atlas-surface-selected/40 border-atlas-accent"
                        : "bg-atlas-surface-2/40 border-atlas-border-subtle"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5">
                        <Box className="w-3.5 h-3.5 text-atlas-accent" />
                        <span className="font-medium text-atlas-text-primary text-xs">
                          {ts.tileset_id}
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => onToggleTileset(ts.tileset_id)}
                        className={`p-1 rounded transition-colors cursor-pointer ${
                          isActive
                            ? "text-atlas-accent hover:bg-atlas-accent/20"
                            : "text-atlas-text-muted hover:text-atlas-text-primary"
                        }`}
                        title={isActive ? "Disable 3D Tileset" : "Enable 3D Tileset"}
                      >
                        {isActive ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                      </button>
                    </div>
                    <p className="text-[10px] text-atlas-text-muted leading-relaxed mb-1.5">
                      {ts.description}
                    </p>
                    <div className="text-[9px] text-atlas-text-muted font-mono truncate">
                      {ts.attribution}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </aside>
  );
}

