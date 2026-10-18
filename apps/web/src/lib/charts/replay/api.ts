/**
 * Authenticated API Client for Stage 75: Historical Chart Replay V1.
 *
 * Communicates with `/api/v1/charts/replay` endpoints.
 */

import {
  ReplayCapabilityResponse,
  ReplaySeekRequest,
  ReplaySeekResponse,
  ReplaySessionDTO,
  ReplayStartRequest,
  ReplayStartResponse,
  ReplayStepRequest,
  ReplayStepResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function parseResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson.error?.message) {
        errorDetail = errJson.error.message;
      } else if (errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      // Fallback to status text
    }
    throw new Error(errorDetail);
  }
  return res.json() as Promise<T>;
}

export async function fetchReplayCapabilities(
  instrumentIdOrSymbol: string,
  interval: string = "1d"
): Promise<ReplayCapabilityResponse> {
  const isUuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
    instrumentIdOrSymbol
  );
  const param = isUuid ? `instrument_id=${instrumentIdOrSymbol}` : `symbol=${instrumentIdOrSymbol}`;
  const res = await fetch(
    `${API_BASE}/api/v1/charts/replay/capabilities?${param}&interval=${interval}`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    }
  );
  return parseResponse<ReplayCapabilityResponse>(res);
}

export const getReplayCapabilities = fetchReplayCapabilities;

export async function createReplaySession(
  request: ReplayStartRequest
): Promise<ReplayStartResponse> {
  const res = await fetch(`${API_BASE}/api/v1/charts/replay/sessions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
  });
  return parseResponse<ReplayStartResponse>(res);
}

export async function fetchReplaySessionStatus(
  sessionId: string
): Promise<ReplaySessionDTO> {
  const res = await fetch(`${API_BASE}/api/v1/charts/replay/sessions/${sessionId}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });
  return parseResponse<ReplaySessionDTO>(res);
}

export async function stepReplaySession(
  sessionId: string,
  request: ReplayStepRequest
): Promise<ReplayStepResponse> {
  const res = await fetch(`${API_BASE}/api/v1/charts/replay/sessions/${sessionId}/step`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
  });
  return parseResponse<ReplayStepResponse>(res);
}

export async function seekReplaySession(
  sessionId: string,
  request: ReplaySeekRequest
): Promise<ReplaySeekResponse> {
  const res = await fetch(`${API_BASE}/api/v1/charts/replay/sessions/${sessionId}/seek`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(request),
  });
  return parseResponse<ReplaySeekResponse>(res);
}

export async function closeReplaySession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/charts/replay/sessions/${sessionId}`, {
    method: "DELETE",
    headers: {
      Accept: "application/json",
    },
  });
  if (!res.ok && res.status !== 404) {
    throw new Error(`Failed to close replay session: HTTP ${res.status}`);
  }
}

export async function calculateReplayIndicators(
  sessionId: string,
  payload: any
): Promise<any> {
  const res = await fetch(
    `${API_BASE}/api/v1/charts/replay/sessions/${sessionId}/indicators`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    }
  );
  return parseResponse<any>(res);
}
