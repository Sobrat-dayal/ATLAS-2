/**
 * Client API functions for Company Earnings Intelligence (Stage 84).
 */

import {
  CompanyEarningsOverviewDTO,
  EarningsCallsResponseDTO,
  EarningsEventDTO,
  EarningsEventsResponseDTO,
  EarningsHistoryResponseDTO,
  GuidanceResponseDTO,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function getEarningsOverview(companyId: string): Promise<CompanyEarningsOverviewDTO> {
  const url = `${API_BASE}/companies/${encodeURIComponent(companyId)}/earnings/overview`;
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load earnings overview (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getEarningsHistory(
  companyId: string,
  periodType: string = "QUARTERLY",
  limit: number = 16
): Promise<EarningsHistoryResponseDTO> {
  const url = new URL(`${API_BASE}/companies/${encodeURIComponent(companyId)}/earnings/history`);
  url.searchParams.set("period_type", periodType);
  url.searchParams.set("limit", String(limit));

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load earnings history (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getEarningsEvents(
  companyId: string,
  status?: string
): Promise<EarningsEventsResponseDTO> {
  const url = new URL(`${API_BASE}/companies/${encodeURIComponent(companyId)}/earnings/events`);
  if (status) {
    url.searchParams.set("status", status);
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load earnings events (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getManagementGuidance(
  companyId: string,
  status?: string
): Promise<GuidanceResponseDTO> {
  const url = new URL(`${API_BASE}/companies/${encodeURIComponent(companyId)}/earnings/guidance`);
  if (status) {
    url.searchParams.set("status", status);
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load guidance (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getEarningsCalls(companyId: string): Promise<EarningsCallsResponseDTO> {
  const url = `${API_BASE}/companies/${encodeURIComponent(companyId)}/earnings/calls`;
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load earnings calls (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getEarningsEventDetail(
  companyId: string,
  eventId: string
): Promise<EarningsEventDTO> {
  const url = `${API_BASE}/companies/${encodeURIComponent(companyId)}/earnings/events/${encodeURIComponent(eventId)}`;
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load event detail (${res.status} ${res.statusText})`);
  }

  return res.json();
}
