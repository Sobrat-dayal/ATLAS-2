"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  FundDirectoryResponse,
  getFundDirectory,
} from "@/lib/markets/funds";

export interface UseFundDirectoryOptions {
  initialQuery?: string;
  initialFundType?: string;
  initialCountry?: string;
  initialExchange?: string;
  initialDomicile?: string;
  initialCategory?: string;
  initialCurrency?: string;
  limit?: number;
}

export interface UseFundDirectoryResult {
  data: FundDirectoryResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // Filter state
  query: string;
  setQuery: (q: string) => void;
  fundType: string;
  setFundType: (t: string) => void;
  marketCountry: string;
  setMarketCountry: (c: string) => void;
  exchange: string;
  setExchange: (e: string) => void;
  domicile: string;
  setDomicile: (d: string) => void;
  fundCategory: string;
  setFundCategory: (cat: string) => void;
  shareClassCurrency: string;
  setShareClassCurrency: (cur: string) => void;
  resetFilters: () => void;

  // Pagination state
  cursor: string | null;
  setCursor: (cursor: string | null) => void;
}

const STALE_TIME_MS = 15_000;

export function useFundDirectory(
  options?: UseFundDirectoryOptions
): UseFundDirectoryResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [query, setQuery] = useState<string>(options?.initialQuery || "");
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query);
  const [fundType, setFundType] = useState<string>(options?.initialFundType || "ALL");
  const [marketCountry, setMarketCountry] = useState<string>(
    options?.initialCountry || "all"
  );
  const [exchange, setExchange] = useState<string>(options?.initialExchange || "all");
  const [domicile, setDomicile] = useState<string>(options?.initialDomicile || "all");
  const [fundCategory, setFundCategory] = useState<string>(
    options?.initialCategory || "all"
  );
  const [shareClassCurrency, setShareClassCurrency] = useState<string>(
    options?.initialCurrency || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<FundDirectoryResponse | null>(null);
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
      setCursor(null);
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
        const result = await getFundDirectory({
          token,
          query: debouncedQuery,
          fund_type: fundType,
          market_country: marketCountry,
          exchange,
          domicile,
          fund_category: fundCategory,
          share_class_currency: shareClassCurrency,
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
            err instanceof Error ? err : new Error("Failed to fetch fund directory");
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
      fundType,
      marketCountry,
      exchange,
      domicile,
      fundCategory,
      shareClassCurrency,
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
      // Listed ETF updates trigger throttled refetch without mutating official NAV
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
    setFundType("ALL");
    setMarketCountry("all");
    setExchange("all");
    setDomicile("all");
    setFundCategory("all");
    setShareClassCurrency("all");
    setCursor(null);
  }, []);

  const manualRefetch = useCallback(async () => {
    await executeFetch(true, () => true);
  }, [executeFetch]);

  const handleFundTypeChange = useCallback((type: string) => {
    setFundType(type);
    setCursor(null);
  }, []);

  const handleCountryChange = useCallback((country: string) => {
    setMarketCountry(country);
    setCursor(null);
  }, []);

  const handleExchangeChange = useCallback((exch: string) => {
    setExchange(exch);
    setCursor(null);
  }, []);

  const handleDomicileChange = useCallback((dom: string) => {
    setDomicile(dom);
    setCursor(null);
  }, []);

  const handleCategoryChange = useCallback((cat: string) => {
    setFundCategory(cat);
    setCursor(null);
  }, []);

  const handleCurrencyChange = useCallback((cur: string) => {
    setShareClassCurrency(cur);
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
    fundType,
    setFundType: handleFundTypeChange,
    marketCountry,
    setMarketCountry: handleCountryChange,
    exchange,
    setExchange: handleExchangeChange,
    domicile,
    setDomicile: handleDomicileChange,
    fundCategory,
    setFundCategory: handleCategoryChange,
    shareClassCurrency,
    setShareClassCurrency: handleCurrencyChange,
    resetFilters,

    cursor,
    setCursor,
  };
}
