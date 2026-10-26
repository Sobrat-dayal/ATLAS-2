"use client";

import React, { useState } from "react";
import { useNewsMonitoring, MonitoringSubTab } from "@/hooks/news/useNewsMonitoring";
import { MonitoringHealthBanner } from "./MonitoringHealthBanner";
import { ActiveRulesTable } from "./ActiveRulesTable";
import { RuleBuilderModal } from "./RuleBuilderModal";
import { AlertHistoryTable } from "./AlertHistoryTable";
import { CustomFeedsPanel } from "./CustomFeedsPanel";
import { NewsDigestPanel } from "./NewsDigestPanel";
import { NewsMonitoringRuleDTO } from "@/lib/news/types";
import {
  Bell,
  SlidersHorizontal,
  Filter,
  Calendar,
  Activity,
  ShieldCheck,
  RefreshCw,
  CheckCircle2,
  Clock,
  Layers,
} from "lucide-react";

export function NewsMonitoringWorkspace() {
  const {
    activeSubTab,
    setActiveSubTab,
    // Rules
    rules,
    selectedRule,
    setSelectedRule,
    isRulesLoading,
    handleCreateRule,
    handleUpdateRule,
    handleToggleRuleActive,
    handleDeleteRule,
    handleValidateRule,
    handlePreviewRule,
    // Feeds
    customFeeds,
    selectedFeed,
    setSelectedFeed,
    feedArticles,
    isFeedsLoading,
    handleCreateCustomFeed,
    handleUpdateCustomFeed,
    handleDeleteCustomFeed,
    handleExecuteFeed,
    // Alerts
    alertFeed,
    selectedAlert,
    setSelectedAlert,
    alertFilterStatus,
    setAlertFilterStatus,
    alertFilterPriority,
    setAlertFilterPriority,
    isAlertsLoading,
    // Digests
    digests,
    selectedDigest,
    setSelectedDigest,
    digestPreview,
    digestHistory,
    isDigestsLoading,
    handleCreateDigest,
    handleUpdateDigest,
    handleDeleteDigest,
    handlePreviewDigest,
    handleTriggerDigest,
    handleLoadDigestHistory,
    // Health
    health,
    isHealthLoading,
    // Global
    error,
    refreshAll,
  } = useNewsMonitoring();

  // Modal State
  const [isRuleBuilderOpen, setIsRuleBuilderOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<NewsMonitoringRuleDTO | null>(null);

  const handleOpenCreateRule = () => {
    setEditingRule(null);
    setIsRuleBuilderOpen(true);
  };

  const handleOpenEditRule = (rule: NewsMonitoringRuleDTO) => {
    setEditingRule(rule);
    setIsRuleBuilderOpen(true);
  };

  const handleOpenPreviewRule = (rule: NewsMonitoringRuleDTO) => {
    setEditingRule(rule);
    setIsRuleBuilderOpen(true);
  };

  return (
    <div className="space-y-4 font-mono text-xs">
      {/* Top Pipeline Health & Metrics Banner */}
      <MonitoringHealthBanner
        health={health}
        isLoading={isHealthLoading}
        onRefresh={refreshAll}
      />

      {/* Sub-tab Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 p-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm">
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setActiveSubTab("RULES")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded transition-colors ${
              activeSubTab === "RULES"
                ? "bg-cyan-600 text-white font-bold shadow-sm"
                : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            <Bell className="w-3.5 h-3.5" />
            <span>Monitoring Rules ({rules.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab("CUSTOM_FEEDS")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded transition-colors ${
              activeSubTab === "CUSTOM_FEEDS"
                ? "bg-indigo-600 text-white font-bold shadow-sm"
                : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Custom Feeds ({customFeeds.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab("ALERTS")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded transition-colors ${
              activeSubTab === "ALERTS"
                ? "bg-amber-600 text-white font-bold shadow-sm"
                : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Alert History ({alertFeed?.total_count ?? 0})</span>
          </button>

          <button
            onClick={() => setActiveSubTab("DIGESTS")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded transition-colors ${
              activeSubTab === "DIGESTS"
                ? "bg-violet-600 text-white font-bold shadow-sm"
                : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Scheduled Digests ({digests.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab("HEALTH")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded transition-colors ${
              activeSubTab === "HEALTH"
                ? "bg-emerald-600 text-white font-bold shadow-sm"
                : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Pipeline Health</span>
          </button>
        </div>

        <button
          onClick={refreshAll}
          className="flex items-center space-x-1 px-2.5 py-1 text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 rounded border border-zinc-200 dark:border-zinc-800"
          title="Refresh All Monitoring Data"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Sync</span>
        </button>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="p-3 rounded bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400">
          <p className="font-semibold">Monitoring Error: {error}</p>
        </div>
      )}

      {/* Main Subtab View */}
      {activeSubTab === "RULES" && (
        <ActiveRulesTable
          rules={rules}
          isLoading={isRulesLoading}
          onToggleActive={handleToggleRuleActive}
          onDeleteRule={handleDeleteRule}
          onSelectRule={setSelectedRule}
          onOpenCreateModal={handleOpenCreateRule}
          onOpenEditModal={handleOpenEditRule}
          onOpenPreviewModal={handleOpenPreviewRule}
        />
      )}

      {activeSubTab === "CUSTOM_FEEDS" && (
        <CustomFeedsPanel
          customFeeds={customFeeds}
          selectedFeed={selectedFeed}
          feedArticles={feedArticles}
          isLoading={isFeedsLoading}
          onSelectFeed={setSelectedFeed}
          onCreateFeed={handleCreateCustomFeed}
          onDeleteFeed={handleDeleteCustomFeed}
          onExecuteFeed={handleExecuteFeed}
        />
      )}

      {activeSubTab === "ALERTS" && (
        <AlertHistoryTable
          alertFeed={alertFeed}
          isLoading={isAlertsLoading}
          selectedAlert={selectedAlert}
          onSelectAlert={setSelectedAlert}
          filterStatus={alertFilterStatus}
          onFilterStatusChange={setAlertFilterStatus}
          filterPriority={alertFilterPriority}
          onFilterPriorityChange={setAlertFilterPriority}
          onRefresh={refreshAll}
        />
      )}

      {activeSubTab === "DIGESTS" && (
        <NewsDigestPanel
          digests={digests}
          selectedDigest={selectedDigest}
          digestPreview={digestPreview}
          digestHistory={digestHistory}
          isLoading={isDigestsLoading}
          onSelectDigest={setSelectedDigest}
          onCreateDigest={handleCreateDigest}
          onDeleteDigest={handleDeleteDigest}
          onPreviewDigest={handlePreviewDigest}
          onTriggerDigest={handleTriggerDigest}
          onLoadHistory={handleLoadDigestHistory}
        />
      )}

      {activeSubTab === "HEALTH" && (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded p-5 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 pb-3 border-b border-zinc-200 dark:border-zinc-800">
            <Activity className="w-4 h-4 text-emerald-500" />
            <h3 className="font-bold text-sm text-zinc-900 dark:text-zinc-100 uppercase">
              Real-Time News Monitoring Engine Telemetry
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3.5 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 space-y-1">
              <span className="text-zinc-500 text-[11px]">Evaluation Engine</span>
              <div className="font-bold text-sm text-zinc-900 dark:text-zinc-100">
                {health?.engine_version ?? "v103.0-institutional"}
              </div>
              <p className="text-[10px] text-zinc-400">Deterministic rule-matcher with cooldown</p>
            </div>

            <div className="p-3.5 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 space-y-1">
              <span className="text-zinc-500 text-[11px]">Average Latency</span>
              <div className="font-bold text-sm text-emerald-600 dark:text-emerald-400">
                {health?.average_eval_latency_ms.toFixed(2) ?? "0.00"} ms
              </div>
              <p className="text-[10px] text-zinc-400">Sub-5ms evaluation budget per article</p>
            </div>

            <div className="p-3.5 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 space-y-1">
              <span className="text-zinc-500 text-[11px]">Suppressed / Deduplicated (24h)</span>
              <div className="font-bold text-sm text-amber-600 dark:text-amber-400">
                {health?.deduplicated_last_24h ?? 0} suppressed
              </div>
              <p className="text-[10px] text-zinc-400">Syndication-aware deduplication</p>
            </div>

            <div className="p-3.5 rounded bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 space-y-1">
              <span className="text-zinc-500 text-[11px]">Active Subscriptions</span>
              <div className="font-bold text-sm text-violet-600 dark:text-violet-400">
                {(health?.active_rules_count ?? 0) + (health?.active_digests_count ?? 0)} active
              </div>
              <p className="text-[10px] text-zinc-400">Rules + Digests combined</p>
            </div>
          </div>

          <div className="p-4 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/50 space-y-2">
            <h4 className="font-semibold text-zinc-900 dark:text-zinc-100">
              Operational Invariants & Guarantees (Stage 103)
            </h4>
            <ul className="space-y-1 text-zinc-600 dark:text-zinc-400 text-[11px]">
              <li>• <strong>Non-Retroactive Preview:</strong> Historical rule validation previews bounded sample articles without firing retroactive notification alerts.</li>
              <li>• <strong>Syndication-Aware Deduplication:</strong> Identical stories across syndication wires are collapsed under SHA-256 deduplication keys with <code>SUPPRESSED_SYNDICATION</code>.</li>
              <li>• <strong>Rule Cooldown Interval:</strong> Successive matches within the configured cooldown window are recorded with <code>SUPPRESSED_COOLDOWN</code> to prevent notification spam.</li>
              <li>• <strong>Quiet-Hours Suppression:</strong> Rules with quiet-hours enabled suppress instant dispatch during off-hours, staging matches for morning digest delivery.</li>
              <li>• <strong>Idempotent Digest Dispatch:</strong> Scheduled and triggered digests generate idempotent tokens to prevent duplicate notifications.</li>
            </ul>
          </div>
        </div>
      )}

      {/* Rule Builder / Editor Modal */}
      <RuleBuilderModal
        isOpen={isRuleBuilderOpen}
        onClose={() => {
          setIsRuleBuilderOpen(false);
          setEditingRule(null);
        }}
        onSaveRule={async (dto) => {
          if (editingRule) {
            return handleUpdateRule(editingRule.rule_id, dto);
          } else {
            return handleCreateRule(dto);
          }
        }}
        onValidateRule={(dto) => handleValidateRule({ rule: dto })}
        onPreviewRule={(dto) => handlePreviewRule({ rule: dto })}
        initialRule={editingRule}
      />
    </div>
  );
}
