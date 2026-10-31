"use client";

import { useEffect, useState } from "react";
import {
  fetchFacilityDetails,
  fetchFacilityHistory,
  fetchFacilitySources,
} from "@/lib/maps/corporate/api";
import {
  CorporateFacility,
  FacilityEvidenceClaim,
  FacilityStatusHistory,
} from "@/lib/maps/corporate/types";

export function useFacilityDetails(facilityId: string | null) {
  const [facility, setFacility] = useState<CorporateFacility | null>(null);
  const [sources, setSources] = useState<FacilityEvidenceClaim[]>([]);
  const [history, setHistory] = useState<FacilityStatusHistory[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!facilityId) {
      setFacility(null);
      setSources([]);
      setHistory([]);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchFacilityDetails(facilityId),
      fetchFacilitySources(facilityId).catch(() => []),
      fetchFacilityHistory(facilityId).catch(() => []),
    ])
      .then(([facData, srcData, histData]) => {
        if (!isMounted) return;
        setFacility(facData);
        setSources(srcData);
        setHistory(histData);
      })
      .catch((err: any) => {
        if (!isMounted) return;
        setError(err?.message || "Failed to load facility details");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [facilityId]);

  return {
    facility,
    sources,
    history,
    loading,
    error,
  };
}

