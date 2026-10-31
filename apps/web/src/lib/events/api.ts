/**
 * Universal Event Model API Client (Stage 135)
 */

import {
  AtlasUniversalEvent,
  EventEvidence,
  EventClaim,
  EventRevision,
  EventSourceRecord,
  EventSearchParams,
  EventSearchResult,
  TimelineResponse,
  ReviewItem,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`Events API error ${res.status}: ${errorBody}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchEventCapabilities(): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/api/v1/events/capabilities`);
  return handleResponse<Record<string, unknown>>(res);
}

export async function fetchEventTypes(): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/api/v1/events/types`);
  return handleResponse<Record<string, unknown>>(res);
}

export async function fetchEventsSearch(params: EventSearchParams): Promise<EventSearchResult> {
  const res = await fetch(`${API_BASE}/api/v1/events/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return handleResponse<EventSearchResult>(res);
}

export async function fetchEventTimeline(
  clock: string = 'occurred_at',
  ascending: boolean = false,
  limit: number = 100
): Promise<TimelineResponse> {
  const url = `${API_BASE}/api/v1/events/timeline?clock=${encodeURIComponent(clock)}&ascending=${ascending}&limit=${limit}`;
  const res = await fetch(url);
  return handleResponse<TimelineResponse>(res);
}

export async function fetchUpcomingEvents(limit: number = 50): Promise<AtlasUniversalEvent[]> {
  const res = await fetch(`${API_BASE}/api/v1/events/upcoming?limit=${limit}`);
  return handleResponse<AtlasUniversalEvent[]>(res);
}

export async function fetchRecentEvents(limit: number = 50): Promise<AtlasUniversalEvent[]> {
  const res = await fetch(`${API_BASE}/api/v1/events/recent?limit=${limit}`);
  return handleResponse<AtlasUniversalEvent[]>(res);
}

export async function fetchEventById(eventId: string): Promise<AtlasUniversalEvent> {
  const res = await fetch(`${API_BASE}/api/v1/events/${encodeURIComponent(eventId)}`);
  return handleResponse<AtlasUniversalEvent>(res);
}

export async function fetchEventEvidence(eventId: string): Promise<EventEvidence[]> {
  const res = await fetch(`${API_BASE}/api/v1/events/${encodeURIComponent(eventId)}/evidence`);
  return handleResponse<EventEvidence[]>(res);
}

export async function fetchEventClaims(eventId: string): Promise<EventClaim[]> {
  const res = await fetch(`${API_BASE}/api/v1/events/${encodeURIComponent(eventId)}/claims`);
  return handleResponse<EventClaim[]>(res);
}

export async function fetchEventRevisions(eventId: string): Promise<EventRevision[]> {
  const res = await fetch(`${API_BASE}/api/v1/events/${encodeURIComponent(eventId)}/revisions`);
  return handleResponse<EventRevision[]>(res);
}

export async function fetchEventSources(eventId: string): Promise<EventSourceRecord[]> {
  const res = await fetch(`${API_BASE}/api/v1/events/${encodeURIComponent(eventId)}/sources`);
  return handleResponse<EventSourceRecord[]>(res);
}

export async function fetchAsOfHistoricalEvents(
  asOfTime: string,
  eventId?: string
): Promise<AtlasUniversalEvent[]> {
  const res = await fetch(`${API_BASE}/api/v1/events/as-of`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ as_of_time: asOfTime, event_id: eventId }),
  });
  return handleResponse<AtlasUniversalEvent[]>(res);
}

export async function fetchReviewQueue(status?: string): Promise<ReviewItem[]> {
  const url = status
    ? `${API_BASE}/api/v1/events/review-queue?status=${encodeURIComponent(status)}`
    : `${API_BASE}/api/v1/events/review-queue`;
  const res = await fetch(url);
  return handleResponse<ReviewItem[]>(res);
}

export async function resolveReviewQueueItem(
  reviewId: string,
  resolution: 'CONFIRMED_MERGE' | 'CONFIRMED_SEPARATE'
): Promise<unknown> {
  const res = await fetch(`${API_BASE}/api/v1/events/review-queue/${encodeURIComponent(reviewId)}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resolution }),
  });
  return handleResponse<unknown>(res);
}
