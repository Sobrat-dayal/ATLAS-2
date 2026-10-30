"use client";

import { useCallback, useEffect, useState } from "react";
import { portfoliosApi } from "@/lib/portfolios/api";
import { AccountDTO, PortfolioDTO } from "@/lib/portfolios/types";
import {
  calculateRisk,
  getPortfolioBenchmarkSensitivity,
  getPortfolioContributions,
  getPortfolioDrawdowns,
  getPortfolioRiskRuns,
  getPortfolioRiskSummary,
  getPortfolioVolatility,
  getRiskMetrics,
  getRiskModels,
} from "@/lib/risk/api";
import {
  AnnualizationPolicy,
  BenchmarkSensitivityDTO,
  ContributionsResponseDTO,
  DrawdownsResponseDTO,
  PortfolioRiskSummaryDTO,
  RiskCalculationRunDTO,
  RiskDataCoverageDTO,
  RiskMetricDefinitionDTO,
  RiskModelDefinitionDTO,
  RiskReturnFrequency,
  VolatilityResponseDTO,
} from "@/lib/risk/types";

export type RiskTab =
  | "overview"
  | "volatility"
  | "drawdowns"
  | "benchmark"
  | "contributions"
  | "models"
  | "data_quality"
  | "runs";

export interface UseRiskTerminalReturn {
  portfolios: PortfolioDTO[];
  selectedPortfolioId: string;
  activePortfolio: PortfolioDTO | null;
  accounts: AccountDTO[];
  selectedAccountId: string;
  summary: PortfolioRiskSummaryDTO | null;
  run: RiskCalculationRunDTO | null;
  volatilityData: VolatilityResponseDTO | null;
  drawdownData: DrawdownsResponseDTO | null;
  benchmarkSensitivity: BenchmarkSensitivityDTO | null;
  contributionsData: ContributionsResponseDTO | null;
  dataQuality: RiskDataCoverageDTO | null;
  runsList: RiskCalculationRunDTO[];
  metricsCatalog: RiskMetricDefinitionDTO[];
  modelsCatalog: RiskModelDefinitionDTO[];
  selectedBenchmark: string;
  selectedModelId: string;
  selectedFrequency: RiskReturnFrequency;
  annualizationPolicy: AnnualizationPolicy;
  rollingWindowSize: number;
  activeTab: RiskTab;
  loading: boolean;
  calculating: boolean;
  error: string | null;
  setSelectedPortfolioId: (id: string) => void;
  setSelectedAccountId: (id: string) => void;
  setSelectedBenchmark: (id: string) => void;
  setSelectedModelId: (id: string) => void;
  setSelectedFrequency: (freq: RiskReturnFrequency) => void;
  setRollingWindowSize: (size: number) => void;
  setActiveTab: (tab: RiskTab) => void;
  calculate: () => Promise<void>;
  refresh: () => Promise<void>;
}

