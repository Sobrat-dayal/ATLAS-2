"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  FundOverviewDetailResponse,
  getFundOverview,
} from "@/lib/markets/funds";

export interface UseFundOverviewResult {
  data: FundOverviewDetailResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useFundOverview(
  instrumentEntityId: string | null
): UseFundOverviewResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<FundOverviewDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchOverview = useCallback(async () => {
    if (!instrumentEntityId) {
      setData(null);
      setIsLoading(false);
      setIsError(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const res = await getFundOverview(instrumentEntityId, { token });
      setData(res);
    } catch (err) {
      const e =
        err instanceof Error ? err : new Error("Failed to load fund details");
      setError(e);
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  }, [instrumentEntityId, token]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!instrumentEntityId) {
        setData(null);
        setIsLoading(false);
        setIsError(false);
        setError(null);
        return;
      }

      setIsLoading(true);
      setIsError(false);
      setError(null);

      try {
        const res = await getFundOverview(instrumentEntityId, { token });
        if (!cancelled) {
          setData(res);
        }
      } catch (err) {
        if (!cancelled) {
          const e =
            err instanceof Error ? err : new Error("Failed to load fund details");
          setError(e);
          setIsError(true);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [instrumentEntityId, token]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: fetchOverview,
  };
}
