/**
 * ATLAS Maps Live Physical-World API Client (Stage 134).
 */

import {
  AtlasGeoObservation,
  InfrastructureProximityMatch,
  LiveGeoProvider,
  LiveObservationCategory,
  SatelliteState,
  TrajectorySegment,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchLiveProviders(): Promise<LiveGeoProvider[]> {
  const res = await fetch(`${API_BASE}/maps/live/providers`);
  if (!res.ok) {
    throw new Error(`Failed to fetch live providers: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchLiveLayers(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/maps/live/layers`);
  if (!res.ok) {
    throw new Error(`Failed to fetch live layers: ${res.statusText}`);
  }
  const data = await res.json();
  return data.layers || [];
}

export async function fetchLiveSnapshot(
  categories?: LiveObservationCategory[],
  bbox?: [number, number, number, number],
  maxResults: number = 1000
): Promise<{ observations: AtlasGeoObservation[]; sequenceCursor: number; count: number }> {
  const res = await fetch(`${API_BASE}/maps/live/observations/snapshot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      categories,
      bbox,
      max_results: maxResults,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch live snapshot: ${res.statusText}`);
  }
  const data = await res.json();
  return {
    observations: data.observations || [],
    sequenceCursor: data.sequence_cursor,
    count: data.count,
  };
}

export async function fetchLiveDeltas(
  sinceSequence: number,
  categories?: LiveObservationCategory[],
  bbox?: [number, number, number, number],
  maxResults: number = 1000
): Promise<{ deltas: AtlasGeoObservation[]; sequenceCursor: number; count: number }> {
  const res = await fetch(`${API_BASE}/maps/live/observations/deltas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      since_sequence: sinceSequence,
      categories,
      bbox,
      max_results: maxResults,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch live deltas: ${res.statusText}`);
  }
  const data = await res.json();
  return {
    deltas: data.deltas || [],
    sequenceCursor: data.sequence_cursor,
    count: data.deltas_count,
  };
}

export async function fetchLivePlayback(
  targetTimeUtc: string,
  categories?: LiveObservationCategory[],
  windowSeconds: number = 3600
): Promise<{ observations: AtlasGeoObservation[]; targetTimeUtc: string; count: number }> {
  const res = await fetch(`${API_BASE}/maps/live/playback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_time_utc: targetTimeUtc,
      categories,
      window_seconds: windowSeconds,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch live playback snapshot: ${res.statusText}`);
  }
  const data = await res.json();
  return {
    observations: data.observations || [],
    targetTimeUtc: data.target_time_utc,
    count: data.count,
  };
}

export async function propagateSatelliteOrbit(payload: {
  noradCatId?: number;
  tleLine1?: string;
  tleLine2?: string;
  propagateAt?: string;
}): Promise<SatelliteState> {
  const res = await fetch(`${API_BASE}/maps/live/satellites/propagate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      norad_cat_id: payload.noradCatId,
      tle_line1: payload.tleLine1,
      tle_line2: payload.tleLine2,
      propagate_at: payload.propagateAt,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to propagate satellite orbit: ${res.statusText}`);
  }
  const data = await res.json();
  return data.satellite_state;
}

export async function correlateInfrastructureProximity(
  event: Record<string, any>,
  maxRadiusKm: number = 150
): Promise<{ matches: InfrastructureProximityMatch[]; disclaimer: string; count: number }> {
  const res = await fetch(`${API_BASE}/maps/live/infrastructure/proximity`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event,
      max_radius_km: maxRadiusKm,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to correlate infrastructure proximity: ${res.statusText}`);
  }
  const data = await res.json();
  return {
    matches: data.matches || [],
    disclaimer: data.disclaimer,
    count: data.match_count,
  };
}

export async function splitTrajectory(
  entityId: string,
  category: LiveObservationCategory,
  points: Array<{ longitude: number; latitude: number; timestamp: string; altitude_m?: number }>,
  maxGapSeconds?: number
): Promise<TrajectorySegment[]> {
  const res = await fetch(`${API_BASE}/maps/live/trajectories/split`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      entity_id: entityId,
      category,
      points,
      max_gap_seconds: maxGapSeconds,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to split trajectory: ${res.statusText}`);
  }
  const data = await res.json();
  return data.segments || [];
}

