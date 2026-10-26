"use client";

import React, { useState } from "react";
import { NewsMonitoringRuleDTO } from "@/lib/news/types";
import { formatRelativeTime } from "@/lib/news/formatting";
import {
  Bell,
  Play,
  Pause,
  Trash2,
  Edit2,
  Plus,
  Eye,
  ShieldAlert,
  Clock,
  Sparkles,
  Building2,
  Hash,
  Layers,
} from "lucide-react";

interface ActiveRulesTableProps {
  rules: NewsMonitoringRuleDTO[];
  isLoading: boolean;
  onToggleActive: (rule: NewsMonitoringRuleDTO) => void;
  onDeleteRule: (ruleId: string) => void;
  onSelectRule: (rule: NewsMonitoringRuleDTO) => void;
  onOpenCreateModal: () => void;
  onOpenEditModal: (rule: NewsMonitoringRuleDTO) => void;
  onOpenPreviewModal: (rule: NewsMonitoringRuleDTO) => void;
}

function getPriorityBadge(priority: string) {
  switch (priority) {
    case "CRITICAL":
      return "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30";
    case "HIGH":
      return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30";
    case "MEDIUM":
      return "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/30";
    default:
      return "bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border-zinc-500/30";
  }
}

function getRuleTypeIcon(type: string) {
  switch (type) {
    case "COMPANY":
      return <Building2 className="w-3.5 h-3.5 text-cyan-500" />;
    case "TOPIC":
      return <Hash className="w-3.5 h-3.5 text-indigo-500" />;
    case "EVENT_TYPE":
      return <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />;
    default:
      return <Layers className="w-3.5 h-3.5 text-violet-500" />;
  }
}

export function ActiveRulesTable({
  rules,
  isLoading,
  onToggleActive,
  onDeleteRule,
  onSelectRule,
  onOpenCreateModal,
  onOpenEditModal,
  onOpenPreviewModal,
}: ActiveRulesTableProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, ruleId: string) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this monitoring rule?")) {
      setDeletingId(ruleId);
      try {
        await onDeleteRule(ruleId);
      } finally {
        setDeletingId(null);
      }
    }
  };

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm font-mono text-xs">
      {/* Table Header Bar */}
      <div className="p-3.5 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bell className="w-4 h-4 text-cyan-500" />
          <h2 className="font-semibold text-zinc-900 dark:text-zinc-100 uppercase tracking-wider text-xs">
            Personalized Monitoring Rules
          </h2>
          <span className="px-2 py-0.5 rounded-full bg-zinc-100 dark:bg-zinc-800 text-[11px] text-zinc-600 dark:text-zinc-400">
            {rules.length} configured
          </span>
        </div>

        <button
          onClick={onOpenCreateModal}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold shadow-sm transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Rule</span>
        </button>
      </div>

      {/* Rules Table */}
      {rules.length === 0 ? (
        <div className="p-8 text-center text-zinc-500 space-y-3">
          <p>No active monitoring rules configured.</p>
          <button
            onClick={onOpenCreateModal}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded bg-cyan-500 text-white text-xs font-semibold"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create First Rule</span>
          </button>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 text-[11px] text-zinc-500">
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Rule Name & Type</th>
                <th className="py-2.5 px-3">Target Conditions</th>
                <th className="py-2.5 px-3">Priority</th>
                <th className="py-2.5 px-3">Policy & Cooldown</th>
                <th className="py-2.5 px-3">Matches</th>
                <th className="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {rules.map((rule) => {
                const isDeleting = deletingId === rule.rule_id;
                return (
                  <tr
                    key={rule.rule_id}
                    onClick={() => onSelectRule(rule)}
                    className="hover:bg-zinc-50/70 dark:hover:bg-zinc-800/40 cursor-pointer transition-colors"
                  >
                    {/* Status Toggle */}
                    <td className="py-3 px-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onToggleActive(rule);
                        }}
                        className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-semibold transition-colors ${
                          rule.is_active
                            ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30"
                            : "bg-zinc-200 dark:bg-zinc-800 text-zinc-500 border border-zinc-300 dark:border-zinc-700"
                        }`}
                        title={rule.is_active ? "Click to Pause" : "Click to Activate"}
                      >
                        {rule.is_active ? (
                          <>
                            <Play className="w-2.5 h-2.5 fill-current" />
                            <span>ACTIVE</span>
                          </>
                        ) : (
                          <>
                            <Pause className="w-2.5 h-2.5 fill-current" />
                            <span>PAUSED</span>
                          </>
                        )}
                      </button>
                    </td>

                    {/* Rule Name & Type */}
                    <td className="py-3 px-3">
                      <div className="flex items-center space-x-2">
                        {getRuleTypeIcon(rule.rule_type)}
                        <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                          {rule.name}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-500">
                          r{rule.rule_revision}
                        </span>
                      </div>
                      {rule.description && (
                        <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-0.5 line-clamp-1">
                          {rule.description}
                        </p>
                      )}
                    </td>

                    {/* Targets */}
                    <td className="py-3 px-3">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {rule.target_tickers?.map((t) => (
                          <span
                            key={t}
                            className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 text-[10px] font-bold"
                          >
                            ${t}
                          </span>
                        ))}
                        {rule.target_topic_ids?.map((tp) => (
                          <span
                            key={tp}
                            className="px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/20 text-[10px]"
                          >
                            #{tp}
                          </span>
                        ))}
                        {rule.target_event_types?.map((ev) => (
                          <span
                            key={ev}
                            className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 text-[10px]"
                          >
                            {ev}
                          </span>
                        ))}
                        {rule.sentiment_condition && (
                          <span
                            className="px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20 text-[10px] flex items-center space-x-0.5"
                            title={`Sentiment: ${rule.sentiment_condition.sentiment_label}`}
                          >
                            <Sparkles className="w-2.5 h-2.5 mr-0.5" />
                            {rule.sentiment_condition.sentiment_label}
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Priority */}
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getPriorityBadge(
                          rule.priority
                        )}`}
                      >
                        {rule.priority}
                      </span>
                    </td>

                    {/* Policy & Cooldown */}
                    <td className="py-3 px-3 text-[11px] text-zinc-600 dark:text-zinc-400">
                      <div>{rule.trigger_policy}</div>
                      <div className="flex items-center space-x-1 text-[10px] text-zinc-500 mt-0.5">
                        <Clock className="w-2.5 h-2.5" />
                        <span>{rule.cooldown_minutes}m cooldown</span>
                        {rule.quiet_hours_enabled && (
                          <span className="text-zinc-400">
                            (QH: {rule.quiet_hours_start_utc}-{rule.quiet_hours_end_utc})
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Matches */}
                    <td className="py-3 px-3 text-zinc-700 dark:text-zinc-300">
                      <strong>{rule.total_matches_count}</strong>
                      {rule.last_triggered_at && (
                        <div className="text-[10px] text-zinc-400">
                          {formatRelativeTime(rule.last_triggered_at)}
                        </div>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-3 text-right space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenPreviewModal(rule);
                        }}
                        className="p-1 rounded text-zinc-400 hover:text-cyan-500 transition-colors"
                        title="Historical Preview"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenEditModal(rule);
                        }}
                        className="p-1 rounded text-zinc-400 hover:text-indigo-500 transition-colors"
                        title="Edit Rule"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(e, rule.rule_id)}
                        disabled={isDeleting}
                        className="p-1 rounded text-zinc-400 hover:text-rose-500 transition-colors"
                        title="Delete Rule"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
