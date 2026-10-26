"use client";

import React from "react";
import { Badge, Button, Input } from "@/design-system";
import {
  InvestigationLifecycleStatus,
  ResearchInvestigation,
  ResearchType,
} from "@/lib/research/types";

interface ResearchInvestigationsTableProps {
  investigations: ResearchInvestigation[];
  isLoading: boolean;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  statusFilter?: InvestigationLifecycleStatus;
  onStatusFilterChange: (status?: InvestigationLifecycleStatus) => void;
  typeFilter?: ResearchType;
  onTypeFilterChange: (type?: ResearchType) => void;
  onSelectInvestigation: (id: string) => void;
  onArchiveInvestigation: (id: string) => void;
  onNewInvestigation: () => void;
}

const STATUS_OPTIONS: { label: string; value?: InvestigationLifecycleStatus }[] = [
  { label: "All Statuses", value: undefined },
  { label: "Draft", value: "DRAFT" },
  { label: "Active", value: "ACTIVE" },
  { label: "On Hold", value: "ON_HOLD" },
  { label: "Completed", value: "COMPLETED" },
  { label: "Archived", value: "ARCHIVED" },
];

const TYPE_OPTIONS: { label: string; value?: ResearchType }[] = [
  { label: "All Research Types", value: undefined },
  { label: "Company Research", value: "COMPANY_RESEARCH" },
  { label: "Security Research", value: "SECURITY_RESEARCH" },
  { label: "Industry Research", value: "INDUSTRY_RESEARCH" },
  { label: "Macroeconomic Research", value: "MACROECONOMIC_RESEARCH" },
  { label: "Market Research", value: "MARKET_RESEARCH" },
  { label: "Financial Event", value: "FINANCIAL_EVENT_RESEARCH" },
  { label: "General Quantitative", value: "GENERAL_FINANCIAL_RESEARCH" },
];

export function ResearchInvestigationsTable({
  investigations,
  isLoading,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  typeFilter,
  onTypeFilterChange,
  onSelectInvestigation,
  onArchiveInvestigation,
  onNewInvestigation,
}: ResearchInvestigationsTableProps) {
  return (
    <div className="flex h-full flex-col p-4">
      {/* Filter and Search Bar */}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2.5 rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-2.5">
        <div className="flex flex-1 flex-wrap items-center gap-2">
          <div className="w-64">
            <Input
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search by title, entity, or thesis..."
              className="h-8 text-xs"
            />
          </div>

          <select
            value={statusFilter || ""}
            onChange={(e) =>
              onStatusFilterChange(
                e.target.value ? (e.target.value as InvestigationLifecycleStatus) : undefined
              )
            }
            className="h-8 rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.label} value={opt.value || ""}>
                {opt.label}
              </option>
            ))}
          </select>

          <select
            value={typeFilter || ""}
            onChange={(e) =>
              onTypeFilterChange(
                e.target.value ? (e.target.value as ResearchType) : undefined
              )
            }
            className="h-8 rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
          >
            {TYPE_OPTIONS.map((opt) => (
              <option key={opt.label} value={opt.value || ""}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <Button variant="primary" size="sm" onClick={onNewInvestigation}>
          + New Investigation
        </Button>
      </div>

      {/* Investigations Table */}
      <div className="flex-1 overflow-auto rounded-sm border border-atlas-border-default bg-atlas-surface-1">
        {isLoading ? (
          <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
            Loading research investigations...
          </div>
        ) : investigations.length === 0 ? (
          <div className="flex h-64 flex-col items-center justify-center space-y-2 text-center text-xs text-atlas-text-muted">
            <p>No research investigations match the selected filters.</p>
            <Button variant="secondary" size="xs" onClick={onNewInvestigation}>
              Create New Investigation
            </Button>
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 z-10 border-b border-atlas-border-default bg-atlas-surface-2 font-mono text-[11px] uppercase tracking-wider text-atlas-text-secondary">
              <tr>
                <th className="px-3 py-2">Investigation Title</th>
                <th className="px-3 py-2">Primary Subject</th>
                <th className="px-3 py-2">Type</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2 text-center">Artifacts</th>
                <th className="px-3 py-2">Revision</th>
                <th className="px-3 py-2">Updated</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default font-normal">
              {investigations.map((inv) => (
                <tr
                  key={inv.investigation_id}
                  className="transition-colors hover:bg-atlas-surface-hover"
                >
                  <td className="px-3 py-2.5">
                    <div
                      onClick={() => onSelectInvestigation(inv.investigation_id)}
                      className="cursor-pointer font-semibold text-atlas-text-primary hover:text-atlas-accent"
                    >
                      {inv.title}
                    </div>
                    {inv.research_objective && (
                      <div className="line-clamp-1 text-[11px] text-atlas-text-muted">
                        {inv.research_objective}
                      </div>
                    )}
                  </td>

                  <td className="px-3 py-2.5 whitespace-nowrap">
                    {inv.primary_subject_entity_id ? (
                      <Badge variant="primary" className="font-mono text-[10px]">
                        {inv.primary_subject_entity_id}
                      </Badge>
                    ) : (
                      <span className="text-atlas-text-muted">—</span>
                    )}
                  </td>

                  <td className="px-3 py-2.5 whitespace-nowrap font-mono text-[11px] text-atlas-text-secondary">
                    {inv.research_type.replace(/_/g, " ")}
                  </td>

                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <Badge
                      variant={
                        inv.status === "ACTIVE"
                          ? "positive"
                          : inv.status === "COMPLETED"
                          ? "default"
                          : inv.status === "ARCHIVED"
                          ? "outline"
                          : "warning"
                      }
                      className="text-[10px]"
                    >
                      {inv.status}
                    </Badge>
                  </td>

                  <td className="px-3 py-2.5 whitespace-nowrap text-center font-mono text-[11px] text-atlas-text-secondary">
                    <span title="Notes" className="text-atlas-text-primary font-bold">{inv.notes_count}n</span> /{" "}
                    <span title="Sources">{inv.sources_count}s</span> /{" "}
                    <span title="Evidence">{inv.evidence_count}e</span>
                  </td>

                  <td className="px-3 py-2.5 whitespace-nowrap font-mono text-[11px] text-atlas-text-muted">
                    v{inv.revision}
                  </td>

                  <td className="px-3 py-2.5 whitespace-nowrap font-mono text-[10px] text-atlas-text-muted">
                    {new Date(inv.updated_at).toLocaleDateString()}
                  </td>

                  <td className="px-3 py-2.5 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button
                        variant="secondary"
                        size="xs"
                        onClick={() => onSelectInvestigation(inv.investigation_id)}
                      >
                        Open Workspace
                      </Button>
                      {inv.status !== "ARCHIVED" && (
                        <Button
                          variant="ghost"
                          size="xs"
                          onClick={() => onArchiveInvestigation(inv.investigation_id)}
                          className="text-atlas-text-muted hover:text-atlas-negative"
                        >
                          Archive
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
