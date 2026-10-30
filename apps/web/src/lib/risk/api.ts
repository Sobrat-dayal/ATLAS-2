/**
 * ATLAS Financial Risk Foundation — Typed API Client (Stage 115 & 116).
 */

import {
  BenchmarkSensitivityDTO,
  CalculateRiskRequestDTO,
  CalculateTailRiskRequest,
  ContributionsResponseDTO,
  CreateScenarioRequest,
  DrawdownsResponseDTO,
  ExecuteScenarioRequest,
  LossDistributionDTO,
  PortfolioRiskSummaryDTO,
  RiskCalculationRunDTO,
  RiskDataCoverageDTO,
  RiskInputManifestDTO,
  RiskMetricDefinitionDTO,
  RiskModelDefinitionDTO,
  RiskRunsListDTO,
  RiskScenarioDTO,
  RiskScenarioRunDTO,
  RunVaRBacktestRequest,
  ScenarioComparisonRequest,
  ScenarioComparisonResponseDTO,
  TailRiskCalculationRunDTO,
  VaRBacktestRunDTO,
  VaRModelType,
  VolatilityResponseDTO,
  CalculateFactorRiskRequest,
  ConcentrationDimension,
  ConcentrationSnapshotDTO,
  CrossExposureMatrixDTO,
  CurrencyExposureItemDTO,
  CurrencyRiskSnapshotDTO,
  FactorModelDiagnosticsDTO,
  FactorRiskContributionDTO,
  FactorRiskRunDTO,
  RiskFactorDefinitionDTO,
  SectorRiskItemDTO,
  SectorRiskSnapshotDTO,
  SecurityFactorExposureDTO,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred in the risk engine.';
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail =
          typeof errorJson.detail === 'object'
            ? errorJson.detail.message || JSON.stringify(errorJson.detail)
            : errorJson.detail;
      }
    } catch {
      errorDetail = `Request failed with status ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Retrieves catalog of available risk metrics.
 */
export async function getRiskMetrics(): Promise<RiskMetricDefinitionDTO[]> {
  return request<RiskMetricDefinitionDTO[]>('/risk/metrics');
}

/**
 * Retrieves catalog of available risk models.
 */
export async function getRiskModels(): Promise<RiskModelDefinitionDTO[]> {
  return request<RiskModelDefinitionDTO[]>('/risk/models');
}

/**
 * Triggers an institutional risk calculation run for a portfolio.
 */
export async function calculateRisk(req: CalculateRiskRequestDTO): Promise<RiskCalculationRunDTO> {
  return request<RiskCalculationRunDTO>('/risk/calculations', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Fetches a completed risk calculation run by ID.
 */
export async function getRiskCalculationRun(runId: string): Promise<RiskCalculationRunDTO> {
  return request<RiskCalculationRunDTO>(`/risk/calculations/${runId}`);
}

/**
 * Fetches the input audit manifest and provenance hash for a run.
 */
export async function getRiskInputManifest(runId: string): Promise<RiskInputManifestDTO> {
  return request<RiskInputManifestDTO>(`/risk/calculations/${runId}/sources`);
}

/**
 * Retrieves the latest portfolio risk summary.
 */
export async function getPortfolioRiskSummary(
  portfolioId: string,
  accountId?: string
): Promise<PortfolioRiskSummaryDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<PortfolioRiskSummaryDTO>(`/risk/portfolios/${portfolioId}${query}`);
}

/**
 * Retrieves annualized historical and rolling volatility series.
 */
export async function getPortfolioVolatility(
  portfolioId: string,
  options?: { accountId?: string; windowSize?: number }
): Promise<VolatilityResponseDTO> {
  const params = new URLSearchParams();
  if (options?.accountId) params.append('account_id', options.accountId);
  if (options?.windowSize) params.append('window_size', options.windowSize.toString());
  const queryString = params.toString() ? `?${params.toString()}` : '';
  return request<VolatilityResponseDTO>(`/risk/portfolios/${portfolioId}/volatility${queryString}`);
}

/**
 * Retrieves drawdown analysis, wealth index series, and episode breakdown.
 */
export async function getPortfolioDrawdowns(
  portfolioId: string,
  accountId?: string
): Promise<DrawdownsResponseDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<DrawdownsResponseDTO>(`/risk/portfolios/${portfolioId}/drawdowns${query}`);
}

/**
 * Retrieves benchmark sensitivity: beta, correlation, tracking error, covariance.
 */
export async function getPortfolioBenchmarkSensitivity(
  portfolioId: string,
  options?: { accountId?: string; benchmarkId?: string }
): Promise<BenchmarkSensitivityDTO> {
  const params = new URLSearchParams();
  if (options?.accountId) params.append('account_id', options.accountId);
  if (options?.benchmarkId) params.append('benchmark_id', options.benchmarkId);
  const queryString = params.toString() ? `?${params.toString()}` : '';
  return request<BenchmarkSensitivityDTO>(`/risk/portfolios/${portfolioId}/benchmark${queryString}`);
}

/**
 * Retrieves security-level Euler risk contributions and covariance diagnostics.
 */
export async function getPortfolioContributions(
  portfolioId: string,
  accountId?: string
): Promise<ContributionsResponseDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<ContributionsResponseDTO>(`/risk/portfolios/${portfolioId}/contributions${query}`);
}

/**
 * Retrieves data coverage, missing intervals, and input completeness audit.
 */
export async function getPortfolioDataQuality(
  portfolioId: string,
  accountId?: string
): Promise<RiskDataCoverageDTO> {
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : '';
  return request<RiskDataCoverageDTO>(`/risk/portfolios/${portfolioId}/quality${query}`);
}

/**
 * Retrieves historical risk calculation runs for auditing.
 */
export async function getPortfolioRiskRuns(
  portfolioId: string,
  limit: number = 20
): Promise<RiskRunsListDTO> {
  return request<RiskRunsListDTO>(`/risk/portfolios/${portfolioId}/runs?limit=${limit}`);
}

// ---------------------------------------------------------------------------
// Stage 116: VaR, Expected Shortfall, Scenarios, and Backtesting Endpoints
// ---------------------------------------------------------------------------

/**
 * Retrieves catalog of available VaR & Expected Shortfall models.
 */
export async function getTailRiskModels(): Promise<{ model_type: string; name: string; description: string }[]> {
  return request<{ model_type: string; name: string; description: string }[]>('/risk/tail/models');
}

/**
 * Executes on-demand VaR and Expected Shortfall calculation.
 */
export async function calculateTailRisk(
  req: CalculateTailRiskRequest
): Promise<TailRiskCalculationRunDTO> {
  return request<TailRiskCalculationRunDTO>('/risk/tail/calculate', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Retrieves the latest tail risk calculation for a portfolio.
 */
export async function getPortfolioTailRisk(
  portfolioId: string,
  options?: {
    accountId?: string;
    modelType?: VaRModelType;
    confidence?: number;
    horizon?: number;
  }
): Promise<TailRiskCalculationRunDTO> {
  const params = new URLSearchParams();
  if (options?.accountId) params.append('account_id', options.accountId);
  if (options?.modelType) params.append('model_type', options.modelType);
  if (options?.confidence) params.append('confidence_level', options.confidence.toString());
  if (options?.horizon) params.append('horizon_days', options.horizon.toString());
  const queryString = params.toString() ? `?${params.toString()}` : '';
  return request<TailRiskCalculationRunDTO>(`/risk/portfolios/${portfolioId}/tail${queryString}`);
}

/**
 * Retrieves a tail calculation run by ID.
 */
export async function getTailRun(runId: string): Promise<TailRiskCalculationRunDTO> {
  return request<TailRiskCalculationRunDTO>(`/risk/tail/runs/${runId}`);
}

/**
 * Retrieves the loss distribution histogram and quantiles for a tail run.
 */
export async function getTailDistribution(runId: string): Promise<LossDistributionDTO> {
  return request<LossDistributionDTO>(`/risk/tail/runs/${runId}/distribution`);
}

/**
 * Lists available risk scenarios (predefined historical episodes and custom).
 */
export async function getRiskScenarios(scenarioType?: string): Promise<RiskScenarioDTO[]> {
  const query = scenarioType ? `?scenario_type=${encodeURIComponent(scenarioType)}` : '';
  return request<RiskScenarioDTO[]>(`/risk/scenarios${query}`);
}

/**
 * Creates a new custom risk scenario.
 */
export async function createRiskScenario(req: CreateScenarioRequest): Promise<RiskScenarioDTO> {
  return request<RiskScenarioDTO>('/risk/scenarios', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Retrieves scenario details by ID.
 */
export async function getRiskScenario(scenarioId: string): Promise<RiskScenarioDTO> {
  return request<RiskScenarioDTO>(`/risk/scenarios/${scenarioId}`);
}

/**
 * Executes a scenario shock against a portfolio.
 */
export async function executeRiskScenario(
  req: ExecuteScenarioRequest
): Promise<RiskScenarioRunDTO> {
  return request<RiskScenarioRunDTO>('/risk/scenarios/execute', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Retrieves a completed scenario execution run.
 */
export async function getScenarioRun(runId: string): Promise<RiskScenarioRunDTO> {
  return request<RiskScenarioRunDTO>(`/risk/scenarios/runs/${runId}`);
}

/**
 * Compares portfolio impact across multiple scenarios.
 */
export async function compareRiskScenarios(
  req: ScenarioComparisonRequest
): Promise<ScenarioComparisonResponseDTO> {
  return request<ScenarioComparisonResponseDTO>('/risk/scenarios/compare', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Runs a rolling VaR backtest and Kupiec unconditional coverage test.
 */
export async function runVaRBacktest(
  req: RunVaRBacktestRequest
): Promise<VaRBacktestRunDTO> {
  return request<VaRBacktestRunDTO>('/risk/diagnostics/backtest', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Retrieves a saved VaR backtest result.
 */
export async function getVaRBacktest(backtestId: string): Promise<VaRBacktestRunDTO> {
  return request<VaRBacktestRunDTO>(`/risk/diagnostics/backtest/${backtestId}`);
}

// ---------------------------------------------------------------------------
// Stage 117: Factor, Concentration, Currency, and Sector Risk API Endpoints
// ---------------------------------------------------------------------------

/**
 * Retrieves the catalog of supported risk factors.
 */
export async function getRiskFactors(): Promise<RiskFactorDefinitionDTO[]> {
  return request<RiskFactorDefinitionDTO[]>('/risk/factors');
}

/**
 * Retrieves a single risk factor definition.
 */
export async function getRiskFactor(factorId: string): Promise<RiskFactorDefinitionDTO> {
  return request<RiskFactorDefinitionDTO>(`/risk/factors/${factorId}`);
}

/**
 * Executes a multi-factor portfolio risk calculation run.
 */
export async function calculateFactorRisk(
  req: CalculateFactorRiskRequest
): Promise<FactorRiskRunDTO> {
  return request<FactorRiskRunDTO>('/risk/factor-models/calculate', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Retrieves the latest factor risk run for a portfolio.
 */
export async function getPortfolioFactorRisk(portfolioId: string): Promise<FactorRiskRunDTO> {
  return request<FactorRiskRunDTO>(`/risk/portfolios/${portfolioId}/factors`);
}

/**
 * Retrieves security-level factor exposures.
 */
export async function getPortfolioFactorExposures(
  portfolioId: string
): Promise<SecurityFactorExposureDTO[]> {
  return request<SecurityFactorExposureDTO[]>(`/risk/portfolios/${portfolioId}/factors/exposures`);
}

/**
 * Retrieves factor risk contributions.
 */
export async function getPortfolioFactorContributions(
  portfolioId: string
): Promise<FactorRiskContributionDTO[]> {
  return request<FactorRiskContributionDTO[]>(`/risk/portfolios/${portfolioId}/factors/contributions`);
}

/**
 * Retrieves factor model diagnostics.
 */
export async function getPortfolioFactorDiagnostics(
  portfolioId: string
): Promise<FactorModelDiagnosticsDTO> {
  return request<FactorModelDiagnosticsDTO>(`/risk/portfolios/${portfolioId}/factors/diagnostics`);
}

/**
 * Retrieves portfolio concentration metrics (HHI, effective holdings, Top-N).
 */
export async function getPortfolioConcentration(
  portfolioId: string,
  dimension: ConcentrationDimension = 'SECURITY'
): Promise<ConcentrationSnapshotDTO> {
  return request<ConcentrationSnapshotDTO>(
    `/risk/portfolios/${portfolioId}/concentration?dimension=${dimension}`
  );
}

/**
 * Retrieves consolidated issuer concentration.
 */
export async function getPortfolioIssuerConcentration(
  portfolioId: string
): Promise<ConcentrationSnapshotDTO> {
  return request<ConcentrationSnapshotDTO>(`/risk/portfolios/${portfolioId}/concentration/issuers`);
}

/**
 * Retrieves currency denomination exposures, FX volatility, and return decomposition.
 */
export async function getPortfolioCurrencyRisk(
  portfolioId: string,
  reportingCurrency?: string
): Promise<CurrencyRiskSnapshotDTO> {
  const query = reportingCurrency ? `?reporting_currency=${reportingCurrency}` : '';
  return request<CurrencyRiskSnapshotDTO>(`/risk/portfolios/${portfolioId}/currencies${query}`);
}

/**
 * Retrieves currency exposure list.
 */
export async function getPortfolioCurrencyExposures(
  portfolioId: string
): Promise<CurrencyExposureItemDTO[]> {
  return request<CurrencyExposureItemDTO[]>(`/risk/portfolios/${portfolioId}/currencies/exposures`);
}

/**
 * Retrieves currency sensitivity details.
 */
export async function getPortfolioCurrencySensitivity(
  portfolioId: string
): Promise<{
  portfolio_id: string;
  reporting_currency: string;
  foreign_currency_weight: number;
  base_local_interaction: Record<string, number>;
  sensitivities: Record<string, any>;
}> {
  return request(`/risk/portfolios/${portfolioId}/currencies/sensitivity`);
}

/**
 * Retrieves sector Euler risk attribution snapshot.
 */
export async function getPortfolioSectorRisk(
  portfolioId: string
): Promise<SectorRiskSnapshotDTO> {
  return request<SectorRiskSnapshotDTO>(`/risk/portfolios/${portfolioId}/sectors`);
}

/**
 * Retrieves sector Euler contributions list.
 */
export async function getPortfolioSectorContributions(
  portfolioId: string
): Promise<SectorRiskItemDTO[]> {
  return request<SectorRiskItemDTO[]>(`/risk/portfolios/${portfolioId}/sectors/contributions`);
}

/**
 * Retrieves 2D cross-exposure matrix.
 */
export async function getPortfolioCrossExposure(
  portfolioId: string,
  rowDimension: string = 'FACTOR',
  colDimension: string = 'SECTOR'
): Promise<CrossExposureMatrixDTO> {
  return request<CrossExposureMatrixDTO>(
    `/risk/portfolios/${portfolioId}/cross-exposures?row_dimension=${rowDimension}&col_dimension=${colDimension}`
  );
}

/**
 * Retrieves portfolio vs benchmark factor exposures.
 */
export async function getPortfolioFactorBenchmark(
  portfolioId: string
): Promise<{
  portfolio_id: string;
  portfolio_exposures: Record<string, number>;
  benchmark_exposures: Record<string, number>;
  active_factor_exposures: Record<string, number>;
}> {
  return request(`/risk/portfolios/${portfolioId}/factor-benchmark`);
}
