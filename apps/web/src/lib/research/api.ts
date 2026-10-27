/**
 * Authenticated REST API Client for ATLAS Institutional Financial Research (Stage 104).
 */

import {
  AttachResearchEvidenceDTO,
  CreateResearchClaimDTO,
  CreateResearchHypothesisDTO,
  CreateResearchInvestigationDTO,
  CreateResearchNoteDTO,
  CreateResearchQuestionDTO,
  InvestigationLifecycleStatus,
  LinkResearchSourceDTO,
  ResearchActivity,
  ResearchCitation,
  ResearchClaim,
  ResearchEvidence,
  ResearchHypothesis,
  ResearchInvestigation,
  ResearchNote,
  ResearchNoteRevision,
  ResearchOverviewSummary,
  ResearchQuestion,
  ResearchSourceReference,
  ResearchSourceType,
  ResearchType,
  UpdateResearchClaimDTO,
  UpdateResearchHypothesisDTO,
  UpdateResearchInvestigationDTO,
  UpdateResearchNoteDTO,
  UpdateResearchQuestionDTO,
  // Stage 105 Types
  ConvertEvidenceCandidateDTO,
  DocumentComparisonRequest,
  DocumentComparisonResult,
  DocumentSearchRequest,
  DocumentSearchResponse,
  EvidenceCandidateListResponse,
  FinancialFactsCompareRequest,
  FinancialFactsCompareResponse,
  ResearchDocumentOutline,
  ResearchDocumentProcessingStatus,
  ResearchDocumentSection,
  ResearchDocumentTable,
  ResearchDocumentTableListResponse,
  ResearchSourceDiscoveryQuery,
  ResearchSourceDiscoveryResponse,
  ResearchSourceTypeListResponse,
  ResolveEvidenceLocationRequest,
  ResolveEvidenceLocationResponse,
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

export class ResearchApiError extends Error {
  public status: number;
  public code: string;

  constructor(message: string, status: number, code: string = "RESEARCH_API_ERROR") {
    super(message);
    this.name = "ResearchApiError";
    this.status = status;
    this.code = code;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let msg = `Request failed with status ${res.status}`;
    let code = `HTTP_${res.status}`;
    try {
      const err = await res.json();
      if (err.error?.message) {
        msg = err.error.message;
        code = err.error.code || code;
      } else if (err.detail) {
        msg = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
      }
    } catch {
      // Non-JSON response
    }
    throw new ResearchApiError(msg, res.status, code);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Research API Client Functions
// ---------------------------------------------------------------------------

export async function getResearchOverview(): Promise<ResearchOverviewSummary> {
  const url = `${getBaseApiUrl()}/api/v1/research/overview`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchOverviewSummary>(res);
}

export async function listInvestigations(params?: {
  entity_id?: string;
  status?: InvestigationLifecycleStatus;
  research_type?: ResearchType;
  q?: string;
  limit?: number;
  offset?: number;
}): Promise<{ items: ResearchInvestigation[]; total_count: number }> {
  const searchParams = new URLSearchParams();
  if (params?.entity_id) searchParams.set("entity_id", params.entity_id);
  if (params?.status) searchParams.set("status", params.status);
  if (params?.research_type) searchParams.set("research_type", params.research_type);
  if (params?.q) searchParams.set("q", params.q);
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));

  const query = searchParams.toString();
  const url = `${getBaseApiUrl()}/api/v1/research/investigations${query ? `?${query}` : ""}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchInvestigation[]; total_count: number }>(res);
}

export async function createInvestigation(
  data: CreateResearchInvestigationDTO
): Promise<ResearchInvestigation> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchInvestigation>(res);
}

export async function getInvestigation(investigationId: string): Promise<ResearchInvestigation> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchInvestigation>(res);
}

export async function updateInvestigation(
  investigationId: string,
  data: UpdateResearchInvestigationDTO
): Promise<ResearchInvestigation> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchInvestigation>(res);
}

export async function archiveInvestigation(
  investigationId: string
): Promise<ResearchInvestigation> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/archive`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
  });
  return handleResponse<ResearchInvestigation>(res);
}

export async function deleteInvestigation(investigationId: string): Promise<{ deleted: boolean }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<{ deleted: boolean }>(res);
}

