"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  CommodityDirectoryResponse,
  SpotBenchmarkDirectoryResponse,
  getCommodities,
  getSpotBenchmarks,
} from "@/lib/markets/futures";

export interface UseCommoditiesResult {
  data: CommodityDirectoryResponse | null;
  spotBenchmarks: SpotBenchmarkDirectoryResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  category: string;
  setCategory: (c: string) => void;
  query: string;
  setQuery: (q: string) => void;
  refetch: () => Promise<void>;
}

export function useCommodities(): UseCommoditiesResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [category, setCategory] = useState<string>("all");
  const [query, setQuery] = useState<string>("");
  const [data, setData] = useState<CommodityDirectoryResponse | null>(null);
  const [spotBenchmarks, setSpotBenchmarks] =
    useState<SpotBenchmarkDirectoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    setError(null);

    try {
      const [commRes, spotRes] = await Promise.all([
        getCommodities({
          token,
          category: category !== "all" ? category : undefined,
          query: query.trim() || undefined,
        }),
        getSpotBenchmarks({ token }),
      ]);
      setData(commRes);
      setSpotBenchmarks(spotRes);
    } catch (err) {
      setIsError(true);
      setError(
        err instanceof Error ? err : new Error("Failed to load commodities")
      );
    } finally {
      setIsLoading(false);
    }
  }, [token, category, query]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData();
  }, [fetchData]);

  return {
    data,
    spotBenchmarks,
    isLoading,
    isError,
    error,
    category,
    setCategory,
    query,
    setQuery,
    refetch: fetchData,
  };
}
