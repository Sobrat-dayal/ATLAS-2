"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  FxPairOverviewDetailResponse,
  getFxPairDetail,
} from "@/lib/markets/fx";

export interface UseFxPairResult {
  data: FxPairOverviewDetailResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useFxPair(instrumentEntityId: string | null): UseFxPairResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<FxPairOverviewDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchDetail = useCallback(async () => {
    if (!instrumentEntityId) {
      setData(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const res = await getFxPairDetail(instrumentEntityId, { token });
      setData(res);
    } catch (err) {
      setIsError(true);
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, [instrumentEntityId, token]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchDetail();
  }, [fetchDetail]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: fetchDetail,
  };
}
