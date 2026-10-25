/**
 * Authenticated REST API Client for Company Financial Statements (Stage 82).
 */

import {
  ComparisonMode,
  ConsolidationScope,
  FinancialStatementResponse,
  RevisionPolicy,
  ScaleType,
  StatementCatalogResponse,
  StatementPeriodType,
  StatementSourcesResponse,
  StatementType,
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

export class StatementApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "STATEMENT_API_ERROR") {
    super(message);
    this.name = "StatementApiError";
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
        errorDetail = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail);
      } else if (errorJson.error?.message) {
        errorDetail = errorJson.error.message;
        errorCode = errorJson.error.code || errorCode;
      }
    } catch {
      // Fallback to HTTP text
    }
    throw new StatementApiError(errorDetail, res.status, errorCode);
  }
  return res.json() as Promise<T>;
}

export interface StatementQueryParams {
  period_type?: StatementPeriodType;
  consolidation_scope?: ConsolidationScope;
  scale?: ScaleType;
  comparison_mode?: ComparisonMode;
  revision_policy?: RevisionPolicy;
  fiscal_year_from?: number;
  fiscal_year_to?: number;
  max_periods?: number;
}

/**
 * Discovers available statements, fiscal years, quarters, and scopes.
 */
export async function getStatementCatalog(
  companyId: string,
  consolidationScope: ConsolidationScope = "consolidated"
): Promise<StatementCatalogResponse> {
  const url = new URL(`${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/statements/catalog`);
  url.searchParams.set("consolidation_scope", consolidationScope);

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<StatementCatalogResponse>(res);
}

/**
 * Retrieves a multi-period financial statement (income, balance sheet, cash flow).
 */
export async function getFinancialStatement(
  companyId: string,
  statementType: StatementType,
  params: StatementQueryParams = {}
): Promise<FinancialStatementResponse> {
  let endpoint = "income";
  if (statementType === "balance_sheet") endpoint = "balance-sheet";
  else if (statementType === "cash_flow_statement") endpoint = "cash-flow";

  const url = new URL(
    `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/statements/${endpoint}`
  );

  if (params.period_type) url.searchParams.set("period_type", params.period_type);
  if (params.consolidation_scope) url.searchParams.set("consolidation_scope", params.consolidation_scope);
  if (params.scale) url.searchParams.set("scale", params.scale);
  if (params.comparison_mode) url.searchParams.set("comparison_mode", params.comparison_mode);
  if (params.revision_policy) url.searchParams.set("revision_policy", params.revision_policy);
  if (params.fiscal_year_from) url.searchParams.set("fiscal_year_from", params.fiscal_year_from.toString());
  if (params.fiscal_year_to) url.searchParams.set("fiscal_year_to", params.fiscal_year_to.toString());
  if (params.max_periods) url.searchParams.set("max_periods", params.max_periods.toString());

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<FinancialStatementResponse>(res);
}

/**
 * Retrieves source filing references, timestamps, and lineages for a statement.
 */
export async function getStatementSources(
  companyId: string,
  statementType: StatementType,
  consolidationScope: ConsolidationScope = "consolidated"
): Promise<StatementSourcesResponse> {
  const url = new URL(
    `${getBaseApiUrl()}/api/v1/companies/${encodeURIComponent(companyId)}/statements/${statementType}/sources`
  );
  url.searchParams.set("consolidation_scope", consolidationScope);

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: getHeaders(),
  });
  return handleResponse<StatementSourcesResponse>(res);
}
