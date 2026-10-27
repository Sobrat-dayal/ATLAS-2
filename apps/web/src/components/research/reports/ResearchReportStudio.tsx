"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchReport,
  ResearchReportSection,
  ResearchReportTemplate,
  ResearchReportRevision,
  ResearchReportVerification,
  ResearchReportExport,
  ReportSectionType,
  ResearchReportContentBlock,
  CreateReportExportDTO,
} from "@/lib/research/types";
import { getReportStatusDisplay, getReportTypeDisplay } from "@/lib/research/formatting";
import { ResearchReportOutline } from "./ResearchReportOutline";
import { ResearchReportEditor } from "./ResearchReportEditor";
import { ResearchReportEvidencePanel } from "./ResearchReportEvidencePanel";
import { ResearchReportVerificationPanel } from "./ResearchReportVerificationPanel";
import { ResearchReportRevisionHistory } from "./ResearchReportRevisionHistory";
import { ResearchReportPreview } from "./ResearchReportPreview";
import { ResearchReportExportDialog } from "./ResearchReportExportDialog";

interface ResearchReportStudioProps {
  report: ResearchReport;
  sections: ResearchReportSection[];
  selectedSectionId: string | null;
  onSelectSection: (sectionId: string) => void;
  templates: ResearchReportTemplate[];
  revisions: ResearchReportRevision[];
  verification: ResearchReportVerification | null;
  isVerifying: boolean;
  exports: ResearchReportExport[];
  onBack: () => void;
  onUpdateReport: (title: string) => Promise<void>;
  onFinalizeReport: () => Promise<void>;
  onCreateSection: (title: string, sectionType: ReportSectionType) => Promise<void>;
  onUpdateSection: (sectionId: string, title: string, blocks: ResearchReportContentBlock[], expectedRev: number) => Promise<void>;
  onDeleteSection: (sectionId: string) => Promise<void>;
  onMoveSection: (sectionId: string, direction: "up" | "down") => Promise<void>;
  onVerify: () => Promise<void>;
  onCompareRevisions: (baseRev: number, targetRev: number) => Promise<any>;
  onExport: (data: CreateReportExportDTO) => Promise<ResearchReportExport>;
  onOpenSource?: (sourceId: string) => void;
}

export function ResearchReportStudio({
  report,
  sections,
  selectedSectionId,
  onSelectSection,
  templates,
  revisions,
  verification,
  isVerifying,
  exports,
  onBack,
  onUpdateReport,
  onFinalizeReport,
  onCreateSection,
  onUpdateSection,
  onDeleteSection,
  onMoveSection,
  onVerify,
  onCompareRevisions,
  onExport,
  onOpenSource,
}: ResearchReportStudioProps) {
  const [rightPanel, setRightPanel] = useState<"VERIFICATION" | "EVIDENCE" | "REVISIONS">("VERIFICATION");
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [isExportDialogOpen, setIsExportDialogOpen] = useState(false);

  const activeSection = sections.find((s) => s.section_id === selectedSectionId) || (sections.length > 0 ? sections[0] : null);
  const statusMeta = getReportStatusDisplay(report.status);
  const isFinalized = report.status === "FINALIZED" || report.status === "PUBLISHED";

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Studio Header Bar */}
      <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2.5 shrink-0">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="xs" onClick={onBack}>
            ← All Reports
          </Button>
          <div className="h-4 w-px bg-atlas-border-default" />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-atlas-text-primary">{report.title}</span>
              <Badge variant={statusMeta.variant} className="text-[10px]">
                {statusMeta.label}
              </Badge>
              <Badge variant="outline" className="text-[10px] font-mono">
                r{report.revision}
              </Badge>
            </div>
            <div className="text-[10px] text-atlas-text-muted flex items-center gap-2 mt-0.5">
              <span>{getReportTypeDisplay(report.report_type)}</span>
              <span>•</span>
              <span>Target: {report.target_entity_name || "General Coverage"}</span>
              <span>•</span>
              <span>Author: {report.primary_author}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Right Panel Switcher */}
          <div className="flex items-center rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-0.5 mr-2">
            <button
              onClick={() => setRightPanel("VERIFICATION")}
              className={`rounded-xs px-2.5 py-1 text-[11px] font-medium transition-colors ${
                rightPanel === "VERIFICATION"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Verification {verification && (verification.is_valid ? "✓" : "⚠")}
            </button>
            <button
              onClick={() => setRightPanel("EVIDENCE")}
              className={`rounded-xs px-2.5 py-1 text-[11px] font-medium transition-colors ${
                rightPanel === "EVIDENCE"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Evidence
            </button>
            <button
              onClick={() => setRightPanel("REVISIONS")}
              className={`rounded-xs px-2.5 py-1 text-[11px] font-medium transition-colors ${
                rightPanel === "REVISIONS"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              History ({revisions.length})
            </button>
          </div>

          <Button variant="secondary" size="sm" onClick={() => setIsPreviewOpen(true)}>
            Document Preview
          </Button>
          <Button variant="primary" size="sm" onClick={() => setIsExportDialogOpen(true)}>
            Export PDF / DOCX
          </Button>
        </div>
      </div>

      {/* 3-Pane Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Outline */}
        <ResearchReportOutline
          sections={sections}
          selectedSectionId={activeSection?.section_id || null}
          onSelectSection={onSelectSection}
          onAddSection={onCreateSection}
          onDeleteSection={onDeleteSection}
          onMoveSection={onMoveSection}
          isFinalized={isFinalized}
        />

        {/* Center: Editor */}
        <ResearchReportEditor
          section={activeSection}
          onUpdateSection={onUpdateSection}
          isFinalized={isFinalized}
        />

        {/* Right: Inspector */}
        <div className="w-80 shrink-0 border-l border-atlas-border-default bg-atlas-surface-0 flex flex-col overflow-hidden">
          {rightPanel === "VERIFICATION" ? (
            <ResearchReportVerificationPanel
              reportId={report.report_id}
              verification={verification}
              isVerifying={isVerifying}
              onVerify={onVerify}
              onFinalize={onFinalizeReport}
              isFinalized={isFinalized}
            />
          ) : rightPanel === "EVIDENCE" ? (
            <ResearchReportEvidencePanel
              report={report}
              sections={sections}
              onOpenSource={onOpenSource}
            />
          ) : (
            <ResearchReportRevisionHistory
              reportId={report.report_id}
              revisions={revisions}
              onCompareRevisions={onCompareRevisions}
            />
          )}
        </div>
      </div>

      {/* Preview Fullscreen Overlay */}
      {isPreviewOpen && (
        <ResearchReportPreview
          report={report}
          sections={sections}
          onClose={() => setIsPreviewOpen(false)}
          onExport={() => {
            setIsPreviewOpen(false);
            setIsExportDialogOpen(true);
          }}
        />
      )}

      {/* Export Dialog */}
      <ResearchReportExportDialog
        isOpen={isExportDialogOpen}
        reportId={report.report_id}
        reportTitle={report.title}
        exports={exports}
        onClose={() => setIsExportDialogOpen(false)}
        onExport={onExport}
      />
    </div>
  );
}
