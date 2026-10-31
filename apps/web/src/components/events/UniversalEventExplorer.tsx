'use client';

import React, { useEffect, useState } from 'react';
import {
  AtlasUniversalEvent,
  EventSearchParams,
  EventSearchResult,
  TimelineResponse,
} from '@/lib/events/types';
import {
  fetchEventsSearch,
  fetchEventTimeline,
  fetchUpcomingEvents,
  fetchRecentEvents,
} from '@/lib/events/api';
import { EventCard } from './EventCard';
import { EventFilterPanel } from './EventFilterPanel';
import { EventDetailInspector } from './EventDetailInspector';
import { EventAsOfModal } from './EventAsOfModal';
import { EventReviewQueueModal } from './EventReviewQueueModal';
import { UniversalEventTimeline } from './UniversalEventTimeline';
import {
  Radio,
  Calendar,
  Layers,
  History,
  ShieldAlert,
  Clock,
  Sparkles,
  RefreshCw,
} from 'lucide-react';

export const UniversalEventExplorer: React.FC = () => {
  const [params, setParams] = useState<EventSearchParams>({
    time_clock: 'occurred_at',
    limit: 50,
    offset: 0,
  });

  const [viewMode, setViewMode] = useState<'timeline' | 'cards' | 'upcoming'>('timeline');
  const [searchResults, setSearchResults] = useState<EventSearchResult | null>(null);
  const [timelineData, setTimelineData] = useState<TimelineResponse | null>(null);
  const [upcomingEvents, setUpcomingEvents] = useState<AtlasUniversalEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<AtlasUniversalEvent | null>(null);
  const [asOfTargetEvent, setAsOfTargetEvent] = useState<AtlasUniversalEvent | null>(null);
  const [isAsOfModalOpen, setIsAsOfModalOpen] = useState<boolean>(false);
  const [isReviewQueueOpen, setIsReviewQueueOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      if (viewMode === 'timeline') {
        const tl = await fetchEventTimeline(params.time_clock || 'occurred_at', false, 100);
        setTimelineData(tl);
      } else if (viewMode === 'upcoming') {
        const up = await fetchUpcomingEvents(50);
        setUpcomingEvents(up);
      } else {
        const res = await fetchEventsSearch(params);
        setSearchResults(res);
      }
    } catch {
      // Fallback
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [viewMode, params]);

  const handleResetFilters = () => {
    setParams({
      time_clock: 'occurred_at',
      limit: 50,
      offset: 0,
    });
  };

  const handleOpenAsOf = (event?: AtlasUniversalEvent) => {
    setAsOfTargetEvent(event || null);
    setIsAsOfModalOpen(true);
  };

  return (
    <div className="flex flex-col h-full bg-black text-zinc-100 font-sans">
      {/* Top Header Bar */}
      <div className="flex flex-wrap items-center justify-between p-4 border-b border-zinc-800 bg-zinc-950/80 gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-950/60 border border-blue-800 text-blue-400">
            <Radio className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-zinc-100 flex items-center gap-2">
              <span>Universal Event Intelligence Foundation</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                Stage 135
              </span>
            </h1>
            <p className="text-xs text-zinc-400 font-mono">
              Canonical Bitemporal Financial, Economic, Corporate, Regulatory & Physical World Events
            </p>
          </div>
        </div>

        {/* View Switchers & Modals Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* View Mode Buttons */}
          <div className="flex items-center bg-zinc-900 border border-zinc-800 rounded p-0.5 text-xs font-mono">
            <button
              onClick={() => setViewMode('timeline')}
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
                viewMode === 'timeline'
                  ? 'bg-blue-600 text-white font-semibold'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Timeline</span>
            </button>

            <button
              onClick={() => setViewMode('cards')}
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
                viewMode === 'cards'
                  ? 'bg-blue-600 text-white font-semibold'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Grid / Cards</span>
            </button>

            <button
              onClick={() => setViewMode('upcoming')}
              className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
                viewMode === 'upcoming'
                  ? 'bg-blue-600 text-white font-semibold'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Upcoming</span>
            </button>
          </div>

          {/* As-Of Modal Trigger */}
          <button
            onClick={() => handleOpenAsOf()}
            className="px-3 py-1.5 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-amber-300 text-xs font-mono flex items-center gap-1.5 transition-colors"
            title="Point-in-Time Historical Evaluation (Zero Look-Ahead Bias)"
          >
            <History className="w-3.5 h-3.5 text-amber-400" />
            <span>As-Of Query</span>
          </button>

          {/* Review Queue Trigger */}
          <button
            onClick={() => setIsReviewQueueOpen(true)}
            className="px-3 py-1.5 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 text-xs font-mono flex items-center gap-1.5 transition-colors"
            title="Candidate Match Review Queue"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-blue-400" />
            <span>Review Queue</span>
          </button>

          {/* Reload Button */}
          <button
            onClick={loadData}
            className="p-1.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200"
            title="Refresh feed"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Content Area with Filters & Streams */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-w-7xl mx-auto w-full">
        {/* Filter Panel */}
        <EventFilterPanel
          params={params}
          onChange={setParams}
          onReset={handleResetFilters}
          totalEventsCount={searchResults?.total_count || timelineData?.total_events}
        />

        {/* View Mode Stream */}
        {viewMode === 'timeline' && (
          <UniversalEventTimeline
            timeline={timelineData}
            activeClock={params.time_clock || 'occurred_at'}
            onSelectEvent={setSelectedEvent}
            onOpenAsOf={handleOpenAsOf}
          />
        )}

        {viewMode === 'cards' && (
          <div>
            {searchResults && searchResults.events.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {searchResults.events.map((evt) => (
                  <EventCard
                    key={evt.event_id}
                    event={evt}
                    activeClock={params.time_clock}
                    onSelect={setSelectedEvent}
                    onOpenAsOf={handleOpenAsOf}
                  />
                ))}
              </div>
            ) : (
              <div className="py-12 text-center text-zinc-500 font-mono text-xs border border-dashed border-zinc-800 rounded-lg">
                No events matched the search criteria.
              </div>
            )}
          </div>
        )}

        {viewMode === 'upcoming' && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono text-amber-400 pb-2 border-b border-zinc-800">
              <Clock className="w-4 h-4" />
              <span className="font-bold">Official Upcoming Scheduled Events (Earnings, Releases, FOMC)</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {upcomingEvents.map((evt) => (
                <EventCard
                  key={evt.event_id}
                  event={evt}
                  activeClock="scheduled_for"
                  onSelect={setSelectedEvent}
                  onOpenAsOf={handleOpenAsOf}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Slide-over Detail Inspector */}
      <EventDetailInspector
        event={selectedEvent}
        onClose={() => setSelectedEvent(null)}
        onOpenAsOf={handleOpenAsOf}
      />

      {/* As-Of Historical Evaluation Modal */}
      <EventAsOfModal
        event={asOfTargetEvent}
        isOpen={isAsOfModalOpen}
        onClose={() => setIsAsOfModalOpen(false)}
        onSelectEvent={(e) => {
          setSelectedEvent(e);
          setIsAsOfModalOpen(false);
        }}
      />

      {/* Review Queue Modal */}
      <EventReviewQueueModal
        isOpen={isReviewQueueOpen}
        onClose={() => setIsReviewQueueOpen(false)}
      />
    </div>
  );
};

