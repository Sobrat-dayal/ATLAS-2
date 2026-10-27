"use client";

import React, { useState } from "react";
import {
  CreateResearchAssumptionDTO,
  CreateResearchFindingDTO,
  ExecuteHypothesisEvaluationDTO,
  ResearchAnalysis,
  ResearchAnalysisResult,
  ResearchAnalysisRun,
  ResearchAssumption,
  ResearchFinding,
  ResearchHypothesis,
  ResearchHypothesisEvaluation,
  SensitivityAnalysisRequest,
  SensitivityAnalysisResponse,
  UpdateResearchFindingDTO,
} from "@/lib/research/types";
import {
  formatCAGR,
  formatStatisticsValue,
  getAnalysisStatusDisplay,
  getAnalysisTypeLabel,
} from "@/lib/research/formatting";
import { Badge, Button } from "@/design-system";
import { FinancialTrendChart } from "./FinancialTrendChart";
import { PeerBenchmarkChart } from "./PeerBenchmarkChart";
import { EconomicResearchChart } from "./EconomicResearchChart";
import { AnalysisResultsTable } from "./AnalysisResultsTable";
import { HypothesisEvaluationPanel } from "./HypothesisEvaluationPanel";
import { FindingsWorkspace } from "./FindingsWorkspace";
import { ScenarioSensitivityWorkspace } from "./ScenarioSensitivityWorkspace";
import { AnalysisProvenanceInspector } from "./AnalysisProvenanceInspector";

export type StudioSubTab =
  | "TREND_RESULTS"
  | "HYPOTHESIS"
  | "FINDINGS"
  | "SCENARIOS"
  | "PROVENANCE";

interface ResearchAnalysisStudioProps {
  analysis: ResearchAnalysis;
  runs: ResearchAnalysisRun[];
  selectedRunId?: string | null;
  runResult?: ResearchAnalysisResult | null;
  provenanceData?: Record<string, unknown> | null;
  isRunExecuting: boolean;
  findings: ResearchFinding[];
  assumptions: ResearchAssumption[];
  sensitivityResult?: SensitivityAnalysisResponse | null;
  isSensitivityLoading: boolean;
  hypotheses: ResearchHypothesis[];
  evaluations: ResearchHypothesisEvaluation[];
  isHypothesisEvaluating: boolean;
  onRunAnalysis: (analysisId: string, policy?: string) => Promise<unknown>;
  onSelectRun: (runId: string) => Promise<unknown>;
  onDuplicate: (analysisId: string) => Promise<unknown>;
  onDelete: (analysisId: string) => Promise<unknown>;
  onCreateFinding: (data: CreateResearchFindingDTO) => Promise<unknown>;
  onUpdateFinding: (findingId: string, data: UpdateResearchFindingDTO) => Promise<unknown>;
  onDeleteFinding: (findingId: string) => Promise<unknown>;
  onCreateAssumption: (data: CreateResearchAssumptionDTO) => Promise<unknown>;
  onDeleteAssumption: (assumptionId: string) => Promise<unknown>;
  onExecuteSensitivity: (data: SensitivityAnalysisRequest) => Promise<unknown>;
  onEvaluateHypothesis: (hypothesisId: string, data: ExecuteHypothesisEvaluationDTO) => Promise<unknown>;
  onOpenSource?: (sourceId: string) => void;
}

