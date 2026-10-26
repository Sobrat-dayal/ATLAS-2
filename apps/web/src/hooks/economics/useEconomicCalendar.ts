"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertDeliveryIntentDTO,
  CalendarViewPreset,
  CreateEventAlertRequestDTO,
  EconomicCalendarCoverageDTO,
  EconomicCalendarEventDetailDTO,
  EconomicCalendarEventDTO,
  EconomicCalendarResponseDTO,
  UserEventAlertDTO,
  createEventAlert,
  deleteEventAlert,
  getAlertDeliveryHistory,
  getCalendarCoverage,
  getCalendarEventDetail,
  getCalendarEvents,
  getUserAlerts,
  updateEventAlert,
} from "@/lib/economics/calendar";

export interface UseEconomicCalendarReturn {
  // Calendar data
  events: EconomicCalendarEventDTO[];
  totalEvents: number;
  categories: string[];
  supportedGeographies: string[];
  coverage: EconomicCalendarCoverageDTO | null;
  alerts: UserEventAlertDTO[];
  deliveryHistory: AlertDeliveryIntentDTO[];

  // Filter & View States
  viewPreset: CalendarViewPreset;
  setViewPreset: (preset: CalendarViewPreset) => void;
  selectedTimezone: string;
  setSelectedTimezone: (tz: string) => void;
  selectedGeography: string | null;
  setSelectedGeography: (geo: string | null) => void;
  selectedCategory: string | null;
  setSelectedCategory: (cat: string | null) => void;
  selectedImportance: string | null;
  setSelectedImportance: (imp: string | null) => void;
  selectedStatus: string | null;
  setSelectedStatus: (status: string | null) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  startDate: string | null;
  endDate: string | null;
  setDateRange: (start: string | null, end: string | null) => void;

  // Selected Event & Detail
  selectedEventId: string | null;
  selectedEventDetail: EconomicCalendarEventDetailDTO | null;
  isDetailModalOpen: boolean;
  openEventDetail: (eventId: string) => Promise<void>;
  closeEventDetail: () => void;

  // Alert Management Modals & Actions
  isAlertsModalOpen: boolean;
  openAlertsModal: () => void;
  closeAlertsModal: () => void;
  addAlert: (payload: CreateEventAlertRequestDTO) => Promise<UserEventAlertDTO | null>;
  toggleAlertEnabled: (alertId: string, enabled: boolean) => Promise<void>;
  removeAlert: (alertId: string) => Promise<boolean>;

  // Coverage Panel State
  isCoverageOpen: boolean;
  setIsCoverageOpen: (open: boolean) => void;

  // Status & Actions
  isLoading: boolean;
  isDetailLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useEconomicCalendar(): UseEconomicCalendarReturn {
  const [events, setEvents] = useState<EconomicCalendarEventDTO[]>([]);
  const [totalEvents, setTotalEvents] = useState<number>(0);
  const [categories, setCategories] = useState<string[]>([]);
  const [supportedGeographies, setSupportedGeographies] = useState<string[]>([]);
  const [coverage, setCoverage] = useState<EconomicCalendarCoverageDTO | null>(null);
  const [alerts, setAlerts] = useState<UserEventAlertDTO[]>([]);
  const [deliveryHistory, setDeliveryHistory] = useState<AlertDeliveryIntentDTO[]>([]);

  // Filters
  const [viewPreset, setViewPreset] = useState<CalendarViewPreset>("all");
  const [selectedTimezone, setSelectedTimezone] = useState<string>("UTC");
  const [selectedGeography, setSelectedGeography] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedImportance, setSelectedImportance] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [startDate, setStartDate] = useState<string | null>(null);
  const [endDate, setEndDate] = useState<string | null>(null);

