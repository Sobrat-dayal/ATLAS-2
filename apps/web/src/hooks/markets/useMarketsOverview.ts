"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import { getMarketsOverview } from "@/lib/markets/api";
import { MarketsOverviewResponse } from "@/lib/markets/types";

export interface UseMarketsOverviewOptions {
  initialGroup?: string;
  limit?: number;
}

export interface UseMarketsOverviewResult {
  data: MarketsOverviewResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;
  selectedGroup: string;
  setSelectedGroup: (group: string) => void;
  cursor: string | null;
  setCursor: (cursor: string | null) => void;
}

const STALE_TIME_MS = 15_000; // 15 seconds

/**
 * Custom Query Hook for Stage 56 Markets Overview V1.
 *
 * Features:
 * - In-memory cache with stale-while-revalidate behavior.
 * - Authenticated token injection via Supabase useAuth.
 * - Snapshot race protection ensuring older responses never overwrite newer state.
 * - Realtime coalesced refetch on Stage 42/43 market quote update events (atlas:market.quote.updated).
 * - Automatic background refetch on window focus and network reconnect.
 * - Zero localStorage persistence (in-memory only).
 */
export function useMarketsOverview(
  options?: UseMarketsOverviewOptions
): UseMarketsOverviewResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [selectedGroup, setSelectedGroup] = useState<string>(options?.initialGroup || "all");
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<MarketsOverviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefetching, setIsRefetching] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const lastFetchTimeRef = useRef<number>(0);
  const isFetchingRef = useRef<boolean>(false);
  const lastAcceptedGeneratedAtRef = useRef<number>(0);

  const limit = options?.limit || 25;

  const executeFetch = useCallback(
    async (isBackground: boolean, isMounted: () => boolean) => {
      if (isFetchingRef.current) return;
      isFetchingRef.current = true;

      if (isBackground) {
        setIsRefetching(true);
      } else {
        setIsLoading(true);
      }

      try {
        const result = await getMarketsOverview({
          token,
          group: selectedGroup,
          limit,
          cursor: cursor || undefined,
        });

        if (isMounted()) {
          // Snapshot Race Protection: Never overwrite with an older out-of-order response
          const generatedAtMs = new Date(result.generated_at).getTime();
          if (generatedAtMs >= lastAcceptedGeneratedAtRef.current) {
            lastAcceptedGeneratedAtRef.current = generatedAtMs;
            setData(result);
            setIsError(false);
            setError(null);
            lastFetchTimeRef.current = Date.now();
          }
        }
      } catch (err) {
        if (isMounted()) {
          const e = err instanceof Error ? err : new Error("Failed to fetch markets overview");
          setError(e);
          setIsError(true);
        }
      } finally {
        if (isMounted()) {
          setIsLoading(false);
          setIsRefetching(false);
        }
        isFetchingRef.current = false;
      }
    },
    [token, selectedGroup, cursor, limit]
  );

  // Group or cursor change triggers a new fetch
  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    executeFetch(false, isMounted);

    return () => {
      mounted = false;
    };
  }, [executeFetch]);

  // Window focus, network reconnect, and live event coalesced refetch handlers
  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;

    const handleFocus = () => {
      const now = Date.now();
      if (now - lastFetchTimeRef.current > STALE_TIME_MS) {
        executeFetch(true, isMounted);
      }
    };

    const handleOnline = () => {
      executeFetch(true, isMounted);
    };

    const handleQuoteUpdated = () => {
      // Coalesced refetch on Stage 42/43 market quote update event
      const now = Date.now();
      if (now - lastFetchTimeRef.current > 2_000) {
        executeFetch(true, isMounted);
      }
    };

    window.addEventListener("focus", handleFocus);
    window.addEventListener("online", handleOnline);
    window.addEventListener("atlas:market.quote.updated", handleQuoteUpdated);

    return () => {
      mounted = false;
      window.removeEventListener("focus", handleFocus);
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("atlas:market.quote.updated", handleQuoteUpdated);
    };
  }, [executeFetch]);

  const handleGroupSelect = useCallback((group: string) => {
    setSelectedGroup(group);
    setCursor(null); // Reset cursor on group change
  }, []);

  const manualRefetch = useCallback(async () => {
    await executeFetch(true, () => true);
  }, [executeFetch]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: manualRefetch,
    isRefetching,
    selectedGroup,
    setSelectedGroup: handleGroupSelect,
    cursor,
    setCursor,
  };
}
