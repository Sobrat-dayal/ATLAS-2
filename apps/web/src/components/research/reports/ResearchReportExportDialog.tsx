"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import { CreateReportExportDTO, ExportFormat, ResearchReportExport } from "@/lib/research/types";
import { formatResearchDate, getExportFormatDisplay } from "@/lib/research/formatting";

interface ResearchReportExportDialogProps {
  isOpen: boolean;
  reportId: string;
  reportTitle: string;
  exports: ResearchReportExport[];
  onClose: () => void;
  onExport: (data: CreateReportExportDTO) => Promise<ResearchReportExport>;
}

export function ResearchReportExportDialog({
  isOpen,
  reportId,
  reportTitle,
  exports,
  onClose,
  onExport,
}: ResearchReportExportDialogProps) {
  const [format, setFormat] = useState<ExportFormat>("PDF");
  const [includeDisclosures, setIncludeDisclosures] = useState(true);
  const [includeCitations, setIncludeCitations] = useState(true);
  const [includeCharts, setIncludeCharts] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setIsExporting(true);
    setError(null);
    try {
      await onExport({
        format,
        include_disclosures: includeDisclosures,
        include_citations: includeCitations,
        include_charts: includeCharts,
      });
    } catch (err: any) {
      setError(err.message || "Failed to generate report export.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownload = (exp: ResearchReportExport) => {
    const downloadUrl = `/api/v1/research/exports/${exp.export_id}/download`;
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = exp.file_name || `${reportTitle}.${exp.format.toLowerCase()}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
      <div className="w-full max-w-xl rounded-sm border border-atlas-border-default bg-atlas-surface-0 shadow-xl overflow-hidden flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-3">
          <div>
            <h3 className="text-sm font-bold text-atlas-text-primary">
              EXPORT INSTITUTIONAL RESEARCH REPORT
            </h3>
            <p className="text-xs text-atlas-text-muted">
              Generate publication-grade PDF, DOCX, or audit archives with mandatory institutional disclaimers.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary text-sm font-mono"
          >
            ✕
          </button>
        </div>

        <div className="p-4 space-y-4 overflow-y-auto flex-1">
          {error && (
            <div className="rounded-xs border border-atlas-negative/30 bg-atlas-negative/10 p-2 text-xs text-atlas-negative">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-atlas-text-secondary uppercase tracking-wider mb-2">
              Export Format
            </label>
            <div className="grid grid-cols-2 gap-2">
              {(["PDF", "DOCX", "HTML", "MARKDOWN", "JSON_ARCHIVE"] as ExportFormat[]).map((fmt) => (
                <div
                  key={fmt}
                  onClick={() => setFormat(fmt)}
                  className={`cursor-pointer rounded-xs border p-2.5 transition-colors ${
                    format === fmt
                      ? "border-atlas-accent bg-atlas-accent/10"
                      : "border-atlas-border-default bg-atlas-surface-1 hover:border-atlas-border-strong"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-atlas-text-primary">
                      {getExportFormatDisplay(fmt)}
                    </span>
                    <Badge variant="outline" className="text-[9px] font-mono">
                      {fmt}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2 border-t border-atlas-border-default pt-3">
            <span className="text-xs font-semibold text-atlas-text-secondary uppercase tracking-wider block">
              Governance & Content Options
            </span>
            <label className="flex items-center gap-2 text-xs text-atlas-text-primary cursor-pointer">
              <input
                type="checkbox"
                checked={includeDisclosures}
                onChange={(e) => setIncludeDisclosures(e.target.checked)}
                className="rounded-xs border-atlas-border-default text-atlas-accent focus:ring-0"
              />
              Include Institutional Disclaimers & Regulatory Notices (Mandatory for external release)
            </label>
            <label className="flex items-center gap-2 text-xs text-atlas-text-primary cursor-pointer">
              <input
                type="checkbox"
                checked={includeCitations}
                onChange={(e) => setIncludeCitations(e.target.checked)}
                className="rounded-xs border-atlas-border-default text-atlas-accent focus:ring-0"
              />
              Include Evidence Citation Table & Filing References
            </label>
            <label className="flex items-center gap-2 text-xs text-atlas-text-primary cursor-pointer">
              <input
                type="checkbox"
                checked={includeCharts}
                onChange={(e) => setIncludeCharts(e.target.checked)}
                className="rounded-xs border-atlas-border-default text-atlas-accent focus:ring-0"
              />
              Embed Stage 106 Analysis Charts and Performance Visualizations
            </label>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-atlas-border-default">
            <Button variant="primary" size="sm" disabled={isExporting} onClick={handleGenerate}>
              {isExporting ? "Generating..." : `Generate ${format}`}
            </Button>
          </div>

          {/* Export Artifacts History */}
          {exports.length > 0 && (
            <div className="border-t border-atlas-border-default pt-3">
              <span className="text-xs font-semibold text-atlas-text-secondary uppercase tracking-wider block mb-2">
                Generated Artifacts ({exports.length})
              </span>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {exports.map((exp) => (
                  <div
                    key={exp.export_id}
                    className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="flex items-center gap-1.5">
                        <Badge variant="outline" className="text-[9px] font-mono">
                          {exp.format}
                        </Badge>
                        <span className="font-semibold text-atlas-text-primary">
                          {exp.file_name}
                        </span>
                      </div>
                      <span className="font-mono text-[10px] text-atlas-text-muted mt-0.5 block">
                        {formatResearchDate(exp.created_at)} • {exp.page_count || 1} pages •{" "}
                        {Math.round((exp.file_size_bytes || 0) / 1024)} KB
                      </span>
                    </div>
                    <Button variant="secondary" size="xs" onClick={() => handleDownload(exp)}>
                      Download
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
