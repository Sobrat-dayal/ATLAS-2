"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import { BondOverviewResponse, getBondOverview } from "@/lib/markets/bonds";

export interface UseBondOverviewResult {
  data: BondOverviewResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useBondOverview(instrumentEntityId?: string | null): UseBondOverviewResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<BondOverviewResponse | null>(null);
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
      const res = await getBondOverview(instrumentEntityId, { token });
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
