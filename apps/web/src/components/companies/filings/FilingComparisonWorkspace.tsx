"use client";

import React, { useState } from "react";
import {
  FilingComparisonResponseDTO,
  FilingSummaryDTO,
} from "@/lib/companies/filings";
import {
  GitCompare,
  ArrowRight,
  FileText,
  Layers,
  AlertCircle,
  Plus,
  Minus,
  CheckCircle2,
  Percent,
} from "lucide-react";

interface FilingComparisonWorkspaceProps {
  filings: FilingSummaryDTO[];
  comparison: FilingComparisonResponseDTO | null;
  leftId: string | null;
  rightId: string | null;
  onSetLeftId: (id: string) => void;
  onSetRightId: (id: string) => void;
  onRunComparison: (left?: string, right?: string) => Promise<void>;
  isComparing: boolean;
}

export const FilingComparisonWorkspace: React.FC<FilingComparisonWorkspaceProps> = ({
  filings,
  comparison,
  leftId,
  rightId,
  onSetLeftId,
  onSetRightId,
  onRunComparison,
  isComparing,
}) => {
  const [activeDiffTab, setActiveDiffTab] = useState<"text" | "facts">("text");

  const handleCompareClick = () => {
    if (leftId && rightId) {
      onRunComparison(leftId, rightId);
    }
  };

  const renderDiffLine = (line: string, idx: number) => {
    if (line.startsWith("+")) {
      return (
        <div key={idx} className="bg-emerald-500/10 text-emerald-400 font-mono text-[11px] px-2 py-0.5 border-l-2 border-emerald-500">
          {line}
        </div>
      );
    }
    if (line.startsWith("-")) {
      return (
        <div key={idx} className="bg-rose-500/10 text-rose-400 font-mono text-[11px] px-2 py-0.5 border-l-2 border-rose-500">
          {line}
        </div>
      );
    }
    if (line.startsWith("@@")) {
      return (
        <div key={idx} className="bg-muted/40 text-muted-foreground font-mono text-[10px] px-2 py-0.5">
          {line}
        </div>
      );
    }
    return (
      <div key={idx} className="text-muted-foreground/80 font-mono text-[11px] px-2 py-0.5">
        {line}
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Comparator Selection Bar */}
      <div className="p-3.5 rounded-lg border border-border/60 bg-card/60 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            {/* Left Filing Select */}
            <div>
              <label className="block text-[10px] font-mono uppercase text-muted-foreground mb-1">
                Base / Original Filing
              </label>
              <select
                value={leftId || ""}
                onChange={(e) => onSetLeftId(e.target.value)}
                className="text-xs px-2.5 py-1.5 rounded bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary w-60 sm:w-72"
              >
                <option value="">Select Base Filing...</option>
                {filings.map((f) => (
                  <option key={f.filing_id} value={f.filing_id}>
                    {f.form_type} ({f.reporting_period}) - {f.filing_date}
                  </option>
                ))}
              </select>
            </div>

            <ArrowRight className="w-4 h-4 text-muted-foreground hidden sm:block self-end mb-2" />

            {/* Right Filing Select */}
            <div>
              <label className="block text-[10px] font-mono uppercase text-muted-foreground mb-1">
                Comparative / Amended Filing
              </label>
              <select
                value={rightId || ""}
                onChange={(e) => onSetRightId(e.target.value)}
                className="text-xs px-2.5 py-1.5 rounded bg-background border border-border text-foreground focus:outline-none focus:ring-1 focus:ring-primary w-60 sm:w-72"
              >
                <option value="">Select Comparative Filing...</option>
                {filings.map((f) => (
                  <option key={f.filing_id} value={f.filing_id}>
                    {f.form_type} ({f.reporting_period}) - {f.filing_date}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Compare Button */}
          <button
            type="button"
            onClick={handleCompareClick}
            disabled={!leftId || !rightId || leftId === rightId || isComparing}
            className="self-end px-4 py-1.5 rounded text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors flex items-center gap-1.5 cursor-pointer shadow-sm"
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>{isComparing ? "Analyzing Diffs..." : "Compare Filings"}</span>
          </button>
        </div>

        {leftId === rightId && leftId && (
          <div className="text-[11px] text-amber-400 flex items-center gap-1">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Select two distinct filings to generate comparison diffs.</span>
          </div>
        )}
      </div>

      {/* Comparison Results */}
      {comparison ? (
        <div className="space-y-3">
          {/* Summary Metric Header */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-lg border border-border/60 bg-card/40 font-mono text-xs">
            <div>
              <div className="text-[10px] text-muted-foreground uppercase">Base Accession</div>
              <div className="text-foreground font-semibold truncate mt-0.5">{comparison.left_accession}</div>
              <div className="text-[10px] text-muted-foreground">{comparison.left_filing_date}</div>
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground uppercase">Comparison Accession</div>
              <div className="text-foreground font-semibold truncate mt-0.5">{comparison.right_accession}</div>
              <div className="text-[10px] text-muted-foreground">{comparison.right_filing_date}</div>
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground uppercase">Textual Modifications</div>
              <div className="text-base font-bold text-foreground mt-0.5">
                {comparison.total_text_changes} changes
              </div>
              <div className="text-[10px] text-muted-foreground">
                {comparison.text_diff_sections.length} modified sections
              </div>
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground uppercase">XBRL Fact Variances</div>
              <div className="text-base font-bold text-emerald-400 mt-0.5">
                {comparison.total_fact_adjustments} differences
              </div>
              <div className="text-[10px] text-muted-foreground">
                {comparison.xbrl_fact_diffs.filter((d) => d.is_restatement).length} restatements
              </div>
            </div>
          </div>

          {/* Comparison Mode Subtabs */}
          <div className="flex border-b border-border/60 gap-1 text-xs font-semibold">
            <button
              type="button"
              onClick={() => setActiveDiffTab("text")}
              className={`px-3 py-2 border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
                activeDiffTab === "text"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Section Text Diffs ({comparison.text_diff_sections.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveDiffTab("facts")}
              className={`px-3 py-2 border-b-2 transition-colors flex items-center gap-1.5 cursor-pointer ${
                activeDiffTab === "facts"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>XBRL Fact Variances ({comparison.xbrl_fact_diffs.length})</span>
            </button>
          </div>

          {/* Mode 1: Text Diff Sections */}
          {activeDiffTab === "text" && (
            <div className="space-y-3">
              {comparison.text_diff_sections.map((sec, idx) => (
                <div key={idx} className="rounded-lg border border-border/60 bg-card/40 overflow-hidden">
                  <div className="p-2.5 bg-muted/40 border-b border-border/60 flex items-center justify-between text-xs">
                    <span className="font-semibold text-foreground">{sec.section_name}</span>
                    <div className="flex items-center gap-2 font-mono text-[10px]">
                      <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 flex items-center gap-0.5">
                        <Plus className="w-3 h-3" /> {sec.added_lines_count} lines
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 flex items-center gap-0.5">
                        <Minus className="w-3 h-3" /> {sec.removed_lines_count} lines
                      </span>
                    </div>
                  </div>
                  <div className="p-2 bg-background/95 overflow-x-auto max-h-[400px]">
                    {sec.diff_text.split("\n").map((line, lIdx) => renderDiffLine(line, lIdx))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Mode 2: XBRL Fact Diff Table */}
          {activeDiffTab === "facts" && (
            <div className="rounded-lg border border-border/60 bg-card/40 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-muted/40 text-muted-foreground font-semibold uppercase tracking-wider text-[10px] border-b border-border/60">
                    <tr>
                      <th className="py-2.5 px-3">Accounting Concept</th>
                      <th className="py-2.5 px-3">Period</th>
                      <th className="py-2.5 px-3 w-16">Unit</th>
                      <th className="py-2.5 px-3 text-right">Prior Reported</th>
                      <th className="py-2.5 px-3 text-right">Revised / Current</th>
                      <th className="py-2.5 px-3 text-right">Variance</th>
                      <th className="py-2.5 px-3 text-right">% Change</th>
                      <th className="py-2.5 px-3 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 font-mono">
                    {comparison.xbrl_fact_diffs.length > 0 ? (
                      comparison.xbrl_fact_diffs.map((diff, idx) => (
                        <tr key={idx} className="hover:bg-muted/20">
                          <td className="py-2 px-3 text-foreground font-semibold">
                            {diff.label}
                            <div className="text-[10px] text-muted-foreground font-mono">{diff.concept_name}</div>
                          </td>
                          <td className="py-2 px-3 text-muted-foreground">{diff.period_label}</td>
                          <td className="py-2 px-3 text-muted-foreground">{diff.unit}</td>
                          <td className="py-2 px-3 text-right text-muted-foreground">
                            {diff.prior_value.toLocaleString()}
                          </td>
                          <td className="py-2 px-3 text-right text-foreground font-bold">
                            {diff.current_value.toLocaleString()}
                          </td>
                          <td
                            className={`py-2 px-3 text-right font-bold ${
                              diff.absolute_difference >= 0 ? "text-emerald-400" : "text-rose-400"
                            }`}
                          >
                            {diff.absolute_difference >= 0 ? "+" : ""}
                            {diff.absolute_difference.toLocaleString()}
                          </td>
                          <td className="py-2 px-3 text-right text-muted-foreground">
                            {diff.percentage_difference !== null && diff.percentage_difference !== undefined
                              ? `${diff.percentage_difference >= 0 ? "+" : ""}${diff.percentage_difference.toFixed(2)}%`
                              : "—"}
                          </td>
                          <td className="py-2 px-3 text-center">
                            {diff.is_restatement ? (
                              <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-300 font-bold border border-amber-500/20">
                                RESTATEMENT
                              </span>
                            ) : (
                              <span className="px-1.5 py-0.5 rounded text-[10px] bg-muted text-muted-foreground">
                                VARIANCE
                              </span>
                            )}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={8} className="py-6 text-center text-muted-foreground font-sans text-xs">
                          No XBRL financial fact differences detected between the selected filings.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="p-8 text-center rounded-lg border border-dashed border-border text-muted-foreground text-xs space-y-2">
          <GitCompare className="w-5 h-5 mx-auto text-muted-foreground/80" />
          <p>Select two filings above to perform unified text and structured XBRL fact comparison.</p>
          <p className="text-[11px]">
            Audits original vs amendment revisions (e.g. 10-K vs 10-K/A) or consecutive fiscal period developments.
          </p>
        </div>
      )}
    </div>
  );
};
