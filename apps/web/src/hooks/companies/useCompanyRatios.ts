"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getCompanyRatios,
  getRatioCatalog,
  getRatioHistory,
  getRatioLineage,
  getRatioMethodology,
} from "@/lib/companies/ratios/api";
import {
  CompanyRatiosResponse,
  RatioCatalogResponse,
  RatioCategory,
  RatioHistoryResponse,
  RatioLineageResponse,
  RatioMethodologyResponse,
  RatioPeriodType,
} from "@/lib/companies/ratios/types";

export interface UseCompanyRatiosOptions {
  initialPeriodId?: string;
  initialPeriodType?: RatioPeriodType;
  initialCategory?: RatioCategory | "all";
}

export function useCompanyRatios(
  companyId: string | null,
  options: UseCompanyRatiosOptions = {}
) {
  const [category, setCategory] = useState<RatioCategory | "all">(
    options.initialCategory || "all"
  );
  const [periodId, setPeriodId] = useState<string>(
    options.initialPeriodId || "FY2024"
  );
  const [periodType, setPeriodType] = useState<RatioPeriodType>(
    options.initialPeriodType || "ANNUAL"
  );

  const [catalog, setCatalog] = useState<RatioCatalogResponse | null>(null);
  const [ratiosData, setRatiosData] = useState<CompanyRatiosResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Historical trend state
  const [historyRatioId, setHistoryRatioId] = useState<string | null>(
    "profitability.gross_margin"
  );
  const [historyData, setHistoryData] = useState<RatioHistoryResponse | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);

  // Inspector state (methodology & lineage)
  const [inspectedRatioId, setInspectedRatioId] = useState<string | null>(null);
  const [methodologyData, setMethodologyData] =
    useState<RatioMethodologyResponse | null>(null);
  const [lineageData, setLineageData] = useState<RatioLineageResponse | null>(null);
  const [isInspectionLoading, setIsInspectionLoading] = useState<boolean>(false);

  // 1. Load Catalog on mount / company change
  useEffect(() => {
    if (!companyId) return;

    let isMounted = true;
    getRatioCatalog(companyId)
      .then((cat) => {
        if (isMounted) setCatalog(cat);
      })
      .catch((err) => {
        if (isMounted) console.error("Catalog load error:", err);
      });

    return () => {
      isMounted = false;
    };
  }, [companyId]);

  // 2. Fetch company ratios when parameters change
  const fetchRatios = useCallback(async () => {
    if (!companyId) return;
    setIsLoading(true);
    setError(null);

    try {
      const data = await getCompanyRatios(
        companyId,
        periodId,
        periodType,
        category === "all" ? undefined : category
      );
      setRatiosData(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load financial ratios";
      setError(msg);
      setRatiosData(null);
    } finally {
      setIsLoading(false);
    }
  }, [companyId, periodId, periodType, category]);

  useEffect(() => {
    fetchRatios();
  }, [fetchRatios]);

  // 3. Fetch historical trend series
  const fetchHistory = useCallback(
    async (ratioId: string) => {
      if (!companyId) return;
      setIsHistoryLoading(true);
      try {
        const hist = await getRatioHistory(companyId, ratioId, periodType, 10);
        setHistoryData(hist);
        setHistoryRatioId(ratioId);
      } catch (err: unknown) {
        console.error("Failed to load ratio history:", err);
        setHistoryData(null);
      } finally {
        setIsHistoryLoading(false);
      }
    },
    [companyId, periodType]
  );

  useEffect(() => {
    if (historyRatioId) {
      fetchHistory(historyRatioId);
    }
  }, [historyRatioId, fetchHistory]);

  // 4. Fetch formula methodology & lineage
  const inspectRatio = useCallback(
    async (ratioId: string) => {
      if (!companyId) return;
      setInspectedRatioId(ratioId);
      setIsInspectionLoading(true);
      try {
        const [meth, lin] = await Promise.all([
          getRatioMethodology(companyId, ratioId),
          getRatioLineage(companyId, ratioId, periodId),
        ]);
        setMethodologyData(meth);
        setLineageData(lin);
      } catch (err: unknown) {
        console.error("Failed to inspect ratio:", err);
        setMethodologyData(null);
        setLineageData(null);
      } finally {
        setIsInspectionLoading(false);
      }
    },
    [companyId, periodId]
  );

  const closeInspector = useCallback(() => {
    setInspectedRatioId(null);
    setMethodologyData(null);
    setLineageData(null);
  }, []);

  return {
    category,
    setCategory,
    periodId,
    setPeriodId,
    periodType,
    setPeriodType,
    catalog,
    ratiosData,
    isLoading,
    error,
    refresh: fetchRatios,
    // History
    historyRatioId,
    historyData,
    isHistoryLoading,
    selectHistoryRatio: fetchHistory,
    // Inspection
    inspectedRatioId,
    methodologyData,
    lineageData,
    isInspectionLoading,
    inspectRatio,
    closeInspector,
  };
}
