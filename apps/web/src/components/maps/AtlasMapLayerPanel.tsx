"use client";

import React from "react";
import { Eye, EyeOff, Sliders, ShieldCheck } from "lucide-react";
import { MapLayer } from "@/lib/maps/types";

interface AtlasMapLayerPanelProps {
  layers: MapLayer[];
  onToggleVisibility: (layerId: string) => void;
  onSetOpacity: (layerId: string, opacity: number) => void;
  className?: string;
}

export function AtlasMapLayerPanel({
  layers,
  onToggleVisibility,
  onSetOpacity,
  className = "",
}: AtlasMapLayerPanelProps) {
  // Group by category
  const categories = Array.from(new Set(layers.map((l) => l.category)));

  return (
    <div className={`h-full flex flex-col bg-atlas-surface-0 font-mono text-xs ${className}`}>
      <div className="px-3 py-2 border-b border-atlas-border-default bg-atlas-surface-1 flex items-center justify-between">
        <span className="font-semibold text-atlas-text-primary uppercase tracking-wider text-[11px]">
          Map Layers ({layers.length})
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {categories.map((category) => {
          const categoryLayers = layers.filter((l) => l.category === category);
          return (
            <div key={category} className="space-y-2">
              <div className="text-[10px] font-semibold text-atlas-text-muted uppercase tracking-wider">
                {category}
              </div>

              <div className="space-y-1.5">
                {categoryLayers.map((layer) => {
                  const isVisible = layer.visible !== false;
                  const opacity = layer.opacity ?? 1.0;

                  return (
                    <div
                      key={layer.layer_id}
                      className="p-2.5 rounded bg-atlas-surface-1 border border-atlas-border-default/60 hover:border-atlas-border-default transition-all"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="font-medium text-atlas-text-primary truncate">
                            {layer.layer_name}
                          </div>
                          <div className="text-[10px] text-atlas-text-muted flex items-center gap-1 mt-0.5">
                            <ShieldCheck className="w-3 h-3 text-emerald-400" />
                            <span>{layer.license_reference || "Licensed"}</span>
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => onToggleVisibility(layer.layer_id)}
                          className={`p-1.5 rounded transition-colors ${
                            isVisible
                              ? "text-blue-400 hover:bg-blue-900/30"
                              : "text-atlas-text-muted hover:bg-atlas-surface-2"
                          }`}
                          title={isVisible ? "Hide Layer" : "Show Layer"}
                        >
                          {isVisible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                        </button>
                      </div>

                      {isVisible && (
                        <div className="mt-2 pt-2 border-t border-atlas-border-default/30 flex items-center gap-2 text-[10px] text-atlas-text-muted">
                          <Sliders className="w-3 h-3 shrink-0" />
                          <span className="shrink-0">Opacity</span>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={Math.round(opacity * 100)}
                            onChange={(e) => onSetOpacity(layer.layer_id, Number(e.target.value) / 100)}
                            className="w-full accent-blue-500 h-1 bg-atlas-surface-2 rounded cursor-pointer"
                          />
                          <span className="w-8 text-right font-mono">{Math.round(opacity * 100)}%</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

