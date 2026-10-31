"use client";

import React, { useState } from "react";
import {
  AtlasBacktestConfig,
  ParameterExperimentConfig,
  ParameterExperimentResult,
} from "@/lib/trading/backtesting/types";
import { runParameterExperiment } from "@/lib/trading/backtesting/api";
import { formatCurrency, formatPercent, formatRatio } from "@/lib/trading/backtesting/formatters";
import { Sliders, Cpu, AlertTriangle, CheckCircle2, TrendingUp, Layers } from "lucide-react";

interface BacktestExperimentBuilderProps {
  baseConfig: AtlasBacktestConfig;
}

export function BacktestExperimentBuilder({ baseConfig }: BacktestExperimentBuilderProps) {
  const [fastMaRange, setFastMaRange] = useState("5, 10, 15, 20");
  const [slowMaRange, setSlowMaRange] = useState("30, 50, 100");
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<ParameterExperimentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunExperiment = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const fastList = fastMaRange
        .split(",")
        .map((s) => Number(s.trim()))
        .filter((n) => !isNaN(n));
      const slowList = slowMaRange
        .split(",")
        .map((s) => Number(s.trim()))
        .filter((n) => !isNaN(n));

      const expConfig: ParameterExperimentConfig = {
        base_config: baseConfig,
        parameter_grid: {
          fast_period: fastList,
          slow_period: slowList,
        },
        metric_target: "sharpe_ratio",
      };

      const res = await runParameterExperiment(expConfig);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Parameter experiment execution failed.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 text-neutral-200 space-y-5">
      <div className="flex items-center justify-between pb-4 border-b border-neutral-800">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-neutral-100 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-amber-400" />
            Parameter Sweep & Optimization Grid
          </h3>
          <p className="text-xs text-neutral-400 mt-0.5">
            Systematic parameter exploration with automated multi-run evaluation and overfitting alerts
          </p>
        </div>
      </div>

      {/* Grid Settings Inputs */}
      <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Fast Period Values (comma separated)
            </label>
            <input
              type="text"
              value={fastMaRange}
              onChange={(e) => setFastMaRange(e.target.value)}
              className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2 text-xs font-mono text-neutral-100 focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-neutral-400 mb-1">
              Slow Period Values (comma separated)
            </label>
            <input
              type="text"
              value={slowMaRange}
              onChange={(e) => setSlowMaRange(e.target.value)}
              className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2 text-xs font-mono text-neutral-100 focus:outline-none focus:border-amber-400"
            />
          </div>
        </div>

        {error && (
          <div className="p-3 bg-rose-950/40 border border-rose-800 text-xs text-rose-300 rounded-lg">
            {error}
          </div>
        )}

        <button
          onClick={handleRunExperiment}
          disabled={isRunning}
          className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-neutral-950 font-semibold text-xs flex items-center gap-2 disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-neutral-950 border-t-transparent rounded-full animate-spin" />
              <span>Evaluating Grid Combinations...</span>
            </>
          ) : (
            <>
              <Sliders className="w-3.5 h-3.5" />
              <span>Execute Parameter Sweep</span>
            </>
          )}
        </button>
      </div>

      {/* Results View */}
      {result && (
        <div className="space-y-4">
          {/* Summary stats */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-neutral-950 p-3 rounded-lg border border-neutral-800">
              <span className="text-neutral-500 text-xs block">Evaluated Runs</span>
              <span className="text-lg font-bold text-neutral-200 mt-0.5 block font-mono">
                {result.evaluated_combinations} / {result.total_combinations}
              </span>
            </div>
            <div className="bg-neutral-950 p-3 rounded-lg border border-neutral-800">
              <span className="text-neutral-500 text-xs block">Target Metric</span>
              <span className="text-lg font-bold text-amber-400 mt-0.5 block font-mono">
                Sharpe Ratio
              </span>
            </div>
            <div className="bg-neutral-950 p-3 rounded-lg border border-neutral-800">
              <span className="text-neutral-500 text-xs block">Overfitting Alerts</span>
              <span
                className={`text-lg font-bold mt-0.5 block font-mono ${
                  result.overfitting_flag_count > 0 ? "text-amber-400" : "text-emerald-400"
                }`}
              >
                {result.overfitting_flag_count} flagged
              </span>
            </div>
          </div>

          {/* Ranked table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-neutral-800 text-neutral-400 uppercase tracking-wider text-[10px]">
                  <th className="pb-2.5 font-medium">Rank</th>
                  <th className="pb-2.5 font-medium">Parameters</th>
                  <th className="pb-2.5 font-medium text-right">Total Return</th>
                  <th className="pb-2.5 font-medium text-right">Sharpe</th>
                  <th className="pb-2.5 font-medium text-right">Max Drawdown</th>
                  <th className="pb-2.5 font-medium text-right">Win Rate</th>
                  <th className="pb-2.5 font-medium">Validation Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800/60 font-mono text-[11px]">
                {result.ranked_runs.map((item, idx) => (
                  <tr key={idx} className="hover:bg-neutral-800/30">
                    <td className="py-2.5 text-neutral-400 font-sans">#{idx + 1}</td>
                    <td className="py-2.5 text-neutral-200">
                      {Object.entries(item.parameters)
                        .map(([k, v]) => `${k}=${v}`)
                        .join(", ")}
                    </td>
                    <td className="py-2.5 text-right font-semibold text-emerald-400">
                      {formatPercent(item.metrics.total_return_pct)}
                    </td>
                    <td className="py-2.5 text-right font-bold text-amber-400">
                      {formatRatio(item.metrics.sharpe_ratio)}
                    </td>
                    <td className="py-2.5 text-right text-rose-400">
                      -{formatPercent(item.metrics.max_drawdown_pct).replace("+", "").replace("-", "")}
                    </td>
                    <td className="py-2.5 text-right text-neutral-300">
                      {formatPercent(item.metrics.win_rate_pct)}
                    </td>
                    <td className="py-2.5 font-sans">
                      {item.overfitting_warning ? (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-950 text-amber-400 border border-amber-800/60 flex items-center gap-1 w-fit">
                          <AlertTriangle className="w-3 h-3" /> Overfitting Risk
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800/60 flex items-center gap-1 w-fit">
                          <CheckCircle2 className="w-3 h-3" /> Validated
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

