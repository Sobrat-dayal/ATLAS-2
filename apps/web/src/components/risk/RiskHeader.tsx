"use client";

import React from "react";
import { AccountDTO, PortfolioDTO } from "@/lib/portfolios/types";
import {
  AnnualizationPolicy,
  RiskModelDefinitionDTO,
  RiskReturnFrequency,
} from "@/lib/risk/types";
import {
  Activity,
  Calendar,
  Layers,
  Play,
  RefreshCw,
  Sliders,
} from "lucide-react";

interface RiskHeaderProps {
  portfolios: PortfolioDTO[];
  selectedPortfolioId: string;
  onSelectPortfolio: (id: string) => void;
  accounts: AccountDTO[];
  selectedAccountId: string;
  onSelectAccount: (id: string) => void;
  selectedBenchmark: string;
  onSelectBenchmark: (b: string) => void;
  selectedModelId: string;
  onSelectModel: (m: string) => void;
  modelsCatalog: RiskModelDefinitionDTO[];
  selectedFrequency: RiskReturnFrequency;
  onSelectFrequency: (f: RiskReturnFrequency) => void;
  rollingWindowSize: number;
  onSelectRollingWindow: (w: number) => void;
  onCalculate: () => void;
  onRefresh: () => void;
  calculating: boolean;
  loading: boolean;
}

export function RiskHeader({
  portfolios,
  selectedPortfolioId,
  onSelectPortfolio,
  accounts,
  selectedAccountId,
  onSelectAccount,
  selectedBenchmark,
  onSelectBenchmark,
  selectedModelId,
  onSelectModel,
  modelsCatalog,
  selectedFrequency,
  onSelectFrequency,
  rollingWindowSize,
  onSelectRollingWindow,
  onCalculate,
  onRefresh,
  calculating,
  loading,
}: RiskHeaderProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default/60 bg-atlas-surface-1 px-4 py-3">
      {/* Left side selectors */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Portfolio Selector */}
        <div className="flex items-center gap-1.5">
          <Layers className="h-4 w-4 text-atlas-text-secondary" />
          <select
            value={selectedPortfolioId}
            onChange={(e) => onSelectPortfolio(e.target.value)}
            className="rounded border border-atlas-border-default bg-atlas-surface-2 px-2.5 py-1 text-xs font-medium text-atlas-text-primary focus:border-atlas-accent-blue focus:outline-none"
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.base_currency})
              </option>
            ))}
          </select>
        </div>

        {/* Account Selector */}
        {accounts.length > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-atlas-text-muted">Account:</span>
            <select
              value={selectedAccountId}
              onChange={(e) => onSelectAccount(e.target.value)}
              className="rounded border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent-blue focus:outline-none"
            >
              <option value="ALL">Consolidated (All Accounts)</option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.account_name} ({a.primary_currency})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Benchmark Selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs text-atlas-text-muted">Benchmark:</span>
          <select
            value={selectedBenchmark}
            onChange={(e) => onSelectBenchmark(e.target.value)}
            className="rounded border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent-blue focus:outline-none"
          >
            <option value="BENCHMARK_SPY">S&P 500 (SPY)</option>
            <option value="BENCHMARK_ACWI">MSCI ACWI (ACWI)</option>
            <option value="BENCHMARK_AGG">US Aggregate Bond (AGG)</option>
          </select>
        </div>

        {/* Model Selector */}
        <div className="flex items-center gap-1.5">
          <Sliders className="h-3.5 w-3.5 text-atlas-text-secondary" />
          <select
            value={selectedModelId}
            onChange={(e) => onSelectModel(e.target.value)}
            className="rounded border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent-blue focus:outline-none"
          >
            {modelsCatalog.length > 0 ? (
              modelsCatalog.map((m) => (
                <option key={m.model_id} value={m.model_id}>
                  {m.display_name} (v{m.version})
                </option>
              ))
            ) : (
              <>
                <option value="COVARIANCE_BASED_PORTFOLIO_RISK">
                  Covariance Parametric (Euler Risk)
                </option>
                <option value="HISTORICAL_SAMPLE_RISK">
                  Historical Sample Volatility (K=252)
                </option>
                <option value="ROLLING_VOLATILITY_RISK">
                  Rolling Volatility Series
                </option>
                <option value="CASH_FLOW_ADJUSTED_DRAWDOWN">
                  Cash-Flow-Neutral Drawdowns
                </option>
              </>
            )}
          </select>
        </div>

        {/* Frequency & Rolling Window */}
        <div className="flex items-center gap-2 border-l border-atlas-border-default/50 pl-3">
          <div className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5 text-atlas-text-muted" />
            <select
              value={selectedFrequency}
              onChange={(e) => onSelectFrequency(e.target.value as RiskReturnFrequency)}
              className="rounded border border-atlas-border-default bg-atlas-surface-2 px-1.5 py-1 text-xs text-atlas-text-primary focus:outline-none"
            >
              <option value="DAILY">Daily (252x)</option>
              <option value="WEEKLY">Weekly (52x)</option>
              <option value="MONTHLY">Monthly (12x)</option>
            </select>
          </div>

          <div className="flex items-center gap-1 text-xs text-atlas-text-muted">
            <span>Window:</span>
            <select
              value={rollingWindowSize}
              onChange={(e) => onSelectRollingWindow(Number(e.target.value))}
              className="rounded border border-atlas-border-default bg-atlas-surface-2 px-1.5 py-1 text-xs text-atlas-text-primary focus:outline-none"
            >
              <option value={20}>20 Days (1M)</option>
              <option value={60}>60 Days (3M)</option>
              <option value={120}>120 Days (6M)</option>
              <option value={252}>252 Days (1Y)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Right side actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={onRefresh}
          disabled={loading || calculating}
          className="flex items-center gap-1.5 rounded border border-atlas-border-default bg-atlas-surface-2 px-2.5 py-1.5 text-xs font-medium text-atlas-text-secondary transition hover:bg-atlas-surface-3 hover:text-atlas-text-primary disabled:opacity-50"
          title="Refresh risk analytics"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>

        <button
          onClick={onCalculate}
          disabled={calculating || !selectedPortfolioId}
          className="flex items-center gap-1.5 rounded bg-atlas-accent-blue px-3 py-1.5 text-xs font-medium text-white shadow-sm transition hover:bg-atlas-accent-blue/90 disabled:opacity-50"
        >
          <Play className={`h-3.5 w-3.5 ${calculating ? "animate-spin" : ""}`} />
          <span>{calculating ? "Calculating Risk..." : "Run Risk Model"}</span>
        </button>
      </div>
    </div>
  );
}
