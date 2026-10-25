"use client";

import React, { useMemo, useState } from "react";
import {
  Activity,
  Bell,
  ChevronDown,
  ChevronUp,
  Plus,
} from "lucide-react";
import {
  AlertCapabilitiesResponse,
  AlertHealthResponse,
  CreateAlertPayload,
  UpdateAlertPayload,
  WatchlistAlertRule,
  WatchlistAlertTrigger,
} from "@/lib/watchlists/alerts/types";
import { AlertRuleRow } from "./AlertRuleRow";
import { CreateAlertDialog } from "./CreateAlertDialog";
import { EditAlertDialog } from "./EditAlertDialog";
import { DeleteAlertDialog } from "./DeleteAlertDialog";
import { AlertHistoryDialog } from "./AlertHistoryDialog";
import { WatchlistItem } from "@/lib/watchlists/types";

interface WatchlistAlertsPanelProps {
  watchlistId: string | null;
  items: WatchlistItem[];
  alerts: WatchlistAlertRule[];
  activeAlerts: WatchlistAlertRule[];
  pausedAlerts: WatchlistAlertRule[];
  capabilities: AlertCapabilitiesResponse | null;
  health: AlertHealthResponse | null;
  loading: boolean;
  error: string | null;
  createAlert: (payload: CreateAlertPayload) => Promise<unknown>;
  updateAlert: (alertId: string, payload: UpdateAlertPayload) => Promise<unknown>;
  deleteAlert: (alertId: string) => Promise<unknown>;
  pauseAlert: (alertId: string) => Promise<unknown>;
  resumeAlert: (alertId: string) => Promise<unknown>;
  fetchHistory: (alertId: string) => Promise<WatchlistAlertTrigger[]>;
  preselectedItem?: WatchlistItem | null;
  onClearPreselectedItem?: () => void;
}

