"use client";

import React from "react";
import {
  OptimizationWorkspaceTab,
  usePortfolioOptimization,
} from "@/hooks/portfolios/usePortfolioOptimization";
import { OptimizationObjective } from "@/lib/portfolios/optimization/types";
import { CandidateAllocationChart } from "./CandidateAllocationChart";
import { CurrentVsCandidateTable } from "./CurrentVsCandidateTable";
import { EfficientFrontierChart } from "./EfficientFrontierChart";
import { HypotheticalTradeTable } from "./HypotheticalTradeTable";
import { OptimizationConstraintBuilder } from "./OptimizationConstraintBuilder";
import { OptimizationFeasibilityPanel } from "./OptimizationFeasibilityPanel";
import { OptimizationMethodologyInspector } from "./OptimizationMethodologyInspector";
import { OptimizationSensitivityPanel } from "./OptimizationSensitivityPanel";
import { OptimizationSolverInspector } from "./OptimizationSolverInspector";
import { OptimizationStudyList } from "./OptimizationStudyList";
import { OptimizationSummaryCards } from "./OptimizationSummaryCards";
import {
  Activity,
  AlertCircle,
  BarChart3,
  BookOpen,
  Compass,
  Cpu,
  FolderOpen,
  PieChart,
  RefreshCw,
  Sliders,
  Sparkles,
} from "lucide-react";

interface PortfolioOptimizationWorkspaceProps {
  portfolioId: string;
}

