'use client';

import React from 'react';
import { AtlasUniversalEvent } from '@/lib/events/types';
import { CATEGORY_METADATA, VERIFICATION_BADGES, LIFECYCLE_BADGES } from '@/lib/events/taxonomy';
import { formatEventTimestamp, getActiveClockTime } from '@/lib/events/temporal';
import {
  ShieldAlert,
  AlertTriangle,
  History,
  Layers,
  FileText,
  Clock,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';

interface EventCardProps {
  event: AtlasUniversalEvent;
  activeClock?: string;
  onSelect: (event: AtlasUniversalEvent) => void;
  onOpenAsOf?: (event: AtlasUniversalEvent) => void;
}

export const EventCard: React.FC<EventCardProps> = ({
  event,
  activeClock = 'occurred_at',
  onSelect,
  onOpenAsOf,
}) => {
  const catMeta = CATEGORY_METADATA[event.event_category] || CATEGORY_METADATA.OTHER_VERIFIED_EVENT;
  const verBadge = VERIFICATION_BADGES[event.verification_status] || VERIFICATION_BADGES.UNVERIFIED;
  const lifeBadge = LIFECYCLE_BADGES[event.lifecycle_status] || LIFECYCLE_BADGES.STATUS_UNKNOWN;

  const clockTimestamp = getActiveClockTime(event, activeClock);
  const formattedTime = formatEventTimestamp(clockTimestamp, event.date_precision);

  const hasConflict = event.claim_conflict_status === 'CONFLICT_DETECTED' || event.claim_conflict_status === 'CONFLICTED';

  return (
    <div
      onClick={() => onSelect(event)}
      className={`group relative border rounded-lg p-4 transition-all duration-200 cursor-pointer bg-zinc-950/70 hover:bg-zinc-900/90 hover:border-zinc-700 ${
        event.is_retracted
          ? 'border-red-900/60 bg-red-950/20 opacity-75'
          : hasConflict
          ? 'border-amber-900/60'
          : 'border-zinc-800'
      } ${catMeta.borderClass} border-l-4`}
    >
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          {/* Category Badge */}
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${catMeta.badgeClass}`}>
            {catMeta.label}
          </span>

          {/* Verification Badge */}
          <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded uppercase tracking-wider ${verBadge.className}`}>
            {verBadge.label}
          </span>

          {/* Lifecycle Status */}
          <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase ${lifeBadge.className}`}>
            {lifeBadge.label}
          </span>
        </div>

        {/* Time Clock Display */}
        <div className="flex items-center text-xs text-zinc-400 font-mono gap-1">
          <Clock className="w-3.5 h-3.5 text-zinc-500" />
          <span>{formattedTime}</span>
        </div>
      </div>

      {/* Retraction Warning Banner */}
      {event.is_retracted && (
        <div className="mb-2 p-2 rounded bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center gap-2 font-mono">
          <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />
          <span>FORMALLY RETRACTED: {event.retraction_reason || 'Discredited / Erroneous Report'}</span>
        </div>
      )}

      {/* Cross-Source Claim Conflict Alert Banner */}
      {hasConflict && !event.is_retracted && (
        <div className="mb-2 p-1.5 rounded bg-amber-950/50 border border-amber-800 text-amber-300 text-[11px] flex items-center gap-2 font-mono">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>Cross-source factual claims conflict detected — conflicting values preserved without fabrication.</span>
        </div>
      )}

      {/* Title */}
      <h3 className="text-sm font-semibold text-zinc-100 group-hover:text-blue-400 transition-colors line-clamp-2 mb-1.5">
        {event.title}
      </h3>

      {/* Factual Summary */}
      <p className="text-xs text-zinc-400 line-clamp-2 leading-relaxed mb-3">
        {event.factual_summary}
      </p>

      {/* Footer Info & Badges */}
      <div className="flex flex-wrap items-center justify-between text-[11px] text-zinc-500 font-mono border-t border-zinc-800/80 pt-2 gap-2">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1" title="Primary ingestion source">
            <FileText className="w-3 h-3 text-zinc-400" />
            <span className="text-zinc-300">{event.primary_source_id}</span>
          </span>

          <span className="flex items-center gap-1" title="Number of corroborating evidence sources">
            <Layers className="w-3 h-3 text-zinc-400" />
            <span>{event.source_count} source{event.source_count > 1 ? 's' : ''}</span>
          </span>

          {event.current_revision_number > 1 && (
            <span className="flex items-center gap-1 text-cyan-400" title="Bitemporal revision count">
              <History className="w-3 h-3" />
              <span>Rev {event.current_revision_number}</span>
            </span>
          )}

          {event.geographic_scope.country_code && (
            <span className="text-zinc-400 uppercase">
              [{event.geographic_scope.country_code}]
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {onOpenAsOf && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOpenAsOf(event);
              }}
              className="px-2 py-0.5 rounded text-[10px] bg-zinc-800/80 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 flex items-center gap-1 transition-colors"
              title="Point-in-Time Historical Knowledge Evaluation"
            >
              <History className="w-3 h-3 text-amber-400" />
              <span>As-Of</span>
            </button>
          )}

          <span className="text-zinc-400 group-hover:text-zinc-200 flex items-center text-xs">
            Inspect <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
          </span>
        </div>
      </div>
    </div>
  );
};
