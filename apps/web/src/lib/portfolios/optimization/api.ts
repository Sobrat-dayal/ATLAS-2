/**
 * ATLAS Portfolios V1 — Typed API Client for Optimization & Construction (Stage 114).
 */

import {
  CandidatePortfolioDTO,
  ConstraintValidationResultDTO,
  CreateOptimizationStudyRequestDTO,
  CurrentVsCandidateItemDTO,
  EfficientFrontierPointDTO,
  ExecuteOptimizationRequestDTO,
  OptimizationConstraintRequestDTO,
  OptimizationMethodologiesDTO,
  OptimizationRunsListDTO,
  OptimizationStudiesListDTO,
  OptimizationStudyDTO,
  PortfolioOptimizationRunDTO,
  SolverDiagnosticsDTO,
  UniverseAssetDTO,
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

/**
 * Creates a persistent optimization study.
 */
export async function createOptimizationStudy(
  portfolioId: string,
  req: CreateOptimizationStudyRequestDTO
): Promise<OptimizationStudyDTO> {
  return request<OptimizationStudyDTO>(`/portfolios/${portfolioId}/optimization/studies`, {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Lists active optimization studies for a portfolio.
 */
export async function listOptimizationStudies(
  portfolioId: string
): Promise<OptimizationStudiesListDTO> {
  return request<OptimizationStudiesListDTO>(`/portfolios/${portfolioId}/optimization/studies`);
}

/**
 * Retrieves an optimization study by ID.
 */
export async function getOptimizationStudy(
  portfolioId: string,
  studyId: string
): Promise<OptimizationStudyDTO> {
  return request<OptimizationStudyDTO>(`/portfolios/${portfolioId}/optimization/studies/${studyId}`);
}

/**
 * Archives an optimization study.
 */
export async function archiveOptimizationStudy(
  portfolioId: string,
  studyId: string
): Promise<OptimizationStudyDTO> {
  return request<OptimizationStudyDTO>(`/portfolios/${portfolioId}/optimization/studies/${studyId}`, {
    method: 'DELETE',
  });
}

/**
 * Executes a mathematical portfolio optimization run.
 */
export async function executeOptimizationRun(
  portfolioId: string,
  req: ExecuteOptimizationRequestDTO
): Promise<PortfolioOptimizationRunDTO> {
  return request<PortfolioOptimizationRunDTO>(`/portfolios/${portfolioId}/optimization/runs`, {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * Lists historical optimization runs.
 */
export async function listOptimizationRuns(
  portfolioId: string,
  studyId?: string
): Promise<OptimizationRunsListDTO> {
  const query = studyId ? `?study_id=${encodeURIComponent(studyId)}` : '';
  return request<OptimizationRunsListDTO>(`/portfolios/${portfolioId}/optimization/runs${query}`);
}

/**
 * Retrieves the latest valid optimization run or computes default.
 */
export async function getLatestOptimizationRun(
  portfolioId: string
): Promise<PortfolioOptimizationRunDTO> {
  return request<PortfolioOptimizationRunDTO>(`/portfolios/${portfolioId}/optimization/runs/latest`);
}

/**
 * Retrieves a specific optimization run by ID.
 */
export async function getOptimizationRun(
  portfolioId: string,
  runId: string
): Promise<PortfolioOptimizationRunDTO> {
  return request<PortfolioOptimizationRunDTO>(`/portfolios/${portfolioId}/optimization/runs/${runId}`);
}

/**
 * Retrieves candidate allocation weights and metrics.
 */
export async function getOptimizationCandidate(
  portfolioId: string,
  runId: string
): Promise<CandidatePortfolioDTO> {
  return request<CandidatePortfolioDTO>(`/portfolios/${portfolioId}/optimization/runs/${runId}/candidate`);
}

/**
 * Retrieves efficient frontier points.
 */
export async function getOptimizationFrontier(
  portfolioId: string,
  runId: string
): Promise<EfficientFrontierPointDTO[]> {
  return request<EfficientFrontierPointDTO[]>(`/portfolios/${portfolioId}/optimization/runs/${runId}/frontier`);
}

/**
 * Retrieves current vs candidate comparison and hypothetical orders.
 */
export async function getOptimizationComparison(
  portfolioId: string,
  runId: string
): Promise<CurrentVsCandidateItemDTO[]> {
  return request<CurrentVsCandidateItemDTO[]>(`/portfolios/${portfolioId}/optimization/runs/${runId}/comparison`);
}

/**
 * Retrieves solver diagnostics.
 */
export async function getOptimizationDiagnostics(
  portfolioId: string,
  runId: string
): Promise<SolverDiagnosticsDTO> {
  return request<SolverDiagnosticsDTO>(`/portfolios/${portfolioId}/optimization/runs/${runId}/diagnostics`);
}

/**
 * Retrieves eligible universe assets.
 */
export async function getOptimizationUniverse(
  portfolioId: string
): Promise<UniverseAssetDTO[]> {
  return request<UniverseAssetDTO[]>(`/portfolios/${portfolioId}/optimization/universe`);
}

/**
 * Pre-checks constraint feasibility.
 */
export async function validateOptimizationConstraints(
  portfolioId: string,
  constraints: OptimizationConstraintRequestDTO[],
  universeSymbols?: string[]
): Promise<ConstraintValidationResultDTO> {
  let query = '';
  if (universeSymbols && universeSymbols.length > 0) {
    query = '?' + universeSymbols.map((s) => `universe_symbols=${encodeURIComponent(s)}`).join('&');
  }
  return request<ConstraintValidationResultDTO>(
    `/portfolios/${portfolioId}/optimization/constraints/validate${query}`,
    {
      method: 'POST',
      body: JSON.stringify(constraints),
    }
  );
}

/**
 * Retrieves supported optimization methodologies and models.
 */
export async function getOptimizationMethodologies(
  portfolioId: string
): Promise<OptimizationMethodologiesDTO> {
  return request<OptimizationMethodologiesDTO>(`/portfolios/${portfolioId}/optimization/methodologies`);
}
