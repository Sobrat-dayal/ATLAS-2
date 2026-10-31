'use client';

import React from 'react';
import { TimelineResponse, AtlasUniversalEvent } from '@/lib/events/types';
import { EventCard } from './EventCard';
import { Calendar, Clock } from 'lucide-react';

interface UniversalEventTimelineProps {
  timeline: TimelineResponse | null;
  activeClock: string;
  onSelectEvent: (event: AtlasUniversalEvent) => void;
  onOpenAsOf: (event: AtlasUniversalEvent) => void;
}

export const UniversalEventTimeline: React.FC<UniversalEventTimelineProps> = ({
  timeline,
  activeClock,
  onSelectEvent,
  onOpenAsOf,
}) => {
  if (!timeline || timeline.events.length === 0) {
    return (
      <div className="py-12 text-center text-zinc-500 font-mono text-xs border border-dashed border-zinc-800 rounded-lg">
        No events found along the {activeClock} timeline for the selected criteria.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {timeline.buckets.map((bucket) => (
        <div key={bucket.bucket_date} className="space-y-3">
          {/* Date Bucket Header */}
          <div className="sticky top-0 z-10 flex items-center gap-2 bg-zinc-950/90 backdrop-blur py-1.5 border-b border-zinc-800 text-xs font-mono">
            <Calendar className="w-3.5 h-3.5 text-blue-400" />
            <span className="font-bold text-zinc-200">{bucket.bucket_date}</span>
            <span className="text-zinc-500 text-[11px]">
              ({bucket.event_count} event{bucket.event_count > 1 ? 's' : ''})
            </span>
          </div>

          {/* Event Cards in Bucket */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-2 border-l border-zinc-800">
            {bucket.events.map((event) => (
              <EventCard
                key={event.event_id}
                event={event}
                activeClock={activeClock}
                onSelect={onSelectEvent}
                onOpenAsOf={onOpenAsOf}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
