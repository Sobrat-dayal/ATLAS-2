"use client";

import { useCallback, useEffect, useState } from "react";
import {
  calculatePortfolioAttribution,
  fetchAttributionBenchmarks,
  fetchPortfolioAttribution,
} from "@/lib/portfolios/attribution/api";
import {
  AttributionBenchmarkSummaryDTO,
  AttributionDimension,
  AttributionMethod,
  AttributionRunDTO,
  CalculateAttributionRequestDTO,
} from "@/lib/portfolios/attribution/types";

export type AttributionTab =
  | "sectors"
  | "securities"
  | "multi_period"
  | "currency"
  | "benchmarks_audit";

export interface UsePortfolioAttributionReturn {
  run: AttributionRunDTO | null;
  benchmarks: AttributionBenchmarkSummaryDTO[];
  selectedBenchmark: string;
  selectedMethod: AttributionMethod;
  selectedDimension: AttributionDimension;
  activeTab: AttributionTab;
  loading: boolean;
  calculating: boolean;
  error: string | null;
  setSelectedBenchmark: (id: string) => void;
  setSelectedMethod: (method: AttributionMethod) => void;
  setSelectedDimension: (dimension: AttributionDimension) => void;
  setActiveTab: (tab: AttributionTab) => void;
  calculate: (overrideParams?: Partial<CalculateAttributionRequestDTO>) => Promise<void>;
  refresh: () => Promise<void>;
}

export function usePortfolioAttribution(portfolioId: string): UsePortfolioAttributionReturn {
  const [run, setRun] = useState<AttributionRunDTO | null>(null);
  const [benchmarks, setBenchmarks] = useState<AttributionBenchmarkSummaryDTO[]>([]);
  const [selectedBenchmark, setSelectedBenchmark] = useState<string>("BENCHMARK_SP500");
  const [selectedMethod, setSelectedMethod] = useState<AttributionMethod>("BRINSON_FACHLER");
  const [selectedDimension, setSelectedDimension] = useState<AttributionDimension>("SECTOR");
  const [activeTab, setActiveTab] = useState<AttributionTab>("sectors");
  const [loading, setLoading] = useState<boolean>(true);
  const [calculating, setCalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!portfolioId) return;
    setLoading(true);
    setError(null);
    try {
      const [attrRun, benchList] = await Promise.all([
        fetchPortfolioAttribution(portfolioId),
        fetchAttributionBenchmarks(portfolioId).catch(() => []),
      ]);
      setRun(attrRun);
      setBenchmarks(benchList);
      if (attrRun.benchmark_id) {
        setSelectedBenchmark(attrRun.benchmark_id);
      }
      if (attrRun.attribution_method) {
        setSelectedMethod(attrRun.attribution_method);
      }
      if (attrRun.classification_dimension) {
        setSelectedDimension(attrRun.classification_dimension);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load performance attribution.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [portfolioId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const calculate = useCallback(
    async (overrideParams?: Partial<CalculateAttributionRequestDTO>) => {
      if (!portfolioId) return;
      setCalculating(true);
      setError(null);
      try {
        const payload: CalculateAttributionRequestDTO = {
          benchmark_id: overrideParams?.benchmark_id || selectedBenchmark,
          attribution_method: overrideParams?.attribution_method || selectedMethod,
          classification_dimension: overrideParams?.classification_dimension || selectedDimension,
          include_currency_decomposition: true,
          include_multi_period_linking: true,
          ...overrideParams,
        };
        const updated = await calculatePortfolioAttribution(portfolioId, payload);
        setRun(updated);
        if (payload.benchmark_id) setSelectedBenchmark(payload.benchmark_id);
        if (payload.attribution_method) setSelectedMethod(payload.attribution_method);
        if (payload.classification_dimension) setSelectedDimension(payload.classification_dimension);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to calculate performance attribution.";
        setError(msg);
      } finally {
        setCalculating(false);
      }
    },
    [portfolioId, selectedBenchmark, selectedMethod, selectedDimension]
  );

  return {
    run,
    benchmarks,
    selectedBenchmark,
    selectedMethod,
    selectedDimension,
    activeTab,
    loading,
    calculating,
    error,
    setSelectedBenchmark,
    setSelectedMethod,
    setSelectedDimension,
    setActiveTab,
    calculate,
    refresh: loadData,
  };
}

