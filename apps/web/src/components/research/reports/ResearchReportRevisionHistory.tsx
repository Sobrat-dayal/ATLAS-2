"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import { ResearchReportRevision } from "@/lib/research/types";
import { formatResearchDate } from "@/lib/research/formatting";

interface ResearchReportRevisionHistoryProps {
  reportId: string;
  revisions: ResearchReportRevision[];
  onCompareRevisions: (baseRev: number, targetRev: number) => Promise<any>;
}

export function ResearchReportRevisionHistory({
  reportId,
  revisions,
  onCompareRevisions,
}: ResearchReportRevisionHistoryProps) {
  const [baseRev, setBaseRev] = useState<number>(revisions.length > 1 ? revisions[revisions.length - 1].revision_number : 1);
  const [targetRev, setTargetRev] = useState<number>(revisions.length > 0 ? revisions[0].revision_number : 1);
  const [diffResult, setDiffResult] = useState<any | null>(null);
  const [isComparing, setIsComparing] = useState(false);

  const handleCompare = async () => {
    setIsComparing(true);
    try {
      const res = await onCompareRevisions(baseRev, targetRev);
      setDiffResult(res);
    } finally {
      setIsComparing(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-atlas-surface-0 border-l border-atlas-border-default overflow-hidden">
      <div className="border-b border-atlas-border-default bg-atlas-surface-1 px-3 py-2.5">
        <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider block">
          Revision History & Audit Log
        </span>
        <span className="text-[10px] text-atlas-text-muted">
          Immutable point-in-time document states
        </span>
      </div>

      {/* Compare Selector Bar */}
      <div className="p-3 border-b border-atlas-border-default bg-atlas-surface-1/40 space-y-2">
        <span className="text-[10px] font-semibold text-atlas-text-secondary uppercase">
          Compare Revisions
        </span>
        <div className="flex items-center gap-2">
          <select
            value={baseRev}
            onChange={(e) => setBaseRev(Number(e.target.value))}
            className="flex-1 rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-secondary font-mono"
          >
            {revisions.map((r) => (
              <option key={r.revision_number} value={r.revision_number}>
                Base: r{r.revision_number}
              </option>
            ))}
          </select>
          <span className="text-xs text-atlas-text-muted">vs</span>
          <select
            value={targetRev}
            onChange={(e) => setTargetRev(Number(e.target.value))}
            className="flex-1 rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-secondary font-mono"
          >
            {revisions.map((r) => (
              <option key={r.revision_number} value={r.revision_number}>
                Target: r{r.revision_number}
              </option>
            ))}
          </select>
          <Button
            variant="secondary"
            size="xs"
            disabled={isComparing || baseRev === targetRev}
            onClick={handleCompare}
          >
            {isComparing ? "..." : "Diff"}
          </Button>
        </div>
      </div>

      {/* Diff Result if generated */}
      {diffResult && (
        <div className="p-3 border-b border-atlas-border-default bg-atlas-surface-1 text-xs space-y-1.5 max-h-48 overflow-y-auto">
          <div className="flex items-center justify-between font-mono text-[10px] text-atlas-text-muted">
            <span>Diff Summary (r{diffResult.base_revision} → r{diffResult.target_revision})</span>
            <button
              onClick={() => setDiffResult(null)}
              className="text-atlas-text-muted hover:text-atlas-text-primary"
            >
              ✕
            </button>
          </div>
          <div className="grid grid-cols-3 gap-1 font-mono text-[10px] text-center">
            <div className="p-1 bg-atlas-surface-0 border border-atlas-border-default rounded-xs">
              <span className="text-atlas-text-muted block">Modified Secs</span>
              <span className="font-bold text-atlas-accent">
                {diffResult.modified_sections?.length || 0}
              </span>
            </div>
            <div className="p-1 bg-atlas-surface-0 border border-atlas-border-default rounded-xs">
              <span className="text-atlas-text-muted block">Added Secs</span>
              <span className="font-bold text-atlas-positive">
                {diffResult.added_sections?.length || 0}
              </span>
            </div>
            <div className="p-1 bg-atlas-surface-0 border border-atlas-border-default rounded-xs">
              <span className="text-atlas-text-muted block">Removed Secs</span>
              <span className="font-bold text-atlas-negative">
                {diffResult.removed_sections?.length || 0}
              </span>
            </div>
          </div>
          {diffResult.metadata_diff && Object.keys(diffResult.metadata_diff).length > 0 && (
            <div className="text-[10px] text-atlas-text-muted font-mono pt-1">
              Title / Header metadata changed between revisions.
            </div>
          )}
        </div>
      )}

      {/* Revision List */}
      <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-default/40 p-2">
        {revisions.map((rev) => (
          <div key={rev.revision_id} className="p-2 space-y-1 text-xs">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className="font-mono text-[10px]">
                r{rev.revision_number}
              </Badge>
              <span className="font-mono text-[10px] text-atlas-text-muted">
                {formatResearchDate(rev.created_at)}
              </span>
            </div>
            <p className="text-atlas-text-primary text-[11px] font-medium">
              {rev.change_summary || "Document updated and auto-saved."}
            </p>
            <div className="flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
              <span>By: {rev.created_by || rev.author_user_id}</span>
              <span>{rev.word_count || 0} words</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