  // Detail Modal
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedEventDetail, setSelectedEventDetail] = useState<EconomicCalendarEventDetailDTO | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState<boolean>(false);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(false);

  // Alert Modal
  const [isAlertsModalOpen, setIsAlertsModalOpen] = useState<boolean>(false);

  // Coverage Panel
  const [isCoverageOpen, setIsCoverageOpen] = useState<boolean>(false);

  // Loading / Error
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCalendar = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const res = await getCalendarEvents({
        display_timezone: selectedTimezone,
        view_preset: viewPreset,
        geography_id: selectedGeography || undefined,
        category: selectedCategory || undefined,
        importance: selectedImportance || undefined,
        status: selectedStatus || undefined,
        search: searchQuery.trim() || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });

      setEvents(res.events || []);
      setTotalEvents(res.context?.total_events || res.events?.length || 0);
      setCategories(res.categories || []);
      setSupportedGeographies(res.supported_geographies || []);
    } catch (err) {
      console.error("Failed to load economic calendar:", err);
      setError(err instanceof Error ? err.message : "Failed to load calendar");
    } finally {
      setIsLoading(false);
    }
  }, [
    selectedTimezone,
    viewPreset,
    selectedGeography,
    selectedCategory,
    selectedImportance,
    selectedStatus,
    searchQuery,
    startDate,
    endDate,
  ]);

  const fetchCoverageAndAlerts = useCallback(async () => {
    try {
      const [cov, userAlerts, hist] = await Promise.allSettled([
        getCalendarCoverage(),
        getUserAlerts(),
        getAlertDeliveryHistory(),
      ]);

      if (cov.status === "fulfilled") {
        setCoverage(cov.value);
      }
      if (userAlerts.status === "fulfilled") {
        setAlerts(userAlerts.value);
      }
      if (hist.status === "fulfilled") {
        setDeliveryHistory(hist.value);
      }
    } catch (err) {
      console.warn("Failed to fetch coverage/alerts:", err);
    }
  }, []);

  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  useEffect(() => {
    fetchCoverageAndAlerts();
  }, [fetchCoverageAndAlerts]);

  const openEventDetail = useCallback(
    async (eventId: string) => {
      setSelectedEventId(eventId);
      setIsDetailModalOpen(true);
      setIsDetailLoading(true);
      try {
        const detail = await getCalendarEventDetail(eventId, selectedTimezone);
        setSelectedEventDetail(detail);
      } catch (err) {
        console.error("Failed to load event detail:", err);
      } finally {
        setIsDetailLoading(false);
      }
    },
    [selectedTimezone]
  );

  const closeEventDetail = useCallback(() => {
    setIsDetailModalOpen(false);
    setSelectedEventId(null);
    setSelectedEventDetail(null);
  }, []);

  const openAlertsModal = useCallback(() => {
    setIsAlertsModalOpen(true);
  }, []);

  const closeAlertsModal = useCallback(() => {
    setIsAlertsModalOpen(false);
  }, []);

  const addAlert = useCallback(
    async (payload: CreateEventAlertRequestDTO) => {
      try {
        const created = await createEventAlert(payload);
        setAlerts((prev) => [...prev, created]);
        return created;
      } catch (err) {
        console.error("Failed to create alert:", err);
        throw err;
      }
    },
    []
  );

  const toggleAlertEnabled = useCallback(
    async (alertId: string, enabled: boolean) => {
      try {
        const updated = await updateEventAlert(alertId, { is_enabled: enabled });
        setAlerts((prev) => prev.map((a) => (a.alert_id === alertId ? updated : a)));
      } catch (err) {
        console.error("Failed to toggle alert:", err);
      }
    },
    []
  );

  const removeAlert = useCallback(
    async (alertId: string) => {
      try {
        const success = await deleteEventAlert(alertId);
        if (success) {
          setAlerts((prev) => prev.filter((a) => a.alert_id !== alertId));
        }
        return success;
      } catch (err) {
        console.error("Failed to delete alert:", err);
        return false;
      }
    },
    []
  );

  const setDateRange = useCallback((start: string | null, end: string | null) => {
    setStartDate(start);
    setEndDate(end);
  }, []);

  const refresh = useCallback(async () => {
    await Promise.all([fetchCalendar(), fetchCoverageAndAlerts()]);
  }, [fetchCalendar, fetchCoverageAndAlerts]);

  return {
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
    startDate,
    endDate,
    setDateRange,

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
  };
}
