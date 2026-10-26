"use client";

import React, { useMemo } from "react";
import { EconomicCalendarEventDTO, UserEventAlertDTO } from "@/lib/economics/calendar";
import { EconomicEventRow } from "./EconomicEventRow";
import { Calendar, AlertCircle } from "lucide-react";

interface EconomicEventTableProps {
  events: EconomicCalendarEventDTO[];
  alerts: UserEventAlertDTO[];
  isLoading: boolean;
  onOpenDetail: (eventId: string) => void;
  onToggleAlert: (event: EconomicCalendarEventDTO) => void;
}

export function EconomicEventTable({
  events,
  alerts,
  isLoading,
  onOpenDetail,
  onToggleAlert,
}: EconomicEventTableProps) {
  // Set of event IDs user has alerts for
  const alertEventIds = useMemo(() => {
    return new Set(alerts.filter((a) => a.is_enabled).map((a) => a.event_id));
  }, [alerts]);

  // Group events by local date string ("YYYY-MM-DD")
  const groupedEvents = useMemo(() => {
    const groups: Record<string, EconomicCalendarEventDTO[]> = {};
    for (const ev of events) {
      const datePart = ev.scheduled_start_display.split(" ")[0] || "Unknown Date";
      if (!groups[datePart]) {
        groups[datePart] = [];
      }
      groups[datePart].push(ev);
    }
    return groups;
  }, [events]);

  const sortedDates = useMemo(() => {
    return Object.keys(groupedEvents).sort();
  }, [groupedEvents]);

  const formatDateHeader = (dateStr: string) => {
    try {
      // Parse YYYY-MM-DD
      const [year, month, day] = dateStr.split("-").map(Number);
      if (!year || !month || !day) return dateStr;
      const dateObj = new Date(Date.UTC(year, month - 1, day));
      return dateObj.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
        timeZone: "UTC",
      });
    } catch {
      return dateStr;
    }
  };

  if (isLoading && events.length === 0) {
    return (
      <div className="p-12 text-center text-atlas-text-muted flex flex-col items-center justify-center gap-2">
        <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
        <p className="text-xs font-mono">Synchronizing verified economic releases...</p>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="p-12 text-center text-atlas-text-muted border border-atlas-border-subtle rounded bg-atlas-surface/30 flex flex-col items-center justify-center gap-3">
        <div className="p-3 rounded-full bg-atlas-surface border border-atlas-border-subtle text-atlas-text-muted">
          <Calendar className="w-6 h-6" />
        </div>
        <div className="max-w-md">
          <h3 className="text-sm font-semibold text-atlas-text-primary mb-1">
            No Scheduled Economic Releases Found
          </h3>
          <p className="text-xs text-atlas-text-muted">
            No verified economic releases match your selected date range and filter criteria. Adjust your jurisdiction, category, or time horizon.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="border border-atlas-border-subtle rounded bg-atlas-surface/40 overflow-hidden shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-subtle bg-atlas-surface text-[10px] font-mono text-atlas-text-muted uppercase tracking-wider select-none sticky top-0 z-5">
              <th className="py-2 px-3 font-semibold w-24">Time</th>
              <th className="py-2 px-2 font-semibold w-14">Area</th>
              <th className="py-2 px-3 font-semibold">Event & Indicator</th>
              <th className="py-2 px-2 font-semibold w-16 text-center">Impact</th>
              <th className="py-2 px-3 font-semibold w-28 text-right">Actual</th>
              <th className="py-2 px-3 font-semibold w-24 text-right">Consensus</th>
              <th className="py-2 px-3 font-semibold w-24 text-right">Previous</th>
              <th className="py-2 px-3 font-semibold w-32 text-right">Surprise</th>
              <th className="py-2 px-3 font-semibold w-28 text-center">Status</th>
              <th className="py-2 px-3 font-semibold w-16 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {sortedDates.map((dateStr) => {
              const dayEvents = groupedEvents[dateStr] || [];
              return (
                <React.Fragment key={dateStr}>
                  {/* Date Group Header */}
                  <tr className="bg-atlas-background/80 border-y border-atlas-border-subtle/80">
                    <td colSpan={10} className="py-2 px-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-atlas-accent" />
                          <span className="text-xs font-bold text-atlas-text-primary tracking-tight">
                            {formatDateHeader(dateStr)}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-atlas-text-muted">
                          {dayEvents.length} {dayEvents.length === 1 ? "release" : "releases"}
                        </span>
                      </div>
                    </td>
                  </tr>

                  {/* Date Event Rows */}
                  {dayEvents.map((ev) => (
                    <EconomicEventRow
                      key={ev.event_id}
                      event={ev}
                      hasUserAlert={alertEventIds.has(ev.event_id)}
                      onOpenDetail={onOpenDetail}
                      onToggleAlert={onToggleAlert}
                    />
                  ))}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
