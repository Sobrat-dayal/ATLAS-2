"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { searchCompanies } from "@/lib/companies/api";
import { CompanySearchResult } from "@/lib/companies/types";

export interface UseCompanySearchResult {
  query: string;
  setQuery: (q: string) => void;
  results: CompanySearchResult[];
  total: number;
  loading: boolean;
  error: Error | null;
  page: number;
  setPage: (p: number) => void;
  search: (q?: string) => Promise<void>;
}

export function useCompanySearch(initialQuery: string = ""): UseCompanySearchResult {
  const [query, setQuery] = useState<string>(initialQuery);
  const [results, setResults] = useState<CompanySearchResult[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const activeControllerRef = useRef<AbortController | null>(null);

  const executeSearch = useCallback(
    async (searchQuery: string, pageNum: number) => {
      if (activeControllerRef.current) {
        activeControllerRef.current.abort();
      }

      const controller = new AbortController();
      activeControllerRef.current = controller;

      setLoading(true);
      setError(null);

      try {
        const resp = await searchCompanies(
          searchQuery,
          pageNum,
          20,
          undefined,
          undefined,
          controller.signal
        );
        setResults(resp.results);
        setTotal(resp.total);
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") return;
        setError(err instanceof Error ? err : new Error(String(err)));
        setResults([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // Debounced query effect
  useEffect(() => {
    const handler = setTimeout(() => {
      setPage(1);
      executeSearch(query, 1);
    }, 250);

    return () => {
      clearTimeout(handler);
    };
  }, [query, executeSearch]);

  // Page change effect
  const handlePageChange = useCallback(
    (newPage: number) => {
      setPage(newPage);
      executeSearch(query, newPage);
    },
    [query, executeSearch]
  );

  const search = useCallback(
    async (explicitQuery?: string) => {
      const q = explicitQuery !== undefined ? explicitQuery : query;
      setPage(1);
      await executeSearch(q, 1);
    },
    [query, executeSearch]
  );

  return {
    query,
    setQuery,
    results,
    total,
    loading,
    error,
    page,
    setPage: handlePageChange,
    search,
  };
}
