"use client";

import { useCallback, useEffect, useState } from "react";
import { portfoliosApi } from "@/lib/portfolios/api";
import { AccountDTO, PortfolioDTO } from "@/lib/portfolios/types";
import {
  calculateRisk,
  calculateTailRisk,
  compareRiskScenarios,
  createRiskScenario,
  executeRiskScenario,
  getPortfolioBenchmarkSensitivity,
  getPortfolioContributions,
  getPortfolioDrawdowns,
  getPortfolioRiskRuns,
  getPortfolioRiskSummary,
  getPortfolioTailRisk,
  getPortfolioVolatility,
  getRiskMetrics,
  getRiskModels,
  getRiskScenarios,
  getTailDistribution,
  runVaRBacktest,
  calculateFactorRisk,
  getPortfolioFactorRisk,
  getPortfolioConcentration,
  getPortfolioCurrencyRisk,
  getPortfolioSectorRisk,
  getPortfolioCrossExposure,
} from "@/lib/risk/api";
import {
  AnnualizationPolicy,
  BenchmarkSensitivityDTO,
  ContributionsResponseDTO,
  CreateScenarioRequest,
  DrawdownsResponseDTO,
  LossDistributionDTO,
  PortfolioRiskSummaryDTO,
  RiskCalculationRunDTO,
  RiskDataCoverageDTO,
  RiskMetricDefinitionDTO,
  RiskModelDefinitionDTO,
  RiskReturnFrequency,
  RiskScenarioDTO,
  RiskScenarioRunDTO,
  ScenarioComparisonResponseDTO,
  TailRiskCalculationRunDTO,
  VaRBacktestRunDTO,
  VaRModelType,
  VolatilityResponseDTO,
  CalculateFactorRiskRequest,
  ConcentrationDimension,
  ConcentrationSnapshotDTO,
  CrossExposureMatrixDTO,
  CurrencyRiskSnapshotDTO,
  FactorRiskRunDTO,
  SectorRiskSnapshotDTO,
  SecurityFactorExposureDTO,
} from "@/lib/risk/types";

