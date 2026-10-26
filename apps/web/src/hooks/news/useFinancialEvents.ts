"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getEntityEvents,
  getNewsEvent,
  getNewsEventEvidence,
  getNewsEvents,
  getNewsEventTypes,
  NewsEventQueryParams,
} from "@/lib/news/api";
import {
  FinancialEventTypeDefinitionDTO,
  NewsEventEvidenceDTO,
  NewsFinancialEventDTO,
} from "@/lib/news/types";

export function useFinancialEvents() {
  const [events, setEvents] = useState<NewsFinancialEventDTO[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<NewsFinancialEventDTO | null>(null);
  const [eventEvidence, setEventEvidence] = useState<NewsEventEvidenceDTO[]>([]);
  const [eventTypes, setEventTypes] = useState<FinancialEventTypeDefinitionDTO[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);

  // Filters
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("");
  const [lifecycleFilter, setLifecycleFilter] = useState<string>("");
  const [assertionFilter, setAssertionFilter] = useState<string>("");
  const [entityFilter, setEntityFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isDetailLoading, setIsDetailLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load event types catalog
  useEffect(() => {
    let mounted = true;
    async function loadCatalog() {
      try {
        const types = await getNewsEventTypes();
        if (mounted) setEventTypes(types);
      } catch (err) {
        console.error("Failed to load event types:", err);
      }
    }
    loadCatalog();
    return () => {
      mounted = false;
    };
  }, []);

  const fetchEvents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: NewsEventQueryParams = {
        limit: 30,
      };
      if (eventTypeFilter) params.event_type = eventTypeFilter;
      if (lifecycleFilter) params.lifecycle_status = lifecycleFilter;
      if (assertionFilter) params.assertion_status = assertionFilter;
      if (entityFilter) params.primary_entity_id = entityFilter;
      if (searchQuery) params.q = searchQuery;

      const res = await getNewsEvents(params);
      setEvents(res.events);
      setTotalCount(res.total_count);
      setNextCursor(res.next_cursor || null);
      setHasMore(res.has_more);

      // Auto-select first event if none selected or previous selection no longer in list
      if (res.events.length > 0) {
        setSelectedEvent((prev) => {
          if (!prev) return res.events[0];
          const exists = res.events.find((e) => e.event_id === prev.event_id);
          return exists || res.events[0];
        });
      } else {
        setSelectedEvent(null);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load Financial Events";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [eventTypeFilter, lifecycleFilter, assertionFilter, entityFilter, searchQuery]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  // Load structured evidence records whenever selectedEvent changes
  useEffect(() => {
    if (!selectedEvent) {
      setEventEvidence([]);
      return;
    }

    let mounted = true;
    setIsDetailLoading(true);

    async function loadEvidence() {
      try {
        const evd = await getNewsEventEvidence(selectedEvent!.event_id);
        if (mounted) setEventEvidence(evd);
      } catch (err) {
        console.error("Failed to load event evidence:", err);
      } finally {
        if (mounted) setIsDetailLoading(false);
      }
    }

    loadEvidence();
    return () => {
      mounted = false;
    };
  }, [selectedEvent?.event_id]);

  const selectEvent = useCallback(
    async (eventId: string) => {
      const existing = events.find((e) => e.event_id === eventId);
      if (existing) {
        setSelectedEvent(existing);
        return;
      }
      try {
        setIsDetailLoading(true);
        const fetched = await getNewsEvent(eventId);
        setSelectedEvent(fetched);
      } catch (err) {
        console.error("Failed to load event by ID:", err);
      } finally {
        setIsDetailLoading(false);
      }
    },
    [events]
  );

  return {
    events,
    selectedEvent,
    eventEvidence,
    eventTypes,
    totalCount,
    hasMore,
    isLoading,
    isDetailLoading,
    error,
    eventTypeFilter,
    setEventTypeFilter,
    lifecycleFilter,
    setLifecycleFilter,
    assertionFilter,
    setAssertionFilter,
    entityFilter,
    setEntityFilter,
    searchQuery,
    setSearchQuery,
    selectEvent,
    refresh: fetchEvents,
  };
}
