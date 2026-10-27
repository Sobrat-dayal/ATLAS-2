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
  ResearchInvestmentThesis,
  ResearchThesisArgument,
  CreateResearchReportDTO,
  UpdateResearchReportDTO,
  FinalizeResearchReportDTO,
  CreateReportSectionDTO,
  UpdateReportSectionDTO,
  ReorderReportSectionsDTO,
  VerifyReportDTO,
  CreateReportExportDTO,
  CreateThesisDTO,
  UpdateThesisDTO,
  CreateThesisArgumentDTO,
  ReportLifecycleStatus,
  ResearchReportType,
  ReportSectionType,
  ResearchReportContentBlock,
} from "@/lib/research/types";
import { ResearchReportsList } from "./ResearchReportsList";
import { ResearchReportStudio } from "./ResearchReportStudio";
import { ResearchThesisWorkspace } from "./ResearchThesisWorkspace";
import { NewResearchReportDialog } from "./NewResearchReportDialog";
import { NewThesisDialog } from "./NewThesisDialog";

interface ResearchReportsWorkspaceProps {
  // Reports State
  reports: ResearchReport[];
  reportsTotal: number;
  isReportsLoading: boolean;
  selectedReportId: string | null;
  currentReport: ResearchReport | null;
  reportSections: ResearchReportSection[];
  selectedSectionId: string | null;
  reportTemplates: ResearchReportTemplate[];
  reportRevisions: ResearchReportRevision[];
  verificationResult: ResearchReportVerification | null;
  isVerifying: boolean;
  reportExports: ResearchReportExport[];
  reportStatusFilter?: ReportLifecycleStatus;
  onStatusFilterChange: (st?: ReportLifecycleStatus) => void;
  reportTypeFilter?: ResearchReportType;
  onTypeFilterChange: (tp?: ResearchReportType) => void;
  reportSearchQuery: string;
  onReportSearchChange: (q: string) => void;

  // Theses State
  theses: ResearchInvestmentThesis[];
  selectedThesisId: string | null;
  currentThesis: ResearchInvestmentThesis | null;
  thesisArguments: ResearchThesisArgument[];
  isThesesLoading: boolean;

  // Actions
  onSelectReport: (id: string | null) => void;
  onCreateReport: (data: CreateResearchReportDTO) => Promise<any>;
  onUpdateReport: (reportId: string, data: UpdateResearchReportDTO) => Promise<any>;
  onFinalizeReport: (reportId: string, data: FinalizeResearchReportDTO) => Promise<any>;
  onDeleteReport: (reportId: string) => Promise<any>;
  onSelectSection: (sectionId: string) => void;
  onCreateSection: (reportId: string, data: CreateReportSectionDTO) => Promise<any>;
  onUpdateSection: (sectionId: string, data: UpdateReportSectionDTO) => Promise<any>;
  onDeleteSection: (sectionId: string) => Promise<any>;
  onReorderSections: (reportId: string, data: ReorderReportSectionsDTO) => Promise<any>;
  onVerifyReport: (reportId: string, data?: VerifyReportDTO) => Promise<any>;
  onCompareRevisions: (reportId: string, baseRev: number, targetRev: number) => Promise<any>;
  onCreateExport: (reportId: string, data: CreateReportExportDTO) => Promise<any>;

  onSelectThesis: (id: string | null) => void;
  onCreateThesis: (data: CreateThesisDTO) => Promise<any>;
  onUpdateThesis: (thesisId: string, data: UpdateThesisDTO) => Promise<any>;
  onDeleteThesis: (thesisId: string) => Promise<any>;
  onCreateThesisArgument: (thesisId: string, data: CreateThesisArgumentDTO) => Promise<any>;
  onDeleteThesisArgument: (argumentId: string) => Promise<any>;

  onOpenSource?: (sourceId: string) => void;
}

