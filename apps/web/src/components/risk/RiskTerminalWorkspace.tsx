"use client";

import React, { useState } from "react";
import { RiskTab, useRiskTerminal } from "@/hooks/risk/useRiskTerminal";
import {
  Activity,
  AlertCircle,
  BarChart3,
  BookOpen,
  Compass,
  Cpu,
  Database,
  Flame,
  History,
  Layers,
  PieChart,
  Scale,
  ShieldAlert,
  ShieldCheck,
  Sliders,
  Zap,
  Globe,
  Grid,
} from "lucide-react";
import { BenchmarkSensitivityPanel } from "./BenchmarkSensitivityPanel";
import { CovarianceDiagnosticsPanel } from "./CovarianceDiagnosticsPanel";
import { DrawdownChart } from "./DrawdownChart";
import { DrawdownEpisodesTable } from "./DrawdownEpisodesTable";
import { HistoricalVolatilityChart } from "./HistoricalVolatilityChart";
import { RiskContributionTable } from "./RiskContributionTable";
import { RiskDataQualityPanel } from "./RiskDataQualityPanel";
import { RiskHeader } from "./RiskHeader";
import { RiskModelInspector } from "./RiskModelInspector";
import { RiskOverviewSummary } from "./RiskOverviewSummary";
import { RiskRunHistory } from "./RiskRunHistory";

// Stage 116 Components
import { TailRiskSummaryCards } from "./tail/TailRiskSummaryCards";
import { LossDistributionChart } from "./tail/LossDistributionChart";
import { TailModelComparisonTable } from "./tail/TailModelComparisonTable";
import { ScenarioLibraryTable } from "./scenarios/ScenarioLibraryTable";
import { ScenarioBuilderModal } from "./scenarios/ScenarioBuilderModal";
import { ScenarioResultsWorkspace } from "./scenarios/ScenarioResultsWorkspace";
import { VaRExceptionBacktestPanel } from "./diagnostics/VaRExceptionBacktestPanel";

// Stage 117 Components
import { FactorRiskWorkspace } from "./factors/FactorRiskWorkspace";
import { ConcentrationWorkspace } from "./concentration/ConcentrationWorkspace";
import { CurrencyRiskWorkspace } from "./currency/CurrencyRiskWorkspace";
import { SectorRiskWorkspace } from "./sectors/SectorRiskWorkspace";
import { CrossExposureWorkspace } from "./cross/CrossExposureWorkspace";

// Stage 118 Components
import { OptionsRiskWorkspace } from "./options/OptionsRiskWorkspace";
import { FixedIncomeRiskWorkspace } from "./fixed-income/FixedIncomeRiskWorkspace";

interface RiskTerminalWorkspaceProps {
  initialPortfolioId?: string;
}

