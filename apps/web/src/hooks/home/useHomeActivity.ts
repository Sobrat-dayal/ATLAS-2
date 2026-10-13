"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  clearHomeActivity,
  getHomeActivity,
  setHomeActivityConsent,
} from "@/lib/activity/activity-api";
import {
  UserActivityItem,
  UserActivityListResponse,
} from "@/lib/activity/activity-types";

export interface UseHomeActivityResult {
  data: UserActivityListResponse | null;
  items: UserActivityItem[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
  isLoadingMore: boolean;
  enableHistory: () => Promise<void>;
  disableHistory: () => Promise<void>;
  clearHistory: () => Promise<void>;
  isMutating: boolean;
}

const DEFAULT_PAGE_LIMIT = 8;

export function useHomeActivity(limit: number = DEFAULT_PAGE_LIMIT): UseHomeActivityResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [data, setData] = useState<UserActivityListResponse | null>(null);
  const [items, setItems] = useState<UserActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const [isMutating, setIsMutating] = useState<boolean>(false);

  const isFetchingRef = useRef<boolean>(false);
  const lastFetchTimeRef = useRef<number>(0);

  // Fetch initial page
  const fetchInitialPage = useCallback(
    async (isMounted: () => boolean) => {
      if (isFetchingRef.current) return;
      isFetchingRef.current = true;

      try {
        const res = await getHomeActivity({ limit }, { token });
        if (isMounted()) {
          setData(res);
          setItems(res.items || []);
          setIsError(false);
          setError(null);
          lastFetchTimeRef.current = Date.now();
        }
      } catch (err) {
        if (isMounted()) {
          const e = err instanceof Error ? err : new Error("Failed to load activity");
          setError(e);
          setIsError(true);
        }
      } finally {
        if (isMounted()) {
          setIsLoading(false);
        }
        isFetchingRef.current = false;
      }
    },
    [limit, token]
  );

  // Initial load or token change (clears cache on auth principal change)
  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;

    // Reset state on user change to prevent cache leakage
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsLoading(true);
    setItems([]);
    setData(null);

    fetchInitialPage(isMounted);

    return () => {
      mounted = false;
    };
  }, [fetchInitialPage]);

  // Listen to background activity events to refresh feed
  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;

    const handleActivityRecorded = () => {
      const now = Date.now();
      // Debounce refetches to avoid burst spamming
      if (now - lastFetchTimeRef.current > 1500) {
        fetchInitialPage(isMounted);
      }
    };

    window.addEventListener("atlas:activity-recorded", handleActivityRecorded);

    return () => {
      mounted = false;
      window.removeEventListener("atlas:activity-recorded", handleActivityRecorded);
    };
  }, [fetchInitialPage]);

  // Load next page
  const loadMore = useCallback(async () => {
    if (!data?.next_cursor || !data.has_more || isLoadingMore) return;
    setIsLoadingMore(true);

    try {
      const nextPage = await getHomeActivity(
        { limit, cursor: data.next_cursor },
        { token }
      );
      setData(nextPage);
      setItems((prev) => [...prev, ...(nextPage.items || [])]);
    } catch (err) {
      const e = err instanceof Error ? err : new Error("Failed to load more activity");
      setError(e);
    } finally {
      setIsLoadingMore(false);
    }
  }, [data, limit, token, isLoadingMore]);

  // Mutations
  const enableHistory = useCallback(async () => {
    setIsMutating(true);
    try {
      await setHomeActivityConsent(true, { token });
      await fetchInitialPage(() => true);
    } finally {
      setIsMutating(false);
    }
  }, [token, fetchInitialPage]);

  const disableHistory = useCallback(async () => {
    setIsMutating(true);
    try {
      await setHomeActivityConsent(false, { token });
      // Disabling also transactionally clears history
      setData((prev) => (prev ? { ...prev, enabled: false, items: [], has_more: false } : null));
      setItems([]);
    } finally {
      setIsMutating(false);
    }
  }, [token]);

  const clearHistory = useCallback(async () => {
    setIsMutating(true);
    try {
      await clearHomeActivity({ token });
      setData((prev) => (prev ? { ...prev, items: [], has_more: false, next_cursor: null } : null));
      setItems([]);
    } finally {
      setIsMutating(false);
    }
  }, [token]);

  const manualRefetch = useCallback(async () => {
    setIsLoading(true);
    await fetchInitialPage(() => true);
  }, [fetchInitialPage]);

  return {
    data,
    items,
    isLoading,
    isError,
    error,
    refetch: manualRefetch,
    loadMore,
    isLoadingMore,
    enableHistory,
    disableHistory,
    clearHistory,
    isMutating,
  };
}
