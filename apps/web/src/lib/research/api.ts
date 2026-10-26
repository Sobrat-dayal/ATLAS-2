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
