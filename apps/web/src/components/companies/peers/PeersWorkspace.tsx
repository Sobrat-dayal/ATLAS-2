"use client";

import React from "react";
import {
  Users,
  Building2,
  TrendingUp,
  DollarSign,
  Compass,
  Layers,
  History,
  FolderKanban,
  Filter,
  RefreshCw,
  HelpCircle,
  ShieldCheck,
  ChevronDown,
} from "lucide-react";
import { useCompanyPeers, PeersSubTab } from "@/hooks/companies/useCompanyPeers";
import { PeersOverviewCards } from "./PeersOverviewCards";
import { PeerCandidateExplorer } from "./PeerCandidateExplorer";
import { PeerGroupManager } from "./PeerGroupManager";
import { PeerFinancialTable } from "./PeerFinancialTable";
import { PeerValuationTable } from "./PeerValuationTable";
import { PeerHistoricalCharts } from "./PeerHistoricalCharts";
import { PeerScatterPlot } from "./PeerScatterPlot";
import { PeerSourceInspector } from "./PeerSourceInspector";
import { PeriodAlignmentMode, OutlierPolicy } from "@/lib/companies/peers";

export interface PeersWorkspaceProps {
  companyId: string;
  companyName: string;
  ticker?: string;
  onNavigateToFinancials?: () => void;
  onNavigateToRatios?: () => void;
  onNavigateToFilings?: () => void;
}

