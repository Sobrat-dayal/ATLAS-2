"use client";

import React from "react";
import { useTerminalLogs } from "@/hooks/terminal/useTerminalLogs";
import { TerminalSession, TerminalUserPreferences, LogSeverity } from "@/lib/terminal/types";
import { RefreshCw, Search, Filter } from "lucide-react";

interface LogsConsoleProps {
  session: TerminalSession;
  preferences: TerminalUserPreferences;
}

export function LogsConsole({ preferences }: LogsConsoleProps) {
  const {
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
    refresh,
  } = useTerminalLogs(false);

  const severities: (LogSeverity | undefined)[] = [
    undefined,
    "INFO",
    "WARNING",
    "ERROR",
    "DEBUG",
  ];

  const getBadgeStyle = (level: LogSeverity) => {
    switch (level) {
      case "ERROR":
      case "CRITICAL":
        return "bg-rose-500/15 text-rose-400 border-rose-500/30";
      case "WARNING":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "DEBUG":
        return "bg-purple-500/15 text-purple-400 border-purple-500/30";
      case "INFO":
      default:
        return "bg-sky-500/15 text-sky-400 border-sky-500/30";
    }
  };

  return (
    <div
      className="flex flex-col flex-1 h-full bg-atlas-surface-0 overflow-hidden font-mono"
      style={{
        fontSize: `${preferences.font_size}px`,
        fontFamily: preferences.font_family,
        lineHeight: preferences.line_height,
      }}
    >
      {/* Filtering & Controls Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-3 py-1.5 bg-atlas-surface-1 border-b border-atlas-border-subtle text-xs select-none">
        {/* Severity buttons */}
        <div className="flex items-center gap-1">
          <Filter className="h-3 w-3 text-atlas-text-muted mr-1" />
          {severities.map((sev) => {
            const isSelected = severity === sev;
            return (
              <button
                key={sev || "ALL"}
                type="button"
                onClick={() => setSeverity(sev)}
                className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase transition-colors ${
                  isSelected
                    ? "bg-atlas-accent text-white"
                    : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover"
                }`}
              >
                {sev || "ALL"}
              </button>
            );
          })}
        </div>

        {/* Search & Service Filter */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 bg-atlas-surface-0 border border-atlas-border-subtle rounded px-2 py-0.5 text-[11px]">
            <Search className="h-3 w-3 text-atlas-text-muted" />
            <input
              type="text"
              placeholder="Search logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-transparent text-atlas-text-primary outline-none w-28 sm:w-36 font-mono"
            />
          </div>

          <div className="hidden sm:flex items-center gap-1.5 bg-atlas-surface-0 border border-atlas-border-subtle rounded px-2 py-0.5 text-[11px]">
            <span className="text-atlas-text-muted text-[10px]">SVC:</span>
            <input
              type="text"
              placeholder="all services"
              value={service}
              onChange={(e) => setService(e.target.value)}
              className="bg-transparent text-atlas-text-primary outline-none w-24 font-mono"
            />
          </div>

          {/* Auto Refresh toggle */}
          <button
            type="button"
            onClick={() => setAutoRefresh(!autoRefresh)}
            title={autoRefresh ? "Auto-refresh active (3s)" : "Auto-refresh paused"}
            className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border transition-colors ${
              autoRefresh
                ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                : "text-atlas-text-muted border-atlas-border-subtle hover:text-atlas-text-primary"
            }`}
          >
            {autoRefresh ? "LIVE 3s" : "PAUSED"}
          </button>

          {/* Refresh button */}
          <button
            type="button"
            onClick={refresh}
            title="Refresh logs"
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Logs Table / Feed */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
        {error && (
          <div className="p-2 text-xs text-rose-400 bg-rose-950/20 rounded border border-rose-800/30">
            {error}
          </div>
        )}

        {logs.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-32 text-center text-atlas-text-muted text-xs">
            <span>No operational logs matching current filters.</span>
          </div>
        )}

        {logs.map((log) => (
          <div
            key={log.log_id}
            className="flex items-start gap-2.5 px-2 py-1 rounded hover:bg-atlas-surface-1 transition-colors leading-relaxed border-b border-atlas-border-subtle/30"
          >
            {preferences.timestamp_display && (
              <span className="text-[10px] text-atlas-text-muted shrink-0 select-none pt-0.5">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
            )}
            <span
              className={`px-1.5 py-0.2 rounded text-[9px] font-bold border uppercase shrink-0 select-none ${getBadgeStyle(
                log.level
              )}`}
            >
              {log.level}
            </span>
            <span className="text-atlas-accent text-[11px] font-semibold shrink-0 select-none">
              [{log.service}]
            </span>
            <span className="flex-1 text-atlas-text-primary break-all select-text">
              {log.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

