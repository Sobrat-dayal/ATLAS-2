"use client";

import { useState, useCallback } from "react";
import { GeoFeatureDetail } from "@/lib/maps/types";
import { fetchFeatureDetail } from "@/lib/maps/api";

export function useMapSelection() {
  const [selectedFeatureId, setSelectedFeatureId] = useState<string | null>(null);
  const [featureDetail, setFeatureDetail] = useState<GeoFeatureDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectFeature = useCallback((featureId: string) => {
    setSelectedFeatureId(featureId);
    setIsLoading(true);
    setError(null);

    fetchFeatureDetail(featureId)
      .then((data) => {
        setFeatureDetail(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load feature:", err);
        setError(err.message);
        setIsLoading(false);
      });
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedFeatureId(null);
    setFeatureDetail(null);
    setError(null);
  }, []);

  return {
    selectedFeatureId,
    featureDetail,
    isLoading,
    error,
    selectFeature,
    clearSelection,
  };
}

