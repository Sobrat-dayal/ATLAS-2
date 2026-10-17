"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  ComparisonWindow,
  getMarketMovers,
  MarketMoverResponse,
  MoverCategory,
  MoverCoverage,
  MoverRankedItem,
} from "@/lib/markets/movers";

export interface UseMarketMoversOptions {
  initialUniverseId?: string;
  initialCategory?: MoverCategory;
  initialWindow?: ComparisonWindow;
  initialExchange?: string;
  limit?: number;
}

export interface UseMarketMoversResult {
  data: MarketMoverResponse | null;
  items: MoverRankedItem[];
  coverage: MoverCoverage | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // State & Setters
  universeId: string;
  setUniverseId: (id: string) => void;
  category: MoverCategory;
  setCategory: (cat: MoverCategory) => void;
  window?: ComparisonWindow;
  setWindow: (win?: ComparisonWindow) => void;
  exchange: string;
  setExchange: (ex: string) => void;
  cursor: string | null;
  setCursor: (cur: string | null) => void;
  selectedItem: MoverRankedItem | null;
  setSelectedItem: (item: MoverRankedItem | null) => void;
  resetFilters: () => void;
}

export function useMarketMovers(
  options?: UseMarketMoversOptions
): UseMarketMoversResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [universeId, setUniverseId] = useState<string>(
    options?.initialUniverseId || "univ_us_equities"
  );
  const [category, setCategory] = useState<MoverCategory>(
    options?.initialCategory || "gainers"
  );
  const [window, setWindow] = useState<ComparisonWindow | undefined>(
    options?.initialWindow
  );
  const [exchange, setExchange] = useState<string>(
    options?.initialExchange || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<MoverRankedItem | null>(null);

  const [data, setData] = useState<MarketMoverResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefetching, setIsRefetching] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(
    async (isBackground = false) => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      if (!isBackground) {
        setIsLoading(true);
      } else {
        setIsRefetching(true);
      }
      setIsError(false);
      setError(null);

      try {
        const res = await getMarketMovers({
          universe_id: universeId,
          category,
          window,
          exchange: exchange !== "all" ? exchange : undefined,
          limit: options?.limit || 25,
          cursor: cursor || undefined,
          token,
          signal: controller.signal,
        });

        setData(res);
        // If selected item is no longer in items or is null, select first item
        if (res.items.length > 0) {
          setSelectedItem((prev) => {
            if (!prev) return res.items[0];
            const found = res.items.find(
              (i) => i.instrument_entity_id === prev.instrument_entity_id
            );
            return found || res.items[0];
          });
        } else {
          setSelectedItem(null);
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }
        setIsError(true);
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setIsLoading(false);
        setIsRefetching(false);
      }
    },
    [universeId, category, window, exchange, cursor, options?.limit, token]
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  const resetFilters = useCallback(() => {
    setExchange("all");
    setCursor(null);
  }, []);

  return {
    data,
    items: data?.items || [],
    coverage: data?.coverage || null,
    isLoading,
    isError,
    error,
    refetch: () => fetchData(true),
    isRefetching,
    universeId,
    setUniverseId: (id) => {
      setUniverseId(id);
      setWindow(undefined); // reset window to default on universe change
      setExchange("all");
      setCursor(null);
    },
    category: category,
    setCategory: (cat) => {
      setCategory(cat);
      setCursor(null);
    },
    window,
    setWindow: (win) => {
      setWindow(win);
      setCursor(null);
    },
    exchange,
    setExchange: (ex) => {
      setExchange(ex);
      setCursor(null);
    },
    cursor,
    setCursor,
    selectedItem,
    setSelectedItem,
    resetFilters,
  };
}