export function RiskTerminalWorkspace({ initialPortfolioId }: RiskTerminalWorkspaceProps) {
  const terminal = useRiskTerminal(initialPortfolioId);
  const [isScenarioBuilderOpen, setIsScenarioBuilderOpen] = useState(false);

  const tabs: { id: RiskTab; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Overview", icon: <BarChart3 className="h-3.5 w-3.5" /> },
    { id: "factors", label: "Multi-Factor", icon: <Cpu className="h-3.5 w-3.5 text-sky-400" /> },
    { id: "concentration", label: "Concentration & HHI", icon: <Scale className="h-3.5 w-3.5 text-purple-400" /> },
    { id: "currency", label: "Currency & FX", icon: <Globe className="h-3.5 w-3.5 text-emerald-400" /> },
    { id: "sectors", label: "Sector Attribution", icon: <PieChart className="h-3.5 w-3.5 text-amber-400" /> },
    { id: "cross_exposure", label: "Cross-Exposure", icon: <Grid className="h-3.5 w-3.5 text-indigo-400" /> },
    { id: "options", label: "Options & Greeks", icon: <Sliders className="h-3.5 w-3.5 text-amber-400" /> },
    { id: "fixed_income", label: "Fixed-Income & Curves", icon: <Activity className="h-3.5 w-3.5 text-emerald-400" /> },
    { id: "tail_risk", label: "VaR & Expected Shortfall", icon: <ShieldAlert className="h-3.5 w-3.5 text-rose-400" /> },
    { id: "scenarios", label: "Scenario Stress Testing", icon: <Zap className="h-3.5 w-3.5 text-amber-400" /> },
    { id: "diagnostics", label: "VaR Backtest & Kupiec", icon: <Scale className="h-3.5 w-3.5 text-emerald-400" /> },
    { id: "volatility", label: "Rolling Volatility", icon: <Activity className="h-3.5 w-3.5" /> },
    { id: "drawdowns", label: "Drawdown Analytics", icon: <Flame className="h-3.5 w-3.5" /> },
    { id: "benchmark", label: "Benchmark Sensitivity", icon: <Compass className="h-3.5 w-3.5" /> },
    { id: "contributions", label: "Euler Contributions", icon: <Layers className="h-3.5 w-3.5" /> },
    { id: "models", label: "Covariance & Diagnostics", icon: <Cpu className="h-3.5 w-3.5" /> },
    { id: "data_quality", label: "Data Quality & Coverage", icon: <Database className="h-3.5 w-3.5" /> },
    { id: "runs", label: "Audit Runs", icon: <History className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="flex h-full min-h-[calc(100vh-4rem)] flex-col bg-atlas-surface-0 text-atlas-text-primary">
      {/* 1. Header Toolbar */}
      <RiskHeader
        portfolios={terminal.portfolios}
        selectedPortfolioId={terminal.selectedPortfolioId}
        onSelectPortfolio={terminal.setSelectedPortfolioId}
        accounts={terminal.accounts}
        selectedAccountId={terminal.selectedAccountId}
        onSelectAccount={terminal.setSelectedAccountId}
        selectedBenchmark={terminal.selectedBenchmark}
        onSelectBenchmark={terminal.setSelectedBenchmark}
        selectedModelId={terminal.selectedModelId}
        onSelectModel={terminal.setSelectedModelId}
        modelsCatalog={terminal.modelsCatalog}
        selectedFrequency={terminal.selectedFrequency}
        onSelectFrequency={terminal.setSelectedFrequency}
        rollingWindowSize={terminal.rollingWindowSize}
        onSelectRollingWindow={terminal.setRollingWindowSize}
        onCalculate={terminal.calculate}
        onRefresh={terminal.refresh}
        calculating={terminal.calculating}
        loading={terminal.loading}
      />

      {/* 2. Error Banner */}
      {terminal.error && (
        <div className="mx-4 mt-3 flex items-start gap-2.5 rounded border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold">Calculation Notice: </span>
            {terminal.error}
          </div>
        </div>
      )}

      {/* 3. Terminal Navigation Sub-tabs */}
      <div className="flex flex-wrap items-center gap-1 border-b border-atlas-border-default/60 bg-atlas-surface-1/70 px-4 pt-2">
        {tabs.map((tab) => {
          const isActive = terminal.activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => terminal.setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-xs font-medium transition ${
                isActive
                  ? "border-atlas-accent-blue text-atlas-accent-blue"
                  : "border-transparent text-atlas-text-secondary hover:border-atlas-border-default hover:text-atlas-text-primary"
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* 4. Main Body Content */}
      <div className="flex-1 space-y-4 p-4 overflow-y-auto">
        {terminal.loading && !terminal.summary ? (
          <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
            <Activity className="h-5 w-5 animate-spin mr-2 text-atlas-accent-blue" />
            Loading portfolio risk profiles and returns telemetry...
          </div>
        ) : terminal.portfolios.length === 0 ? (
          <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-8 text-center">
            <ShieldCheck className="h-10 w-10 mx-auto text-atlas-text-muted opacity-40" />
            <h3 className="mt-2 text-sm font-semibold text-atlas-text-primary">
              No Portfolios Available
            </h3>
            <p className="mt-1 text-xs text-atlas-text-muted">
              Create an investment portfolio in the Portfolios module to analyze historical and model risk metrics.
            </p>
          </div>
        ) : (
          <>
            {/* Always show high-density KPI summary at top of overview or relevant tabs */}
            <RiskOverviewSummary
              summary={terminal.summary}
              run={terminal.run}
              benchmarkSensitivity={terminal.benchmarkSensitivity}
              dataQuality={terminal.dataQuality}
            />

            {/* Tab 1: Overview */}
            {terminal.activeTab === "overview" && (
              <div className="space-y-4">
                <TailRiskSummaryCards
                  run={terminal.tailRiskRun}
                  selectedModel={terminal.selectedTailModel}
                  selectedConfidence={terminal.selectedConfidence}
                  selectedHorizon={terminal.selectedHorizon}
                  calculating={terminal.calculatingTail}
                  onSelectModel={(m) => {
                    terminal.setSelectedTailModel(m);
                    terminal.calculateTailRiskAction(m);
                  }}
                  onSelectConfidence={(c) => {
                    terminal.setSelectedConfidence(c);
                    terminal.calculateTailRiskAction(undefined, c);
                  }}
                  onSelectHorizon={(h) => {
                    terminal.setSelectedHorizon(h);
                    terminal.calculateTailRiskAction(undefined, undefined, h);
                  }}
                  onRecalculate={() => terminal.calculateTailRiskAction()}
                />
                <HistoricalVolatilityChart
                  volatilityData={terminal.volatilityData}
                  rollingWindowSize={terminal.rollingWindowSize}
                  onSelectRollingWindow={terminal.setRollingWindowSize}
                />
                <DrawdownChart drawdownData={terminal.drawdownData} />
                <RiskContributionTable contributionsData={terminal.contributionsData} />
              </div>
            )}

            {/* Stage 116 Tab: VaR & Expected Shortfall */}
            {terminal.activeTab === "tail_risk" && (
              <div className="space-y-4">
                <TailRiskSummaryCards
                  run={terminal.tailRiskRun}
                  selectedModel={terminal.selectedTailModel}
                  selectedConfidence={terminal.selectedConfidence}
                  selectedHorizon={terminal.selectedHorizon}
                  calculating={terminal.calculatingTail}
                  onSelectModel={(m) => {
                    terminal.setSelectedTailModel(m);
                    terminal.calculateTailRiskAction(m);
                  }}
                  onSelectConfidence={(c) => {
                    terminal.setSelectedConfidence(c);
                    terminal.calculateTailRiskAction(undefined, c);
                  }}
                  onSelectHorizon={(h) => {
                    terminal.setSelectedHorizon(h);
                    terminal.calculateTailRiskAction(undefined, undefined, h);
                  }}
                  onRecalculate={() => terminal.calculateTailRiskAction()}
                />

                <LossDistributionChart
                  distribution={terminal.tailDistribution}
                  run={terminal.tailRiskRun}
                />

                <TailModelComparisonTable
                  activeModel={terminal.selectedTailModel}
                  onSelectModel={(m) => {
                    terminal.setSelectedTailModel(m);
                    terminal.calculateTailRiskAction(m);
                  }}
                />
              </div>
            )}

            {/* Stage 116 Tab: Scenario Stress Testing */}
            {terminal.activeTab === "scenarios" && (
              <div className="space-y-4">
                <ScenarioLibraryTable
                  scenarios={terminal.scenarios}
                  executing={terminal.executingScenario}
                  onExecuteScenario={terminal.executeScenarioAction}
                  onOpenCreateModal={() => setIsScenarioBuilderOpen(true)}
                  onCompareScenarios={() => terminal.compareScenariosAction()}
                  comparing={terminal.comparingScenarios}
                />

                <ScenarioResultsWorkspace
                  run={terminal.activeScenarioRun}
                  comparison={terminal.scenarioComparison}
                />
              </div>
            )}

            {/* Stage 117 Tab: Multi-Factor Risk */}
            {terminal.activeTab === "factors" && (
              <FactorRiskWorkspace
                factorRun={terminal.factorRun}
                securityExposures={terminal.factorRun?.security_exposures}
                calculating={terminal.calculatingFactors}
                onRecalculate={() => terminal.calculateFactorsAction()}
              />
            )}

            {/* Stage 117 Tab: Concentration & HHI */}
            {terminal.activeTab === "concentration" && (
              <ConcentrationWorkspace
                snapshot={terminal.concentrationSnapshot}
                selectedDimension={terminal.selectedConcentrationDimension}
                onSelectDimension={terminal.loadConcentrationAction}
                loading={terminal.loadingConcentration}
                onRefresh={() => terminal.loadConcentrationAction()}
              />
            )}

            {/* Stage 117 Tab: Currency & FX Risk */}
            {terminal.activeTab === "currency" && (
              <CurrencyRiskWorkspace
                snapshot={terminal.currencySnapshot}
                loading={terminal.loadingCurrency}
                onRefresh={() => terminal.loadCurrencyRiskAction()}
              />
            )}

            {/* Stage 117 Tab: Sector & Industry Attribution */}
            {terminal.activeTab === "sectors" && (
              <SectorRiskWorkspace
                snapshot={terminal.sectorSnapshot}
                loading={terminal.loadingSector}
                onRefresh={terminal.loadSectorRiskAction}
              />
            )}

            {/* Stage 117 Tab: 2D Cross-Exposure */}
            {terminal.activeTab === "cross_exposure" && (
              <CrossExposureWorkspace
                matrix={terminal.crossExposureMatrix}
                selectedRowDim={terminal.selectedCrossRowDim}
                selectedColDim={terminal.selectedCrossColDim}
                onSelectDimensions={terminal.loadCrossExposureAction}
                loading={terminal.loadingCross}
                onRefresh={() => terminal.loadCrossExposureAction()}
              />
            )}

            {/* Stage 118 Tab: Options & Greeks */}
            {terminal.activeTab === "options" && (
              <OptionsRiskWorkspace
                portfolioId={terminal.selectedPortfolioId}
                optionsSummary={terminal.optionsSummary}
                loading={terminal.loadingOptions}
                onRefresh={terminal.fetchOptionsRiskAction}
                onCalculateOption={terminal.calculateOptionContractAction}
              />
            )}

            {/* Stage 118 Tab: Fixed-Income & Yield Curves */}
            {terminal.activeTab === "fixed_income" && (
              <FixedIncomeRiskWorkspace
                portfolioId={terminal.selectedPortfolioId}
                fixedIncomeSummary={terminal.fixedIncomeSummary}
                curveDefinition={terminal.curveDefinition}
                selectedBondCashFlows={terminal.selectedBondCashFlows}
                loading={terminal.loadingFixedIncome}
                onRefresh={terminal.fetchFixedIncomeRiskAction}
                onCalculateBond={terminal.calculateBondContractAction}
                onFetchCashFlows={terminal.fetchBondCashFlowsAction}
              />
            )}

            {/* Stage 116 Tab: VaR Backtest & Kupiec */}
            {terminal.activeTab === "diagnostics" && (
              <div className="space-y-4">
                <VaRExceptionBacktestPanel
                  backtest={terminal.backtestRun}
                  running={terminal.runningBacktest}
                  selectedModel={terminal.backtestModel}
                  selectedConfidence={terminal.backtestConfidence}
                  selectedWindowSize={terminal.backtestWindowSize}
                  onSelectModel={terminal.setBacktestModel}
                  onSelectConfidence={terminal.setBacktestConfidence}
                  onSelectWindowSize={terminal.setBacktestWindowSize}
                  onRunBacktest={() => terminal.runBacktestAction()}
                />
              </div>
            )}

            {/* Tab 2: Rolling Volatility */}
            {terminal.activeTab === "volatility" && (
              <div className="space-y-4">
                <HistoricalVolatilityChart
                  volatilityData={terminal.volatilityData}
                  rollingWindowSize={terminal.rollingWindowSize}
                  onSelectRollingWindow={terminal.setRollingWindowSize}
                />
                <RiskModelInspector
                  modelsCatalog={terminal.modelsCatalog}
                  metricsCatalog={terminal.metricsCatalog}
                />
              </div>
            )}

            {/* Tab 3: Drawdown Analytics */}
            {terminal.activeTab === "drawdowns" && (
              <div className="space-y-4">
                <DrawdownChart drawdownData={terminal.drawdownData} />
                <DrawdownEpisodesTable episodes={terminal.drawdownData?.episodes || []} />
              </div>
            )}

            {/* Tab 4: Benchmark Sensitivity */}
            {terminal.activeTab === "benchmark" && (
              <div className="space-y-4">
                <BenchmarkSensitivityPanel
                  benchmarkSensitivity={terminal.benchmarkSensitivity}
                />
              </div>
            )}

            {/* Tab 5: Euler Contributions */}
            {terminal.activeTab === "contributions" && (
              <div className="space-y-4">
                <RiskContributionTable contributionsData={terminal.contributionsData} />
              </div>
            )}

            {/* Tab 6: Covariance & Diagnostics */}
            {terminal.activeTab === "models" && (
              <div className="space-y-4">
                <CovarianceDiagnosticsPanel
                  diagnostics={
                    terminal.contributionsData?.covariance_diagnostics ||
                    terminal.run?.covariance_diagnostics ||
                    null
                  }
                />
                <RiskModelInspector
                  modelsCatalog={terminal.modelsCatalog}
                  metricsCatalog={terminal.metricsCatalog}
                />
              </div>
            )}

            {/* Tab 7: Data Quality & Coverage */}
            {terminal.activeTab === "data_quality" && (
              <div className="space-y-4">
                <RiskDataQualityPanel
                  dataQuality={terminal.dataQuality}
                  inputManifest={terminal.run?.input_manifest}
                />
              </div>
            )}

            {/* Tab 8: Audit Runs */}
            {terminal.activeTab === "runs" && (
              <div className="space-y-4">
                <RiskRunHistory
                  runsList={terminal.runsList}
                  selectedRunId={terminal.run?.risk_run_id}
                />
              </div>
            )}
          </>
        )}
      </div>

      {/* Scenario Builder Modal */}
      <ScenarioBuilderModal
        isOpen={isScenarioBuilderOpen}
        onClose={() => setIsScenarioBuilderOpen(false)}
        onCreateScenario={terminal.createScenarioAction}
      />
    </div>
  );
}
