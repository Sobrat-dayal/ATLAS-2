"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import { useCompanyStatements } from "@/hooks/companies/useCompanyStatements";
import {
  ComparisonMode,
  ConsolidationScope,
  FinancialStatementCellDTO,
  FinancialStatementRowDTO,
  ScaleType,
  StatementPeriodDTO,
} from "@/lib/companies/statements/types";
import {
  AlertTriangle,
  Calendar,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  DollarSign,
  FileSpreadsheet,
  Info,
  Layers,
  Maximize2,
  Minimize2,
  RotateCw,
  Scale,
} from "lucide-react";

export interface FinancialStatementsWorkspaceProps {
  companyId: string;
  companyName?: string;
}

export function FinancialStatementsWorkspace({
  companyId,
  companyName = "Company",
}: FinancialStatementsWorkspaceProps) {
  const {
    statementType,
    setStatementType,
    periodType,
    setPeriodType,
    scale,
    setScale,
    comparisonMode,
    setComparisonMode,
    consolidationScope,
    setConsolidationScope,
    statement,
    sources,
    isLoading,
    error,
    expandedRows,
    toggleRow,
    expandAll,
    collapseAll,
    refetch,
  } = useCompanyStatements({ companyId });

  // Selected cell for provenance popover inspection
  const [selectedCell, setSelectedCell] = useState<{
    row: FinancialStatementRowDTO;
    period: StatementPeriodDTO;
    cell: FinancialStatementCellDTO;
  } | null>(null);

  return (
    <div className="space-y-4">
      {/* 1. Statement Type Navigation Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-atlas-border-subtle pb-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 p-1 bg-atlas-surface-2 rounded-sm border border-atlas-border-default">
            <button
              onClick={() => setStatementType("income_statement")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-colors flex items-center gap-1.5 ${
                statementType === "income_statement"
                  ? "bg-atlas-surface-1 text-atlas-text-primary shadow-xs border border-atlas-border-subtle"
                  : "text-atlas-text-muted hover:text-atlas-text-secondary"
              }`}
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Income Statement</span>
            </button>

          <button
            onClick={() => setStatementType("balance_sheet")}
            className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-colors flex items-center gap-1.5 ${
              statementType === "balance_sheet"
                ? "bg-atlas-surface-1 text-atlas-text-primary shadow-xs border border-atlas-border-subtle"
                : "text-atlas-text-muted hover:text-atlas-text-secondary"
            }`}
          >
            <Scale className="w-3.5 h-3.5" />
            <span>Balance Sheet</span>
          </button>

          <button
            onClick={() => setStatementType("cash_flow_statement")}
            className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-colors flex items-center gap-1.5 ${
              statementType === "cash_flow_statement"
                ? "bg-atlas-surface-1 text-atlas-text-primary shadow-xs border border-atlas-border-subtle"
                : "text-atlas-text-muted hover:text-atlas-text-secondary"
            }`}
          >
            <DollarSign className="w-3.5 h-3.5" />
            <span>Cash Flow</span>
          </button>
        </div>
        {companyName && (
          <span className="text-xs font-semibold text-atlas-text-primary hidden md:inline">
            {companyName}
          </span>
        )}
      </div>

        {/* Global Metadata: Currency & Standard */}
        {statement && (
          <div className="flex items-center gap-3 text-xs text-atlas-text-muted font-mono">
            <span className="flex items-center gap-1">
              <span className="text-atlas-text-secondary">Standard:</span>
              <span className="uppercase font-semibold text-atlas-text-primary">
                {statement.accounting_framework.replace("_", " ")}
              </span>
            </span>
            <span className="text-atlas-border-default">•</span>
            <span className="flex items-center gap-1">
              <span className="text-atlas-text-secondary">Currency:</span>
              <span className="font-semibold text-atlas-text-primary">{statement.reporting_currency}</span>
            </span>
          </div>
        )}
      </div>

      {/* 2. Interactive Controls Toolbar */}
      <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Left: Period Frequency Selector */}
        <div className="flex items-center gap-2">
          <span className="text-atlas-text-muted font-medium flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" /> Period:
          </span>
          <div className="inline-flex rounded-sm border border-atlas-border-default p-0.5 bg-atlas-surface-2">
            <button
              onClick={() => setPeriodType("annual")}
              className={`px-2.5 py-1 text-[11px] font-medium rounded-xs transition-colors ${
                periodType === "annual"
                  ? "bg-atlas-surface-1 text-atlas-text-primary font-semibold shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-secondary"
              }`}
            >
              Annual
            </button>
            <button
              onClick={() => setPeriodType("quarterly")}
              className={`px-2.5 py-1 text-[11px] font-medium rounded-xs transition-colors ${
                periodType === "quarterly"
                  ? "bg-atlas-surface-1 text-atlas-text-primary font-semibold shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-secondary"
              }`}
            >
              Quarterly
            </button>
            <button
              onClick={() => {
                if (statementType !== "balance_sheet") setPeriodType("ttm");
              }}
              disabled={statementType === "balance_sheet"}
              title={
                statementType === "balance_sheet"
                  ? "TTM summation is mathematically prohibited for Balance Sheet stock balances."
                  : "Trailing-twelve-months flow calculation"
              }
              className={`px-2.5 py-1 text-[11px] font-medium rounded-xs transition-colors ${
                statementType === "balance_sheet"
                  ? "opacity-40 cursor-not-allowed text-atlas-text-muted"
                  : periodType === "ttm"
                  ? "bg-atlas-surface-1 text-atlas-text-primary font-semibold shadow-xs"
                  : "text-atlas-text-muted hover:text-atlas-text-secondary"
              }`}
            >
              TTM
            </button>
          </div>
        </div>

        {/* Center: Scope and Scale */}
        <div className="flex items-center gap-3">
          {/* Scope Selector */}
          <div className="flex items-center gap-1.5">
            <span className="text-atlas-text-muted font-medium flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" /> Scope:
            </span>
            <select
              value={consolidationScope}
              onChange={(e) => setConsolidationScope(e.target.value as ConsolidationScope)}
              className="bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-primary rounded-sm px-2 py-1 text-xs focus:outline-hidden font-mono"
            >
              <option value="consolidated">Consolidated</option>
              <option value="standalone">Standalone</option>
            </select>
          </div>

          {/* Scale Selector */}
          <div className="flex items-center gap-1.5">
            <span className="text-atlas-text-muted font-medium">Scale:</span>
            <select
              value={scale}
              onChange={(e) => setScale(e.target.value as ScaleType)}
              className="bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-primary rounded-sm px-2 py-1 text-xs focus:outline-hidden font-mono"
            >
              <option value="billions">Billions ($B)</option>
              <option value="millions">Millions ($M)</option>
              <option value="thousands">Thousands ($K)</option>
              <option value="original">Original Units</option>
              <option value="auto">Auto Scale</option>
            </select>
          </div>

          {/* Comparison Mode Selector */}
          <div className="flex items-center gap-1.5">
            <span className="text-atlas-text-muted font-medium">Comparison:</span>
            <select
              value={comparisonMode}
              onChange={(e) => setComparisonMode(e.target.value as ComparisonMode)}
              className="bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-primary rounded-sm px-2 py-1 text-xs focus:outline-hidden font-mono"
            >
              <option value="none">Values Only</option>
              <option value="yoy_absolute">YoY Change ($)</option>
              <option value="yoy_percent">YoY Change (%)</option>
              <option value="qoq_absolute">QoQ Change ($)</option>
              <option value="qoq_percent">QoQ Change (%)</option>
              <option value="common_size">Common Size (%)</option>
            </select>
          </div>
        </div>

        {/* Right: Expand/Collapse and Refresh */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            onClick={expandAll}
            className="text-[11px] text-atlas-text-secondary h-7 px-2"
            title="Expand All Row Groups"
          >
            <Maximize2 className="w-3.5 h-3.5 mr-1" />
            Expand All
          </Button>

          <Button
            variant="ghost"
            onClick={collapseAll}
            className="text-[11px] text-atlas-text-secondary h-7 px-2"
            title="Collapse All Row Groups"
          >
            <Minimize2 className="w-3.5 h-3.5 mr-1" />
            Collapse All
          </Button>

          <Button
            variant="secondary"
            onClick={() => refetch()}
            className="text-[11px] h-7 px-2"
            title="Refresh Canonical Statement Data"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* 3. Accounting Diagnostics Banner */}
      {statement && statement.diagnostics && (
        <div
          className={`px-3.5 py-2.5 rounded-sm border text-xs flex items-center justify-between ${
            statement.diagnostics.is_balanced
              ? "bg-atlas-surface-1 border-atlas-border-subtle text-atlas-text-secondary"
              : "bg-atlas-status-warning/10 border-atlas-status-warning/40 text-atlas-status-warning"
          }`}
        >
          <div className="flex items-center gap-2">
            {statement.diagnostics.is_balanced ? (
              <CheckCircle2 className="w-4 h-4 text-atlas-status-positive" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-atlas-status-warning" />
            )}
            <span className="font-semibold">
              {statementType === "balance_sheet" ? "Balance Sheet Reconciliation: " : "Statement Diagnostics: "}
            </span>
            <span className="font-mono">{statement.diagnostics.notes[0] || "All checks consistent."}</span>
          </div>

          <Badge
            variant={statement.diagnostics.is_balanced ? "positive" : "warning"}
            className="uppercase text-[10px] font-mono"
          >
            {statement.diagnostics.status.replace(/_/g, " ")}
          </Badge>
        </div>
      )}

      {/* 4. High-Density Multi-Period Financial Table */}
      {isLoading ? (
        <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-12 text-center text-xs text-atlas-text-muted">
          <RotateCw className="w-6 h-6 animate-spin mx-auto mb-3 text-atlas-text-muted" />
          Loading verified institutional financial statement data...
        </div>
      ) : error ? (
        <div className="bg-atlas-surface-1 border border-atlas-status-negative/30 rounded-sm p-6 text-center text-xs text-atlas-status-negative">
          <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-atlas-status-negative" />
          <div className="font-bold text-sm mb-1">Financial Statement Unavailable</div>
          <div className="text-atlas-text-muted">{error}</div>
          <Button variant="secondary" onClick={() => refetch()} className="mt-4">
            Retry Request
          </Button>
        </div>
      ) : statement && statement.periods.length > 0 ? (
        <div className="border border-atlas-border-default rounded-sm overflow-hidden bg-atlas-surface-1">
          <div className="overflow-x-auto max-h-[680px]">
            <table className="w-full border-collapse text-xs text-left">
              {/* Sticky Table Header */}
              <thead className="bg-atlas-surface-2 border-b border-atlas-border-default sticky top-0 z-20">
                <tr>
                  {/* Sticky Line Item Label Column */}
                  <th
                    scope="col"
                    className="py-2.5 px-3.5 font-bold uppercase tracking-wider text-[11px] text-atlas-text-muted min-w-[280px] max-w-[340px] sticky left-0 bg-atlas-surface-2 border-r border-atlas-border-default z-30"
                  >
                    Financial Concept
                  </th>

                  {/* Period Columns (Chronological) */}
                  {statement.periods.map((period) => (
                    <th
                      key={period.period_id}
                      scope="col"
                      className="py-2.5 px-3 font-mono font-bold text-right min-w-[130px] border-r border-atlas-border-subtle last:border-r-0"
                    >
                      <div className="text-atlas-text-primary text-xs flex items-center justify-end gap-1.5">
                        <span>{period.label}</span>
                        {period.is_restated && (
                          <Badge variant="warning" className="text-[9px] px-1 py-0 uppercase">
                            Restated
                          </Badge>
                        )}
                        {period.is_derived && (
                          <Badge variant="outline" className="text-[9px] px-1 py-0 uppercase">
                            Derived
                          </Badge>
                        )}
                      </div>
                      <div className="text-[10px] text-atlas-text-muted font-normal mt-0.5">
                        End: {period.period_end}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              {/* Table Body with Hierarchical Rows */}
              <tbody className="divide-y divide-atlas-border-subtle font-mono">
                {statement.rows.map((row) => {
                  const isExpanded = expandedRows.has(row.concept_id);
                  const isVisible =
                    !row.parent_id ||
                    expandedRows.has(row.parent_id);

                  if (!isVisible && row.hierarchy_level > 1) {
                    return null;
                  }

                  const rowClass = row.is_total
                    ? "bg-atlas-surface-2/40 font-bold text-atlas-text-primary"
                    : row.is_group
                    ? "font-semibold text-atlas-text-primary bg-atlas-surface-1"
                    : "text-atlas-text-secondary hover:bg-atlas-surface-2/30 transition-colors";

                  return (
                    <tr key={row.concept_id} className={rowClass}>
                      {/* Sticky Row Concept Label */}
                      <td
                        className={`py-2 px-3.5 sticky left-0 bg-atlas-surface-1 border-r border-atlas-border-default z-10 flex items-center justify-between gap-2 ${
                          row.is_total ? "bg-atlas-surface-2" : ""
                        }`}
                        style={{ paddingLeft: `${row.hierarchy_level * 16 + 12}px` }}
                      >
                        <div className="flex items-center gap-1.5 truncate">
                          {row.is_group && (
                            <button
                              onClick={() => toggleRow(row.concept_id)}
                              className="text-atlas-text-muted hover:text-atlas-text-primary p-0.5 focus:outline-hidden"
                              aria-label={isExpanded ? "Collapse group" : "Expand group"}
                            >
                              {isExpanded ? (
                                <ChevronDown className="w-3.5 h-3.5" />
                              ) : (
                                <ChevronRight className="w-3.5 h-3.5" />
                              )}
                            </button>
                          )}
                          <span className={`truncate ${row.is_total ? "font-bold text-atlas-text-primary" : ""}`}>
                            {row.label}
                          </span>
                        </div>

                        {row.description && (
                          <span
                            title={row.description}
                            className="text-atlas-text-muted hover:text-atlas-text-primary cursor-help ml-1"
                          >
                            <Info className="w-3 h-3" />
                          </span>
                        )}
                      </td>

                      {/* Period Value Cells */}
                      {statement.periods.map((period) => {
                        const cell = row.cells[period.period_id];
                        if (!cell) {
                          return (
                            <td
                              key={period.period_id}
                              className="py-2 px-3 text-right text-atlas-text-muted border-r border-atlas-border-subtle last:border-r-0"
                            >
                              —
                            </td>
                          );
                        }

                        const hasComparison =
                          comparisonMode !== "none" &&
                          (cell.comparison_formatted !== null || cell.is_not_meaningful);

                        return (
                          <td
                            key={period.period_id}
                            onClick={() => setSelectedCell({ row, period, cell })}
                            title="Click to view accounting provenance and exact decimals"
                            className="py-2 px-3 text-right border-r border-atlas-border-subtle last:border-r-0 cursor-pointer hover:bg-atlas-accent/5 transition-colors group"
                          >
                            <div className="flex flex-col items-end">
                              <span
                                className={`text-xs ${
                                  cell.formatted_value.startsWith("(")
                                    ? "text-atlas-status-negative"
                                    : row.is_total
                                    ? "text-atlas-text-primary font-bold"
                                    : "text-atlas-text-primary"
                                }`}
                              >
                                {cell.formatted_value}
                              </span>

                              {/* Comparison sub-value */}
                              {hasComparison && (
                                <span
                                  className={`text-[10px] font-mono mt-0.5 ${
                                    cell.is_not_meaningful
                                      ? "text-atlas-text-muted font-normal"
                                      : cell.comparison_formatted?.startsWith("(") ||
                                        cell.comparison_formatted?.startsWith("-")
                                      ? "text-atlas-status-negative"
                                      : "text-atlas-status-positive"
                                  }`}
                                >
                                  {cell.comparison_formatted}
                                </span>
                              )}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-12 text-center text-xs text-atlas-text-muted">
          No verified {statementType.replace(/_/g, " ")} periods indexed for this entity.
        </div>
      )}

      {/* 5. Provenance & Cell Detail Drawer / Modal */}
      {selectedCell && (
        <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4 text-xs space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-atlas-accent" />
              <span className="font-bold text-atlas-text-primary">
                Accounting Concept Provenance & Exact Valuation
              </span>
            </div>
            <button
              onClick={() => setSelectedCell(null)}
              className="text-atlas-text-muted hover:text-atlas-text-primary text-xs"
            >
              ✕ Close
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-atlas-text-muted block">Normalized Concept:</span>
              <span className="font-mono font-semibold text-atlas-text-primary">{selectedCell.row.concept_id}</span>
            </div>

            <div>
              <span className="text-atlas-text-muted block">Original Concept / Label:</span>
              <span className="font-mono text-atlas-text-secondary">
                {selectedCell.cell.original_label || selectedCell.row.label}
              </span>
            </div>

            <div>
              <span className="text-atlas-text-muted block">Lossless Exact Decimal:</span>
              <span className="font-mono font-bold text-atlas-status-positive">
                {selectedCell.cell.exact_value != null ? selectedCell.cell.exact_value.toString() : "—"}
              </span>
            </div>

            <div>
              <span className="text-atlas-text-muted block">Derivation Kind:</span>
              <Badge variant="outline" className="text-[10px] font-mono uppercase mt-0.5">
                {selectedCell.cell.derivation_kind}
              </Badge>
            </div>

            <div>
              <span className="text-atlas-text-muted block">Fiscal Period:</span>
              <span className="font-mono text-atlas-text-secondary">
                {selectedCell.period.label} ({selectedCell.period.period_end})
              </span>
            </div>

            <div>
              <span className="text-atlas-text-muted block">Filing / Document:</span>
              <span className="font-mono text-atlas-text-secondary truncate">
                {selectedCell.period.source_filing_name || "Official SEC 10-K / 10-Q"}
              </span>
            </div>

            <div>
              <span className="text-atlas-text-muted block">Restatement Status:</span>
              <span className="font-mono text-atlas-text-secondary">
                {selectedCell.cell.is_restated ? "Amended / Restated" : "Original Reported"}
              </span>
            </div>

            <div>
              <span className="text-atlas-text-muted block">Scale / Units:</span>
              <span className="font-mono text-atlas-text-secondary">
                {selectedCell.cell.scale} ({selectedCell.cell.unit})
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 6. Legal & Auditability Disclosure Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between text-[11px] text-atlas-text-muted pt-2 border-t border-atlas-border-subtle font-mono">
        <span>
          Source: Stage 34 Canonical Fundamental Store • SEC EDGAR verified taxonomies
          {sources && sources.length > 0 ? ` (${sources.length} filings verified)` : ""}
        </span>
        <span>Institutional financial statements • Point-in-time provenance guaranteed</span>
      </div>
    </div>
  );
}
