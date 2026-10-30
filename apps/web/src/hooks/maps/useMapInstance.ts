"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { Map as MapLibreMap } from "maplibre-gl";
import { MapCameraState } from "@/lib/maps/types";
import { DEFAULT_CAMERA } from "@/lib/maps/styles";

interface UseMapInstanceOptions {
  containerRef: React.RefObject<HTMLDivElement | null>;
  initialCamera?: Partial<MapCameraState>;
  styleUrl: string;
  onCameraChange?: (camera: MapCameraState) => void;
  onFeatureClick?: (featureId: string, layerId: string) => void;
}

export function useMapInstance({
  containerRef,
  initialCamera,
  styleUrl,
  onCameraChange,
  onFeatureClick,
}: UseMapInstanceOptions) {
  const mapRef = useRef<MapLibreMap | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [webGlError, setWebGlError] = useState<string | null>(null);
  const [currentZoom, setCurrentZoom] = useState(initialCamera?.zoom ?? DEFAULT_CAMERA.zoom);

  // Check WebGL availability
  const checkWebGL = useCallback(() => {
    if (typeof window === "undefined") return false;
    try {
      const canvas = document.createElement("canvas");
      return !!(
        window.WebGLRenderingContext &&
        (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
      );
    } catch {
      return false;
    }
  }, []);

  // Initialize Map
  useEffect(() => {
    if (typeof window === "undefined" || !containerRef.current) return;

    if (!checkWebGL()) {
      setWebGlError("WebGL hardware acceleration is unavailable in this environment.");
      return;
    }

    const initMap = async () => {
      try {
        const maplibregl = await import("maplibre-gl");

        const centerLon = initialCamera?.longitude ?? DEFAULT_CAMERA.longitude;
        const centerLat = initialCamera?.latitude ?? DEFAULT_CAMERA.latitude;
        const zoom = initialCamera?.zoom ?? DEFAULT_CAMERA.zoom;
        const bearing = initialCamera?.bearing ?? DEFAULT_CAMERA.bearing;
        const pitch = initialCamera?.pitch ?? DEFAULT_CAMERA.pitch;

        const instance = new maplibregl.Map({
          container: containerRef.current!,
          style: styleUrl,
          center: [centerLon, centerLat],
          zoom,
          bearing,
          pitch,
          attributionControl: false, // Custom institutional attribution component used
        });

        instance.on("load", () => {
          setIsReady(true);
          mapRef.current = instance;
        });

        // Camera movement synchronization
        const handleCameraUpdate = () => {
          const center = instance.getCenter();
          const z = instance.getZoom();
          const b = instance.getBearing();
          const p = instance.getPitch();
          setCurrentZoom(Math.round(z * 10) / 10);

          if (onCameraChange) {
            onCameraChange({
              longitude: Math.round(center.lng * 10000) / 10000,
              latitude: Math.round(center.lat * 10000) / 10000,
              zoom: Math.round(z * 10) / 10,
              bearing: Math.round(b * 10) / 10,
              pitch: Math.round(p * 10) / 10,
              projection: "mercator",
              revision: 1,
            });
          }
        };

        instance.on("moveend", handleCameraUpdate);

        // Feature click handler
        instance.on("click", (e) => {
          const features = instance.queryRenderedFeatures(e.point);
          if (features.length > 0) {
            const topFeature = features[0];
            const featId =
              (topFeature.properties as any)?.feature_id ||
              topFeature.id?.toString();
            const layerId = topFeature.layer.id;
            if (featId && onFeatureClick) {
              onFeatureClick(featId, layerId);
            }
          }
        });

        mapRef.current = instance;
      } catch (err: any) {
        console.error("MapLibre initialization failure:", err);
        setWebGlError(err.message || "Failed to initialize MapLibre GL instance.");
      }
    };

    initMap();

    // Resize observer for responsive panels and split views
    const resizeObserver = new ResizeObserver(() => {
      if (mapRef.current) {
        mapRef.current.resize();
      }
    });

    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      resizeObserver.disconnect();
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
      setIsReady(false);
    };
  }, [containerRef, checkWebGL, styleUrl]);

  // Controls
  const zoomIn = useCallback(() => {
    mapRef.current?.zoomIn();
  }, []);

  const zoomOut = useCallback(() => {
    mapRef.current?.zoomOut();
  }, []);

  const resetBearing = useCallback(() => {
    mapRef.current?.resetNorthPitch();
  }, []);

  const flyTo = useCallback((longitude: number, latitude: number, zoom?: number) => {
    mapRef.current?.flyTo({
      center: [longitude, latitude],
      zoom: zoom ?? 10,
      essential: true,
    });
  }, []);

  const fitBounds = useCallback((west: number, south: number, east: number, north: number) => {
    mapRef.current?.fitBounds(
      [
        [west, south],
        [east, north],
      ],
      { padding: 40, maxZoom: 14 }
    );
  }, []);

  return {
    map: mapRef.current,
    isReady,
    webGlError,
    currentZoom,
    zoomIn,
    zoomOut,
    resetBearing,
    flyTo,
    fitBounds,
  };
}