export function PeersWorkspace({
  companyId,
  companyName,
  ticker = "AAPL",
  onNavigateToFinancials,
  onNavigateToRatios,
  onNavigateToFilings,
}: PeersWorkspaceProps) {
  const {
    activeSubTab,
    setActiveSubTab,
    overview,
    candidates,
    competitorsOnly,
    setCompetitorsOnly,
    peerGroups,
    selectedGroupId,
    setSelectedGroupId,
    selectedPeerIds,
    addPeerId,
    removePeerId,
    metricCatalog,
    comparison,
    historical,
    methodology,
    periodAlignmentMode,
    setPeriodAlignmentMode,
    fiscalPeriod,
    setFiscalPeriod,
    outlierPolicy,
    setOutlierPolicy,
    subjectInclusionPolicy,
    setSubjectInclusionPolicy,
    activeInspectorObservation,
    setActiveInspectorObservation,
    isLoading,
    isComparing,
    isMutatingGroup,
    error,
    refreshComparison,
    createGroup,
    updateGroup,
    deleteGroup,
  } = useCompanyPeers(companyId);

  const subTabs: { id: PeersSubTab; label: string; icon: React.ElementType }[] = [
    { id: "overview", label: "Peers Overview", icon: Compass },
    { id: "discovery", label: "Peer Discovery", icon: Users },
    { id: "financial", label: "Financial Comparison", icon: Layers },
    { id: "valuation", label: "Relative Valuation", icon: DollarSign },
    { id: "historical", label: "Historical Trends", icon: History },
    { id: "groups", label: "Peer Groups", icon: FolderKanban },
  ];

  const handleGroupSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedGroupId(val);
    const grp = peerGroups.find((g) => g.id === val);
    if (grp) {
      // Set the peer IDs from this group
      const newPeerIds = grp.peer_company_ids.filter((id) => id !== companyId);
      // Update hook's peer IDs (done by trigger in useCompanyPeers)
    }
  };

  return (
    <div className="flex flex-col h-full bg-atlas-background text-atlas-text-primary p-4 space-y-4">
      {/* Top Controls Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-atlas-surface border border-atlas-border-subtle rounded">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto">
          {subTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`px-3 py-1.5 text-xs rounded transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  isActive
                    ? "bg-atlas-accent text-white font-medium"
                    : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-subtle"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Filters and Controls */}
        <div className="flex items-center gap-2 text-xs">
          {/* Peer Group Selector */}
          <div className="flex items-center gap-1.5 bg-atlas-surface-subtle px-2 py-1 rounded border border-atlas-border-subtle">
            <Users className="w-3.5 h-3.5 text-atlas-text-muted" />
            <select
              value={selectedGroupId || ""}
              onChange={handleGroupSelectChange}
              className="bg-transparent text-xs text-atlas-text-primary focus:outline-none cursor-pointer"
            >
              {peerGroups.map((g) => (
                <option key={g.id} value={g.id} className="bg-atlas-surface text-atlas-text-primary">
                  {g.name} ({g.peer_company_ids.length} peers)
                </option>
              ))}
            </select>
          </div>

          {/* Period Alignment Selector */}
          <div className="flex items-center gap-1.5 bg-atlas-surface-subtle px-2 py-1 rounded border border-atlas-border-subtle">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider font-semibold">Period:</span>
            <select
              value={periodAlignmentMode}
              onChange={(e) => setPeriodAlignmentMode(e.target.value as PeriodAlignmentMode)}
              className="bg-transparent text-xs text-atlas-text-primary focus:outline-none cursor-pointer"
            >
              <option value="LATEST_COMMON_FISCAL_YEAR" className="bg-atlas-surface text-atlas-text-primary">
                Latest Common FY (FY24)
              </option>
              <option value="LATEST_AVAILABLE" className="bg-atlas-surface text-atlas-text-primary">
                Latest Available Period
              </option>
              <option value="QUALIFIED_TTM" className="bg-atlas-surface text-atlas-text-primary">
                Qualified TTM
              </option>
            </select>
          </div>

          {/* Outlier Policy Selector */}
          <div className="hidden md:flex items-center gap-1.5 bg-atlas-surface-subtle px-2 py-1 rounded border border-atlas-border-subtle">
            <span className="text-[10px] text-atlas-text-muted uppercase tracking-wider font-semibold">Outliers:</span>
            <select
              value={outlierPolicy}
              onChange={(e) => setOutlierPolicy(e.target.value as OutlierPolicy)}
              className="bg-transparent text-xs text-atlas-text-primary focus:outline-none cursor-pointer"
            >
              <option value="ALL_VALID_VALUES" className="bg-atlas-surface text-atlas-text-primary">
                All Valid Observations
              </option>
              <option value="EXCLUDE_SELECTED_OUTLIERS" className="bg-atlas-surface text-atlas-text-primary">
                Exclude Statistical Outliers
              </option>
            </select>
          </div>

          {/* Refresh Button */}
          <button
            onClick={() => refreshComparison()}
            disabled={isComparing}
            className="p-1.5 text-atlas-text-muted hover:text-atlas-text-primary rounded border border-atlas-border-subtle hover:bg-atlas-surface-subtle transition-colors disabled:opacity-50"
            title="Refresh Benchmarks"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isComparing ? "animate-spin text-atlas-accent" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Workspace Body */}
      {activeSubTab === "overview" && (
        <div className="space-y-4">
          <PeersOverviewCards
            overview={overview}
            comparison={comparison}
            peerCount={selectedPeerIds.length}
          />
          <PeerScatterPlot comparison={comparison} isLoading={isComparing || isLoading} />
          <PeerFinancialTable
            comparison={comparison}
            metricCatalog={metricCatalog}
            onSelectObservation={(obs) => setActiveInspectorObservation(obs)}
            isLoading={isComparing || isLoading}
          />
        </div>
      )}

      {activeSubTab === "discovery" && (
        <PeerCandidateExplorer
          candidates={candidates}
          selectedPeerIds={selectedPeerIds}
          onAddPeer={addPeerId}
          onRemovePeer={removePeerId}
          competitorsOnly={competitorsOnly}
          onToggleCompetitorsOnly={setCompetitorsOnly}
        />
      )}

      {activeSubTab === "financial" && (
        <div className="space-y-4">
          <PeerFinancialTable
            comparison={comparison}
            metricCatalog={metricCatalog}
            onSelectObservation={(obs) => setActiveInspectorObservation(obs)}
            isLoading={isComparing || isLoading}
          />
        </div>
      )}

      {activeSubTab === "valuation" && (
        <div className="space-y-4">
          <PeerValuationTable
            comparison={comparison}
            metricCatalog={metricCatalog}
            onSelectObservation={(obs) => setActiveInspectorObservation(obs)}
            isLoading={isComparing || isLoading}
          />
        </div>
      )}

      {activeSubTab === "historical" && (
        <div className="space-y-4">
          <PeerHistoricalCharts historical={historical} isLoading={isComparing || isLoading} />
        </div>
      )}

      {activeSubTab === "groups" && (
        <PeerGroupManager
          peerGroups={peerGroups}
          selectedGroupId={selectedGroupId}
          onSelectGroup={(id) => setSelectedGroupId(id)}
          candidates={candidates}
          onCreateGroup={createGroup}
          onUpdateGroup={updateGroup}
          onDeleteGroup={deleteGroup}
          isMutating={isMutatingGroup}
        />
      )}

      {/* Cell Observation Inspector Modal */}
      {activeInspectorObservation && (
        <PeerSourceInspector
          observation={activeInspectorObservation}
          onClose={() => setActiveInspectorObservation(null)}
        />
      )}

      {/* Institutional Methodology & Boundaries Footer */}
      <div className="pt-3 border-t border-atlas-border-subtle flex flex-wrap items-center justify-between gap-2 text-[11px] text-atlas-text-muted">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>
            Stage 87 Institutional Peer Benchmarking Engine. Methodologies adhere to canonical financial reporting and valuation standards.
          </span>
        </div>
        <div className="flex items-center gap-3">
          {onNavigateToFinancials && (
            <button
              onClick={onNavigateToFinancials}
              className="text-atlas-accent hover:underline text-[11px]"
            >
              Financial Statements →
            </button>
          )}
          {onNavigateToRatios && (
            <button
              onClick={onNavigateToRatios}
              className="text-atlas-accent hover:underline text-[11px]"
            >
              Financial Ratios →
            </button>
          )}
          {onNavigateToFilings && (
            <button
              onClick={onNavigateToFilings}
              className="text-atlas-accent hover:underline text-[11px]"
            >
              SEC Filings →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
