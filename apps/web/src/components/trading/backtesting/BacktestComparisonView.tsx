"use client";

import React from "react";
import { AtlasBacktestResult } from "@/lib/trading/backtesting/types";
import {
  formatCurrency,
  formatPercent,
  formatRatio,
  formatNumber,
} from "@/lib/trading/backtesting/formatters";
import { GitCompare, Award, ArrowUpRight, ShieldAlert, Activity } from "lucide-react";

interface BacktestComparisonViewProps {
  runs: AtlasBacktestResult[];
}

export function BacktestComparisonView({ runs }: BacktestComparisonViewProps) {
  if (runs.length === 0) {
    return (
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 text-center text-neutral-400">
        <GitCompare className="w-8 h-8 mx-auto text-neutral-600 mb-2" />
        <p className="text-sm">No historical backtest runs saved for comparison yet.</p>
        <p className="text-xs text-neutral-500 mt-1">
          Execute multiple backtest simulations to review side-by-side performance attribution.
        </p>
      </div>
    );
  }

  const metricRows = [
    { label: "Strategy ID", render: (r: AtlasBacktestResult) => r.config.strategy_id },
    { label: "Historical Dataset", render: (r: AtlasBacktestResult) => r.config.dataset_id },
    {
      label: "Total Net Return",
      render: (r: AtlasBacktestResult) => (
        <span
          className={
            r.performance.total_return_dollar >= 0 ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"
          }
        >
          {formatCurrency(r.performance.total_return_dollar)} (
          {formatPercent(r.performance.total_return_pct)})
        </span>
      ),
    },
    {
      label: "CAGR (Annualized)",
      render: (r: AtlasBacktestResult) => formatPercent(r.performance.cagr_pct),
    },
    {
      label: "Sharpe Ratio",
      render: (r: AtlasBacktestResult) => (
        <span className="text-amber-400 font-bold">{formatRatio(r.performance.sharpe_ratio)}</span>
      ),
    },
    {
      label: "Sortino Ratio",
      render: (r: AtlasBacktestResult) => formatRatio(r.performance.sortino_ratio),
    },
    {
      label: "Calmar Ratio",
      render: (r: AtlasBacktestResult) => formatRatio(r.performance.calmar_ratio),
    },
    {
      label: "Max Drawdown",
      render: (r: AtlasBacktestResult) => (
        <span className="text-rose-400 font-bold">
          -{formatPercent(r.performance.drawdown.max_drawdown_pct).replace("+", "").replace("-", "")}
        </span>
      ),
    },
    {
      label: "Profit Factor",
      render: (r: AtlasBacktestResult) => formatRatio(r.performance.profit_factor),
    },
    {
      label: "Win Rate",
      render: (r: AtlasBacktestResult) => formatPercent(r.performance.win_rate_pct),
    },
    {
      label: "Expectancy per Trade",
      render: (r: AtlasBacktestResult) => formatCurrency(r.performance.expectancy_dollar),
    },
    {
      label: "Total Trades Count",
      render: (r: AtlasBacktestResult) => `${r.performance.total_trades_count} trades`,
    },
    {
      label: "Commissions Paid",
      render: (r: AtlasBacktestResult) => formatCurrency(r.performance.total_commissions_paid),
    },
    {
      label: "Slippage Friction",
      render: (r: AtlasBacktestResult) => formatCurrency(r.performance.total_slippage_cost),
    },
    {
      label: "Fill Model",
      render: (r: AtlasBacktestResult) => r.config.fill_model || "TOUCHED",
    },
    {
      label: "Execution Duration",
      render: (r: AtlasBacktestResult) => `${r.execution_duration_sec.toFixed(2)}s`,
    },
  ];

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 text-neutral-200 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-neutral-100 flex items-center gap-2">
            <GitCompare className="w-4 h-4 text-amber-400" />
            Cross-Run Performance & Risk Comparison
          </h3>
          <p className="text-xs text-neutral-400 mt-0.5">
            Side-by-side quantitative benchmarking across distinct strategies, datasets, and fill policies
          </p>
        </div>
        <span className="text-xs font-mono text-neutral-400">
          Comparing {runs.length} Active Run{runs.length > 1 ? "s" : ""}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-neutral-800 text-neutral-400 text-[10px] uppercase tracking-wider">
              <th className="pb-3 font-medium w-48">Metric / Dimension</th>
              {runs.map((r) => (
                <th key={r.run_id} className="pb-3 font-medium font-mono text-neutral-200">
                  {r.config.name || r.run_id.slice(0, 14)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-800/60 font-mono text-[11px]">
            {metricRows.map((row, idx) => (
              <tr key={idx} className="hover:bg-neutral-800/30">
                <td className="py-2.5 font-sans font-medium text-neutral-400">{row.label}</td>
                {runs.map((r) => (
                  <td key={r.run_id} className="py-2.5 text-neutral-200">
                    {row.render(r)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

