'use client';

import React from 'react';
import {
  EventCategory,
  EventLifecycleStatus,
  EventVerificationStatus,
  EventSearchParams,
} from '@/lib/events/types';
import { CATEGORY_METADATA } from '@/lib/events/taxonomy';
import { Search, Filter, RotateCcw, Clock, ShieldCheck } from 'lucide-react';

interface EventFilterPanelProps {
  params: EventSearchParams;
  onChange: (updated: EventSearchParams) => void;
  onReset: () => void;
  totalEventsCount?: number;
}

const CATEGORIES: EventCategory[] = [
  'FINANCIAL',
  'CORPORATE',
  'ECONOMIC',
  'MONETARY_POLICY',
  'REGULATORY',
  'SANCTIONS',
  'GEOPOLITICAL',
  'NATURAL_DISASTER',
  'PHYSICAL_WORLD',
  'INFRASTRUCTURE',
  'NEWS_REPORTED',
];

const CLOCKS = [
  { id: 'occurred_at', label: 'Occurred At (Default)' },
  { id: 'source_published_at', label: 'Published At' },
  { id: 'scheduled_for', label: 'Scheduled For' },
  { id: 'announced_at', label: 'Announced At' },
  { id: 'effective_at', label: 'Effective At' },
];

export const EventFilterPanel: React.FC<EventFilterPanelProps> = ({
  params,
  onChange,
  onReset,
  totalEventsCount,
}) => {
  const toggleCategory = (cat: EventCategory) => {
    const current = params.categories || [];
    const exists = current.includes(cat);
    const updated = exists ? current.filter((c) => c !== cat) : [...current, cat];
    onChange({ ...params, categories: updated.length ? updated : undefined, offset: 0 });
  };

  const toggleVerification = (ver: EventVerificationStatus) => {
    const current = params.verification_statuses || [];
    const exists = current.includes(ver);
    const updated = exists ? current.filter((v) => v !== ver) : [...current, ver];
    onChange({ ...params, verification_statuses: updated.length ? updated : undefined, offset: 0 });
  };

  return (
    <div className="bg-zinc-950/80 border border-zinc-800 rounded-lg p-4 space-y-4">
      {/* Search Header */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-3 border-b border-zinc-800/80">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-zinc-500" />
          <input
            type="text"
            placeholder="Search canonical events, issuers, indicators, jurisdictions..."
            value={params.query || ''}
            onChange={(e) => onChange({ ...params, query: e.target.value || undefined, offset: 0 })}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-zinc-900 border border-zinc-700/80 rounded text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Time Clock Selector */}
          <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-mono">
            <Clock className="w-3.5 h-3.5 text-zinc-500" />
            <select
              value={params.time_clock || 'occurred_at'}
              onChange={(e) => onChange({ ...params, time_clock: e.target.value, offset: 0 })}
              className="bg-zinc-900 border border-zinc-700/80 rounded px-2 py-1 text-xs text-zinc-200 font-mono focus:outline-none"
            >
              {CLOCKS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={onReset}
            className="px-2.5 py-1 text-xs text-zinc-400 hover:text-zinc-200 border border-zinc-800 hover:border-zinc-700 rounded flex items-center gap-1 bg-zinc-900 font-mono transition-colors"
            title="Reset Filters"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Categories Filter Pills */}
      <div>
        <div className="text-[11px] font-mono text-zinc-400 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>Event Categories</span>
          {params.categories && (
            <span className="text-blue-400 lowercase">{params.categories.length} selected</span>
          )}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {CATEGORIES.map((cat) => {
            const isSelected = params.categories?.includes(cat);
            const meta = CATEGORY_METADATA[cat];
            return (
              <button
                key={cat}
                onClick={() => toggleCategory(cat)}
                className={`text-[10px] font-mono px-2 py-1 rounded border transition-all duration-150 ${
                  isSelected
                    ? `${meta.badgeClass} ring-1 ring-white/20 font-semibold shadow-sm`
                    : 'bg-zinc-900/80 border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700'
                }`}
              >
                {meta.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Verification Statuses & Retraction Toggle */}
      <div className="flex flex-wrap items-center justify-between pt-2 border-t border-zinc-800/80 gap-3 text-xs font-mono">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-zinc-500 uppercase flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-zinc-500" />
            Verification:
          </span>
          {(['OFFICIALLY_CONFIRMED', 'INDEPENDENTLY_CORROBORATED', 'CONFLICTED', 'UNVERIFIED'] as EventVerificationStatus[]).map((v) => {
            const isSelected = params.verification_statuses?.includes(v);
            return (
              <button
                key={v}
                onClick={() => toggleVerification(v)}
                className={`text-[10px] px-2 py-0.5 rounded border ${
                  isSelected
                    ? 'bg-blue-950 border-blue-700 text-blue-300 font-semibold'
                    : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200'
                }`}
              >
                {v.replace('_', ' ')}
              </button>
            );
          })}
        </div>

        {/* Retraction Toggle */}
        <label className="flex items-center gap-2 cursor-pointer text-zinc-400 hover:text-zinc-200 select-none">
          <input
            type="checkbox"
            checked={Boolean(params.include_retracted)}
            onChange={(e) => onChange({ ...params, include_retracted: e.target.checked, offset: 0 })}
            className="rounded bg-zinc-900 border-zinc-700 text-red-500 focus:ring-0"
          />
          <span className="text-[11px]">Include Retracted Events</span>
        </label>
      </div>
    </div>
  );
};

