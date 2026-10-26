"use client";

import React, { useState } from "react";
import { useEconomicCalendar } from "@/hooks/economics/useEconomicCalendar";
import { EconomicCalendarToolbar } from "./EconomicCalendarToolbar";
import { EconomicCalendarCoveragePanel } from "./EconomicCalendarCoveragePanel";
import { EconomicEventTable } from "./EconomicEventTable";
import { EconomicEventDetailModal } from "./EconomicEventDetailModal";
import { EconomicCalendarAlertsModal } from "./EconomicCalendarAlertsModal";
import { EconomicCalendarEventDTO } from "@/lib/economics/calendar";
import { Calendar, AlertTriangle, ShieldCheck } from "lucide-react";

export function EconomicCalendarWorkspace() {
  const {
    events,
    totalEvents,
    categories,
    supportedGeographies,
    coverage,
    alerts,
    deliveryHistory,

    viewPreset,
    setViewPreset,
    selectedTimezone,
    setSelectedTimezone,
    selectedGeography,
    setSelectedGeography,
    selectedCategory,
    setSelectedCategory,
    selectedImportance,
    setSelectedImportance,
    selectedStatus,
    setSelectedStatus,
    searchQuery,
    setSearchQuery,

    selectedEventId,
    selectedEventDetail,
    isDetailModalOpen,
    openEventDetail,
    closeEventDetail,

    isAlertsModalOpen,
    openAlertsModal,
    closeAlertsModal,
    addAlert,
    toggleAlertEnabled,
    removeAlert,

    isCoverageOpen,
    setIsCoverageOpen,

    isLoading,
    isDetailLoading,
    error,
    refresh,
  } = useEconomicCalendar();

  const [preselectedAlertEvent, setPreselectedAlertEvent] =
    useState<EconomicCalendarEventDTO | null>(null);

  const handleOpenAlertForEvent = (event: EconomicCalendarEventDTO) => {
    setPreselectedAlertEvent(event);
    openAlertsModal();
  };

  const handleCloseAlertsModal = () => {
    closeAlertsModal();
    setPreselectedAlertEvent(null);
  };

  const hasAlertForEvent = (eventId: string) => {
    return alerts.some((a) => a.event_id === eventId && a.is_enabled);
  };

  return (
    <div className="space-y-4">
      {/* Top Workspace Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-atlas-border-subtle pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold text-atlas-text-primary tracking-tight">
              Global Economic Calendar
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              STAGE 92 VERIFIED RELEASES
            </span>
          </div>
          <p className="text-xs text-atlas-text-muted mt-0.5">
            Verified Macroeconomic Schedules, Central Bank Decisions, Pre-Release Consensus & Statistical Surprises
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs text-atlas-text-muted font-mono">
          <span>
            {totalEvents} {totalEvents === 1 ? "release" : "releases"} active
          </span>
          <span>•</span>
          <span className="text-emerald-400 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            Official Sources Verified
          </span>
        </div>
      </div>

      {/* Error Alert (if any) */}
      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded flex items-center gap-2 text-xs text-rose-400">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Toolbar Controls */}
      <EconomicCalendarToolbar
        viewPreset={viewPreset}
        onSelectPreset={setViewPreset}
        selectedTimezone={selectedTimezone}
        onSelectTimezone={setSelectedTimezone}
        selectedGeography={selectedGeography}
        onSelectGeography={setSelectedGeography}
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
        selectedImportance={selectedImportance}
        onSelectImportance={setSelectedImportance}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        categories={categories}
        supportedGeographies={supportedGeographies}
        totalAlertsCount={alerts.filter((a) => a.is_enabled).length}
        onOpenAlerts={openAlertsModal}
        isCoverageOpen={isCoverageOpen}
        onToggleCoverage={() => setIsCoverageOpen(!isCoverageOpen)}
        isLoading={isLoading}
        onRefresh={refresh}
      />

      {/* Coverage & Source Precision Drawer */}
      <EconomicCalendarCoveragePanel
        coverage={coverage}
        isOpen={isCoverageOpen}
        onClose={() => setIsCoverageOpen(false)}
      />

      {/* Main Events Table */}
      <EconomicEventTable
        events={events}
        alerts={alerts}
        isLoading={isLoading}
        onOpenDetail={openEventDetail}
        onToggleAlert={handleOpenAlertForEvent}
      />

      {/* Event Details Inspector Modal */}
      <EconomicEventDetailModal
        isOpen={isDetailModalOpen}
        onClose={closeEventDetail}
        detail={selectedEventDetail}
        isLoading={isDetailLoading}
        onToggleAlert={handleOpenAlertForEvent}
        hasAlert={selectedEventId ? hasAlertForEvent(selectedEventId) : false}
      />

      {/* User Alerts & Notification Outbox Modal */}
      <EconomicCalendarAlertsModal
        isOpen={isAlertsModalOpen}
        onClose={handleCloseAlertsModal}
        alerts={alerts}
        deliveryHistory={deliveryHistory}
        onToggleEnabled={toggleAlertEnabled}
        onRemoveAlert={removeAlert}
        onCreateAlert={addAlert}
        events={events}
        preselectedEvent={preselectedAlertEvent}
      />
    </div>
  );
}
