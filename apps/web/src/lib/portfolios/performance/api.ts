/**
 * ATLAS Portfolios V1 — Typed Performance API Client (Stage 111).
 */

import {
  BenchmarkListResponse,
  PerformanceCalculateRequest,
  PerformanceCashFlowDTO,
  PerformanceDataQualityDTO,
  PerformancePeriodType,
  PerformanceResponse,
  PerformanceRunListResponse,
  PerformanceSeriesResponse,
  PeriodicReturnsResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An unexpected performance calculation error occurred.";
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (typeof errorJson.detail === "object" && errorJson.detail.message) {
          errorDetail = errorJson.detail.message;
        } else {
          errorDetail = String(errorJson.detail);
        }
      } else if (errorJson.message) {
        errorDetail = errorJson.message;
      }
    } catch {
      errorDetail = `${response.status} ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const performanceApi = {
  /**
   * Fetch canonical benchmarks available for comparison.
   */
  async getBenchmarks(): Promise<BenchmarkListResponse> {
    return request<BenchmarkListResponse>("/portfolios/benchmarks");
  },

  /**
   * Get active performance summary for a portfolio or specific account.
   */
  async getPerformanceSummary(
    portfolioId: string,
    params: {
      period_type?: PerformancePeriodType;
      methodology?: string;
      account_id?: string;
      benchmark_id?: string;
      custom_start_date?: string;
      custom_end_date?: string;
    } = {}
  ): Promise<PerformanceResponse> {
    const query = new URLSearchParams();
    if (params.period_type) query.set("period_type", params.period_type);
    if (params.methodology) query.set("methodology", params.methodology);
    if (params.account_id && params.account_id !== "ALL") query.set("account_id", params.account_id);
    if (params.benchmark_id && params.benchmark_id !== "NONE") query.set("benchmark_id", params.benchmark_id);
    if (params.custom_start_date) query.set("custom_start_date", params.custom_start_date);
    if (params.custom_end_date) query.set("custom_end_date", params.custom_end_date);

    const qs = query.toString() ? `?${query.toString()}` : "";
    return request<PerformanceResponse>(`/portfolios/${portfolioId}/performance${qs}`);
  },

  /**
   * Trigger explicit immutable performance calculation run.
   */
  async calculatePerformance(
    portfolioId: string,
    payload: PerformanceCalculateRequest
  ): Promise<PerformanceResponse> {
    return request<PerformanceResponse>(`/portfolios/${portfolioId}/performance/calculate`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Fetch time-series equity curve and rebased growth series.
   */
  async getPerformanceSeries(
    portfolioId: string,
    params: {
      period_type?: PerformancePeriodType;
      account_id?: string;
      benchmark_id?: string;
    } = {}
  ): Promise<PerformanceSeriesResponse> {
    const query = new URLSearchParams();
    if (params.period_type) query.set("period_type", params.period_type);
    if (params.account_id && params.account_id !== "ALL") query.set("account_id", params.account_id);
    if (params.benchmark_id && params.benchmark_id !== "NONE") query.set("benchmark_id", params.benchmark_id);

    const qs = query.toString() ? `?${query.toString()}` : "";
    return request<PerformanceSeriesResponse>(`/portfolios/${portfolioId}/performance/series${qs}`);
  },

  /**
   * Fetch calendar periodic returns table (monthly and annual returns).
   */
  async getPeriodicReturns(
    portfolioId: string,
    params: {
      account_id?: string;
    } = {}
  ): Promise<PeriodicReturnsResponse> {
    const query = new URLSearchParams();
    if (params.account_id && params.account_id !== "ALL") query.set("account_id", params.account_id);

    const qs = query.toString() ? `?${query.toString()}` : "";
    return request<PeriodicReturnsResponse>(`/portfolios/${portfolioId}/performance/periodic${qs}`);
  },

  /**
   * Fetch classified cash flows within the period.
   */
  async getClassifiedCashFlows(
    portfolioId: string,
    params: {
      period_type?: PerformancePeriodType;
      account_id?: string;
    } = {}
  ): Promise<PerformanceCashFlowDTO[]> {
    const query = new URLSearchParams();
    if (params.period_type) query.set("period_type", params.period_type);
    if (params.account_id && params.account_id !== "ALL") query.set("account_id", params.account_id);

    const qs = query.toString() ? `?${query.toString()}` : "";
    return request<PerformanceCashFlowDTO[]>(`/portfolios/${portfolioId}/performance/cash-flows${qs}`);
  },

  /**
   * Fetch data quality audit for the portfolio.
   */
  async getDataQualityAudit(portfolioId: string): Promise<PerformanceDataQualityDTO> {
    return request<PerformanceDataQualityDTO>(`/portfolios/${portfolioId}/performance/data-quality`);
  },

  /**
   * List historical calculation runs for audit and reproducibility.
   */
  async getPerformanceRuns(
    portfolioId: string,
    params: { limit?: number; offset?: number } = {}
  ): Promise<PerformanceRunListResponse> {
    const query = new URLSearchParams();
    if (params.limit) query.set("limit", String(params.limit));
    if (params.offset) query.set("offset", String(params.offset));

    const qs = query.toString() ? `?${query.toString()}` : "";
    return request<PerformanceRunListResponse>(`/portfolios/${portfolioId}/performance/runs${qs}`);
  },
};

