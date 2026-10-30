"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchTerminalLogs } from "@/lib/terminal/api";
import { LogEntry, LogSeverity } from "@/lib/terminal/types";

export function useTerminalLogs(initialAutoRefresh: boolean = false) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [severity, setSeverity] = useState<LogSeverity | undefined>(undefined);
  const [service, setService] = useState<string>("");
  const [search, setSearch] = useState<string>("");
  const [autoRefresh, setAutoRefresh] = useState<boolean>(initialAutoRefresh);

  const loadLogs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTerminalLogs({
        severity: severity || undefined,
        service: service.trim() || undefined,
        search: search.trim() || undefined,
        limit: 100,
      });
      setLogs(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load logs";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [severity, service, search]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  // Polling when autoRefresh is enabled
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadLogs();
    }, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, loadLogs]);

  return {
    logs,
    loading,
    error,
    severity,
    setSeverity,
    service,
    setService,
    search,
    setSearch,
    autoRefresh,
    setAutoRefresh,
    refresh: loadLogs,
  };
}

