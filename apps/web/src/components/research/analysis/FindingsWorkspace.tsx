"use client";

import React, { useState } from "react";
import {
  CreateResearchFindingDTO,
  ResearchAnalysis,
  ResearchFinding,
  ResearchFindingReviewStatus,
  ResearchFindingType,
  UpdateResearchFindingDTO,
} from "@/lib/research/types";
import {
  getFindingReviewStatusDisplay,
  getFindingTypeDisplay,
} from "@/lib/research/formatting";
import { Badge, Button } from "@/design-system";

interface FindingsWorkspaceProps {
  analysis: ResearchAnalysis;
  findings: ResearchFinding[];
  onCreateFinding: (data: CreateResearchFindingDTO) => Promise<unknown>;
  onUpdateFinding: (findingId: string, data: UpdateResearchFindingDTO) => Promise<unknown>;
  onDeleteFinding: (findingId: string) => Promise<unknown>;
}

export function FindingsWorkspace({
  analysis,
  findings,
  onCreateFinding,
  onUpdateFinding,
  onDeleteFinding,
}: FindingsWorkspaceProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [statement, setStatement] = useState("");
  const [findingType, setFindingType] = useState<ResearchFindingType>("CALCULATED_RESULT");
  const [methodology, setMethodology] = useState("");
  const [limitationsInput, setLimitationsInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!statement.trim()) return;

    setIsSubmitting(true);
    try {
      const limitations = limitationsInput
        ? limitationsInput.split(";").map((s) => s.trim()).filter(Boolean)
        : [];

      await onCreateFinding({
        analysis_id: analysis.analysis_id,
        analysis_run_id: analysis.latest_run_id,
        finding_type: findingType,
        statement: statement.trim(),
        methodology_description: methodology.trim() || undefined,
        limitations,
        review_status: "DRAFT",
        investigation_id: analysis.investigation_id,
      });

      setStatement("");
      setMethodology("");
      setLimitationsInput("");
      setIsCreating(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStatusChange = async (finding: ResearchFinding, newStatus: ResearchFindingReviewStatus) => {
    await onUpdateFinding(finding.finding_id, {
      expected_revision: finding.revision,
      review_status: newStatus,
    });
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Evidence-Grounded Research Findings
          </h3>
          <p className="text-xs text-atlas-text-muted">
            Formal findings distinguishing quantitative derivations from analyst interpretations, with explicit citation lineage.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={() => setIsCreating(true)}
          disabled={isCreating}
        >
          Draft New Finding
        </Button>
      </div>

      {/* Creation Form */}
      {isCreating && (
        <div className="rounded-sm border border-atlas-accent/40 bg-atlas-surface-0 p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between border-b border-atlas-border-subtle pb-2">
            <span className="text-xs font-semibold text-atlas-text-primary">
              Draft Research Finding
            </span>
            <button
              onClick={() => setIsCreating(false)}
              className="text-xs text-atlas-text-muted hover:text-atlas-text-primary"
            >
              Cancel
            </button>
          </div>

          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Finding Epistemic Category
              </label>
              <select
                value={findingType}
                onChange={(e) => setFindingType(e.target.value as ResearchFindingType)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
              >
                <option value="CALCULATED_RESULT">Calculated Result (Deterministic Derivation)</option>
                <option value="OBSERVED_FACT">Observed Fact (Direct Filing Fact)</option>
                <option value="STATISTICAL_OBSERVATION">Statistical Observation (Sample Statistics)</option>
                <option value="ANALYST_INTERPRETATION">Analyst Interpretation (Subjective Thesis)</option>
                <option value="INCONCLUSIVE_RESULT">Inconclusive Result (Insufficient/Mixed)</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Finding Statement
              </label>
              <textarea
                rows={3}
                placeholder="State the verifiable finding with explicit quantitative precision..."
                value={statement}
                onChange={(e) => setStatement(e.target.value)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                  Derivation Methodology Description
                </label>
                <input
                  type="text"
                  placeholder="e.g. Calculated operating profit CAGR over FY20-FY24 Form 10-K filings"
                  value={methodology}
                  onChange={(e) => setMethodology(e.target.value)}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                  Methodology Limitations (Semicolon-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. U.S. GAAP reported; Excludes non-operating revisions"
                  value={limitationsInput}
                  onChange={(e) => setLimitationsInput(e.target.value)}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => setIsCreating(false)}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                {isSubmitting ? "Saving Finding..." : "Persist Finding"}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Findings List */}
      <div className="space-y-3">
        {findings.length === 0 ? (
          <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-8 text-center text-xs text-atlas-text-muted">
            No research findings recorded for this analysis. Click &quot;Draft New Finding&quot; to document reproducible insights.
          </div>
        ) : (
          findings.map((f) => {
            const typeBadge = getFindingTypeDisplay(f.finding_type);
            const statusBadge = getFindingReviewStatusDisplay(f.review_status);

            return (
              <div
                key={f.finding_id}
                className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4 transition-all hover:border-atlas-border-strong"
              >
                <div className="mb-2 flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-subtle pb-2">
                  <div className="flex items-center gap-2">
                    <Badge variant={typeBadge.variant} className="text-[10px]">
                      {typeBadge.label}
                    </Badge>
                    <Badge variant={statusBadge.variant} className="text-[10px]">
                      {statusBadge.label}
                    </Badge>
                    <span className="font-mono text-[10px] text-atlas-text-muted">
                      Rev {f.revision} • ID: {f.finding_id}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <select
                      value={f.review_status}
                      onChange={(e) =>
                        handleStatusChange(f, e.target.value as ResearchFindingReviewStatus)
                      }
                      className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2 py-0.5 text-[11px] text-atlas-text-secondary"
                    >
                      <option value="DRAFT">Draft</option>
                      <option value="NEEDS_EVIDENCE">Needs Citations</option>
                      <option value="READY_FOR_REVIEW">Ready for Review</option>
                      <option value="REVIEWED">Reviewed & Verified</option>
                      <option value="ARCHIVED">Archived</option>
                    </select>

                    <button
                      type="button"
                      onClick={() => onDeleteFinding(f.finding_id)}
                      className="text-xs text-atlas-text-muted hover:text-rose-500"
                      title="Delete Finding"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                <p className="text-xs text-atlas-text-primary leading-relaxed font-medium">
                  {f.statement}
                </p>

                {f.methodology_description && (
                  <div className="mt-2 text-[11px] text-atlas-text-secondary">
                    <span className="font-semibold text-atlas-text-muted">Methodology: </span>
                    {f.methodology_description}
                  </div>
                )}

                {f.limitations && f.limitations.length > 0 && (
                  <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[10px] text-atlas-text-muted">
                    <span className="font-semibold">Caveats:</span>
                    {f.limitations.map((lim, i) => (
                      <span key={i} className="rounded-xs bg-atlas-surface-1 px-1.5 py-0.5">
                        {lim}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
