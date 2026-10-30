/**
 * 3D Globe Feature Inspector (Stage 130).
 *
 * Inspects selected geographic features, surface coordinates,
 * elevation, data provenance, and source attribution.
 */

"use client";

import React from "react";
import { Info, X, MapPin, Database, ShieldCheck, Copy, Check } from "lucide-react";

interface GlobeFeatureInspectorProps {
  isOpen: boolean;
  onClose: () => void;
  selectedFeature: any | null;
  surfacePosition?: { lon: number; lat: number; height: number } | null;
  terrainActive?: boolean;
}

export function GlobeFeatureInspector({
  isOpen,
  onClose,
  selectedFeature,
  surfacePosition,
  terrainActive = false,
}: GlobeFeatureInspectorProps) {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen) return null;

  const handleCopyCoords = () => {
    if (!surfacePosition) return;
    const text = `${surfacePosition.lat.toFixed(6)}, ${surfacePosition.lon.toFixed(6)}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <aside
      aria-label="3D Globe Feature Inspector"
      className="absolute top-12 right-4 z-20 w-84 max-h-[calc(100%-4rem)] flex flex-col rounded-md bg-atlas-surface-1/95 backdrop-blur-md border border-atlas-border-default shadow-xl text-atlas-text-primary overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-atlas-border-subtle bg-atlas-surface-2/60">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-atlas-accent" />
          <h2 className="text-xs font-semibold tracking-wide uppercase text-atlas-text-primary">
            Feature Inspector
          </h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close Inspector"
          className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content Area */}
      <div className="p-3.5 overflow-y-auto space-y-3.5 text-xs">
        {/* Surface Position Section */}
        {surfacePosition ? (
          <div className="p-2.5 rounded bg-atlas-surface-2/50 border border-atlas-border-subtle space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-atlas-text-muted flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-atlas-accent" />
                Target Surface Coordinates
              </span>
              <button
                type="button"
                onClick={handleCopyCoords}
                className="text-[10px] text-atlas-accent flex items-center gap-1 hover:underline cursor-pointer"
              >
                {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
            <div className="font-mono text-xs text-atlas-text-primary">
              {surfacePosition.lat.toFixed(6)}°, {surfacePosition.lon.toFixed(6)}°
            </div>
            <div className="flex items-center justify-between text-[10px] text-atlas-text-muted border-t border-atlas-border-subtle/50 pt-1.5">
              <span>Vertical Elevation:</span>
              <span className="font-mono text-atlas-text-primary">
                {terrainActive
                  ? `${surfacePosition.height.toFixed(1)} m (Topographic)`
                  : "0.0 m (WGS84 Ellipsoid Surface)"}
              </span>
            </div>
          </div>
        ) : (
          <div className="p-3 rounded bg-atlas-surface-2/30 border border-atlas-border-subtle/60 text-center text-[11px] text-atlas-text-muted">
            Click any surface point on the globe to inspect coordinates and elevation.
          </div>
        )}

        {/* Selected Entity Section */}
        {selectedFeature ? (
          <div className="space-y-3">
            <div>
              <span className="text-[10px] font-semibold uppercase text-atlas-text-muted tracking-wider">
                Feature
              </span>
              <h3 className="text-sm font-semibold text-atlas-text-primary mt-0.5">
                {selectedFeature.label || selectedFeature.properties?.name || selectedFeature.feature_id}
              </h3>
              <p className="text-[11px] text-atlas-text-muted font-mono mt-0.5">
                ID: {selectedFeature.feature_id}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded bg-atlas-surface-2/40 border border-atlas-border-subtle">
                <span className="text-atlas-text-muted block text-[10px]">Dataset</span>
                <span className="font-medium truncate block">{selectedFeature.dataset_id}</span>
              </div>
              <div className="p-2 rounded bg-atlas-surface-2/40 border border-atlas-border-subtle">
                <span className="text-atlas-text-muted block text-[10px]">Quality</span>
                <span className="font-medium text-atlas-positive flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  {selectedFeature.data_quality || "Verified"}
                </span>
              </div>
            </div>

            {/* Properties Table */}
            {selectedFeature.properties && Object.keys(selectedFeature.properties).length > 0 && (
              <div>
                <span className="text-[10px] font-semibold uppercase text-atlas-text-muted tracking-wider block mb-1.5">
                  Attributes
                </span>
                <div className="rounded border border-atlas-border-subtle overflow-hidden">
                  <table className="w-full text-left text-[11px]">
                    <tbody>
                      {Object.entries(selectedFeature.properties).map(([k, v], idx) => (
                        <tr
                          key={k}
                          className={idx % 2 === 0 ? "bg-atlas-surface-2/30" : "bg-transparent"}
                        >
                          <td className="px-2 py-1 font-mono text-atlas-text-muted border-r border-atlas-border-subtle/50">
                            {k}
                          </td>
                          <td className="px-2 py-1 font-medium text-atlas-text-primary truncate max-w-[120px]">
                            {String(v)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="p-3 text-center text-atlas-text-muted text-[11px] italic">
            Select a financial hub, sovereign boundary, or 3D asset to inspect institutional metadata.
          </div>
        )}
      </div>
    </aside>
  );
}

