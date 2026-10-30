/**
 * Client API for Stage 127: AI Research and Retrieval-Augmented Generation.
 */

import {
  DocumentComparisonRequest,
  DocumentComparisonResponse,
  IngestDocumentRequest,
  IngestDocumentResponse,
  ResearchAnswerResponse,
  ResearchDocumentDTO,
  ResearchPassageDTO,
  ResearchQueryRequest,
  ResearchSearchRequest,
  ResearchSourceDTO,
} from "./types";

const API_BASE = "/api/v1/ai/research";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // Use fallback
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Lists authorized research sources.
 */
export async function fetchResearchSources(): Promise<ResearchSourceDTO[]> {
  const data = await request<{ sources: ResearchSourceDTO[]; count: number }>("/sources");
  return data.sources;
}

/**
 * Lists authorized research documents with optional symbol, type, or historical cutoff.
 */
export async function fetchResearchDocuments(params?: {
  symbol?: string;
  document_type?: string;
  historical_as_of?: string;
}): Promise<ResearchDocumentDTO[]> {
  const queryParams = new URLSearchParams();
  if (params?.symbol) queryParams.append("symbol", params.symbol);
  if (params?.document_type) queryParams.append("document_type", params.document_type);
  if (params?.historical_as_of) queryParams.append("historical_as_of", params.historical_as_of);

  const qs = queryParams.toString() ? `?${queryParams.toString()}` : "";
  const data = await request<{ documents: ResearchDocumentDTO[]; count: number }>(`/documents${qs}`);
  return data.documents;
}

/**
 * Retrieves document metadata by ID.
 */
export async function fetchResearchDocument(documentId: string): Promise<ResearchDocumentDTO> {
  return request<ResearchDocumentDTO>(`/documents/${documentId}`);
}

/**
 * Searches authorized passages and excerpts.
 */
export async function searchResearchPassages(
  payload: ResearchSearchRequest,
): Promise<{ query: string; passages: ResearchPassageDTO[]; total_hits: number }> {
  return request<{ query: string; passages: ResearchPassageDTO[]; total_hits: number }>(
    "/search",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

/**
 * Executes full grounded research generation query.
 */
export async function executeResearchQuery(
  payload: ResearchQueryRequest,
): Promise<ResearchAnswerResponse> {
  return request<ResearchAnswerResponse>("/query", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Compares two document revisions or financial reports.
 */
export async function compareResearchDocuments(
  payload: DocumentComparisonRequest,
): Promise<DocumentComparisonResponse> {
  return request<DocumentComparisonResponse>("/compare", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Resolves a citation back to verified source excerpt with re-authorization.
 */
export async function resolveResearchCitation(
  citationId: string,
): Promise<Record<string, any>> {
  return request<Record<string, any>>(`/citations/${citationId}`);
}

/**
 * Ingests a new document into the research registry.
 */
export async function ingestResearchDocument(
  payload: IngestDocumentRequest,
): Promise<IngestDocumentResponse> {
  return request<IngestDocumentResponse>("/ingest", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