export async function listQuestions(
  investigationId: string
): Promise<{ items: ResearchQuestion[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/questions`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchQuestion[]; total_count: number }>(res);
}

export async function addQuestion(
  investigationId: string,
  data: CreateResearchQuestionDTO
): Promise<ResearchQuestion> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/questions`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchQuestion>(res);
}

export async function updateQuestion(
  questionId: string,
  data: UpdateResearchQuestionDTO
): Promise<ResearchQuestion> {
  const url = `${getBaseApiUrl()}/api/v1/research/questions/${encodeURIComponent(questionId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchQuestion>(res);
}

export async function deleteQuestion(questionId: string): Promise<{ deleted: boolean }> {
  const url = `${getBaseApiUrl()}/api/v1/research/questions/${encodeURIComponent(questionId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<{ deleted: boolean }>(res);
}

export async function listHypotheses(
  investigationId: string
): Promise<{ items: ResearchHypothesis[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/hypotheses`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchHypothesis[]; total_count: number }>(res);
}

export async function addHypothesis(
  investigationId: string,
  data: CreateResearchHypothesisDTO
): Promise<ResearchHypothesis> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/hypotheses`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchHypothesis>(res);
}

export async function updateHypothesis(
  hypothesisId: string,
  data: UpdateResearchHypothesisDTO
): Promise<ResearchHypothesis> {
  const url = `${getBaseApiUrl()}/api/v1/research/hypotheses/${encodeURIComponent(hypothesisId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchHypothesis>(res);
}

export async function deleteHypothesis(hypothesisId: string): Promise<{ deleted: boolean }> {
  const url = `${getBaseApiUrl()}/api/v1/research/hypotheses/${encodeURIComponent(hypothesisId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<{ deleted: boolean }>(res);
}

export async function listNotes(
  investigationId: string
): Promise<{ items: ResearchNote[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/notes`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchNote[]; total_count: number }>(res);
}

export async function createNote(
  investigationId: string,
  data: CreateResearchNoteDTO
): Promise<ResearchNote> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/notes`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchNote>(res);
}

export async function getNote(noteId: string): Promise<ResearchNote> {
  const url = `${getBaseApiUrl()}/api/v1/research/notes/${encodeURIComponent(noteId)}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchNote>(res);
}

export async function updateNote(
  noteId: string,
  data: UpdateResearchNoteDTO
): Promise<ResearchNote> {
  const url = `${getBaseApiUrl()}/api/v1/research/notes/${encodeURIComponent(noteId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchNote>(res);
}

export async function deleteNote(noteId: string): Promise<{ deleted: boolean }> {
  const url = `${getBaseApiUrl()}/api/v1/research/notes/${encodeURIComponent(noteId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<{ deleted: boolean }>(res);
}

export async function getNoteRevisions(noteId: string): Promise<ResearchNoteRevision[]> {
  const url = `${getBaseApiUrl()}/api/v1/research/notes/${encodeURIComponent(noteId)}/revisions`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchNoteRevision[]>(res);
}

export async function listClaims(
  investigationId: string
): Promise<{ items: ResearchClaim[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/claims`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchClaim[]; total_count: number }>(res);
}

export async function createClaim(
  investigationId: string,
  data: CreateResearchClaimDTO
): Promise<ResearchClaim> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/claims`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchClaim>(res);
}

export async function updateClaim(
  claimId: string,
  data: UpdateResearchClaimDTO
): Promise<ResearchClaim> {
  const url = `${getBaseApiUrl()}/api/v1/research/claims/${encodeURIComponent(claimId)}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchClaim>(res);
}

export async function deleteClaim(claimId: string): Promise<{ deleted: boolean }> {
  const url = `${getBaseApiUrl()}/api/v1/research/claims/${encodeURIComponent(claimId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<{ deleted: boolean }>(res);
}

export async function listSources(params?: {
  source_type?: ResearchSourceType;
  entity_id?: string;
  q?: string;
}): Promise<{ items: ResearchSourceReference[]; total_count: number }> {
  const searchParams = new URLSearchParams();
  if (params?.source_type) searchParams.set("source_type", params.source_type);
  if (params?.entity_id) searchParams.set("entity_id", params.entity_id);
  if (params?.q) searchParams.set("q", params.q);

  const query = searchParams.toString();
  const url = `${getBaseApiUrl()}/api/v1/research/sources${query ? `?${query}` : ""}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchSourceReference[]; total_count: number }>(res);
}

export async function listInvestigationSources(
  investigationId: string
): Promise<{ items: ResearchSourceReference[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/sources`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchSourceReference[]; total_count: number }>(res);
}

export async function linkSource(
  investigationId: string,
  data: LinkResearchSourceDTO
): Promise<ResearchSourceReference> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/sources`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchSourceReference>(res);
}

export async function unlinkSource(
  investigationId: string,
  sourceReferenceId: string
): Promise<{ unlinked: boolean }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/sources/${encodeURIComponent(sourceReferenceId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<{ unlinked: boolean }>(res);
}

export async function listEvidence(
  investigationId: string
): Promise<{ items: ResearchEvidence[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/evidence`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchEvidence[]; total_count: number }>(res);
}

export async function attachEvidence(
  investigationId: string,
  data: AttachResearchEvidenceDTO
): Promise<ResearchEvidence> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/evidence`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchEvidence>(res);
}

export async function removeEvidence(evidenceId: string): Promise<{ removed: boolean }> {
  const url = `${getBaseApiUrl()}/api/v1/research/evidence/${encodeURIComponent(evidenceId)}`;
  const res = await fetch(url, {
    method: "DELETE",
    headers: getHeaders(),
  });
  return handleResponse<{ removed: boolean }>(res);
}

export async function listCitations(
  investigationId: string
): Promise<{ items: ResearchCitation[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/citations`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchCitation[]; total_count: number }>(res);
}

export async function listActivity(
  investigationId: string
): Promise<{ items: ResearchActivity[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/investigations/${encodeURIComponent(investigationId)}/activity`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<{ items: ResearchActivity[]; total_count: number }>(res);
}

// ---------------------------------------------------------------------------
// Stage 105 — Advanced Source Discovery & Document Intelligence
// ---------------------------------------------------------------------------

export async function discoverSources(
  query: ResearchSourceDiscoveryQuery
): Promise<ResearchSourceDiscoveryResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/sources/search`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(query),
  });
  return handleResponse<ResearchSourceDiscoveryResponse>(res);
}

export async function getSourceTypes(): Promise<ResearchSourceTypeListResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/source-types`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchSourceTypeListResponse>(res);
}

export async function getDocument(documentId: string): Promise<ResearchSourceReference> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchSourceReference>(res);
}

export async function getDocumentProcessingStatus(
  documentId: string
): Promise<ResearchDocumentProcessingStatus> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}/processing-status`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchDocumentProcessingStatus>(res);
}

export async function getDocumentOutline(
  documentId: string
): Promise<ResearchDocumentOutline> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}/outline`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchDocumentOutline>(res);
}

export async function getDocumentSections(
  documentId: string
): Promise<ResearchDocumentSection[]> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}/sections`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchDocumentSection[]>(res);
}

export async function getDocumentSection(
  documentId: string,
  sectionId: string
): Promise<ResearchDocumentSection> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}/sections/${encodeURIComponent(sectionId)}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchDocumentSection>(res);
}

export async function searchDocument(
  documentId: string,
  data: DocumentSearchRequest
): Promise<DocumentSearchResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}/search`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<DocumentSearchResponse>(res);
}

export async function getDocumentTables(
  documentId: string
): Promise<ResearchDocumentTableListResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}/tables`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchDocumentTableListResponse>(res);
}

export async function getDocumentTable(
  documentId: string,
  tableId: string
): Promise<ResearchDocumentTable> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/${encodeURIComponent(documentId)}/tables/${encodeURIComponent(tableId)}`;
  const res = await fetch(url, { headers: getHeaders(), cache: "no-store" });
  return handleResponse<ResearchDocumentTable>(res);
}

export async function listEvidenceCandidates(
  documentId?: string,
  investigationId?: string,
  limit: number = 20
): Promise<EvidenceCandidateListResponse> {
  const params = new URLSearchParams();
  if (documentId) params.append("document_id", documentId);
  if (investigationId) params.append("investigation_id", investigationId);
  params.append("limit", limit.toString());

  const url = `${getBaseApiUrl()}/api/v1/research/evidence/candidates?${params.toString()}`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
  });
  return handleResponse<EvidenceCandidateListResponse>(res);
}

