/**
 * Authenticated REST API Client for ATLAS Institutional Financial News (Stage 99).
 */

import {
  NewsArticleDTO,
  NewsCoverageResponseDTO,
  NewsFeedQueryParams,
  NewsFeedResponseDTO,
  NewsFreshnessResponseDTO,
  NewsPublisherDTO,
  NewsSourceDTO,
} from "./types";

function getBaseApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

function getHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...extra,
  };
}

export class NewsApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "NEWS_API_ERROR") {
    super(message);
    this.name = "NewsApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    let errorCode = "UNKNOWN_NEWS_ERROR";
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail);
      } else if (errorJson.error?.message) {
        errorDetail = errorJson.error.message;
        errorCode = errorJson.error.code || errorCode;
      }
    } catch {
      // Fallback to HTTP text
    }
    throw new NewsApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export async function getNewsFeed(params?: NewsFeedQueryParams): Promise<NewsFeedResponseDTO> {
  const url = new URL("/api/v1/news/feed", getBaseApiUrl());
  if (params) {
    if (params.category) url.searchParams.set("category", params.category);
    if (params.source_id) url.searchParams.set("source_id", params.source_id);
    if (params.publisher_id) url.searchParams.set("publisher_id", params.publisher_id);
    if (params.entity_id) url.searchParams.set("entity_id", params.entity_id);
    if (params.geography) url.searchParams.set("geography", params.geography);
    if (params.q) url.searchParams.set("q", params.q);
    if (params.start_date) url.searchParams.set("start_date", params.start_date);
    if (params.end_date) url.searchParams.set("end_date", params.end_date);
    if (params.limit) url.searchParams.set("limit", String(params.limit));
    if (params.cursor) url.searchParams.set("cursor", params.cursor);
  }

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFeedResponseDTO>(res);
}

export async function getNewsArticle(articleId: string): Promise<NewsArticleDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/articles/${encodeURIComponent(articleId)}`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsArticleDTO>(res);
}

export async function getNewsSources(): Promise<NewsSourceDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/sources`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsSourceDTO[]>(res);
}

export async function getNewsPublishers(): Promise<NewsPublisherDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/publishers`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsPublisherDTO[]>(res);
}

export async function getNewsCategories(): Promise<string[]> {
  const url = `${getBaseApiUrl()}/api/v1/news/categories`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<string[]>(res);
}

export async function searchNews(
  q: string,
  category?: string,
  limit: number = 30
): Promise<NewsFeedResponseDTO> {
  const url = new URL("/api/v1/news/search", getBaseApiUrl());
  url.searchParams.set("q", q);
  if (category) url.searchParams.set("category", category);
  url.searchParams.set("limit", String(limit));

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFeedResponseDTO>(res);
}

export async function getEntityNews(
  entityId: string,
  limit: number = 20
): Promise<NewsFeedResponseDTO> {
  const url = new URL(
    `/api/v1/news/entities/${encodeURIComponent(entityId)}`,
    getBaseApiUrl()
  );
  url.searchParams.set("limit", String(limit));

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFeedResponseDTO>(res);
}

export async function getNewsCoverage(): Promise<NewsCoverageResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/coverage`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsCoverageResponseDTO>(res);
}

export async function getNewsStatus(): Promise<NewsFreshnessResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/news/status`;
  const res = await fetch(url, {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<NewsFreshnessResponseDTO>(res);
}
