"use client";

import React, { useRef, useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { useMapInstance } from "@/hooks/maps/useMapInstance";
import { AtlasMapAttribution } from "./AtlasMapAttribution";
import { MapBasemapStyle, MapCameraState, MapLayer } from "@/lib/maps/types";
import "maplibre-gl/dist/maplibre-gl.css";

interface AtlasMapCanvasProps {
  styleUrl: string;
  attribution: string;
  layers: MapLayer[];
  initialCamera?: Partial<MapCameraState>;
  onCameraChange?: (camera: MapCameraState) => void;
  onFeatureClick?: (featureId: string, layerId: string) => void;
  mapInstanceRef?: React.MutableRefObject<any>;
}

export function AtlasMapCanvas({
  styleUrl,
  attribution,
  layers,
  initialCamera,
  onCameraChange,
  onFeatureClick,
  mapInstanceRef,
}: AtlasMapCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const {
    map,
    isReady,
    webGlError,
    zoomIn,
    zoomOut,
    resetBearing,
    flyTo,
    fitBounds,
    currentZoom,
  } = useMapInstance({
    containerRef,
    styleUrl,
    initialCamera,
    onCameraChange,
    onFeatureClick,
  });

  // Expose control methods to parent via mapInstanceRef
  useEffect(() => {
    if (mapInstanceRef) {
      mapInstanceRef.current = {
        zoomIn,
        zoomOut,
        resetBearing,
        flyTo,
        fitBounds,
        currentZoom,
        map,
      };
    }
  }, [mapInstanceRef, zoomIn, zoomOut, resetBearing, flyTo, fitBounds, currentZoom, map]);

  // Synchronize vector/geojson layers onto the active MapLibre instance
  useEffect(() => {
    if (!map || !isReady) return;

    // 1. Add Source for Financial Centers if not present
    if (!map.getSource("atlas-source-financial-centers")) {
      map.addSource("atlas-source-financial-centers", {
        type: "geojson",
        data: "/api/v1/maps/features/query?limit=50",
      });
    }

    // 2. Add Layer for Financial Centers
    if (!map.getLayer("atlas-layer-financial-centers")) {
      map.addLayer({
        id: "atlas-layer-financial-centers",
        type: "circle",
        source: "atlas-source-financial-centers",
        paint: {
          "circle-radius": 7,
          "circle-color": "#38BDF8",
          "circle-stroke-width": 2,
          "circle-stroke-color": "#0284C7",
          "circle-opacity": 0.9,
        },
      });
    }

    // Update layer visibility and opacity based on active props
    const fcLayer = layers.find((l) => l.layer_id === "atlas.layer.financial_centers");
    if (fcLayer && map.getLayer("atlas-layer-financial-centers")) {
      const visibility = fcLayer.visible !== false ? "visible" : "none";
      map.setLayoutProperty("atlas-layer-financial-centers", "visibility", visibility);
      if (fcLayer.opacity !== undefined) {
        map.setPaintProperty("atlas-layer-financial-centers", "circle-opacity", fcLayer.opacity);
      }
    }
  }, [map, isReady, layers, styleUrl]);

  if (webGlError) {
    return (
      <div className="h-full w-full bg-atlas-surface-0 flex flex-col items-center justify-center p-6 text-center font-mono">
        <AlertCircle className="w-12 h-12 text-amber-400 mb-3" />
        <h3 className="text-sm font-semibold text-atlas-text-primary">
          WebGL Context Unavailable
        </h3>
        <p className="text-xs text-atlas-text-muted mt-1 max-w-md">
          {webGlError}
        </p>
        <div className="mt-4 p-3 bg-atlas-surface-1 border border-atlas-border-default rounded text-[11px] text-atlas-text-secondary text-left space-y-1">
          <div>• Ensure hardware acceleration is enabled in browser settings.</div>
          <div>• MapLibre 2D WebGL rendering requires an active GPU context.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full bg-atlas-surface-0 overflow-hidden select-none">
      <div ref={containerRef} className="h-full w-full" />
      <AtlasMapAttribution customAttribution={attribution} />
    </div>
  );
}

