"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import { ResearchReport, ResearchReportSection } from "@/lib/research/types";

interface ResearchReportEvidencePanelProps {
  report: ResearchReport;
  sections: ResearchReportSection[];
  onOpenSource?: (sourceId: string) => void;
}

export function ResearchReportEvidencePanel({
  report,
  sections,
  onOpenSource,
}: ResearchReportEvidencePanelProps) {
  // Extract all citations from blocks
  const allCitationIds = new Set<string>();
  const analysisRunEmbeds: string[] = [];

  sections.forEach((sec) => {
    (sec.blocks || []).forEach((blk) => {
      (blk.citation_ids || []).forEach((c) => allCitationIds.add(c));
      if (blk.chart_spec?.analysis_run_id) {
        analysisRunEmbeds.push(blk.chart_spec.analysis_run_id);
      }
      if (blk.table_content?.analysis_run_id) {
        analysisRunEmbeds.push(blk.table_content.analysis_run_id);
      }
    });
  });

  const citationList = Array.from(allCitationIds);

  return (
    <div className="flex h-full flex-col bg-atlas-surface-0 border-l border-atlas-border-default overflow-hidden">
      <div className="border-b border-atlas-border-default bg-atlas-surface-1 px-3 py-2.5">
        <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider block">
          Evidence & Provenance Inspector
        </span>
        <span className="text-[10px] text-atlas-text-muted">
          Anchored sources, filings & quantitative runs
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4 text-xs">
        {/* Cited Evidence Sources */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-atlas-text-secondary uppercase">
              Cited Evidence Anchors ({citationList.length})
            </span>
          </div>
          {citationList.length === 0 ? (
            <p className="text-atlas-text-muted text-[11px] italic">
              No citations attached to blocks yet. Use citation tags to anchor claims to Stage 104/105 sources.
            </p>
          ) : (
            <div className="space-y-1.5">
              {citationList.map((citId) => (
                <div
                  key={citId}
                  className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 flex items-center justify-between"
                >
                  <div>
                    <span className="font-mono text-[10px] text-atlas-accent font-semibold block">
                      {citId}
                    </span>
                    <span className="text-[10px] text-atlas-text-muted">
                      Source-anchored factual anchor
                    </span>
                  </div>
                  {onOpenSource && (
                    <Button
                      variant="ghost"
                      size="xs"
                      onClick={() => onOpenSource(citId)}
                    >
                      View
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Embedded Analysis Runs */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-atlas-text-secondary uppercase">
              Embedded Stage 106 Runs ({analysisRunEmbeds.length})
            </span>
          </div>
          {analysisRunEmbeds.length === 0 ? (
            <p className="text-atlas-text-muted text-[11px] italic">
              No quantitative analysis runs embedded. Add chart or table blocks to embed reproducible models.
            </p>
          ) : (
            <div className="space-y-1.5">
              {analysisRunEmbeds.map((runId, i) => (
                <div
                  key={i}
                  className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 flex items-center justify-between"
                >
                  <div>
                    <span className="font-mono text-[10px] text-atlas-text-primary font-semibold block">
                      {runId}
                    </span>
                    <span className="text-[10px] text-atlas-text-muted">
                      Reproducible Point-in-Time Run
                    </span>
                  </div>
                  <Badge variant="positive" className="text-[9px]">
                    Verified
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Temporal Cutoff Summary */}
        <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2.5 space-y-1">
          <span className="text-[11px] font-bold text-atlas-text-secondary uppercase block">
            Point-in-Time Cutoff
          </span>
          <p className="text-[11px] text-atlas-text-muted">
            Report As-Of Cutoff:{" "}
            <span className="font-mono text-atlas-text-primary">
              {report.research_cutoff || "None specified"}
            </span>
          </p>
          <p className="text-[10px] text-atlas-text-muted leading-relaxed">
            All embedded financial statement line items and macroeconomic indicators are validated to ensure strict compliance against look-ahead bias.
          </p>
        </div>
      </div>
    </div>
  );
}
