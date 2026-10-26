"use client";

import React from "react";
import {
  EconomicCalendarEventDTO,
  EconomicEventImportance,
  EconomicEventStatus,
} from "@/lib/economics/calendar";
import { EconomicSurpriseBadge } from "./EconomicSurpriseBadge";
import {
  Bell,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  ExternalLink,
  ChevronRight,
  Info,
} from "lucide-react";

interface EconomicEventRowProps {
  event: EconomicCalendarEventDTO;
  hasUserAlert: boolean;
  onOpenDetail: (eventId: string) => void;
  onToggleAlert: (event: EconomicCalendarEventDTO) => void;
}

const COUNTRY_CONFIG: Record<string, { label: string; code: string; color: string }> = {
  US: { label: "United States", code: "US", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" },
  EA: { label: "Euro Area", code: "EU", color: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
  EU: { label: "Euro Area", code: "EU", color: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
  GB: { label: "United Kingdom", code: "GB", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
  JP: { label: "Japan", code: "JP", color: "bg-rose-500/10 text-rose-400 border-rose-500/20" },
  IN: { label: "India", code: "IN", color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
  CN: { label: "China", code: "CN", color: "bg-red-500/10 text-red-400 border-red-500/20" },
};

export function EconomicEventRow({
  event,
  hasUserAlert,
  onOpenDetail,
  onToggleAlert,
}: EconomicEventRowProps) {
  const geoId = event.geographic_entity_ids[0] || "GLOBAL";
  const geoConfig = COUNTRY_CONFIG[geoId] || {
    label: geoId,
    code: geoId,
    color: "bg-atlas-surface text-atlas-text-secondary border-atlas-border-subtle",
  };

  // Importance visual
  const renderImportance = (imp: EconomicEventImportance) => {
    switch (imp) {
      case "HIGH":
        return (
          <div className="flex items-center gap-0.5" title="High Market Significance">
            <span className="w-1.5 h-3 bg-rose-500 rounded-2xs" />
            <span className="w-1.5 h-3 bg-rose-500 rounded-2xs" />
            <span className="w-1.5 h-3 bg-rose-500 rounded-2xs" />
          </div>
        );
      case "MEDIUM":
        return (
          <div className="flex items-center gap-0.5" title="Medium Market Significance">
            <span className="w-1.5 h-3 bg-amber-400 rounded-2xs" />
            <span className="w-1.5 h-3 bg-amber-400 rounded-2xs" />
            <span className="w-1.5 h-3 bg-atlas-border-subtle rounded-2xs" />
          </div>
        );
      case "LOW":
        return (
          <div className="flex items-center gap-0.5" title="Low Market Significance">
            <span className="w-1.5 h-3 bg-emerald-400 rounded-2xs" />
            <span className="w-1.5 h-3 bg-atlas-border-subtle rounded-2xs" />
            <span className="w-1.5 h-3 bg-atlas-border-subtle rounded-2xs" />
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-0.5" title="Unclassified">
            <span className="w-1.5 h-3 bg-atlas-border-subtle rounded-2xs" />
            <span className="w-1.5 h-3 bg-atlas-border-subtle rounded-2xs" />
            <span className="w-1.5 h-3 bg-atlas-border-subtle rounded-2xs" />
          </div>
        );
    }
  };

  // Status badge
  const renderStatus = (status: EconomicEventStatus) => {
    switch (status) {
      case "RELEASE_VERIFIED":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>VERIFIED</span>
          </span>
        );
      case "RESCHEDULED":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
            <Clock className="w-3 h-3" />
            <span>RESCHEDULED</span>
          </span>
        );
      case "POSTPONED":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium text-amber-500 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>POSTPONED</span>
          </span>
        );
      case "CANCELLED":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded border border-rose-500/20">
            <XCircle className="w-3 h-3" />
            <span>CANCELLED</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-medium text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded border border-blue-500/20">
            <Clock className="w-3 h-3" />
            <span>SCHEDULED</span>
          </span>
        );
    }
  };

  // Format time portion from scheduled_start_display
  const timeDisplay =
    event.schedule_precision === "DATE_ONLY"
      ? "Date Only"
      : event.scheduled_start_display.split(" ")[1] || event.scheduled_start_display;

  return (
    <tr
      onClick={() => onOpenDetail(event.event_id)}
      className="border-b border-atlas-border-subtle/60 hover:bg-atlas-surface/60 transition-colors cursor-pointer text-xs group"
    >
      {/* Column 1: Time */}
      <td className="py-2.5 px-3 font-mono font-medium whitespace-nowrap text-atlas-text-secondary">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3 h-3 text-atlas-text-muted" />
          <span>{timeDisplay}</span>
        </div>
      </td>

      {/* Column 2: Country / Area */}
      <td className="py-2.5 px-2 whitespace-nowrap">
        <span
          className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-mono font-bold border ${geoConfig.color}`}
          title={geoConfig.label}
        >
          {geoConfig.code}
        </span>
      </td>

      {/* Column 3: Event & Reference Period */}
      <td className="py-2.5 px-3">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-atlas-text-primary group-hover:text-atlas-accent transition-colors">
              {event.title}
            </span>
            {event.reference_period && (
              <span className="text-[10px] font-mono text-atlas-text-muted px-1.5 py-0.2 rounded bg-atlas-surface border border-atlas-border-subtle">
                {event.reference_period}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-[10px] text-atlas-text-muted mt-0.5">
            <span>{event.official_source_name}</span>
            <span>•</span>
            <span className="uppercase">{event.category.replace("_", " ")}</span>
          </div>
        </div>
      </td>

      {/* Column 4: Importance */}
      <td className="py-2.5 px-2 whitespace-nowrap text-center">
        <div className="inline-flex justify-center">
          {renderImportance(event.importance)}
        </div>
      </td>

      {/* Column 5: Actual */}
      <td className="py-2.5 px-3 font-mono whitespace-nowrap text-right">
        {event.actual_value !== null && event.actual_value !== undefined ? (
          <span className="font-bold text-atlas-text-primary text-[13px]">
            {event.actual_value.toLocaleString()} {event.unit}
          </span>
        ) : event.event_status === "RELEASE_VERIFIED" ? (
          <span className="text-atlas-text-muted italic text-[11px]">Processing...</span>
        ) : (
          <span className="text-atlas-text-muted text-[11px]">—</span>
        )}
      </td>

      {/* Column 6: Forecast */}
      <td className="py-2.5 px-3 font-mono whitespace-nowrap text-right text-atlas-text-secondary">
        {event.consensus_value !== null && event.consensus_value !== undefined ? (
          <span>
            {event.consensus_value.toLocaleString()} {event.unit}
          </span>
        ) : (
          <span className="text-atlas-text-muted">—</span>
        )}
      </td>

      {/* Column 7: Previous (with revision indicator if available) */}
      <td className="py-2.5 px-3 font-mono whitespace-nowrap text-right text-atlas-text-muted">
        {event.previous_value !== null && event.previous_value !== undefined ? (
          <div className="flex flex-col items-end">
            <span>
              {event.previous_value.toLocaleString()} {event.unit}
            </span>
            {event.revised_previous_value !== null &&
              event.revised_previous_value !== undefined &&
              event.revised_previous_value !== event.previous_value && (
                <span
                  className="text-[9px] text-amber-400 font-mono"
                  title={`Revised from ${event.previous_value} to ${event.revised_previous_value}`}
                >
                  Rev: {event.revised_previous_value.toLocaleString()}
                </span>
              )}
          </div>
        ) : (
          <span>—</span>
        )}
      </td>

      {/* Column 8: Surprise */}
      <td className="py-2.5 px-3 whitespace-nowrap text-right">
        <EconomicSurpriseBadge surprise={event.surprise} compact={true} />
      </td>

      {/* Column 9: Status */}
      <td className="py-2.5 px-3 whitespace-nowrap text-center">
        {renderStatus(event.event_status)}
      </td>

      {/* Column 10: Actions */}
      <td
        className="py-2.5 px-3 whitespace-nowrap text-right"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-end gap-1">
          <button
            onClick={() => onToggleAlert(event)}
            className={`p-1 rounded transition-colors ${
              hasUserAlert
                ? "text-amber-400 bg-amber-500/10 hover:bg-amber-500/20"
                : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface"
            }`}
            title={hasUserAlert ? "Alert Active - Click to Manage" : "Set Release Reminder"}
          >
            <Bell className={`w-3.5 h-3.5 ${hasUserAlert ? "fill-current" : ""}`} />
          </button>
          <button
            onClick={() => onOpenDetail(event.event_id)}
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface transition-colors"
            title="Inspect Official Release Details"
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </td>
    </tr>
  );
}
