"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchReviewRequestResponse,
  CreateReviewDecisionRequest,
  ReviewDecisionType,
  QualityGateResultResponse,
} from "@/lib/research/types";
import {
  getReviewStatusDisplay,
  getReviewDecisionDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";

interface ResearchReviewDetailProps {
  review: ResearchReviewRequestResponse | null;
  qualityGateResult: QualityGateResultResponse | null;
  isQualityGateRunning: boolean;
  onRunQualityGate: (targetId: string, revisionNumber?: number) => void;
  onDecideReview: (reviewId: string, data: CreateReviewDecisionRequest) => Promise<unknown>;
  onCancelReview: (reviewId: string) => Promise<unknown>;
  onOpenParticipants: () => void;
  onOpenCirculation: () => void;
}

export function ResearchReviewDetail({
  review,
  qualityGateResult,
  isQualityGateRunning,
  onRunQualityGate,
  onDecideReview,
  onCancelReview,
  onOpenParticipants,
  onOpenCirculation,
}: ResearchReviewDetailProps) {
  const [decisionType, setDecisionType] = useState<ReviewDecisionType>("APPROVE");
  const [decisionComment, setDecisionComment] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [actionError, setActionError] = useState<string | null>(null);

  if (!review) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center text-xs text-atlas-text-muted">
        Select a review request from the queue to inspect governance requirements and issue review decisions.
      </div>
    );
  }

  const statusMeta = getReviewStatusDisplay(review.status);
  const isPending = review.status === "SUBMITTED" || review.status === "IN_REVIEW";

  const handleDecisionSubmit = async () => {
    setActionError(null);
    setIsSubmitting(true);
    try {
      await onDecideReview(review.review_request_id, {
        decision: decisionType,
        decision_comment: decisionComment.trim() || undefined,
        expected_revision_number: review.target_revision_number,
      });
      setDecisionComment("");
    } catch (err: unknown) {
      const e = err as Error;
      setActionError(e.message || "Failed to record review decision.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm("Are you sure you want to cancel this review request?")) return;
    setActionError(null);
    try {
      await onCancelReview(review.review_request_id);
    } catch (err: unknown) {
      const e = err as Error;
      setActionError(e.message || "Failed to cancel review request.");
    }
  };

  return (
    <div className="flex h-full flex-col overflow-y-auto p-4 space-y-4">
      {/* Top Banner / Metadata Card */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-atlas-text-primary">
                {review.target_type}: {review.target_id}
              </span>
              <Badge variant={statusMeta.variant} className="text-xs">
                {statusMeta.label}
              </Badge>
              <Badge variant="outline" className="text-xs font-mono">
                Round {review.review_round}
              </Badge>
            </div>
            <p className="mt-1 text-xs text-atlas-text-secondary">
              Scope: <strong>{review.review_scope.replace("_", " ")}</strong> • Requested by:{" "}
              <strong>{review.requested_by}</strong> • Assigned Reviewer:{" "}
              <strong>{review.assigned_reviewer_id}</strong>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="secondary" size="xs" onClick={onOpenParticipants}>
              Manage Participants
            </Button>
            {review.status === "APPROVED" && (
              <Button variant="primary" size="xs" onClick={onOpenCirculation}>
                Circulate Approved
              </Button>
            )}
            {isPending && (
              <Button variant="danger" size="xs" onClick={handleCancel}>
                Cancel Request
              </Button>
            )}
          </div>
        </div>

        {/* Revision & Content Hash Pinning */}
        <div className="mt-3 grid grid-cols-2 gap-3 border-t border-atlas-border-default pt-3 text-[11px] sm:grid-cols-4">
          <div>
            <span className="text-atlas-text-muted">Target Revision:</span>
            <div className="font-mono font-medium text-atlas-text-primary">
              v{review.target_revision_number}
            </div>
          </div>
          <div>
            <span className="text-atlas-text-muted">Pinned Content Hash:</span>
            <div className="truncate font-mono font-medium text-atlas-text-primary" title={review.target_content_hash}>
              {review.target_content_hash.slice(0, 16)}...
            </div>
          </div>
          <div>
            <span className="text-atlas-text-muted">Requested Date:</span>
            <div className="font-mono text-atlas-text-primary">
              {formatResearchDate(review.created_at)}
            </div>
          </div>
          <div>
            <span className="text-atlas-text-muted">Due Date:</span>
            <div className="font-mono text-atlas-text-primary">
              {review.due_date ? formatResearchDate(review.due_date) : "Open"}
            </div>
          </div>
        </div>

        {review.instructions && (
          <div className="mt-3 rounded-xs bg-atlas-surface-2 p-2 text-xs text-atlas-text-secondary">
            <span className="font-semibold text-atlas-text-primary">Review Instructions: </span>
            {review.instructions}
          </div>
        )}
      </div>

      {/* Governance Quality Gate Audit */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-default">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Institutional Quality Gate Evaluation
            </h3>
            <p className="text-[11px] text-atlas-text-muted">
              Pre-flight validation for revision structural integrity, citation cutoff compliance, and comment resolution.
            </p>
          </div>
          <Button
            variant="secondary"
            size="xs"
            onClick={() => onRunQualityGate(review.target_id, review.target_revision_number)}
            disabled={isQualityGateRunning}
          >
            {isQualityGateRunning ? "Evaluating..." : "Run Quality Gate"}
          </Button>
        </div>

        {qualityGateResult ? (
          <div className="mt-3 space-y-3">
            <div className="flex items-center gap-3">
              <Badge
                variant={qualityGateResult.eligible_for_review ? "positive" : "negative"}
                className="text-[11px]"
              >
                {qualityGateResult.eligible_for_review ? "Review Gate: Passed" : "Review Gate: Blocked"}
              </Badge>
              <Badge
                variant={qualityGateResult.eligible_for_finalization ? "positive" : "warning"}
                className="text-[11px]"
              >
                {qualityGateResult.eligible_for_finalization
                  ? "Publication Ready"
                  : "Finalization Pending Resolution"}
              </Badge>
              <span className="text-[11px] text-atlas-text-muted font-mono">
                {qualityGateResult.blocking_issues_count} Blocking • {qualityGateResult.warnings_count} Warnings
              </span>
            </div>

            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {qualityGateResult.checklist.map((item) => (
                <div
                  key={item.check_id}
                  className="flex items-start gap-2 rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs"
                >
                  <span
                    className={`mt-0.5 inline-block h-2 w-2 rounded-full shrink-0 ${
                      item.passed ? "bg-emerald-500" : "bg-amber-500"
                    }`}
                  />
                  <div>
                    <div className="font-semibold text-atlas-text-primary">
                      {item.check_id}: {item.title}
                    </div>
                    <div className="text-[11px] text-atlas-text-muted">{item.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="mt-3 text-center text-xs text-atlas-text-muted py-2">
            Quality gate evaluation has not been executed on revision v{review.target_revision_number}. Click &ldquo;Run Quality Gate&rdquo; above.
          </div>
        )}
      </div>

      {/* Review Decision Workspace */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary mb-2">
          Formal Review Decision
        </h3>

        {actionError && (
          <div className="mb-3 rounded-xs border border-rose-500/30 bg-rose-500/10 p-2 text-xs text-rose-400">
            {actionError}
          </div>
        )}

        {isPending ? (
          <div className="space-y-3">
            <p className="text-xs text-atlas-text-secondary">
              As an assigned reviewer, evaluate the evidence claims and analytical findings before recording your formal audit decision. Under Separation of Duties, report authors cannot approve their own reports.
            </p>

            <div className="flex gap-2">
              {(["APPROVE", "REQUEST_CHANGES", "REJECT"] as ReviewDecisionType[]).map((dt) => {
                const decMeta = getReviewDecisionDisplay(dt);
                const isChosen = decisionType === dt;
                return (
                  <button
                    key={dt}
                    type="button"
                    onClick={() => setDecisionType(dt)}
                    className={`flex-1 rounded-xs border px-3 py-2 text-xs font-semibold transition-all ${
                      isChosen
                        ? dt === "APPROVE"
                          ? "border-emerald-500 bg-emerald-500/20 text-emerald-400"
                          : dt === "REQUEST_CHANGES"
                          ? "border-amber-500 bg-amber-500/20 text-amber-400"
                          : "border-rose-500 bg-rose-500/20 text-rose-400"
                        : "border-atlas-border-default bg-atlas-surface-1 text-atlas-text-secondary hover:bg-atlas-surface-2"
                    }`}
                  >
                    {decMeta.label}
                  </button>
                );
              })}
            </div>

            <div>
              <label className="block text-[11px] font-medium text-atlas-text-secondary mb-1">
                Decision Audit Comments & Rationale:
              </label>
              <textarea
                value={decisionComment}
                onChange={(e) => setDecisionComment(e.target.value)}
                placeholder="Detail verification findings, filing confirmation, or required modifications..."
                className="w-full h-24 rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-none"
              />
            </div>

            <div className="flex justify-end">
              <Button
                variant={decisionType === "APPROVE" ? "primary" : "secondary"}
                size="sm"
                onClick={handleDecisionSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? "Recording..." : `Confirm Decision: ${decisionType}`}
              </Button>
            </div>
          </div>
        ) : review.latest_decision ? (
          <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge
                  variant={getReviewDecisionDisplay(review.latest_decision.decision).variant}
                  className="text-xs"
                >
                  {getReviewDecisionDisplay(review.latest_decision.decision).label}
                </Badge>
                <span className="text-xs text-atlas-text-secondary">
                  Decided by <strong>{review.latest_decision.reviewer_user_id}</strong>
                </span>
              </div>
              <span className="font-mono text-[11px] text-atlas-text-muted">
                {formatResearchDate(review.latest_decision.decided_at)}
              </span>
            </div>

            {review.latest_decision.decision_comment && (
              <p className="mt-2 text-xs italic text-atlas-text-primary">
                &ldquo;{review.latest_decision.decision_comment}&rdquo;
              </p>
            )}

            <div className="mt-2 text-[10px] text-atlas-text-muted font-mono">
              Binding Content Hash: {review.latest_decision.target_content_hash}
            </div>
          </div>
        ) : (
          <div className="text-xs text-atlas-text-muted">
            This review request is closed ({review.status}).
          </div>
        )}
      </div>
    </div>
  );
}
