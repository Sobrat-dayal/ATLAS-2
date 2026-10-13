"use client";

import React from "react";
import { Clock, Eye, ShieldAlert, ShieldCheck } from "lucide-react";
import { ApprovalItem } from "@/lib/approvals/types";

interface PendingApprovalRowProps {
  approval: ApprovalItem;
  onReview: (approval: ApprovalItem) => void;
}

export function PendingApprovalRow({
  approval,
  onReview,
}: PendingApprovalRowProps) {
  const isPending = approval.status === "PENDING";
  const isExpired = approval.is_expired;

  // Format expiration cleanly
  const formatExpiration = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="flex items-start justify-between gap-3 p-2.5 rounded border border-atlas-border-subtle bg-atlas-surface-card hover:border-atlas-border-strong hover:bg-atlas-surface-hover transition-colors">
      <div className="flex-1 min-w-0">
        {/* Top Badges */}
        <div className="flex flex-wrap items-center gap-1.5 text-[10px] mb-1 font-mono">
          <span className="px-1.5 py-0.5 rounded bg-atlas-surface-3 text-atlas-text-secondary border border-atlas-border-subtle">
            {approval.producer_key}
          </span>
          <span className="px-1.5 py-0.5 rounded bg-atlas-surface-3 text-atlas-text-primary border border-atlas-border-subtle">
            {approval.action_kind}
          </span>

          {/* Status / Expiration Badge */}
          {isPending && !isExpired && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-sans">
              <Clock className="h-2.5 w-2.5" />
              <span>Expires {formatExpiration(approval.expires_at)}</span>
            </span>
          )}

          {isPending && isExpired && (
            <span className="px-1.5 py-0.5 rounded bg-atlas-error/15 text-atlas-error border border-atlas-error/30 font-sans font-medium">
              Expired
            </span>
          )}

          {approval.status === "APPROVED" && (
            <span className="px-1.5 py-0.5 rounded bg-atlas-teal/15 text-atlas-teal border border-atlas-teal/30 font-sans font-medium">
              Approved
            </span>
          )}

          {approval.status === "REJECTED" && (
            <span className="px-1.5 py-0.5 rounded bg-atlas-error/15 text-atlas-error border border-atlas-error/30 font-sans font-medium">
              Rejected
            </span>
          )}
        </div>

        {/* Title */}
        <h4 className="text-xs font-medium text-atlas-text-primary truncate">
          {approval.title}
        </h4>

        {/* Summary preview */}
        <p className="text-[11px] text-atlas-text-secondary mt-0.5 line-clamp-1">
          {approval.summary}
        </p>
      </div>

      {/* Review Button */}
      <div className="shrink-0 self-center">
        <button
          type="button"
          onClick={() => onReview(approval)}
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-atlas-surface-2 hover:bg-atlas-surface-3 border border-atlas-border-subtle hover:border-atlas-border-strong text-atlas-text-primary text-[11px] font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
        >
          <Eye className="h-3 w-3 text-atlas-text-secondary" aria-hidden="true" />
          <span>Review</span>
        </button>
      </div>
    </div>
  );
}
