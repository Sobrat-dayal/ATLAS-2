"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  FuturesContractOverviewResponse,
  getFuturesContractOverview,
} from "@/lib/markets/futures";

export interface UseFuturesContractOverviewResult {
  data: FuturesContractOverviewResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useFuturesContractOverview(
  instrumentEntityId: string | null
): UseFuturesContractOverviewResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<FuturesContractOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(Boolean(instrumentEntityId));
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchOverview = useCallback(async () => {
    if (!instrumentEntityId) {
      setData(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const res = await getFuturesContractOverview(instrumentEntityId, { token });
      setData(res);
    } catch (err) {
      setIsError(true);
      setError(
        err instanceof Error ? err : new Error("Failed to load contract overview")
      );
    } finally {
      setIsLoading(false);
    }
  }, [instrumentEntityId, token]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchOverview();
  }, [fetchOverview]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: fetchOverview,
  };
}
