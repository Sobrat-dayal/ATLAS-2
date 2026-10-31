'use client';

import React, { useEffect, useState } from 'react';
import {
  AtlasUniversalEvent,
  EventEvidence,
  EventClaim,
  EventRevision,
  EventSourceRecord,
} from '@/lib/events/types';
import { CATEGORY_METADATA, VERIFICATION_BADGES, LIFECYCLE_BADGES } from '@/lib/events/taxonomy';
import { formatEventTimestamp } from '@/lib/events/temporal';
import {
  fetchEventEvidence,
  fetchEventClaims,
  fetchEventRevisions,
  fetchEventSources,
} from '@/lib/events/api';
import {
  X,
  FileText,
  Layers,
  History,
  AlertTriangle,
  Globe,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Copy,
  Clock,
  Hash,
  Database,
} from 'lucide-react';

interface EventDetailInspectorProps {
  event: AtlasUniversalEvent | null;
  onClose: () => void;
  onOpenAsOf?: (event: AtlasUniversalEvent) => void;
}

type TabType = 'summary' | 'evidence' | 'claims' | 'revisions';

export const EventDetailInspector: React.FC<EventDetailInspectorProps> = ({
  event,
  onClose,
  onOpenAsOf,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('summary');
  const [evidenceList, setEvidenceList] = useState<EventEvidence[]>([]);
  const [claimsList, setClaimsList] = useState<EventClaim[]>([]);
  const [revisionsList, setRevisionsList] = useState<EventRevision[]>([]);
  const [sourcesList, setSourcesList] = useState<EventSourceRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copiedKey, setCopiedKey] = useState<boolean>(false);

  useEffect(() => {
    if (!event) return;
    let isMounted = true;
    setIsLoading(true);

    Promise.all([
      fetchEventEvidence(event.event_id).catch(() => []),
      fetchEventClaims(event.event_id).catch(() => []),
      fetchEventRevisions(event.event_id).catch(() => []),
      fetchEventSources(event.event_id).catch(() => []),
    ]).then(([evis, clms, revs, srcs]) => {
      if (isMounted) {
        setEvidenceList(evis);
        setClaimsList(clms);
        setRevisionsList(revs);
        setSourcesList(srcs);
        setIsLoading(false);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [event]);

  if (!event) return null;

  const catMeta = CATEGORY_METADATA[event.event_category] || CATEGORY_METADATA.OTHER_VERIFIED_EVENT;
  const verBadge = VERIFICATION_BADGES[event.verification_status] || VERIFICATION_BADGES.UNVERIFIED;
  const lifeBadge = LIFECYCLE_BADGES[event.lifecycle_status] || LIFECYCLE_BADGES.STATUS_UNKNOWN;

  const handleCopyKey = () => {
    navigator.clipboard.writeText(event.canonical_event_key);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  const hasConflict = event.claim_conflict_status === 'CONFLICT_DETECTED' || event.claim_conflict_status === 'CONFLICTED';

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[640px] lg:w-[720px] bg-zinc-950 border-l border-zinc-800 shadow-2xl flex flex-col font-sans text-zinc-100">
      {/* Drawer Header */}
      <div className="p-4 border-b border-zinc-800 bg-zinc-900/60 flex items-start justify-between gap-3">
        <div className="space-y-1.5 flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${catMeta.badgeClass}`}>
              {catMeta.label}
            </span>
            <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded uppercase ${verBadge.className}`}>
              {verBadge.label}
            </span>
            <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase ${lifeBadge.className}`}>
              {lifeBadge.label}
            </span>
            {event.current_revision_number > 1 && (
              <span className="text-[10px] font-mono text-cyan-400 border border-cyan-800/80 bg-cyan-950/40 px-1.5 py-0.5 rounded">
                Rev {event.current_revision_number}
              </span>
            )}
          </div>

          <h2 className="text-base font-bold text-zinc-100 leading-snug break-words">
            {event.title}
          </h2>

          <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
            <span className="text-zinc-500">Key:</span>
            <span className="text-zinc-300 truncate max-w-sm" title={event.canonical_event_key}>
              {event.canonical_event_key}
            </span>
            <button
              onClick={handleCopyKey}
              className="text-zinc-400 hover:text-zinc-200 transition-colors"
              title="Copy canonical event key"
            >
              {copiedKey ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onOpenAsOf && (
            <button
              onClick={() => onOpenAsOf(event)}
              className="px-2.5 py-1 text-xs font-mono bg-zinc-800 hover:bg-zinc-700 text-amber-300 border border-amber-900/60 rounded flex items-center gap-1 transition-colors"
              title="Historical Point-in-Time Knowledge Query"
            >
              <History className="w-3.5 h-3.5 text-amber-400" />
              <span>As-Of</span>
            </button>
          )}

          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-zinc-800 bg-zinc-950 px-4 text-xs font-mono">
        <button
          onClick={() => setActiveTab('summary')}
          className={`py-2.5 px-3 border-b-2 font-medium flex items-center gap-1.5 transition-colors ${
            activeTab === 'summary'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Summary</span>
        </button>

        <button
          onClick={() => setActiveTab('evidence')}
          className={`py-2.5 px-3 border-b-2 font-medium flex items-center gap-1.5 transition-colors ${
            activeTab === 'evidence'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Evidence ({evidenceList.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('claims')}
          className={`py-2.5 px-3 border-b-2 font-medium flex items-center gap-1.5 transition-colors ${
            activeTab === 'claims'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          {hasConflict ? (
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
          ) : (
            <ShieldCheck className="w-3.5 h-3.5" />
          )}
          <span>Claims ({claimsList.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('revisions')}
          className={`py-2.5 px-3 border-b-2 font-medium flex items-center gap-1.5 transition-colors ${
            activeTab === 'revisions'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <History className="w-3.5 h-3.5" />
          <span>Revisions ({revisionsList.length})</span>
        </button>
      </div>

      {/* Tab Contents */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs font-sans">
        {/* SUMMARY TAB */}
        {activeTab === 'summary' && (
          <div className="space-y-4">
            {/* Factual Summary Card */}
            <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-3">
              <h4 className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider mb-1.5">
                Verified Factual Summary
              </h4>
              <p className="text-zinc-200 leading-relaxed text-sm">
                {event.factual_summary}
              </p>
            </div>

            {/* Multi-Clock Temporal Metadata */}
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-3 space-y-2">
              <h4 className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-blue-400" />
                <span>Multi-Clock Temporal Profile</span>
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono text-[11px]">
                <div className="bg-zinc-950/60 p-2 rounded border border-zinc-800/80">
                  <span className="text-zinc-500 block">Occurred At:</span>
                  <span className="text-zinc-200 font-semibold">
                    {formatEventTimestamp(event.occurred_at, event.date_precision)}
                  </span>
                </div>

                <div className="bg-zinc-950/60 p-2 rounded border border-zinc-800/80">
                  <span className="text-zinc-500 block">Published At:</span>
                  <span className="text-zinc-200">
                    {formatEventTimestamp(event.source_published_at, event.date_precision)}
                  </span>
                </div>

                {event.scheduled_for && (
                  <div className="bg-zinc-950/60 p-2 rounded border border-zinc-800/80">
                    <span className="text-zinc-500 block">Scheduled For:</span>
                    <span className="text-amber-300">
                      {formatEventTimestamp(event.scheduled_for, event.date_precision)}
                    </span>
                  </div>
                )}

                {event.effective_at && (
                  <div className="bg-zinc-950/60 p-2 rounded border border-zinc-800/80">
                    <span className="text-zinc-500 block">Effective At:</span>
                    <span className="text-cyan-300">
                      {formatEventTimestamp(event.effective_at, event.date_precision)}
                    </span>
                  </div>
                )}

                <div className="bg-zinc-950/60 p-2 rounded border border-zinc-800/80">
                  <span className="text-zinc-500 block">System Ingested:</span>
                  <span className="text-zinc-400">
                    {formatEventTimestamp(event.first_ingested_at, 'EXACT_TIMESTAMP')}
                  </span>
                </div>

                <div className="bg-zinc-950/60 p-2 rounded border border-zinc-800/80">
                  <span className="text-zinc-500 block">Precision Tier:</span>
                  <span className="text-blue-300 font-semibold">{event.date_precision}</span>
                </div>
              </div>
            </div>

            {/* Geographic Scope */}
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-3">
              <h4 className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>Geographic & Jurisdictional Scope</span>
              </h4>
              <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
                <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200">
                  Type: {event.geographic_scope.scope_type}
                </span>
                {event.geographic_scope.country_code && (
                  <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-emerald-400">
                    Jurisdiction: {event.geographic_scope.country_code}
                  </span>
                )}
                {event.geographic_scope.location_name && (
                  <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200">
                    Place: {event.geographic_scope.location_name}
                  </span>
                )}
                {event.geographic_scope.latitude !== null && event.geographic_scope.latitude !== undefined && (
                  <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-400">
                    Lat/Lon: {event.geographic_scope.latitude.toFixed(4)}, {event.geographic_scope.longitude?.toFixed(4)}
                  </span>
                )}
              </div>
            </div>

            {/* Event Payload Data */}
            <div className="bg-zinc-900/40 border border-zinc-800 rounded-lg p-3">
              <h4 className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-purple-400" />
                <span>Structured Domain Payload</span>
              </h4>
              <pre className="p-2.5 rounded bg-zinc-950 border border-zinc-800 font-mono text-[11px] text-zinc-300 overflow-x-auto">
                {JSON.stringify(event.event_payload, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* EVIDENCE TAB */}
        {activeTab === 'evidence' && (
          <div className="space-y-3">
            <div className="text-zinc-400 text-xs font-mono flex items-center justify-between pb-1 border-b border-zinc-800">
              <span>Supporting authorized source releases and regulatory filings</span>
              <span className="text-blue-400">{evidenceList.length} total</span>
            </div>

            {evidenceList.map((ev) => (
              <div key={ev.evidence_id} className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/50 space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-[11px]">
                  <span className="px-2 py-0.5 rounded bg-zinc-800 text-blue-400 border border-zinc-700 uppercase">
                    {ev.evidence_role.replace('_', ' ')}
                  </span>
                  <span className="text-zinc-500">
                    Recorded: {formatEventTimestamp(ev.recorded_at, 'EXACT_TIMESTAMP')}
                  </span>
                </div>

                {ev.snippet && (
                  <blockquote className="border-l-2 border-zinc-700 pl-2.5 py-1 italic text-zinc-300 text-xs bg-zinc-950/40">
                    &ldquo;{ev.snippet}&rdquo;
                  </blockquote>
                )}

                <div className="text-[11px] font-mono text-zinc-400 flex items-center justify-between pt-1 border-t border-zinc-800/60">
                  <span>Source ID: {ev.source_record_id}</span>
                  <span className="text-zinc-500">Status: {ev.verification_status}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* CLAIMS & CONFLICTS TAB */}
        {activeTab === 'claims' && (
          <div className="space-y-3">
            {hasConflict && (
              <div className="p-3 rounded-lg bg-amber-950/60 border border-amber-800 text-amber-200 text-xs space-y-1">
                <div className="font-semibold flex items-center gap-1.5 font-mono">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>PRESERVED SOURCE CONTRADICTION</span>
                </div>
                <p className="text-[11px] leading-relaxed text-amber-300">
                  Multiple sources have asserted conflicting factual values for identical predicates.
                  Per ATLAS Institutional Rule 1779, conflicting claims are preserved verbatim with source attribution and NEVER averaged into fabricated synthetic values.
                </p>
              </div>
            )}

            <div className="space-y-2">
              {claimsList.map((clm) => (
                <div key={clm.claim_id} className="p-2.5 rounded border border-zinc-800 bg-zinc-900/50 space-y-1 font-mono text-xs">
                  <div className="flex items-center justify-between text-zinc-400">
                    <span className="text-zinc-300 font-semibold">{clm.predicate}</span>
                    <span className="text-[10px] text-zinc-500">Source: {clm.source_record_id}</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-base font-bold text-zinc-100">
                      {String(clm.claim_value)}
                    </span>
                    {clm.units && <span className="text-zinc-400 text-xs">{clm.units}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* REVISIONS TAB */}
        {activeTab === 'revisions' && (
          <div className="space-y-3">
            <div className="text-zinc-400 text-xs font-mono pb-1 border-b border-zinc-800">
              Immutable Bitemporal Audit History (Zero Look-Ahead Bias)
            </div>

            {revisionsList.map((rev) => (
              <div key={rev.event_revision_id} className="p-3 rounded-lg border border-zinc-800 bg-zinc-900/50 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-cyan-400">Revision #{rev.revision_number}</span>
                  <span className="text-zinc-500">
                    Recorded: {formatEventTimestamp(rev.recorded_at, 'EXACT_TIMESTAMP')}
                  </span>
                </div>

                <div className="text-xs text-zinc-300 font-medium">
                  Reason: {rev.reason}
                </div>

                {rev.changed_fields && Object.keys(rev.changed_fields).length > 0 && (
                  <div className="mt-2 p-2 rounded bg-zinc-950 border border-zinc-800 text-[11px] font-mono">
                    <span className="text-zinc-500 block mb-1">State Snapshot / Changed Fields:</span>
                    <pre className="text-zinc-300 overflow-x-auto">
                      {JSON.stringify(rev.changed_fields, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

