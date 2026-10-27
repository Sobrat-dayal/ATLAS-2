"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import { ResearchReportSection, ReportSectionType } from "@/lib/research/types";

interface ResearchReportOutlineProps {
  sections: ResearchReportSection[];
  selectedSectionId: string | null;
  onSelectSection: (id: string) => void;
  onAddSection: (title: string, sectionType: ReportSectionType) => Promise<void>;
  onDeleteSection: (id: string) => Promise<void>;
  onMoveSection: (id: string, direction: "up" | "down") => Promise<void>;
  isFinalized?: boolean;
}

export function ResearchReportOutline({
  sections,
  selectedSectionId,
  onSelectSection,
  onAddSection,
  onDeleteSection,
  onMoveSection,
  isFinalized = false,
}: ResearchReportOutlineProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newType, setNewType] = useState<ReportSectionType>("METHODOLOGY_AND_DATA");

  const sortedSections = [...sections].sort((a, b) => a.order_index - b.order_index);

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    await onAddSection(newTitle.trim(), newType);
    setNewTitle("");
    setIsAdding(false);
  };

  return (
    <div className="flex h-full flex-col border-r border-atlas-border-default bg-atlas-surface-0 w-64 shrink-0">
      <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-3 py-2">
        <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
          Report Outline
        </span>
        {!isFinalized && !isAdding && (
          <Button variant="ghost" size="xs" onClick={() => setIsAdding(true)}>
            + Section
          </Button>
        )}
      </div>

      {isAdding && (
        <form onSubmit={handleAddSubmit} className="border-b border-atlas-border-default bg-atlas-surface-1 p-2.5 space-y-2">
          <input
            type="text"
            placeholder="Section Title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
            autoFocus
          />
          <select
            value={newType}
            onChange={(e) => setNewType(e.target.value as ReportSectionType)}
            className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-secondary focus:border-atlas-accent focus:outline-hidden"
          >
            <option value="EXECUTIVE_SUMMARY">Executive Summary</option>
            <option value="INVESTMENT_THESIS">Investment Thesis</option>
            <option value="FINANCIAL_PERFORMANCE">Financial Performance</option>
            <option value="VALUATION_FRAMEWORK">Valuation Framework</option>
            <option value="INDUSTRY_DYNAMICS">Industry Dynamics</option>
            <option value="RISK_FACTORS">Risk Factors</option>
            <option value="BULL_BEAR_CASES">Bull / Bear Cases</option>
            <option value="METHODOLOGY_AND_DATA">Methodology & Data</option>
            <option value="CUSTOM">Custom Section</option>
          </select>
          <div className="flex items-center justify-end gap-1.5 pt-1">
            <Button variant="ghost" size="xs" type="button" onClick={() => setIsAdding(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="xs" type="submit">
              Add
            </Button>
          </div>
        </form>
      )}

      <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-default/40">
        {sortedSections.map((sec, index) => {
          const isSelected = sec.section_id === selectedSectionId;
          return (
            <div
              key={sec.section_id}
              onClick={() => onSelectSection(sec.section_id)}
              className={`p-2.5 cursor-pointer transition-colors flex items-center justify-between group ${
                isSelected
                  ? "bg-atlas-accent/10 border-l-2 border-atlas-accent"
                  : "hover:bg-atlas-surface-1"
              }`}
            >
              <div className="flex-1 min-w-0 pr-2">
                <div className="flex items-center gap-1.5">
                  <span className="font-mono text-[10px] text-atlas-text-muted">
                    {index + 1}.
                  </span>
                  <span
                    className={`text-xs truncate font-medium ${
                      isSelected ? "text-atlas-text-primary font-bold" : "text-atlas-text-secondary"
                    }`}
                  >
                    {sec.title}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 mt-1 text-[10px] text-atlas-text-muted">
                  <span className="font-mono">{sec.blocks?.length || 0} blocks</span>
                  {sec.is_mandatory && (
                    <Badge variant="outline" className="text-[9px] px-1 py-0">
                      Req
                    </Badge>
                  )}
                </div>
              </div>

              {!isFinalized && (
                <div
                  className="opacity-0 group-hover:opacity-100 flex items-center gap-0.5 transition-opacity"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    disabled={index === 0}
                    onClick={() => onMoveSection(sec.section_id, "up")}
                    className="p-1 text-atlas-text-muted hover:text-atlas-text-primary disabled:opacity-20 text-[10px]"
                    title="Move Up"
                  >
                    ▲
                  </button>
                  <button
                    disabled={index === sortedSections.length - 1}
                    onClick={() => onMoveSection(sec.section_id, "down")}
                    className="p-1 text-atlas-text-muted hover:text-atlas-text-primary disabled:opacity-20 text-[10px]"
                    title="Move Down"
                  >
                    ▼
                  </button>
                  {!sec.is_mandatory && (
                    <button
                      onClick={() => {
                        if (window.confirm(`Delete section "${sec.title}"?`)) {
                          onDeleteSection(sec.section_id);
                        }
                      }}
                      className="p-1 text-atlas-negative hover:text-atlas-negative/80 text-[10px]"
                      title="Delete Section"
                    >
                      ✕
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
