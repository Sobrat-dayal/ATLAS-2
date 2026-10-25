"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  createWatchlistAlert,
  deleteWatchlistAlert,
  getWatchlistAlertCapabilities,
  getWatchlistAlertHealth,
  getWatchlistAlertHistory,
  getWatchlistAlerts,
  pauseWatchlistAlert,
  resumeWatchlistAlert,
  updateWatchlistAlert,
} from "@/lib/watchlists/alerts/api";
import {
  AlertCapabilitiesResponse,
  AlertHealthResponse,
  CreateAlertPayload,
  UpdateAlertPayload,
  WatchlistAlertRule,
  WatchlistAlertTrigger,
} from "@/lib/watchlists/alerts/types";

interface UseWatchlistAlertsOptions {
  watchlistId: string | null;
  pollIntervalMs?: number;
}

export function useWatchlistAlerts({
  watchlistId,
  pollIntervalMs = 5000,
}: UseWatchlistAlertsOptions) {
  const [alerts, setAlerts] = useState<WatchlistAlertRule[]>([]);
  const [capabilities, setCapabilities] = useState<AlertCapabilitiesResponse | null>(null);
  const [health, setHealth] = useState<AlertHealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load capabilities once
  useEffect(() => {
    let mounted = true;
    getWatchlistAlertCapabilities()
      .then((caps) => {
        if (mounted) setCapabilities(caps);
      })
      .catch((err) => {
        console.warn("Failed to load alert capabilities:", err);
      });

    getWatchlistAlertHealth()
      .then((h) => {
        if (mounted) setHealth(h);
      })
      .catch((err) => {
        console.warn("Failed to load alert evaluator health:", err);
      });

    return () => {
      mounted = false;
    };
  }, []);

  // Fetch alerts for active watchlist
  const fetchAlerts = useCallback(async () => {
    if (!watchlistId) {
      setAlerts([]);
      return;
    }
    try {
      const resp = await getWatchlistAlerts(watchlistId, 1, 100);
      setAlerts(resp.items);
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load alerts";
      setError(msg);
    }
  }, [watchlistId]);

  useEffect(() => {
    if (!watchlistId) return;
    setLoading(true);
    fetchAlerts().finally(() => setLoading(false));

    const interval = setInterval(fetchAlerts, pollIntervalMs);
    return () => clearInterval(interval);
  }, [watchlistId, fetchAlerts, pollIntervalMs]);

  // Derived metrics
  const activeAlerts = useMemo(
    () => alerts.filter((a) => a.enabled && a.state === "ENABLED"),
    [alerts],
  );

  const pausedAlerts = useMemo(
    () => alerts.filter((a) => a.state === "PAUSED"),
    [alerts],
  );

  // Map of item_id -> active alerts count for row indicators
  const itemAlertCounts = useMemo(() => {
    const map: Record<string, number> = {};
    for (const alert of activeAlerts) {
      map[alert.watchlist_item_id] = (map[alert.watchlist_item_id] || 0) + 1;
    }
    return map;
  }, [activeAlerts]);

  // Mutations
  const createAlert = useCallback(
    async (payload: CreateAlertPayload) => {
      if (!watchlistId) throw new Error("No active watchlist selected");
      const created = await createWatchlistAlert(watchlistId, payload);
      await fetchAlerts();
      return created;
    },
    [watchlistId, fetchAlerts],
  );

  const updateAlert = useCallback(
    async (alertId: string, payload: UpdateAlertPayload) => {
      if (!watchlistId) throw new Error("No active watchlist selected");
      const updated = await updateWatchlistAlert(watchlistId, alertId, payload);
      await fetchAlerts();
      return updated;
    },
    [watchlistId, fetchAlerts],
  );

  const deleteAlert = useCallback(
    async (alertId: string) => {
      if (!watchlistId) throw new Error("No active watchlist selected");
      await deleteWatchlistAlert(watchlistId, alertId);
      await fetchAlerts();
    },
    [watchlistId, fetchAlerts],
  );

  const pauseAlert = useCallback(
    async (alertId: string) => {
      if (!watchlistId) throw new Error("No active watchlist selected");
      const updated = await pauseWatchlistAlert(watchlistId, alertId);
      await fetchAlerts();
      return updated;
    },
    [watchlistId, fetchAlerts],
  );

  const resumeAlert = useCallback(
    async (alertId: string) => {
      if (!watchlistId) throw new Error("No active watchlist selected");
      const updated = await resumeWatchlistAlert(watchlistId, alertId);
      await fetchAlerts();
      return updated;
    },
    [watchlistId, fetchAlerts],
  );

  const fetchHistory = useCallback(
    async (alertId: string, limit = 50, offset = 0): Promise<WatchlistAlertTrigger[]> => {
      if (!watchlistId) return [];
      return getWatchlistAlertHistory(watchlistId, alertId, limit, offset);
    },
    [watchlistId],
  );

  return {
    alerts,
    activeAlerts,
    pausedAlerts,
    itemAlertCounts,
    capabilities,
    health,
    loading,
    error,
    refresh: fetchAlerts,
    createAlert,
    updateAlert,
    deleteAlert,
    pauseAlert,
    resumeAlert,
    fetchHistory,
  };
}
