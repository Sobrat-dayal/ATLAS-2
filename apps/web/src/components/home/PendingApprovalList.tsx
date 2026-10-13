"use client";

import React from "react";
import { AlertCircle, RotateCcw, ShieldCheck } from "lucide-react";
import { ApprovalItem, ApprovalStatusFilter } from "@/lib/approvals/types";
import { PendingApprovalRow } from "./PendingApprovalRow";

interface PendingApprovalListProps {
  approvals: ApprovalItem[];
  statusFilter: ApprovalStatusFilter;
  onFilterChange: (filter: ApprovalStatusFilter) => void;
  isLoading: boolean;
  isLoadingMore: boolean;
  isError: boolean;
  error: Error | null;
  hasMore: boolean;
  onRetry: () => void;
  onLoadMore: () => void;
  onReview: (approval: ApprovalItem) => void;
}

export function PendingApprovalList({
  approvals,
  statusFilter,
  onFilterChange,
  isLoading,
  isLoadingMore,
  isError,
  error,
  hasMore,
  onRetry,
  onLoadMore,
  onReview,
}: PendingApprovalListProps) {
  const filterOptions: { label: string; value: ApprovalStatusFilter }[] = [
    { label: "Pending", value: "PENDING" },
    { label: "Approved", value: "APPROVED" },
    { label: "Rejected", value: "REJECTED" },
    { label: "Expired", value: "EXPIRED" },
    { label: "All", value: "ALL" },
  ];

  return (
    <div className="flex flex-col gap-3">
      {/* Sub-header Filter Tabs */}
      <div className="flex items-center justify-between gap-2 border-b border-atlas-border-subtle pb-2">
        <div className="flex items-center gap-1" role="tablist" aria-label="Approval status filters">
          {filterOptions.map((opt) => {
            const isActive = statusFilter === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                role="tab"
                aria-selected={isActive}
                onClick={() => onFilterChange(opt.value)}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                  isActive
                    ? "bg-atlas-surface-3 text-atlas-text-primary shadow-xs"
                    : "text-atlas-text-muted hover:text-atlas-text-secondary hover:bg-atlas-surface-2"
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Loading Skeletons */}
      {isLoading && (
        <div className="space-y-2 py-2" aria-label="Loading approval requests">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="h-14 rounded border border-atlas-border-subtle bg-atlas-surface-2/40 animate-pulse"
            />
          ))}
        </div>
      )}

      {/* Error State */}
      {!isLoading && isError && (
        <div className="p-3 rounded border border-atlas-error/30 bg-atlas-error/10 text-xs text-atlas-error flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
            <span>{error?.message || "Failed to load approval requests."}</span>
          </div>
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1 px-2 py-1 rounded bg-atlas-error/20 hover:bg-atlas-error/30 text-atlas-error text-[11px] font-medium transition-colors"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Truthful Empty State (Section 51 & 140) */}
      {!isLoading && !isError && approvals.length === 0 && (
        <div className="py-6 px-4 text-center rounded border border-dashed border-atlas-border-subtle bg-atlas-surface-2/20 flex flex-col items-center justify-center">
          <ShieldCheck className="h-6 w-6 text-atlas-text-muted mb-2 stroke-[1.5]" aria-hidden="true" />
          <p className="text-xs font-medium text-atlas-text-primary">
            {statusFilter === "PENDING" ? "No pending approvals." : "No approval requests found."}
          </p>
          <p className="text-[11px] text-atlas-text-muted mt-0.5 max-w-xs">
            {statusFilter === "PENDING"
              ? "When trusted ATLAS subsystems require explicit human decisions, requests appear here."
              : `No approval records match the ${statusFilter.toLowerCase()} filter.`}
          </p>
        </div>
      )}

      {/* Approval Rows */}
      {!isLoading && !isError && approvals.length > 0 && (
        <div className="space-y-2">
          {approvals.map((approval) => (
            <PendingApprovalRow
              key={approval.approval_id}
              approval={approval}
              onReview={onReview}
            />
          ))}

          {/* Load More Button */}
          {hasMore && (
            <div className="pt-2 text-center">
              <button
                type="button"
                onClick={onLoadMore}
                disabled={isLoadingMore}
                className="px-3 py-1 rounded text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors focus-visible:outline-none disabled:opacity-50"
              >
                {isLoadingMore ? "Loading..." : "Load More Requests"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
