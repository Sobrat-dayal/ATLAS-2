"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  CurrencyItem,
  FxPairDirectoryResponse,
  getFxCurrencies,
  getFxDirectory,
} from "@/lib/markets/fx";

export interface UseFxDirectoryOptions {
  initialQuery?: string;
  initialBaseCurrency?: string;
  initialQuoteCurrency?: string;
  limit?: number;
}

export interface UseFxDirectoryResult {
  data: FxPairDirectoryResponse | null;
  currencies: CurrencyItem[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // Filter state
  query: string;
  setQuery: (q: string) => void;
  baseCurrency: string;
  setBaseCurrency: (c: string) => void;
  quoteCurrency: string;
  setQuoteCurrency: (c: string) => void;
  resetFilters: () => void;

  // Pagination state
  cursor: string | null;
  setCursor: (cursor: string | null) => void;
}

export function useFxDirectory(
  options?: UseFxDirectoryOptions
): UseFxDirectoryResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [query, setQuery] = useState<string>(options?.initialQuery || "");
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query);
  const [baseCurrency, setBaseCurrency] = useState<string>(
    options?.initialBaseCurrency || "all"
  );
  const [quoteCurrency, setQuoteCurrency] = useState<string>(
    options?.initialQuoteCurrency || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<FxPairDirectoryResponse | null>(null);
  const [currencies, setCurrencies] = useState<CurrencyItem[]>([]);
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

  // Load supported currencies once
  useEffect(() => {
    let cancelled = false;
    async function loadCurrencies() {
      try {
        const res = await getFxCurrencies({ token });
        if (!cancelled && res?.items) {
          setCurrencies(res.items);
        }
      } catch (e) {
        console.warn("Failed to load supported FX currencies:", e);
      }
    }
    loadCurrencies();
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
        const res = await getFxDirectory({
          token,
          base_currency: baseCurrency,
          quote_currency: quoteCurrency,
          query: debouncedQuery,
          limit,
          cursor: cursor || undefined,
        });
        setData(res);
      } catch (err) {
        setIsError(true);
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setIsLoading(false);
        setIsRefetching(false);
        isFetchingRef.current = false;
      }
    },
    [token, baseCurrency, quoteCurrency, debouncedQuery, limit, cursor]
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData(false);
  }, [fetchData]);

  const refetch = useCallback(async () => {
    await fetchData(true);
  }, [fetchData]);

  const resetFilters = useCallback(() => {
    setQuery("");
    setDebouncedQuery("");
    setBaseCurrency("all");
    setQuoteCurrency("all");
    setCursor(null);
  }, []);

  return {
    data,
    currencies,
    isLoading,
    isError,
    error,
    refetch,
    isRefetching,
    query,
    setQuery,
    baseCurrency,
    setBaseCurrency,
    quoteCurrency,
    setQuoteCurrency,
    resetFilters,
    cursor,
    setCursor,
  };
}
