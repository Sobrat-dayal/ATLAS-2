/**
 * Client API functions for Company Financial Ratios (Stage 83).
 */

import {
  CompanyRatiosResponse,
  RatioCatalogResponse,
  RatioHistoryResponse,
  RatioLineageResponse,
  RatioMethodologyResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function getRatioCatalog(
  companyId: string,
  category?: string
): Promise<RatioCatalogResponse> {
  const url = new URL(`${API_BASE}/companies/${encodeURIComponent(companyId)}/ratios/catalog`);
  if (category) {
    url.searchParams.set("category", category);
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load ratio catalog (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getCompanyRatios(
  companyId: string,
  periodId: string = "FY2024",
  periodType: string = "ANNUAL",
  category?: string
): Promise<CompanyRatiosResponse> {
  const url = new URL(`${API_BASE}/companies/${encodeURIComponent(companyId)}/ratios`);
  url.searchParams.set("period_id", periodId);
  url.searchParams.set("period_type", periodType);
  if (category && category !== "all") {
    url.searchParams.set("category", category);
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load company ratios (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getRatioHistory(
  companyId: string,
  ratioId: string,
  periodType: string = "ANNUAL",
  limit: number = 10
): Promise<RatioHistoryResponse> {
  const url = new URL(`${API_BASE}/companies/${encodeURIComponent(companyId)}/ratios/history`);
  url.searchParams.set("ratio_id", ratioId);
  url.searchParams.set("period_type", periodType);
  url.searchParams.set("limit", limit.toString());

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load ratio history (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getRatioMethodology(
  companyId: string,
  ratioId: string
): Promise<RatioMethodologyResponse> {
  const url = new URL(
    `${API_BASE}/companies/${encodeURIComponent(companyId)}/ratios/${encodeURIComponent(ratioId)}/methodology`
  );

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load ratio methodology (${res.status} ${res.statusText})`);
  }

  return res.json();
}

export async function getRatioLineage(
  companyId: string,
  ratioId: string,
  periodId: string = "FY2024"
): Promise<RatioLineageResponse> {
  const url = new URL(
    `${API_BASE}/companies/${encodeURIComponent(companyId)}/ratios/${encodeURIComponent(ratioId)}/lineage`
  );
  url.searchParams.set("period_id", periodId);

  const res = await fetch(url.toString(), {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Failed to load ratio lineage (${res.status} ${res.statusText})`);
  }

  return res.json();
}
