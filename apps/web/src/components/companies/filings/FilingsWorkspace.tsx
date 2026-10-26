"use client";

import React from "react";
import {
  FilingsSubTab,
  useCompanyFilings,
} from "@/hooks/companies/useCompanyFilings";
import { FilingsOverviewCards } from "./FilingsOverviewCards";
import { FilingHistoryTable } from "./FilingHistoryTable";
import { FilingDetailView } from "./FilingDetailView";
import { FilingSearchPanel } from "./FilingSearchPanel";
import { FilingComparisonWorkspace } from "./FilingComparisonWorkspace";
import {
  Layers,
  FileText,
  Calendar,
  Clock,
  PieChart,
  Search,
  GitCompare,
  RefreshCw,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  Building,
} from "lucide-react";

interface FilingsWorkspaceProps {
  companyId: string;
  companyName?: string;
  onNavigateToStatements?: () => void;
  onNavigateToRatios?: () => void;
  onNavigateToEarnings?: () => void;
  onNavigateToOwnership?: () => void;
}

export const FilingsWorkspace: React.FC<FilingsWorkspaceProps> = ({
  companyId,
  companyName = "Company",
  onNavigateToStatements,
  onNavigateToRatios,
  onNavigateToEarnings,
  onNavigateToOwnership,
}) => {
  const {
    activeSubTab,
    setActiveSubTab,
    selectedFilingId,
    setSelectedFilingId,
    overview,
    coverage,
    filings,
    totalFilings,
    selectedFilingDetail,
    selectedFilingContent,
    selectedFilingFacts,
    selectedFilingSources,
    searchQuery,
    setSearchQuery,
    searchHits,
    comparison,
    comparisonLeftId,
    comparisonRightId,
    setComparisonLeftId,
    setComparisonRightId,
    isLoading,
    isDetailLoading,
    isSearching,
    isComparing,
    error,
    refresh,
    selectFiling,
    performSearch,
    runComparison,
  } = useCompanyFilings(companyId);

  const subTabs: { id: FilingsSubTab; label: string; icon: React.ReactNode; count?: number }[] = [
    { id: "overview", label: "Overview", icon: <Layers className="h-3.5 w-3.5" /> },
    { id: "all", label: "All Filings", icon: <FileText className="h-3.5 w-3.5" />, count: totalFilings },
    {
      id: "annual",
      label: "Annual Reports",
      icon: <Calendar className="h-3.5 w-3.5" />,
      count: filings.filter((f) => f.category === "ANNUAL_REPORTS").length,
    },
    {
      id: "quarterly",
      label: "Quarterly Reports",
      icon: <Clock className="h-3.5 w-3.5" />,
      count: filings.filter((f) => f.category === "QUARTERLY_REPORTS").length,
    },
    {
      id: "events",
      label: "Current Events (8-K)",
      icon: <Clock className="h-3.5 w-3.5" />,
      count: filings.filter((f) => f.category === "CURRENT_REPORTS").length,
    },
    {
      id: "ownership",
      label: "Ownership & Insiders",
      icon: <PieChart className="h-3.5 w-3.5" />,
      count: filings.filter((f) => f.category === "OWNERSHIP_INSIDER").length,
    },
    { id: "search", label: "Document Search", icon: <Search className="h-3.5 w-3.5" /> },
    { id: "compare", label: "Filing Comparison", icon: <GitCompare className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="flex flex-col gap-4 p-4 min-h-[600px] bg-background text-foreground">
      {/* Subheader and Refresh Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-foreground tracking-tight">
              Regulatory Filings & Disclosures
            </h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-primary/10 text-primary border border-primary/20">
              Stage 86
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20">
              SEC EDGAR Active
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Verified corporate disclosures, XBRL financial facts, revision histories, and text comparisons for{" "}
            <span className="text-foreground font-semibold">{companyName}</span> (CIK:{" "}
            <span className="font-mono text-foreground">{coverage?.filer_cik || "0000320193"}</span>).
          </p>
        </div>

        {/* Action Controls & Module Links */}
        <div className="flex flex-wrap items-center gap-2">
          {onNavigateToStatements && (
            <button
              type="button"
              onClick={onNavigateToStatements}
              className="px-2.5 py-1 text-xs rounded border border-border bg-card/60 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
            >
              Financial Statements &rarr;
            </button>
          )}

          {onNavigateToRatios && (
            <button
              type="button"
              onClick={onNavigateToRatios}
              className="px-2.5 py-1 text-xs rounded border border-border bg-card/60 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
            >
              Ratios &rarr;
            </button>
          )}

          {onNavigateToEarnings && (
            <button
              type="button"
              onClick={onNavigateToEarnings}
              className="px-2.5 py-1 text-xs rounded border border-border bg-card/60 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
            >
              Earnings &rarr;
            </button>
          )}

          {onNavigateToOwnership && (
            <button
              type="button"
              onClick={onNavigateToOwnership}
              className="px-2.5 py-1 text-xs rounded border border-border bg-card/60 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
            >
              Ownership &rarr;
            </button>
          )}

          <button
            type="button"
            onClick={refresh}
            disabled={isLoading}
            className="p-1.5 rounded border border-border bg-card/60 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer disabled:opacity-50"
            title="Refresh filings"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-3 rounded-lg border border-destructive/40 bg-destructive/10 text-destructive text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Workspace Body */}
      {selectedFilingId && selectedFilingDetail ? (
        /* Selected Filing Detail Viewer */
        <FilingDetailView
          detail={selectedFilingDetail}
          content={selectedFilingContent}
          facts={selectedFilingFacts}
          sources={selectedFilingSources}
          onBack={() => setSelectedFilingId(null)}
          onCompareWith={(otherId) => {
            setComparisonLeftId(selectedFilingId);
            setComparisonRightId(otherId);
            setActiveSubTab("compare");
            setSelectedFilingId(null);
            runComparison(selectedFilingId, otherId);
          }}
        />
      ) : (
        /* Filings Subtab Navigation & Views */
        <div className="space-y-4">
          {/* Subtab Buttons */}
          <div className="flex overflow-x-auto border-b border-border/60 gap-1 pb-1 text-xs font-medium">
            {subTabs.map((tab) => {
              const isActive = activeSubTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveSubTab(tab.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md whitespace-nowrap transition-colors cursor-pointer ${
                    isActive
                      ? "bg-primary text-primary-foreground font-semibold shadow-sm"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  {tab.icon}
                  <span>{tab.label}</span>
                  {tab.count !== undefined && (
                    <span
                      className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                        isActive
                          ? "bg-primary-foreground/20 text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {tab.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Subtab Contents */}
          {activeSubTab === "overview" && (
            <div className="space-y-4">
              <FilingsOverviewCards
                overview={overview}
                coverage={coverage}
                onSelectFiling={(id) => selectFiling(id)}
              />

              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground font-semibold uppercase tracking-wider">
                  <span>Recent Disclosures</span>
                  <button
                    type="button"
                    onClick={() => setActiveSubTab("all")}
                    className="text-primary hover:underline font-mono text-[11px]"
                  >
                    View All ({totalFilings}) &rarr;
                  </button>
                </div>
                <FilingHistoryTable
                  filings={filings.slice(0, 10)}
                  onSelectFiling={(id) => selectFiling(id)}
                  onCompareFilings={(l, r) => {
                    setComparisonLeftId(l);
                    setComparisonRightId(r);
                    setActiveSubTab("compare");
                    runComparison(l, r);
                  }}
                />
              </div>
            </div>
          )}

          {activeSubTab === "all" && (
            <FilingHistoryTable
              filings={filings}
              onSelectFiling={(id) => selectFiling(id)}
              onCompareFilings={(l, r) => {
                setComparisonLeftId(l);
                setComparisonRightId(r);
                setActiveSubTab("compare");
                runComparison(l, r);
              }}
              initialCategory="ALL"
            />
          )}

          {activeSubTab === "annual" && (
            <FilingHistoryTable
              filings={filings.filter((f) => f.category === "ANNUAL_REPORTS")}
              onSelectFiling={(id) => selectFiling(id)}
              onCompareFilings={(l, r) => {
                setComparisonLeftId(l);
                setComparisonRightId(r);
                setActiveSubTab("compare");
                runComparison(l, r);
              }}
              initialCategory="ANNUAL_REPORTS"
            />
          )}

          {activeSubTab === "quarterly" && (
            <FilingHistoryTable
              filings={filings.filter((f) => f.category === "QUARTERLY_REPORTS")}
              onSelectFiling={(id) => selectFiling(id)}
              onCompareFilings={(l, r) => {
                setComparisonLeftId(l);
                setComparisonRightId(r);
                setActiveSubTab("compare");
                runComparison(l, r);
              }}
              initialCategory="QUARTERLY_REPORTS"
            />
          )}

          {activeSubTab === "events" && (
            <FilingHistoryTable
              filings={filings.filter((f) => f.category === "CURRENT_REPORTS")}
              onSelectFiling={(id) => selectFiling(id)}
              onCompareFilings={(l, r) => {
                setComparisonLeftId(l);
                setComparisonRightId(r);
                setActiveSubTab("compare");
                runComparison(l, r);
              }}
              initialCategory="CURRENT_REPORTS"
            />
          )}

          {activeSubTab === "ownership" && (
            <FilingHistoryTable
              filings={filings.filter((f) => f.category === "OWNERSHIP_INSIDER")}
              onSelectFiling={(id) => selectFiling(id)}
              onCompareFilings={(l, r) => {
                setComparisonLeftId(l);
                setComparisonRightId(r);
                setActiveSubTab("compare");
                runComparison(l, r);
              }}
              initialCategory="OWNERSHIP_INSIDER"
            />
          )}

          {activeSubTab === "search" && (
            <FilingSearchPanel
              onSearch={performSearch}
              searchHits={searchHits}
              isSearching={isSearching}
              onSelectFiling={(id) => selectFiling(id)}
            />
          )}

          {activeSubTab === "compare" && (
            <FilingComparisonWorkspace
              filings={filings}
              comparison={comparison}
              leftId={comparisonLeftId}
              rightId={comparisonRightId}
              onSetLeftId={setComparisonLeftId}
              onSetRightId={setComparisonRightId}
              onRunComparison={runComparison}
              isComparing={isComparing}
            />
          )}
        </div>
      )}

      {/* Institutional Audit & Provenance Footer */}
      <div className="mt-auto pt-3 border-t border-border/40 text-[11px] text-muted-foreground flex flex-wrap items-center justify-between gap-2 font-mono">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span>Regulator: U.S. Securities and Exchange Commission (EDGAR API)</span>
          <span>&bull;</span>
          <span>Access Policy: Fair Access (User-Agent Configured)</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Point-in-Time Disclosures</span>
          <span>&bull;</span>
          <span>SHA-256 Digest Verification</span>
        </div>
      </div>
    </div>
  );
};
