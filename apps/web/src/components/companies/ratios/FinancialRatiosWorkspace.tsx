"use client";

import React, { useMemo, useState } from "react";
import { useCompanyRatios } from "@/hooks/companies/useCompanyRatios";
import { RatioTrendChart } from "./RatioTrendChart";
import { RatioFormulaModal } from "./RatioFormulaModal";
import {
  RatioCategory,
  RatioValueDTO,
  RatioDefinitionDTO,
  RatioPeriodType,
} from "@/lib/companies/ratios/types";
import { Badge, Button, Input } from "@/design-system";
import {
  Activity,
  Calendar,
  CheckCircle2,
  DollarSign,
  Info,
  Layers,
  Percent,
  RefreshCw,
  RotateCw,
  Search,
  TrendingUp,
} from "lucide-react";

export interface FinancialRatiosWorkspaceProps {
  companyId: string;
  companyName?: string;
}

const CATEGORIES: Array<{ id: RatioCategory | "all"; label: string }> = [
  { id: "all", label: "All Categories" },
  { id: "profitability", label: "Profitability" },
  { id: "liquidity", label: "Liquidity" },
  { id: "solvency", label: "Solvency & Leverage" },
  { id: "efficiency", label: "Efficiency" },
  { id: "cash_flow", label: "Cash Flow" },
  { id: "valuation", label: "Valuation Multiples" },
];

const COMMON_PERIODS = ["FY2024", "FY2023", "FY2022", "FY2021", "Q4-2024", "Q3-2024", "Q2-2024", "Q1-2024"];

