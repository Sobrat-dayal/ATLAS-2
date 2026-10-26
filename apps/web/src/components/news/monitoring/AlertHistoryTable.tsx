"use client";

import React from "react";
import { NewsAlertFeedResponseDTO, NewsAlertMatchDTO } from "@/lib/news/types";
import { formatRelativeTime } from "@/lib/news/formatting";
import {
  Bell,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Filter,
  ExternalLink,
  ShieldAlert,
  Hash,
} from "lucide-react";

interface AlertHistoryTableProps {
  alertFeed: NewsAlertFeedResponseDTO | null;
  isLoading: boolean;
  selectedAlert: NewsAlertMatchDTO | null;
  onSelectAlert: (alert: NewsAlertMatchDTO) => void;
  filterStatus: string;
  onFilterStatusChange: (status: string) => void;
  filterPriority: string;
  onFilterPriorityChange: (priority: string) => void;
  onRefresh: () => void;
}

function getStatusBadge(status: string) {
  switch (status) {
    case "DISPATCHED":
      return "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30";
    case "MATCHED":
      return "bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border-cyan-500/30";
    case "SUPPRESSED_COOLDOWN":
      return "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30";
    case "SUPPRESSED_SYNDICATION":
      return "bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 border-indigo-500/30";
    case "SUPPRESSED_QUIET_HOURS":
      return "bg-violet-500/15 text-violet-600 dark:text-violet-400 border-violet-500/30";
    default:
      return "bg-zinc-500/15 text-zinc-600 dark:text-zinc-400 border-zinc-500/30";
  }
}

function getPriorityBadge(priority: string) {
  switch (priority) {
    case "CRITICAL":
      return "bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30 font-bold";
    case "HIGH":
      return "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30 font-semibold";
    case "MEDIUM":
      return "bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border-cyan-500/30";
    default:
      return "bg-zinc-500/15 text-zinc-600 dark:text-zinc-400 border-zinc-500/30";
  }
}

export function AlertHistoryTable({
  alertFeed,
  isLoading,
  selectedAlert,
  onSelectAlert,
  filterStatus,
  onFilterStatusChange,
  filterPriority,
  onFilterPriorityChange,
  onRefresh,
}: AlertHistoryTableProps) {
  const alerts = alertFeed?.alerts || [];

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm font-mono text-xs">
      {/* Top Filter and Title Header */}
      <div className="p-3.5 border-b border-zinc-200 dark:border-zinc-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Bell className="w-4 h-4 text-cyan-500" />
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider text-xs">
            Alert Dispatch & Suppression History
          </h2>
          <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-[11px] text-zinc-600 dark:text-zinc-400">
            {alertFeed?.total_count ?? 0} total
          </span>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center space-x-2">
          {/* Priority filter */}
          <select
            value={filterPriority}
            onChange={(e) => onFilterPriorityChange(e.target.value)}
            className="px-2.5 py-1 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 text-zinc-700 dark:text-zinc-300 text-xs"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="HIGH">High Only</option>
            <option value="MEDIUM">Medium Only</option>
            <option value="LOW">Low Only</option>
          </select>

          {/* Status filter */}
          <select
            value={filterStatus}
            onChange={(e) => onFilterStatusChange(e.target.value)}
            className="px-2.5 py-1 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 text-zinc-700 dark:text-zinc-300 text-xs"
          >
            <option value="">All Statuses</option>
            <option value="DISPATCHED">DISPATCHED</option>
            <option value="MATCHED">MATCHED</option>
            <option value="SUPPRESSED_COOLDOWN">SUPPRESSED_COOLDOWN</option>
            <option value="SUPPRESSED_SYNDICATION">SUPPRESSED_SYNDICATION</option>
            <option value="SUPPRESSED_QUIET_HOURS">SUPPRESSED_QUIET_HOURS</option>
          </select>
        </div>
      </div>

      {/* Table */}
      {alerts.length === 0 ? (
        <div className="p-8 text-center text-zinc-500">
          <p>No alert records found matching the current criteria.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 text-[11px] text-zinc-500">
                <th className="py-2.5 px-3">Matched</th>
                <th className="py-2.5 px-3">Priority</th>
                <th className="py-2.5 px-3">Triggered Rule</th>
                <th className="py-2.5 px-3">Source Headline / Event</th>
                <th className="py-2.5 px-3">Matched Conditions</th>
                <th className="py-2.5 px-3">Delivery Status</th>
                <th className="py-2.5 px-3">Dedup Key</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {alerts.map((alert) => (
                <tr
                  key={alert.alert_id}
                  onClick={() => onSelectAlert(alert)}
                  className="hover:bg-zinc-50/70 dark:hover:bg-zinc-800/40 cursor-pointer transition-colors"
                >
                  {/* Timestamp */}
                  <td className="py-2.5 px-3 whitespace-nowrap text-zinc-500">
                    {formatRelativeTime(alert.matched_at)}
                  </td>

                  {/* Priority */}
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] border ${getPriorityBadge(
                        alert.priority
                      )}`}
                    >
                      {alert.priority}
                    </span>
                  </td>

                  {/* Rule Name */}
                  <td className="py-2.5 px-3 font-semibold text-zinc-900 dark:text-zinc-100 whitespace-nowrap">
                    {alert.rule_name}
                  </td>

                  {/* Headline */}
                  <td className="py-2.5 px-3 max-w-md">
                    <div className="font-medium text-zinc-900 dark:text-zinc-100 line-clamp-1">
                      {alert.headline_or_title}
                    </div>
                    {alert.publisher_name && (
                      <div className="text-[10px] text-zinc-500">
                        {alert.publisher_name} • {alert.source_object_type}
                      </div>
                    )}
                  </td>

                  {/* Matched Conditions */}
                  <td className="py-2.5 px-3">
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {alert.matched_conditions.map((cond, idx) => (
                        <span
                          key={idx}
                          className="px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-[10px] text-zinc-600 dark:text-zinc-300"
                        >
                          {cond}
                        </span>
                      ))}
                    </div>
                  </td>

                  {/* Delivery Status */}
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getStatusBadge(
                        alert.match_status
                      )}`}
                    >
                      {alert.match_status}
                    </span>
                  </td>

                  {/* Dedup Key */}
                  <td className="py-2.5 px-3 whitespace-nowrap text-zinc-400 text-[10px] font-mono">
                    <span title={alert.deduplication_key}>
                      {alert.deduplication_key.slice(0, 14)}...
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
