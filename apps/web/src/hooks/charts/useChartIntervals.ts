"use client";

/**
 * Custom React hook managing interval availability discovery for ATLAS Charts (Stage 68).
 *
 * Queries GET /api/v1/charts/intervals for the selected financial instrument,
 * maintaining typed availability statuses, native/derived classifications, and truthful
 * unavailability reasons.
 */

import { useCallback, useEffect, useState } from "react";
import {
  ChartIntervalOptionDTO,
  ChartIntervalsResponse,
  fetchChartIntervals,
} from "@/lib/charts";

export interface UseChartIntervalsReturn {
  intervals: ChartIntervalOptionDTO[];
  defaultInterval: string;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useChartIntervals(symbolOrId?: string): UseChartIntervalsReturn {
  const [intervals, setIntervals] = useState<ChartIntervalOptionDTO[]>([]);
  const [defaultInterval, setDefaultInterval] = useState<string>("1d");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadIntervals = useCallback(async () => {
    if (!symbolOrId) return;

    setIsLoading(true);
    setError(null);

    try {
      const isUuid =
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
          symbolOrId.trim()
        );

      const res: ChartIntervalsResponse = await fetchChartIntervals({
        instrumentId: isUuid ? symbolOrId.trim() : undefined,
        symbol: !isUuid ? symbolOrId.trim() : undefined,
      });

      setIntervals(res.intervals);
      setDefaultInterval(res.default_interval || "1d");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load interval metadata.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [symbolOrId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadIntervals();
  }, [loadIntervals]);

  return {
    intervals,
    defaultInterval,
    isLoading,
    error,
    refetch: loadIntervals,
  };
}
