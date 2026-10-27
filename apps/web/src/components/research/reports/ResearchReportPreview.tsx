"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import { ResearchReport, ResearchReportSection } from "@/lib/research/types";
import { formatResearchDate, getReportTypeDisplay } from "@/lib/research/formatting";

interface ResearchReportPreviewProps {
  report: ResearchReport;
  sections: ResearchReportSection[];
  onClose: () => void;
  onExport: () => void;
}

export function ResearchReportPreview({
  report,
  sections,
  onClose,
  onExport,
}: ResearchReportPreviewProps) {
  const sortedSections = [...sections].sort((a, b) => a.order_index - b.order_index);

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-atlas-surface-0 overflow-hidden">
      {/* Top Preview Toolbar */}
      <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2.5 shrink-0">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="xs" onClick={onClose}>
            ← Back to Studio
          </Button>
          <div className="h-4 w-px bg-atlas-border-default" />
          <span className="text-xs font-bold text-atlas-text-primary">
            DOCUMENT PREVIEW MODE
          </span>
          <Badge variant="outline" className="font-mono text-[10px]">
            r{report.revision} • {report.status}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="primary" size="sm" onClick={onExport}>
            Export PDF / DOCX
          </Button>
        </div>
      </div>

      {/* Document Sheet Layout */}
      <div className="flex-1 overflow-y-auto p-8 bg-atlas-surface-2 flex justify-center">
        <div className="w-full max-w-4xl bg-atlas-surface-0 border border-atlas-border-default shadow-lg p-10 min-h-[1100px] text-atlas-text-primary space-y-8 font-serif">
          {/* Header Banner */}
          <div className="border-b-2 border-atlas-accent pb-6 font-sans">
            <div className="flex items-center justify-between text-xs text-atlas-text-muted mb-2 font-mono uppercase tracking-wider">
              <span>ATLAS INSTITUTIONAL RESEARCH</span>
              <span>{getReportTypeDisplay(report.report_type)}</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-atlas-text-primary mb-3">
              {report.title}
            </h1>
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-atlas-text-secondary pt-2 border-t border-atlas-border-default/60 font-mono">
              <div>
                <span>Target: </span>
                <span className="font-bold text-atlas-text-primary">
                  {report.target_entity_name || "General Market"}
                </span>{" "}
                {report.target_entity_id && `(${report.target_entity_id})`}
              </div>
              <div>
                <span>Author: </span>
                <span className="font-bold text-atlas-text-primary">{report.primary_author}</span>
                {report.co_authors && report.co_authors.length > 0 && (
                  <span>, {report.co_authors.join(", ")}</span>
                )}
              </div>
              <div>
                <span>As-Of Cutoff: </span>
                <span className="font-bold text-atlas-text-primary">
                  {formatResearchDate(report.research_cutoff)}
                </span>
              </div>
            </div>
          </div>

          {/* Sections Loop */}
          <div className="space-y-8">
            {sortedSections.map((sec, sIdx) => (
              <section key={sec.section_id} className="space-y-4">
                <h2 className="text-lg font-bold font-sans text-atlas-text-primary border-b border-atlas-border-default pb-1 flex items-center gap-2">
                  <span className="font-mono text-sm text-atlas-accent">{sIdx + 1}.</span>
                  <span>{sec.title}</span>
                </h2>

                <div className="space-y-4 text-xs font-serif leading-relaxed text-atlas-text-primary/95">
                  {(sec.blocks || []).map((blk) => (
                    <div key={blk.block_id} className="space-y-2">
                      {blk.block_type === "HEADING_2" ? (
                        <h3 className="text-sm font-bold font-sans text-atlas-text-primary pt-2">
                          {blk.text_content}
                        </h3>
                      ) : blk.block_type === "HEADING_3" ? (
                        <h4 className="text-xs font-semibold font-sans text-atlas-text-secondary pt-1">
                          {blk.text_content}
                        </h4>
                      ) : blk.block_type === "PARAGRAPH" ? (
                        <p className="whitespace-pre-line">
                          {blk.text_content}
                          {blk.citation_ids && blk.citation_ids.length > 0 && (
                            <span className="font-sans font-mono text-[10px] text-atlas-accent ml-1">
                              [{blk.citation_ids.join(", ")}]
                            </span>
                          )}
                        </p>
                      ) : blk.block_type === "QUOTE" ? (
                        <blockquote className="border-l-2 border-atlas-accent pl-4 py-1 italic font-serif text-atlas-text-secondary">
                          "{blk.text_content}"
                        </blockquote>
                      ) : blk.block_type === "FINANCIAL_TABLE" && blk.table_content ? (
                        <div className="overflow-x-auto border border-atlas-border-default rounded-xs bg-atlas-surface-0 font-sans my-3">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead className="bg-atlas-surface-1 border-b border-atlas-border-default font-mono text-[11px] text-atlas-text-secondary">
                              <tr>
                                {blk.table_content.columns.map((c, i) => (
                                  <th key={i} className="py-2 px-3">
                                    {c}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-atlas-border-default font-mono text-[11px]">
                              {blk.table_content.rows.map((row, rIdx) => (
                                <tr key={rIdx}>
                                  {row.map((cell, cIdx) => (
                                    <td key={cIdx} className="py-1.5 px-3">
                                      {cell}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : blk.block_type === "CHART" ? (
                        <div className="border border-atlas-border-default rounded-xs bg-atlas-surface-1/40 p-4 font-sans my-3">
                          <div className="text-xs font-bold text-atlas-text-primary mb-2">
                            {blk.chart_spec?.series_name || "Quantitative Analysis Chart"}
                          </div>
                          <div className="flex items-end justify-around h-24 gap-3 px-6 bg-atlas-surface-0 rounded-xs border border-atlas-border-default p-2">
                            {(blk.chart_spec?.data_points || []).map((dp: any, i: number) => (
                              <div key={i} className="flex flex-col items-center gap-1 flex-1">
                                <div
                                  className="w-full bg-atlas-accent rounded-t-xs"
                                  style={{
                                    height: `${Math.min(100, Math.max(15, dp.value * 2.5))}%`,
                                  }}
                                />
                                <span className="font-mono text-[9px] text-atlas-text-muted">
                                  {dp.period}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </section>
            ))}
          </div>

          {/* Institutional Compliance Disclaimer */}
          <div className="border-t-2 border-atlas-border-default pt-6 font-sans text-[10px] text-atlas-text-muted space-y-2">
            <span className="font-bold uppercase tracking-wider block text-atlas-text-secondary">
              IMPORTANT REGULATORY DISCLOSURES & RESEARCH CERTIFICATIONS
            </span>
            <p className="leading-relaxed">
              This institutional research report has been prepared for institutional and qualified clients solely for informational and analytical purposes. It does not constitute an offer, solicitation, or recommendation to buy or sell any security, derivative, or financial instrument. Past performance is not indicative of future results. All statements of fact are derived from verified regulatory filings (SEC Forms 10-K, 10-Q, 8-K) and macroeconomic statistical releases. Opinions, estimates, and projections reflect the author's judgment as of the research cutoff date and are subject to change without notice.
            </p>
            <div className="flex items-center justify-between pt-2 border-t border-atlas-border-default/40 font-mono text-[9px]">
              <span>ATLAS FINANCIAL RESEARCH PLATFORM</span>
              <span>POINT-IN-TIME REVISION r{report.revision}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
