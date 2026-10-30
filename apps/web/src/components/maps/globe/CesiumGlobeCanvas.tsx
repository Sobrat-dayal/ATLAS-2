/**
 * Client-Only Cesium Canvas Container (Stage 130).
 *
 * Hosts the genuine 3D WebGL Earth globe with WebGL error fallback and loading state.
 */

"use client";

import React, { useRef } from "react";
import { GlobeStatus } from "@/lib/maps/globe/types";
import { AlertTriangle, Loader2 } from "lucide-react";

interface CesiumGlobeCanvasProps {
  status: GlobeStatus;
  errorMessage?: string | null;
  containerRef: React.RefObject<HTMLDivElement | null>;
  onFallback2D?: () => void;
}

export function CesiumGlobeCanvas({
  status,
  errorMessage,
  containerRef,
  onFallback2D,
}: CesiumGlobeCanvasProps) {
  return (
    <div className="relative w-full h-full overflow-hidden bg-black select-none">
      {/* Primary Cesium WebGL Container */}
      <div
        ref={containerRef}
        className="w-full h-full"
        tabIndex={0}
        aria-label="Interactive 3D Earth Globe Canvas"
        role="application"
      />

      {/* Loading Overlay */}
      {status === "INITIALIZING" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-atlas-bg-0/90 z-20">
          <Loader2 className="w-8 h-8 text-atlas-accent animate-spin mb-3" />
          <p className="text-sm font-medium text-atlas-text-primary">
            Initializing 3D God's Eye Globe...
          </p>
          <p className="text-xs text-atlas-text-muted mt-1">
            Loading WGS84 ellipsoid and spatial layers
          </p>
        </div>
      )}

      {/* WebGL Unavailable or Fatal Error Fallback */}
      {(status === "WEBGL_UNAVAILABLE" || status === "ERROR") && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-atlas-bg-0 z-30 p-6 text-center">
          <div className="p-3 rounded-full bg-atlas-negative/10 border border-atlas-negative/20 text-atlas-negative mb-4">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h3 className="text-base font-semibold text-atlas-text-primary mb-2">
            {status === "WEBGL_UNAVAILABLE"
              ? "WebGL 3D Acceleration Unavailable"
              : "3D Globe Renderer Error"}
          </h3>
          <p className="text-xs text-atlas-text-muted max-w-md mb-6 leading-relaxed">
            {errorMessage ||
              "Your browser or hardware cannot allocate a WebGL 3D context. You can switch to the high-performance 2D map."}
          </p>

          {onFallback2D && (
            <button
              type="button"
              onClick={onFallback2D}
              className="px-4 py-2 rounded bg-atlas-accent hover:bg-atlas-accent-hover text-white text-xs font-medium shadow-sm transition-colors cursor-pointer"
            >
              Switch to 2D Map
            </button>
          )}
        </div>
      )}
    </div>
  );
}

