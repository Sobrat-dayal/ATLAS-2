"use client";

import React, { useState } from "react";
import {
  ExecuteHypothesisEvaluationDTO,
  HypothesisTestCriteria,
  ResearchAnalysisResult,
  ResearchHypothesis,
  ResearchHypothesisEvaluation,
} from "@/lib/research/types";
import { getHypothesisOutcomeDisplay } from "@/lib/research/formatting";
import { Badge, Button } from "@/design-system";

interface HypothesisEvaluationPanelProps {
  analysisResult?: ResearchAnalysisResult | null;
  hypotheses: ResearchHypothesis[];
  evaluations: ResearchHypothesisEvaluation[];
  isEvaluating: boolean;
  onEvaluate: (hypothesisId: string, data: ExecuteHypothesisEvaluationDTO) => Promise<unknown>;
}

export function HypothesisEvaluationPanel({
  analysisResult,
  hypotheses,
  evaluations,
  isEvaluating,
  onEvaluate,
}: HypothesisEvaluationPanelProps) {
  const [selectedHypothesisId, setSelectedHypothesisId] = useState<string>(
    hypotheses.length > 0 ? hypotheses[0].hypothesis_id : ""
  );

  const [operator, setOperator] = useState<"GT" | "GTE" | "LT" | "LTE" | "EQ" | "BETWEEN">("GTE");
  const [thresholdValue, setThresholdValue] = useState<number>(30.0);
  const [secondaryThreshold, setSecondaryThreshold] = useState<number>(40.0);
  const [requiredPeriods, setRequiredPeriods] = useState<number>(3);
  const [allowMissing, setAllowMissing] = useState<boolean>(false);
  const [analystNotes, setAnalystNotes] = useState<string>("");

  const latestEvaluation = evaluations.find(
    (ev) => ev.hypothesis_id === selectedHypothesisId && (!analysisResult || ev.analysis_run_id === analysisResult.run_id)
  ) || evaluations[0];

  const handleRunEvaluation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHypothesisId || !analysisResult) return;

    const criteria: HypothesisTestCriteria = {
      metric_id: analysisResult.metric_id,
      operator,
      threshold_value: Number(thresholdValue),
      secondary_threshold: operator === "BETWEEN" ? Number(secondaryThreshold) : undefined,
      required_periods_count: Number(requiredPeriods),
      allow_missing: allowMissing,
    };

    await onEvaluate(selectedHypothesisId, {
      analysis_run_id: analysisResult.run_id,
      criteria,
      eligible_universe: [analysisResult.primary_subject_id],
      analyst_notes: analystNotes || undefined,
    });
  };

  if (!analysisResult) {
    return (
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-8 text-center text-xs text-atlas-text-muted">
        Execute an analysis run first to test hypotheses against grounded observational datasets.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Criteria Form */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div className="mb-3 border-b border-atlas-border-subtle pb-3">
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Deterministic Hypothesis Evaluation
          </h3>
          <p className="text-xs text-atlas-text-muted">
            Formally test whether verified financial observations satisfy explicit numerical criteria without fabricating conclusions.
          </p>
        </div>

        <form onSubmit={handleRunEvaluation} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Target Hypothesis
              </label>
              {hypotheses.length > 0 ? (
                <select
                  value={selectedHypothesisId}
                  onChange={(e) => setSelectedHypothesisId(e.target.value)}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
                >
                  {hypotheses.map((h) => (
                    <option key={h.hypothesis_id} value={h.hypothesis_id}>
                      {h.statement}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="rounded-xs border border-dashed border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-muted">
                  No investigation hypotheses found. A generic thesis will be evaluated.
                </div>
              )}
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Analytical Dataset Context
              </label>
              <div className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary">
                Run: {analysisResult.run_id} ({analysisResult.primary_subject_id} — {analysisResult.metric_id})
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Operator
              </label>
              <select
                value={operator}
                onChange={(e) => setOperator(e.target.value as "GT" | "GTE" | "LT" | "LTE" | "EQ" | "BETWEEN")}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary font-mono"
              >
                <option value="GTE">&gt;= (Greater or Equal)</option>
                <option value="GT">&gt; (Strictly Greater)</option>
                <option value="LTE">&lt;= (Less or Equal)</option>
                <option value="LT">&lt; (Strictly Less)</option>
                <option value="EQ">== (Exact Match)</option>
                <option value="BETWEEN">BETWEEN (Range)</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Threshold Value
              </label>
              <input
                type="number"
                step="any"
                value={thresholdValue}
                onChange={(e) => setThresholdValue(Number(e.target.value))}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary"
                required
              />
            </div>

            {operator === "BETWEEN" && (
              <div>
                <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                  Upper Threshold
                </label>
                <input
                  type="number"
                  step="any"
                  value={secondaryThreshold}
                  onChange={(e) => setSecondaryThreshold(Number(e.target.value))}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary"
                  required
                />
              </div>
            )}

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Required Periods
              </label>
              <input
                type="number"
                min={1}
                max={20}
                value={requiredPeriods}
                onChange={(e) => setRequiredPeriods(Number(e.target.value))}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Analyst Evaluation Notes & Caveats
            </label>
            <input
              type="text"
              placeholder="e.g. Accounting rules changed under ASC 606 in prior fiscal years."
              value={analystNotes}
              onChange={(e) => setAnalystNotes(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <label className="flex items-center gap-2 text-xs text-atlas-text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={allowMissing}
                onChange={(e) => setAllowMissing(e.target.checked)}
                className="rounded-xs border-atlas-border-default text-atlas-accent"
              />
              Allow missing observations to pass criteria
            </label>

            <Button type="submit" variant="primary" size="sm" disabled={isEvaluating}>
              {isEvaluating ? "Evaluating Criteria..." : "Execute Deterministic Test"}
            </Button>
          </div>
        </form>
      </div>

      {/* Latest Evaluation Outcome Result */}
      {latestEvaluation && (
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-subtle pb-3">
            <div>
              <div className="text-xs text-atlas-text-muted">Evaluation Outcome</div>
              <div className="flex items-center gap-2 mt-0.5">
                {(() => {
                  const badge = getHypothesisOutcomeDisplay(latestEvaluation.result_status);
                  return (
                    <Badge variant={badge.variant} className="text-xs font-medium">
                      {badge.label}
                    </Badge>
                  );
                })()}
                <span className="text-xs text-atlas-text-secondary font-mono">
                  {latestEvaluation.observation_count} Observations Evaluated
                </span>
              </div>
            </div>

            <div className="text-right text-[11px] text-atlas-text-muted font-mono">
              Tested: {new Date(latestEvaluation.created_at).toLocaleTimeString()}
            </div>
          </div>

          {/* Evidence Breakdown Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="rounded-xs border border-emerald-500/20 bg-emerald-500/5 p-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-emerald-600">
                  Supporting Observations
                </span>
                <Badge variant="positive" className="text-[10px]">
                  {latestEvaluation.supporting_evidence_ids.length}
                </Badge>
              </div>
              {latestEvaluation.supporting_evidence_ids.length > 0 ? (
                <ul className="space-y-1 text-xs text-atlas-text-secondary font-mono">
                  {latestEvaluation.supporting_evidence_ids.map((id) => (
                    <li key={id} className="truncate">
                      • {id}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-atlas-text-muted italic">
                  No observations satisfied the threshold.
                </p>
              )}
            </div>

            <div className="rounded-xs border border-rose-500/20 bg-rose-500/5 p-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-rose-600">
                  Contradicting / Inconsistent Observations
                </span>
                <Badge variant="negative" className="text-[10px]">
                  {latestEvaluation.contradicting_evidence_ids.length}
                </Badge>
              </div>
              {latestEvaluation.contradicting_evidence_ids.length > 0 ? (
                <ul className="space-y-1 text-xs text-atlas-text-secondary font-mono">
                  {latestEvaluation.contradicting_evidence_ids.map((id) => (
                    <li key={id} className="truncate">
                      • {id}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-atlas-text-muted italic">
                  Zero contradicting observations detected.
                </p>
              )}
            </div>
          </div>

          {/* Limitations Disclosure */}
          {latestEvaluation.limitations && latestEvaluation.limitations.length > 0 && (
            <div className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-2.5 text-xs text-atlas-text-muted">
              <span className="font-semibold text-atlas-text-secondary">Analytical Caveats: </span>
              {latestEvaluation.limitations.join("; ")}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
