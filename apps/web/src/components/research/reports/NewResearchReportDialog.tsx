"use client";

import React, { useState } from "react";
import { Badge, Button, Input } from "@/design-system";
import { CreateResearchReportDTO, ResearchReportTemplate, ResearchReportType } from "@/lib/research/types";

interface NewResearchReportDialogProps {
  isOpen: boolean;
  templates: ResearchReportTemplate[];
  onClose: () => void;
  onSubmit: (data: CreateResearchReportDTO) => Promise<void>;
}

export function NewResearchReportDialog({
  isOpen,
  templates,
  onClose,
  onSubmit,
}: NewResearchReportDialogProps) {
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("tpl-company-research");
  const [title, setTitle] = useState("");
  const [reportType, setReportType] = useState<ResearchReportType>("COMPANY_RESEARCH");
  const [targetEntityId, setTargetEntityId] = useState("");
  const [targetEntityName, setTargetEntityName] = useState("");
  const [primaryAuthor, setPrimaryAuthor] = useState("Lead Equity Analyst");
  const [coAuthors, setCoAuthors] = useState("");
  const [researchCutoff, setResearchCutoff] = useState(new Date().toISOString().split("T")[0]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleTemplateSelect = (tpl: ResearchReportTemplate) => {
    setSelectedTemplateId(tpl.template_id);
    setReportType(tpl.report_type);
    if (!title) {
      setTitle(`${tpl.title} — ${targetEntityName || "Coverage"}`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Report title is required.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const coAuthorsList = coAuthors
        .split(",")
        .map((a) => a.trim())
        .filter(Boolean);

      await onSubmit({
        template_id: selectedTemplateId || undefined,
        title: title.trim(),
        report_type: reportType,
        target_entity_id: targetEntityId.trim() || undefined,
        target_entity_name: targetEntityName.trim() || undefined,
        primary_author: primaryAuthor.trim(),
        co_authors: coAuthorsList,
        research_cutoff: researchCutoff ? `${researchCutoff}T23:59:59Z` : undefined,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to instantiate research report.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
      <div className="w-full max-w-2xl rounded-sm border border-atlas-border-default bg-atlas-surface-0 shadow-xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-3">
          <div>
            <h3 className="text-sm font-bold text-atlas-text-primary">
              CREATE INSTITUTIONAL RESEARCH REPORT
            </h3>
            <p className="text-xs text-atlas-text-muted">
              Select an institutional template with pre-configured governance sections and citation rules.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary text-sm font-mono"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4 overflow-y-auto flex-1">
          {error && (
            <div className="rounded-xs border border-atlas-negative/30 bg-atlas-negative/10 p-2 text-xs text-atlas-negative">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-atlas-text-secondary uppercase tracking-wider mb-2">
              Select Institutional Template
            </label>
            <div className="grid grid-cols-2 gap-2 max-h-44 overflow-y-auto pr-1">
              {templates.map((tpl) => (
                <div
                  key={tpl.template_id}
                  onClick={() => handleTemplateSelect(tpl)}
                  className={`cursor-pointer rounded-xs border p-2.5 transition-colors ${
                    selectedTemplateId === tpl.template_id
                      ? "border-atlas-accent bg-atlas-accent/10"
                      : "border-atlas-border-default bg-atlas-surface-1 hover:border-atlas-border-strong"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-atlas-text-primary">{tpl.title}</span>
                    <Badge variant="outline" className="text-[9px]">
                      {tpl.default_sections?.length || 0} Secs
                    </Badge>
                  </div>
                  <p className="text-[11px] text-atlas-text-muted mt-1 line-clamp-2">
                    {tpl.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Report Title *
              </label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Apple Inc. (AAPL) Q4 Coverage Initiation"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Report Type
              </label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value as ResearchReportType)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                <option value="COMPANY_RESEARCH">Company Research</option>
                <option value="EQUITY_INITIATION">Equity Initiation</option>
                <option value="EARNINGS_REVIEW">Earnings Review</option>
                <option value="MACROECONOMIC_REPORT">Macroeconomic Report</option>
                <option value="INDUSTRY_PRIMER">Industry Primer</option>
                <option value="INVESTMENT_THESIS">Investment Thesis</option>
                <option value="EVENT_MEMO">Event Reaction Memo</option>
                <option value="RISK_BRIEF">Risk Assessment Brief</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Target Entity Ticker / CIK
              </label>
              <Input
                value={targetEntityId}
                onChange={(e) => setTargetEntityId(e.target.value)}
                placeholder="e.g. AAPL or 0000320193"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Target Entity Name
              </label>
              <Input
                value={targetEntityName}
                onChange={(e) => setTargetEntityName(e.target.value)}
                placeholder="e.g. Apple Inc."
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Primary Author
              </label>
              <Input
                value={primaryAuthor}
                onChange={(e) => setPrimaryAuthor(e.target.value)}
                placeholder="Lead Analyst"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Co-Authors (comma-separated)
              </label>
              <Input
                value={coAuthors}
                onChange={(e) => setCoAuthors(e.target.value)}
                placeholder="e.g. J. Doe, A. Smith"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-atlas-text-secondary mb-1">
                Research Cutoff (As-Of Date)
              </label>
              <Input
                type="date"
                value={researchCutoff}
                onChange={(e) => setResearchCutoff(e.target.value)}
              />
            </div>
          </div>

          <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2.5 text-[11px] text-atlas-text-muted">
            <span className="font-semibold text-atlas-text-secondary">Point-in-Time Cutoff Policy:</span>{" "}
            All embedded financial metrics, analysis runs, and cited sources must be dated on or prior to the research cutoff date. Look-ahead data will be flagged by automated verification.
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-atlas-border-default">
            <Button variant="secondary" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Create Report"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