export async function resolveEvidenceLocation(
  data: ResolveEvidenceLocationRequest
): Promise<ResolveEvidenceLocationResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/evidence/resolve-location`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResolveEvidenceLocationResponse>(res);
}

export async function convertEvidenceCandidate(
  data: ConvertEvidenceCandidateDTO
): Promise<ResearchEvidence> {
  const url = `${getBaseApiUrl()}/api/v1/research/evidence/convert-candidate`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchEvidence>(res);
}

export async function compareDocuments(
  data: DocumentComparisonRequest
): Promise<DocumentComparisonResult> {
  const url = `${getBaseApiUrl()}/api/v1/research/documents/compare`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<DocumentComparisonResult>(res);
}

export async function compareFinancialFacts(
  data: FinancialFactsCompareRequest
): Promise<FinancialFactsCompareResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/financial-facts/compare`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<FinancialFactsCompareResponse>(res);
}

// ---------------------------------------------------------------------------
// Stage 106 — Research Analysis, Hypothesis Testing & Scenarios
// ---------------------------------------------------------------------------

import {
  CreateResearchAnalysisDTO,
  CreateResearchAssumptionDTO,
  CreateResearchFindingDTO,
  ExecuteHypothesisEvaluationDTO,
  ResearchAnalysis,
  ResearchAnalysisResult,
  ResearchAnalysisRun,
  ResearchAnalysisType,
  ResearchAnalysisTypeDefinition,
  ResearchAssumption,
  ResearchFinding,
  ResearchHypothesisEvaluation,
  SensitivityAnalysisRequest,
  SensitivityAnalysisResponse,
  UpdateResearchAnalysisDTO,
  UpdateResearchFindingDTO,
  ValidateAnalysisSpecificationRequest,
  ValidateAnalysisSpecificationResponse,
} from "./types";