export function ResearchAnalysisStudio({
  analysis,
  runs,
  selectedRunId,
  runResult,
  provenanceData,
  isRunExecuting,
  findings,
  assumptions,
  sensitivityResult,
  isSensitivityLoading,
  hypotheses,
  evaluations,
  isHypothesisEvaluating,
  onRunAnalysis,
  onSelectRun,
  onDuplicate,
  onDelete,
  onCreateFinding,
  onUpdateFinding,
  onDeleteFinding,
  onCreateAssumption,
  onDeleteAssumption,
  onExecuteSensitivity,
  onEvaluateHypothesis,
  onOpenSource,
}: ResearchAnalysisStudioProps) {
  const [subTab, setSubTab] = useState<StudioSubTab>("TREND_RESULTS");
  const [inputPolicy, setInputPolicy] = useState<string>("PINNED_SOURCE_VERSION");

  const statusBadge = getAnalysisStatusDisplay(analysis.status);
  const stats = runResult?.summary_statistics;

  return (
    <div className="flex h-full flex-col overflow-y-auto p-4 space-y-4">
      {/* Studio Header & Action Bar */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4 shrink-0 shadow-xs">
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-atlas-border-subtle pb-3">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h2 className="text-base font-bold text-atlas-text-primary tracking-tight">
                {analysis.title}
              </h2>
              <Badge variant="outline" className="font-mono text-[10px]">
                {getAnalysisTypeLabel(analysis.analysis_type)}
              </Badge>
              <Badge variant={statusBadge.variant} className="text-[10px]">
                {statusBadge.label}
              </Badge>
              <span className="font-mono text-[10px] text-atlas-text-muted">
                Rev {analysis.current_revision} • ID: {analysis.analysis_id}
              </span>
            </div>

            {analysis.description && (
              <p className="text-xs text-atlas-text-secondary">{analysis.description}</p>
            )}

            {analysis.research_objective && (
              <div className="mt-1 text-xs text-atlas-text-muted">
                <span className="font-semibold text-atlas-text-secondary">Objective: </span>
                {analysis.research_objective}
              </div>
            )}
          </div>

          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={inputPolicy}
              onChange={(e) => setInputPolicy(e.target.value)}
              className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2.5 py-1 text-xs text-atlas-text-primary font-mono"
              title="Input versioning policy"
            >
              <option value="PINNED_SOURCE_VERSION">Pinned Filing Version</option>
              <option value="LATEST_AUTHORIZED_DATA">Latest Data Refresh</option>
            </select>

            <Button
              variant="primary"
              size="sm"
              onClick={() => onRunAnalysis(analysis.analysis_id, inputPolicy)}
              disabled={isRunExecuting}
            >
              {isRunExecuting ? "Running Analysis..." : "Execute Analysis"}
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => onDuplicate(analysis.analysis_id)}
            >
              Duplicate
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => onDelete(analysis.analysis_id)}
              className="text-rose-500 hover:text-rose-400"
            >
              Delete
            </Button>
          </div>
        </div>

        {/* Studio Sub-Navigation & Run History Switcher */}
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
          <nav className="flex items-center rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-0.5 text-xs">
            <button
              onClick={() => setSubTab("TREND_RESULTS")}
              className={`rounded-xs px-3 py-1 font-medium transition-colors ${
                subTab === "TREND_RESULTS"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Results & Trend
            </button>
            <button
              onClick={() => setSubTab("HYPOTHESIS")}
              className={`rounded-xs px-3 py-1 font-medium transition-colors ${
                subTab === "HYPOTHESIS"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Hypothesis Test
            </button>
            <button
              onClick={() => setSubTab("FINDINGS")}
              className={`rounded-xs px-3 py-1 font-medium transition-colors ${
                subTab === "FINDINGS"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Findings ({findings.length})
            </button>
            <button
              onClick={() => setSubTab("SCENARIOS")}
              className={`rounded-xs px-3 py-1 font-medium transition-colors ${
                subTab === "SCENARIOS"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Scenarios ({assumptions.length})
            </button>
            <button
              onClick={() => setSubTab("PROVENANCE")}
              className={`rounded-xs px-3 py-1 font-medium transition-colors ${
                subTab === "PROVENANCE"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Provenance & Audit
            </button>
          </nav>

          {/* Historical Run Selector */}
          {runs.length > 0 && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-atlas-text-muted">Run History:</span>
              <select
                value={selectedRunId || ""}
                onChange={(e) => onSelectRun(e.target.value)}
                className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2 py-0.5 text-xs font-mono text-atlas-text-primary"
              >
                {runs.map((r) => (
                  <option key={r.run_id} value={r.run_id}>
                    {r.run_id} ({r.input_policy}) — {new Date(r.started_at).toLocaleTimeString()}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Main Studio Sub-Tab Content */}
      <div className="flex-1">
        {subTab === "TREND_RESULTS" && (
          <div className="space-y-4">
            {/* KPI Metric Strip */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
                  <div className="text-[10px] uppercase font-mono text-atlas-text-muted">
                    Sample Size N
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-text-primary mt-1">
                    {stats.sample_size_n}
                  </div>
                </div>

                <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
                  <div className="text-[10px] uppercase font-mono text-atlas-text-muted">
                    Compound Growth (CAGR)
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-accent mt-1">
                    {formatCAGR(stats.cagr_percentage)}
                  </div>
                </div>

                <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
                  <div className="text-[10px] uppercase font-mono text-atlas-text-muted">
                    Sample Mean
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-text-primary mt-1">
                    {formatStatisticsValue(stats.mean, runResult?.observations[0]?.unit)}
                  </div>
                </div>

                <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
                  <div className="text-[10px] uppercase font-mono text-atlas-text-muted">
                    Sample Median
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-text-primary mt-1">
                    {formatStatisticsValue(stats.median, runResult?.observations[0]?.unit)}
                  </div>
                </div>

                <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
                  <div className="text-[10px] uppercase font-mono text-atlas-text-muted">
                    Std Deviation (s)
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-text-primary mt-1">
                    {formatStatisticsValue(stats.standard_deviation)}
                  </div>
                </div>

                <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3">
                  <div className="text-[10px] uppercase font-mono text-atlas-text-muted">
                    Missing / Excluded
                  </div>
                  <div className="text-base font-bold font-mono text-atlas-text-muted mt-1">
                    {stats.missing_count}
                  </div>
                </div>
              </div>
            )}

            {/* Visual Chart Panel */}
            {runResult ? (
              analysis.analysis_type === "PEER_BENCHMARKING" ? (
                <PeerBenchmarkChart
                  observations={runResult.observations}
                  summaryStatistics={runResult.summary_statistics}
                  comparabilityWarnings={runResult.comparability_warnings}
                  metricLabel={runResult.metric_id}
                />
              ) : analysis.analysis_type === "MACROECONOMIC_TIME_SERIES" ? (
                <EconomicResearchChart
                  observations={runResult.observations}
                  summaryStatistics={runResult.summary_statistics}
                  indicatorLabel={runResult.metric_id}
                />
              ) : (
                <FinancialTrendChart
                  observations={runResult.observations}
                  summaryStatistics={runResult.summary_statistics}
                  metricLabel={runResult.metric_id}
                  unit={runResult.observations[0]?.unit}
                />
              )
            ) : (
              <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-8 text-center text-xs text-atlas-text-muted">
                No active run execution results. Click &quot;Execute Analysis&quot; above to compute quantitative metrics.
              </div>
            )}

            {/* Observations Table */}
            {runResult && (
              <AnalysisResultsTable
                observations={runResult.observations}
                onOpenSource={onOpenSource}
              />
            )}
          </div>
        )}

        {subTab === "HYPOTHESIS" && (
          <HypothesisEvaluationPanel
            analysisResult={runResult}
            hypotheses={hypotheses}
            evaluations={evaluations}
            isEvaluating={isHypothesisEvaluating}
            onEvaluate={onEvaluateHypothesis}
          />
        )}

        {subTab === "FINDINGS" && (
          <FindingsWorkspace
            analysis={analysis}
            findings={findings}
            onCreateFinding={onCreateFinding}
            onUpdateFinding={onUpdateFinding}
            onDeleteFinding={onDeleteFinding}
          />
        )}

        {subTab === "SCENARIOS" && (
          <ScenarioSensitivityWorkspace
            analysis={analysis}
            assumptions={assumptions}
            sensitivityResult={sensitivityResult}
            isLoading={isSensitivityLoading}
            onCreateAssumption={onCreateAssumption}
            onDeleteAssumption={onDeleteAssumption}
            onExecuteSensitivity={onExecuteSensitivity}
          />
        )}

        {subTab === "PROVENANCE" && (
          <AnalysisProvenanceInspector
            result={runResult}
            provenanceData={provenanceData}
          />
        )}
      </div>
    </div>
  );
}
