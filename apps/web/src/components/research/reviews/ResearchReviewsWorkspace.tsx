"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/design-system";
import {
  ResearchReviewRequestResponse,
  ReviewStatus,
  ResearchReport,
  QualityGateResultResponse,
  CreateReviewRequest,
  CreateReviewDecisionRequest,
  ResearchAccessGrantResponse,
  CreateAccessGrantRequest,
  ResearchCommentThreadResponse,
  CreateCommentThreadRequest,
  CreateCirculationRequest,
  ResearchInternalCirculationResponse,
  ResearchResourceType,
  ResearchRole,
} from "@/lib/research/types";
import { ResearchReviewQueue } from "./ResearchReviewQueue";
import { ResearchReviewDetail } from "./ResearchReviewDetail";
import { ResearchCommentSidebar } from "./ResearchCommentSidebar";
import { ResearchParticipantsModal } from "./ResearchParticipantsModal";
import { ResearchCirculationDialog } from "./ResearchCirculationDialog";
import { NewReviewDialog } from "./NewReviewDialog";

interface ResearchReviewsWorkspaceProps {
  reviews: ResearchReviewRequestResponse[];
  selectedReviewId: string | null;
  currentReview: ResearchReviewRequestResponse | null;
  isReviewsLoading: boolean;
  reviewStatusFilter: ReviewStatus | undefined;
  setReviewStatusFilter: (status: ReviewStatus | undefined) => void;
  availableReports: ResearchReport[];
  qualityGateResult: QualityGateResultResponse | null;
  isQualityGateRunning: boolean;
  participants: ResearchAccessGrantResponse[];
  isParticipantsLoading: boolean;
  comments: ResearchCommentThreadResponse[];
  isCommentsLoading: boolean;
  circulations: ResearchInternalCirculationResponse[];
  isCirculationsLoading: boolean;
  onSelectReview: (id: string) => void;
  onSubmitReview: (data: CreateReviewRequest) => Promise<unknown>;
  onDecideReview: (reviewId: string, data: CreateReviewDecisionRequest) => Promise<unknown>;
  onCancelReview: (reviewId: string) => Promise<unknown>;
  onRunQualityGate: (targetId: string, revisionNumber?: number) => void;
  onLoadParticipants: (resourceType: ResearchResourceType, resourceId: string) => void;
  onGrantParticipant: (resourceType: ResearchResourceType, resourceId: string, data: CreateAccessGrantRequest) => Promise<unknown>;
  onUpdateParticipant: (grantId: string, role: ResearchRole) => Promise<unknown>;
  onRevokeParticipant: (grantId: string) => Promise<unknown>;
  onLoadComments: (resourceType: string, resourceId: string, revisionNumber?: number) => void;
  onAddCommentThread: (resourceType: string, resourceId: string, data: CreateCommentThreadRequest) => Promise<unknown>;
  onAddCommentReply: (threadId: string, body: string) => Promise<unknown>;
  onResolveCommentThread: (threadId: string) => Promise<unknown>;
  onReopenCommentThread: (threadId: string) => Promise<unknown>;
  onLoadCirculations: (reportId: string) => void;
  onCirculateReport: (reportId: string, data: CreateCirculationRequest) => Promise<unknown>;
  onRevokeCirculation: (circulationId: string) => Promise<unknown>;
}

