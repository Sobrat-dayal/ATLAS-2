"use client";

import React from "react";
import {
  Globe,
  Sliders,
  Target,
  Users,
  FileText,
  Mic,
  Banknote,
  History,
  ShieldCheck,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";
import { CentralBankSectionTab, useCentralBanks } from "@/hooks/economics/useCentralBanks";
import { CentralBankSelector } from "./CentralBankSelector";
import { CentralBankOverviewPanel } from "./CentralBankOverviewPanel";
import { PolicyRatesPanel } from "./PolicyRatesPanel";
import { DecisionsPanel } from "./DecisionsPanel";
import { MeetingsPanel } from "./MeetingsPanel";
import { PublicationsPanel } from "./PublicationsPanel";
import { SpeechesPanel } from "./SpeechesPanel";
import { BalanceSheetPanel } from "./BalanceSheetPanel";
import { PolicyTimelinePanel } from "./PolicyTimelinePanel";
import { CentralBankCoveragePanel } from "./CentralBankCoveragePanel";

interface CentralBanksWorkspaceProps {
  initialBankId?: string;
}

export function CentralBanksWorkspace({ initialBankId = "cb-fed" }: CentralBanksWorkspaceProps) {
  const {
    selectedBankId,
    selectCentralBank,
    activeTab,
    setActiveTab,
    institutions,
    overview,
    instruments,
    decisions,
    selectedDecisionId,
    selectDecision,
    meetings,
    selectedMeetingId,
    selectMeeting,
    selectedVotingRecord,
    publications,
    selectedPublicationId,
    selectPublication,
    speeches,
    balanceSheet,
    programs,
    timeline,
    coverage,
    isLoading,
    error,
    refresh,
  } = useCentralBanks(initialBankId);

  const tabs: { id: CentralBankSectionTab; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Overview", icon: <Globe className="w-3.5 h-3.5" /> },
    { id: "rates", label: "Policy Rates", icon: <Sliders className="w-3.5 h-3.5" /> },
    { id: "decisions", label: "Decisions", icon: <Target className="w-3.5 h-3.5" /> },
    { id: "meetings", label: "Meetings & Votes", icon: <Users className="w-3.5 h-3.5" /> },
    { id: "publications", label: "Publications", icon: <FileText className="w-3.5 h-3.5" /> },
    { id: "speeches", label: "Speeches", icon: <Mic className="w-3.5 h-3.5" /> },
    { id: "balance-sheet", label: "Balance Sheet & QE", icon: <Banknote className="w-3.5 h-3.5" /> },
    { id: "timeline", label: "Timeline", icon: <History className="w-3.5 h-3.5" /> },
    { id: "coverage", label: "Coverage", icon: <ShieldCheck className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="space-y-5">
      {/* 1. Central Bank Selector Bar */}
      <CentralBankSelector
        institutions={institutions}
        selectedBankId={selectedBankId}
        onSelectBank={selectCentralBank}
      />

      {/* 2. Central Bank Navigation Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-atlas-border-subtle pb-2">
        <nav className="flex items-center gap-1 overflow-x-auto text-xs pb-1 sm:pb-0">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-colors shrink-0 ${
                  isActive
                    ? "bg-atlas-surface text-atlas-text-primary shadow-xs font-semibold border border-atlas-border-subtle"
                    : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface/50"
                }`}
              >
                <span className={isActive ? "text-atlas-accent" : "text-atlas-text-muted"}>
                  {tab.icon}
                </span>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        <button
          onClick={refresh}
          disabled={isLoading}
          className="self-end sm:self-auto flex items-center gap-1.5 px-2.5 py-1 text-xs bg-atlas-background hover:bg-atlas-surface border border-atlas-border-subtle rounded text-atlas-text-muted hover:text-atlas-text-primary transition-colors disabled:opacity-50"
          title="Refresh Central Bank Data"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* 3. Error Alert */}
      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded flex items-center gap-2 text-xs text-rose-400">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 4. Active Tab Content */}
      {isLoading && !overview ? (
        <div className="p-12 text-center text-xs text-atlas-text-muted flex flex-col items-center gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-atlas-accent" />
          <span>Loading central bank intelligence...</span>
        </div>
      ) : (
        <div>
          {activeTab === "overview" && overview && (
            <CentralBankOverviewPanel
              overview={overview}
              onNavigateTab={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === "rates" && (
            <PolicyRatesPanel instruments={instruments} />
          )}

          {activeTab === "decisions" && (
            <DecisionsPanel
              decisions={decisions}
              selectedDecisionId={selectedDecisionId}
              onSelectDecision={selectDecision}
            />
          )}

          {activeTab === "meetings" && (
            <MeetingsPanel
              meetings={meetings}
              selectedMeetingId={selectedMeetingId}
              onSelectMeeting={selectMeeting}
              votingRecord={selectedVotingRecord}
            />
          )}

          {activeTab === "publications" && (
            <PublicationsPanel
              publications={publications}
              selectedPublicationId={selectedPublicationId}
              onSelectPublication={selectPublication}
            />
          )}

          {activeTab === "speeches" && (
            <SpeechesPanel speeches={speeches} />
          )}

          {activeTab === "balance-sheet" && (
            <BalanceSheetPanel
              balanceSheet={balanceSheet}
              programs={programs}
            />
          )}

          {activeTab === "timeline" && (
            <PolicyTimelinePanel timeline={timeline} />
          )}

          {activeTab === "coverage" && (
            <CentralBankCoveragePanel coverage={coverage} />
          )}
        </div>
      )}
    </div>
  );
}
