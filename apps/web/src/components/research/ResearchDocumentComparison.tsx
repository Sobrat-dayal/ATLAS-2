"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  DocumentComparisonMode,
  DocumentComparisonResult,
} from "@/lib/research/types";
import {
  formatFinancialDelta,
  formatPercentageDelta,
} from "@/lib/research/formatting";

interface ResearchDocumentComparisonProps {
  leftDocId: string;
  rightDocId: string;
  comparisonMode: DocumentComparisonMode;
  comparisonResult: DocumentComparisonResult | null;
  isLoading: boolean;
  onCompare: (leftId: string, rightId: string, mode: DocumentComparisonMode) => void;
  onOpenDocument: (documentId: string) => void;
}

const COMPARISON_MODES: { label: string; value: DocumentComparisonMode }[] = [
  { label: "Aligned Sections & Diffs", value: "SECTIONS" },
  { label: "Financial Tables & Statement Variance", value: "FINANCIAL_TABLES" },
  { label: "Full Text Document Diff", value: "FULL_TEXT" },
];

const PRESET_COMPARISONS = [
  {
    label: "Apple: FY2024 vs FY2023 Form 10-K",
    left: "0000320193-23-000106",
    right: "0000320193-24-000106",
  },
  {
    label: "Microsoft vs Apple FY2024 Cross-Entity",
    left: "0000320193-24-000106",
    right: "0000950170-24-087843",
  },
];

