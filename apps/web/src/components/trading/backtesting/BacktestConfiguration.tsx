"use client";

import React, { useState } from "react";
import {
  AtlasBacktestConfig,
  AtlasStrategyDefinition,
  FillModelType,
  HistoricalDatasetManifest,
  SlippagePolicy,
  FeeModelType,
  LatencyModelType,
} from "@/lib/trading/backtesting/types";
import { validateBacktestConfig } from "@/lib/trading/backtesting/formatters";
import {
  Play,
  Settings,
  ShieldAlert,
  Sliders,
  Database,
  DollarSign,
  Cpu,
  Layers,
  AlertTriangle,
} from "lucide-react";

interface BacktestConfigurationProps {
  strategies: AtlasStrategyDefinition[];
  datasets: HistoricalDatasetManifest[];
  isRunning: boolean;
  onExecute: (config: AtlasBacktestConfig) => Promise<void>;
}

export function BacktestConfiguration({
  strategies,
  datasets,
  isRunning,
  onExecute,
}: BacktestConfigurationProps) {
  const [selectedStrategyId, setSelectedStrategyId] = useState<string>(
    strategies[0]?.strategy_id || "BUY_AND_HOLD",
  );
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>(
    datasets[0]?.dataset_id || "ds_spy_daily_2024",
  );
  const [initialCash, setInitialCash] = useState<number>(100000);
  const [accountType, setAccountType] = useState<"CASH" | "MARGIN">("CASH");
  const [fillModel, setFillModel] = useState<FillModelType>("TOUCHED_BID_ASK");
  const [slippagePolicy, setSlippagePolicy] = useState<SlippagePolicy>("NONE");
  const [slippageValue, setSlippageValue] = useState<number>(0.0);
  const [feeModel, setFeeModel] = useState<FeeModelType>("PER_SHARE");
  const [commissionRate, setCommissionRate] = useState<number>(0.005);
  const [latencyModel, setLatencyModel] = useState<LatencyModelType>("ZERO_LATENCY");
  const [latencyMs, setLatencyMs] = useState<number>(0);
  const [maxPositionSize, setMaxPositionSize] = useState<number>(500000);

  // Strategy Parameters
  const selectedStrategy =
    strategies.find((s) => s.strategy_id === selectedStrategyId) || strategies[0];
  const [strategyParams, setStrategyParams] = useState<Record<string, any>>(
    selectedStrategy?.default_parameters || { quantity: 100 },
  );
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const handleStrategyChange = (newStratId: string) => {
    setSelectedStrategyId(newStratId);
    const strat = strategies.find((s) => s.strategy_id === newStratId);
    if (strat) {
      setStrategyParams({ ...strat.default_parameters });
    }
  };

  const handleParamChange = (paramKey: string, val: any) => {
    const num = isNaN(Number(val)) ? val : Number(val);
    setStrategyParams((prev) => ({ ...prev, [paramKey]: num }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const config: AtlasBacktestConfig = {
      strategy_id: selectedStrategyId,
      strategy_parameters: strategyParams,
      dataset_id: selectedDatasetId,
      initial_cash: initialCash,
      account_type: accountType,
      fill_model: fillModel,
      slippage_policy: slippagePolicy,
      slippage_value: slippageValue,
      fee_model: feeModel,
      commission_rate: commissionRate,
      latency_model: latencyModel,
      latency_ms: latencyMs,
      max_position_size: maxPositionSize,
      include_replay_events: true,
    };

    const val = validateBacktestConfig(config);
    if (!val.isValid) {
      setValidationErrors(val.errors);
      return;
    }
    setValidationErrors([]);
    await onExecute(config);
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 text-neutral-200">
      <div className="flex items-center justify-between pb-4 border-b border-neutral-800 mb-5">
        <div className="flex items-center gap-2">
          <Settings className="w-5 h-5 text-amber-400" />
          <h2 className="text-lg font-semibold tracking-wide">Simulation Configuration</h2>
        </div>
        <span className="text-xs px-2.5 py-1 rounded bg-neutral-800 text-neutral-400 font-mono">
          NautilusTrader v1.231.0
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Strategy Selection */}
        <div>
          <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-2">
            Trading Strategy Template
          </label>
          <select
            value={selectedStrategyId}
            onChange={(e) => handleStrategyChange(e.target.value)}
            className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 text-sm text-neutral-100 focus:outline-none focus:border-amber-400"
          >
            {strategies.map((strat) => (
              <option key={strat.strategy_id} value={strat.strategy_id}>
                {strat.name} ({strat.category})
              </option>
            ))}
          </select>
          {selectedStrategy && (
            <p className="text-xs text-neutral-400 mt-1.5 leading-relaxed">
              {selectedStrategy.description}
            </p>
          )}
        </div>

        {/* Dynamic Strategy Parameters */}
        <div className="bg-neutral-950/60 p-3.5 rounded-lg border border-neutral-800">
          <div className="flex items-center gap-2 mb-3">
            <Sliders className="w-4 h-4 text-neutral-400" />
            <span className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">
              Strategy Parameters
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(strategyParams).map(([key, val]) => (
              <div key={key}>
                <label className="block text-xs text-neutral-400 mb-1 capitalize">
                  {key.replace(/_/g, " ")}
                </label>
                <input
                  type="number"
                  value={val}
                  step={key.includes("ratio") || key.includes("pct") ? "0.01" : "1"}
                  onChange={(e) => handleParamChange(key, e.target.value)}
                  className="w-full bg-neutral-900 border border-neutral-700 rounded px-2.5 py-1.5 text-xs text-neutral-100 focus:outline-none focus:border-amber-400"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Dataset Selection */}
        <div>
          <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-2">
            Historical Data Catalog
          </label>
          <select
            value={selectedDatasetId}
            onChange={(e) => setSelectedDatasetId(e.target.value)}
            className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 text-sm text-neutral-100 focus:outline-none focus:border-amber-400"
          >
            {datasets.map((ds) => (
              <option key={ds.dataset_id} value={ds.dataset_id}>
                {ds.symbol} — {ds.data_granularity.toUpperCase()} ({ds.start_date} to {ds.end_date})
              </option>
            ))}
          </select>
        </div>

        {/* Capital & Margin */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Initial Capital ($)
            </label>
            <input
              type="number"
              value={initialCash}
              step="5000"
              onChange={(e) => setInitialCash(Number(e.target.value))}
              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 text-sm text-neutral-100 focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Account Type
            </label>
            <select
              value={accountType}
              onChange={(e) => setAccountType(e.target.value as any)}
              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-3 py-2 text-sm text-neutral-100 focus:outline-none focus:border-amber-400"
            >
              <option value="CASH">CASH (100% Cash Covered)</option>
              <option value="MARGIN">MARGIN (Reg-T 2x Buying Power)</option>
            </select>
          </div>
        </div>

        {/* Execution Realism: Fill & Slippage */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Fill Model
            </label>
            <select
              value={fillModel}
              onChange={(e) => setFillModel(e.target.value as any)}
              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-2.5 py-1.5 text-xs text-neutral-100 focus:outline-none focus:border-amber-400"
            >
              <option value="TOUCHED_BID_ASK">TOUCHED (Fill on Touch)</option>
              <option value="CROSS_BID_ASK">CROSS (Fill on Through)</option>
              <option value="VOLUME_CONSTRAINED">VOLUME CONSTRAINED (10% Cap)</option>
              <option value="PROBABILISTIC">PROBABILISTIC (Queue Estimation)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Slippage Policy
            </label>
            <select
              value={slippagePolicy}
              onChange={(e) => setSlippagePolicy(e.target.value as any)}
              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-2.5 py-1.5 text-xs text-neutral-100 focus:outline-none focus:border-amber-400"
            >
              <option value="NONE">NONE (Zero Slippage)</option>
              <option value="FIXED_TICKS">FIXED TICKS ($0.01 / tick)</option>
              <option value="FIXED_BPS">FIXED BPS (Basis Points)</option>
              <option value="VOLUME_WEIGHTED">VOLUME WEIGHTED (Square Root)</option>
            </select>
          </div>
        </div>

        {/* Commissions & Latency */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Fee Model
            </label>
            <select
              value={feeModel}
              onChange={(e) => setFeeModel(e.target.value as any)}
              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-2.5 py-1.5 text-xs text-neutral-100 focus:outline-none focus:border-amber-400"
            >
              <option value="ZERO_FEE">ZERO FEE</option>
              <option value="PER_SHARE">PER SHARE ($0.005/share)</option>
              <option value="PER_CONTRACT">PER CONTRACT ($0.65/contract)</option>
              <option value="PERCENTAGE">PERCENTAGE (BPS Fee)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Latency Model
            </label>
            <select
              value={latencyModel}
              onChange={(e) => setLatencyModel(e.target.value as any)}
              className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-2.5 py-1.5 text-xs text-neutral-100 focus:outline-none focus:border-amber-400"
            >
              <option value="ZERO_LATENCY">ZERO LATENCY</option>
              <option value="FIXED_MS">FIXED MS (Simulated Delay)</option>
              <option value="JITTER_DISTRIBUTION">JITTER DISTRIBUTION</option>
            </select>
          </div>
        </div>

        {/* Validation Errors */}
        {validationErrors.length > 0 && (
          <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-lg space-y-1">
            <div className="flex items-center gap-1.5 text-rose-400 font-medium text-xs">
              <AlertTriangle className="w-4 h-4" />
              <span>Configuration Invalid:</span>
            </div>
            {validationErrors.map((err, i) => (
              <p key={i} className="text-xs text-rose-300 pl-5">
                • {err}
              </p>
            ))}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isRunning}
          className={`w-full py-2.5 px-4 rounded-lg font-medium text-sm flex items-center justify-center gap-2 transition-colors ${
            isRunning
              ? "bg-neutral-800 text-neutral-500 cursor-not-allowed"
              : "bg-amber-500 hover:bg-amber-400 text-neutral-950 shadow-md shadow-amber-500/10"
          }`}
        >
          {isRunning ? (
            <>
              <div className="w-4 h-4 border-2 border-neutral-950 border-t-transparent rounded-full animate-spin" />
              <span>Simulating Event Replay...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute NautilusTrader Backtest</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}

