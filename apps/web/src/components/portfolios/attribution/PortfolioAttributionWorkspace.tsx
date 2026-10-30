"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  AttributionTab,
  usePortfolioAttribution,
} from "@/hooks/portfolios/usePortfolioAttribution";
import { AttributionDimension, AttributionMethod } from "@/lib/portfolios/attribution/types";
import { ActiveReturnWaterfall } from "./ActiveReturnWaterfall";
import { AttributionReconciliationPanel } from "./AttributionReconciliationPanel";
import { AttributionSummaryCards } from "./AttributionSummaryCards";
import { BenchmarkInspectorPanel } from "./BenchmarkInspectorPanel";
import { CurrencyAttributionPanel } from "./CurrencyAttributionPanel";
import { MethodologyInspectorPanel } from "./MethodologyInspectorPanel";
import { MultiPeriodAttributionPanel } from "./MultiPeriodAttributionPanel";
import { SectorAttributionTable } from "./SectorAttributionTable";
import { SecurityContributionPanel } from "./SecurityContributionPanel";
import {
  AlertCircle,
  BarChart3,
  BookOpen,
  Calendar,
  Coins,
  Compass,
  Layers,
  PieChart,
  RefreshCw,
  Scale,
  Sliders,
} from "lucide-react";

interface PortfolioAttributionWorkspaceProps {
  portfolioId: string;
}

export function PortfolioAttributionWorkspace({
  portfolioId,
}: PortfolioAttributionWorkspaceProps) {
  const {
    run,
    benchmarks,
    selectedBenchmark,
    selectedMethod,
    selectedDimension,
    activeTab,
    loading,
    calculating,
    error,
    setSelectedBenchmark,
    setSelectedMethod,
    setSelectedDimension,
    setActiveTab,
    calculate,
    refresh,
  } = usePortfolioAttribution(portfolioId);

  if (loading && !run) {
    return (
      <div className="flex h-96 flex-col items-center justify-center space-y-3 rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <RefreshCw className="h-6 w-6 animate-spin text-atlas-accent" />
        <p className="text-sm text-atlas-text-secondary">
          Computing institutional performance attribution...
        </p>
      </div>
    );
  }

  if (error && !run) {
    return (
      <div className="flex h-96 flex-col items-center justify-center space-y-3 rounded border border-rose-500/20 bg-rose-500/5 p-6 text-center">
        <AlertCircle className="h-8 w-8 text-rose-400" />
        <h4 className="text-base font-semibold text-atlas-text-primary">Attribution Computation Failed</h4>
        <p className="max-w-md text-xs text-atlas-text-secondary">{error}</p>
        <Button variant="secondary" size="sm" onClick={refresh} className="mt-2">
          Retry Computation
        </Button>
      </div>
    );
  }

  if (!run) return null;

  return (
    <div className="space-y-4">
      {/* Workspace Controls Header */}
      <div className="flex flex-col gap-3 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-atlas-text-primary">
              Performance Attribution Analytics
            </h2>
            <span className="rounded bg-atlas-accent/10 px-2 py-0.5 text-xs font-semibold text-atlas-accent">
              Stage 113 Institutional
            </span>
          </div>
          <p className="mt-0.5 text-xs text-atlas-text-secondary">
            Multi-dimensional Brinson decomposition, security return contributions, and Carino logarithmic compounding.
          </p>
        </div>

        {/* Attribution Parameter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Benchmark Selector */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-atlas-text-muted">Benchmark:</span>
            <select
              value={selectedBenchmark}
              onChange={(e) => {
                const newBench = e.target.value;
                setSelectedBenchmark(newBench);
                calculate({ benchmark_id: newBench });
              }}
              disabled={calculating}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            >
              {benchmarks.map((b) => (
                <option key={b.benchmark_id} value={b.benchmark_id}>
                  {b.symbol} ({b.name})
                </option>
              ))}
            </select>
          </div>

          {/* Attribution Method Selector */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-atlas-text-muted">Method:</span>
            <select
              value={selectedMethod}
              onChange={(e) => {
                const newMethod = e.target.value as AttributionMethod;
                setSelectedMethod(newMethod);
                calculate({ attribution_method: newMethod });
              }}
              disabled={calculating}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            >
              <option value="BRINSON_FACHLER">Brinson-Fachler (1985)</option>
              <option value="BRINSON_HOOD_BEEBOWER">Brinson-Hood-Beebower (1986)</option>
            </select>
          </div>

          {/* Dimension Selector */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-atlas-text-muted">Dimension:</span>
            <select
              value={selectedDimension}
              onChange={(e) => {
                const newDim = e.target.value as AttributionDimension;
                setSelectedDimension(newDim);
                calculate({ classification_dimension: newDim });
              }}
              disabled={calculating}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            >
              <option value="SECTOR">GICS Sectors</option>
              <option value="INDUSTRY">Industry Groups</option>
            </select>
          </div>

          {/* Recalculate Button */}
          <Button
            variant="secondary"
            size="sm"
            onClick={() => calculate()}
            disabled={calculating}
            className="h-7 gap-1 text-xs"
          >
            <RefreshCw className={`h-3 w-3 ${calculating ? "animate-spin" : ""}`} />
            <span>{calculating ? "Calculating..." : "Recalculate"}</span>
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <AttributionSummaryCards run={run} />

      {/* Active Return Decomposition Waterfall */}
      <ActiveReturnWaterfall run={run} />

      {/* Tab Navigation */}
      <div className="flex border-b border-atlas-border-default/60">
        <nav className="flex space-x-1" aria-label="Attribution Views">
          {[
            { id: "sectors", label: "Sector Attribution", icon: PieChart },
            { id: "securities", label: "Security Contributions", icon: BarChart3 },
            { id: "multi_period", label: "Multi-Period (Carino)", icon: Calendar },
            { id: "currency", label: "Currency Decomposition", icon: Coins },
            { id: "benchmarks_audit", label: "Audit & Benchmarks", icon: Scale },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as AttributionTab)}
                className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-xs font-medium transition-colors ${
                  isActive
                    ? "border-atlas-accent text-atlas-text-primary font-semibold"
                    : "border-transparent text-atlas-text-secondary hover:border-atlas-border-default hover:text-atlas-text-primary"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content Panels */}
      {activeTab === "sectors" && <SectorAttributionTable run={run} />}

      {activeTab === "securities" && <SecurityContributionPanel run={run} />}

      {activeTab === "multi_period" && <MultiPeriodAttributionPanel run={run} />}

      {activeTab === "currency" && <CurrencyAttributionPanel run={run} />}

      {activeTab === "benchmarks_audit" && (
        <div className="space-y-6">
          <AttributionReconciliationPanel run={run} />
          <BenchmarkInspectorPanel
            run={run}
            benchmarks={benchmarks}
            selectedBenchmark={selectedBenchmark}
            onSelectBenchmark={setSelectedBenchmark}
            onApplyBenchmark={(id) => calculate({ benchmark_id: id })}
            calculating={calculating}
          />
          <MethodologyInspectorPanel />
        </div>
      )}
    </div>
  );
}

