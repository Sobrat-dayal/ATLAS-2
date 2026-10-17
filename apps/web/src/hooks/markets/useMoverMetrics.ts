"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  ComparisonWindow,
  getMoverMetrics,
  MoverCategory,
  MoverMetricDefinition,
  MoverMetricOptionsResponse,
} from "@/lib/markets/movers";

export interface UseMoverMetricsResult {
  data: MoverMetricOptionsResponse | null;
  metrics: MoverMetricDefinition[];
  supportedCategories: MoverCategory[];
  supportedWindows: ComparisonWindow[];
  activityMetricLabel?: string | null;
  activityUnit?: string | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useMoverMetrics(universeId: string): UseMoverMetricsResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<MoverMetricOptionsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchMetrics = useCallback(async () => {
    if (!universeId) return;
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const res = await getMoverMetrics(universeId, { token });
      setData(res);
    } catch (err: unknown) {
      setIsError(true);
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, [universeId, token]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchMetrics();
  }, [fetchMetrics]);

  return {
    data,
    metrics: data?.metrics || [],
    supportedCategories: data?.supported_categories || [],
    supportedWindows: data?.supported_windows || [],
    activityMetricLabel: data?.activity_metric_label,
    activityUnit: data?.activity_unit,
    isLoading,
    isError,
    error,
    refetch: fetchMetrics,
  };
}
