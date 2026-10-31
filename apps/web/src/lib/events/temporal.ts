/**
 * Temporal formatting and multi-clock utilities for Universal Events (Stage 135)
 */

import { DatePrecision, AtlasUniversalEvent } from './types';

export function formatEventTimestamp(
  isoDateStr: string | null | undefined,
  precision: DatePrecision = 'EXACT_TIMESTAMP',
  timeZone: string = 'UTC'
): string {
  if (!isoDateStr) return 'Undated';

  const date = new Date(isoDateStr);
  if (isNaN(date.getTime())) return isoDateStr;

  switch (precision) {
    case 'DATE_ONLY':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        timeZone,
      });

    case 'MONTH_ONLY':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        timeZone,
      });

    case 'YEAR_ONLY':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        timeZone,
      });

    case 'TIME_UNKNOWN':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        timeZone,
      }) + ' (Time Unknown)';

    case 'EXACT_TIMESTAMP':
    default:
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone,
        timeZoneName: 'short',
      });
  }
}

export function getActiveClockTime(event: AtlasUniversalEvent, clock: string): string | null {
  const c = clock.toLowerCase();
  if (c.includes('occurred')) {
    return event.occurred_at || event.announced_at || event.source_published_at || null;
  }
  if (c.includes('announced')) {
    return event.announced_at || event.occurred_at || null;
  }
  if (c.includes('published')) {
    return event.source_published_at || event.occurred_at || null;
  }
  if (c.includes('scheduled')) {
    return event.scheduled_for || event.occurred_at || null;
  }
  if (c.includes('effective')) {
    return event.effective_at || event.occurred_at || null;
  }
  return event.occurred_at || event.first_ingested_at;
}

export function computeRateChangeBps(newRate: number, prevRate: number): number {
  return Math.round((newRate - prevRate) * 100 * 100) / 100;
}