export function ResearchDocumentComparison({
  leftDocId,
  rightDocId,
  comparisonMode,
  comparisonResult,
  isLoading,
  onCompare,
  onOpenDocument,
}: ResearchDocumentComparisonProps) {
  const [selectedLeft, setSelectedLeft] = useState<string>(leftDocId);
  const [selectedRight, setSelectedRight] = useState<string>(rightDocId);
  const [selectedMode, setSelectedMode] = useState<DocumentComparisonMode>(comparisonMode);
  const [activeTab, setActiveTab] = useState<"FACTS" | "DIFFS">("FACTS");
  const [selectedDiffIndex, setSelectedDiffIndex] = useState<number>(0);

  const handleRunComparison = () => {
    onCompare(selectedLeft, selectedRight, selectedMode);
  };

  const handleApplyPreset = (left: string, right: string) => {
    setSelectedLeft(left);
    setSelectedRight(right);
    onCompare(left, right, selectedMode);
  };

  const activeDiff =
    comparisonResult?.section_diffs &&
    comparisonResult.section_diffs.length > selectedDiffIndex
      ? comparisonResult.section_diffs[selectedDiffIndex]
      : null;

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0 p-4">
      {/* Configuration Header */}
      <div className="mb-3 shrink-0 rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
        <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Multi-Document Comparison & Financial Fact Variance Engine
            </h2>
            <p className="text-[11px] text-atlas-text-muted">
              Side-by-side section text alignment diffs and multi-period mathematical variance calculation.
            </p>
          </div>

          {/* Quick Presets */}
          <div className="flex items-center gap-1.5">
            <span className="text-[10px] uppercase font-bold text-atlas-text-muted">Presets:</span>
            {PRESET_COMPARISONS.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => handleApplyPreset(p.left, p.right)}
                className="rounded-xs border border-atlas-border-default/60 bg-atlas-surface-0 px-2 py-0.5 text-[10px] text-atlas-text-secondary hover:text-atlas-text-primary transition-colors"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Controls */}
        <div className="flex flex-wrap items-center gap-3 pt-1 border-t border-atlas-border-default/60">
          <div className="flex flex-1 items-center gap-2">
            <div className="flex-1">
              <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-0.5">
                Baseline Document (Left):
              </label>
              <input
                type="text"
                value={selectedLeft}
                onChange={(e) => setSelectedLeft(e.target.value)}
                placeholder="Accession or Source ID (e.g. 0000320193-23-000106)"
                className="h-8 w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2.5 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              />
            </div>

            <div className="text-atlas-text-muted text-xs font-bold pt-4">vs</div>

            <div className="flex-1">
              <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-0.5">
                Comparison Document (Right):
              </label>
              <input
                type="text"
                value={selectedRight}
                onChange={(e) => setSelectedRight(e.target.value)}
                placeholder="Accession or Source ID (e.g. 0000320193-24-000106)"
                className="h-8 w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2.5 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              />
            </div>

            <div className="w-52">
              <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-0.5">
                Comparison Mode:
              </label>
              <select
                value={selectedMode}
                onChange={(e) => setSelectedMode(e.target.value as DocumentComparisonMode)}
                className="h-8 w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                {COMPARISON_MODES.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="pt-4">
            <Button
              variant="primary"
              size="sm"
              disabled={isLoading || !selectedLeft || !selectedRight}
              onClick={handleRunComparison}
              className="h-8 px-4 text-xs font-semibold"
            >
              {isLoading ? "Comparing..." : "Execute Comparison"}
            </Button>
          </div>
        </div>
      </div>

      {/* Comparison Result Container */}
      {comparisonResult ? (
        <div className="flex flex-1 flex-col overflow-hidden rounded-sm border border-atlas-border-default bg-atlas-surface-1">
          {/* Result Summary Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default bg-atlas-surface-2 p-3">
            <div className="flex flex-wrap items-center gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-bold text-atlas-text-primary">
                    {comparisonResult.left_title}
                  </h3>
                  <span className="text-atlas-text-muted text-xs">vs</span>
                  <h3 className="text-xs font-bold text-atlas-text-primary">
                    {comparisonResult.right_title}
                  </h3>
                </div>
                <div className="flex items-center gap-2 text-[10px] font-mono text-atlas-text-muted mt-0.5">
                  <span>Periods: {comparisonResult.left_period || "Prior"} → {comparisonResult.right_period || "Current"}</span>
                  <span>• Compared: {new Date(comparisonResult.compared_at).toLocaleTimeString()}</span>
                </div>
              </div>

              <div className="flex items-center gap-1.5">
                <Badge variant="positive" className="font-mono text-[10px]">
                  +{comparisonResult.total_added_lines} lines added
                </Badge>
                <Badge variant="negative" className="font-mono text-[10px]">
                  -{comparisonResult.total_removed_lines} lines removed
                </Badge>
              </div>
            </div>

            {/* View Mode Toggle */}
            <div className="flex rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-0.5">
              <button
                onClick={() => setActiveTab("FACTS")}
                className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                  activeTab === "FACTS"
                    ? "bg-atlas-accent text-white"
                    : "text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                Financial Fact Variance ({comparisonResult.financial_fact_diffs?.length || 0})
              </button>
              <button
                onClick={() => setActiveTab("DIFFS")}
                className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                  activeTab === "DIFFS"
                    ? "bg-atlas-accent text-white"
                    : "text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                Section Text Diffs ({comparisonResult.section_diffs?.length || 0})
              </button>
            </div>
          </div>

          {/* Compatibility Warnings (if any) */}
          {comparisonResult.compatibility_warnings && comparisonResult.compatibility_warnings.length > 0 && (
            <div className="border-b border-atlas-warning/30 bg-atlas-warning/10 px-4 py-2 text-xs text-atlas-warning">
              {comparisonResult.compatibility_warnings.map((w, i) => (
                <div key={i}>⚠️ {w}</div>
              ))}
            </div>
          )}

          {/* Tab 1: Financial Fact Variance Table */}
          {activeTab === "FACTS" && (
            <div className="flex-1 overflow-y-auto p-4">
              {comparisonResult.financial_fact_diffs?.length > 0 ? (
                <div className="overflow-x-auto rounded-sm border border-atlas-border-default bg-atlas-surface-0">
                  <table className="w-full text-left text-xs">
                    <thead className="border-b border-atlas-border-default bg-atlas-surface-2 text-[10px] uppercase font-bold text-atlas-text-muted">
                      <tr>
                        <th className="p-2.5">Financial Concept / Metric</th>
                        <th className="p-2.5 text-right font-mono">
                          {comparisonResult.left_period || "Prior Period"}
                        </th>
                        <th className="p-2.5 text-right font-mono">
                          {comparisonResult.right_period || "Current Period"}
                        </th>
                        <th className="p-2.5 text-right font-mono">Variance (Δ)</th>
                        <th className="p-2.5 text-right font-mono">% Change (%Δ)</th>
                        <th className="p-2.5 text-center">Scale & Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-atlas-border-default/60">
                      {comparisonResult.financial_fact_diffs.map((diff) => {
                        const isPos = diff.absolute_delta > 0;
                        const isNeg = diff.absolute_delta < 0;
                        return (
                          <tr
                            key={diff.fact_key}
                            className="hover:bg-atlas-surface-2/60 transition-colors"
                          >
                            <td className="p-2.5 font-semibold text-atlas-text-primary">
                              {diff.label}
                            </td>
                            <td className="p-2.5 text-right font-mono text-atlas-text-secondary">
                              {new Intl.NumberFormat("en-US").format(diff.left_value)}
                            </td>
                            <td className="p-2.5 text-right font-mono text-atlas-text-primary font-medium">
                              {new Intl.NumberFormat("en-US").format(diff.right_value)}
                            </td>
                            <td
                              className={`p-2.5 text-right font-mono font-semibold ${
                                isPos
                                  ? "text-atlas-positive"
                                  : isNeg
                                  ? "text-atlas-negative"
                                  : "text-atlas-text-secondary"
                              }`}
                            >
                              {formatFinancialDelta(diff.absolute_delta, diff.currency)}
                            </td>
                            <td
                              className={`p-2.5 text-right font-mono font-bold ${
                                isPos
                                  ? "text-atlas-positive"
                                  : isNeg
                                  ? "text-atlas-negative"
                                  : "text-atlas-text-secondary"
                              }`}
                            >
                              {formatPercentageDelta(diff.percentage_delta)}
                            </td>
                            <td className="p-2.5 text-center">
                              <div className="flex items-center justify-center gap-1">
                                <Badge variant="outline" className="font-mono text-[9px]">
                                  {diff.unit_scale}
                                </Badge>
                                {diff.is_restated && (
                                  <Badge variant="warning" className="text-[9px]">
                                    Restated
                                  </Badge>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
                  No standardized financial statement line items were matched for variance comparison.
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Aligned Section Text Diffs */}
          {activeTab === "DIFFS" && (
            <div className="flex flex-1 overflow-hidden">
              {/* Section selector sidebar */}
              <div className="w-64 border-r border-atlas-border-default bg-atlas-surface-0 overflow-y-auto p-2 shrink-0">
                <div className="text-[10px] uppercase font-bold text-atlas-text-muted px-2 py-1 mb-1">
                  Aligned Sections
                </div>
                {comparisonResult.section_diffs?.map((sd, idx) => {
                  const isSelected = selectedDiffIndex === idx;
                  return (
                    <button
                      key={`${sd.section_name}-${idx}`}
                      onClick={() => setSelectedDiffIndex(idx)}
                      className={`w-full text-left rounded-xs p-2 text-xs transition-colors mb-1 ${
                        isSelected
                          ? "bg-atlas-accent/15 border-l-2 border-atlas-accent text-atlas-text-primary font-medium"
                          : "text-atlas-text-secondary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
                      }`}
                    >
                      <div className="font-semibold truncate">{sd.section_name}</div>
                      <div className="flex items-center gap-1.5 text-[10px] font-mono text-atlas-text-muted mt-0.5">
                        <span className="text-atlas-positive">+{sd.added_lines_count}</span>
                        <span className="text-atlas-negative">-{sd.removed_lines_count}</span>
                        <span>• {sd.alignment_status}</span>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Diff unified viewer */}
              <div className="flex-1 overflow-y-auto p-4 bg-atlas-surface-0">
                {activeDiff ? (
                  <div>
                    <div className="mb-3 flex items-center justify-between pb-2 border-b border-atlas-border-default">
                      <div>
                        <h4 className="text-xs font-bold text-atlas-text-primary">
                          {activeDiff.section_name}
                        </h4>
                        <p className="text-[10px] text-atlas-text-muted font-mono">
                          {activeDiff.left_section_heading || "Left Section"} → {activeDiff.right_section_heading || "Right Section"}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="positive" className="font-mono text-[10px]">
                          +{activeDiff.added_lines_count}
                        </Badge>
                        <Badge variant="negative" className="font-mono text-[10px]">
                          -{activeDiff.removed_lines_count}
                        </Badge>
                      </div>
                    </div>

                    {/* Unified Diff Box */}
                    <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-3 font-mono text-xs leading-relaxed overflow-x-auto space-y-0.5">
                      {activeDiff.diff_unified.split("\n").map((line, lIdx) => {
                        const isAdd = line.startsWith("+");
                        const isRem = line.startsWith("-");
                        const isHeader = line.startsWith("@@");
                        return (
                          <div
                            key={lIdx}
                            className={`whitespace-pre px-1 rounded-2xs ${
                              isAdd
                                ? "bg-emerald-950/30 text-emerald-400 font-semibold"
                                : isRem
                                ? "bg-rose-950/30 text-rose-400 font-semibold"
                                : isHeader
                                ? "text-atlas-accent font-bold bg-atlas-surface-2"
                                : "text-atlas-text-secondary"
                            }`}
                          >
                            {line}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
                    Select an aligned section to view text diff.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="flex flex-1 items-center justify-center rounded-sm border border-atlas-border-default bg-atlas-surface-1 text-center p-6">
          <div className="max-w-md">
            <h3 className="text-sm font-semibold text-atlas-text-primary mb-1">
              Select Two Documents to Compare
            </h3>
            <p className="text-xs text-atlas-text-secondary mb-3">
              Atlas will align sections, compute unified text diffs, and calculate normalized financial statement fact variance.
            </p>
            <Button
              variant="primary"
              size="sm"
              disabled={isLoading}
              onClick={handleRunComparison}
            >
              {isLoading ? "Running..." : "Run Default Apple FY24 vs FY23 Comparison"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
