"use client";

import React from "react";
import {
  OwnershipSubTab,
  useCompanyOwnership,
} from "@/hooks/companies/useCompanyOwnership";
import { OwnershipOverviewCards } from "./OwnershipOverviewCards";
import { InstitutionalHoldersTable } from "./InstitutionalHoldersTable";
import { InsiderHoldingsTable } from "./InsiderHoldingsTable";
import { BeneficialOwnersTable } from "./BeneficialOwnersTable";
import { ShareholdingPatternPanel } from "./ShareholdingPatternPanel";
import { OwnershipHistoryChart } from "./OwnershipHistoryChart";
import { OwnershipChangesTable } from "./OwnershipChangesTable";
import {
  Layers,
  Building,
  UserCheck,
  ShieldCheck,
  PieChart,
  History,
  TrendingUp,
  RefreshCw,
  AlertCircle,
  Shield,
  ExternalLink,
  ChevronDown,
} from "lucide-react";

interface OwnershipWorkspaceProps {
  companyId: string;
  companyName?: string;
  onNavigateToOverview?: () => void;
  onNavigateToFinancials?: () => void;
  onNavigateToRatios?: () => void;
  onNavigateToEarnings?: () => void;
}

export const OwnershipWorkspace: React.FC<OwnershipWorkspaceProps> = ({
  companyId,
  companyName = "Company",
  onNavigateToOverview,
  onNavigateToFinancials,
  onNavigateToRatios,
  onNavigateToEarnings,
}) => {
  const {
    activeSubTab,
    setActiveSubTab,
    selectedSecurityId,
    setSelectedSecurityId,
    selectedPeriod,
    setSelectedPeriod,
    overview,
    institutions,
    insiders,
    beneficialOwners,
    patterns,
    historySnapshots,
    changes,
    isLoading,
    error,
    refresh,
  } = useCompanyOwnership(companyId);

  const subTabs: { id: OwnershipSubTab; label: string; icon: React.ReactNode; count?: number }[] = [
    { id: "overview", label: "Overview", icon: <Layers className="h-3.5 w-3.5" /> },
    {
      id: "institutional",
      label: "Institutional Holders",
      icon: <Building className="h-3.5 w-3.5" />,
      count: institutions.length,
    },
    {
      id: "insiders",
      label: "Insider Holdings",
      icon: <UserCheck className="h-3.5 w-3.5" />,
      count: insiders.length,
    },
    {
      id: "beneficial",
      label: "Beneficial Ownership",
      icon: <ShieldCheck className="h-3.5 w-3.5" />,
      count: beneficialOwners.length,
    },
    {
      id: "patterns",
      label: "Shareholding Patterns",
      icon: <PieChart className="h-3.5 w-3.5" />,
    },
    {
      id: "history",
      label: "Historical Snapshots",
      icon: <History className="h-3.5 w-3.5" />,
      count: historySnapshots.length,
    },
    {
      id: "changes",
      label: "Position Changes",
      icon: <TrendingUp className="h-3.5 w-3.5" />,
      count: changes.length,
    },
  ];

  if (error && !overview && institutions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-border/60 rounded-lg bg-card/40 my-6">
        <AlertCircle className="h-10 w-10 text-rose-500 mb-3" />
        <h3 className="text-base font-semibold text-foreground">
          Unable to Load Ownership Intelligence
        </h3>
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
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-border/60 pb-3">
        {/* Navigation Subtabs */}
        <div className="flex flex-wrap items-center gap-1 bg-muted/30 p-1 rounded-lg border border-border/50">
          {subTabs.map((tab) => {
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  isActive
                    ? "bg-card text-foreground shadow-xs border border-border/60 font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/40"
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {tab.count !== undefined && tab.count > 0 && (
                  <span className="ml-1 text-[10px] text-muted-foreground bg-muted/60 px-1.5 py-0.2 rounded-full font-mono">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Security and Period Controls */}
        <div className="flex items-center gap-2">
          {/* Share Class Selector */}
          {overview?.available_securities && overview.available_securities.length > 0 && (
            <div className="relative">
              <select
                value={selectedSecurityId || overview.selected_security?.security_id}
                onChange={(e) => setSelectedSecurityId(e.target.value)}
                className="appearance-none pl-3 pr-8 py-1.5 text-xs rounded-md bg-muted/40 border border-border/60 text-foreground font-medium focus:outline-none focus:ring-1 focus:ring-primary"
              >
                {overview.available_securities.map((sec) => (
                  <option key={sec.security_id} value={sec.security_id}>
                    {sec.security_name} ({sec.ticker || "N/A"})
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
            </div>
          )}

          {/* Period Selector */}
          {historySnapshots.length > 0 && (
            <div className="relative">
              <select
                value={selectedPeriod || overview?.reporting_period}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="appearance-none pl-3 pr-8 py-1.5 text-xs rounded-md bg-muted/40 border border-border/60 text-foreground font-mono focus:outline-none focus:ring-1 focus:ring-primary"
              >
                {historySnapshots.map((s) => (
                  <option key={s.reporting_period} value={s.reporting_period}>
                    {s.reporting_period} ({s.reporting_date})
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
            </div>
          )}

          <button
            onClick={refresh}
            disabled={isLoading}
            className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-md border border-border/60 bg-muted/40 text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-colors"
            title="Refresh ownership records"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      {overview && (
        <>
          {activeSubTab === "overview" && (
            <div className="space-y-4">
              {/* Executive Metrics Cards */}
              <OwnershipOverviewCards overview={overview} />

              {/* Top Disclosed Holders Table & Shareholding Pattern */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Left 2 Cols: Top 10 Disclosed Holders */}
                <div className="lg:col-span-2 space-y-2">
                  <div className="flex items-center justify-between border-b border-border/50 pb-2">
                    <span className="font-semibold text-xs text-foreground">
                      Top 10 Disclosed Shareholders ({overview.reporting_period})
                    </span>
                    <button
                      onClick={() => setActiveSubTab("institutional")}
                      className="text-[11px] text-primary hover:underline font-medium"
                    >
                      View All Institutional Holders →
                    </button>
                  </div>

                  <div className="overflow-x-auto rounded-lg border border-border/60 bg-card/40">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-muted/50 border-b border-border/60 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                        <tr>
                          <th className="py-2 px-3 w-10 text-center">#</th>
                          <th className="py-2 px-3">Shareholder Entity</th>
                          <th className="py-2 px-3">Category</th>
                          <th className="py-2 px-3 text-right">Shares Held</th>
                          <th className="py-2 px-3 text-right">% Stake</th>
                          <th className="py-2 px-3 text-right">Indicative Value</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/40">
                        {overview.top_holders.map((pos, idx) => (
                          <tr key={pos.position_id} className="hover:bg-muted/20 transition-colors">
                            <td className="py-2 px-3 text-center font-mono text-[11px] text-muted-foreground">
                              {idx + 1}
                            </td>
                            <td className="py-2 px-3">
                              <div className="font-semibold text-foreground truncate max-w-[200px]" title={pos.holder.name}>
                                {pos.holder.name}
                              </div>
                              <div className="text-[10px] text-muted-foreground font-mono">
                                {pos.holder.country || "United States"}
                              </div>
                            </td>
                            <td className="py-2 px-3 font-mono text-[11px] text-muted-foreground">
                              {pos.holder.category.replace(/_/g, " ")}
                            </td>
                            <td className="py-2 px-3 text-right font-mono font-medium text-foreground">
                              {pos.formatted_shares}
                            </td>
                            <td className="py-2 px-3 text-right font-mono font-bold text-primary">
                              {pos.formatted_percentage || "N/A"}
                            </td>
                            <td className="py-2 px-3 text-right font-mono text-muted-foreground">
                              {pos.formatted_market_value || "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Right Col: Macro Pattern Preview */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between border-b border-border/50 pb-2">
                    <span className="font-semibold text-xs text-foreground">Pattern Overview</span>
                    <button
                      onClick={() => setActiveSubTab("patterns")}
                      className="text-[11px] text-primary hover:underline font-medium"
                    >
                      Details →
                    </button>
                  </div>
                  <ShareholdingPatternPanel patterns={overview.patterns || null} />
                </div>
              </div>
            </div>
          )}

          {activeSubTab === "institutional" && (
            <InstitutionalHoldersTable
              items={institutions}
              reportingPeriod={overview.reporting_period}
            />
          )}

          {activeSubTab === "insiders" && (
            <InsiderHoldingsTable
              items={insiders}
              reportingPeriod={overview.reporting_period}
            />
          )}

          {activeSubTab === "beneficial" && (
            <BeneficialOwnersTable
              items={beneficialOwners}
              reportingPeriod={overview.reporting_period}
            />
          )}

          {activeSubTab === "patterns" && (
            <ShareholdingPatternPanel patterns={overview.patterns || patterns} />
          )}

          {activeSubTab === "history" && (
            <OwnershipHistoryChart
              snapshots={historySnapshots}
              selectedPeriod={selectedPeriod}
              onSelectPeriod={(p) => setSelectedPeriod(p)}
            />
          )}

          {activeSubTab === "changes" && (
            <OwnershipChangesTable
              items={changes}
              currentPeriod={selectedPeriod || overview.reporting_period}
              priorPeriod="2024-Q2"
            />
          )}
        </>
      )}

      {/* Institutional Provenance & Methodology Footer */}
      <div className="mt-8 pt-4 border-t border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <Shield className="h-4 w-4 text-primary" />
          <span className="font-semibold text-foreground">
            ATLAS Stage 85 Company Ownership Intelligence
          </span>
          <span>•</span>
          <span className="font-mono text-[11px]">SEC 13F / 13G / Form 4 Compliant</span>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-[11px]">
          {onNavigateToOverview && (
            <button onClick={onNavigateToOverview} className="hover:text-primary transition-colors">
              Company Overview
            </button>
          )}
          {onNavigateToFinancials && (
            <button onClick={onNavigateToFinancials} className="hover:text-primary transition-colors">
              Financial Statements
            </button>
          )}
          {onNavigateToRatios && (
            <button onClick={onNavigateToRatios} className="hover:text-primary transition-colors">
              Financial Ratios
            </button>
          )}
          {onNavigateToEarnings && (
            <button onClick={onNavigateToEarnings} className="hover:text-primary transition-colors">
              Earnings
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
