"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  CreateRevalidationRequest,
  ResearchRevalidationResultResponse,
} from "@/lib/research/types";
import { getRevalidationOutcomeDisplay, formatResearchDate } from "@/lib/research/formatting";

interface ResearchRevalidationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (request: CreateRevalidationRequest) => Promise<ResearchRevalidationResultResponse>;
  defaultTargetType?: string;
  defaultTargetId?: string;
}

export function ResearchRevalidationDialog({
  isOpen,
  onClose,
  onSubmit,
  defaultTargetType = "REPORT",
  defaultTargetId = "",
}: ResearchRevalidationDialogProps) {
  const [targetType, setTargetType] = useState<string>(defaultTargetType);
  const [targetId, setTargetId] = useState<string>(defaultTargetId);
  const [revisionNumber, setRevisionNumber] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ResearchRevalidationResultResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleExecute = async () => {
    if (!targetId.trim()) {
      setErrorMessage("Target ID is required.");
      return;
    }
    setErrorMessage(null);
    setIsLoading(true);
    try {
      const res = await onSubmit({
        target_type: targetType,
        target_id: targetId.trim(),
        target_revision_number: revisionNumber ? parseInt(revisionNumber, 10) : null,
      });
      setResult(res);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Revalidation failed.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="flex flex-col w-full max-w-lg max-h-[85vh] rounded-sm border border-atlas-border-default bg-atlas-surface-0 shadow-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-3 shrink-0">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-atlas-text-primary">
              Automated Research Revalidation
            </h3>
            <p className="text-[11px] text-atlas-text-muted">
              Verify citation integrity, upstream source changes, and approval revision status.
            </p>
          </div>
          <Button variant="ghost" size="xs" onClick={onClose}>
            ✕
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {errorMessage && (
            <div className="p-3 text-xs bg-atlas-negative/10 border border-atlas-negative/30 text-atlas-negative rounded-sm">
              {errorMessage}
            </div>
          )}

          {!result ? (
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1">
                  Target Resource Type
                </label>
                <select
                  value={targetType}
                  onChange={(e) => setTargetType(e.target.value)}
                  className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent"
                >
                  <option value="REPORT">REPORT (Research Report)</option>
                  <option value="ANALYSIS">ANALYSIS (Quantitative Analysis)</option>
                  <option value="FINDING">FINDING (Empirical Finding)</option>
                  <option value="THESIS">THESIS (Investment Thesis)</option>
                </select>
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1">
                  Target Resource ID
                </label>
                <input
                  type="text"
                  value={targetId}
                  onChange={(e) => setTargetId(e.target.value)}
                  placeholder="e.g. rep-apple-services-expansion-fy24"
                  className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent font-mono"
                />
              </div>

              <div>
                <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1">
                  Target Revision Number (Optional)
                </label>
                <input
                  type="number"
                  value={revisionNumber}
                  onChange={(e) => setRevisionNumber(e.target.value)}
                  placeholder="Leave blank for latest active revision"
                  className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-1 px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent font-mono"
                />
              </div>
            </div>
          ) : (
            /* Results View */
            <div className="space-y-4 text-xs">
              <div className="p-3 bg-atlas-surface-1 rounded-sm border border-atlas-border-default space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase text-atlas-text-muted">Revalidation Outcome</span>
                  <Badge variant={getRevalidationOutcomeDisplay(result.outcome).variant} className="text-[10px]">
                    {getRevalidationOutcomeDisplay(result.outcome).label}
                  </Badge>
                </div>
                <div className="flex items-center justify-between font-mono">
                  <span className="text-atlas-text-muted">Target:</span>
                  <span className="text-atlas-text-primary">{result.target_type}/{result.target_id} (rev {result.target_revision_number})</span>
                </div>
                <div className="flex items-center justify-between font-mono">
                  <span className="text-atlas-text-muted">Executed At:</span>
                  <span className="text-atlas-text-secondary">{formatResearchDate(result.executed_at)}</span>
                </div>
              </div>

              <div>
                <div className="text-[11px] font-bold uppercase tracking-wider text-atlas-text-muted mb-2">
                  Validation Issues & Observations ({result.issues.length})
                </div>
                {result.issues.length === 0 ? (
                  <div className="p-3 text-center text-xs text-atlas-positive bg-atlas-positive/10 border border-atlas-positive/20 rounded-sm">
                    ✓ All citations, source references, and approval versions are completely valid.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {result.issues.map((iss) => (
                      <div
                        key={iss.issue_id}
                        className="p-2.5 rounded-sm border border-atlas-border-default bg-atlas-surface-1 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <Badge
                            variant={
                              iss.severity === "BLOCKING"
                                ? "negative"
                                : iss.severity === "WARNING"
                                ? "warning"
                                : "outline"
                            }
                            className="text-[9px]"
                          >
                            {iss.severity}: {iss.issue_type}
                          </Badge>
                          {iss.target_reference && (
                            <span className="font-mono text-[10px] text-atlas-text-muted">
                              {iss.target_reference}
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-atlas-text-primary leading-relaxed">
                          {iss.message}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-atlas-border-default bg-atlas-surface-1 px-4 py-3 shrink-0">
          {!result ? (
            <>
              <Button variant="ghost" size="xs" onClick={onClose}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="xs"
                onClick={handleExecute}
                disabled={isLoading || !targetId.trim()}
              >
                {isLoading ? "Executing Revalidation..." : "Run Revalidation"}
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="xs" onClick={handleReset}>
                ← Validate Another
              </Button>
              <Button variant="primary" size="xs" onClick={onClose}>
                Done
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

