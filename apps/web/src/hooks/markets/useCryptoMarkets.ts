"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  CryptoFilterOptionsResponse,
  CryptoSpotMarketDirectoryResponse,
  getCryptoFilterOptions,
  getCryptoSpotMarkets,
} from "@/lib/markets/crypto";

export interface UseCryptoMarketsOptions {
  initialQuery?: string;
  initialBaseAsset?: string;
  initialQuoteAsset?: string;
  initialVenue?: string;
  initialQuoteAssetType?: string;
  limit?: number;
}

export interface UseCryptoMarketsResult {
  data: CryptoSpotMarketDirectoryResponse | null;
  filterOptions: CryptoFilterOptionsResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // Filter state
  query: string;
  setQuery: (q: string) => void;
  baseAsset: string;
  setBaseAsset: (a: string) => void;
  quoteAsset: string;
  setQuoteAsset: (q: string) => void;
  venue: string;
  setVenue: (v: string) => void;
  quoteAssetType: string;
  setQuoteAssetType: (t: string) => void;
  resetFilters: () => void;

  // Pagination state
  cursor: string | null;
  setCursor: (cursor: string | null) => void;
}

export function useCryptoMarkets(
  options?: UseCryptoMarketsOptions
): UseCryptoMarketsResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [query, setQuery] = useState<string>(options?.initialQuery || "");
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query);
  const [baseAsset, setBaseAsset] = useState<string>(
    options?.initialBaseAsset || "all"
  );
  const [quoteAsset, setQuoteAsset] = useState<string>(
    options?.initialQuoteAsset || "all"
  );
  const [venue, setVenue] = useState<string>(options?.initialVenue || "all");
  const [quoteAssetType, setQuoteAssetType] = useState<string>(
    options?.initialQuoteAssetType || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<CryptoSpotMarketDirectoryResponse | null>(null);
  const [filterOptions, setFilterOptions] =
    useState<CryptoFilterOptionsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefetching, setIsRefetching] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const isFetchingRef = useRef<boolean>(false);
  const limit = options?.limit || 25;

  // Debounce search query input (300ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
      setCursor(null);
    }, 300);
    return () => clearTimeout(handler);
  }, [query]);

  // Load filter options once
  useEffect(() => {
    let cancelled = false;
    async function loadFilterOptions() {
      try {
        const res = await getCryptoFilterOptions({ token });
        if (!cancelled && res) {
          setFilterOptions(res);
        }
      } catch (e) {
        console.warn("Failed to load crypto filter options:", e);
      }
    }
    loadFilterOptions();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const fetchData = useCallback(
    async (isManualRefresh = false) => {
      if (isFetchingRef.current) return;
      isFetchingRef.current = true;

      if (isManualRefresh) {
        setIsRefetching(true);
      } else {
        setIsLoading(true);
      }
      setIsError(false);
      setError(null);

      try {
        const res = await getCryptoSpotMarkets({
          token,
          base_asset: baseAsset,
          quote_asset: quoteAsset,
          venue,
          quote_asset_type: quoteAssetType,
          query: debouncedQuery,
          limit,
          cursor: cursor || undefined,
        });
        setData(res);
      } catch (err) {
        setIsError(true);
        setError(
          err instanceof Error
            ? err
            : new Error("An error occurred while fetching crypto markets")
        );
      } finally {
        setIsLoading(false);
        setIsRefetching(false);
        isFetchingRef.current = false;
      }
    },
    [
      token,
      baseAsset,
      quoteAsset,
      venue,
      quoteAssetType,
      debouncedQuery,
      limit,
      cursor,
    ]
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
  }, [fetchData]);

  const resetFilters = useCallback(() => {
    setQuery("");
    setDebouncedQuery("");
    setBaseAsset("all");
    setQuoteAsset("all");
    setVenue("all");
    setQuoteAssetType("all");
    setCursor(null);
  }, []);

  return {
    data,
    filterOptions,
    isLoading,
    isError,
    error,
    refetch: () => fetchData(true),
    isRefetching,
    query,
    setQuery,
    baseAsset,
    setBaseAsset: (a: string) => {
      setBaseAsset(a);
      setCursor(null);
    },
    quoteAsset,
    setQuoteAsset: (q: string) => {
      setQuoteAsset(q);
      setCursor(null);
    },
    venue,
    setVenue: (v: string) => {
      setVenue(v);
      setCursor(null);
    },
    quoteAssetType,
    setQuoteAssetType: (t: string) => {
      setQuoteAssetType(t);
      setCursor(null);
    },
    resetFilters,
    cursor,
    setCursor,
  };
}
