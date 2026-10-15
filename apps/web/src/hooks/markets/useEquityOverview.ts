"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  EquityOverviewDetailResponse,
  getEquityOverview,
} from "@/lib/markets/equities";

export interface UseEquityOverviewResult {
  data: EquityOverviewDetailResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useEquityOverview(
  instrumentEntityId: string | null
): UseEquityOverviewResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<EquityOverviewDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const activeIdRef = useRef<string | null>(instrumentEntityId);
  activeIdRef.current = instrumentEntityId;

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
      const res = await getEquityOverview(instrumentEntityId, { token });
      if (activeIdRef.current === instrumentEntityId) {
        setData(res);
      }
    } catch (err) {
      if (activeIdRef.current === instrumentEntityId) {
        const e =
          err instanceof Error
            ? err
            : new Error("Failed to load equity security details");
        setError(e);
        setIsError(true);
      }
    } finally {
      if (activeIdRef.current === instrumentEntityId) {
        setIsLoading(false);
      }
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
