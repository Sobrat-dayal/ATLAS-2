"use client";

import React from "react";
import { Badge } from "@/design-system";
import { ResearchReviewRequestResponse } from "@/lib/research/types";
import { getReviewStatusDisplay, formatResearchDate } from "@/lib/research/formatting";

interface ResearchReviewQueueProps {
  reviews: ResearchReviewRequestResponse[];
  selectedReviewId: string | null;
  onSelectReview: (id: string) => void;
  isLoading?: boolean;
}

export function ResearchReviewQueue({
  reviews,
  selectedReviewId,
  onSelectReview,
  isLoading = false,
}: ResearchReviewQueueProps) {
  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center p-4 text-xs text-atlas-text-muted">
        Loading review requests...
      </div>
    );
  }

  if (reviews.length === 0) {
    return (
      <div className="flex h-48 flex-col items-center justify-center p-4 text-center">
        <p className="text-xs font-medium text-atlas-text-secondary">No review requests found</p>
        <p className="mt-1 text-[11px] text-atlas-text-muted">
          Submit a report or thesis revision to initiate an institutional peer review round.
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-atlas-border-default overflow-y-auto">
      {reviews.map((r) => {
        const isSelected = r.review_request_id === selectedReviewId;
        const statusMeta = getReviewStatusDisplay(r.status);

        return (
          <div
            key={r.review_request_id}
            onClick={() => onSelectReview(r.review_request_id)}
            className={`cursor-pointer p-3 transition-colors ${
              isSelected
                ? "bg-atlas-accent/10 border-l-2 border-atlas-accent"
                : "hover:bg-atlas-surface-1"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] font-semibold text-atlas-text-primary">
                    {r.target_type}: {r.target_id.slice(0, 16)}...
                  </span>
                  <Badge variant={statusMeta.variant} className="text-[10px]">
                    {statusMeta.label}
                  </Badge>
                </div>
                <div className="mt-1 flex items-center gap-2 text-[11px] text-atlas-text-muted">
                  <span>Rev v{r.target_revision_number}</span>
                  <span>•</span>
                  <span>Round {r.review_round}</span>
                  <span>•</span>
                  <span>Scope: {r.review_scope.replace("_", " ")}</span>
                </div>
              </div>
            </div>

            <div className="mt-2 flex items-center justify-between text-[11px] text-atlas-text-secondary">
              <span className="truncate">Reviewer: <strong className="text-atlas-text-primary">{r.assigned_reviewer_id}</strong></span>
              <span className="shrink-0 text-atlas-text-muted font-mono">{formatResearchDate(r.created_at)}</span>
            </div>

            {r.instructions && (
              <p className="mt-1 line-clamp-1 text-[11px] italic text-atlas-text-muted">
                &ldquo;{r.instructions}&rdquo;
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
