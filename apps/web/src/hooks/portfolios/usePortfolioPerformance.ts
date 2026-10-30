"use client";

import { useCallback, useEffect, useState } from "react";
import { performanceApi } from "@/lib/portfolios/performance/api";
import {
  BenchmarkDefinitionDTO,
  PerformanceCashFlowDTO,
  PerformanceMethodology,
  PerformancePeriodType,
  PerformanceResponse,
  PerformanceRunSummaryDTO,
  PerformanceSeriesPoint,
  PeriodicReturnDTO,
} from "@/lib/portfolios/performance/types";

export function usePortfolioPerformance(
  portfolioId: string | null,
  initialAccountId = "ALL"
) {
  const [selectedPeriod, setSelectedPeriod] = useState<PerformancePeriodType>("INCEPTION");
  const [selectedMethodology, setSelectedMethodology] = useState<PerformanceMethodology>("EXACT_TWR");
  const [selectedBenchmarkId, setSelectedBenchmarkId] = useState<string>("BENCHMARK_SP500");
  const [selectedAccountId, setSelectedAccountId] = useState<string>(initialAccountId);
  const [customStartDate, setCustomStartDate] = useState<string>("");
  const [customEndDate, setCustomEndDate] = useState<string>("");

  const [summary, setSummary] = useState<PerformanceResponse | null>(null);
  const [series, setSeries] = useState<PerformanceSeriesPoint[]>([]);
  const [periodicReturns, setPeriodicReturns] = useState<PeriodicReturnDTO[]>([]);
  const [cashFlows, setCashFlows] = useState<PerformanceCashFlowDTO[]>([]);
  const [benchmarks, setBenchmarks] = useState<BenchmarkDefinitionDTO[]>([]);
  const [runHistory, setRunHistory] = useState<PerformanceRunSummaryDTO[]>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [calculating, setCalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load canonical benchmarks on mount
  useEffect(() => {
    let ignore = false;
    performanceApi
      .getBenchmarks()
      .then((res) => {
        if (!ignore) {
          setBenchmarks(res.benchmarks || res.items || []);
        }
      })
      .catch((err) => {
        console.error("Failed to load benchmarks:", err);
      });
    return () => {
      ignore = true;
    };
  }, []);

  // Fetch performance data
  const fetchPerformanceData = useCallback(async () => {
    if (!portfolioId) return;

    setLoading(true);
    setError(null);

    try {
      const [sumRes, serRes, perRes, flowRes, runRes] = await Promise.all([
        performanceApi.getPerformanceSummary(portfolioId, {
          period_type: selectedPeriod,
          methodology: selectedMethodology,
          account_id: selectedAccountId,
          benchmark_id: selectedBenchmarkId,
          custom_start_date: selectedPeriod === "CUSTOM" ? customStartDate : undefined,
          custom_end_date: selectedPeriod === "CUSTOM" ? customEndDate : undefined,
        }),
        performanceApi.getPerformanceSeries(portfolioId, {
          period_type: selectedPeriod,
          account_id: selectedAccountId,
          benchmark_id: selectedBenchmarkId,
        }),
        performanceApi.getPeriodicReturns(portfolioId, {
          account_id: selectedAccountId,
        }),
        performanceApi.getClassifiedCashFlows(portfolioId, {
          period_type: selectedPeriod,
          account_id: selectedAccountId,
        }),
        performanceApi.getPerformanceRuns(portfolioId, { limit: 20 }),
      ]);

      setSummary(sumRes);
      setSeries(serRes.points || []);
      setPeriodicReturns(perRes.returns || []);
      setCashFlows(flowRes || []);
      setRunHistory(runRes.runs || runRes.items || []);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load performance analytics";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [
    portfolioId,
    selectedPeriod,
    selectedMethodology,
    selectedBenchmarkId,
    selectedAccountId,
    customStartDate,
    customEndDate,
  ]);

  useEffect(() => {
    fetchPerformanceData();
  }, [fetchPerformanceData]);

  // Explicit calculation trigger
  const triggerRecalculation = async () => {
    if (!portfolioId) return;

    setCalculating(true);
    setError(null);

    try {
      await performanceApi.calculatePerformance(portfolioId, {
        period_type: selectedPeriod,
        methodology: selectedMethodology,
        benchmark_id: selectedBenchmarkId !== "NONE" ? selectedBenchmarkId : undefined,
        account_id: selectedAccountId !== "ALL" ? selectedAccountId : undefined,
        custom_start_date: selectedPeriod === "CUSTOM" ? customStartDate : undefined,
        custom_end_date: selectedPeriod === "CUSTOM" ? customEndDate : undefined,
      });
      await fetchPerformanceData();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to recalculate performance";
      setError(msg);
    } finally {
      setCalculating(false);
    }
  };

  return {
    selectedPeriod,
    setSelectedPeriod,
    selectedMethodology,
    setSelectedMethodology,
    selectedBenchmarkId,
    setSelectedBenchmarkId,
    selectedAccountId,
    setSelectedAccountId,
    customStartDate,
    setCustomStartDate,
    customEndDate,
    setCustomEndDate,
    summary,
    series,
    periodicReturns,
    cashFlows,
    benchmarks,
    runHistory,
    loading,
    calculating,
    error,
    refresh: fetchPerformanceData,
    triggerRecalculation,
  };
}
