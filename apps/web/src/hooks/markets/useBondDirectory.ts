"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  BondDirectoryResponse,
  BondFilterOptionsResponse,
  getBondFilterOptions,
  getBondsDirectory,
} from "@/lib/markets/bonds";

export interface UseBondDirectoryOptions {
  initialQuery?: string;
  initialIssuerType?: string;
  initialBondType?: string;
  initialCurrency?: string;
  initialCouponType?: string;
  initialMaturityBucket?: string;
  limit?: number;
}

export interface UseBondDirectoryResult {
  data: BondDirectoryResponse | null;
  filterOptions: BondFilterOptionsResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefetching: boolean;

  // Filter state
  query: string;
  setQuery: (q: string) => void;
  issuerType: string;
  setIssuerType: (t: string) => void;
  bondType: string;
  setBondType: (bt: string) => void;
  currency: string;
  setCurrency: (c: string) => void;
  couponType: string;
  setCouponType: (ct: string) => void;
  maturityBucket: string;
  setMaturityBucket: (mb: string) => void;
  resetFilters: () => void;

  // Pagination state
  cursor: string | null;
  setCursor: (cursor: string | null) => void;
}

export function useBondDirectory(
  options?: UseBondDirectoryOptions
): UseBondDirectoryResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [query, setQuery] = useState<string>(options?.initialQuery || "");
  const [debouncedQuery, setDebouncedQuery] = useState<string>(query);
  const [issuerType, setIssuerType] = useState<string>(
    options?.initialIssuerType || "all"
  );
  const [bondType, setBondType] = useState<string>(
    options?.initialBondType || "all"
  );
  const [currency, setCurrency] = useState<string>(
    options?.initialCurrency || "all"
  );
  const [couponType, setCouponType] = useState<string>(
    options?.initialCouponType || "all"
  );
  const [maturityBucket, setMaturityBucket] = useState<string>(
    options?.initialMaturityBucket || "all"
  );
  const [cursor, setCursor] = useState<string | null>(null);

  const [data, setData] = useState<BondDirectoryResponse | null>(null);
  const [filterOptions, setFilterOptions] =
    useState<BondFilterOptionsResponse | null>(null);
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
        const res = await getBondFilterOptions({ token });
        if (!cancelled && res) {
          setFilterOptions(res);
        }
      } catch (e) {
        console.warn("Failed to load bond filter options:", e);
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
        const res = await getBondsDirectory({
          token,
          query: debouncedQuery,
          issuer_type: issuerType !== "all" ? issuerType : undefined,
          bond_type: bondType !== "all" ? bondType : undefined,
          currency: currency !== "all" ? currency : undefined,
          coupon_type: couponType !== "all" ? couponType : undefined,
          maturity_bucket: maturityBucket !== "all" ? maturityBucket : undefined,
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
    [
      token,
      debouncedQuery,
      issuerType,
      bondType,
      currency,
      couponType,
      maturityBucket,
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
    setIssuerType("all");
    setBondType("all");
    setCurrency("all");
    setCouponType("all");
    setMaturityBucket("all");
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
    issuerType,
    setIssuerType: (it: string) => {
      setIssuerType(it);
      setCursor(null);
    },
    bondType,
    setBondType: (bt: string) => {
      setBondType(bt);
      setCursor(null);
    },
    currency,
    setCurrency: (c: string) => {
      setCurrency(c);
      setCursor(null);
    },
    couponType,
    setCouponType: (ct: string) => {
      setCouponType(ct);
      setCursor(null);
    },
    maturityBucket,
    setMaturityBucket: (mb: string) => {
      setMaturityBucket(mb);
      setCursor(null);
    },
    resetFilters,
    cursor,
    setCursor,
  };
}
