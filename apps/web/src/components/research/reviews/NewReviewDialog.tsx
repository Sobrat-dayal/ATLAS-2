"use client";

import React, { useState } from "react";
import { Button } from "@/design-system";
import { CreateReviewRequest, ReviewScope, ResearchReport, ResearchResourceType } from "@/lib/research/types";

interface NewReviewDialogProps {
  isOpen: boolean;
  onClose: () => void;
  availableReports: ResearchReport[];
  onSubmitReview: (data: CreateReviewRequest) => Promise<unknown>;
}

export function NewReviewDialog({
  isOpen,
  onClose,
  availableReports,
  onSubmitReview,
}: NewReviewDialogProps) {
  const [targetType, setTargetType] = useState<ResearchResourceType>("REPORT");
  const [targetId, setTargetId] = useState<string>(
    availableReports.length > 0 ? availableReports[0].report_id : ""
  );
  const [assignedReviewerId, setAssignedReviewerId] = useState<string>("senior-analyst-02");
  const [reviewScope, setReviewScope] = useState<ReviewScope>("FULL_REPORT");
  const [dueDate, setDueDate] = useState<string>("");
  const [instructions, setInstructions] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetId.trim()) {
      setErrorMsg("Please select or specify a target report ID.");
      return;
    }
    if (!assignedReviewerId.trim()) {
      setErrorMsg("Please assign a peer reviewer.");
      return;
    }

    setErrorMsg(null);
    setIsSubmitting(true);
    try {
      await onSubmitReview({
        target_type: targetType,
        target_id: targetId.trim(),
        assigned_reviewer_id: assignedReviewerId.trim(),
        review_scope: reviewScope,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
        instructions: instructions.trim() || undefined,
      });
      onClose();
    } catch (err: unknown) {
      const e = err as Error;
      setErrorMsg(e.message || "Failed to submit review request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-sm border border-atlas-border-default bg-atlas-surface-0 shadow-2xl">
        <div className="flex items-center justify-between border-b border-atlas-border-default p-4">
          <div>
            <h3 className="text-sm font-bold text-atlas-text-primary">
              Initiate Peer Review Round
            </h3>
            <p className="text-xs text-atlas-text-muted">
              Submit an authored report or thesis revision to an independent reviewer.
            </p>
          </div>
          <Button variant="ghost" size="xs" onClick={onClose}>
            ✕
          </Button>
        </div>

        {errorMsg && (
          <div className="mx-4 mt-3 rounded-xs border border-rose-500/30 bg-rose-500/10 p-2 text-xs text-rose-400">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
                Target Domain:
              </label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value as ResearchResourceType)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary"
              >
                <option value="REPORT">Research Report</option>
                <option value="THESIS">Investment Thesis</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
                Review Scope:
              </label>
              <select
                value={reviewScope}
                onChange={(e) => setReviewScope(e.target.value as ReviewScope)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary"
              >
                <option value="FULL_REPORT">Full Report Synthesis</option>
                <option value="DOCUMENT_CONTENT">Document Content</option>
                <option value="FINANCIAL_MODEL">Financial Model & Runs</option>
                <option value="CITATION_AUDIT">Source Citation Audit</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
              Target Report:
            </label>
            {availableReports.length > 0 ? (
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary"
              >
                {availableReports.map((rep) => (
                  <option key={rep.report_id} value={rep.report_id}>
                    {rep.title} (v{rep.current_revision} • {rep.status})
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                placeholder="Enter report ID"
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary"
              />
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
                Assigned Reviewer User ID:
              </label>
              <input
                type="text"
                value={assignedReviewerId}
                onChange={(e) => setAssignedReviewerId(e.target.value)}
                placeholder="senior-reviewer"
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
                Review Due Date (Optional):
              </label>
              <input
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-atlas-text-primary mb-1">
              Instructions & Review Criteria:
            </label>
            <textarea
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder="e.g. Please check Form 10-K operating income reconciliations and verify peer benchmarking table..."
              className="w-full h-20 rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
            />
          </div>

          <div className="border-t border-atlas-border-default pt-3 flex justify-end gap-2">
            <Button variant="secondary" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Submitting..." : "Submit for Review"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
