"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  getMoverUniverses,
  MoverUniverseDefinition,
  MoverUniverseResponse,
} from "@/lib/markets/movers";

export interface UseMoverUniversesResult {
  data: MoverUniverseResponse | null;
  universes: MoverUniverseDefinition[];
  defaultUniverseId: string;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useMoverUniverses(): UseMoverUniversesResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<MoverUniverseResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchUniverses = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);
    try {
      const res = await getMoverUniverses({ token });
      setData(res);
    } catch (err: unknown) {
      setIsError(true);
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchUniverses();
  }, [fetchUniverses]);

  return {
    data,
    universes: data?.universes || [],
    defaultUniverseId: data?.default_universe_id || "univ_us_equities",
    isLoading,
    isError,
    error,
    refetch: fetchUniverses,
  };
}
