"use client";

import React from "react";
import { PerformanceMetrics } from "@/lib/trading/backtesting/types";
import {
  formatCurrency,
  formatPercent,
  formatRatio,
  formatNumber,
} from "@/lib/trading/backtesting/formatters";
import {
  TrendingUp,
  TrendingDown,
  ShieldAlert,
  Percent,
  Activity,
  Award,
  Zap,
  Clock,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";

interface BacktestPerformanceDashboardProps {
  performance: PerformanceMetrics;
  initialCash: number;
  durationSec: number;
}

export function BacktestPerformanceDashboard({
  performance,
  initialCash,
  durationSec,
}: BacktestPerformanceDashboardProps) {
  const isPositive = performance.total_return_dollar >= 0;

  return (
    <div className="space-y-4">
      {/* Top Level Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Total Return */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Total Net Return</span>
            {isPositive ? (
              <ArrowUpRight className="w-4 h-4 text-emerald-400" />
            ) : (
              <ArrowDownRight className="w-4 h-4 text-rose-400" />
            )}
          </div>
          <div
            className={`text-2xl font-bold tracking-tight ${
              isPositive ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {formatCurrency(performance.total_return_dollar)}
          </div>
          <div className="text-xs text-neutral-400 mt-1 flex items-center gap-1.5">
            <span
              className={`font-semibold ${
                isPositive ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {formatPercent(performance.total_return_pct)}
            </span>
            <span>on ${initialCash.toLocaleString()} initial</span>
          </div>
        </div>

        {/* Max Drawdown */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Max Drawdown</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold tracking-tight text-neutral-100">
            -{formatPercent(performance.drawdown.max_drawdown_pct).replace("+", "").replace("-", "")}
          </div>
          <div className="text-xs text-neutral-400 mt-1 flex items-center justify-between">
            <span>Depth: -${performance.drawdown.max_drawdown_dollar.toLocaleString()}</span>
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded ${
                performance.drawdown.is_recovered
                  ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                  : "bg-amber-950 text-amber-400 border border-amber-800"
              }`}
            >
              {performance.drawdown.is_recovered ? "Recovered" : "Underwater"}
            </span>
          </div>
        </div>

        {/* Sharpe & Sortino */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Sharpe Ratio</span>
            <Award className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold tracking-tight text-neutral-100">
            {formatRatio(performance.sharpe_ratio)}
          </div>
          <div className="text-xs text-neutral-400 mt-1 flex items-center justify-between">
            <span>Sortino: {formatRatio(performance.sortino_ratio)}</span>
            <span>Calmar: {formatRatio(performance.calmar_ratio)}</span>
          </div>
        </div>

        {/* Win Rate & Expectancy */}
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-neutral-400 text-xs font-medium uppercase tracking-wider mb-2">
            <span>Win Rate</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold tracking-tight text-neutral-100">
            {formatPercent(performance.win_rate_pct)}
          </div>
          <div className="text-xs text-neutral-400 mt-1 flex items-center justify-between">
            <span>
              {performance.winning_trades_count}W / {performance.losing_trades_count}L (
              {performance.total_trades_count} total)
            </span>
            <span>PF: {formatRatio(performance.profit_factor)}</span>
          </div>
        </div>
      </div>

      {/* Institutional Attribution Grid */}
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4">
        <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-3">
          Institutional Risk & Execution Attribution
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
          <div className="bg-neutral-950/70 p-2.5 rounded-lg border border-neutral-800/80">
            <span className="text-neutral-500 block">CAGR (Annualized)</span>
            <span className="font-semibold text-neutral-200 mt-0.5 block">
              {formatPercent(performance.cagr_pct)}
            </span>
          </div>

          <div className="bg-neutral-950/70 p-2.5 rounded-lg border border-neutral-800/80">
            <span className="text-neutral-500 block">Annualized Volatility</span>
            <span className="font-semibold text-neutral-200 mt-0.5 block">
              {formatPercent(performance.annualized_volatility_pct)}
            </span>
          </div>

          <div className="bg-neutral-950/70 p-2.5 rounded-lg border border-neutral-800/80">
            <span className="text-neutral-500 block">Expectancy per Trade</span>
            <span className="font-semibold text-neutral-200 mt-0.5 block">
              {formatCurrency(performance.expectancy_dollar)}
            </span>
          </div>

          <div className="bg-neutral-950/70 p-2.5 rounded-lg border border-neutral-800/80">
            <span className="text-neutral-500 block">Total Commissions</span>
            <span className="font-semibold text-neutral-200 mt-0.5 block">
              {formatCurrency(performance.total_commissions_paid)}
            </span>
          </div>

          <div className="bg-neutral-950/70 p-2.5 rounded-lg border border-neutral-800/80">
            <span className="text-neutral-500 block">Slippage Friction</span>
            <span className="font-semibold text-neutral-200 mt-0.5 block">
              {formatCurrency(performance.total_slippage_cost)}
            </span>
          </div>

          <div className="bg-neutral-950/70 p-2.5 rounded-lg border border-neutral-800/80">
            <span className="text-neutral-500 block">Simulation Duration</span>
            <span className="font-semibold text-neutral-200 mt-0.5 block">
              {durationSec.toFixed(2)}s
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

