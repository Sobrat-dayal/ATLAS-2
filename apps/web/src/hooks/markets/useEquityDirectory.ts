"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  EquityDirectoryResponse,
  getEquityDirectory,
} from "@/lib/markets/equities";

export interface UseEquityDirectoryOptions {
  initialQuery?: string;
  initialCountry?: string;
  initialExchange?: string;
  initialType?: string;
  initialListingStatus?: string;
  limit?: number;
}

export interface UseEquityDirectoryResult {
  data: EquityDirectoryResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // Filter state
  query: string;
  setQuery: (q: string) => void;
  marketCountry: string;
  setMarketCountry: (c: string) => void;
  exchange: string;
  setExchange: (e: string) => void;
  equityType: string;
  setEquityType: (t: string) => void;
  listingStatus: string;
  setListingStatus: (s: string) => void;
  resetFilters: () => void;

  // Pagination state
  cursor: string | null;
  setCursor: (cursor: string | null) => void;
}

const STALE_TIME_MS = 15_000;

export function useEquityDirectory(
  options?: UseEquityDirectoryOptions
): UseEquityDirectoryResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [query, setQuery] = useState<string>(options?.initialQuery || "");
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query);
  const [marketCountry, setMarketCountry] = useState<string>(
    options?.initialCountry || "all"
  );
  const [exchange, setExchange] = useState<string>(options?.initialExchange || "all");
  const [equityType, setEquityType] = useState<string>(options?.initialType || "all");
  const [listingStatus, setListingStatus] = useState<string>(
    options?.initialListingStatus || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<EquityDirectoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefetching, setIsRefetching] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const lastFetchTimeRef = useRef<number>(0);
  const isFetchingRef = useRef<boolean>(false);
  const lastAcceptedGeneratedAtRef = useRef<number>(0);

  const limit = options?.limit || 25;

  // Debounce search query input (300ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
      setCursor(null); // Reset pagination on new search term
    }, 300);
    return () => clearTimeout(handler);
  }, [query]);

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
        const result = await getEquityDirectory({
          token,
          query: debouncedQuery,
          market_country: marketCountry,
          exchange,
          equity_type: equityType,
          listing_status: listingStatus,
          limit,
          cursor: cursor || undefined,
        });

        if (isMounted()) {
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
          const e =
            err instanceof Error ? err : new Error("Failed to fetch equity directory");
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
    [
      token,
      debouncedQuery,
      marketCountry,
      exchange,
      equityType,
      listingStatus,
      cursor,
      limit,
    ]
  );

  // Trigger fetch on parameter changes
  useEffect(() => {
    let mounted = true;
    const isMounted = () => mounted;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    executeFetch(false, isMounted);

    return () => {
      mounted = false;
    };
  }, [executeFetch]);

  // Window focus, online reconnect, and realtime quote events
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

  const resetFilters = useCallback(() => {
    setQuery("");
    setDebouncedQuery("");
    setMarketCountry("all");
    setExchange("all");
    setEquityType("all");
    setListingStatus("all");
    setCursor(null);
  }, []);

  const manualRefetch = useCallback(async () => {
    await executeFetch(true, () => true);
  }, [executeFetch]);

  const handleCountryChange = useCallback((country: string) => {
    setMarketCountry(country);
    setCursor(null);
  }, []);

  const handleExchangeChange = useCallback((exch: string) => {
    setExchange(exch);
    setCursor(null);
  }, []);

  const handleTypeChange = useCallback((typ: string) => {
    setEquityType(typ);
    setCursor(null);
  }, []);

  const handleListingStatusChange = useCallback((status: string) => {
    setListingStatus(status);
    setCursor(null);
  }, []);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: manualRefetch,
    isRefetching,

    query,
    setQuery,
    marketCountry,
    setMarketCountry: handleCountryChange,
    exchange,
    setExchange: handleExchangeChange,
    equityType,
    setEquityType: handleTypeChange,
    listingStatus,
    setListingStatus: handleListingStatusChange,
    resetFilters,

    cursor,
    setCursor,
  };
}
