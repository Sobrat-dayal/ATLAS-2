"use client";

import React, { useState } from "react";
import { Badge } from "@/design-system";
import { CompanyFinancialSummary } from "@/lib/companies/types";
import { FinancialStatementsWorkspace } from "@/components/companies/statements/FinancialStatementsWorkspace";
import { DollarSign, FileSpreadsheet, LayoutGrid } from "lucide-react";

export interface CompanyFinancialsTabProps {
  financialSummary: CompanyFinancialSummary;
  companyId?: string;
  companyName?: string;
}

export function CompanyFinancialsTab({
  financialSummary,
  companyId,
  companyName = "Company",
}: CompanyFinancialsTabProps) {
  const [viewMode, setViewMode] = useState<"statements" | "summary">(
    companyId ? "statements" : "summary"
  );
  const isAvailable = financialSummary.status === "AVAILABLE" && financialSummary.metrics.length > 0;

  return (
    <div className="space-y-6">
      {/* View Mode Switcher */}
      {companyId && (
        <div className="flex items-center justify-between border-b border-atlas-border-subtle pb-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode("statements")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-colors flex items-center gap-1.5 ${
                viewMode === "statements"
                  ? "bg-atlas-accent text-white shadow-xs"
                  : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary border border-atlas-border-default"
              }`}
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Full Financial Statements (Stage 82)</span>
            </button>

            <button
              onClick={() => setViewMode("summary")}
              className={`px-3 py-1.5 text-xs font-semibold rounded-sm transition-colors flex items-center gap-1.5 ${
                viewMode === "summary"
                  ? "bg-atlas-accent text-white shadow-xs"
                  : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary border border-atlas-border-default"
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span>Executive Summary</span>
            </button>
          </div>

          <div className="text-[11px] text-atlas-text-muted font-mono hidden sm:block">
            {viewMode === "statements"
              ? "Institutional Multi-Period Statements • Lossless Decimal Calculation"
              : "Stage 34 / 81 High-Level Metrics"}
          </div>
        </div>
      )}

      {/* 1. Full Stage 82 Financial Statements Workspace */}
      {viewMode === "statements" && companyId ? (
        <FinancialStatementsWorkspace companyId={companyId} companyName={companyName} />
      ) : (
        /* 2. Executive Financial Summary Cards (Stage 81 Baseline) */
        <div className="space-y-6">
          <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-atlas-border-subtle">
              <div className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-atlas-text-muted" aria-hidden="true" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-atlas-text-muted">
                  Qualified High-Level Financial Summary
                </h3>
                <Badge
                  variant={isAvailable ? "positive" : "default"}
                  className="font-mono text-[10px]"
                >
                  {financialSummary.status}
                </Badge>
              </div>
              <span className="text-[11px] text-atlas-text-muted">Stage 34 Fundamental Data</span>
            </div>

            {isAvailable ? (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-3 text-xs">
                <div>
                  <div className="text-atlas-text-muted">Reporting Currency</div>
                  <div className="font-mono font-bold text-atlas-text-primary text-sm mt-0.5">
                    {financialSummary.reporting_currency}
                  </div>
                </div>

                <div>
                  <div className="text-atlas-text-muted">Fiscal Period</div>
                  <div className="font-mono font-medium text-atlas-text-secondary mt-0.5">
                    {financialSummary.fiscal_period || "Annual (FY)"}
                  </div>
                </div>

                <div>
                  <div className="text-atlas-text-muted">Period End Date</div>
                  <div className="font-mono text-atlas-text-secondary mt-0.5">
                    {financialSummary.period_end_date || "—"}
                  </div>
                </div>

                <div>
                  <div className="text-atlas-text-muted">Publication / Filing Date</div>
                  <div className="font-mono text-atlas-text-secondary mt-0.5">
                    {financialSummary.publication_date || "—"}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-xs text-atlas-text-muted py-3 italic">
                No canonical corporate financial statements filed or indexed for this entity.
              </div>
            )}
          </div>

          {/* Key Metrics Grid */}
          {isAvailable && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {financialSummary.metrics.map((metric) => (
                <div
                  key={metric.metric_key}
                  className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-4 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-xs text-atlas-text-muted">
                      <span>{metric.metric_name}</span>
                      <span className="font-mono text-[10px] uppercase text-atlas-text-muted">
                        {metric.consolidation_scope}
                      </span>
                    </div>

                    <div className="text-2xl font-bold font-mono text-atlas-text-primary mt-2">
                      {metric.value || "—"}
                    </div>
                  </div>

                  <div className="mt-4 pt-2 border-t border-atlas-border-subtle flex items-center justify-between text-[11px] text-atlas-text-muted font-mono">
                    <span>Period: {metric.fiscal_period || "FY"}</span>
                    <span className="text-atlas-text-secondary capitalize">{metric.restatement_status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
