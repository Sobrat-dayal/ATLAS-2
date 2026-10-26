"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getEarningsCalls,
  getEarningsEvents,
  getEarningsHistory,
  getEarningsOverview,
  getManagementGuidance,
} from "@/lib/companies/earnings/api";
import {
  CompanyEarningsOverviewDTO,
  EarningsCallDTO,
  EarningsEventDTO,
  EarningsPeriodType,
  ManagementGuidanceDTO,
  QuarterlyEarningsItemDTO,
} from "@/lib/companies/earnings/types";

export type EarningsSubTab = "overview" | "history" | "guidance" | "calls";

export interface UseCompanyEarningsOptions {
  initialSubTab?: EarningsSubTab;
  initialPeriodType?: EarningsPeriodType;
}

export function useCompanyEarnings(
  companyId: string | null,
  options: UseCompanyEarningsOptions = {}
) {
  const [activeSubTab, setActiveSubTab] = useState<EarningsSubTab>(
    options.initialSubTab || "overview"
  );
  const [periodType, setPeriodType] = useState<EarningsPeriodType>(
    options.initialPeriodType || "QUARTERLY"
  );

  const [overview, setOverview] = useState<CompanyEarningsOverviewDTO | null>(null);
  const [historyItems, setHistoryItems] = useState<QuarterlyEarningsItemDTO[]>([]);
  const [events, setEvents] = useState<EarningsEventDTO[]>([]);
  const [guidance, setGuidance] = useState<ManagementGuidanceDTO[]>([]);
  const [calls, setCalls] = useState<EarningsCallDTO[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Inspector / modal state
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const fetchEarningsData = useCallback(async () => {
    if (!companyId) return;
    setIsLoading(true);
    setError(null);

    try {
      const [ov, hist, evts, guid, clls] = await Promise.all([
        getEarningsOverview(companyId).catch(() => null),
        getEarningsHistory(companyId, periodType, 20).catch(() => null),
        getEarningsEvents(companyId).catch(() => null),
        getManagementGuidance(companyId).catch(() => null),
        getEarningsCalls(companyId).catch(() => null),
      ]);

      if (ov) setOverview(ov);
      if (hist) setHistoryItems(hist.items);
      if (evts) setEvents(evts.events);
      if (guid) setGuidance(guid.guidance_items);
      if (clls) setCalls(clls.calls);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load company earnings";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [companyId, periodType]);

  useEffect(() => {
    fetchEarningsData();
  }, [fetchEarningsData]);

  return {
    activeSubTab,
    setActiveSubTab,
    periodType,
    setPeriodType,
    overview,
    historyItems,
    events,
    guidance,
    calls,
    isLoading,
    error,
    refresh: fetchEarningsData,
    selectedEventId,
    setSelectedEventId,
  };
}
