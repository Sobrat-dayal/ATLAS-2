"use client";

import React, { useState } from "react";
import {
  CreateResearchAnalysisDTO,
  CreateResearchAssumptionDTO,
  CreateResearchFindingDTO,
  ExecuteHypothesisEvaluationDTO,
  ResearchAnalysis,
  ResearchAnalysisResult,
  ResearchAnalysisRun,
  ResearchAnalysisType,
  ResearchAssumption,
  ResearchFinding,
  ResearchHypothesis,
  ResearchHypothesisEvaluation,
  ResearchInvestigation,
  SensitivityAnalysisRequest,
  SensitivityAnalysisResponse,
  UpdateResearchFindingDTO,
} from "@/lib/research/types";
import { ResearchAnalysisList } from "./ResearchAnalysisList";
import { ResearchAnalysisStudio } from "./ResearchAnalysisStudio";
import { NewAnalysisDialog } from "./NewAnalysisDialog";
import { Button } from "@/design-system";

interface ResearchAnalysisWorkspaceProps {
  analyses: ResearchAnalysis[];
  analysesTotal: number;
  isAnalysesLoading: boolean;
  selectedAnalysisId?: string | null;
  currentAnalysis?: ResearchAnalysis | null;
  analysisRuns: ResearchAnalysisRun[];
  selectedRunId?: string | null;
  currentRunResult?: ResearchAnalysisResult | null;
  currentRunProvenance?: Record<string, unknown> | null;
  isRunExecuting: boolean;
  analysisFindings: ResearchFinding[];
  analysisAssumptions: ResearchAssumption[];
  sensitivityResult?: SensitivityAnalysisResponse | null;
  isSensitivityLoading: boolean;
  hypothesisEvaluations: ResearchHypothesisEvaluation[];
  isHypothesisEvaluating: boolean;
  investigations: ResearchInvestigation[];
  hypotheses: ResearchHypothesis[];
  onSelectAnalysis: (id: string | null) => void;
  onCreateAnalysis: (data: CreateResearchAnalysisDTO) => Promise<unknown>;
  onDuplicateAnalysis: (id: string) => Promise<unknown>;
  onDeleteAnalysis: (id: string) => Promise<unknown>;
  onExecuteAnalysisRun: (id: string, policy?: string) => Promise<unknown>;
  onSelectRun: (runId: string) => Promise<unknown>;
  onCreateFinding: (data: CreateResearchFindingDTO) => Promise<unknown>;
  onUpdateFinding: (id: string, data: UpdateResearchFindingDTO) => Promise<unknown>;
  onDeleteFinding: (id: string) => Promise<unknown>;
  onCreateAssumption: (data: CreateResearchAssumptionDTO) => Promise<unknown>;
  onDeleteAssumption: (id: string) => Promise<unknown>;
  onExecuteSensitivity: (data: SensitivityAnalysisRequest) => Promise<unknown>;
  onEvaluateHypothesis: (hypothesisId: string, data: ExecuteHypothesisEvaluationDTO) => Promise<unknown>;
  onOpenSource?: (sourceId: string) => void;
}

export function ResearchAnalysisWorkspace({
  analyses,
  isAnalysesLoading,
  selectedAnalysisId,
  currentAnalysis,
  analysisRuns,
  selectedRunId,
  currentRunResult,
  currentRunProvenance,
  isRunExecuting,
  analysisFindings,
  analysisAssumptions,
  sensitivityResult,
  isSensitivityLoading,
  hypothesisEvaluations,
  isHypothesisEvaluating,
  investigations,
  hypotheses,
  onSelectAnalysis,
  onCreateAnalysis,
  onDuplicateAnalysis,
  onDeleteAnalysis,
  onExecuteAnalysisRun,
  onSelectRun,
  onCreateFinding,
  onUpdateFinding,
  onDeleteFinding,
  onCreateAssumption,
  onDeleteAssumption,
  onExecuteSensitivity,
  onEvaluateHypothesis,
  onOpenSource,
}: ResearchAnalysisWorkspaceProps) {
  const [isNewDialogOpen, setIsNewDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<ResearchAnalysisType | undefined>(undefined);
  const [entityFilter, setEntityFilter] = useState("");

  const filteredAnalyses = analyses.filter((an) => {
    if (typeFilter && an.analysis_type !== typeFilter) return false;
    if (entityFilter && an.primary_subject_entity_id?.toUpperCase() !== entityFilter.toUpperCase()) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        an.title.toLowerCase().includes(q) ||
        an.description?.toLowerCase().includes(q) ||
        an.primary_subject_entity_id?.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="flex h-full w-full overflow-hidden bg-atlas-surface-1">
      {/* Sidebar List */}
      <ResearchAnalysisList
        analyses={filteredAnalyses}
        isLoading={isAnalysesLoading}
        selectedAnalysisId={selectedAnalysisId}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
        entityFilter={entityFilter}
        onEntityFilterChange={setEntityFilter}
        onSelectAnalysis={(id) => onSelectAnalysis(id)}
        onNewAnalysis={() => setIsNewDialogOpen(true)}
      />

      {/* Main Studio Console */}
      <div className="flex-1 overflow-hidden">
        {currentAnalysis ? (
          <ResearchAnalysisStudio
            analysis={currentAnalysis}
            runs={analysisRuns}
            selectedRunId={selectedRunId}
            runResult={currentRunResult}
            provenanceData={currentRunProvenance}
            isRunExecuting={isRunExecuting}
            findings={analysisFindings}
            assumptions={analysisAssumptions}
            sensitivityResult={sensitivityResult}
            isSensitivityLoading={isSensitivityLoading}
            hypotheses={hypotheses}
            evaluations={hypothesisEvaluations}
            isHypothesisEvaluating={isHypothesisEvaluating}
            onRunAnalysis={onExecuteAnalysisRun}
            onSelectRun={onSelectRun}
            onDuplicate={onDuplicateAnalysis}
            onDelete={onDeleteAnalysis}
            onCreateFinding={(data) => onCreateFinding(data)}
            onUpdateFinding={onUpdateFinding}
            onDeleteFinding={onDeleteFinding}
            onCreateAssumption={(data) => onCreateAssumption(data)}
            onDeleteAssumption={onDeleteAssumption}
            onExecuteSensitivity={onExecuteSensitivity}
            onEvaluateHypothesis={onEvaluateHypothesis}
            onOpenSource={onOpenSource}
          />
        ) : (
          <div className="flex h-full flex-col items-center justify-center p-8 text-center text-atlas-text-muted space-y-3">
            <div className="text-2xl font-bold text-atlas-text-secondary">
              No Analysis Selected
            </div>
            <p className="max-w-md text-xs">
              Select an institutional research analysis from the sidebar to inspect trends, verify peer benchmarks, evaluate hypotheses, or launch a new study.
            </p>
            <Button variant="primary" size="sm" onClick={() => setIsNewDialogOpen(true)}>
              + Create Analysis
            </Button>
          </div>
        )}
      </div>

      {/* Modal Dialog */}
      <NewAnalysisDialog
        isOpen={isNewDialogOpen}
        investigations={investigations}
        onClose={() => setIsNewDialogOpen(false)}
        onSubmit={async (data) => {
          await onCreateAnalysis(data);
        }}
      />
    </div>
  );
}
