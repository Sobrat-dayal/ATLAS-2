"use client";

import React, { useState } from "react";
import {
  AlertDeliveryIntentDTO,
  CreateEventAlertRequestDTO,
  EconomicCalendarEventDTO,
  EventAlertType,
  UserEventAlertDTO,
} from "@/lib/economics/calendar";
import {
  X,
  Bell,
  CheckCircle2,
  Trash2,
  Clock,
  ShieldCheck,
  Send,
  AlertTriangle,
  History,
} from "lucide-react";

interface EconomicCalendarAlertsModalProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: UserEventAlertDTO[];
  deliveryHistory: AlertDeliveryIntentDTO[];
  onToggleEnabled: (alertId: string, enabled: boolean) => Promise<void>;
  onRemoveAlert: (alertId: string) => Promise<boolean>;
  onCreateAlert: (payload: CreateEventAlertRequestDTO) => Promise<UserEventAlertDTO | null>;
  events: EconomicCalendarEventDTO[];
  preselectedEvent?: EconomicCalendarEventDTO | null;
}

export function EconomicCalendarAlertsModal({
  isOpen,
  onClose,
  alerts,
  deliveryHistory,
  onToggleEnabled,
  onRemoveAlert,
  onCreateAlert,
  events,
  preselectedEvent,
}: EconomicCalendarAlertsModalProps) {
  const [activeSubTab, setActiveSubTab] = useState<"rules" | "history">("rules");
  const [selectedEventId, setSelectedEventId] = useState<string>(
    preselectedEvent?.event_id || (events[0]?.event_id || "")
  );
  const [alertType, setAlertType] = useState<EventAlertType>("BEFORE_SCHEDULED_RELEASE");
  const [reminderOffset, setReminderOffset] = useState<number>(15);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEventId) return;

    try {
      setIsSubmitting(true);
      setSubmitError(null);
      await onCreateAlert({
        event_id: selectedEventId,
        alert_type: alertType,
        reminder_offset_minutes: reminderOffset,
        is_enabled: true,
      });
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to create alert");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div
        className="bg-atlas-background border border-atlas-border-subtle rounded-lg max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-atlas-border-subtle bg-atlas-surface/80">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded bg-amber-500/15 text-amber-400">
              <Bell className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                Economic Event Alerts & Notifications
              </h2>
              <p className="text-[10px] text-atlas-text-muted mt-0.5">
                Stage 49 Notification Center Integration • User-Owned Delivery Rules
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab switch */}
        <div className="flex items-center border-b border-atlas-border-subtle px-4 bg-atlas-surface/40 text-xs">
          <button
            onClick={() => setActiveSubTab("rules")}
            className={`py-2 px-3 font-medium border-b-2 transition-colors flex items-center gap-1.5 ${
              activeSubTab === "rules"
                ? "border-atlas-accent text-atlas-accent"
                : "border-transparent text-atlas-text-muted hover:text-atlas-text-primary"
            }`}
          >
            <Bell className="w-3.5 h-3.5" />
            <span>Configured Alerts ({alerts.length})</span>
          </button>
          <button
            onClick={() => setActiveSubTab("history")}
            className={`py-2 px-3 font-medium border-b-2 transition-colors flex items-center gap-1.5 ${
              activeSubTab === "history"
                ? "border-atlas-accent text-atlas-accent"
                : "border-transparent text-atlas-text-muted hover:text-atlas-text-primary"
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Delivery History ({deliveryHistory.length})</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-4 overflow-y-auto space-y-4 text-xs text-atlas-text-secondary flex-1">
          {activeSubTab === "rules" && (
            <>
              {/* Add New Alert Form */}
              <form
                onSubmit={handleCreate}
                className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded space-y-3"
              >
                <h3 className="font-semibold text-atlas-text-primary text-xs flex items-center gap-1.5">
                  <Bell className="w-3.5 h-3.5 text-atlas-accent" />
                  <span>Configure Release Alert</span>
                </h3>

                {submitError && (
                  <div className="p-2 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[11px] flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                    <span>{submitError}</span>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <div className="sm:col-span-2">
                    <label className="block text-[10px] text-atlas-text-muted uppercase font-mono mb-1">
                      Target Release Event
                    </label>
                    <select
                      value={selectedEventId}
                      onChange={(e) => setSelectedEventId(e.target.value)}
                      className="w-full p-1.5 bg-atlas-background border border-atlas-border-subtle rounded text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-accent"
                    >
                      {events.map((ev) => (
                        <option key={ev.event_id} value={ev.event_id}>
                          {ev.scheduled_start_display.split(" ")[0]} — {ev.title} (
                          {ev.geographic_entity_ids.join(",")})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[10px] text-atlas-text-muted uppercase font-mono mb-1">
                      Reminder Offset
                    </label>
                    <select
                      value={reminderOffset}
                      onChange={(e) => setReminderOffset(Number(e.target.value))}
                      className="w-full p-1.5 bg-atlas-background border border-atlas-border-subtle rounded text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-accent"
                    >
                      <option value={5}>5 minutes before</option>
                      <option value={15}>15 minutes before</option>
                      <option value={30}>30 minutes before</option>
                      <option value={60}>1 hour before</option>
                      <option value={120}>2 hours before</option>
                    </select>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[10px] text-atlas-text-muted">
                    Alert rules dispatch idempotent notification intents into Stage 49.
                  </span>
                  <button
                    type="submit"
                    disabled={isSubmitting || !selectedEventId}
                    className="px-3 py-1.5 rounded bg-atlas-accent hover:bg-atlas-accent/90 text-white font-medium text-xs transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? "Saving..." : "Add Event Alert"}
                  </button>
                </div>
              </form>

              {/* Active Rules List */}
              <div className="space-y-2">
                <h3 className="font-semibold text-atlas-text-primary text-xs uppercase tracking-wider">
                  Active Alerts ({alerts.length})
                </h3>

                {alerts.length === 0 ? (
                  <p className="text-atlas-text-muted italic text-xs py-4 text-center">
                    No active release alerts configured. Create one above to receive reminders.
                  </p>
                ) : (
                  alerts.map((al) => (
                    <div
                      key={al.alert_id}
                      className="p-3 bg-atlas-surface/60 border border-atlas-border-subtle rounded flex items-center justify-between gap-3 font-mono"
                    >
                      <div>
                        <div className="font-bold text-atlas-text-primary text-xs">
                          {al.event_title}
                        </div>
                        <div className="text-[10px] text-atlas-text-muted mt-0.5">
                          Trigger: {al.reminder_offset_minutes}m before • Scheduled:{" "}
                          {new Date(al.scheduled_time).toLocaleString()}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => onToggleEnabled(al.alert_id, !al.is_enabled)}
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold border transition-colors ${
                            al.is_enabled
                              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                              : "bg-atlas-surface text-atlas-text-muted border-atlas-border-subtle"
                          }`}
                        >
                          {al.is_enabled ? "ACTIVE" : "PAUSED"}
                        </button>
                        <button
                          onClick={() => onRemoveAlert(al.alert_id)}
                          className="p-1 text-atlas-text-muted hover:text-rose-400 transition-colors"
                          title="Cancel Alert Rule"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}

          {activeSubTab === "history" && (
            <div className="space-y-2">
              <h3 className="font-semibold text-atlas-text-primary text-xs uppercase tracking-wider">
                Notification Outbox & Delivery Log
              </h3>

              {deliveryHistory.length === 0 ? (
                <p className="text-atlas-text-muted italic text-xs py-4 text-center">
                  No notification delivery records found.
                </p>
              ) : (
                deliveryHistory.map((hist) => (
                  <div
                    key={hist.intent_id}
                    className="p-3 bg-atlas-surface/60 border border-atlas-border-subtle rounded font-mono text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-atlas-text-primary">{hist.title}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded border ${
                          hist.is_delivered
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                        }`}
                      >
                        {hist.is_delivered ? "DELIVERED" : "PENDING"}
                      </span>
                    </div>
                    <p className="text-[11px] text-atlas-text-secondary">{hist.body}</p>
                    <div className="text-[10px] text-atlas-text-muted">
                      Scheduled for: {new Date(hist.scheduled_for).toLocaleString()}
                      {hist.delivered_at &&
                        ` • Dispatched: ${new Date(hist.delivered_at).toLocaleTimeString()}`}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-atlas-border-subtle bg-atlas-surface/80 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-atlas-surface border border-atlas-border-subtle text-atlas-text-secondary hover:text-atlas-text-primary text-xs font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