export function WatchlistAlertsPanel({
  watchlistId,
  items,
  alerts,
  activeAlerts,
  pausedAlerts,
  capabilities,
  health,
  loading,
  error,
  createAlert,
  updateAlert,
  deleteAlert,
  pauseAlert,
  resumeAlert,
  fetchHistory,
  preselectedItem,
  onClearPreselectedItem,
}: WatchlistAlertsPanelProps) {
  const [tab, setTab] = useState<"ACTIVE" | "PAUSED" | "ALL">("ACTIVE");
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Dialog states
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [targetItemForCreate, setTargetItemForCreate] = useState<WatchlistItem | null>(null);
  const [editingAlert, setEditingAlert] = useState<WatchlistAlertRule | null>(null);
  const [deletingAlert, setDeletingAlert] = useState<WatchlistAlertRule | null>(null);
  const [historyAlert, setHistoryAlert] = useState<WatchlistAlertRule | null>(null);

  // When a row action triggers "Create Alert" for a specific item
  React.useEffect(() => {
    if (preselectedItem) {
      setTargetItemForCreate(preselectedItem);
      setIsCreateOpen(true);
      if (onClearPreselectedItem) onClearPreselectedItem();
    }
  }, [preselectedItem, onClearPreselectedItem]);

  const displayedAlerts = useMemo(() => {
    if (tab === "ACTIVE") return activeAlerts;
    if (tab === "PAUSED") return pausedAlerts;
    return alerts;
  }, [tab, activeAlerts, pausedAlerts, alerts]);

  const handleOpenCreateGeneric = () => {
    // Default to first item if available
    setTargetItemForCreate(items.length > 0 ? items[0] : null);
    setIsCreateOpen(true);
  };

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-lg overflow-hidden font-mono text-xs">
      {/* Panel Top Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 bg-zinc-900/70 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsCollapsed((prev) => !prev)}
            className="flex items-center gap-1.5 text-zinc-200 hover:text-white font-semibold transition-colors"
          >
            <Bell className="w-4 h-4 text-sky-400" />
            <span>Watchlist Alerts</span>
            <span className="px-1.5 py-0.2 rounded text-[10px] bg-zinc-800 text-zinc-300">
              {activeAlerts.length} Active
            </span>
            {isCollapsed ? (
              <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
            ) : (
              <ChevronUp className="w-3.5 h-3.5 text-zinc-500" />
            )}
          </button>

          {/* Evaluator worker operational status badge */}
          {health && (
            <div
              className="flex items-center gap-1 text-[10px] text-zinc-400 pl-2 border-l border-zinc-800"
              title={`Evaluator worker running: ${health.evaluator?.worker_running ? "Yes" : "No"} (${health.evaluator?.active_indexed_series || 0} active series)`}
            >
              <Activity
                className={`w-3 h-3 ${
                  health.evaluator?.worker_running ? "text-emerald-400" : "text-amber-400"
                }`}
              />
              <span>
                {health.evaluator?.worker_running ? "Evaluator Online" : "Evaluator Standby"}
              </span>
            </div>
          )}
        </div>

        {/* Tab Filters & Create Button */}
        <div className="flex items-center gap-2">
          {!isCollapsed && (
            <div className="flex items-center bg-zinc-950 border border-zinc-800 rounded p-0.5 text-[11px]">
              <button
                type="button"
                onClick={() => setTab("ACTIVE")}
                className={`px-2 py-0.5 rounded transition-colors ${
                  tab === "ACTIVE"
                    ? "bg-zinc-800 text-zinc-100 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Active ({activeAlerts.length})
              </button>
              <button
                type="button"
                onClick={() => setTab("PAUSED")}
                className={`px-2 py-0.5 rounded transition-colors ${
                  tab === "PAUSED"
                    ? "bg-zinc-800 text-zinc-100 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Paused ({pausedAlerts.length})
              </button>
              <button
                type="button"
                onClick={() => setTab("ALL")}
                className={`px-2 py-0.5 rounded transition-colors ${
                  tab === "ALL"
                    ? "bg-zinc-800 text-zinc-100 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                All ({alerts.length})
              </button>
            </div>
          )}

          <button
            type="button"
            disabled={!watchlistId || items.length === 0}
            onClick={handleOpenCreateGeneric}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-sky-600 text-white font-medium hover:bg-sky-500 disabled:opacity-40 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create Alert</span>
          </button>
        </div>
      </div>

      {/* Panel Body */}
      {!isCollapsed && (
        <div>
          {error && (
            <div className="p-2 bg-rose-950/40 border-b border-rose-800 text-rose-300 text-[11px]">
              {error}
            </div>
          )}

          {displayedAlerts.length === 0 ? (
            <div className="py-8 px-4 text-center text-zinc-500">
              <Bell className="w-6 h-6 mx-auto mb-2 opacity-30 text-zinc-400" />
              <p className="text-zinc-400">
                {tab === "ACTIVE"
                  ? "No active alerts in this watchlist."
                  : tab === "PAUSED"
                    ? "No paused alerts."
                    : "No alert rules defined yet."}
              </p>
              {items.length > 0 && (
                <button
                  type="button"
                  onClick={handleOpenCreateGeneric}
                  className="mt-2 text-sky-400 hover:text-sky-300 underline text-[11px]"
                >
                  Configure price or percentage-change alerts for instruments in this watchlist
                </button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-zinc-800 text-[10px] uppercase text-zinc-500 bg-zinc-950/60">
                    <th className="py-2 px-3">Instrument</th>
                    <th className="py-2 px-3">Condition & Measure</th>
                    <th className="py-2 px-3">Threshold</th>
                    <th className="py-2 px-3">Recurrence / Cooldown</th>
                    <th className="py-2 px-3">Status</th>
                    <th className="py-2 px-3">Last Trigger</th>
                    <th className="py-2 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedAlerts.map((alert) => (
                    <AlertRuleRow
                      key={alert.id}
                      alert={alert}
                      onEdit={setEditingAlert}
                      onDelete={setDeletingAlert}
                      onPause={pauseAlert}
                      onResume={resumeAlert}
                      onViewHistory={setHistoryAlert}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Modal Dialogs */}
      {isCreateOpen && (
        <CreateAlertDialog
          isOpen={isCreateOpen}
          onClose={() => {
            setIsCreateOpen(false);
            setTargetItemForCreate(null);
          }}
          item={targetItemForCreate}
          capabilities={capabilities}
          onSubmit={createAlert}
        />
      )}

      {editingAlert && (
        <EditAlertDialog
          isOpen={Boolean(editingAlert)}
          onClose={() => setEditingAlert(null)}
          alert={editingAlert}
          onSubmit={updateAlert}
        />
      )}

      {deletingAlert && (
        <DeleteAlertDialog
          isOpen={Boolean(deletingAlert)}
          onClose={() => setDeletingAlert(null)}
          alert={deletingAlert}
          onConfirm={deleteAlert}
        />
      )}

      {historyAlert && (
        <AlertHistoryDialog
          isOpen={Boolean(historyAlert)}
          onClose={() => setHistoryAlert(null)}
          alert={historyAlert}
          fetchHistory={fetchHistory}
        />
      )}
    </div>
  );
}