export function useRiskTerminal(initialPortfolioId?: string): UseRiskTerminalReturn {
  const [portfolios, setPortfolios] = useState<PortfolioDTO[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>(initialPortfolioId || "");
  const [activePortfolio, setActivePortfolio] = useState<PortfolioDTO | null>(null);
  const [accounts, setAccounts] = useState<AccountDTO[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string>("ALL");

  const [summary, setSummary] = useState<PortfolioRiskSummaryDTO | null>(null);
  const [run, setRun] = useState<RiskCalculationRunDTO | null>(null);
  const [volatilityData, setVolatilityData] = useState<VolatilityResponseDTO | null>(null);
  const [drawdownData, setDrawdownData] = useState<DrawdownsResponseDTO | null>(null);
  const [benchmarkSensitivity, setBenchmarkSensitivity] = useState<BenchmarkSensitivityDTO | null>(null);
  const [contributionsData, setContributionsData] = useState<ContributionsResponseDTO | null>(null);
  const [dataQuality, setDataQuality] = useState<RiskDataCoverageDTO | null>(null);
  const [runsList, setRunsList] = useState<RiskCalculationRunDTO[]>([]);

  const [metricsCatalog, setMetricsCatalog] = useState<RiskMetricDefinitionDTO[]>([]);
  const [modelsCatalog, setModelsCatalog] = useState<RiskModelDefinitionDTO[]>([]);

  const [selectedBenchmark, setSelectedBenchmark] = useState<string>("BENCHMARK_SPY");
  const [selectedModelId, setSelectedModelId] = useState<string>("COVARIANCE_BASED_PORTFOLIO_RISK");
  const [selectedFrequency, setSelectedFrequency] = useState<RiskReturnFrequency>("DAILY");
  const [annualizationPolicy] = useState<AnnualizationPolicy>("DAYS_252");
  const [rollingWindowSize, setRollingWindowSize] = useState<number>(20);
  const [activeTab, setActiveTab] = useState<RiskTab>("overview");

  const [loading, setLoading] = useState<boolean>(true);
  const [calculating, setCalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load portfolios list and catalogs on mount
  useEffect(() => {
    let mounted = true;
    async function init() {
      try {
        const [portfoliosRes, metricsRes, modelsRes] = await Promise.all([
          portfoliosApi.listPortfolios().catch(() => ({ items: [], total: 0 })),
          getRiskMetrics().catch(() => []),
          getRiskModels().catch(() => []),
        ]);

        if (!mounted) return;
        setPortfolios(portfoliosRes.items || []);
        setMetricsCatalog(metricsRes || []);
        setModelsCatalog(modelsRes || []);

        if (portfoliosRes.items && portfoliosRes.items.length > 0 && !selectedPortfolioId) {
          setSelectedPortfolioId(portfoliosRes.items[0].id);
        }
      } catch (err: unknown) {
        if (!mounted) return;
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    init();
    return () => {
      mounted = false;
    };
  }, []);

  // Update active portfolio and accounts when selectedPortfolioId changes
  useEffect(() => {
    if (!selectedPortfolioId || portfolios.length === 0) return;
    const found = portfolios.find((p) => p.id === selectedPortfolioId) || null;
    setActivePortfolio(found);

    // Fetch accounts
    portfoliosApi
      .listAccounts(selectedPortfolioId)
      .then((accRes) => {
        setAccounts(accRes.items || []);
      })
      .catch(() => {
        setAccounts([]);
      });
  }, [selectedPortfolioId, portfolios]);

  // Load risk analytics for selected portfolio
  const loadRiskData = useCallback(async () => {
    if (!selectedPortfolioId) return;
    setLoading(true);
    setError(null);
    try {
      const accountParam = selectedAccountId === "ALL" ? undefined : selectedAccountId;

      const [summaryRes, volRes, ddRes, benchRes, contribRes, runsRes] = await Promise.all([
        getPortfolioRiskSummary(selectedPortfolioId, accountParam).catch(() => null),
        getPortfolioVolatility(selectedPortfolioId, { accountId: accountParam, windowSize: rollingWindowSize }).catch(() => null),
        getPortfolioDrawdowns(selectedPortfolioId, accountParam).catch(() => null),
        getPortfolioBenchmarkSensitivity(selectedPortfolioId, { accountId: accountParam, benchmarkId: selectedBenchmark }).catch(() => null),
        getPortfolioContributions(selectedPortfolioId, accountParam).catch(() => null),
        getPortfolioRiskRuns(selectedPortfolioId, 10).catch(() => ({ items: [], total: 0 })),
      ]);

      setSummary(summaryRes);
      setVolatilityData(volRes);
      setDrawdownData(ddRes);
      setBenchmarkSensitivity(benchRes);
      setContributionsData(contribRes);
      setRunsList(runsRes.items || []);

      if (runsRes.items && runsRes.items.length > 0) {
        setRun(runsRes.items[0]);
        setDataQuality(runsRes.items[0].data_coverage || null);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [selectedPortfolioId, selectedAccountId, rollingWindowSize, selectedBenchmark]);

  useEffect(() => {
    loadRiskData();
  }, [loadRiskData]);

  // Trigger on-demand calculation
  const calculate = useCallback(async () => {
    if (!selectedPortfolioId) return;
    setCalculating(true);
    setError(null);
    try {
      const accountParam = selectedAccountId === "ALL" ? undefined : selectedAccountId;
      const newRun = await calculateRisk({
        subject_type: "PORTFOLIO",
        subject_id: selectedPortfolioId,
        account_id: accountParam,
        model_id: selectedModelId,
        benchmark_id: selectedBenchmark,
        return_frequency: selectedFrequency,
        annualization_policy: annualizationPolicy,
        rolling_window_size: rollingWindowSize,
      });

      setRun(newRun);
      setDataQuality(newRun.data_coverage);
      await loadRiskData();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setCalculating(false);
    }
  }, [
    selectedPortfolioId,
    selectedAccountId,
    selectedModelId,
    selectedBenchmark,
    selectedFrequency,
    annualizationPolicy,
    rollingWindowSize,
    loadRiskData,
  ]);

  return {
    portfolios,
    selectedPortfolioId,
    activePortfolio,
    accounts,
    selectedAccountId,
    summary,
    run,
    volatilityData,
    drawdownData,
    benchmarkSensitivity,
    contributionsData,
    dataQuality,
    runsList,
    metricsCatalog,
    modelsCatalog,
    selectedBenchmark,
    selectedModelId,
    selectedFrequency,
    annualizationPolicy,
    rollingWindowSize,
    activeTab,
    loading,
    calculating,
    error,
    setSelectedPortfolioId,
    setSelectedAccountId,
    setSelectedBenchmark,
    setSelectedModelId,
    setSelectedFrequency,
    setRollingWindowSize,
    setActiveTab,
    calculate,
    refresh: loadRiskData,
  };
}