export type RiskTab =
  | "overview"
  | "factors"
  | "concentration"
  | "currency"
  | "sectors"
  | "cross_exposure"
  | "tail_risk"
  | "scenarios"
  | "diagnostics"
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

  // Stage 116 State
  tailRiskRun: TailRiskCalculationRunDTO | null;
  tailDistribution: LossDistributionDTO | null;
  selectedTailModel: VaRModelType;
  selectedConfidence: number;
  selectedHorizon: number;
  calculatingTail: boolean;

  scenarios: RiskScenarioDTO[];
  activeScenarioRun: RiskScenarioRunDTO | null;
  scenarioComparison: ScenarioComparisonResponseDTO | null;
  executingScenario: boolean;
  comparingScenarios: boolean;

  backtestRun: VaRBacktestRunDTO | null;
  backtestModel: VaRModelType;
  backtestConfidence: number;
  backtestWindowSize: number;
  runningBacktest: boolean;

  // Stage 117 State
  factorRun: FactorRiskRunDTO | null;
  calculatingFactors: boolean;
  concentrationSnapshot: ConcentrationSnapshotDTO | null;
  selectedConcentrationDimension: ConcentrationDimension;
  currencySnapshot: CurrencyRiskSnapshotDTO | null;
  sectorSnapshot: SectorRiskSnapshotDTO | null;
  crossExposureMatrix: CrossExposureMatrixDTO | null;
  selectedCrossRowDim: string;
  selectedCrossColDim: string;
  loadingConcentration: boolean;
  loadingCurrency: boolean;
  loadingSector: boolean;
  loadingCross: boolean;

  // Setters & Actions
  setSelectedPortfolioId: (id: string) => void;
  setSelectedAccountId: (id: string) => void;
  setSelectedBenchmark: (id: string) => void;
  setSelectedModelId: (id: string) => void;
  setSelectedFrequency: (freq: RiskReturnFrequency) => void;
  setRollingWindowSize: (size: number) => void;
  setActiveTab: (tab: RiskTab) => void;

  setSelectedTailModel: (model: VaRModelType) => void;
  setSelectedConfidence: (conf: number) => void;
  setSelectedHorizon: (horizon: number) => void;
  setBacktestModel: (model: VaRModelType) => void;
  setBacktestConfidence: (conf: number) => void;
  setBacktestWindowSize: (size: number) => void;

  calculate: () => Promise<void>;
  calculateTailRiskAction: (
    overrideModel?: VaRModelType,
    overrideConf?: number,
    overrideHorizon?: number
  ) => Promise<void>;
  executeScenarioAction: (scenarioId: string) => Promise<void>;
  createScenarioAction: (req: CreateScenarioRequest) => Promise<RiskScenarioDTO>;
  compareScenariosAction: (scenarioIds?: string[]) => Promise<void>;
  runBacktestAction: (
    overrideModel?: VaRModelType,
    overrideConf?: number,
    overrideWindow?: number
  ) => Promise<void>;
  // Stage 117 Actions
  calculateFactorsAction: (modelId?: string, factorIds?: string[]) => Promise<void>;
  loadConcentrationAction: (dim?: ConcentrationDimension) => Promise<void>;
  loadCurrencyRiskAction: (reportingCurrency?: string) => Promise<void>;
  loadSectorRiskAction: () => Promise<void>;
  loadCrossExposureAction: (rowDim?: string, colDim?: string) => Promise<void>;
  setSelectedConcentrationDimension: (dim: ConcentrationDimension) => void;
  setSelectedCrossRowDim: (dim: string) => void;
  setSelectedCrossColDim: (dim: string) => void;
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

  // Stage 116 State
  const [tailRiskRun, setTailRiskRun] = useState<TailRiskCalculationRunDTO | null>(null);
  const [tailDistribution, setTailDistribution] = useState<LossDistributionDTO | null>(null);
  const [selectedTailModel, setSelectedTailModel] = useState<VaRModelType>("HISTORICAL_SIMULATION");
  const [selectedConfidence, setSelectedConfidence] = useState<number>(0.95);
  const [selectedHorizon, setSelectedHorizon] = useState<number>(1);
  const [calculatingTail, setCalculatingTail] = useState<boolean>(false);

  const [scenarios, setScenarios] = useState<RiskScenarioDTO[]>([]);
  const [activeScenarioRun, setActiveScenarioRun] = useState<RiskScenarioRunDTO | null>(null);
  const [scenarioComparison, setScenarioComparison] = useState<ScenarioComparisonResponseDTO | null>(null);
  const [executingScenario, setExecutingScenario] = useState<boolean>(false);
  const [comparingScenarios, setComparingScenarios] = useState<boolean>(false);

  const [backtestRun, setBacktestRun] = useState<VaRBacktestRunDTO | null>(null);
  const [backtestModel, setBacktestModel] = useState<VaRModelType>("HISTORICAL_SIMULATION");
  const [backtestConfidence, setBacktestConfidence] = useState<number>(0.95);
  const [backtestWindowSize, setBacktestWindowSize] = useState<number>(250);
  const [runningBacktest, setRunningBacktest] = useState<boolean>(false);

  // Stage 117 State
  const [factorRun, setFactorRun] = useState<FactorRiskRunDTO | null>(null);
  const [calculatingFactors, setCalculatingFactors] = useState<boolean>(false);
  const [concentrationSnapshot, setConcentrationSnapshot] = useState<ConcentrationSnapshotDTO | null>(null);
  const [selectedConcentrationDimension, setSelectedConcentrationDimension] = useState<ConcentrationDimension>("SECURITY");
  const [currencySnapshot, setCurrencySnapshot] = useState<CurrencyRiskSnapshotDTO | null>(null);
  const [sectorSnapshot, setSectorSnapshot] = useState<SectorRiskSnapshotDTO | null>(null);
  const [crossExposureMatrix, setCrossExposureMatrix] = useState<CrossExposureMatrixDTO | null>(null);
  const [selectedCrossRowDim, setSelectedCrossRowDim] = useState<string>("FACTOR");
  const [selectedCrossColDim, setSelectedCrossColDim] = useState<string>("SECTOR");
  const [loadingConcentration, setLoadingConcentration] = useState<boolean>(false);
  const [loadingCurrency, setLoadingCurrency] = useState<boolean>(false);
  const [loadingSector, setLoadingSector] = useState<boolean>(false);
  const [loadingCross, setLoadingCross] = useState<boolean>(false);

  // Load portfolios list and catalogs on mount
  useEffect(() => {
    let mounted = true;
    async function init() {
      try {
        const [portfoliosRes, metricsRes, modelsRes, scenariosRes] = await Promise.all([
          portfoliosApi.listPortfolios().catch(() => ({ items: [], total: 0 })),
          getRiskMetrics().catch(() => []),
          getRiskModels().catch(() => []),
          getRiskScenarios().catch(() => []),
        ]);

        if (!mounted) return;
        setPortfolios(portfoliosRes.items || []);
        setMetricsCatalog(metricsRes || []);
        setModelsCatalog(modelsRes || []);
        setScenarios(scenariosRes || []);

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

      const [summaryRes, volRes, ddRes, benchRes, contribRes, runsRes, tailRes, factorRes, concRes, currRes, secRes, crossRes] =
        await Promise.all([
          getPortfolioRiskSummary(selectedPortfolioId, accountParam).catch(() => null),
          getPortfolioVolatility(selectedPortfolioId, {
            accountId: accountParam,
            windowSize: rollingWindowSize,
          }).catch(() => null),
          getPortfolioDrawdowns(selectedPortfolioId, accountParam).catch(() => null),
          getPortfolioBenchmarkSensitivity(selectedPortfolioId, {
            accountId: accountParam,
            benchmarkId: selectedBenchmark,
          }).catch(() => null),
          getPortfolioContributions(selectedPortfolioId, accountParam).catch(() => null),
          getPortfolioRiskRuns(selectedPortfolioId, 10).catch(() => ({ items: [], total: 0 })),
          getPortfolioTailRisk(selectedPortfolioId, {
            accountId: accountParam,
            modelType: selectedTailModel,
            confidence: selectedConfidence,
            horizon: selectedHorizon,
          }).catch(() => null),
          getPortfolioFactorRisk(selectedPortfolioId).catch(() => null),
          getPortfolioConcentration(selectedPortfolioId, selectedConcentrationDimension).catch(() => null),
          getPortfolioCurrencyRisk(selectedPortfolioId).catch(() => null),
          getPortfolioSectorRisk(selectedPortfolioId).catch(() => null),
          getPortfolioCrossExposure(selectedPortfolioId, selectedCrossRowDim, selectedCrossColDim).catch(() => null),
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

      if (tailRes) {
        setTailRiskRun(tailRes);
        if (tailRes.loss_distribution) {
          setTailDistribution(tailRes.loss_distribution);
        } else if (tailRes.run_id) {
          getTailDistribution(tailRes.run_id)
            .then(setTailDistribution)
            .catch(() => {});
        }
      }

      if (factorRes) setFactorRun(factorRes);
      if (concRes) setConcentrationSnapshot(concRes);
      if (currRes) setCurrencySnapshot(currRes);
      if (secRes) setSectorSnapshot(secRes);
      if (crossRes) setCrossExposureMatrix(crossRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [
    selectedPortfolioId,
    selectedAccountId,
    rollingWindowSize,
    selectedBenchmark,
    selectedTailModel,
    selectedConfidence,
    selectedHorizon,
    selectedConcentrationDimension,
    selectedCrossRowDim,
    selectedCrossColDim,
  ]);

  useEffect(() => {
    loadRiskData();
  }, [loadRiskData]);

  // Trigger on-demand foundation calculation
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

  // Stage 116: Trigger on-demand VaR & Expected Shortfall calculation
  const calculateTailRiskAction = useCallback(
    async (
      overrideModel?: VaRModelType,
      overrideConf?: number,
      overrideHorizon?: number
    ) => {
      if (!selectedPortfolioId) return;
      setCalculatingTail(true);
      setError(null);
      try {
        const model = overrideModel || selectedTailModel;
        const conf = overrideConf || selectedConfidence;
        const horizon = overrideHorizon || selectedHorizon;
        const accountParam = selectedAccountId === "ALL" ? undefined : selectedAccountId;

        const newTailRun = await calculateTailRisk({
          portfolio_id: selectedPortfolioId,
          model_type: model,
          confidence_level: conf,
          horizon_days: horizon,
          account_id: accountParam,
        });

        setTailRiskRun(newTailRun);
        if (newTailRun.loss_distribution) {
          setTailDistribution(newTailRun.loss_distribution);
        } else if (newTailRun.run_id) {
          const dist = await getTailDistribution(newTailRun.run_id).catch(() => null);
          setTailDistribution(dist);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setCalculatingTail(false);
      }
    },
    [selectedPortfolioId, selectedAccountId, selectedTailModel, selectedConfidence, selectedHorizon]
  );

  // Stage 116: Execute a Scenario Shock
  const executeScenarioAction = useCallback(
    async (scenarioId: string) => {
      if (!selectedPortfolioId) return;
      setExecutingScenario(true);
      setError(null);
      try {
        const accountParam = selectedAccountId === "ALL" ? undefined : selectedAccountId;
        const runRes = await executeRiskScenario({
          scenario_id: scenarioId,
          portfolio_id: selectedPortfolioId,
          account_id: accountParam,
        });
        setActiveScenarioRun(runRes);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setExecutingScenario(false);
      }
    },
    [selectedPortfolioId, selectedAccountId]
  );

  // Stage 116: Create a Custom Scenario
  const createScenarioAction = useCallback(
    async (req: CreateScenarioRequest): Promise<RiskScenarioDTO> => {
      try {
        const newScen = await createRiskScenario(req);
        const refreshed = await getRiskScenarios().catch(() => []);
        setScenarios(refreshed);
        return newScen;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        throw err;
      }
    },
    []
  );

  // Stage 116: Compare Multiple Scenarios
  const compareScenariosAction = useCallback(
    async (scenarioIds?: string[]) => {
      if (!selectedPortfolioId) return;
      setComparingScenarios(true);
      setError(null);
      try {
        const accountParam = selectedAccountId === "ALL" ? undefined : selectedAccountId;
        const compRes = await compareRiskScenarios({
          portfolio_id: selectedPortfolioId,
          scenario_ids: scenarioIds,
          account_id: accountParam,
        });
        setScenarioComparison(compRes);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setComparingScenarios(false);
      }
    },
    [selectedPortfolioId, selectedAccountId]
  );

  // Stage 116: Run VaR Backtest & Kupiec POF Test
  const runBacktestAction = useCallback(
    async (
      overrideModel?: VaRModelType,
      overrideConf?: number,
      overrideWindow?: number
    ) => {
      if (!selectedPortfolioId) return;
      setRunningBacktest(true);
      setError(null);
      try {
        const model = overrideModel || backtestModel;
        const conf = overrideConf || backtestConfidence;
        const win = overrideWindow || backtestWindowSize;
        const accountParam = selectedAccountId === "ALL" ? undefined : selectedAccountId;

        const btestRes = await runVaRBacktest({
          portfolio_id: selectedPortfolioId,
          model_type: model,
          confidence_level: conf,
          window_size: win,
          account_id: accountParam,
        });
        setBacktestRun(btestRes);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setRunningBacktest(false);
      }
    },
    [selectedPortfolioId, selectedAccountId, backtestModel, backtestConfidence, backtestWindowSize]
  );

  // Stage 117: Calculate multi-factor risk
  const calculateFactorsAction = useCallback(
    async (modelId?: string, factorIds?: string[]) => {
      if (!selectedPortfolioId) return;
      setCalculatingFactors(true);
      setError(null);
      try {
        const accountParam = selectedAccountId === "ALL" ? undefined : selectedAccountId;
        const res = await calculateFactorRisk({
          portfolio_id: selectedPortfolioId,
          account_id: accountParam,
          model_id: modelId || "FAMA_FRENCH_6",
          factor_ids: factorIds,
        });
        setFactorRun(res);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setCalculatingFactors(false);
      }
    },
    [selectedPortfolioId, selectedAccountId]
  );

  const loadConcentrationAction = useCallback(
    async (dim?: ConcentrationDimension) => {
      if (!selectedPortfolioId) return;
      const targetDim = dim || selectedConcentrationDimension;
      setLoadingConcentration(true);
      setError(null);
      try {
        const res = await getPortfolioConcentration(selectedPortfolioId, targetDim);
        setConcentrationSnapshot(res);
        if (dim) setSelectedConcentrationDimension(dim);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setLoadingConcentration(false);
      }
    },
    [selectedPortfolioId, selectedConcentrationDimension]
  );

  const loadCurrencyRiskAction = useCallback(
    async (reportingCurrency?: string) => {
      if (!selectedPortfolioId) return;
      setLoadingCurrency(true);
      setError(null);
      try {
        const res = await getPortfolioCurrencyRisk(selectedPortfolioId, reportingCurrency);
        setCurrencySnapshot(res);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setLoadingCurrency(false);
      }
    },
    [selectedPortfolioId]
  );

  const loadSectorRiskAction = useCallback(async () => {
    if (!selectedPortfolioId) return;
    setLoadingSector(true);
    setError(null);
    try {
      const res = await getPortfolioSectorRisk(selectedPortfolioId);
      setSectorSnapshot(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setLoadingSector(false);
    }
  }, [selectedPortfolioId]);

  const loadCrossExposureAction = useCallback(
    async (rowDim?: string, colDim?: string) => {
      if (!selectedPortfolioId) return;
      const r = rowDim || selectedCrossRowDim;
      const c = colDim || selectedCrossColDim;
      setLoadingCross(true);
      setError(null);
      try {
        const res = await getPortfolioCrossExposure(selectedPortfolioId, r, c);
        setCrossExposureMatrix(res);
        if (rowDim) setSelectedCrossRowDim(rowDim);
        if (colDim) setSelectedCrossColDim(colDim);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      } finally {
        setLoadingCross(false);
      }
    },
    [selectedPortfolioId, selectedCrossRowDim, selectedCrossColDim]
  );

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

    // Stage 116 State
    tailRiskRun,
    tailDistribution,
    selectedTailModel,
    selectedConfidence,
    selectedHorizon,
    calculatingTail,

    scenarios,
    activeScenarioRun,
    scenarioComparison,
    executingScenario,
    comparingScenarios,

    backtestRun,
    backtestModel,
    backtestConfidence,
    backtestWindowSize,
    runningBacktest,

    // Stage 117 State
    factorRun,
    calculatingFactors,
    concentrationSnapshot,
    selectedConcentrationDimension,
    currencySnapshot,
    sectorSnapshot,
    crossExposureMatrix,
    selectedCrossRowDim,
    selectedCrossColDim,
    loadingConcentration,
    loadingCurrency,
    loadingSector,
    loadingCross,

    // Setters & Actions
    setSelectedPortfolioId,
    setSelectedAccountId,
    setSelectedBenchmark,
    setSelectedModelId,
    setSelectedFrequency,
    setRollingWindowSize,
    setActiveTab,

    setSelectedTailModel,
    setSelectedConfidence,
    setSelectedHorizon,
    setBacktestModel,
    setBacktestConfidence,
    setBacktestWindowSize,

    calculate,
    calculateTailRiskAction,
    executeScenarioAction,
    createScenarioAction,
    compareScenariosAction,
    runBacktestAction,

    // Stage 117 Actions
    calculateFactorsAction,
    loadConcentrationAction,
    loadCurrencyRiskAction,
    loadSectorRiskAction,
    loadCrossExposureAction,
    setSelectedConcentrationDimension,
    setSelectedCrossRowDim,
    setSelectedCrossColDim,
    refresh: loadRiskData,
  };
}