export function ResearchReportsWorkspace({
  reports,
  reportsTotal,
  isReportsLoading,
  selectedReportId,
  currentReport,
  reportSections,
  selectedSectionId,
  reportTemplates,
  reportRevisions,
  verificationResult,
  isVerifying,
  reportExports,
  reportStatusFilter,
  onStatusFilterChange,
  reportTypeFilter,
  onTypeFilterChange,
  reportSearchQuery,
  onReportSearchChange,

  theses,
  selectedThesisId,
  currentThesis,
  thesisArguments,
  isThesesLoading,

  onSelectReport,
  onCreateReport,
  onUpdateReport,
  onFinalizeReport,
  onDeleteReport,
  onSelectSection,
  onCreateSection,
  onUpdateSection,
  onDeleteSection,
  onReorderSections,
  onVerifyReport,
  onCompareRevisions,
  onCreateExport,

  onSelectThesis,
  onCreateThesis,
  onUpdateThesis,
  onDeleteThesis,
  onCreateThesisArgument,
  onDeleteThesisArgument,

  onOpenSource,
}: ResearchReportsWorkspaceProps) {
  const [activeSubView, setActiveSubView] = useState<"REPORTS" | "THESES">("REPORTS");
  const [isNewReportOpen, setIsNewReportOpen] = useState(false);
  const [isNewThesisOpen, setIsNewThesisOpen] = useState(false);

  // If inside an active report, render the 3-pane studio
  if (selectedReportId && currentReport) {
    return (
      <ResearchReportStudio
        report={currentReport}
        sections={reportSections}
        selectedSectionId={selectedSectionId}
        onSelectSection={onSelectSection}
        templates={reportTemplates}
        revisions={reportRevisions}
        verification={verificationResult}
        isVerifying={isVerifying}
        exports={reportExports}
        onBack={() => onSelectReport(null)}
        onUpdateReport={async (title) => {
          await onUpdateReport(currentReport.report_id, {
            expected_revision: currentReport.revision,
            title,
          });
        }}
        onFinalizeReport={async () => {
          await onFinalizeReport(currentReport.report_id, {
            expected_revision: currentReport.revision,
            publication_notes: "Certified for publication",
          });
        }}
        onCreateSection={async (title, sectionType) => {
          await onCreateSection(currentReport.report_id, {
            title,
            section_type: sectionType,
            order_index: reportSections.length,
          });
        }}
        onUpdateSection={async (sectionId, title, blocks, expectedRev) => {
          await onUpdateSection(sectionId, {
            expected_revision: expectedRev,
            title,
            blocks,
          });
        }}
        onDeleteSection={async (sectionId) => {
          await onDeleteSection(sectionId);
        }}
        onMoveSection={async (sectionId, direction) => {
          const sorted = [...reportSections].sort((a, b) => a.order_index - b.order_index);
          const idx = sorted.findIndex((s) => s.section_id === sectionId);
          if (idx === -1) return;
          const targetIdx = direction === "up" ? idx - 1 : idx + 1;
          if (targetIdx < 0 || targetIdx >= sorted.length) return;
          const item = sorted.splice(idx, 1)[0];
          sorted.splice(targetIdx, 0, item);
          const orderedIds = sorted.map((s) => s.section_id);
          await onReorderSections(currentReport.report_id, {
            ordered_section_ids: orderedIds,
          });
        }}
        onVerify={async () => {
          await onVerifyReport(currentReport.report_id);
        }}
        onCompareRevisions={async (baseRev, targetRev) => {
          return onCompareRevisions(currentReport.report_id, baseRev, targetRev);
        }}
        onExport={async (data) => {
          return onCreateExport(currentReport.report_id, data);
        }}
        onOpenSource={onOpenSource}
      />
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Sub-view Nav Header */}
      <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2 shrink-0">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveSubView("REPORTS")}
            className={`rounded-xs px-3 py-1 text-xs font-semibold transition-colors ${
              activeSubView === "REPORTS"
                ? "bg-atlas-surface-0 text-atlas-text-primary shadow-xs border border-atlas-border-default"
                : "text-atlas-text-secondary hover:text-atlas-text-primary"
            }`}
          >
            Analyst Research Reports ({reportsTotal})
          </button>
          <button
            onClick={() => setActiveSubView("THESES")}
            className={`rounded-xs px-3 py-1 text-xs font-semibold transition-colors ${
              activeSubView === "THESES"
                ? "bg-atlas-surface-0 text-atlas-text-primary shadow-xs border border-atlas-border-default"
                : "text-atlas-text-secondary hover:text-atlas-text-primary"
            }`}
          >
            Investment Theses ({theses.length})
          </button>
        </div>

        <div className="flex items-center gap-2">
          {activeSubView === "REPORTS" ? (
            <Button variant="primary" size="xs" onClick={() => setIsNewReportOpen(true)}>
              + New Research Report
            </Button>
          ) : (
            <Button variant="primary" size="xs" onClick={() => setIsNewThesisOpen(true)}>
              + New Investment Thesis
            </Button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        {activeSubView === "REPORTS" ? (
          <ResearchReportsList
            reports={reports}
            isLoading={isReportsLoading}
            searchQuery={reportSearchQuery}
            onSearchChange={onReportSearchChange}
            statusFilter={reportStatusFilter}
            onStatusFilterChange={onStatusFilterChange}
            typeFilter={reportTypeFilter}
            onTypeFilterChange={onTypeFilterChange}
            onSelectReport={(id) => onSelectReport(id)}
            onNewReport={() => setIsNewReportOpen(true)}
            onDeleteReport={onDeleteReport}
          />
        ) : (
          <ResearchThesisWorkspace
            theses={theses}
            selectedThesisId={selectedThesisId}
            currentThesis={currentThesis}
            argumentsList={thesisArguments}
            isLoading={isThesesLoading}
            onSelectThesis={onSelectThesis}
            onNewThesis={() => setIsNewThesisOpen(true)}
            onDeleteThesis={onDeleteThesis}
            onCreateArgument={onCreateThesisArgument}
            onDeleteArgument={onDeleteThesisArgument}
            onOpenSource={onOpenSource}
          />
        )}
      </div>

      {/* Modals */}
      <NewResearchReportDialog
        isOpen={isNewReportOpen}
        templates={reportTemplates}
        onClose={() => setIsNewReportOpen(false)}
        onSubmit={async (data) => {
          await onCreateReport(data);
        }}
      />

      <NewThesisDialog
        isOpen={isNewThesisOpen}
        onClose={() => setIsNewThesisOpen(false)}
        onSubmit={async (data) => {
          await onCreateThesis(data);
        }}
      />
    </div>
  );
}
