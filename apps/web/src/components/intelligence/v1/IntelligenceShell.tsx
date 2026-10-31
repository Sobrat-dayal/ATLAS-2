"use client";

import React, { useState, useEffect } from "react";
import { IntelligenceViewType, IntelligenceSearchResult } from "@/lib/intelligence/v1/types";
import { fetchSourcesStatus } from "@/lib/intelligence/v1/api";
import { IntelligenceToolbar } from "./IntelligenceToolbar";
import { IntelligenceOverview } from "./IntelligenceOverview";
import { IntelligenceEntityView } from "./IntelligenceEntityView";
import { IntelligenceGeographyView } from "./IntelligenceGeographyView";
import { IntelligenceHistoricalView } from "./IntelligenceHistoricalView";
import { IntelligenceSourcesView } from "./IntelligenceSourcesView";
import { IntelligenceInvestigationWorkspace } from "./IntelligenceInvestigationWorkspace";
import { IntelligenceSearchModal } from "./IntelligenceSearchModal";
import { IntelligenceScoringView } from "@/components/intelligence/scoring";

// Stage 135-137 Subsystem Integrations
import { UniversalEventExplorer } from "@/components/events/UniversalEventExplorer";
import { EventEntityGraphExplorer } from "@/components/intelligence/graph/EventEntityGraphExplorer";
import { ExposureExplorer } from "@/components/intelligence/exposure/ExposureExplorer";

export function IntelligenceShell() {
  const [activeView, setActiveView] = useState<IntelligenceViewType>("OVERVIEW");
  const [asOfDate, setAsOfDate] = useState<string | null>(null);
  const [searchModalOpen, setSearchModalOpen] = useState(false);
  const [selectedEntityId, setSelectedEntityId] = useState<string>("COMP_AAPL");
  const [selectedEventId, setSelectedEventId] = useState<string | undefined>(undefined);
  const [degradedSourceCount, setDegradedSourceCount] = useState<number>(0);

  // Keyboard shortcut Ctrl+K / Cmd+K to open unified search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchModalOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Poll or check source health once on mount
  useEffect(() => {
    fetchSourcesStatus()
      .then((sources) => {
        const degraded = sources.filter((s) => s.status !== "READY").length;
        setDegradedSourceCount(degraded);
      })
      .catch(() => {
        // Fallback gracefully without throwing
      });
  }, []);

  const handleNavigateToView = (view: string, entityOrEventId?: string) => {
    const upper = view.toUpperCase();
    if (upper.includes("SCORE") || upper.includes("PRIOR")) {
      setActiveView("SCORING");
      if (entityOrEventId) setSelectedEventId(entityOrEventId);
    } else if (upper.includes("EVENT")) {
      setActiveView("EVENTS");
      if (entityOrEventId) setSelectedEventId(entityOrEventId);
    } else if (upper.includes("ENTIT")) {
      setActiveView("ENTITIES");
      if (entityOrEventId) setSelectedEntityId(entityOrEventId);
    } else if (upper.includes("GRAPH")) {
      setActiveView("GRAPH");
      if (entityOrEventId) setSelectedEntityId(entityOrEventId);
    } else if (upper.includes("EXPOS")) {
      setActiveView("EXPOSURE");
      if (entityOrEventId) setSelectedEntityId(entityOrEventId);
    } else if (upper.includes("GEO") || upper.includes("MAP")) {
      setActiveView("GEOGRAPHY");
      if (entityOrEventId) setSelectedEventId(entityOrEventId);
    } else if (upper.includes("INVEST")) {
      setActiveView("INVESTIGATIONS");
    } else if (upper.includes("HIST")) {
      setActiveView("HISTORY");
    } else if (upper.includes("SOURCE") || upper.includes("QUAL")) {
      setActiveView("SOURCES");
    } else {
      setActiveView("OVERVIEW");
    }
  };

  const handleSelectSearchResult = (result: IntelligenceSearchResult) => {
    setSearchModalOpen(false);
    if (result.result_type === "ENTITY") {
      setSelectedEntityId(result.canonical_id);
      setActiveView("ENTITIES");
    } else if (result.result_type === "EVENT") {
      setSelectedEventId(result.canonical_id);
      setActiveView("EVENTS");
    } else if (result.result_type === "SOURCE") {
      setActiveView("SOURCES");
    } else {
      setActiveView("OVERVIEW");
    }
  };

  return (
    <div className="flex h-full flex-col bg-black text-zinc-100 overflow-hidden font-mono text-xs select-none">
      {/* Intelligence V1 Master Toolbar */}
      <IntelligenceToolbar
        activeView={activeView}
        onSelectView={setActiveView}
        onOpenSearch={() => setSearchModalOpen(true)}
        asOfDate={asOfDate}
        degradedSourceCount={degradedSourceCount}
      />

      {/* Primary Intelligence Workspace Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {activeView === "OVERVIEW" && (
          <IntelligenceOverview
            onNavigateToView={handleNavigateToView}
            asOfDate={asOfDate}
          />
        )}

        {activeView === "EVENTS" && (
          <div className="h-full overflow-y-auto">
            <UniversalEventExplorer />
          </div>
        )}

        {activeView === "SCORING" && (
          <IntelligenceScoringView
            asOfDate={asOfDate}
            onNavigateToView={handleNavigateToView}
          />
        )}

        {activeView === "ENTITIES" && (
          <IntelligenceEntityView
            initialEntityId={selectedEntityId}
            onNavigateToView={handleNavigateToView}
          />
        )}

        {activeView === "GRAPH" && (
          <div className="h-full overflow-hidden">
            <EventEntityGraphExplorer />
          </div>
        )}

        {activeView === "EXPOSURE" && (
          <div className="h-full overflow-hidden">
            <ExposureExplorer />
          </div>
        )}

        {activeView === "GEOGRAPHY" && (
          <IntelligenceGeographyView
            initialEventId={selectedEventId}
            onNavigateToView={handleNavigateToView}
          />
        )}

        {activeView === "INVESTIGATIONS" && (
          <IntelligenceInvestigationWorkspace
            onNavigateToView={handleNavigateToView}
          />
        )}

        {activeView === "HISTORY" && (
          <IntelligenceHistoricalView
            asOfDate={asOfDate}
            onSetAsOfDate={setAsOfDate}
          />
        )}

        {activeView === "SOURCES" && (
          <IntelligenceSourcesView />
        )}
      </div>

      {/* Unified Fast Search Modal */}
      <IntelligenceSearchModal
        isOpen={searchModalOpen}
        onClose={() => setSearchModalOpen(false)}
        onSelectResult={handleSelectSearchResult}
      />
    </div>
  );
}