export function ResearchReviewsWorkspace({
  reviews,
  selectedReviewId,
  currentReview,
  isReviewsLoading,
  reviewStatusFilter,
  setReviewStatusFilter,
  availableReports,
  qualityGateResult,
  isQualityGateRunning,
  participants,
  isParticipantsLoading,
  comments,
  isCommentsLoading,
  circulations,
  isCirculationsLoading,
  onSelectReview,
  onSubmitReview,
  onDecideReview,
  onCancelReview,
  onRunQualityGate,
  onLoadParticipants,
  onGrantParticipant,
  onUpdateParticipant,
  onRevokeParticipant,
  onLoadComments,
  onAddCommentThread,
  onAddCommentReply,
  onResolveCommentThread,
  onReopenCommentThread,
  onLoadCirculations,
  onCirculateReport,
  onRevokeCirculation,
}: ResearchReviewsWorkspaceProps) {
  const [isNewReviewOpen, setIsNewReviewOpen] = useState<boolean>(false);
  const [isParticipantsOpen, setIsParticipantsOpen] = useState<boolean>(false);
  const [isCirculationOpen, setIsCirculationOpen] = useState<boolean>(false);

  // Load comments and participants when current review changes
  useEffect(() => {
    if (currentReview) {
      onLoadComments(currentReview.target_type, currentReview.target_id, currentReview.target_revision_number);
      onLoadParticipants(currentReview.target_type, currentReview.target_id);
      if (currentReview.target_type === "REPORT") {
        onLoadCirculations(currentReview.target_id);
      }
    }
  }, [currentReview, onLoadComments, onLoadParticipants, onLoadCirculations]);

  const filterOptions: { label: string; value: ReviewStatus | undefined }[] = [
    { label: "All Reviews", value: undefined },
    { label: "Pending", value: "SUBMITTED" },
    { label: "In Review", value: "IN_REVIEW" },
    { label: "Changes Requested", value: "CHANGES_REQUESTED" },
    { label: "Approved", value: "APPROVED" },
    { label: "Rejected", value: "REJECTED" },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden bg-atlas-surface-0">
      {/* Top Filter and Actions Toolbar */}
      <div className="flex flex-wrap items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2 gap-2">
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {filterOptions.map((opt) => (
            <button
              key={opt.label}
              onClick={() => setReviewStatusFilter(opt.value)}
              className={`rounded-xs px-2.5 py-1 text-xs font-medium transition-colors ${
                reviewStatusFilter === opt.value
                  ? "bg-atlas-accent text-white font-semibold"
                  : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="xs"
            onClick={() => setIsNewReviewOpen(true)}
          >
            + Initiate Review
          </Button>
        </div>
      </div>

      {/* Main 3-Pane Review Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Pane: Review Queue */}
        <div className="w-80 border-r border-atlas-border-default overflow-y-auto shrink-0 bg-atlas-surface-0">
          <div className="border-b border-atlas-border-default p-2 text-xs font-semibold text-atlas-text-secondary uppercase tracking-wider">
            Review Queue ({reviews.length})
          </div>
          <ResearchReviewQueue
            reviews={reviews}
            selectedReviewId={selectedReviewId}
            onSelectReview={onSelectReview}
            isLoading={isReviewsLoading}
          />
        </div>

        {/* Center Pane: Review Request Detail & Quality Gates */}
        <div className="flex-1 overflow-hidden bg-atlas-surface-1">
          <ResearchReviewDetail
            review={currentReview}
            qualityGateResult={qualityGateResult}
            isQualityGateRunning={isQualityGateRunning}
            onRunQualityGate={onRunQualityGate}
            onDecideReview={onDecideReview}
            onCancelReview={onCancelReview}
            onOpenParticipants={() => setIsParticipantsOpen(true)}
            onOpenCirculation={() => setIsCirculationOpen(true)}
          />
        </div>

        {/* Right Pane: Anchored Comment Sidebar */}
        {currentReview && (
          <ResearchCommentSidebar
            threads={comments}
            resourceType={currentReview.target_type}
            resourceId={currentReview.target_id}
            currentRevisionNumber={currentReview.target_revision_number}
            isLoading={isCommentsLoading}
            onAddThread={(data) =>
              onAddCommentThread(currentReview.target_type, currentReview.target_id, data)
            }
            onAddReply={onAddCommentReply}
            onResolveThread={onResolveCommentThread}
            onReopenThread={onReopenCommentThread}
          />
        )}
      </div>

      {/* Modals & Dialogs */}
      <NewReviewDialog
        isOpen={isNewReviewOpen}
        onClose={() => setIsNewReviewOpen(false)}
        availableReports={availableReports}
        onSubmitReview={onSubmitReview}
      />

      {currentReview && (
        <>
          <ResearchParticipantsModal
            isOpen={isParticipantsOpen}
            onClose={() => setIsParticipantsOpen(false)}
            resourceType={currentReview.target_type}
            resourceId={currentReview.target_id}
            participants={participants}
            isLoading={isParticipantsLoading}
            onGrantParticipant={(data) =>
              onGrantParticipant(currentReview.target_type, currentReview.target_id, data)
            }
            onUpdateParticipant={onUpdateParticipant}
            onRevokeParticipant={onRevokeParticipant}
          />

          <ResearchCirculationDialog
            isOpen={isCirculationOpen}
            onClose={() => setIsCirculationOpen(false)}
            reportId={currentReview.target_id}
            revisionNumber={currentReview.target_revision_number}
            isApproved={currentReview.status === "APPROVED"}
            circulations={circulations}
            isLoading={isCirculationsLoading}
            onCirculate={(data) => onCirculateReport(currentReview.target_id, data)}
            onRevokeCirculation={onRevokeCirculation}
          />
        </>
      )}
    </div>
  );
}
