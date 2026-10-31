"use client";

import React, { useState, useEffect } from "react";
import {
  AtlasBacktestConfig,
  AtlasBacktestResult,
  AtlasStrategyDefinition,
  HistoricalDatasetManifest,
  STAGE_143_DISCLAIMERS,
} from "@/lib/trading/backtesting/types";
import {
  executeBacktestRun,
  listBacktestDatasets,
  listBacktestStrategies,
} from "@/lib/trading/backtesting/api";
import { BacktestConfiguration } from "./BacktestConfiguration";
import { BacktestPerformanceDashboard } from "./BacktestPerformanceDashboard";
import { BacktestEquityChart } from "./BacktestEquityChart";
import { BacktestTradesTable } from "./BacktestTradesTable";
import { BacktestOrdersTable } from "./BacktestOrdersTable";
import { BacktestReplay } from "./BacktestReplay";
import { BacktestExperimentBuilder } from "./BacktestExperimentBuilder";
import { BacktestComparisonView } from "./BacktestComparisonView";
import {
  Play,
  LineChart,
  ListOrdered,
  FileText,
  Clock,
  Cpu,
  GitCompare,
  ShieldAlert,
  AlertCircle,
  Database,
  Terminal,
} from "lucide-react";

export function BacktestingLab() {
  const [strategies, setStrategies] = useState<AtlasStrategyDefinition[]>([]);
  const [datasets, setDatasets] = useState<HistoricalDatasetManifest[]>([]);
  const [activeTab, setActiveTab] = useState<
    "OVERVIEW" | "EQUITY" | "TRADES" | "ORDERS" | "REPLAY" | "SWEEP" | "COMPARE"
  >("OVERVIEW");
  const [isRunning, setIsRunning] = useState(false);
  const [currentResult, setCurrentResult] = useState<AtlasBacktestResult | null>(null);
  const [historyRuns, setHistoryRuns] = useState<AtlasBacktestResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [strats, dsets] = await Promise.all([
          listBacktestStrategies(),
          listBacktestDatasets(),
        ]);
        setStrategies(strats);
        setDatasets(dsets);
      } catch (err: any) {
        console.error("Failed to load backtesting metadata:", err);
      }
    }
    loadData();
  }, []);

  const handleExecute = async (config: AtlasBacktestConfig) => {
    setIsRunning(true);
    setError(null);
    try {
      const res = await executeBacktestRun(config);
      setCurrentResult(res);
      setHistoryRuns((prev) => [res, ...prev.slice(0, 9)]);
    } catch (err: any) {
      setError(err.message || "Failed to execute backtest.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 space-y-6">
      {/* Top Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between pb-4 border-b border-neutral-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h1 className="text-xl font-bold tracking-tight">
              ATLAS Quantitative Backtesting Lab
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">
              Stage 143 · NautilusTrader Core
            </span>
          </div>
          <p className="text-xs text-neutral-400 mt-1">
            Institutional event-driven market simulation, fill modeling, slippage, and walk-forward research
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-neutral-400 bg-neutral-900 border border-neutral-800 px-3 py-1.5 rounded-lg font-mono">
            <Database className="w-3.5 h-3.5 text-neutral-500" />
            <span>{datasets.length} Datasets</span>
            <span className="text-neutral-600">|</span>
            <span>{strategies.length} Strategies</span>
          </div>
        </div>
      </div>

      {/* Stage 143 Regulatory & Research Disclaimer Banner */}
      <div className="p-3.5 bg-neutral-900/80 border border-neutral-800 rounded-xl flex items-start gap-3 text-xs text-neutral-400">
        <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <span className="font-semibold text-neutral-200">
            Institutional Research & Governance Protocol (Stage 143):
          </span>
          <p className="text-[11px] leading-relaxed">
            Hypothetical backtesting results have inherent limitations and do not represent actual trading.
            Point-in-time correctness enforces zero look-ahead bias and genuine historical quotes.
            Automated live execution, sandbox routing, and broker connections are strictly prohibited in Stage 143.
          </p>
        </div>
      </div>

      {/* Main Grid: Left Config, Right Visualizer Cockpit */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Configuration Form (4 cols) */}
        <div className="lg:col-span-4">
          <BacktestConfiguration
            strategies={strategies}
            datasets={datasets}
            isRunning={isRunning}
            onExecute={handleExecute}
          />
        </div>

        {/* Right Column: Visualization & Analysis Cockpit (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          {error && (
            <div className="p-3.5 bg-rose-950/40 border border-rose-800 rounded-xl text-xs text-rose-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}

          {/* Tab Navigation */}
          <div className="flex flex-wrap items-center gap-1.5 bg-neutral-900 border border-neutral-800 p-1 rounded-xl text-xs">
            <button
              onClick={() => setActiveTab("OVERVIEW")}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-colors ${
                activeTab === "OVERVIEW"
                  ? "bg-neutral-800 text-neutral-100 shadow-sm"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <Terminal className="w-3.5 h-3.5" /> Executive KPI
            </button>
            <button
              onClick={() => setActiveTab("EQUITY")}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-colors ${
                activeTab === "EQUITY"
                  ? "bg-neutral-800 text-neutral-100 shadow-sm"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <LineChart className="w-3.5 h-3.5" /> Equity & Drawdown
            </button>
            <button
              onClick={() => setActiveTab("TRADES")}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-colors ${
                activeTab === "TRADES"
                  ? "bg-neutral-800 text-neutral-100 shadow-sm"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <ListOrdered className="w-3.5 h-3.5" /> Trade Blotter (
              {currentResult?.trades.length || 0})
            </button>
            <button
              onClick={() => setActiveTab("ORDERS")}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-colors ${
                activeTab === "ORDERS"
                  ? "bg-neutral-800 text-neutral-100 shadow-sm"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <FileText className="w-3.5 h-3.5" /> Order Lifecycle
            </button>
            <button
              onClick={() => setActiveTab("REPLAY")}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-colors ${
                activeTab === "REPLAY"
                  ? "bg-neutral-800 text-neutral-100 shadow-sm"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <Clock className="w-3.5 h-3.5" /> Event Replay
            </button>
            <button
              onClick={() => setActiveTab("SWEEP")}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-colors ${
                activeTab === "SWEEP"
                  ? "bg-neutral-800 text-neutral-100 shadow-sm"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <Cpu className="w-3.5 h-3.5" /> Parameter Sweep
            </button>
            <button
              onClick={() => setActiveTab("COMPARE")}
              className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium transition-colors ${
                activeTab === "COMPARE"
                  ? "bg-neutral-800 text-neutral-100 shadow-sm"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              <GitCompare className="w-3.5 h-3.5" /> Compare ({historyRuns.length})
            </button>
          </div>

          {/* Active Tab Content */}
          {currentResult ? (
            <div className="space-y-4">
              {activeTab === "OVERVIEW" && (
                <>
                  <BacktestPerformanceDashboard
                    performance={currentResult.performance}
                    initialCash={currentResult.config.initial_cash || 100000}
                    durationSec={currentResult.execution_duration_sec}
                  />
                  <BacktestEquityChart
                    equityCurve={currentResult.equity_curve}
                    initialCash={currentResult.config.initial_cash || 100000}
                  />
                </>
              )}

              {activeTab === "EQUITY" && (
                <BacktestEquityChart
                  equityCurve={currentResult.equity_curve}
                  initialCash={currentResult.config.initial_cash || 100000}
                />
              )}

              {activeTab === "TRADES" && (
                <BacktestTradesTable trades={currentResult.trades} />
              )}

              {activeTab === "ORDERS" && (
                <BacktestOrdersTable orders={currentResult.orders} />
              )}

              {activeTab === "REPLAY" && (
                <BacktestReplay replayEvents={currentResult.replay_events} />
              )}

              {activeTab === "SWEEP" && (
                <BacktestExperimentBuilder baseConfig={currentResult.config} />
              )}

              {activeTab === "COMPARE" && (
                <BacktestComparisonView runs={historyRuns} />
              )}
            </div>
          ) : (
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-16 text-center text-neutral-400 space-y-3">
              <Terminal className="w-10 h-10 mx-auto text-amber-400/80 mb-2" />
              <h3 className="text-base font-semibold text-neutral-200">
                Ready for Historical Backtest Execution
              </h3>
              <p className="text-xs text-neutral-400 max-w-md mx-auto leading-relaxed">
                Select a strategy template, historical dataset, and simulation constraints on the left,
                then click Execute to run the NautilusTrader event-driven backtesting engine.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