export function FinancialRatiosWorkspace({
  companyId,
  companyName = "Company",
}: FinancialRatiosWorkspaceProps) {
  const {
    category,
    setCategory,
    periodId,
    setPeriodId,
    periodType,
    setPeriodType,
    catalog,
    ratiosData,
    isLoading,
    error,
    refresh,
    historyRatioId,
    historyData,
    isHistoryLoading,
    selectHistoryRatio,
    inspectedRatioId,
    methodologyData,
    lineageData,
    isInspectionLoading,
    inspectRatio,
    closeInspector,
  } = useCompanyRatios(companyId);

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [showTrendChart, setShowTrendChart] = useState<boolean>(true);

  // Map ratio definition lookup for easy display
  const defMap = useMemo(() => {
    const map = new Map<string, RatioDefinitionDTO>();
    if (catalog?.ratios) {
      catalog.ratios.forEach((def: RatioDefinitionDTO) => map.set(def.id, def));
    }
    return map;
  }, [catalog]);

  const ratios = ratiosData?.ratios || [];

  // Filter ratios by search query
  const filteredRatios = useMemo(() => {
    if (!searchQuery.trim()) return ratios;
    const q = searchQuery.toLowerCase().trim();
    return ratios.filter(
      (r: RatioValueDTO) =>
        r.name.toLowerCase().includes(q) ||
        r.ratio_id.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q)
    );
  }, [ratios, searchQuery]);

  // Selected ratio definition for inspection modal
  const selectedDefForModal = useMemo(() => {
    if (!inspectedRatioId) return null;
    return defMap.get(inspectedRatioId) || methodologyData?.definition || null;
  }, [inspectedRatioId, defMap, methodologyData]);

  const selectedRatioValueForModal = useMemo(() => {
    if (!inspectedRatioId) return null;
    return ratios.find((r: RatioValueDTO) => r.ratio_id === inspectedRatioId) || null;
  }, [inspectedRatioId, ratios]);

  return (
    <div className="space-y-4 text-xs font-sans">
      {/* Workspace Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-atlas-border-subtle pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-atlas-surface-2 rounded-sm border border-atlas-border-default text-atlas-accent">
            <Percent className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-atlas-text-primary tracking-wide">
                Financial Ratios & Fundamental Analysis
              </h2>
              <Badge variant="outline" className="font-mono text-[10px]">
                Stage 83
              </Badge>
              <Badge variant="default" className="font-mono text-[10px]">
                44 Canonical Ratios
              </Badge>
            </div>
            <div className="text-[11px] text-atlas-text-muted font-mono mt-0.5">
              Lossless Decimal Calculation • Point-in-Time Fact Qualification • Source Provenance Lineage
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="text-atlas-text-muted">Entity:</span>
          <span className="font-bold text-atlas-text-primary">{companyName}</span>
          <Button
            variant="secondary"
            size="sm"
            onClick={refresh}
            disabled={isLoading}
            className="h-7 px-2 text-xs gap-1 ml-2"
            title="Refresh canonical calculations"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Recalculate</span>
          </Button>
        </div>
      </div>

      {/* Controls Toolbar: Categories, Period Type, Fiscal Period, Search */}
      <div className="flex flex-col gap-2.5 bg-atlas-surface-1 border border-atlas-border-default rounded-sm p-3 shadow-xs">
        {/* Category Navigation Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-xs transition-colors whitespace-nowrap shrink-0 ${
                category === cat.id
                  ? "bg-atlas-accent text-white shadow-xs"
                  : "bg-atlas-surface-2 text-atlas-text-secondary hover:text-atlas-text-primary border border-atlas-border-subtle"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Second Row: Period Selector, Scope, Search */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-atlas-border-subtle">
          <div className="flex flex-wrap items-center gap-2">
            {/* Period Type */}
            <div className="flex items-center gap-1 bg-atlas-surface-2 p-0.5 rounded-xs border border-atlas-border-subtle">
              {(["ANNUAL", "QUARTERLY", "TTM"] as RatioPeriodType[]).map((pt) => (
                <button
                  key={pt}
                  onClick={() => setPeriodType(pt)}
                  className={`px-2 py-0.5 text-[11px] font-mono rounded-xs transition-colors ${
                    periodType === pt
                      ? "bg-atlas-surface-1 text-atlas-text-primary font-bold shadow-xs border border-atlas-border-subtle"
                      : "text-atlas-text-muted hover:text-atlas-text-secondary"
                  }`}
                >
                  {pt}
                </button>
              ))}
            </div>

            {/* Fiscal Period Dropdown */}
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-atlas-text-muted" />
              <select
                value={periodId}
                onChange={(e) => setPeriodId(e.target.value)}
                className="bg-atlas-surface-2 text-atlas-text-primary border border-atlas-border-default rounded-xs px-2 py-1 text-xs font-mono focus:outline-hidden focus:border-atlas-accent"
              >
                {COMMON_PERIODS.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-atlas-text-muted" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter ratios..."
              className="pl-8 text-xs h-7 py-0 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Historical Trend Chart (if active) */}
      {showTrendChart && historyData && (
        <RatioTrendChart
          series={historyData}
          onClose={() => setShowTrendChart(false)}
        />
      )}

      {/* Loading & Error States */}
      {isLoading && (
        <div className="flex items-center justify-center p-8 bg-atlas-surface-1 border border-atlas-border-default rounded-sm gap-2 text-atlas-text-muted">
          <RotateCw className="w-4 h-4 animate-spin text-atlas-accent" />
          <span>Computing canonical financial ratios with exact Decimal precision...</span>
        </div>
      )}

      {error && !isLoading && (
        <div className="p-4 bg-atlas-surface-1 border border-atlas-negative/40 text-atlas-negative rounded-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-bold">Error:</span>
            <span>{error}</span>
          </div>
          <Button variant="secondary" size="sm" onClick={refresh} className="text-xs">
            Retry
          </Button>
        </div>
      )}

      {/* High-Density Ratios Table */}
      {!isLoading && !error && (
        <div className="bg-atlas-surface-1 border border-atlas-border-default rounded-sm overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-atlas-surface-2 border-b border-atlas-border-default text-atlas-text-muted font-mono text-[11px] uppercase tracking-wider">
                  <th className="py-2.5 px-3.5 font-bold">Financial Ratio</th>
                  <th className="py-2.5 px-2.5 font-bold">Category</th>
                  <th className="py-2.5 px-3.5 text-right font-bold">Calculated Value</th>
                  <th className="py-2.5 px-2 font-bold text-center">Unit</th>
                  <th className="py-2.5 px-2.5 font-bold text-center">Status</th>
                  <th className="py-2.5 px-3.5 font-bold hidden lg:table-cell">Canonical Formula</th>
                  <th className="py-2.5 px-3.5 text-right font-bold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-subtle font-mono text-xs">
                {filteredRatios.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-atlas-text-muted">
                      No matching financial ratios found for {periodId} ({category}).
                    </td>
                  </tr>
                ) : (
                  filteredRatios.map((ratio: RatioValueDTO) => {
                    const def = defMap.get(ratio.ratio_id);
                    const isSelectedTrend = historyRatioId === ratio.ratio_id && showTrendChart;

                    // Color code based on availability and negative/positive value
                    const isAvailable = ratio.status === "AVAILABLE";
                    const isNotMeaningful = ratio.status === "NOT_MEANINGFUL";
                    const numVal =
                      ratio.exact_value !== null && ratio.exact_value !== undefined
                        ? typeof ratio.exact_value === "number"
                          ? ratio.exact_value
                          : parseFloat(ratio.exact_value)
                        : null;
                    const isNegative = numVal !== null && numVal < 0;

                    return (
                      <tr
                        key={ratio.ratio_id}
                        className={`hover:bg-atlas-surface-2/60 transition-colors ${
                          isSelectedTrend ? "bg-atlas-accent/10" : ""
                        }`}
                      >
                        {/* Name and ID */}
                        <td className="py-2 px-3.5">
                          <div className="font-semibold text-atlas-text-primary">
                            {ratio.name}
                          </div>
                          <div className="text-[10px] text-atlas-text-muted font-mono">
                            {ratio.ratio_id}
                          </div>
                        </td>

                        {/* Category */}
                        <td className="py-2 px-2.5">
                          <span className="text-[10px] font-mono text-atlas-text-secondary uppercase">
                            {ratio.category}
                          </span>
                        </td>

                        {/* Calculated Value */}
                        <td className="py-2 px-3.5 text-right">
                          {isAvailable ? (
                            <span
                              className={`font-bold font-mono text-sm ${
                                isNegative
                                  ? "text-atlas-negative"
                                  : "text-atlas-text-primary"
                              }`}
                            >
                              {ratio.formatted_value}
                            </span>
                          ) : isNotMeaningful ? (
                            <span
                              className="text-amber-500 font-bold font-mono text-xs"
                              title={ratio.explanation || "Not meaningful due to negative base"}
                            >
                              N/M
                            </span>
                          ) : (
                            <span
                              className="text-atlas-text-muted font-mono"
                              title={ratio.explanation || "Missing input facts"}
                            >
                              —
                            </span>
                          )}
                        </td>

                        {/* Unit */}
                        <td className="py-2 px-2 text-center">
                          <span className="text-[10px] text-atlas-text-muted font-mono">
                            {ratio.unit_kind}
                          </span>
                        </td>

                        {/* Status */}
                        <td className="py-2 px-2.5 text-center">
                          <Badge
                            variant={
                              isAvailable
                                ? "positive"
                                : isNotMeaningful
                                ? "outline"
                                : "default"
                            }
                            className="text-[9px] font-mono py-0"
                          >
                            {ratio.status}
                          </Badge>
                        </td>

                        {/* Canonical Formula Preview */}
                        <td className="py-2 px-3.5 text-atlas-text-secondary text-[11px] font-mono hidden lg:table-cell max-w-[240px] truncate">
                          {ratio.formula_display || def?.formula_display || "—"}
                        </td>

                        {/* Actions */}
                        <td className="py-2 px-3.5 text-right whitespace-nowrap">
                          <div className="flex items-center justify-end gap-1.5">
                            {/* Trend Button */}
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => {
                                selectHistoryRatio(ratio.ratio_id);
                                setShowTrendChart(true);
                              }}
                              className={`h-6 px-2 text-[10px] font-mono gap-1 ${
                                isSelectedTrend ? "bg-atlas-accent text-white" : ""
                              }`}
                              title="View Multi-Period Historical Trend"
                            >
                              <TrendingUp className="w-3 h-3" />
                              <span>Trend</span>
                            </Button>

                            {/* Inspect Methodology Button */}
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => inspectRatio(ratio.ratio_id)}
                              className="h-6 px-2 text-[10px] font-mono gap-1"
                              title="Inspect Methodology and Source Facts"
                            >
                              <Info className="w-3 h-3" />
                              <span>Inspect</span>
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Table Footer */}
          <div className="px-3.5 py-2.5 bg-atlas-surface-2 border-t border-atlas-border-subtle flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-atlas-text-muted">
            <div className="flex items-center gap-3">
              <span>Showing {filteredRatios.length} of {ratios.length} ratios</span>
              <span>•</span>
              <span>Observation Period: {periodId} ({periodType})</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1 text-atlas-positive">
                <CheckCircle2 className="w-3.5 h-3.5" />
                No Look-Ahead Point-in-Time Qualification
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Formula & Lineage Inspection Modal */}
      {selectedDefForModal && (
        <RatioFormulaModal
          companyId={companyId}
          ratioDef={selectedDefForModal}
          calculatedValue={selectedRatioValueForModal}
          methodologyData={methodologyData}
          lineageData={lineageData}
          isLoading={isInspectionLoading}
          onClose={closeInspector}
        />
      )}
    </div>
  );
}
