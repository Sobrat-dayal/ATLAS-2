"use client";

import React from "react";
import { MonitoringHealthStatusDTO } from "@/lib/news/types";
import { formatFullUtcTime } from "@/lib/news/formatting";
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Bell,
  Filter,
  Layers,
  Calendar,
  Clock,
} from "lucide-react";

interface MonitoringHealthBannerProps {
  health: MonitoringHealthStatusDTO | null;
  isLoading: boolean;
  onRefresh: () => void;
}

export function MonitoringHealthBanner({
  health,
  isLoading,
  onRefresh,
}: MonitoringHealthBannerProps) {
  if (!health) {
    return (
      <div className="p-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded font-mono text-xs text-zinc-500 flex items-center justify-between">
        <span>Initializing monitoring pipeline telemetry...</span>
        <button
          onClick={onRefresh}
          className="p-1 hover:text-zinc-900 dark:hover:text-zinc-100"
          title="Refresh"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
        </button>
      </div>
    );
  }

  return (
    <div className="p-3.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Left: Health Indicator & Version */}
        <div className="flex items-center space-x-3">
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${
              health.is_healthy
                ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30"
                : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30"
            }`}
          >
            {health.is_healthy ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
            ) : (
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
            )}
            <span>{health.is_healthy ? "PIPELINE OPERATIONAL" : "PIPELINE DEGRADED"}</span>
          </div>

          <span className="text-zinc-400 dark:text-zinc-600">|</span>

          <span className="text-zinc-600 dark:text-zinc-400">
            Engine: <strong className="text-zinc-900 dark:text-zinc-100">{health.engine_version}</strong>
          </span>

          {health.watermark_timestamp && (
            <span className="hidden sm:inline text-zinc-500 dark:text-zinc-400">
              Watermark: {formatFullUtcTime(health.watermark_timestamp)}
            </span>
          )}
        </div>

        {/* Right: Metrics & Refresh */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1 text-zinc-600 dark:text-zinc-400" title="Active Rules">
            <Bell className="w-3.5 h-3.5 text-cyan-500" />
            <span>Rules:</span>
            <strong className="text-zinc-900 dark:text-zinc-100">{health.active_rules_count}</strong>
          </div>

          <div className="flex items-center space-x-1 text-zinc-600 dark:text-zinc-400" title="Active Custom Feeds">
            <Filter className="w-3.5 h-3.5 text-indigo-500" />
            <span>Feeds:</span>
            <strong className="text-zinc-900 dark:text-zinc-100">{health.active_custom_feeds_count}</strong>
          </div>

          <div className="flex items-center space-x-1 text-zinc-600 dark:text-zinc-400" title="Active Digests">
            <Calendar className="w-3.5 h-3.5 text-violet-500" />
            <span>Digests:</span>
            <strong className="text-zinc-900 dark:text-zinc-100">{health.active_digests_count}</strong>
          </div>

          <div className="flex items-center space-x-1 text-zinc-600 dark:text-zinc-400" title="24h Alerts / Deduplicated">
            <Layers className="w-3.5 h-3.5 text-amber-500" />
            <span>Alerts (24h):</span>
            <strong className="text-zinc-900 dark:text-zinc-100">{health.alerts_last_24h}</strong>
            <span className="text-[10px] text-zinc-400">({health.deduplicated_last_24h} deduped)</span>
          </div>

          <div className="flex items-center space-x-1 text-zinc-600 dark:text-zinc-400" title="Average Evaluation Latency">
            <Clock className="w-3.5 h-3.5 text-emerald-500" />
            <span>Latency:</span>
            <strong className="text-zinc-900 dark:text-zinc-100">{health.average_eval_latency_ms.toFixed(1)}ms</strong>
          </div>

          <button
            onClick={onRefresh}
            className="p-1 rounded text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors"
            title="Refresh telemetry"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>
    </div>
  );
}
