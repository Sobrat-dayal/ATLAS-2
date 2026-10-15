"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  CryptoSpotMarketOverviewDetailResponse,
  getCryptoMarketDetail,
} from "@/lib/markets/crypto";

export function useCryptoMarketDetail(instrumentEntityId: string | null) {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] =
    useState<CryptoSpotMarketOverviewDetailResponse | null>(null);
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
      const res = await getCryptoMarketDetail(instrumentEntityId, { token });
      setData(res);
    } catch (err) {
      setIsError(true);
      setError(
        err instanceof Error
          ? err
          : new Error("Failed to load crypto market details")
      );
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