export async function listAnalysisTypes(): Promise<{
  analysis_types: ResearchAnalysisTypeDefinition[];
  total_count: number;
}> {
  const url = `${getBaseApiUrl()}/api/v1/research/analysis-types`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<{
    analysis_types: ResearchAnalysisTypeDefinition[];
    total_count: number;
  }>(res);
}

export async function validateAnalysisSpecification(
  data: ValidateAnalysisSpecificationRequest
): Promise<ValidateAnalysisSpecificationResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/validate`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ValidateAnalysisSpecificationResponse>(res);
}

export async function listAnalyses(params?: {
  investigationId?: string;
  analysisType?: ResearchAnalysisType;
  entityId?: string;
  search?: string;
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<{ analyses: ResearchAnalysis[]; total_count: number }> {
  const query = new URLSearchParams();
  if (params?.investigationId) query.append("investigation_id", params.investigationId);
  if (params?.analysisType) query.append("analysis_type", params.analysisType);
  if (params?.entityId) query.append("entity_id", params.entityId);
  if (params?.search) query.append("search", params.search);
  if (params?.status) query.append("status", params.status);
  if (params?.limit) query.append("limit", params.limit.toString());
  if (params?.offset) query.append("offset", params.offset.toString());

  const url = `${getBaseApiUrl()}/api/v1/research/analyses?${query.toString()}`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<{ analyses: ResearchAnalysis[]; total_count: number }>(res);
}

export async function createAnalysis(
  data: CreateResearchAnalysisDTO
): Promise<ResearchAnalysis> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchAnalysis>(res);
}

export async function getAnalysis(analysisId: string): Promise<ResearchAnalysis> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<ResearchAnalysis>(res);
}

export async function updateAnalysis(
  analysisId: string,
  data: UpdateResearchAnalysisDTO
): Promise<ResearchAnalysis> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchAnalysis>(res);
}

export async function duplicateAnalysis(analysisId: string): Promise<ResearchAnalysis> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/duplicate`;
  const res = await fetch(url, { method: "POST", headers: getHeaders() });
  return handleResponse<ResearchAnalysis>(res);
}

export async function deleteAnalysis(
  analysisId: string
): Promise<{ deleted: boolean; analysis_id: string }> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}`;
  const res = await fetch(url, { method: "DELETE", headers: getHeaders() });
  return handleResponse<{ deleted: boolean; analysis_id: string }>(res);
}

export async function executeAnalysisRun(
  analysisId: string,
  inputPolicy: string = "PINNED_SOURCE_VERSION"
): Promise<ResearchAnalysisRun> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/runs?input_policy=${inputPolicy}`;
  const res = await fetch(url, { method: "POST", headers: getHeaders() });
  return handleResponse<ResearchAnalysisRun>(res);
}

