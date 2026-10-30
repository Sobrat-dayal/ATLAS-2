"use client";

import React, { useState } from "react";
import { Button } from "@/design-system";
import { usePortfolioPerformance } from "@/hooks/portfolios/usePortfolioPerformance";
import { BenchmarkComparisonView } from "./BenchmarkComparisonView";
import { CashFlowSummaryTable } from "./CashFlowSummaryTable";
import { PerformanceDataQualityPanel } from "./PerformanceDataQualityPanel";
import { PerformanceMethodologyInspector } from "./PerformanceMethodologyInspector";
import { PerformanceRunHistory } from "./PerformanceRunHistory";
import { PerformanceSummaryCards } from "./PerformanceSummaryCards";
import { PeriodicReturnsTable } from "./PeriodicReturnsTable";
import { PortfolioValueChart } from "./PortfolioValueChart";
import { TimeWeightedGrowthChart } from "./TimeWeightedGrowthChart";
import { AccountDTO, PortfolioDTO } from "@/lib/portfolios/types";
import {
  PerformanceMethodology,
  PerformancePeriodType,
} from "@/lib/portfolios/performance/types";
import {
  BarChart3,
  Calendar,
  DollarSign,
  FileText,
  Filter,
  History,
  Info,
  RefreshCw,
  Scale,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

interface PortfolioPerformanceWorkspaceProps {
  portfolio: PortfolioDTO;
  accounts: AccountDTO[];
  initialAccountId?: string;
}

type PerformanceTab =
  | "growth"
  | "equity_value"
  | "periodic"
  | "cash_flows"
  | "benchmark"
  | "quality"
  | "runs";

const PERIOD_OPTIONS: { id: PerformancePeriodType; label: string }[] = [
  { id: "1D", label: "1D" },
  { id: "WTD", label: "WTD" },
  { id: "MTD", label: "MTD" },
  { id: "QTD", label: "QTD" },
  { id: "YTD", label: "YTD" },
  { id: "1M", label: "1M" },
  { id: "3M", label: "3M" },
  { id: "1Y", label: "1Y" },
  { id: "3Y", label: "3Y" },
  { id: "5Y", label: "5Y" },
  { id: "INCEPTION", label: "Inception" },
  { id: "CUSTOM", label: "Custom" },
];

export function PortfolioPerformanceWorkspace({
  portfolio,
  accounts,
  initialAccountId = "ALL",
}: PortfolioPerformanceWorkspaceProps) {
  const {
    selectedPeriod,
    setSelectedPeriod,
    selectedMethodology,
    setSelectedMethodology,
    selectedBenchmarkId,
    setSelectedBenchmarkId,
    selectedAccountId,
    setSelectedAccountId,
    customStartDate,
    setCustomStartDate,
    customEndDate,
    setCustomEndDate,
    summary,
    series,
    periodicReturns,
    cashFlows,
    benchmarks,
    runHistory,
    loading,
    calculating,
    error,
    refresh,
    triggerRecalculation,
  } = usePortfolioPerformance(portfolio.id, initialAccountId);

  const [activeTab, setActiveTab] = useState<PerformanceTab>("growth");
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  return (
    <div className="space-y-4">
      {/* Control Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-sm border border-atlas-border-default/80 bg-atlas-surface-1 p-3 shadow-xs">
        {/* Left: Period Pills */}
        <div className="flex flex-wrap items-center gap-1">
          <Calendar className="mr-1.5 h-3.5 w-3.5 text-atlas-text-tertiary" />
          {PERIOD_OPTIONS.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedPeriod(p.id)}
              className={`rounded-xs px-2.5 py-1 text-xs font-mono font-medium transition-colors ${
                selectedPeriod === p.id
                  ? "bg-atlas-accent text-white font-semibold shadow-xs"
                  : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Right: Actions, Methodology & Accounts */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Account Filter */}
          <select
            value={selectedAccountId}
            onChange={(e) => setSelectedAccountId(e.target.value)}
            className="rounded-sm border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
          >
            <option value="ALL">All Accounts (Portfolio Scope)</option>
            {accounts.map((acc) => (
              <option key={acc.id} value={acc.id}>
                {acc.account_name} ({acc.primary_currency})
              </option>
            ))}
          </select>

          {/* Methodology Selector */}
          <select
            value={selectedMethodology}
            onChange={(e) => setSelectedMethodology(e.target.value as PerformanceMethodology)}
            className="rounded-sm border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
          >
            <option value="EXACT_TWR">Exact Subperiod TWR</option>
            <option value="MODIFIED_DIETZ">Modified Dietz (Approx)</option>
          </select>

          {/* Methodology Inspector Button */}
          {summary && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsInspectorOpen(true)}
              className="h-7 text-xs gap-1"
              title="Inspect exact formula and calculation provenance"
            >
              <Info className="h-3.5 w-3.5 text-atlas-accent" />
              Formula Audit
            </Button>
          )}

          {/* Recalculate Run Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={triggerRecalculation}
            disabled={calculating}
            className="h-7 text-xs gap-1 text-atlas-text-secondary hover:text-atlas-text-primary"
            title="Recalculate performance"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${calculating ? "animate-spin text-atlas-accent" : ""}`} />
            {calculating ? "Calculating..." : "Recalculate"}
          </Button>
        </div>
      </div>

      {/* Custom Date Range Bar if CUSTOM is selected */}
      {selectedPeriod === "CUSTOM" && (
        <div className="flex items-center gap-3 rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/40 px-3 py-2 text-xs">
          <span className="text-atlas-text-secondary font-medium">Custom Date Bounds:</span>
          <div className="flex items-center gap-2 font-mono">
            <input
              type="date"
              value={customStartDate}
              onChange={(e) => setCustomStartDate(e.target.value)}
              className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2 py-1 text-xs text-atlas-text-primary"
            />
            <span className="text-atlas-text-tertiary">&rarr;</span>
            <input
              type="date"
              value={customEndDate}
              onChange={(e) => setCustomEndDate(e.target.value)}
              className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2 py-1 text-xs text-atlas-text-primary"
            />
          </div>
          <Button variant="secondary" size="sm" onClick={refresh} className="h-7 text-xs">
            Apply Bounds
          </Button>
        </div>
      )}

      {/* Error Callout if any */}
      {error && (
        <div className="rounded-sm border border-rose-500/40 bg-rose-500/10 p-3 text-xs text-rose-300">
          <span className="font-semibold">Performance Calculation Notice: </span>
          {error}
        </div>
      )}

      {/* Primary KPI Cards */}
      <PerformanceSummaryCards summary={summary} loading={loading} />

      {/* Inner Analytics Tabs */}
      <div className="border-b border-atlas-border-default/60">
        <nav className="flex space-x-1" aria-label="Performance Sub-modules">
          {(
            [
              { id: "growth", label: "TWR Growth Curve", icon: TrendingUp },
              { id: "equity_value", label: "Monetary Equity Curve", icon: DollarSign },
              { id: "periodic", label: "Periodic Returns Matrix", icon: BarChart3 },
              { id: "cash_flows", label: "Classified Flows Ledger", icon: Filter },
              { id: "benchmark", label: "Benchmark Analysis", icon: Scale },
              { id: "quality", label: "Data Quality & Marks", icon: ShieldCheck },
              { id: "runs", label: "Run History & Audit", icon: History },
            ] as const
          ).map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-xs font-medium transition-colors ${
                  activeTab === tab.id
                    ? "border-atlas-accent text-atlas-text-primary font-semibold"
                    : "border-transparent text-atlas-text-secondary hover:border-atlas-border-default hover:text-atlas-text-primary"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content Panes */}
      <div className="space-y-4">
        {activeTab === "growth" && (
          <TimeWeightedGrowthChart
            points={series}
            benchmarkName={
              summary?.benchmark_comparison?.benchmark_name ||
              benchmarks.find((b) => b.benchmark_id === selectedBenchmarkId)?.name
            }
            baseCurrency={portfolio.base_currency}
          />
        )}

        {activeTab === "equity_value" && (
          <PortfolioValueChart
            points={series}
            baseCurrency={portfolio.base_currency}
          />
        )}

        {activeTab === "periodic" && (
          <PeriodicReturnsTable returns={periodicReturns} />
        )}

        {activeTab === "cash_flows" && (
          <CashFlowSummaryTable
            flows={cashFlows}
            baseCurrency={portfolio.base_currency}
          />
        )}

        {activeTab === "benchmark" && (
          <BenchmarkComparisonView
            comparison={summary?.benchmark_comparison}
            benchmarks={benchmarks}
            selectedBenchmarkId={selectedBenchmarkId}
            onSelectBenchmark={setSelectedBenchmarkId}
          />
        )}

        {activeTab === "quality" && (
          <PerformanceDataQualityPanel dataQuality={summary?.data_quality} />
        )}

        {activeTab === "runs" && (
          <PerformanceRunHistory runs={runHistory} />
        )}
      </div>

      {/* Methodology Inspector Drawer */}
      {summary && (
        <PerformanceMethodologyInspector
          summary={summary}
          isOpen={isInspectorOpen}
          onClose={() => setIsInspectorOpen(false)}
        />
      )}
    </div>
  );
}

