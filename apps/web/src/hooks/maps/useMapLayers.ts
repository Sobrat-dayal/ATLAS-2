"use client";

import { useEffect, useState, useCallback } from "react";
import { MapLayer } from "@/lib/maps/types";
import { fetchMapLayers } from "@/lib/maps/api";

export function useMapLayers() {
  const [layers, setLayers] = useState<MapLayer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchMapLayers()
      .then((data) => {
        if (mounted) {
          setLayers(
            data.map((l) => ({
              ...l,
              visible: l.default_visibility,
              opacity: l.default_opacity,
            }))
          );
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message);
          setIsLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const toggleLayerVisibility = useCallback((layerId: string) => {
    setLayers((prev) =>
      prev.map((l) => (l.layer_id === layerId ? { ...l, visible: !l.visible } : l))
    );
  }, []);

  const setLayerOpacity = useCallback((layerId: string, opacity: number) => {
    setLayers((prev) =>
      prev.map((l) => (l.layer_id === layerId ? { ...l, opacity: Math.max(0, Math.min(1, opacity)) } : l))
    );
  }, []);

  return {
    layers,
    isLoading,
    error,
    toggleLayerVisibility,
    setLayerOpacity,
  };
}