export function PortfolioOptimizationWorkspace({
  portfolioId,
}: PortfolioOptimizationWorkspaceProps) {
  const {
    activeRun,
    activeStudy,
    studies,
    universe,
    methodologies,
    activeTab,
    selectedObjective,
    riskAversion,
    targetReturn,
    constraints,
    validationResult,
    loading,
    solving,
    error,
    setActiveTab,
    setSelectedObjective,
    setRiskAversion,
    setTargetReturn,
    addConstraint,
    removeConstraint,
    validateConstraints,
    selectStudy,
    createStudy,
    archiveStudy,
    executeRun,
    refresh,
  } = usePortfolioOptimization(portfolioId);

  if (loading && !activeRun) {
    return (
      <div className="flex h-96 flex-col items-center justify-center space-y-3 rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <RefreshCw className="h-6 w-6 animate-spin text-atlas-accent" />
        <p className="text-sm text-atlas-text-secondary">
          Initializing institutional convex optimization engines...
        </p>
      </div>
    );
  }

  if (error && !activeRun) {
    return (
      <div className="flex h-96 flex-col items-center justify-center space-y-3 rounded border border-rose-500/20 bg-rose-500/5 p-6 text-center">
        <AlertCircle className="h-8 w-8 text-rose-400" />
        <h4 className="text-base font-semibold text-atlas-text-primary">
          Optimization Solver Initialization Failed
        </h4>
        <p className="max-w-md text-xs text-atlas-text-secondary">{error}</p>
        <button
          onClick={refresh}
          className="mt-2 rounded bg-atlas-accent px-4 py-1.5 text-xs font-semibold text-atlas-surface-0 hover:bg-atlas-accent/90"
        >
          Retry Initialization
        </button>
      </div>
    );
  }

  if (!activeRun) return null;

  return (
    <div className="space-y-4">
      {/* Workspace Controls Header */}
      <div className="flex flex-col gap-3 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-atlas-text-primary">
              Portfolio Optimization & Construction Platform
            </h2>
            <span className="rounded bg-atlas-accent/10 px-2 py-0.5 text-xs font-semibold text-atlas-accent">
              Stage 114 Institutional
            </span>
            {activeStudy && (
              <span className="rounded border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 text-[11px] font-mono text-cyan-300">
                Study: {activeStudy.name}
              </span>
            )}
          </div>
          <p className="mt-0.5 text-xs text-atlas-text-secondary">
            Mean-Variance, Efficient Frontier, Maximum Sharpe, Spinu Risk-Parity, and Rebalancing Proposals.
          </p>
        </div>

        {/* Controls Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Objective Selector */}
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-atlas-text-muted">Objective:</span>
            <select
              value={selectedObjective}
              onChange={(e) => {
                const newObj = e.target.value as OptimizationObjective;
                setSelectedObjective(newObj);
              }}
              disabled={solving}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            >
              <option value="MINIMUM_VARIANCE">Minimum Variance</option>
              <option value="MAXIMUM_SHARPE">Maximum Sharpe Ratio</option>
              <option value="MEAN_VARIANCE_UTILITY">Mean-Variance Utility (λ)</option>
              <option value="RISK_PARITY">Equal Risk Contribution (Risk Parity)</option>
              <option value="TARGET_RETURN_MIN_VARIANCE">Target Return Min Variance</option>
              <option value="MAXIMUM_EXPECTED_RETURN">Maximum Expected Return</option>
            </select>
          </div>

          {/* Risk Aversion Slider / Input if Utility */}
          {selectedObjective === "MEAN_VARIANCE_UTILITY" && (
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-atlas-text-muted">λ (Risk Aversion):</span>
              <input
                type="number"
                step="0.5"
                min="0.1"
                max="20"
                value={riskAversion}
                onChange={(e) => setRiskAversion(parseFloat(e.target.value) || 2.0)}
                disabled={solving}
                className="w-16 rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2 py-1 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>
          )}

          {/* Target Return Input if Target Return */}
          {selectedObjective === "TARGET_RETURN_MIN_VARIANCE" && (
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-atlas-text-muted">Target Return:</span>
              <input
                type="number"
                step="0.01"
                placeholder="0.10"
                value={targetReturn !== undefined ? targetReturn : ""}
                onChange={(e) =>
                  setTargetReturn(e.target.value ? parseFloat(e.target.value) : undefined)
                }
                disabled={solving}
                className="w-20 rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2 py-1 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            </div>
          )}

          {/* Execute / Solve Button */}
          <button
            onClick={() => executeRun()}
            disabled={solving}
            className="flex items-center gap-1.5 rounded bg-atlas-accent px-3 py-1 text-xs font-semibold text-atlas-surface-0 hover:bg-atlas-accent/90 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-3 w-3 ${solving ? "animate-spin" : ""}`} />
            <span>{solving ? "Optimizing..." : "Solve Portfolio"}</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <OptimizationSummaryCards run={activeRun} />

      {/* Tab Navigation */}
      <div className="flex border-b border-atlas-border-default/60">
        <nav className="flex space-x-1 overflow-x-auto" aria-label="Optimization Views">
          {[
            { id: "frontier", label: "Efficient Frontier", icon: Compass },
            { id: "comparison", label: "Current vs Candidate", icon: BarChart3 },
            { id: "constraints", label: "Constraints & Feasibility", icon: Sliders },
            { id: "sensitivity", label: "Sensitivity Analysis", icon: Sparkles },
            { id: "diagnostics", label: "Solver Diagnostics", icon: Cpu },
            { id: "studies", label: `Studies (${studies.length})`, icon: FolderOpen },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as OptimizationWorkspaceTab)}
                className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap ${
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

      {/* Tab Content Display */}
      <div>
        {activeTab === "frontier" && (
          <div className="space-y-4">
            <EfficientFrontierChart run={activeRun} />
            <CandidateAllocationChart
              comparisons={activeRun.comparisons}
              cashWeight={activeRun.candidate.cash_weight}
              baseCurrency={activeRun.base_currency}
            />
          </div>
        )}

        {activeTab === "comparison" && (
          <div className="space-y-4">
            <CurrentVsCandidateTable run={activeRun} />
            <HypotheticalTradeTable
              comparisons={activeRun.comparisons}
              baseCurrency={activeRun.base_currency}
              baselineNav={activeRun.baseline_nav}
              estimatedTurnover={activeRun.candidate.estimated_turnover}
              estimatedCost={activeRun.candidate.estimated_cost}
            />
          </div>
        )}

        {activeTab === "constraints" && (
          <div className="space-y-4">
            <OptimizationConstraintBuilder
              constraints={constraints}
              universe={universe}
              validationResult={validationResult}
              onAddConstraint={addConstraint}
              onRemoveConstraint={removeConstraint}
              onValidate={validateConstraints}
            />
            <OptimizationFeasibilityPanel
              candidate={activeRun.candidate}
              diagnostics={activeRun.diagnostics}
            />
          </div>
        )}

        {activeTab === "sensitivity" && (
          <OptimizationSensitivityPanel scenarios={activeRun.sensitivity_results} />
        )}

        {activeTab === "diagnostics" && (
          <OptimizationSolverInspector
            diagnostics={activeRun.diagnostics}
            covariance={activeRun.covariance}
            expectedReturns={activeRun.expected_returns}
            inputHash={activeRun.input_hash}
          />
        )}

        {activeTab === "studies" && (
          <OptimizationStudyList
            studies={studies}
            activeStudy={activeStudy}
            universe={universe}
            onSelectStudy={selectStudy}
            onCreateStudy={createStudy}
            onArchiveStudy={archiveStudy}
          />
        )}
      </div>

      {/* Expandable Mathematical Disclosures & Formulations */}
      <OptimizationMethodologyInspector />
    </div>
  );
}
