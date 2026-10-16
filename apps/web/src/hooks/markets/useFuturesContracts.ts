"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  FuturesContractDirectoryResponse,
  FuturesFilterOptionsResponse,
  getFuturesContracts,
  getFuturesFilterOptions,
} from "@/lib/markets/futures";

export interface UseFuturesContractsOptions {
  initialQuery?: string;
  initialCategory?: string;
  initialExchange?: string;
  initialProductEntityId?: string;
  initialRootSymbol?: string;
  initialContractMonth?: string;
  initialSettlementType?: string;
  initialLifecycleStatus?: string;
  limit?: number;
}

export interface UseFuturesContractsResult {
  data: FuturesContractDirectoryResponse | null;
  filterOptions: FuturesFilterOptionsResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // Filter state
  query: string;
  setQuery: (q: string) => void;
  category: string;
  setCategory: (c: string) => void;
  exchange: string;
  setExchange: (e: string) => void;
  productEntityId: string;
  setProductEntityId: (p: string) => void;
  rootSymbol: string;
  setRootSymbol: (rs: string) => void;
  contractMonth: string;
  setContractMonth: (cm: string) => void;
  settlementType: string;
  setSettlementType: (st: string) => void;
  lifecycleStatus: string;
  setLifecycleStatus: (ls: string) => void;
  resetFilters: () => void;

  // Pagination state
  cursor: string | null;
  setCursor: (cursor: string | null) => void;
}

export function useFuturesContracts(
  options?: UseFuturesContractsOptions
): UseFuturesContractsResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [query, setQuery] = useState<string>(options?.initialQuery || "");
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query);
  const [category, setCategory] = useState<string>(
    options?.initialCategory || "all"
  );
  const [exchange, setExchange] = useState<string>(
    options?.initialExchange || "all"
  );
  const [productEntityId, setProductEntityId] = useState<string>(
    options?.initialProductEntityId || "all"
  );
  const [rootSymbol, setRootSymbol] = useState<string>(
    options?.initialRootSymbol || "all"
  );
  const [contractMonth, setContractMonth] = useState<string>(
    options?.initialContractMonth || "all"
  );
  const [settlementType, setSettlementType] = useState<string>(
    options?.initialSettlementType || "all"
  );
  const [lifecycleStatus, setLifecycleStatus] = useState<string>(
    options?.initialLifecycleStatus || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<FuturesContractDirectoryResponse | null>(null);
  const [filterOptions, setFilterOptions] =
    useState<FuturesFilterOptionsResponse | null>(null);
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
        const res = await getFuturesFilterOptions({ token });
        if (!cancelled && res) {
          setFilterOptions(res);
        }
      } catch (e) {
        console.warn("Failed to load futures filter options:", e);
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
        const res = await getFuturesContracts({
          token,
          query: debouncedQuery,
          category: category !== "all" ? category : undefined,
          exchange: exchange !== "all" ? exchange : undefined,
          product_entity_id:
            productEntityId !== "all" ? productEntityId : undefined,
          root_symbol: rootSymbol !== "all" ? rootSymbol : undefined,
          contract_month: contractMonth !== "all" ? contractMonth : undefined,
          settlement_type: settlementType !== "all" ? settlementType : undefined,
          lifecycle_status:
            lifecycleStatus !== "all" ? lifecycleStatus : undefined,
          limit,
          cursor: cursor || undefined,
        });
        setData(res);
      } catch (err) {
        setIsError(true);
        setError(
          err instanceof Error ? err : new Error("Failed to load futures contracts")
        );
      } finally {
        setIsLoading(false);
        setIsRefetching(false);
        isFetchingRef.current = false;
      }
    },
    [
      token,
      debouncedQuery,
      category,
      exchange,
      productEntityId,
      rootSymbol,
      contractMonth,
      settlementType,
      lifecycleStatus,
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
    setCategory("all");
    setExchange("all");
    setProductEntityId("all");
    setRootSymbol("all");
    setContractMonth("all");
    setSettlementType("all");
    setLifecycleStatus("all");
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
    setQuery: (q: string) => {
      setQuery(q);
      setCursor(null);
    },
    category: category,
    setCategory: (c: string) => {
      setCategory(c);
      setCursor(null);
    },
    exchange: exchange,
    setExchange: (e: string) => {
      setExchange(e);
      setCursor(null);
    },
    productEntityId,
    setProductEntityId: (p: string) => {
      setProductEntityId(p);
      setCursor(null);
    },
    rootSymbol,
    setRootSymbol: (rs: string) => {
      setRootSymbol(rs);
      setCursor(null);
    },
    contractMonth,
    setContractMonth: (cm: string) => {
      setContractMonth(cm);
      setCursor(null);
    },
    settlementType,
    setSettlementType: (st: string) => {
      setSettlementType(st);
      setCursor(null);
    },
    lifecycleStatus,
    setLifecycleStatus: (ls: string) => {
      setLifecycleStatus(ls);
      setCursor(null);
    },
    resetFilters,

    cursor,
    setCursor,
  };
}
