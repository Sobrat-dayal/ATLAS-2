"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import { ResearchReportVerification, VerificationIssue } from "@/lib/research/types";
import { getVerificationSeverityDisplay, formatResearchDate } from "@/lib/research/formatting";

interface ResearchReportVerificationPanelProps {
  reportId: string;
  verification: ResearchReportVerification | null;
  isVerifying: boolean;
  onVerify: () => Promise<void>;
  onFinalize: () => Promise<void>;
  isFinalized?: boolean;
}

export function ResearchReportVerificationPanel({
  reportId,
  verification,
  isVerifying,
  onVerify,
  onFinalize,
  isFinalized = false,
}: ResearchReportVerificationPanelProps) {
  const [isFinalizing, setIsFinalizing] = useState(false);

  const handleFinalize = async () => {
    if (
      !window.confirm(
        "Finalizing this research report will lock all section edits, freeze content blocks into an immutable point-in-time revision, and certify publication readiness. Proceed?"
      )
    ) {
      return;
    }
    setIsFinalizing(true);
    try {
      await onFinalize();
    } finally {
      setIsFinalizing(false);
    }
  };

  return (
    <div
      className="flex h-full flex-col bg-atlas-surface-0 border-l border-atlas-border-default overflow-hidden"
      data-report-id={reportId}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-3 py-2.5">
        <div>
          <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider block">
            Institutional Verification
          </span>
          <span className="text-[10px] text-atlas-text-muted">
            Claim-to-evidence, cutoff timestamp & run validation
          </span>
        </div>
        <Button
          variant="secondary"
          size="xs"
          disabled={isVerifying}
          onClick={onVerify}
        >
          {isVerifying ? "Verifying..." : "Run Verification"}
        </Button>
      </div>

      {/* Verification Status Summary */}
      <div className="p-3 border-b border-atlas-border-default bg-atlas-surface-1/40">
        {verification ? (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-atlas-text-secondary">Audit Status:</span>
              <Badge
                variant={verification.is_valid ? "positive" : "negative"}
                className="text-[10px] font-mono"
              >
                {verification.is_valid ? "CERTIFIED READINESS" : "VIOLATIONS DETECTED"}
              </Badge>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-1.5 text-center">
                <span className="text-atlas-text-muted block text-[10px]">Blocking</span>
                <span className={`font-bold ${verification.blocking_issues_count > 0 ? "text-atlas-negative" : "text-atlas-text-primary"}`}>
                  {verification.blocking_issues_count}
                </span>
              </div>
              <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-1.5 text-center">
                <span className="text-atlas-text-muted block text-[10px]">Warnings</span>
                <span className="font-bold text-atlas-warning">
                  {verification.warnings_count}
                </span>
              </div>
            </div>
            <div className="text-[10px] text-atlas-text-muted font-mono">
              Last Run: {formatResearchDate(verification.verified_at)}
            </div>
          </div>
        ) : (
          <div className="text-center py-2 text-xs text-atlas-text-muted">
            No verification run recorded for this draft.
          </div>
        )}
      </div>

      {/* Finalize Action */}
      {!isFinalized && (
        <div className="p-3 border-b border-atlas-border-default bg-atlas-surface-0">
          <Button
            variant="primary"
            size="sm"
            className="w-full"
            disabled={!verification?.is_valid || isFinalizing}
            onClick={handleFinalize}
          >
            {isFinalizing ? "Finalizing..." : "Certify & Finalize Report"}
          </Button>
          {!verification?.is_valid && (
            <p className="text-[10px] text-atlas-text-muted mt-1 text-center">
              Resolve all blocking issues before publication finalization.
            </p>
          )}
        </div>
      )}

      {/* Issues List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <span className="text-[11px] font-bold text-atlas-text-secondary uppercase tracking-wider block">
          Verification Findings ({verification?.issues?.length || 0})
        </span>

        {(!verification || verification.issues?.length === 0) ? (
          <div className="text-xs text-atlas-text-muted py-4 text-center">
            Zero verification violations detected.
          </div>
        ) : (
          verification.issues.map((issue: VerificationIssue, idx: number) => {
            const sev = getVerificationSeverityDisplay(issue.severity);
            return (
              <div
                key={idx}
                className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs space-y-1"
              >
                <div className="flex items-center justify-between">
                  <Badge variant={sev.variant} className="text-[9px]">
                    {sev.label}
                  </Badge>
                  <span className="font-mono text-[9px] text-atlas-text-muted">
                    {issue.issue_type}
                  </span>
                </div>
                <p className="text-atlas-text-primary text-[11px] leading-tight">
                  {issue.message}
                </p>
                {issue.section_id && (
                  <span className="font-mono text-[9px] text-atlas-text-muted block">
                    Sec: {issue.section_id}
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
