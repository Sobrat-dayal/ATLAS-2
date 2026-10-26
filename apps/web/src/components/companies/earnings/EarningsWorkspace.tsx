"use client";

import React from "react";
import {
  useCompanyEarnings,
  EarningsSubTab,
} from "@/hooks/companies/useCompanyEarnings";
import { EarningsOverviewCards } from "./EarningsOverviewCards";
import { EarningsActualVsEstimateChart } from "./EarningsActualVsEstimateChart";
import { EarningsHistoryTable } from "./EarningsHistoryTable";
import { ManagementGuidancePanel } from "./ManagementGuidancePanel";
import { EarningsCallsPanel } from "./EarningsCallsPanel";
import {
  Calendar,
  History,
  Target,
  PhoneCall,
  RefreshCw,
  AlertCircle,
  FileSpreadsheet,
  Percent,
  Layers,
  ShieldCheck,
} from "lucide-react";

interface EarningsWorkspaceProps {
  companyId: string;
  companyName?: string;
  onNavigateToStatements?: () => void;
  onNavigateToRatios?: () => void;
}

export const EarningsWorkspace: React.FC<EarningsWorkspaceProps> = ({
  companyId,
  companyName = "Company",
  onNavigateToStatements,
  onNavigateToRatios,
}) => {
  const {
    activeSubTab,
    setActiveSubTab,
    periodType,
    setPeriodType,
    overview,
    historyItems,
    guidance,
    calls,
    isLoading,
    error,
    refresh,
  } = useCompanyEarnings(companyId);

  const currency = historyItems[0]?.currency || overview?.latest_completed?.currency || "USD";

  const subTabs: { id: EarningsSubTab; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Overview", icon: <Layers className="h-3.5 w-3.5" /> },
    { id: "history", label: "Earnings History", icon: <History className="h-3.5 w-3.5" /> },
    { id: "guidance", label: "Management Guidance", icon: <Target className="h-3.5 w-3.5" /> },
    { id: "calls", label: "Calls & Transcripts", icon: <PhoneCall className="h-3.5 w-3.5" /> },
  ];

  if (error && !overview && historyItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-border/60 rounded-lg bg-card/40 my-6">
        <AlertCircle className="h-10 w-10 text-rose-500 mb-3" />
        <h3 className="text-base font-semibold text-foreground">Unable to Load Earnings Intelligence</h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-md">{error}</p>
        <button
          onClick={refresh}
          className="mt-4 inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Retry Request
        </button>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* Workspace Subheader / Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/60 pb-3">
        {/* Navigation Subtabs */}
        <div className="flex items-center gap-1 bg-muted/30 p-1 rounded-lg border border-border/50">
          {subTabs.map((tab) => {
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? "bg-card text-foreground shadow-sm border border-border/60 font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {tab.id === "history" && historyItems.length > 0 && (
                  <span className="ml-1 text-[10px] text-muted-foreground bg-muted/50 px-1.5 py-0.2 rounded-full font-mono">
                    {historyItems.length}
                  </span>
                )}
                {tab.id === "guidance" && guidance.length > 0 && (
                  <span className="ml-1 text-[10px] text-muted-foreground bg-muted/50 px-1.5 py-0.2 rounded-full font-mono">
                    {guidance.length}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Period Switcher & Cross-Module Quick Links */}
        <div className="flex items-center gap-2">
          {/* Period Type Toggle */}
          <div className="flex items-center rounded-md border border-border/60 bg-muted/20 p-0.5 text-xs">
            <button
              onClick={() => setPeriodType("QUARTERLY")}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                periodType === "QUARTERLY"
                  ? "bg-card text-foreground font-semibold shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Quarterly
            </button>
            <button
              onClick={() => setPeriodType("ANNUAL")}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                periodType === "ANNUAL"
                  ? "bg-card text-foreground font-semibold shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Annual
            </button>
          </div>

          {/* Quick links to Stage 82 Statements and Stage 83 Ratios */}
          {onNavigateToStatements && (
            <button
              onClick={onNavigateToStatements}
              title="Navigate to Financial Statements"
              className="hidden lg:flex items-center gap-1 rounded-md border border-border/60 bg-card/60 px-2.5 py-1 text-[11px] text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
            >
              <FileSpreadsheet className="h-3 w-3 text-sky-500" />
              <span>Statements</span>
            </button>
          )}

          {onNavigateToRatios && (
            <button
              onClick={onNavigateToRatios}
              title="Navigate to Financial Ratios"
              className="hidden lg:flex items-center gap-1 rounded-md border border-border/60 bg-card/60 px-2.5 py-1 text-[11px] text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
            >
              <Percent className="h-3 w-3 text-emerald-500" />
              <span>Ratios</span>
            </button>
          )}

          {/* Refresh Action */}
          <button
            onClick={refresh}
            disabled={isLoading}
            title="Refresh Earnings Data"
            className="flex items-center justify-center h-7 w-7 rounded-md border border-border/60 bg-card/60 text-muted-foreground hover:text-foreground hover:bg-muted/40 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin text-primary" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Tab Content Panes */}
      {activeSubTab === "overview" && (
        <div className="space-y-5">
          {/* Executive Summary Cards */}
          <EarningsOverviewCards overview={overview} />

          {/* Actual vs Estimate Evolution Chart */}
          <EarningsActualVsEstimateChart
            items={historyItems}
            currency={currency}
          />

          {/* Recent History Table Summary */}
          <div className="pt-2">
            <EarningsHistoryTable
              items={historyItems.slice(0, 8)}
              currency={currency}
            />
          </div>

          {/* Lower Grid: Quick Guidance & Calls Preview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <Target className="h-3.5 w-3.5 text-primary" />
                  Latest Guidance
                </span>
                <button
                  onClick={() => setActiveSubTab("guidance")}
                  className="text-[11px] text-primary hover:underline font-medium"
                >
                  View All ({guidance.length})
                </button>
              </div>
              <ManagementGuidancePanel
                guidance={guidance.slice(0, 2)}
                currency={currency}
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                  <PhoneCall className="h-3.5 w-3.5 text-primary" />
                  Recent Conference Calls
                </span>
                <button
                  onClick={() => setActiveSubTab("calls")}
                  className="text-[11px] text-primary hover:underline font-medium"
                >
                  View All ({calls.length})
                </button>
              </div>
              <EarningsCallsPanel calls={calls.slice(0, 2)} />
            </div>
          </div>
        </div>
      )}

      {activeSubTab === "history" && (
        <div className="space-y-4">
          <EarningsHistoryTable
            items={historyItems}
            currency={currency}
          />
        </div>
      )}

      {activeSubTab === "guidance" && (
        <div className="space-y-4">
          <ManagementGuidancePanel
            guidance={guidance}
            currency={currency}
          />
        </div>
      )}

      {activeSubTab === "calls" && (
        <div className="space-y-4">
          <EarningsCallsPanel calls={calls} />
        </div>
      )}

      {/* Institutional Methodology & Safeguards Footer */}
      <div className="rounded-lg border border-border/40 bg-muted/10 p-3 text-xs text-muted-foreground flex flex-col sm:flex-row sm:items-center justify-between gap-2 mt-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-primary shrink-0" />
          <span>
            Institutional Earnings Architecture: Temporal pre-release estimate cutoff enforced. No look-ahead bias or synthetic accounting forecasts.
          </span>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-mono shrink-0">
          <span>Reporting: {currency}</span>
          <span>•</span>
          <span>Scope: Consolidated</span>
        </div>
      </div>
    </div>
  );
};