export async function listAnalysisRuns(
  analysisId: string
): Promise<{ runs: ResearchAnalysisRun[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/runs`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<{ runs: ResearchAnalysisRun[]; total_count: number }>(res);
}

export async function getAnalysisRun(runId: string): Promise<ResearchAnalysisRun> {
  const url = `${getBaseApiUrl()}/api/v1/research/analysis-runs/${runId}`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<ResearchAnalysisRun>(res);
}

export async function getAnalysisRunResults(
  runId: string
): Promise<ResearchAnalysisResult> {
  const url = `${getBaseApiUrl()}/api/v1/research/analysis-runs/${runId}/results`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<ResearchAnalysisResult>(res);
}

export async function getAnalysisRunProvenance(
  runId: string
): Promise<Record<string, unknown>> {
  const url = `${getBaseApiUrl()}/api/v1/research/analysis-runs/${runId}/provenance`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<Record<string, unknown>>(res);
}

export async function listHypothesisEvaluations(
  hypothesisId: string
): Promise<{ evaluations: ResearchHypothesisEvaluation[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/hypotheses/${hypothesisId}/evaluations`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<{
    evaluations: ResearchHypothesisEvaluation[];
    total_count: number;
  }>(res);
}

export async function executeHypothesisEvaluation(
  hypothesisId: string,
  data: ExecuteHypothesisEvaluationDTO
): Promise<ResearchHypothesisEvaluation> {
  const url = `${getBaseApiUrl()}/api/v1/research/hypotheses/${hypothesisId}/evaluations`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchHypothesisEvaluation>(res);
}

export async function getHypothesisEvaluation(
  evaluationId: string
): Promise<ResearchHypothesisEvaluation> {
  const url = `${getBaseApiUrl()}/api/v1/research/hypothesis-evaluations/${evaluationId}`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<ResearchHypothesisEvaluation>(res);
}

export async function listAnalysisFindings(
  analysisId: string
): Promise<{ findings: ResearchFinding[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/findings`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<{ findings: ResearchFinding[]; total_count: number }>(res);
}

export async function createAnalysisFinding(
  analysisId: string,
  data: CreateResearchFindingDTO
): Promise<ResearchFinding> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/findings`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchFinding>(res);
}

export async function getFinding(findingId: string): Promise<ResearchFinding> {
  const url = `${getBaseApiUrl()}/api/v1/research/findings/${findingId}`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<ResearchFinding>(res);
}

export async function updateFinding(
  findingId: string,
  data: UpdateResearchFindingDTO
): Promise<ResearchFinding> {
  const url = `${getBaseApiUrl()}/api/v1/research/findings/${findingId}`;
  const res = await fetch(url, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchFinding>(res);
}

export async function deleteFinding(
  findingId: string
): Promise<{ deleted: boolean; finding_id: string }> {
  const url = `${getBaseApiUrl()}/api/v1/research/findings/${findingId}`;
  const res = await fetch(url, { method: "DELETE", headers: getHeaders() });
  return handleResponse<{ deleted: boolean; finding_id: string }>(res);
}

export async function listAnalysisAssumptions(
  analysisId: string
): Promise<{ assumptions: ResearchAssumption[]; total_count: number }> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/assumptions`;
  const res = await fetch(url, { method: "GET", headers: getHeaders() });
  return handleResponse<{ assumptions: ResearchAssumption[]; total_count: number }>(res);
}

export async function createAnalysisAssumption(
  analysisId: string,
  data: CreateResearchAssumptionDTO
): Promise<ResearchAssumption> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/assumptions`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<ResearchAssumption>(res);
}

export async function deleteAssumption(
  assumptionId: string
): Promise<{ deleted: boolean; assumption_id: string }> {
  const url = `${getBaseApiUrl()}/api/v1/research/assumptions/${assumptionId}`;
  const res = await fetch(url, { method: "DELETE", headers: getHeaders() });
  return handleResponse<{ deleted: boolean; assumption_id: string }>(res);
}

export async function executeSensitivityAnalysis(
  analysisId: string,
  data: SensitivityAnalysisRequest
): Promise<SensitivityAnalysisResponse> {
  const url = `${getBaseApiUrl()}/api/v1/research/analyses/${analysisId}/scenarios/sensitivity`;
  const res = await fetch(url, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<SensitivityAnalysisResponse>(res);
}

