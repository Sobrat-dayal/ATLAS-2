/**
 * Authenticated REST API Client for Country Economics Intelligence (Stage 90).
 */

import {
  CountryCoverageResponseDTO,
  CountryDemographicsSummaryDTO,
  CountryEconomicProfileDTO,
  CountryEconomicsOverviewDTO,
  CountryExternalSummaryDTO,
  CountryFiscalSummaryDTO,
  CountryGDPDecompositionDTO,
  CountryIndustrySummaryDTO,
  CountryInflationSummaryDTO,
  CountryLaborSummaryDTO,
  CountryMonetarySummaryDTO,
  CountryProductionDecompositionDTO,
  GDPApproachKind,
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

export class CountryEconomicsApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "COUNTRY_ECONOMICS_API_ERROR") {
    super(message);
    this.name = "CountryEconomicsApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    let errorCode = "UNKNOWN_ERROR";
    try {
      const errorJson = await res.json();
      if (errorJson.detail) {
        errorDetail =
          typeof errorJson.detail === "string"
            ? errorJson.detail
            : JSON.stringify(errorJson.detail);
      } else if (errorJson.error?.message) {
        errorDetail = errorJson.error.message;
        errorCode = errorJson.error.code || errorCode;
      }
    } catch {
      // Use status text fallback
    }
    throw new CountryEconomicsApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

/**
 * List all supported sovereign country economic profiles.
 */
export async function getCountries(): Promise<CountryEconomicProfileDTO[]> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryEconomicProfileDTO[]>(res);
}

/**
 * Fetch master macroeconomic overview for a selected country.
 */
export async function getCountryOverview(countryId: string): Promise<CountryEconomicsOverviewDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/overview`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryEconomicsOverviewDTO>(res);
}

/**
 * Fetch canonical country metadata profile.
 */
export async function getCountryProfile(countryId: string): Promise<CountryEconomicProfileDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/profile`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryEconomicProfileDTO>(res);
}

/**
 * Fetch national accounts GDP expenditure decomposition.
 */
export async function getCountryGDP(
  countryId: string,
  approach: GDPApproachKind = "EXPENDITURE"
): Promise<CountryGDPDecompositionDTO> {
  const params = new URLSearchParams({ approach });
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/gdp?${params.toString()}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryGDPDecompositionDTO>(res);
}

/**
 * Fetch national accounts Gross Value Added by sector (production approach).
 */
export async function getCountryProduction(
  countryId: string
): Promise<CountryProductionDecompositionDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/gdp/production`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryProductionDecompositionDTO>(res);
}

/**
 * Fetch national price levels, CPI inflation, and components.
 */
export async function getCountryInflation(countryId: string): Promise<CountryInflationSummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/inflation`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryInflationSummaryDTO>(res);
}

/**
 * Fetch labor market survey, employment, and wage indicators.
 */
export async function getCountryLabor(countryId: string): Promise<CountryLaborSummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/labor`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryLaborSummaryDTO>(res);
}

/**
 * Fetch industrial production, retail sales, and sentiment.
 */
export async function getCountryIndustry(countryId: string): Promise<CountryIndustrySummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/industry`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryIndustrySummaryDTO>(res);
}

/**
 * Fetch monetary aggregates, bank credit, and policy rate context.
 */
export async function getCountryMonetary(countryId: string): Promise<CountryMonetarySummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/monetary`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryMonetarySummaryDTO>(res);
}

/**
 * Fetch government fiscal accounts, revenue, expenditure, and debt.
 */
export async function getCountryFiscal(countryId: string): Promise<CountryFiscalSummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/fiscal`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryFiscalSummaryDTO>(res);
}

/**
 * Fetch international trade, balance of payments, and foreign reserves.
 */
export async function getCountryExternal(countryId: string): Promise<CountryExternalSummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/external`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryExternalSummaryDTO>(res);
}

/**
 * Fetch demographic structure, population totals, and age dependency.
 */
export async function getCountryDemographics(
  countryId: string
): Promise<CountryDemographicsSummaryDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/demographics`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryDemographicsSummaryDTO>(res);
}

/**
 * Fetch indicator coverage and data availability matrix for a country.
 */
export async function getCountryCoverage(countryId: string): Promise<CountryCoverageResponseDTO> {
  const url = `${getBaseApiUrl()}/api/v1/economics/countries/${encodeURIComponent(countryId)}/coverage`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<CountryCoverageResponseDTO>(res);
}
