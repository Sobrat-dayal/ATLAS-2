/**
 * ATLAS Portfolios V1 — Typed API Client for Allocation & Exposure (Stage 112).
 */

import {
  AllocationChangeResponse,
  CalculateExposureRequest,
  ConcentrationSummaryResponse,
  CrossFundOverlapResponse,
  ExposureDimension,
  ExposureDimensionResponse,
  FundLookThroughResponse,
  HistoricalAllocationPointResponse,
  IssuerWeightResponse,
  PortfolioExposureRunResponse,
  SecurityWeightResponse,
  ExposureDataQualityResponse,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred.';
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail =
          typeof errorJson.detail === 'object'
            ? errorJson.detail.message || JSON.stringify(errorJson.detail)
            : errorJson.detail;
      }
    } catch {
      errorDetail = `Request failed with status ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const portfolioExposureApi = {
  calculateExposure: async (
    portfolioId: string,
    payload: CalculateExposureRequest = {}
  ): Promise<PortfolioExposureRunResponse> => {
    return request<PortfolioExposureRunResponse>(
      `/portfolios/${portfolioId}/exposures/calculate`,
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
  },

  getLatestExposure: async (
    portfolioId: string,
    params: {
      exposure_basis?: string;
      geography_policy?: string;
      enable_look_through?: boolean;
      force_recalculate?: boolean;
    } = {}
  ): Promise<PortfolioExposureRunResponse> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.geography_policy) query.append('geography_policy', params.geography_policy);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    if (params.force_recalculate !== undefined)
      query.append('force_recalculate', String(params.force_recalculate));

    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<PortfolioExposureRunResponse>(`/portfolios/${portfolioId}/exposures${qs}`);
  },

  listExposureRuns: async (portfolioId: string): Promise<PortfolioExposureRunResponse[]> => {
    return request<PortfolioExposureRunResponse[]>(`/portfolios/${portfolioId}/exposures/runs`);
  },

  getExposureRun: async (
    portfolioId: string,
    runId: string
  ): Promise<PortfolioExposureRunResponse> => {
    return request<PortfolioExposureRunResponse>(
      `/portfolios/${portfolioId}/exposures/runs/${runId}`
    );
  },

  getAssetClassAllocation: async (
    portfolioId: string,
    params: { exposure_basis?: string; enable_look_through?: boolean } = {}
  ): Promise<ExposureDimensionResponse> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<ExposureDimensionResponse>(
      `/portfolios/${portfolioId}/allocations/asset-classes${qs}`
    );
  },

  getSectorExposure: async (
    portfolioId: string,
    params: { exposure_basis?: string; enable_look_through?: boolean } = {}
  ): Promise<ExposureDimensionResponse> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<ExposureDimensionResponse>(
      `/portfolios/${portfolioId}/allocations/sectors${qs}`
    );
  },

  getIndustryExposure: async (
    portfolioId: string,
    params: { exposure_basis?: string; enable_look_through?: boolean } = {}
  ): Promise<ExposureDimensionResponse> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<ExposureDimensionResponse>(
      `/portfolios/${portfolioId}/allocations/industries${qs}`
    );
  },

  getCountryExposure: async (
    portfolioId: string,
    params: { exposure_basis?: string; geography_policy?: string; enable_look_through?: boolean } = {}
  ): Promise<ExposureDimensionResponse> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.geography_policy) query.append('geography_policy', params.geography_policy);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<ExposureDimensionResponse>(
      `/portfolios/${portfolioId}/allocations/countries${qs}`
    );
  },

  getCurrencyExposure: async (
    portfolioId: string,
    params: { exposure_basis?: string; enable_look_through?: boolean } = {}
  ): Promise<ExposureDimensionResponse> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<ExposureDimensionResponse>(
      `/portfolios/${portfolioId}/allocations/currencies${qs}`
    );
  },

  getSecurityWeights: async (
    portfolioId: string,
    params: { exposure_basis?: string; enable_look_through?: boolean } = {}
  ): Promise<SecurityWeightResponse[]> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<SecurityWeightResponse[]>(
      `/portfolios/${portfolioId}/concentration/securities${qs}`
    );
  },

  getIssuerWeights: async (
    portfolioId: string,
    params: { exposure_basis?: string; enable_look_through?: boolean } = {}
  ): Promise<IssuerWeightResponse[]> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<IssuerWeightResponse[]>(
      `/portfolios/${portfolioId}/concentration/issuers${qs}`
    );
  },

  getConcentrationSummary: async (
    portfolioId: string,
    params: { exposure_basis?: string; enable_look_through?: boolean } = {}
  ): Promise<ConcentrationSummaryResponse> => {
    const query = new URLSearchParams();
    if (params.exposure_basis) query.append('exposure_basis', params.exposure_basis);
    if (params.enable_look_through !== undefined)
      query.append('enable_look_through', String(params.enable_look_through));
    const qs = query.toString() ? `?${query.toString()}` : '';
    return request<ConcentrationSummaryResponse>(
      `/portfolios/${portfolioId}/concentration/summary${qs}`
    );
  },

  getLookThroughDetails: async (portfolioId: string): Promise<FundLookThroughResponse[]> => {
    return request<FundLookThroughResponse[]>(`/portfolios/${portfolioId}/lookthrough`);
  },

  getFundLookThrough: async (
    portfolioId: string,
    instrumentId: string
  ): Promise<FundLookThroughResponse> => {
    return request<FundLookThroughResponse>(
      `/portfolios/${portfolioId}/lookthrough/funds/${instrumentId}`
    );
  },

  getCrossFundOverlap: async (portfolioId: string): Promise<CrossFundOverlapResponse[]> => {
    return request<CrossFundOverlapResponse[]>(`/portfolios/${portfolioId}/lookthrough/overlap`);
  },

  getHistoricalExposures: async (
    portfolioId: string,
    dimension: ExposureDimension = 'ASSET_CLASS'
  ): Promise<HistoricalAllocationPointResponse[]> => {
    return request<HistoricalAllocationPointResponse[]>(
      `/portfolios/${portfolioId}/exposures/history?dimension=${dimension}`
    );
  },

  getAllocationChanges: async (
    portfolioId: string,
    startDate: string,
    endDate: string,
    dimension: ExposureDimension = 'ASSET_CLASS'
  ): Promise<AllocationChangeResponse[]> => {
    return request<AllocationChangeResponse[]>(
      `/portfolios/${portfolioId}/exposures/changes?start_date=${startDate}&end_date=${endDate}&dimension=${dimension}`
    );
  },

  getExposureDataQuality: async (portfolioId: string): Promise<ExposureDataQualityResponse> => {
    return request<ExposureDataQualityResponse>(`/portfolios/${portfolioId}/exposures/data-quality`);
  },
};
