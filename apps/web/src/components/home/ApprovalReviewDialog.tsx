"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldAlert,
  ShieldCheck,
  X,
  XCircle,
} from "lucide-react";
import {
  ApprovalDecisionInput,
  ApprovalDecisionResponse,
  ApprovalDecisionType,
  ApprovalDetail,
  ApprovalItem,
} from "@/lib/approvals/types";

interface ApprovalReviewDialogProps {
  isOpen: boolean;
  onClose: () => void;
  approvalItem: ApprovalItem | null;
  onFetchDetail: (approvalId: string) => Promise<ApprovalDetail>;
  onDecide: (
    approvalId: string,
    input: ApprovalDecisionInput
  ) => Promise<ApprovalDecisionResponse>;
  isDeciding?: boolean;
}

export function ApprovalReviewDialog({
  isOpen,
  onClose,
  approvalItem,
  onFetchDetail,
  onDecide,
  isDeciding = false,
}: ApprovalReviewDialogProps) {
  const [detail, setDetail] = useState<ApprovalDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(true);
  const [reason, setReason] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [decisionSuccess, setDecisionSuccess] = useState<ApprovalDecisionResponse | null>(null);

  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen || !approvalItem) {
      setDetail(null);
      setReason("");
      setErrorMsg(null);
      setDecisionSuccess(null);
      return;
    }

    setLoadingDetail(true);
    setErrorMsg(null);
    setDecisionSuccess(null);

    onFetchDetail(approvalItem.approval_id)
      .then((res) => {
        setDetail(res);
        setLoadingDetail(false);
      })
      .catch((err) => {
        setErrorMsg(err instanceof Error ? err.message : String(err));
        setLoadingDetail(false);
      });
  }, [isOpen, approvalItem, onFetchDetail]);

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !approvalItem) return null;

  const currentItem = detail || approvalItem;
  const isPending = currentItem.status === "PENDING";
  const isExpired = currentItem.is_expired;
  const isDecided = currentItem.status === "APPROVED" || currentItem.status === "REJECTED";
  const canDecide = isPending && !isExpired && !decisionSuccess;

  const handleDecision = async (decisionType: ApprovalDecisionType) => {
    if (!canDecide || isDeciding) return;
    setErrorMsg(null);

    try {
      const res = await onDecide(currentItem.approval_id, {
        decision: decisionType,
        reason: reason.trim() || null,
        expected_version: currentItem.version,
      });
      setDecisionSuccess(res);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : String(err));
    }
  };

  const formatTimestamp = (isoString?: string | null) => {
    if (!isoString) return "—";
    try {
      const d = new Date(isoString);
      return d.toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="approval-review-dialog-title"
    >
      <div
        ref={dialogRef}
        className="relative w-full max-w-xl p-5 rounded-lg border border-atlas-border-strong bg-atlas-surface-1 shadow-2xl animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle shrink-0">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-amber-400" aria-hidden="true" />
            <h2
              id="approval-review-dialog-title"
              className="text-sm font-semibold text-atlas-text-primary"
            >
              Approval Request Review
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
            aria-label="Close dialog"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Scrollable Content Body */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4 text-xs pr-1">
          {/* Success Banner */}
          {decisionSuccess && (
            <div className="p-3 rounded bg-atlas-teal/15 border border-atlas-teal/30 text-atlas-teal flex items-start gap-2.5">
              <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">
                  Decision Recorded: {decisionSuccess.decision}
                </p>
                <p className="text-[11px] text-atlas-text-secondary mt-0.5">
                  {decisionSuccess.message}
                </p>
                <p className="text-[10px] text-atlas-text-muted mt-1 font-mono">
                  Recorded at {formatTimestamp(decisionSuccess.decided_at)}
                </p>
              </div>
            </div>
          )}

          {/* Error Banner */}
          {errorMsg && (
            <div className="p-3 rounded bg-atlas-error/10 border border-atlas-error/30 text-atlas-error flex items-start gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Critical Security Box: Section 8 & Section 142 */}
          <div className="p-3 rounded bg-atlas-surface-2 border border-atlas-border-subtle">
            <div className="flex items-start gap-2">
              <ShieldCheck className="h-4 w-4 text-atlas-teal shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-atlas-text-primary text-[11px] uppercase tracking-wider">
                  Important Architectural Safeguard
                </h3>
                <p className="text-[11px] text-atlas-text-secondary mt-0.5">
                  Your decision will be recorded as a durable audit entry.{" "}
                  <strong className="text-atlas-text-primary">
                    It does not execute the proposed action automatically.
                  </strong>
                </p>
              </div>
            </div>
          </div>

          {/* Request Header & Description */}
          <div>
            <h4 className="text-sm font-medium text-atlas-text-primary">
              {currentItem.title}
            </h4>
            <p className="text-atlas-text-secondary mt-1 whitespace-pre-wrap leading-relaxed">
              {currentItem.summary}
            </p>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-2.5 p-3 rounded bg-atlas-surface-2/60 border border-atlas-border-subtle text-[11px]">
            <div>
              <span className="text-atlas-text-muted block">Trusted Origin:</span>
              <span className="font-mono font-medium text-atlas-text-primary">
                {currentItem.producer_key}
              </span>
            </div>
            <div>
              <span className="text-atlas-text-muted block">Action Category:</span>
              <span className="font-mono font-medium text-atlas-text-primary">
                {currentItem.action_kind}
              </span>
            </div>
            <div>
              <span className="text-atlas-text-muted block">Proposal Reference:</span>
              <span className="font-mono text-atlas-text-secondary truncate block" title={currentItem.proposal_reference}>
                {currentItem.proposal_reference}
              </span>
            </div>
            <div>
              <span className="text-atlas-text-muted block">Status:</span>
              <span
                className={`font-semibold ${
                  currentItem.status === "APPROVED"
                    ? "text-atlas-teal"
                    : currentItem.status === "REJECTED"
                    ? "text-atlas-error"
                    : currentItem.is_expired
                    ? "text-atlas-text-muted"
                    : "text-amber-400"
                }`}
              >
                {currentItem.display_status}
              </span>
            </div>
            <div>
              <span className="text-atlas-text-muted block">Requested:</span>
              <span className="text-atlas-text-secondary">
                {formatTimestamp(currentItem.requested_at)}
              </span>
            </div>
            <div>
              <span className="text-atlas-text-muted block">Expires At:</span>
              <span
                className={`text-atlas-text-secondary ${
                  currentItem.is_expired ? "text-atlas-error font-medium" : ""
                }`}
              >
                {formatTimestamp(currentItem.expires_at)}
                {currentItem.is_expired && " (Expired)"}
              </span>
            </div>
          </div>

          {/* Proposal Digest (SHA-256) */}
          {detail?.proposal_digest && (
            <div className="p-2.5 rounded bg-atlas-surface-3/50 border border-atlas-border-subtle text-[10px] font-mono">
              <span className="text-atlas-text-muted block mb-0.5">Proposal Binding Digest (SHA-256):</span>
              <span className="text-atlas-text-secondary break-all">
                {detail.proposal_digest}
              </span>
            </div>
          )}

          {/* Decision Record (if decided already) */}
          {detail?.decision_record && (
            <div className="p-3 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-[11px]">
              <span className="text-atlas-text-muted block font-medium uppercase tracking-wider mb-1">
                Recorded Decision Audit Record:
              </span>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-atlas-text-primary">
                  {detail.decision_record.decision}
                </span>
                <span className="text-atlas-text-muted">at</span>
                <span className="text-atlas-text-secondary">
                  {formatTimestamp(detail.decision_record.decided_at)}
                </span>
              </div>
              {detail.decision_record.reason && (
                <p className="text-atlas-text-secondary mt-1 italic">
                  &ldquo;{detail.decision_record.reason}&rdquo;
                </p>
              )}
            </div>
          )}

          {/* Reason input for pending items */}
          {canDecide && (
            <div>
              <label
                htmlFor="approval-decision-reason"
                className="block font-medium text-atlas-text-secondary mb-1"
              >
                Decision Reason / Notes (optional, max 500 chars)
              </label>
              <textarea
                id="approval-decision-reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                maxLength={500}
                rows={2}
                placeholder="Enter justification or context for audit record..."
                className="w-full px-3 py-1.5 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-atlas-text-primary placeholder:text-atlas-text-muted/60 focus:outline-none focus:border-atlas-teal transition-colors resize-none"
              />
              <div className="text-[10px] text-atlas-text-muted text-right mt-0.5">
                {reason.length}/500
              </div>
            </div>
          )}

          {/* Expired warning if expired */}
          {isPending && isExpired && (
            <div className="p-3 rounded bg-atlas-surface-2 border border-atlas-border-subtle text-atlas-text-muted flex items-center gap-2">
              <Clock className="h-4 w-4 shrink-0 text-atlas-text-muted" />
              <span>
                This request has expired and is no longer eligible for human decision.
              </span>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-3 border-t border-atlas-border-subtle shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors focus-visible:outline-none"
          >
            {decisionSuccess ? "Done" : "Close"}
          </button>

          {canDecide && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleDecision("REJECT")}
                disabled={isDeciding}
                className="px-3.5 py-1.5 rounded bg-atlas-error/15 text-atlas-error border border-atlas-error/30 font-medium hover:bg-atlas-error/25 transition-colors focus-visible:outline-none disabled:opacity-50"
              >
                {isDeciding ? "Recording..." : "Reject"}
              </button>
              <button
                type="button"
                onClick={() => handleDecision("APPROVE")}
                disabled={isDeciding}
                className="px-4 py-1.5 rounded bg-atlas-teal text-white font-medium hover:bg-atlas-teal/90 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal disabled:opacity-50"
              >
                {isDeciding ? "Recording..." : "Approve"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
