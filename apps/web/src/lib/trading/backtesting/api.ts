/**
 * Client API interface for ATLAS NautilusTrader Historical Backtesting (Stage 143).
 */

import {
  AtlasBacktestConfig,
  AtlasBacktestResult,
  AtlasStrategyDefinition,
  BacktestComparisonResult,
  HistoricalDatasetManifest,
  ParameterExperimentConfig,
  ParameterExperimentResult,
  WalkForwardResult,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getBacktestCapabilities() {
  const res = await fetch(`${API_BASE}/api/v1/trading/backtests/capabilities`);
  if (!res.ok) throw new Error(`Failed to fetch backtest capabilities: ${res.statusText}`);
  return res.json();
}

export async function listBacktestStrategies(): Promise<AtlasStrategyDefinition[]> {
  const res = await fetch(`${API_BASE}/api/v1/trading/backtests/strategies`);
  if (!res.ok) throw new Error(`Failed to list backtest strategies: ${res.statusText}`);
  const data = await res.json();
  return data.strategies;
}

export async function listBacktestDatasets(): Promise<HistoricalDatasetManifest[]> {
  const res = await fetch(`${API_BASE}/api/v1/trading/backtests/datasets`);
  if (!res.ok) throw new Error(`Failed to list backtest datasets: ${res.statusText}`);
  const data = await res.json();
  return data.datasets;
}

export async function executeBacktestRun(
  config: AtlasBacktestConfig,
  token?: string,
): Promise<AtlasBacktestResult> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/trading/backtests/runs`, {
    method: "POST",
    headers,
    body: JSON.stringify(config),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Backtest execution failed: ${res.statusText}`);
  }
  return res.json();
}

export async function getBacktestRun(
  runId: string,
  token?: string,
): Promise<AtlasBacktestResult> {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(
    `${API_BASE}/api/v1/trading/backtests/runs/${encodeURIComponent(runId)}`,
    { headers },
  );
  if (!res.ok) throw new Error(`Failed to retrieve backtest run: ${res.statusText}`);
  return res.json();
}

export async function runParameterExperiment(
  experimentConfig: ParameterExperimentConfig,
  token?: string,
): Promise<ParameterExperimentResult> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/trading/backtests/experiments`, {
    method: "POST",
    headers,
    body: JSON.stringify(experimentConfig),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Parameter experiment failed: ${res.statusText}`);
  }
  return res.json();
}

export async function runWalkForwardValidation(
  payload: {
    base_config: AtlasBacktestConfig;
    fold_windows: Array<{
      train_start: string;
      train_end: string;
      test_start: string;
      test_end: string;
    }>;
    param_candidates?: Array<Record<string, any>>;
  },
  token?: string,
): Promise<WalkForwardResult> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/trading/backtests/walk-forward`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Walk-forward validation failed: ${res.statusText}`);
  }
  return res.json();
}

export async function compareBacktestRuns(
  runIds: string[],
  token?: string,
): Promise<BacktestComparisonResult> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/v1/trading/backtests/compare`, {
    method: "POST",
    headers,
    body: JSON.stringify({ run_ids: runIds }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Run comparison failed: ${res.statusText}`);
  }
  return res.json();
}
