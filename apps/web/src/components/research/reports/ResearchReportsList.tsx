"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import { ResearchReport, ReportLifecycleStatus, ResearchReportType } from "@/lib/research/types";
import { formatResearchDate, getReportStatusDisplay, getReportTypeDisplay } from "@/lib/research/formatting";

interface ResearchReportsListProps {
  reports: ResearchReport[];
  isLoading: boolean;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  statusFilter?: ReportLifecycleStatus;
  onStatusFilterChange: (st?: ReportLifecycleStatus) => void;
  typeFilter?: ResearchReportType;
  onTypeFilterChange: (tp?: ResearchReportType) => void;
  onSelectReport: (reportId: string) => void;
  onNewReport: () => void;
  onDeleteReport: (reportId: string) => void;
}

export function ResearchReportsList({
  reports,
  isLoading,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  typeFilter,
  onTypeFilterChange,
  onSelectReport,
  onNewReport,
  onDeleteReport,
}: ResearchReportsListProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Search and Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-2.5">
        <div className="flex items-center gap-2 flex-1 max-w-xl">
          <input
            type="text"
            placeholder="Search reports by title, entity, or author..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-3 py-1.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-hidden"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={statusFilter || ""}
            onChange={(e) =>
              onStatusFilterChange(
                e.target.value ? (e.target.value as ReportLifecycleStatus) : undefined
              )
            }
            className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1.5 text-xs text-atlas-text-secondary focus:border-atlas-accent focus:outline-hidden"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="FINALIZED">Finalized</option>
            <option value="PUBLISHED">Published</option>
            <option value="SUPERSEDED">Superseded</option>
            <option value="ARCHIVED">Archived</option>
          </select>

          <select
            value={typeFilter || ""}
            onChange={(e) =>
              onTypeFilterChange(
                e.target.value ? (e.target.value as ResearchReportType) : undefined
              )
            }
            className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1.5 text-xs text-atlas-text-secondary focus:border-atlas-accent focus:outline-hidden"
          >
            <option value="">All Report Types</option>
            <option value="COMPANY_RESEARCH">Company Research</option>
            <option value="EQUITY_INITIATION">Equity Initiation</option>
            <option value="EARNINGS_REVIEW">Earnings Review</option>
            <option value="MACROECONOMIC_REPORT">Macroeconomic Report</option>
            <option value="INDUSTRY_PRIMER">Industry Primer</option>
            <option value="INVESTMENT_THESIS">Investment Thesis</option>
            <option value="EVENT_MEMO">Event Reaction Memo</option>
            <option value="RISK_BRIEF">Risk Assessment Brief</option>
          </select>

          <Button variant="primary" size="sm" onClick={onNewReport}>
            + New Report
          </Button>
        </div>
      </div>

      {/* Reports Table */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-xs text-atlas-text-muted">
            Loading research reports...
          </div>
        ) : reports.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-center px-4">
            <p className="text-sm font-semibold text-atlas-text-primary mb-1">
              No Research Reports Found
            </p>
            <p className="text-xs text-atlas-text-muted max-w-md mb-4">
              Create an institutional research report from pre-configured coverage templates with claim-to-evidence validation.
            </p>
            <Button variant="primary" size="sm" onClick={onNewReport}>
              + Create First Report
            </Button>
          </div>
        ) : (
          <table className="w-full border-collapse text-left text-xs">
            <thead className="sticky top-0 border-b border-atlas-border-default bg-atlas-surface-1 text-atlas-text-secondary">
              <tr>
                <th className="py-2.5 px-4 font-semibold uppercase tracking-wider text-[11px]">
                  Report Title & Target
                </th>
                <th className="py-2.5 px-3 font-semibold uppercase tracking-wider text-[11px]">
                  Type
                </th>
                <th className="py-2.5 px-3 font-semibold uppercase tracking-wider text-[11px]">
                  Status
                </th>
                <th className="py-2.5 px-3 font-semibold uppercase tracking-wider text-[11px]">
                  Author
                </th>
                <th className="py-2.5 px-3 font-semibold uppercase tracking-wider text-[11px]">
                  Cutoff (As-Of)
                </th>
                <th className="py-2.5 px-3 font-semibold uppercase tracking-wider text-[11px]">
                  Rev
                </th>
                <th className="py-2.5 px-3 font-semibold uppercase tracking-wider text-[11px]">
                  Updated
                </th>
                <th className="py-2.5 px-4 font-semibold uppercase tracking-wider text-[11px] text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/60">
              {reports.map((report) => {
                const statusMeta = getReportStatusDisplay(report.status);
                return (
                  <tr
                    key={report.report_id}
                    className="hover:bg-atlas-surface-1/50 transition-colors cursor-pointer group"
                    onClick={() => onSelectReport(report.report_id)}
                  >
                    <td className="py-3 px-4">
                      <div className="font-semibold text-atlas-text-primary group-hover:text-atlas-accent transition-colors">
                        {report.title}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5 text-[11px] text-atlas-text-muted">
                        {report.target_entity_name ? (
                          <span>
                            {report.target_entity_name}{" "}
                            {report.target_entity_id && (
                              <span className="font-mono text-atlas-text-secondary">
                                ({report.target_entity_id})
                              </span>
                            )}
                          </span>
                        ) : (
                          <span>General Analysis</span>
                        )}
                        <span>•</span>
                        <span>{report.section_count || 0} Sections</span>
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      <span className="text-atlas-text-secondary">
                        {getReportTypeDisplay(report.report_type)}
                      </span>
                    </td>

                    <td className="py-3 px-3">
                      <Badge variant={statusMeta.variant} className="text-[10px]">
                        {statusMeta.label}
                      </Badge>
                    </td>

                    <td className="py-3 px-3 text-atlas-text-secondary">
                      {report.primary_author}
                    </td>

                    <td className="py-3 px-3 font-mono text-atlas-text-muted text-[11px]">
                      {formatResearchDate(report.research_cutoff)}
                    </td>

                    <td className="py-3 px-3 font-mono text-atlas-text-muted text-[11px]">
                      r{report.revision}
                    </td>

                    <td className="py-3 px-3 font-mono text-atlas-text-muted text-[11px]">
                      {formatResearchDate(report.updated_at)}
                    </td>

                    <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-1.5">
                        <Button
                          variant="ghost"
                          size="xs"
                          onClick={() => onSelectReport(report.report_id)}
                        >
                          Open Studio
                        </Button>
                        <Button
                          variant="ghost"
                          size="xs"
                          className="text-atlas-negative hover:text-atlas-negative/80"
                          onClick={() => {
                            if (window.confirm(`Delete report "${report.title}"?`)) {
                              onDeleteReport(report.report_id);
                            }
                          }}
                        >
                          Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
